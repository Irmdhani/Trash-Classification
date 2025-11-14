import os
from collections import Counter
import numpy as np
from ultralytics import YOLO
import torch

print("=" * 80)
print("TRAINING YOLOV8S ON GARBAGE_CLASSIFICATION_CLAHE (6 Classes)")
print("=" * 80)

# ===== CONFIGURATION =====
DATASET_NAME = "GARBAGE_CLASSIFICATION_CLAHE"
YAML_PATH = "GARBAGE_CLASSIFICATION_clahe/data.yaml"
NUM_CLASSES = 6
CLASS_NAMES = ['BIODEGRADABLE', 'CARDBOARD', 'GLASS', 'METAL', 'PAPER', 'PLASTIC']
MODEL_NAME = "yolov8s"
EPOCHS = 150
BATCH_SIZE = 16
IMG_SIZE = 640
PATIENCE = 20

# Device detection
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"\nDevice: {device}")
if device == 'cuda':
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")

# ===== COMPUTE CLASS WEIGHTS (INFO ONLY) =====
print(f"\n[1/3] Computing class weights...")

label_dir = "GARBAGE_CLASSIFICATION_clahe/train/labels"

if not os.path.isdir(label_dir):
    print(f"✗ ERROR: Label directory not found: {label_dir}")
    exit(1)

cnt = Counter()
for fn in os.listdir(label_dir):
    if fn.endswith('.txt'):
        with open(os.path.join(label_dir, fn), 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split()
                if parts:
                    try:
                        cls = int(float(parts[0]))
                        if cls < NUM_CLASSES:
                            cnt[cls] += 1
                    except (ValueError, IndexError):
                        pass

counts_arr = np.array([cnt.get(i, 1.0) for i in range(NUM_CLASSES)], dtype=float)
counts_arr[counts_arr == 0] = 1.0
class_weights = (counts_arr.sum() / counts_arr).tolist()
class_weights = [w / sum(class_weights) * len(class_weights) for w in class_weights]

print(f"\nClass distribution (for reference):")
print("-" * 80)
for i, name in enumerate(CLASS_NAMES):
    count = cnt.get(i, 0)
    pct = (count / sum(cnt.values()) * 100) if sum(cnt.values()) > 0 else 0
    print(f"  {name:15s}: {count:6d} boxes ({pct:5.2f}%)")

# ===== LOAD MODEL =====
print(f"\n[2/3] Loading {MODEL_NAME} model...")
model = YOLO(f'{MODEL_NAME}.pt')
print(f"✓ {MODEL_NAME} model loaded")

# ===== TRAINING CONFIGURATION =====
print(f"\n[3/3] Starting training...")
print("-" * 80)
print(f"Dataset: {DATASET_NAME}")
print(f"Model: {MODEL_NAME}")
print(f"Image size: {IMG_SIZE}x{IMG_SIZE}")
print(f"Batch size: {BATCH_SIZE}")
print(f"Epochs: {EPOCHS}")
print(f"Device: {device}")
print("-" * 80)

# ===== TRAIN =====
results = model.train(
    data=YAML_PATH,
    epochs=EPOCHS,
    imgsz=IMG_SIZE,
    batch=BATCH_SIZE,
    lr0=1e-3,
    lrf=0.01,
    warmup_epochs=5,
    weight_decay=5e-4,
    optimizer='Adam',
    patience=PATIENCE,
    device=0 if device == 'cuda' else 'cpu',
    # ===== AUGMENTATIONS =====
    hsv_h=0.015,
    hsv_s=0.7,
    hsv_v=0.4,
    degrees=15.0,
    translate=0.15,
    scale=0.7,
    flipud=0.5,
    fliplr=0.5,
    mosaic=1.0,
    mixup=0.1,
    copy_paste=0.1,
    # ===== TRAINING =====
    verbose=True,
    save=True,
    plots=True,
    project='runs/detect',
    name='train',
    exist_ok=False,
    workers=4,
    fraction=1.0,
)

# ===== SUMMARY =====
print("\n" + "=" * 80)
print("TRAINING COMPLETE")
print("=" * 80)
print(f"\n✓ Best model: runs/detect/train/weights/best.pt")
print(f"✓ Results: runs/detect/train/results.csv")
print(f"✓ Plots: runs/detect/train/results.png")
print("\nNext steps:")
print("  1. Evaluate: python scripts/evaluate_realesrgan.py")
print("  2. Live test: python live_detection.py")
print(f"\n{'=' * 80}\n")