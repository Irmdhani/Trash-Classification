import 'package:flutter/material.dart';

import '../models/scan_result.dart';
import '../models/waste_class.dart';
import '../state/app_controller.dart';
import '../widgets/detection_view.dart';
import 'guide_screen.dart';

class ResultScreen extends StatefulWidget {
  const ResultScreen({super.key, required this.result});

  final ScanResult result;

  @override
  State<ResultScreen> createState() => _ResultScreenState();
}

class _ResultScreenState extends State<ResultScreen> {
  int? _selected;

  Future<void> _delete() async {
    final ok = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Hapus hasil ini?'),
        content: const Text('Foto dan hasil deteksi akan dihapus dari riwayat.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Batal'),
          ),
          FilledButton.tonal(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Hapus'),
          ),
        ],
      ),
    );
    if (ok != true || !mounted) return;
    await AppScope.of(context).delete(widget.result);
    if (mounted) Navigator.of(context).pop();
  }

  @override
  Widget build(BuildContext context) {
    final app = AppScope.of(context);
    final r = widget.result;
    final text = Theme.of(context).textTheme;
    final scheme = Theme.of(context).colorScheme;
    final focus = _selected != null ? r.detections[_selected!] : r.primary;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Hasil Deteksi'),
        actions: [
          IconButton(
            tooltip: 'Hapus',
            onPressed: _delete,
            icon: const Icon(Icons.delete_outline),
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(20, 8, 20, 32),
        children: [
          ConstrainedBox(
            constraints: BoxConstraints(
              maxHeight: MediaQuery.sizeOf(context).height * 0.5,
            ),
            // heightFactor 1: tinggi mengikuti foto, tanpa ruang kosong.
            child: Center(
              heightFactor: 1,
              child: ClipRRect(
                borderRadius: BorderRadius.circular(24),
                child: DetectionView(
                  image: app.imageFor(r),
                  result: r,
                  highlighted: _selected,
                ),
              ),
            ),
          ),
          if (r.isDemo) ...[
            const SizedBox(height: 12),
            Row(
              children: [
                Icon(Icons.science_outlined,
                    size: 16, color: scheme.onSurfaceVariant),
                const SizedBox(width: 6),
                Expanded(
                  child: Text(
                    'Hasil demo: model belum dipasang.',
                    style: text.bodySmall
                        ?.copyWith(color: scheme.onSurfaceVariant),
                  ),
                ),
              ],
            ),
          ],
          const SizedBox(height: 20),
          if (focus == null)
            const _EmptyResult()
          else ...[
            _BinCard(wasteClass: focus.wasteClass),
            const SizedBox(height: 24),
            Text(
              '${r.detections.length} objek terdeteksi',
              style: text.titleMedium?.copyWith(fontWeight: FontWeight.w700),
            ),
            const SizedBox(height: 8),
            for (var i = 0; i < r.detections.length; i++)
              _DetectionTile(
                detection: r.detections[i],
                selected: _selected == i,
                onTap: () =>
                    setState(() => _selected = _selected == i ? null : i),
              ),
            const SizedBox(height: 20),
            _TipsCard(wasteClass: focus.wasteClass),
          ],
          const SizedBox(height: 24),
          FilledButton.icon(
            onPressed: () => Navigator.of(context).pop(),
            icon: const Icon(Icons.photo_camera_rounded),
            label: const Text('Pindai Lagi'),
          ),
        ],
      ),
    );
  }
}

class _BinCard extends StatelessWidget {
  const _BinCard({required this.wasteClass});

  final WasteClass wasteClass;

