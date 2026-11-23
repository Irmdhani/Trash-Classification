import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

import '../state/app_controller.dart';
import 'guide_screen.dart';
import 'history_screen.dart';
import 'home_screen.dart';
import 'result_screen.dart';

/// Kerangka utama dengan navigasi bawah (Beranda, Riwayat, Panduan).
class Shell extends StatefulWidget {
  const Shell({super.key});

  @override
  State<Shell> createState() => _ShellState();
}

class _ShellState extends State<Shell> {
  int _tab = 0;
  bool _busy = false;
  final _picker = ImagePicker();

  Future<void> _scan(ImageSource source) async {
    if (_busy) return;
    final controller = AppScope.of(context);
    final navigator = Navigator.of(context);
    final messenger = ScaffoldMessenger.of(context);

    final XFile? file;
    try {
      file = await _picker.pickImage(source: source, maxWidth: 2048);
    } catch (e) {
      messenger.showSnackBar(
        SnackBar(content: Text('Tidak bisa membuka ${source == ImageSource.camera ? 'kamera' : 'galeri'}: $e')),
      );
      return;
    }
    if (file == null) return;

    setState(() => _busy = true);
    try {
      final result = await controller.scan(file.path);
      if (!mounted) return;
      await navigator.push(
        MaterialPageRoute(builder: (_) => ResultScreen(result: result)),
      );
    } catch (e) {
      messenger.showSnackBar(SnackBar(content: Text('Deteksi gagal: $e')));
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final pages = [
      HomeScreen(onScan: _scan, onOpenHistory: () => setState(() => _tab = 1)),
      const HistoryScreen(),
      const GuideScreen(),
    ];

    return Stack(
      children: [
        Scaffold(
          body: IndexedStack(index: _tab, children: pages),
          bottomNavigationBar: NavigationBar(
            selectedIndex: _tab,
            onDestinationSelected: (i) => setState(() => _tab = i),
            destinations: const [
              NavigationDestination(
                icon: Icon(Icons.home_outlined),
                selectedIcon: Icon(Icons.home_rounded),
                label: 'Beranda',
              ),
              NavigationDestination(
                icon: Icon(Icons.history_outlined),
                selectedIcon: Icon(Icons.history_rounded),
                label: 'Riwayat',
              ),
              NavigationDestination(
                icon: Icon(Icons.menu_book_outlined),
                selectedIcon: Icon(Icons.menu_book_rounded),
                label: 'Panduan',
              ),
            ],
          ),
        ),
        if (_busy) const _AnalyzingOverlay(),
      ],
    );
  }
}

class _AnalyzingOverlay extends StatelessWidget {
  const _AnalyzingOverlay();

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Positioned.fill(
      child: ColoredBox(
        color: Colors.black54,
        child: Center(
          child: Card(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 28),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  CircularProgressIndicator(color: scheme.primary),
                  const SizedBox(height: 20),
                  Text(
                    'Menganalisis sampah…',
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
