import os
from pathlib import Path
from collections import Counter

def check_distribution():
    """Check detailed class distribution per split."""
    
    print("=" * 80)
    print("DETAILED CLASS DISTRIBUTION ANALYSIS")
    print("=" * 80)
    
    class_names = {
        0: 'BIODEGRADABLE',
        1: 'CARDBOARD',
        2: 'GLASS',
        3: 'METAL',
        4: 'PAPER',
        5: 'PLASTIC',
        6: 'NEGATIVE'
    }
    
    splits = ['train', 'valid', 'test']
    
    total_cnt = Counter()
    
    for split in splits:
        labels_dir = f'GARBAGE_CLASSIFICATION_clahe/{split}/labels'
        split_cnt = Counter()
        
        if not os.path.isdir(labels_dir):
            print(f"\n✗ {split} not found: {labels_dir}")
            continue
        
        print(f"\n{split.upper()} SPLIT:")
        print("-" * 80)
        
        for fn in os.listdir(labels_dir):
            if fn.endswith('.txt'):
                with open(os.path.join(labels_dir, fn), 'r') as f:
                    for line in f:
                        parts = line.strip().split()
                        if parts:
                            try:
                                cls = int(float(parts[0]))
                                split_cnt[cls] += 1
                                total_cnt[cls] += 1
                            except (ValueError, IndexError):
                                pass
        
        split_total = sum(split_cnt.values())
        for cls in range(7):
            count = split_cnt.get(cls, 0)
            pct = (count / split_total * 100) if split_total > 0 else 0
            class_name = class_names.get(cls, f'Unknown_{cls}')
            print(f"  {class_name:15s}: {count:6d} ({pct:6.2f}%)")
    
    # Total summary
    print("\n" + "=" * 80)
    print("TOTAL SUMMARY")
    print("-" * 80)
    total = sum(total_cnt.values())
    for cls in range(7):
        count = total_cnt.get(cls, 0)
        pct = (count / total * 100) if total > 0 else 0
        class_name = class_names.get(cls, f'Unknown_{cls}')
        status = "✓" if count > 0 else "✗ MISSING"
        print(f"  {status} {class_name:15s}: {count:6d} ({pct:6.2f}%)")
    
    print("=" * 80)
    
    # Check if NEGATIVE is missing
    if total_cnt.get(6, 0) == 0:
        print("\n⚠️  WARNING: NEGATIVE class (class 6) tidak ditemukan!")
        print("\nOpsi perbaikan:")
        print("  1. Label ulang images yang bukan sampah sebagai class 6 (NEGATIVE)")
        print("  2. Atau gunakan Pilihan B: Training tanpa NEGATIVE class (6 classes saja)")
        print("\nJika pilih opsi 2, update:")
        print("  - data.yaml: nc = 6 (bukan 7)")
        print("  - data.yaml: names = ['BIODEGRADABLE', 'CARDBOARD', 'GLASS', 'METAL', 'PAPER', 'PLASTIC']")
    
    # Check if imbalance severe
    if total_cnt.get(0, 0) > total * 0.5:
        print("\n⚠️  WARNING: BIODEGRADABLE terlalu dominan (>50%)!")
        print("\nSaran:")
        print("  1. Gunakan class_weights untuk balance (sudah automatic di training)")
        print("  2. Atau undersample BIODEGRADABLE dan oversample kelas lain")
        print("  3. Atau tambah lebih banyak data untuk kelas minority")

if __name__ == "__main__":
    check_distribution()