import os
import sys
from collections import Counter
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ===== CONFIGURATION =====
DATASET_PATH = 'GARBAGE_CLASSIFICATION_clahe'
NUM_CLASSES = 6
CLASS_NAMES = ['BIODEGRADABLE', 'CARDBOARD', 'GLASS', 'METAL', 'PAPER', 'PLASTIC']

# ===== ANALYSIS =====
label_dirs = [
    f'{DATASET_PATH}/train/labels',
    f'{DATASET_PATH}/valid/labels',
    f'{DATASET_PATH}/test/labels'
]

cnt = Counter()
total_files = 0

print("=" * 80)
print("ANALYZING GARBAGE_CLASSIFICATION_CLAHE DATASET (6 Classes)")
print("=" * 80)
print(f"\nDataset path: {DATASET_PATH}\n")

for labels_dir in label_dirs:
    if not os.path.isdir(labels_dir):
        print(f"⚠ Warning: Label directory not found: {labels_dir}")
        continue
    
    split_name = labels_dir.split('/')[-2]
    print(f"Processing: {labels_dir}")
    
    for fn in os.listdir(labels_dir):
        if fn.endswith('.txt'):
            total_files += 1
            filepath = os.path.join(labels_dir, fn)
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split()
                    if parts:
                        try:
                            cls = int(float(parts[0]))
                            if cls < NUM_CLASSES:
                                cnt[cls] += 1
                            else:
                                print(f"⚠ Warning: Invalid class {cls} in {fn}")
                        except (ValueError, IndexError):
                            print(f"⚠ Warning: Invalid line in {fn}: {line}")

total = sum(cnt.values())

print(f"\n{'=' * 80}")
print(f"SUMMARY")
print(f"{'=' * 80}")
print(f"Total label files: {total_files}")
print(f"Total bounding boxes: {total}\n")

print(f"{'Class Name':<20} {'Count':>10} {'Percentage':>15} {'Boxes':>10}")
print("-" * 80)

for cls in range(NUM_CLASSES):
    count = cnt.get(cls, 0)
    pct = (count / total * 100) if total > 0 else 0
    class_name = CLASS_NAMES[cls]
    print(f"{class_name:<20} {count:>10d} {pct:>14.2f}% {count:>10d}")

print("-" * 80)
print(f"{'TOTAL':<20} {total:>10d} {100.0:>14.2f}%")

# ===== COMPUTE CLASS WEIGHTS =====
print(f"\n{'=' * 80}")
print("CLASS WEIGHTS (untuk training)")
print(f"{'=' * 80}")

counts_arr = np.array([cnt.get(i, 1) for i in range(NUM_CLASSES)], dtype=float)
counts_arr[counts_arr == 0] = 1.0
weights = (counts_arr.sum() / counts_arr)
weights = weights / weights.sum() * len(weights)

weights_list = weights.tolist()

print(f"\n{'Class Name':<20} {'Weight':>15}")
print("-" * 80)
for i, w in enumerate(weights_list):
    print(f"{CLASS_NAMES[i]:<20} {w:>15.6f}")

# ===== SAVE WEIGHTS =====
weights_file = 'class_weights.txt'
with open(weights_file, 'w') as f:
    f.write(','.join(map(str, weights_list)))

print(f"\n✓ Class weights saved to: {weights_file}")
print(f"Content: {','.join([f'{w:.6f}' for w in weights_list])}")
print(f"\n{'=' * 80}\n")