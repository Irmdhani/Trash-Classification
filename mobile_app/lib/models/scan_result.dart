import 'dart:ui';

import 'waste_class.dart';

/// Satu objek sampah yang terdeteksi. [box] dinormalisasi 0..1 terhadap
/// lebar dan tinggi gambar asli.
class Detection {
  const Detection({
    required this.wasteClass,
    required this.confidence,
    required this.box,
  });

  final WasteClass wasteClass;
  final double confidence;
  final Rect box;

  Map<String, dynamic> toJson() => {
        'c': wasteClass.index,
        'p': confidence,
        'b': [box.left, box.top, box.right, box.bottom],
      };

  factory Detection.fromJson(Map<String, dynamic> json) {
    final b = (json['b'] as List).cast<num>();
    return Detection(
      wasteClass: WasteClass.fromIndex(json['c'] as int),
      confidence: (json['p'] as num).toDouble(),
      box: Rect.fromLTRB(
        b[0].toDouble(),
        b[1].toDouble(),
        b[2].toDouble(),
        b[3].toDouble(),
      ),
    );
  }
}

/// Hasil satu kali pemindaian, disimpan di riwayat.
class ScanResult {
  const ScanResult({
    required this.id,
    required this.imageFile,
    required this.imageSize,
    required this.createdAt,
    required this.detections,
    required this.isDemo,
  });

  final String id;

  /// Nama file di folder dokumen aplikasi (bukan path absolut, karena path
  /// container iOS berubah setiap kali aplikasi diperbarui).
  final String imageFile;
  final Size imageSize;
  final DateTime createdAt;
  final List<Detection> detections;

  /// True jika hasil berasal dari detektor demo (model belum dipasang).
  final bool isDemo;

  /// Kelas dengan confidence tertinggi, atau null bila tidak ada deteksi.
  Detection? get primary => detections.isEmpty
      ? null
      : detections.reduce((a, b) => a.confidence >= b.confidence ? a : b);

  Map<String, dynamic> toJson() => {
        'id': id,
        'img': imageFile,
        'w': imageSize.width,
        'h': imageSize.height,
        't': createdAt.toIso8601String(),
        'd': detections.map((d) => d.toJson()).toList(),
        'demo': isDemo,
      };

  factory ScanResult.fromJson(Map<String, dynamic> json) => ScanResult(
        id: json['id'] as String,
        imageFile: json['img'] as String,
        imageSize: Size(
          (json['w'] as num).toDouble(),
          (json['h'] as num).toDouble(),
        ),
        createdAt: DateTime.parse(json['t'] as String),
        detections: (json['d'] as List)
            .map((e) => Detection.fromJson(e as Map<String, dynamic>))
            .toList(),
        isDemo: json['demo'] as bool? ?? false,
      );
}
