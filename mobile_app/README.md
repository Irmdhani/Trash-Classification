# TrashScan

Flutter app that detects and sorts household waste on-device with a YOLOv8 TensorFlow Lite model.

See the [project README](../README.md) for features, model details, and setup.

```bash
python tools/export_tflite.py path/to/best.pt --half   # adds assets/models/trash_yolov8.tflite
flutter pub get
flutter run
```

Without a model in `assets/models/`, the app runs in demo mode.
