import os
import cv2
import torch
from pathlib import Path
from tqdm import tqdm
import subprocess
import sys

class DatasetEnhancer:
    """Enhance dataset images menggunakan Real-ESRGAN."""
    
    def __init__(self, model_name='RealESRGAN_x4plus', scale=4, tile=200):
        """
        Args:
            model_name: Model name ('RealESRGAN_x4plus' atau 'RealESRGAN_x2plus')
            scale: Upscaling factor (2 atau 4)
            tile: Tile size untuk processing
        """
        self.scale = scale
        self.model_name = model_name
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        print(f"Device: {self.device}")
        print(f"Model: {model_name}")
        print(f"Scale: {scale}x")
        
        # Setup model path
        model_dir = 'weights'
        os.makedirs(model_dir, exist_ok=True)
        
        if model_name == 'RealESRGAN_x4plus':
            self.model_path = os.path.join(model_dir, 'RealESRGAN_x4plus.pth')
        elif model_name == 'RealESRGAN_x2plus':
            self.model_path = os.path.join(model_dir, 'RealESRGAN_x2plus.pth')
        else:
            raise ValueError(f"Unsupported model: {model_name}")
        
        # Download model jika belum ada
        if not os.path.exists(self.model_path):
            print(f"\n⚠ Model not found: {self.model_path}")
            self._download_model()
        else:
            print(f"✓ Model found: {self.model_path}")
        
        # Load model
        self._load_model()
    
    def _download_model(self):
        """Download model dari GitHub."""
        print("\nDownloading model from GitHub...")
        
        if self.model_name == 'RealESRGAN_x4plus':
            url = "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/RealESRGAN_x4plus.pth"
        else:
            url = "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/RealESRGAN_x2plus.pth"
        
        print(f"URL: {url}")
        print(f"Destination: {self.model_path}")
        print("(This may take several minutes...)\n")
        
        try:
            # Gunakan wget (Windows built-in di PowerShell)
            if sys.platform == 'win32':
                # Try urllib untuk Windows
                import urllib.request
                urllib.request.urlretrieve(url, self.model_path)
            else:
                # Gunakan wget untuk Linux/Mac
                subprocess.run(['wget', url, '-O', self.model_path], check=True)
            
            print(f"✓ Downloaded successfully: {self.model_path}")
            
            # Verify file
            if os.path.getsize(self.model_path) > 0:
                print(f"✓ File size: {os.path.getsize(self.model_path) / 1e6:.0f} MB")
            else:
                raise Exception("Downloaded file is empty")
        
        except Exception as e:
            print(f"✗ Download failed: {e}")
            print("\nManual download:")
            print(f"  1. Visit: {url}")
            print(f"  2. Download file")
            print(f"  3. Place in: {self.model_path}")
            print(f"  4. Run script again")
            raise
    
    def _load_model(self):
        """Load Real-ESRGAN model."""
        print(f"\nLoading model...")
        
        try:
            # Import basic realesrgan
            from basicsr.archs.rrdbnet_arch import RRDBNet
            from realesrgan import RealESRGANer
            
            # Define model architecture
            if self.model_name == 'RealESRGAN_x4plus':
                model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4)
            else:  # x2plus
                model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=2)
            
            # Initialize upsampler
            self.upsampler = RealESRGANer(
                scale=self.scale,
                model_path=self.model_path,
                model=model,
                tile=200,
                tile_pad=10,
                pre_pad=0,
                half=torch.cuda.is_available()
            )
            
            print(f"✓ Model loaded successfully (scale={self.scale}x)")
        
        except Exception as e:
            print(f"✗ Error loading model: {e}")
            print("\nTrying alternative initialization...")
            
            try:
                # Alternative: simpler initialization
                from realesrgan import RealESRGANer
                
                self.upsampler = RealESRGANer(
                    scale=self.scale,
                    model_path=self.model_path,
                    tile=200,
                    tile_pad=10,
                    pre_pad=0,
                    half=torch.cuda.is_available()
                )
                print(f"✓ Model loaded (alternative method)")
            
            except Exception as e2:
                print(f"✗ Alternative load failed: {e2}")
                raise
    
    def enhance_image(self, image_path, output_path=None):
        """Enhance single image."""
        try:
            img = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
            if img is None:
                return False
            
            # Enhance
            output, _ = self.upsampler.enhance(img, outscale=self.scale)
            
            # Save
            if output_path:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                cv2.imwrite(str(output_path), output)
            
            return True
        except Exception as e:
            print(f"Error enhancing {image_path}: {e}")
            return False
    
    def enhance_dataset(self, input_dir, output_dir, file_extensions=('.jpg', '.jpeg', '.png')):
        """Enhance all images in directory."""
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        
        if not input_path.exists():
            print(f"✗ Error: {input_dir} not found")
            return False
        
        # Get image files
        image_files = []
        for ext in file_extensions:
            image_files.extend(input_path.glob(f'*{ext}'))
            image_files.extend(input_path.glob(f'*{ext.upper()}'))
        
        image_files = list(set(image_files))
        
        if not image_files:
            print(f"⚠ No images found in {input_dir}")
            return False
        
        print(f"\nEnhancing: {input_dir}")
        print(f"  Found: {len(image_files)} images")
        print(f"  Output: {output_dir}")
        
        success_count = 0
        for img_file in tqdm(image_files, desc="Progress"):
            output_file = output_path / img_file.name
            if self.enhance_image(str(img_file), str(output_file)):
                success_count += 1
        
        print(f"✓ Successfully enhanced: {success_count}/{len(image_files)}")
        return success_count == len(image_files)

