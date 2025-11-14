# ...existing code...
import cv2
import numpy as np
from pathlib import Path
from basicsr.archs.rrdbnet_arch import RRDBNet
from realesrgan import RealESRGANer
import torch

class ImagePreprocessor:
    """Preprocessing untuk dataset dengan CLAHE dan optional Real-ESRGAN."""
    
    def __init__(self, img_size=640, use_clahe=True, use_realesrgan=False, 
                 realesrgan_model_path='RealESRGAN_x4plus.pth', use_normalization=True):
        self.img_size = img_size
        self.use_clahe = use_clahe
        self.use_normalization = use_normalization
        
        self.upsampler = None
        if use_realesrgan:
            print("Initializing Real-ESRGAN upsampler...")
            try:
                model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32)
                self.upsampler = RealESRGANer(
                    scale=2,
                    model_path=realesrgan_model_path,
                    model=model,
                    tile=400,
                    tile_pad=10,
                    pre_pad=0,
                    half=torch.cuda.is_available()
                )
                print("✓ Real-ESRGAN loaded")
            except Exception as e:
                print(f"Warning: Could not load Real-ESRGAN: {e}")
                self.upsampler = None
    
    def preprocess(self, image):
        """Preprocess image untuk training & inference."""
        if image is None:
            raise ValueError("Image is None")
        
        # Apply Real-ESRGAN enhancement jika tersedia
        if self.upsampler is not None:
            try:
                image, _ = self.upsampler.enhance(image, outscale=2)
            except Exception as e:
                print(f"Warning: Real-ESRGAN enhancement failed: {e}")
        
        h, w = image.shape[:2]
        scale = self.img_size / max(h, w)
        new_h, new_w = int(h * scale), int(w * scale)
        image = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
        
        # Pad to square
        pad_h = (self.img_size - new_h) // 2
        pad_w = (self.img_size - new_w) // 2
        image = cv2.copyMakeBorder(
            image, 
            pad_h, self.img_size - new_h - pad_h,
            pad_w, self.img_size - new_w - pad_w,
            cv2.BORDER_CONSTANT, value=(114, 114, 114)
        )
        
        # Apply CLAHE
        if self.use_clahe:
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            l_channel = lab[:, :, 0]
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            l_channel = clahe.apply(l_channel)
            lab[:, :, 0] = l_channel
            image = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        
        # Normalization
        if self.use_normalization:
            image = image.astype(np.float32) / 255.0
        
        return image