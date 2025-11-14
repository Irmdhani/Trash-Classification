from ultralytics import YOLO
import cv2
import os
import datetime
import torch

# ===== CONFIGURATION =====
# Path ke model terbaik
MODEL_WEIGHTS_PATH = 'runs/detect/train/weights/best.pt'  # CLAHE only
# MODEL_WEIGHTS_PATH = 'runs/detect/train_realesrgan/weights/best.pt'  # Real-ESRGAN (uncomment jika pakai)

# Device
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'

# Camera
CAMERA_INDEX = 0

# Thresholds
CONF_THRESHOLD = 0.5
IOU_THRESHOLD = 0.45

# Output folder
SAVE_FRAMES_FOLDER = 'live_detection_captures'
SAVE_INTERVAL_SECONDS = 0

# ===== 6 CLASSES (UPDATED) =====
CLASS_NAMES = {
    0: 'BIODEGRADABLE',
    1: 'CARDBOARD',
    2: 'GLASS',
    3: 'METAL',
    4: 'PAPER',
    5: 'PLASTIC'
}

CLASS_COLORS = {
    0: (0, 255, 0),      # BIODEGRADABLE - hijau
    1: (255, 0, 0),      # CARDBOARD - biru
    2: (0, 0, 255),      # GLASS - merah
    3: (255, 255, 0),    # METAL - cyan
    4: (0, 255, 255),    # PAPER - kuning
    5: (255, 0, 255)     # PLASTIC - magenta
}

# ===== FUNCTIONS =====
def draw_detections(frame, results):
    """Draw bounding boxes dengan label per class."""
    if results.boxes is None or len(results.boxes) == 0:
        return frame
    
    for box in results.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        conf = float(box.conf[0])
        cls = int(box.cls[0])
        
        color = CLASS_COLORS.get(cls, (255, 255, 255))
        class_name = CLASS_NAMES.get(cls, f'Unknown_{cls}')
        
        # Draw rectangle
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        
        # Draw label dengan background
        label = f"{class_name} {conf:.2f}"
        text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
        
        cv2.rectangle(frame,
                     (x1, y1 - text_size[1] - 8),
                     (x1 + text_size[0], y1),
                     color, -1)
        
        cv2.putText(frame, label, (x1, y1 - 4),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    return frame

def live_detect_trash():
    """Live trash detection."""
    print("=" * 80)
    print("LIVE TRASH DETECTION - GARBAGE_CLASSIFICATION_CLAHE (6 Classes)")
    print("=" * 80)
    print(f"\nConfiguration:")
    print(f"  Model: {MODEL_WEIGHTS_PATH}")
    print(f"  Device: {DEVICE}")
    print(f"  Confidence threshold: {CONF_THRESHOLD}")
    print(f"  IOU threshold: {IOU_THRESHOLD}")
    
    # Load model
    print(f"\nLoading model...")
    try:
        model = YOLO(MODEL_WEIGHTS_PATH)
        model.to(DEVICE)
        print("✓ Model loaded successfully")
    except FileNotFoundError:
        print(f"✗ ERROR: Model not found at {MODEL_WEIGHTS_PATH}")
        print("Please train model first: python trainingnew_clahe.py")
        return
    except Exception as e:
        print(f"✗ ERROR: {e}")
        return
    
    # Open camera
    print(f"\nOpening camera...")
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print(f"✗ ERROR: Cannot open camera (index {CAMERA_INDEX})")
        print("Try: CAMERA_INDEX = 1, 2, etc.")
        return
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    print(f"✓ Camera opened")
    print(f"  Resolution: {width}x{height}")
    print(f"  FPS: {fps:.1f}")
    
    print("\n" + "=" * 80)
    print("DETECTION STARTED")
    print("=" * 80)
    print("Controls:")
    print("  'q' = Quit")
    print("  's' = Save frame")
    print("=" * 80 + "\n")
    
    frame_count = 0
    detections_count = 0
    last_save_time = datetime.datetime.now()
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("✗ Failed to read frame")
                break
            
            frame_count += 1
            
            # Inference
            results = model(
                source=frame,
                imgsz=640,
                conf=CONF_THRESHOLD,
                iou=IOU_THRESHOLD,
                device=DEVICE,
                verbose=False
            )
            
            # Draw detections
            annotated_frame = draw_detections(frame.copy(), results[0])
            
            # Add info
            num_detections = len(results[0].boxes) if results[0].boxes else 0
            detections_count += num_detections
            
            info_text = f"Frame: {frame_count} | Detections: {num_detections}"
            cv2.putText(annotated_frame, info_text, (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Display
            cv2.imshow('Live Trash Detection - 6 Classes', annotated_frame)
            
            # Save frames periodically
            if SAVE_INTERVAL_SECONDS > 0:
                current_time = datetime.datetime.now()
                if (current_time - last_save_time).total_seconds() >= SAVE_INTERVAL_SECONDS:
                    os.makedirs(SAVE_FRAMES_FOLDER, exist_ok=True)
                    timestamp = current_time.strftime("%Y%m%d_%H%M%S")
                    output_filename = os.path.join(SAVE_FRAMES_FOLDER,
                                                   f"detected_frame_{timestamp}.jpg")
                    cv2.imwrite(output_filename, annotated_frame)
                    print(f"Saved: {output_filename}")
                    last_save_time = current_time
            
            # Key handling
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("\nStopping...")
                break
            elif key == ord('s'):
                os.makedirs(SAVE_FRAMES_FOLDER, exist_ok=True)
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = os.path.join(SAVE_FRAMES_FOLDER,
                                               f"manual_capture_{timestamp}.jpg")
                cv2.imwrite(output_filename, annotated_frame)
                print(f"Saved: {output_filename}")
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        
        print("\n" + "=" * 80)
        print("DETECTION COMPLETE")
        print("=" * 80)
        print(f"Total frames: {frame_count}")
        print(f"Total detections: {detections_count}")
        if frame_count > 0:
            print(f"Average detections per frame: {detections_count/frame_count:.2f}")
        print("=" * 80 + "\n")

if __name__ == '__main__':
    live_detect_trash()