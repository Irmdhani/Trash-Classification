# --- START OF FILE process_negatives.py ---

import cv2
import os
from tqdm import tqdm

# --- KONFIGURASI ---
# 1. Path ke folder yang berisi gambar COCO asli Anda
SOURCE_IMAGES_DIR = 'coco'

# 2. Path ke folder di mana gambar hasil CLAHE akan disimpan
DEST_IMAGES_DIR = 'coco_negatives_clahe'
# --- AKHIR KONFIGURASI ---


def apply_clahe_to_folder(source_dir, dest_dir):
    """
    Membaca semua gambar dari satu folder, menerapkan CLAHE,
    dan menyimpannya ke folder tujuan.
    """
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
        print(f"Direktori dibuat: {dest_dir}")

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    image_files = [f for f in os.listdir(source_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

    print(f"Memproses {len(image_files)} gambar negatif dari '{source_dir}'...")
    for filename in tqdm(image_files):
        source_path = os.path.join(source_dir, filename)
        dest_path = os.path.join(dest_dir, filename)

        image_bgr = cv2.imread(source_path)
        if image_bgr is None:
            print(f"Peringatan: Gagal membaca gambar {source_path}, dilewati.")
            continue

        # Terapkan logika CLAHE yang sama persis dengan data training Anda
        image_lab = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2LAB)
        l_channel, a_channel, b_channel = cv2.split(image_lab)
        l_channel_clahe = clahe.apply(l_channel)
        lab_clahe = cv2.merge((l_channel_clahe, a_channel, b_channel))
        image_bgr_clahe = cv2.cvtColor(lab_clahe, cv2.COLOR_LAB2BGR)
        cv2.imwrite(dest_path, image_bgr_clahe)

if __name__ == '__main__':
    print("Memulai preprocessing untuk gambar negatif...")
    apply_clahe_to_folder(SOURCE_IMAGES_DIR, DEST_IMAGES_DIR)
    print("\n--- Preprocessing Gambar Negatif Selesai! ---")
    print(f"Gambar yang sudah diproses tersedia di: '{DEST_IMAGES_DIR}'")
    print("Langkah selanjutnya adalah menyalin gambar-gambar ini ke folder training utama Anda.")

# --- END OF FILE process_negatives.py ---