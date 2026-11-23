import 'package:flutter/material.dart';

import '../models/waste_class.dart';
import '../widgets/detection_view.dart';

class GuideScreen extends StatelessWidget {
  const GuideScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final text = Theme.of(context).textTheme;
    final scheme = Theme.of(context).colorScheme;

    return Scaffold(
      appBar: AppBar(title: const Text('Panduan Pilah')),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(20, 8, 20, 24),
        children: [
          Text(
            'Tiga tempat sampah utama',
            style: text.titleMedium?.copyWith(fontWeight: FontWeight.w700),
          ),
          const SizedBox(height: 12),
          IntrinsicHeight(
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                for (final bin in WasteBin.values) ...[
                  Expanded(child: _BinChip(bin: bin)),
                  if (bin != WasteBin.values.last) const SizedBox(width: 10),
                ],
              ],
            ),
          ),
          const SizedBox(height: 28),
          Text(
            'Jenis sampah yang dikenali',
            style: text.titleMedium?.copyWith(fontWeight: FontWeight.w700),
          ),
          const SizedBox(height: 4),
          Text(
            'Model YOLOv8 dilatih untuk 6 kelas berikut.',
            style: text.bodyMedium?.copyWith(color: scheme.onSurfaceVariant),
          ),
          const SizedBox(height: 12),
          GridView.count(
            crossAxisCount: 2,
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            mainAxisSpacing: 12,
            crossAxisSpacing: 12,
            childAspectRatio: 1.05,
            children: [
              for (final c in WasteClass.values) _ClassCard(wasteClass: c),
            ],
          ),
        ],
      ),
    );
  }
}

class _BinChip extends StatelessWidget {
  const _BinChip({required this.bin});

  final WasteBin bin;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: bin.color,
        borderRadius: BorderRadius.circular(18),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Icon(Icons.delete_rounded, color: Colors.white),
          const SizedBox(height: 8),
          Text(
            bin.label,
            style: const TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.w800,
              fontSize: 15,
            ),
          ),
          const SizedBox(height: 2),
          Text(
            bin.examples,
            style: TextStyle(
              color: Colors.white.withValues(alpha: 0.85),
              fontSize: 12,
            ),
          ),
        ],
      ),
    );
  }
}

class _ClassCard extends StatelessWidget {
  const _ClassCard({required this.wasteClass});

  final WasteClass wasteClass;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Card(
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: () => Navigator.of(context).push(
          MaterialPageRoute(
            builder: (_) => ClassDetailScreen(wasteClass: wasteClass),
          ),
        ),
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              ClassAvatar(color: wasteClass.color, icon: wasteClass.icon),
              const Spacer(),
              Text(
                wasteClass.label,
                style:
                    const TextStyle(fontWeight: FontWeight.w800, fontSize: 17),
              ),
              const SizedBox(height: 2),
              Text(
                wasteClass.bin.description,
                style: TextStyle(color: scheme.onSurfaceVariant, fontSize: 12),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class ClassDetailScreen extends StatelessWidget {
  const ClassDetailScreen({super.key, required this.wasteClass});

  final WasteClass wasteClass;

  @override
  Widget build(BuildContext context) {
    final c = wasteClass;
    final text = Theme.of(context).textTheme;
    final scheme = Theme.of(context).colorScheme;

    return Scaffold(
      appBar: AppBar(title: Text(c.label)),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(20, 8, 20, 24),
        children: [
          Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: c.color.withValues(alpha: 0.12),
              borderRadius: BorderRadius.circular(24),
            ),
            child: Column(
              children: [
                ClassAvatar(color: c.color, icon: c.icon, size: 80),
                const SizedBox(height: 16),
                Text(c.description,
                    textAlign: TextAlign.center,
                    style: text.bodyLarge?.copyWith(height: 1.4)),
              ],
            ),
          ),
          const SizedBox(height: 16),
          Card(
            child: Column(
              children: [
                ListTile(
                  leading: Icon(Icons.delete_rounded, color: c.bin.color),
                  title: const Text('Tempat buang'),
                  subtitle: Text('${c.bin.description} (${c.bin.label})'),
                ),
                const Divider(height: 1, indent: 16, endIndent: 16),
                ListTile(
                  leading: Icon(Icons.hourglass_bottom_rounded,
                      color: scheme.onSurfaceVariant),
                  title: const Text('Waktu terurai di alam'),
                  subtitle: Text(c.decomposeTime),
                ),
                const Divider(height: 1, indent: 16, endIndent: 16),
                ListTile(
                  leading: Icon(Icons.label_outline,
                      color: scheme.onSurfaceVariant),
                  title: const Text('Label kelas model'),
                  subtitle: Text(c.modelName),
                ),
              ],
            ),
          ),
          const SizedBox(height: 20),
          Text('Cara mengelola',
              style: text.titleMedium?.copyWith(fontWeight: FontWeight.w700)),
          const SizedBox(height: 10),
          for (final (i, tip) in c.tips.indexed)
            Padding(
              padding: const EdgeInsets.only(bottom: 10),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  CircleAvatar(
                    radius: 13,
                    backgroundColor: c.color,
                    child: Text('${i + 1}',
                        style: const TextStyle(
                            color: Colors.white,
                            fontSize: 12,
                            fontWeight: FontWeight.w700)),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Padding(
                      padding: const EdgeInsets.only(top: 3),
                      child: Text(tip, style: const TextStyle(height: 1.35)),
                    ),
                  ),
                ],
              ),
            ),
        ],
      ),
    );
  }
}
