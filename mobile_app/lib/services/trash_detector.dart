import 'dart:io';
import 'dart:isolate';
import 'dart:math' as math;

import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import 'package:image/image.dart' as img;
import 'package:tflite_flutter/tflite_flutter.dart';

import '../models/scan_result.dart';
import '../models/waste_class.dart';
import 'yolo_postprocess.dart';

/// Lokasi model hasil ekspor (lihat tools/export_tflite.py).
const kModelAsset = 'assets/models/trash_yolov8.tflite';

/// Menjalankan model YOLOv8 di perangkat (on-device, offline).
///
/// Jika file model belum dipasang di assets, detektor berjalan dalam mode
/// demo: hasilnya acak tetapi alur UI tetap bisa dicoba dan ditampilkan.
class TrashDetector {
  TrashDetector._(this._interpreter, this.loadError);

  final Interpreter? _interpreter;

  /// Alasan model gagal dimuat (null jika model aktif).
  final String? loadError;

  bool get isDemo => _interpreter == null;

  static Future<TrashDetector> load() async {
    try {
      final options = InterpreterOptions()..threads = 4;
      final interpreter =
          await Interpreter.fromAsset(kModelAsset, options: options)
            ..allocateTensors();
      final input = interpreter.getInputTensor(0);
      if (input.type != TensorType.float32 || input.shape.length != 4) {
        interpreter.close();
        return TrashDetector._(
          null,
          'Model harus float32 dengan input [1, H, W, 3], '
          'ditemukan ${input.type} ${input.shape}.',
        );
      }
      return TrashDetector._(interpreter, null);
    } catch (e) {
      debugPrint('Model tidak dimuat, memakai mode demo: $e');
      return TrashDetector._(null, 'Model belum dipasang di $kModelAsset');
    }
  }

  /// Menyiapkan gambar dari [sourcePath], menyimpannya ke [savePath], lalu
  /// menjalankan deteksi. Semua kerja berat berjalan di isolate terpisah.
  Future<ScanResult> scan({
    required String sourcePath,
    required String savePath,
  }) async {
    final address = _interpreter?.address;
    final job = await Isolate.run(
      () => _runJob(address, sourcePath, savePath),
    );
    return ScanResult(
      id: DateTime.now().microsecondsSinceEpoch.toString(),
      imageFile: savePath.split(Platform.pathSeparator).last,
      imageSize: Size(job.width.toDouble(), job.height.toDouble()),
      createdAt: DateTime.now(),
      detections: job.detections
          .map(
            (d) => Detection(
              wasteClass: WasteClass.fromIndex(d.classIndex),
              confidence: d.score,
              box: Rect.fromLTRB(d.l, d.t, d.r, d.b),
            ),
          )
          .toList(),
      isDemo: address == null,
    );
  }

  void dispose() => _interpreter?.close();
}

class _JobResult {
  const _JobResult(this.width, this.height, this.detections);
  final int width;
  final int height;
  final List<RawDetection> detections;
}

/// Ukuran sisi terpanjang foto yang disimpan ke riwayat.
const _maxSavedSide = 1280;

_JobResult _runJob(int? interpreterAddress, String source, String save) {
  final decoded = img.decodeImage(File(source).readAsBytesSync());
  if (decoded == null) {
    throw const FormatException('Format gambar tidak didukung.');
  }
  // Putar sesuai EXIF agar foto kamera tidak miring.
  var image = img.bakeOrientation(decoded);
  if (math.max(image.width, image.height) > _maxSavedSide) {
    image = image.width >= image.height
        ? img.copyResize(image, width: _maxSavedSide)
        : img.copyResize(image, height: _maxSavedSide);
  }
  File(save).writeAsBytesSync(img.encodeJpg(image, quality: 88));

  if (interpreterAddress == null) {
    return _JobResult(image.width, image.height, _demoDetections(image));
  }

  // Tensor sudah dialokasikan di isolate utama (lihat load()).
  final interpreter =
      Interpreter.fromAddress(interpreterAddress, allocated: true);
  final inputTensor = interpreter.getInputTensor(0);
  final inputSize = inputTensor.shape[1];
  final lb = Letterbox(
    srcWidth: image.width,
    srcHeight: image.height,
    inputSize: inputSize,
  );

  // Letterbox: skala proporsional + padding abu-abu (114) seperti saat training.
  final canvas = img.Image(width: inputSize, height: inputSize)
    ..clear(img.ColorRgb8(114, 114, 114));
  img.compositeImage(
    canvas,
    img.copyResize(
      image,
      width: lb.scaledWidth,
      height: lb.scaledHeight,
      interpolation: img.Interpolation.linear,
    ),
    dstX: lb.padX,
    dstY: lb.padY,
  );
  final rgb = canvas.getBytes(order: img.ChannelOrder.rgb);
  final input = Float32List(rgb.length);
  for (var i = 0; i < rgb.length; i++) {
    input[i] = rgb[i] / 255.0;
  }

  inputTensor.data = input.buffer.asUint8List();
  interpreter.invoke();

  final outputTensor = interpreter.getOutputTensor(0);
  // Salin ke buffer baru agar offset selalu sejajar 4 byte untuk float32.
  final output = Uint8List.fromList(outputTensor.data).buffer.asFloat32List();
  final detections = decodeYolov8(
    output: output,
    shape: outputTensor.shape,
    numClasses: WasteClass.values.length,
    letterbox: lb,
  );
  return _JobResult(image.width, image.height, detections);
}

/// Hasil tiruan yang stabil untuk gambar yang sama (mode demo).
List<RawDetection> _demoDetections(img.Image image) {
  final p = image.getPixel(image.width ~/ 2, image.height ~/ 2);
  final rng = math.Random(image.width * 31 + image.height + p.r.toInt() * 7);
  final count = 1 + rng.nextInt(2);
  return List.generate(count, (i) {
    final w = 0.35 + rng.nextDouble() * 0.25;
    final h = 0.3 + rng.nextDouble() * 0.3;
    final l = i == 0 ? (1 - w) / 2 : rng.nextDouble() * (1 - w);
    final t = i == 0 ? (1 - h) / 2 : rng.nextDouble() * (1 - h);
    return RawDetection(
      rng.nextInt(WasteClass.values.length),
      0.62 + rng.nextDouble() * 0.33,
      l,
      t,
      l + w,
      t + h,
    );
  })
    ..sort((a, b) => b.score.compareTo(a.score));
}
