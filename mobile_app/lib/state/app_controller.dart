import 'dart:convert';
import 'dart:io';

import 'package:flutter/widgets.dart';
import 'package:path_provider/path_provider.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../models/scan_result.dart';
import '../models/waste_class.dart';
import '../services/trash_detector.dart';

/// State aplikasi: detektor, folder penyimpanan, dan riwayat pemindaian.
class AppController extends ChangeNotifier {
  AppController._(this.detector, this._prefs, this._scanDir, this._history);

  static const _historyKey = 'scan_history_v1';

  final TrashDetector detector;
  final SharedPreferences _prefs;
  final Directory _scanDir;
  final List<ScanResult> _history;

  static Future<AppController> init() async {
    final results = await Future.wait([
      TrashDetector.load(),
      SharedPreferences.getInstance(),
      getApplicationDocumentsDirectory(),
    ]);
    final prefs = results[1] as SharedPreferences;
    final scanDir = Directory('${(results[2] as Directory).path}/scans');
    await scanDir.create(recursive: true);

    final history = <ScanResult>[];
    for (final raw in prefs.getStringList(_historyKey) ?? const <String>[]) {
      try {
        history.add(ScanResult.fromJson(jsonDecode(raw) as Map<String, dynamic>));
      } catch (_) {
        // Lewati entri lama yang rusak.
      }
    }
    return AppController._(
      results[0] as TrashDetector,
      prefs,
      scanDir,
      history,
    );
  }

  List<ScanResult> get history => List.unmodifiable(_history);

  File imageFor(ScanResult r) => File('${_scanDir.path}/${r.imageFile}');

  int get totalItems =>
      _history.fold(0, (sum, r) => sum + r.detections.length);

  /// Jumlah objek per kelas di seluruh riwayat.
  Map<WasteClass, int> get countsByClass {
    final counts = {for (final c in WasteClass.values) c: 0};
    for (final r in _history) {
      for (final d in r.detections) {
        counts[d.wasteClass] = counts[d.wasteClass]! + 1;
      }
    }
    return counts;
  }

  Future<ScanResult> scan(String sourcePath) async {
    final name = 'scan_${DateTime.now().millisecondsSinceEpoch}.jpg';
    final result = await detector.scan(
      sourcePath: sourcePath,
      savePath: '${_scanDir.path}/$name',
    );
    _history.insert(0, result);
    await _persist();
    notifyListeners();
    return result;
  }

  Future<void> delete(ScanResult r) async {
    _history.removeWhere((e) => e.id == r.id);
    final file = imageFor(r);
    if (await file.exists()) await file.delete();
    await _persist();
    notifyListeners();
  }

  Future<void> clearHistory() async {
    for (final r in List.of(_history)) {
      final file = imageFor(r);
      if (await file.exists()) await file.delete();
    }
    _history.clear();
    await _persist();
    notifyListeners();
  }

  Future<void> _persist() => _prefs.setStringList(
        _historyKey,
        _history.map((r) => jsonEncode(r.toJson())).toList(),
      );

  @override
  void dispose() {
    detector.dispose();
    super.dispose();
  }
}

/// Menyediakan [AppController] ke seluruh widget tree.
class AppScope extends InheritedNotifier<AppController> {
  const AppScope({
    super.key,
    required AppController controller,
    required super.child,
  }) : super(notifier: controller);

  static AppController of(BuildContext context) =>
      context.dependOnInheritedWidgetOfExactType<AppScope>()!.notifier!;
}