  @override
  Widget build(BuildContext context) {
    final bin = wasteClass.bin;
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: bin.color,
        borderRadius: BorderRadius.circular(22),
      ),
      child: Row(
        children: [
          Container(
            width: 56,
            height: 56,
            decoration: BoxDecoration(
              color: Colors.white.withValues(alpha: 0.2),
              borderRadius: BorderRadius.circular(16),
            ),
            child: const Icon(Icons.delete_rounded, color: Colors.white, size: 32),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Buang ke',
                  style: TextStyle(color: Colors.white.withValues(alpha: 0.85)),
                ),
                Text(
                  bin.description,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 20,
                    fontWeight: FontWeight.w800,
                  ),
                ),
                Text(
                  'Kategori ${bin.label} · ${wasteClass.label}',
                  style: TextStyle(color: Colors.white.withValues(alpha: 0.85)),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _DetectionTile extends StatelessWidget {
  const _DetectionTile({
    required this.detection,
    required this.selected,
    required this.onTap,
  });

  final Detection detection;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final c = detection.wasteClass;
    final scheme = Theme.of(context).colorScheme;
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Material(
        color: selected
            ? c.color.withValues(alpha: 0.12)
            : scheme.surfaceContainerLow,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
          side: BorderSide(
            color: selected ? c.color : Colors.transparent,
            width: 1.5,
          ),
        ),
        child: InkWell(
          borderRadius: BorderRadius.circular(16),
          onTap: onTap,
          child: Padding(
            padding: const EdgeInsets.all(12),
            child: Row(
              children: [
                ClassAvatar(color: c.color, icon: c.icon),
                const SizedBox(width: 14),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(c.label,
                          style: const TextStyle(
                              fontWeight: FontWeight.w700, fontSize: 16)),
                      const SizedBox(height: 6),
                      ClipRRect(
                        borderRadius: BorderRadius.circular(4),
                        child: LinearProgressIndicator(
                          value: detection.confidence,
                          minHeight: 6,
                          color: c.color,
                          backgroundColor: c.color.withValues(alpha: 0.15),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 14),
                Text(
                  '${(detection.confidence * 100).round()}%',
                  style: TextStyle(
                    fontWeight: FontWeight.w800,
                    color: c.color,
                    fontSize: 16,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _TipsCard extends StatelessWidget {
  const _TipsCard({required this.wasteClass});

  final WasteClass wasteClass;

  @override
  Widget build(BuildContext context) {
    final text = Theme.of(context).textTheme;
    final scheme = Theme.of(context).colorScheme;
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.lightbulb_outline, color: wasteClass.color),
                const SizedBox(width: 8),
                Text('Tips ${wasteClass.label}',
                    style: text.titleMedium
                        ?.copyWith(fontWeight: FontWeight.w700)),
              ],
            ),
            const SizedBox(height: 12),
            for (final tip in wasteClass.tips)
              Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Padding(
                      padding: const EdgeInsets.only(top: 3),
                      child: Icon(Icons.check_circle,
                          size: 16, color: wasteClass.color),
                    ),
                    const SizedBox(width: 10),
                    Expanded(child: Text(tip, style: const TextStyle(height: 1.35))),
                  ],
                ),
              ),
            const Divider(height: 24),
            Row(
              children: [
                Icon(Icons.hourglass_bottom_rounded,
                    size: 18, color: scheme.onSurfaceVariant),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    'Waktu terurai: ${wasteClass.decomposeTime}',
                    style: text.bodyMedium
                        ?.copyWith(color: scheme.onSurfaceVariant),
                  ),
                ),
                TextButton(
                  onPressed: () => Navigator.of(context).push(
                    MaterialPageRoute(
                      builder: (_) => ClassDetailScreen(wasteClass: wasteClass),
                    ),
                  ),
                  child: const Text('Selengkapnya'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _EmptyResult extends StatelessWidget {
  const _EmptyResult();

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            Icon(Icons.search_off_rounded,
                size: 48, color: scheme.onSurfaceVariant),
            const SizedBox(height: 12),
            Text('Sampah tidak terdeteksi',
                style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 6),
            Text(
              'Coba foto lebih dekat dengan pencahayaan yang cukup, '
              'dan pastikan objek terlihat jelas.',
              textAlign: TextAlign.center,
              style: TextStyle(color: scheme.onSurfaceVariant),
            ),
          ],
        ),
      ),
    );
  }
}
