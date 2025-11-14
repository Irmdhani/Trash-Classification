import os
import shutil
import yaml
from pathlib import Path

print("=" * 80)
print("SETTING UP REAL-ESRGAN X4PLUS ENHANCED DATASET")
print("=" * 80)

# ===== CONFIGURATION =====
SOURCE_DATASET = "GARBAGE_CLASSIFICATION_clahe"
TARGET_DATASET = "GARBAGE_CLASSIFICATION_clahe_realesrgan_x4"
SPLITS = ['train', 'valid', 'test']
NUM_CLASSES = 6
CLASS_NAMES = ['BIODEGRADABLE', 'CARDBOARD', 'GLASS', 'METAL', 'PAPER', 'PLASTIC']

source_root = Path(SOURCE_DATASET)
target_root = Path(TARGET_DATASET)

# ===== STEP 1: CREATE DIRECTORY STRUCTURE =====
print(f"\n[1/3] Creating directory structure for x4plus enhancement...")

for split in SPLITS:
    (target_root / split / 'images').mkdir(parents=True, exist_ok=True)
    (target_root / split / 'labels').mkdir(parents=True, exist_ok=True)
    print(f"  ✓ Created {split}/ folders")

print(f"✓ All directories created")

# ===== STEP 2: COPY LABELS =====
print(f"\n[2/3] Copying labels...")

try:
    for split in SPLITS:
        src_labels = source_root / split / 'labels'
        dst_labels = target_root / split / 'labels'
        
        if src_labels.exists():
            label_count = 0
            for label_file in src_labels.glob('*.txt'):
                shutil.copy2(label_file, dst_labels / label_file.name)
                label_count += 1
            print(f"  ✓ Copied {label_count} labels for {split}")
        else:
            print(f"  ⚠ Warning: {split} labels not found")
except Exception as e:
    print(f"  ✗ Error copying labels: {e}")
    exit(1)

# ===== STEP 3: CREATE DATA.YAML =====
print(f"\n[3/3] Creating data.yaml...")

data_config = {
    'path': str(target_root.absolute()),
    'train': 'train/images',
    'val': 'valid/images',
    'test': 'test/images',
    'nc': NUM_CLASSES,
    'names': CLASS_NAMES
}

yaml_path = target_root / 'data.yaml'
with open(yaml_path, 'w') as f:
    yaml.dump(data_config, f, default_flow_style=False, sort_keys=False)

print(f"  ✓ data.yaml created")
print(f"    Path: {yaml_path}")
print(f"    Classes: {NUM_CLASSES}")
print(f"    Scale: 4x (upscaled)")

# ===== SUMMARY =====
print("\n" + "=" * 80)
print("SETUP COMPLETE")
print("=" * 80)
print(f"\nTarget dataset: {TARGET_DATASET}/")
print(f"  ├── train/images/ (4x upscaled)")
print(f"  ├── valid/images/ (4x upscaled)")
print(f"  ├── test/images/  (4x upscaled)")
print(f"  └── data.yaml")

print(f"\n✓ Ready for training!")
print(f"Run: python trainingnew_clahe_realesrgan_x4.py")
print(f"\n{'=' * 80}\n")