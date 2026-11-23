import 'dart:math' as math;
import 'dart:typed_data';

/// Posisi gambar asli di dalam kanvas input model (letterbox ala Ultralytics).
class Letterbox {
  const Letterbox({
    required this.srcWidth,
    required this.srcHeight,
    required this.inputSize,
  });

  final int srcWidth;
  final int srcHeight;
  final int inputSize;

  double get scale =>
      math.min(inputSize / srcWidth, inputSize / srcHeight);
  int get scaledWidth => (srcWidth * scale).round();
  int get scaledHeight => (srcHeight * scale).round();
  int get padX => (inputSize - scaledWidth) ~/ 2;
  int get padY => (inputSize - scaledHeight) ~/ 2;
}

/// Deteksi mentah: indeks kelas, skor, dan kotak ternormalisasi 0..1
/// terhadap gambar asli (left, top, right, bottom).
class RawDetection {
  const RawDetection(this.classIndex, this.score, this.l, this.t, this.r, this.b);

  final int classIndex;
  final double score;
  final double l, t, r, b;

  double get area => math.max(0, r - l) * math.max(0, b - t);
}

/// Mendekode output YOLOv8 hasil `model.export(format='tflite')`.
///
/// Bentuk output yang didukung: `[1, 4 + nc, N]` (bawaan Ultralytics) atau
/// `[1, N, 4 + nc]`. Kotak berformat cx, cy, w, h — bisa dalam piksel input
/// atau sudah dinormalisasi 0..1 (Ultralytics >= 8.1); keduanya ditangani.
List<RawDetection> decodeYolov8({
  required Float32List output,
  required List<int> shape,
  required int numClasses,
  required Letterbox letterbox,
  double confThreshold = 0.35,
  double iouThreshold = 0.45,
  int maxDetections = 20,
}) {
  if (shape.length != 3) {
    throw ArgumentError('Bentuk output tidak dikenal: $shape');
  }
  final attrs = 4 + numClasses;
  final channelsFirst = shape[1] == attrs;
  if (!channelsFirst && shape[2] != attrs) {
    throw ArgumentError(
      'Output model $shape tidak cocok dengan $numClasses kelas.',
    );
  }
  final n = channelsFirst ? shape[2] : shape[1];
  double v(int attr, int i) =>
      channelsFirst ? output[attr * n + i] : output[i * attrs + attr];

  // Deteksi apakah koordinat sudah dinormalisasi.
  var maxCoord = 0.0;
  for (var i = 0; i < n; i++) {
    final c = v(0, i);
    if (c > maxCoord) maxCoord = c;
  }
  final coordScale = maxCoord <= 1.5 ? letterbox.inputSize.toDouble() : 1.0;

  final candidates = <RawDetection>[];
  for (var i = 0; i < n; i++) {
    var best = -1;
    var bestScore = confThreshold;
    for (var c = 0; c < numClasses; c++) {
      final s = v(4 + c, i);
      if (s > bestScore) {
        bestScore = s;
        best = c;
      }
    }
    if (best < 0) continue;

    final cx = v(0, i) * coordScale;
    final cy = v(1, i) * coordScale;
    final w = v(2, i) * coordScale;
    final h = v(3, i) * coordScale;

    // Kembalikan dari ruang letterbox ke gambar asli, lalu normalisasi.
    double nx(double x) =>
        ((x - letterbox.padX) / letterbox.scale / letterbox.srcWidth)
            .clamp(0.0, 1.0);
    double ny(double y) =>
        ((y - letterbox.padY) / letterbox.scale / letterbox.srcHeight)
            .clamp(0.0, 1.0);

    final det = RawDetection(
      best,
      bestScore,
      nx(cx - w / 2),
      ny(cy - h / 2),
      nx(cx + w / 2),
      ny(cy + h / 2),
    );
    if (det.area > 0) candidates.add(det);
  }

  return nonMaxSuppression(candidates, iouThreshold, maxDetections);
}

/// NMS per kelas, seperti perilaku default Ultralytics.
List<RawDetection> nonMaxSuppression(
  List<RawDetection> dets,
  double iouThreshold,
  int maxDetections,
) {
  final sorted = [...dets]..sort((a, b) => b.score.compareTo(a.score));
  final kept = <RawDetection>[];
  for (final d in sorted) {
    final overlaps = kept.any(
      (k) => k.classIndex == d.classIndex && iou(k, d) > iouThreshold,
    );
    if (!overlaps) kept.add(d);
    if (kept.length >= maxDetections) break;
  }
  return kept;
}

double iou(RawDetection a, RawDetection b) {
  final l = math.max(a.l, b.l);
  final t = math.max(a.t, b.t);
  final r = math.min(a.r, b.r);
  final bo = math.min(a.b, b.b);
  final inter = math.max(0, r - l) * math.max(0, bo - t);
  final union = a.area + b.area - inter;
  return union <= 0 ? 0 : inter / union;
}