def main():
    print("=" * 80)
    print("REAL-ESRGAN DATASET ENHANCEMENT (x4plus)")
    print("=" * 80)
    
    SOURCE = "GARBAGE_CLASSIFICATION_clahe"
    TARGET = "GARBAGE_CLASSIFICATION_clahe_realesrgan_x4"
    SPLITS = ['train', 'valid', 'test']
    
    # ===== CONFIGURATION =====
    MODEL_NAME = 'RealESRGAN_x4plus'  # atau 'RealESRGAN_x2plus'
    SCALE = 4
    
    print(f"\nDataset:")
    print(f"  Source: {SOURCE}/")
    print(f"  Target: {TARGET}/")
    
    try:
        enhancer = DatasetEnhancer(
            model_name=MODEL_NAME,
            scale=SCALE,
            tile=200
        )
    except Exception as e:
        print(f"\n✗ Failed to initialize enhancer")
        print(f"Error: {e}")
        print("\nPlease:")
        print(f"  1. Download manually from:")
        print(f"     https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/RealESRGAN_x4plus.pth")
        print(f"  2. Create folder: weights/")
        print(f"  3. Place file in: weights/RealESRGAN_x4plus.pth")
        print(f"  4. Run script again")
        return
    
    # Enhance all splits
    print(f"\n{'=' * 80}")
    print("STARTING ENHANCEMENT")
    print(f"{'=' * 80}")
    
    for i, split in enumerate(SPLITS, 1):
        input_dir = f'{SOURCE}/{split}/images'
        output_dir = f'{TARGET}/{split}/images'
        
        print(f"\n[{i}/{len(SPLITS)}] {split.upper()} SPLIT")
        print("-" * 80)
        enhancer.enhance_dataset(input_dir, output_dir)
    
    print("\n" + "=" * 80)
    print("ENHANCEMENT COMPLETE")
    print("=" * 80)
    print(f"\nEnhanced dataset: {TARGET}/")
    print(f"\nNext step:")
    print(f"  python scripts/verify_enhanced_dataset.py")
    print(f"  python trainingnew_clahe_realesrgan_x4.py")
    print(f"\n{'=' * 80}\n")

if __name__ == "__main__":
    main()