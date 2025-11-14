from ultralytics import YOLO
import os
import cv2
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image

# --- Konfigurasi Inferensi ---
# Path ke model terbaik Anda (misal: dari pelatihan yolov8n_taco_v1)
# Sesuaikan ini dengan path hasil pelatihan Anda!
MODEL_WEIGHTS_PATH = 'Trash_Detection/yolov8s_epochs100_aug_v32/weights/best.pt' 

# Path ke folder gambar untuk diuji
# Anda bisa menggunakan gambar dari TACO dataset (test set) atau gambar baru
IMAGE_FOLDER = 'GARBAGE_CLASSIFICATION_clahe/test/images' 
# Atau Anda bisa arahkan ke folder dengan gambar Anda sendiri, misal:
# IMAGE_FOLDER = 'my_test_images' 

# Nama folder untuk menyimpan hasil deteksi
OUTPUT_FOLDER = 'detection_results'

# DEVICE: Gunakan 'mps' untuk GPU Apple Silicon, 'cpu' jika tidak
DEVICE = 'cuda' 

def detect_and_visualize():
    print(f"--- Memulai Proses Deteksi Sampah ---")
    print(f"Memuat model dari: {MODEL_WEIGHTS_PATH}")

    # Buat folder output jika belum ada
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    # 1. Muat model yang sudah dilatih
    try:
        model = YOLO(MODEL_WEIGHTS_PATH)
        print("Model berhasil dimuat.")
    except Exception as e:
        print(f"ERROR: Gagal memuat model: {e}")
        print("Pastikan path ke MODEL_WEIGHTS_PATH benar.")
        return

    # Dapatkan nama kelas dari model (ini otomatis diambil dari data.yaml saat pelatihan)
    class_names = model.names
    print(f"Kelas yang terdeteksi: {class_names}")

    # 2. Iterasi melalui gambar di folder
    image_files = [f for f in os.listdir(IMAGE_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

    if not image_files:
        print(f"Tidak ada gambar ditemukan di folder: {IMAGE_FOLDER}")
        return

    for img_file in image_files:
        image_path = os.path.join(IMAGE_FOLDER, img_file)
        print(f"\nMemproses gambar: {img_file}")

        # Lakukan inferensi
        # Parameter confidence threshold (conf=0.25) dan IoU threshold (iou=0.7) bisa disesuaikan
        results = model(image_path, conf=0.25, iou=0.7, device=DEVICE, verbose=False) # verbose=False agar tidak banyak output

        # Hasilnya adalah list, biasanya hanya ada satu objek Result untuk satu gambar
        for r in results:
            # Muat gambar asli untuk visualisasi
            # Menggunakan PIL untuk loading dan Matplotlib untuk display agar lebih mudah dengan bounding box
            img_pil = Image.open(image_path).convert("RGB")
            
            fig, ax = plt.subplots(1)
            ax.imshow(img_pil)
            ax.axis('off') # Sembunyikan sumbu

            if r.boxes: # Jika ada deteksi bounding box
                for box in r.boxes:
                    # Koordinat bounding box dalam format xyxy (x_min, y_min, x_max, y_max)
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                    conf = box.conf[0].cpu().numpy()
                    class_id = int(box.cls[0].cpu().numpy())
                    class_name = class_names[class_id]

                    # Gambarkan bounding box
                    rect = patches.Rectangle((x1, y1), x2 - x1, y2 - y1, 
                                             linewidth=2, edgecolor='r', facecolor='none')
                    ax.add_patch(rect)

                    # Teks label (kelas dan confidence)
                    label = f"{class_name} {conf:.2f}"
                    ax.text(x1, y1 - 10, label, 
                            color='white', fontsize=8, 
                            bbox=dict(facecolor='red', alpha=0.7, edgecolor='none', pad=1))
            else:
                print(f"Tidak ada sampah terdeteksi di {img_file}.")

            # Simpan atau tampilkan gambar hasil
            output_filename = os.path.join(OUTPUT_FOLDER, f"detected_{img_file}")
            plt.savefig(output_filename, bbox_inches='tight', pad_inches=0)
            plt.close(fig) # Tutup figure untuk menghemat memori
            print(f"Deteksi disimpan di: {output_filename}")

    print("\n--- Proses Deteksi Selesai ---")

if __name__ == '__main__':
    detect_and_visualize()