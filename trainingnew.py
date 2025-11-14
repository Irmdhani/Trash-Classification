import os
from collections import Counter
import numpy as np
from ultralytics import YOLO
import torch

def main():
    """Main training function."""
    print("=" * 80)
    print("TRAINING YOLOV8S ON REAL-ESRGAN X4PLUS ENHANCED DATASET (6 Classes)")
    print("=" * 80)
    print("\n🖥️  SYSTEM SPECS:")
    print("  GPU: RTX 2060 6GB")
    print("  RAM: 16GB")
    print("  CPU: Ryzen 7 3750H (4C/8T)")
    print("  Storage: HDD")
    print("  Storage: SSD ⚡")  # ✅ Updated

    # ===== CONFIGURATION (OPTIMIZED FOR YOUR HARDWARE) =====
    DATASET_NAME = "GARBAGE_CLASSIFICATION_CLAHE_REALESRGAN_X4"
    YAML_PATH = "GARBAGE_CLASSIFICATION_clahe_realesrgan_x4/data.yaml"
    NUM_CLASSES = 6
    CLASS_NAMES = ['BIODEGRADABLE', 'CARDBOARD', 'GLASS', 'METAL', 'PAPER', 'PLASTIC']
    MODEL_NAME = "yolov8s"
    
    # ===== TUNED FOR RTX 2060 6GB =====
    EPOCHS = 150
    PATIENCE = 20
    BATCH_SIZE = 8  # ✅ SAFE: 12 → 8 (prevent OOM during image loading)
    IMG_SIZE = 640
    WORKERS = 2  # ✅ SAFE: 4 → 2 (reduce memory pressure from multiprocessing)

    # Device detection
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"\nDevice: {device}")
    if device == 'cuda':
        gpu_name = torch.cuda.get_device_name(0)
        gpu_mem = torch.cuda.get_device_properties(0).total_memory / 1e9
        print(f"GPU: {gpu_name}")
        print(f"GPU Memory: {gpu_mem:.1f} GB")
        print(f"CUDA Version: {torch.version.cuda}")

    # Check available RAM
    import psutil
    ram_available = psutil.virtual_memory().available / 1e9
    ram_total = psutil.virtual_memory().total / 1e9
    swap_total = psutil.swap_memory().total / 1e9
    print(f"\nRAM: {ram_available:.1f}GB free / {ram_total:.1f}GB total")
    print(f"Swap/Paging: {swap_total:.1f}GB")
    if swap_total < 8:
        print("⚠️  WARNING: Low paging file size may cause errors!")
        print("💡 TIP: With SSD, workers can be safely disabled if paging error occurs")

    # ===== COMPUTE CLASS WEIGHTS =====
    print(f"\n[1/3] Computing class weights from x4plus enhanced dataset...")

    label_dir = "GARBAGE_CLASSIFICATION_clahe_realesrgan_x4/train/labels"

    if not os.path.isdir(label_dir):
        print(f"✗ ERROR: Label directory not found: {label_dir}")
        return

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

    print(f"\nClass distribution:")
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
    print(f"\n[3/3] Starting optimized training...")
    print("-" * 80)
    print(f"Dataset: {DATASET_NAME} (4x Real-ESRGAN Enhanced)")
    print(f"Model: {MODEL_NAME}")
    print(f"Batch size: {BATCH_SIZE} (memory-safe configuration)")
    print(f"Workers: {WORKERS} (reduced to prevent OOM)")
    print(f"Cache: False (prevent memory spikes)")
    print(f"Learning rate: 5e-4")
    print("-" * 80)

    # ===== TRAIN WITH HARDWARE-OPTIMIZED SETTINGS =====
    results = model.train(
        data=YAML_PATH,
        epochs=EPOCHS,
        imgsz=IMG_SIZE,
        batch=BATCH_SIZE,  # ✅ 8 (safe for 6GB VRAM + 16GB RAM with Real-ESRGAN x4)
        # ===== LEARNING RATE =====
        lr0=5e-4,
        lrf=0.01,
        warmup_epochs=5,
        # ===== REGULARIZATION =====
        weight_decay=5e-4,
        dropout=0.0,
        # ===== OPTIMIZER =====
        optimizer='SGD',
        momentum=0.937,
        # ===== EARLY STOPPING =====
        patience=PATIENCE,
        device=0 if device == 'cuda' else 'cpu',
        # ===== AUGMENTATIONS (OPTIMIZED) =====
        hsv_h=0.015,
        hsv_s=0.7,
        hsv_v=0.4,
        degrees=10.0,
        translate=0.10,
        scale=0.5,
        flipud=0.5,
        fliplr=0.5,
        mosaic=1.0,
        mixup=0.05,
        copy_paste=0.0,
        # ===== TRAINING SETTINGS =====
        verbose=True,
        save=True,
        plots=True,
        project='runs/detect',
        name='train_realesrgan_x4_v2',
        exist_ok=False,
        # ===== DATA LOADING (MEMORY-SAFE) =====
        workers=WORKERS,  # ✅ 2 workers (safe balance for 16GB RAM)
        fraction=1.0,
        cache=False,  # ✅ CRITICAL: Disable cache to prevent memory spikes
        # Real-ESRGAN x4 images are large (~3-5MB each), caching can cause OOM
        rect=True,  # ✅ ENABLED: Rectangular training (efficient batching)
        close_mosaic=10,  # ✅ Close mosaic augmentation di epoch akhir (stabilize)
        # ===== MEMORY STABILITY =====
        amp=True,  # ✅ Automatic Mixed Precision (reduce VRAM usage)
        # persistent_workers akan otomatis diatur oleh ultralytics
    )

    # ===== SUMMARY =====
    print("\n" + "=" * 80)
    print("TRAINING COMPLETE")
    print("=" * 80)
    print(f"\n✓ Best model: runs/detect/train_realesrgan_x4_v2/weights/best.pt")
    print(f"\n⚙️  Hardware-Specific Optimizations (Memory-Safe):")
    print(f"  ✅ Batch: 8 (safe for RTX 2060 6GB + 16GB RAM)")
    print(f"  ✅ Workers: 2 (balanced for stability)")
    print(f"  ✅ Cache: False (prevent OOM with large Real-ESRGAN images)")
    print(f"  ✅ AMP: True (reduce VRAM usage ~30%)")
    print(f"  ✅ Rect: True (efficient batching)")
    print(f"  ✅ Learning rate: 5e-4 (controlled convergence)")
    print(f"  ✅ Optimizer: SGD with momentum (detection-optimized)")
    print(f"\n📊 Expected Performance (Memory-Safe Mode):")
    print(f"  Time per epoch: ~3-4 minutes")
    print(f"  Total time: ~7-10 hours (150 epochs)")
    print(f"  mAP50 target: 70-80%")
    print(f"  Memory usage: ~4-5GB VRAM, ~8-10GB RAM")
    print(f"\n💡 SSD Performance Tips:")
    print(f"  1. First epoch will be slower (no caching)")
    print(f"  2. Each epoch loads fresh from SSD (~3-4 min)")
    print(f"  3. Monitor GPU/RAM usage with Task Manager")
    print(f"\n💡 If OOM Error Still Occurs:")
    print(f"  1. Reduce batch to 6: batch=6")
    print(f"  2. Reduce workers to 0: workers=0")
    print(f"  3. Reduce image size: imgsz=512")
    print(f"  4. Close all other applications")
    print(f"  5. Consider using Real-ESRGAN x2 instead of x4")
    print(f"\n{'=' * 80}\n")

if __name__ == '__main__':
    # ✅ Multiprocessing safeguard for Windows
    import multiprocessing
    multiprocessing.freeze_support()
    main()