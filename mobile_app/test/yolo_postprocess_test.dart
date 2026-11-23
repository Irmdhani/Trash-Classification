import 'dart:typed_data';
import 'dart:ui';

import 'package:flutter_test/flutter_test.dart';
import 'package:trash_scan/models/scan_result.dart';
import 'package:trash_scan/models/waste_class.dart';
import 'package:trash_scan/services/yolo_postprocess.dart';

/// Membuat output tiruan berbentuk [1, 4 + nc, n] (channels-first).
Float32List fakeOutput(List<List<double>> anchors, {int nc = 6}) {
  final attrs = 4 + nc;
  final n = anchors.length;
  final out = Float32List(attrs * n);
  for (var i = 0; i < n; i++) {
    for (var a = 0; a < attrs; a++) {
      out[a * n + i] = anchors[i][a];
    }
  }
  return out;
}

List<double> anchor(double cx, double cy, double w, double h, int cls, double score) =>
    [cx, cy, w, h, for (var c = 0; c < 6; c++) c == cls ? score : 0.01];

void main() {
  const square = Letterbox(srcWidth: 640, srcHeight: 640, inputSize: 640);

  test('mendekode kotak piksel dan menormalisasi ke gambar asli', () {
    final dets = decodeYolov8(
      output: fakeOutput([anchor(320, 320, 128, 64, 5, 0.9)]),
      shape: const [1, 10, 1],
      numClasses: 6,
      letterbox: square,
    );
    expect(dets, hasLength(1));
    expect(dets.first.classIndex, 5);
    expect(dets.first.l, closeTo(0.4, 1e-6));
    expect(dets.first.t, closeTo(0.45, 1e-6));
    expect(dets.first.r, closeTo(0.6, 1e-6));
  });

  test('menerima koordinat yang sudah dinormalisasi 0..1', () {
    final dets = decodeYolov8(
      output: fakeOutput([anchor(0.5, 0.5, 0.2, 0.1, 2, 0.8)]),
      shape: const [1, 10, 1],
      numClasses: 6,
      letterbox: square,
    );
    expect(dets.single.l, closeTo(0.4, 1e-6));
    expect(dets.single.b, closeTo(0.55, 1e-6));
  });

  test('membalik letterbox untuk gambar potret', () {
    // 480x640 -> skala 1.0, padding kiri-kanan 80 px.
    const lb = Letterbox(srcWidth: 480, srcHeight: 640, inputSize: 640);
    final dets = decodeYolov8(
      output: fakeOutput([anchor(320, 320, 240, 320, 0, 0.7)]),
      shape: const [1, 10, 1],
      numClasses: 6,
      letterbox: lb,
    );
    expect(lb.padX, 80);
    expect(dets.single.l, closeTo(0.25, 1e-6));
    expect(dets.single.r, closeTo(0.75, 1e-6));
  });

  test('NMS membuang kotak tumpang tindih di kelas yang sama saja', () {
    final dets = decodeYolov8(
      output: fakeOutput([
        anchor(320, 320, 200, 200, 1, 0.9),
        anchor(325, 322, 200, 200, 1, 0.8), // duplikat -> dibuang
        anchor(325, 322, 200, 200, 3, 0.7), // kelas lain -> dipertahankan
        anchor(100, 100, 50, 50, 4, 0.2), // di bawah ambang
      ]),
      shape: const [1, 10, 4],
      numClasses: 6,
      letterbox: square,
    );
    expect(dets.map((d) => d.classIndex), [1, 3]);
  });

  test('mendukung output channels-last [1, n, 4 + nc]', () {
    final a = anchor(320, 320, 64, 64, 4, 0.6);
    final dets = decodeYolov8(
      output: Float32List.fromList(a),
      shape: const [1, 1, 10],
      numClasses: 6,
      letterbox: square,
    );
    expect(dets.single.classIndex, 4);
  });

  test('ScanResult tetap utuh setelah serialisasi JSON', () {
    final r = ScanResult(
      id: '1',
      imageFile: 'scan_1.jpg',
      imageSize: const Size(800, 600),
      createdAt: DateTime(2026, 11, 16, 9, 30),
      detections: const [
        Detection(
          wasteClass: WasteClass.glass,
          confidence: 0.4,
          box: Rect.fromLTRB(0.1, 0.2, 0.3, 0.4),
        ),
        Detection(
          wasteClass: WasteClass.metal,
          confidence: 0.9,
          box: Rect.fromLTRB(0.5, 0.5, 0.9, 0.9),
        ),
      ],
      isDemo: true,
    );
    final back = ScanResult.fromJson(r.toJson());
    expect(back.primary!.wasteClass, WasteClass.metal);
    expect(back.detections.first.box, r.detections.first.box);
    expect(back.isDemo, isTrue);
  });
}
