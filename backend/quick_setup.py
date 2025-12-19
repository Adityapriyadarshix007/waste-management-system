import os
import shutil
import random
from pathlib import Path

print("=== Creating Waste Detection Dataset ===")

base_dir = Path("/Users/adityapriyadarshi/Desktop/waste-management-system/backend")
raw_dir = base_dir / "kaggle_raw"
yolo_dir = base_dir / "kaggle_yolo"

# Find all images
image_extensions = ['.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG']
all_images = []
for ext in image_extensions:
    all_images.extend(list(raw_dir.rglob(f"*{ext}")))

print(f"Found {len(all_images)} images")

if len(all_images) == 0:
    print("❌ No images found! Check extraction.")
    print("Contents of kaggle_raw:")
    for item in raw_dir.iterdir():
        print(f"  {item.name}")
    exit(1)

# Shuffle and split
random.shuffle(all_images)
split_idx = int(len(all_images) * 0.8)
train_images = all_images[:split_idx]
val_images = all_images[split_idx:]

print(f"Train: {len(train_images)}, Val: {len(val_images)}")

# Process training images
print("Processing training images...")
for i, img_path in enumerate(train_images[:200]):  # Use first 200 for quick training
    # Copy image
    dest_name = f"train_{i:04d}{img_path.suffix}"
    dest_path = yolo_dir / "images" / "train" / dest_name
    shutil.copy(img_path, dest_path)
    
    # Create label (full image = class 0)
    label_path = yolo_dir / "labels" / "train" / f"train_{i:04d}.txt"
    with open(label_path, 'w') as f:
        # YOLO format: class_id x_center y_center width height
        # Using class 0 for all (we'll fix this later)
        f.write("0 0.5 0.5 0.98 0.98")
    
    if i % 50 == 0:
        print(f"  Processed {i} images...")

# Process validation images
print("Processing validation images...")
for i, img_path in enumerate(val_images[:50]):  # Use first 50 for validation
    dest_name = f"val_{i:04d}{img_path.suffix}"
    dest_path = yolo_dir / "images" / "val" / dest_name
    shutil.copy(img_path, dest_path)
    
    label_path = yolo_dir / "labels" / "val" / f"val_{i:04d}.txt"
    with open(label_path, 'w') as f:
        f.write("0 0.5 0.5 0.98 0.98")

# Create data.yaml
data_yaml = """path: /Users/adityapriyadarshi/Desktop/waste-management-system/backend/kaggle_yolo
train: images/train
val: images/val

nc: 3
names: ['biodegradable', 'recyclable', 'hazardous']
"""

(yolo_dir / "data.yaml").write_text(data_yaml)

print(f"\n✅ Dataset created at: {yolo_dir}")
print(f"📁 Training images: {min(200, len(train_images))}")
print(f"📁 Validation images: {min(50, len(val_images))}")
print("\n📋 To train:")
print("cd /Users/adityapriyadarshi/Desktop/waste-management-system/backend")
print("yolo task=detect mode=train model=yolov8n.pt data=kaggle_yolo/data.yaml epochs=10")
