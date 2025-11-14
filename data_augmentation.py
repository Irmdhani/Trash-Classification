from albumentations import (
    Compose, HorizontalFlip, VerticalFlip, RandomRotate90,
    ColorJitter, RandomBrightnessContrast, CLAHE
)

def get_train_augmentation():
    return Compose([
        HorizontalFlip(p=0.5),
        VerticalFlip(p=0.3),
        RandomRotate90(p=0.5),
        ColorJitter(p=0.3),
        RandomBrightnessContrast(p=0.3),
        CLAHE(p=0.3)
    ], bbox_params={'format': 'yolo', 'label_fields': ['class_labels']})