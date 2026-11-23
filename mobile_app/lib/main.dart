import 'package:flutter/material.dart';

import 'screens/shell.dart';
import 'state/app_controller.dart';
import 'theme.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final controller = await AppController.init();
  runApp(TrashScanApp(controller: controller));
}

class TrashScanApp extends StatelessWidget {
  const TrashScanApp({super.key, required this.controller});

  final AppController controller;

  @override
  Widget build(BuildContext context) {
    return AppScope(
      controller: controller,
      child: MaterialApp(
        title: 'TrashScan',
        debugShowCheckedModeBanner: false,
        theme: buildTheme(Brightness.light),
        darkTheme: buildTheme(Brightness.dark),
        home: const Shell(),
      ),
    );
  }
}
