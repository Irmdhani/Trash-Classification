# --- START OF FILE apply_clahe.py (REVISED) ---
import cv2
import os
import shutil
from tqdm import tqdm

# --- FUNGSI INTI (TIDAK BERUBAH) ---
def apply_clahe_to_images(source_img_dir, dest_img_dir):
    if not os.path.exists(dest_img_dir):
        os.makedirs(dest_img_dir)
        print(f"Direktori dibuat: {dest_img_dir}")

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    image_files = [f for f in os.listdir(source_img_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    print(f"Memproses {len(image_files)} gambar dari '{os.path.basename(os.path.dirname(source_img_dir))}'...")
    for filename in tqdm(image_files):
        source_path = os.path.join(source_img_dir, filename)
        dest_path = os.path.join(dest_img_dir, filename)
        image_bgr = cv2.imread(source_path)
        if image_bgr is None: continue
        image_lab = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2LAB)
        l_channel, a_channel, b_channel = cv2.split(image_lab)
        l_channel_clahe = clahe.apply(l_channel)
        lab_clahe = cv2.merge((l_channel_clahe, a_channel, b_channel))
        image_bgr_clahe = cv2.cvtColor(lab_clahe, cv2.COLOR_LAB2BGR)
        cv2.imwrite(dest_path, image_bgr_clahe)

if __name__ == '__main__':
    # --- KONFIGURASI ---
    SOURCE_DATASET_DIR = 'GARBAGE_CLASSIFICATION' # <-- Nama folder dataset asli Anda
    DEST_DATASET_DIR = f'{SOURCE_DATASET_DIR}_clahe' # Nama folder untuk dataset baru
    SUBSETS_TO_PROCESS = ['train', 'valid', 'test'] # <-- Sesuaikan jika nama folder berbeda (misal 'val' bukan 'valid')
    # --- AKHIR KONFIGURASI ---
    
    print(f"Memulai preprocessing dari '{SOURCE_DATASET_DIR}' ke '{DEST_DATASET_DIR}'...")

    for subset in SUBSETS_TO_PROCESS:
        source_subset_dir = os.path.join(SOURCE_DATASET_DIR, subset)
        dest_subset_dir = os.path.join(DEST_DATASET_DIR, subset)

        if not os.path.exists(source_subset_dir):
            print(f"Peringatan: Subset '{subset}' tidak ditemukan di {SOURCE_DATASET_DIR}, dilewati.")
            continue
            
        # 1. Proses gambar (images)
        source_img_dir = os.path.join(source_subset_dir, 'images')
        dest_img_dir = os.path.join(dest_subset_dir, 'images')
        if os.path.exists(source_img_dir):
            apply_clahe_to_images(source_img_dir, dest_img_dir)
        
        # 2. Salin label (labels)
        source_labels_dir = os.path.join(source_subset_dir, 'labels')
        dest_labels_dir = os.path.join(dest_subset_dir, 'labels')
        if os.path.exists(source_labels_dir):
            print(f"Menyalin folder labels untuk subset '{subset}'...")
            if os.path.exists(dest_labels_dir): # Hapus dulu jika sudah ada
                shutil.rmtree(dest_labels_dir)
            shutil.copytree(source_labels_dir, dest_labels_dir)

    # 3. Salin file konfigurasi penting dari root
    for filename in ['data.yaml', 'README.md', 'LICENSE']: # Tambahkan file lain jika perlu
        source_file = os.path.join(SOURCE_DATASET_DIR, filename)
        dest_file = os.path.join(DEST_DATASET_DIR, filename)
        if os.path.exists(source_file):
            shutil.copy(source_file, dest_file)
            
    print(f"\n--- Preprocessing Selesai! ---")
    print(f"Dataset baru tersedia di: '{DEST_DATASET_DIR}'")

# --- END OF FILE apply_clahe.py (REVISED) ---