import 'dart:io';

import 'package:flutter/material.dart';

import '../models/scan_result.dart';

/// Menampilkan foto beserta bounding box hasil deteksi di atasnya.
class DetectionView extends StatelessWidget {
  const DetectionView({
    super.key,
    required this.image,
    required this.result,
    this.highlighted,
  });

  final File image;
  final ScanResult result;

  /// Indeks deteksi yang sedang disorot; deteksi lain dibuat samar.
  final int? highlighted;

  @override
  Widget build(BuildContext context) {
    return AspectRatio(
      aspectRatio: result.imageSize.width / result.imageSize.height,
      child: LayoutBuilder(
        builder: (context, constraints) {
          final w = constraints.maxWidth;
          final h = constraints.maxHeight;
          return Stack(
            children: [
              Positioned.fill(
                child: Image.file(image, fit: BoxFit.cover),
              ),
              for (var i = 0; i < result.detections.length; i++)
                _Box(
                  detection: result.detections[i],
                  width: w,
                  height: h,
                  dimmed: highlighted != null && highlighted != i,
                ),
            ],
          );
        },
      ),
    );
  }
}

class _Box extends StatelessWidget {
  const _Box({
    required this.detection,
    required this.width,
    required this.height,
    required this.dimmed,
  });

  final Detection detection;
  final double width;
  final double height;
  final bool dimmed;

  @override
  Widget build(BuildContext context) {
    final color = detection.wasteClass.color;
    final b = detection.box;
    return AnimatedPositioned(
      duration: const Duration(milliseconds: 250),
      left: b.left * width,
      top: b.top * height,
      width: b.width * width,
      height: b.height * height,
      child: AnimatedOpacity(
        duration: const Duration(milliseconds: 200),
        opacity: dimmed ? 0.35 : 1,
        child: Container(
          decoration: BoxDecoration(
            border: Border.all(color: color, width: 3),
            borderRadius: BorderRadius.circular(10),
          ),
          alignment: Alignment.topLeft,
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
            decoration: BoxDecoration(
              color: color,
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(6),
                bottomRight: Radius.circular(8),
              ),
            ),
            child: Text(
              '${detection.wasteClass.label} '
              '${(detection.confidence * 100).round()}%',
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 12,
                fontWeight: FontWeight.w700,
              ),
            ),
          ),
        ),
      ),
    );
  }
}

/// Lencana kecil bulat berisi ikon kelas sampah.
class ClassAvatar extends StatelessWidget {
  const ClassAvatar({
    super.key,
    required this.color,
    required this.icon,
    this.size = 44,
  });

  final Color color;
  final IconData icon;
  final double size;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.15),
        borderRadius: BorderRadius.circular(size * 0.32),
      ),
      child: Icon(icon, color: color, size: size * 0.55),
    );
  }
}
