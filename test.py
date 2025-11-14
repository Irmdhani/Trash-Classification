import os
import torch
import cv2
from basicsr.archs.rrdbnet_arch import RRDBNet
from realesrgan import RealESRGANer

def test_installation():
    try:
        # ubah di sini: isi path ke file weight yang sudah Anda download
        model_path = 'RealESRGAN_x4plus.pth'

        if not os.path.isfile(model_path):
            print(f"Model weight not found: {model_path}")
            print("Download weight dari release Real-ESRGAN dan simpan di folder 'weights/'.")
            print("Contoh (PowerShell):")
            print("  mkdir weights;")
            print("  Invoke-WebRequest -Uri 'URL_TO_WEIGHT' -OutFile weights\\RealESRGAN_x4plus.pth")
            return False

        model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32)
        upsampler = RealESRGANer(scale=2, model_path=model_path, model=model)
        print("Real-ESRGAN installation successful!")
        return True
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_installation()