# --- START OF FILE visualize_data.py (REVISED) ---
import cv2
import os
import random
import matplotlib.pyplot as plt

# --- KONFIGURASI ---
DATASET_BASE_DIR = 'GARBAGE_CLASSIFICATION' # <-- Ganti dengan nama folder dataset baru Anda
SUBSET_TO_VISUALIZE = 'train'

# Path sekarang dibangun secara otomatis
IMAGES_DIR = os.path.join(DATASET_BASE_DIR, SUBSET_TO_VISUALIZE, 'images')
LABELS_DIR = os.path.join(DATASET_BASE_DIR, SUBSET_TO_VISUALIZE, 'labels')

# PENTING: Sesuaikan dengan file data.yaml di dataset BARU Anda
CLASS_NAMES = [
    'BIODEGRADABLE', 'CARDBOARD', 'GLASS', 'METAL', 'PAPER', 'PLASTIC' # <-- CONTOH, SESUAIKAN
]
NUM_IMAGES_TO_SHOW = 10
COLORS = [ (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (0, 255, 255) ]
# --- AKHIR KONFIGURASI ---

def visualize_annotations():
    # ... (Sisa kode tidak perlu diubah, sama seperti sebelumnya) ...
    # (Kode dari versi sebelumnya bisa langsung disalin ke sini)
    if not os.path.exists(IMAGES_DIR):
        print(f"ERROR: Direktori gambar tidak ditemukan di: {IMAGES_DIR}")
        return

    all_images = [f for f in os.listdir(IMAGES_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    if not all_images:
        print(f"ERROR: Tidak ada gambar yang ditemukan di {IMAGES_DIR}")
        return

    selected_images = random.sample(all_images, min(NUM_IMAGES_TO_SHOW, len(all_images)))

    for image_name in selected_images:
        image_path = os.path.join(IMAGES_DIR, image_name)
        image = cv2.imread(image_path)
        img_height, img_width, _ = image.shape
        print(f"\n--- Menampilkan: {image_name} (Ukuran: {img_width}x{img_height}) ---")
        
        label_name = os.path.splitext(image_name)[0] + '.txt'
        label_path = os.path.join(LABELS_DIR, label_name)

        if os.path.exists(label_path):
            with open(label_path, 'r') as f:
                for line in f.readlines():
                    class_id, x_center_norm, y_center_norm, width_norm, height_norm = map(float, line.split())
                    class_id = int(class_id)
                    box_width = width_norm * img_width
                    box_height = height_norm * img_height
                    x_min = int((x_center_norm * img_width) - (box_width / 2))
                    y_min = int((y_center_norm * img_height) - (box_height / 2))
                    class_name = CLASS_NAMES[class_id]
                    color = COLORS[class_id % len(COLORS)]
                    cv2.rectangle(image, (x_min, y_min), (int(x_min + box_width), int(y_min + box_height)), color, 2)
                    label_text = f"{class_name}"
                    (w, h), _ = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                    cv2.rectangle(image, (x_min, y_min - 20), (x_min + w, y_min), color, -1)
                    cv2.putText(image, label_text, (x_min, y_min - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        plt.figure(figsize=(12, 8))
        plt.imshow(image_rgb)
        plt.title(image_name)
        plt.axis('off')
        plt.show()

if __name__ == '__main__':
    visualize_annotations()
# --- END OF FILE visualize_data.py (REVISED) ---