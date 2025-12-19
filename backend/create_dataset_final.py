import os
import shutil
import random
from pathlib import Path

print("=== Direct Dataset Creation ===")

base_dir = Path("/Users/adityapriyadarshi/Desktop/waste-management-system/backend")
yolo_dir = base_dir / "kaggle_yolo"

# Create directories
(yolo_dir / "images/train").mkdir(parents=True, exist_ok=True)
(yolo_dir / "images/val").mkdir(parents=True, exist_ok=True)
(yolo_dir / "labels/train").mkdir(parents=True, exist_ok=True)
(yolo_dir / "labels/val").mkdir(parents=True, exist_ok=True)

# Get O (Organic/Biodegradable) and R (Recyclable) images
train_o_dir = base_dir / "kaggle_raw" / "DATASET" / "TRAIN" / "O"
train_r_dir = base_dir / "kaggle_raw" / "DATASET" / "TRAIN" / "R"
test_o_dir = base_dir / "kaggle_raw" / "DATASET" / "TEST" / "O"
test_r_dir = base_dir / "kaggle_raw" / "DATASET" / "TEST" / "R"

print(f"Organic images (TRAIN): {len(list(train_o_dir.glob('*.jpg')))}")
print(f"Recyclable images (TRAIN): {len(list(train_r_dir.glob('*.jpg')))}")
print(f"Organic images (TEST): {len(list(test_o_dir.glob('*.jpg')))}")
print(f"Recyclable images (TEST): {len(list(test_r_dir.glob('*.jpg')))}")

# Function to copy images
def copy_images(source_dir, dest_dir, class_id, max_images=500):
    images = list(source_dir.glob("*.jpg"))
    random.shuffle(images)
    
    count = 0
    for img_path in images[:max_images]:
        dest_name = f"{class_id}_{count:05d}{img_path.suffix}"
        dest_path = dest_dir / dest_name
        shutil.copy(img_path, dest_path)
        
        # Create label
        label_name = f"{class_id}_{count:05d}.txt"
        label_path = yolo_dir / "labels" / dest_dir.name / label_name
        
        with open(label_path, 'w') as f:
            f.write(f"{class_id} 0.5 0.5 0.98 0.98")
        
        count += 1
        if count % 100 == 0:
            print(f"  Copied {count} images...")
    
    return count

print("\nCopying Organic (class 0 = biodegradable) images...")
# Use 400 from TRAIN/O for training, 100 from TEST/O for validation
train_o_count = copy_images(train_o_dir, yolo_dir / "images/train", 0, 400)
val_o_count = copy_images(test_o_dir, yolo_dir / "images/val", 0, 100)

print("\nCopying Recyclable (class 1 = recyclable) images...")
# Use 400 from TRAIN/R for training, 100 from TEST/R for validation
train_r_count = copy_images(train_r_dir, yolo_dir / "images/train", 1, 400)
val_r_count = copy_images(test_r_dir, yolo_dir / "images/val", 1, 100)

print(f"\n✅ Dataset created!")
print(f"Training images: {train_o_count + train_r_count}")
print(f"  - Organic: {train_o_count}")
print(f"  - Recyclable: {train_r_count}")
print(f"Validation images: {val_o_count + val_r_count}")
print(f"  - Organic: {val_o_count}")
print(f"  - Recyclable: {val_r_count}")

# Create data.yaml
data_yaml_content = """path: /Users/adityapriyadarshi/Desktop/waste-management-system/backend/kaggle_yolo
train: images/train
val: images/val

nc: 2
names: ['biodegradable', 'recyclable']
"""

(yolo_dir / "data.yaml").write_text(data_yaml_content)
print(f"\n✅ Created data.yaml with 2 classes")

# Verify
print(f"\n📁 Verification:")
print(f"Train images: {len(list((yolo_dir / 'images/train').glob('*.jpg')))}")
print(f"Val images: {len(list((yolo_dir / 'images/val').glob('*.jpg')))}")
print(f"Train labels: {len(list((yolo_dir / 'labels/train').glob('*.txt')))}")
print(f"Val labels: {len(list((yolo_dir / 'labels/val').glob('*.txt')))}")

print(f"\n🚀 Training command:")
print(f"cd {base_dir}")
print(f"yolo detect train model=yolov8n.pt data=kaggle_yolo/data.yaml epochs=20 imgsz=640")
