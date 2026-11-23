# Model

Letakkan model hasil ekspor di sini dengan nama `trash_yolov8.tflite`:

```bash
python mobile_app/tools/export_tflite.py runs/detect/train/weights/best.pt
```

Jika file ini tidak ada, aplikasi berjalan dalam **mode demo** (hasil deteksi acak).
