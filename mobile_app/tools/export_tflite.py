"""Ekspor model YOLOv8 (best.pt) ke TFLite untuk aplikasi TrashScan.

Pemakaian (dari root repo Trash-Classification):

    pip install ultralytics tensorflow
    python mobile_app/tools/export_tflite.py runs/detect/train/weights/best.pt

Hasilnya disalin ke mobile_app/assets/models/trash_yolov8.tflite, lalu
aplikasi otomatis keluar dari mode demo saat dijalankan ulang.
"""

import argparse
import shutil
from pathlib import Path

from ultralytics import YOLO

EXPECTED_CLASSES = ['BIODEGRADABLE', 'CARDBOARD', 'GLASS', 'METAL', 'PAPER', 'PLASTIC']
TARGET = Path(__file__).resolve().parents[1] / 'assets' / 'models' / 'trash_yolov8.tflite'


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('weights', help='Path ke best.pt hasil training')
    parser.add_argument('--imgsz', type=int, default=640)
    parser.add_argument('--half', action='store_true',
                        help='Bobot float16: ukuran file ~separuh, input/output tetap float32')
    args = parser.parse_args()

    model = YOLO(args.weights)
    names = [model.names[i].upper() for i in sorted(model.names)]
    if names != EXPECTED_CLASSES:
        print(f'PERINGATAN: urutan kelas model {names} berbeda dengan '
              f'yang dipakai aplikasi {EXPECTED_CLASSES}. '
              'Sesuaikan enum WasteClass di lib/models/waste_class.dart.')

    # Tanpa NMS: NMS dijalankan di Dart (lib/services/yolo_postprocess.dart).
    exported = Path(model.export(format='tflite', imgsz=args.imgsz, half=args.half))
    if exported.is_dir():
        suffix = 'float16' if args.half else 'float32'
        exported = next(exported.glob(f'*_{suffix}.tflite'))

    TARGET.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(exported, TARGET)
    print(f'Model disalin ke {TARGET} ({TARGET.stat().st_size / 1e6:.1f} MB)')


if __name__ == '__main__':
    main()
