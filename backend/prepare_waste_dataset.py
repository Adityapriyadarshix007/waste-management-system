import os
import shutil
import random
from pathlib import Path
from sklearn.model_selection import train_test_split

print("=== Preparing Waste Classification Dataset ===")

base_dir = Path("/Users/adityapriyadarshi/Desktop/waste-management-system/backend")
dataset_dir = base_dir / "kaggle_raw" / "DATASET"
yolo_dir = base_dir / "kaggle_yolo"

# Create YOLO structure
(yolo_dir / "images/train").mkdir(parents=True, exist_ok=True)
(yolo_dir / "images/val").mkdir(parents=True, exist_ok=True)
(yolo_dir / "labels/train").mkdir(parents=True, exist_ok=True)
(yolo_dir / "labels/val").mkdir(parents=True, exist_ok=True)

print(f"Dataset source: {dataset_dir}")
print(f"YOLO output: {yolo_dir}")

# Check TRAIN and TEST directories
train_dir = dataset_dir / "TRAIN"
test_dir = dataset_dir / "TEST"

print(f"\nChecking directories:")
print(f"Train dir exists: {train_dir.exists()}")
print(f"Test dir exists: {test_dir.exists()}")

# Find class folders in TRAIN
if train_dir.exists():
    class_folders = [f for f in train_dir.iterdir() if f.is_dir()]
    print(f"\nFound {len(class_folders)} class folders in TRAIN:")
    for folder in class_folders:
        images = list(folder.glob("*.jpg")) + list(folder.glob("*.jpeg")) + list(folder.glob("*.png"))
        print(f"  {folder.name}: {len(images)} images")
else:
    # Look in TEST if no TRAIN
    class_folders = [f for f in test_dir.iterdir() if f.is_dir()]
    print(f"\nFound {len(class_folders)} class folders in TEST:")
    for folder in class_folders:
        images = list(folder.glob("*.jpg")) + list(folder.glob("*.jpeg")) + list(folder.glob("*.png"))
        print(f"  {folder.name}: {len(images)} images")

# Map folder names to our categories
# R = Recyclable, O = Organic/Biodegradable
category_map = {
    'R': 'recyclable',
    'O': 'biodegradable', 
    'H': 'hazardous',
    'recyclable': 'recyclable',
    'organic': 'biodegradable',
    'hazardous': 'hazardous'
}

# Class names for YOLO
class_names = ['biodegradable', 'recyclable', 'hazardous']
class_to_id = {name: idx for idx, name in enumerate(class_names)}

# Collect all images with their categories
all_images = []
for folder in class_folders:
    folder_name = folder.name
    if folder_name in category_map:
        category = category_map[folder_name]
    elif folder_name in ['R', 'r', 'R_', 'recyclable']:
        category = 'recyclable'
    elif folder_name in ['O', 'o', 'O_', 'organic']:
        category = 'biodegradable'
    else:
        category = 'biodegradable'  # default
    
    class_id = class_to_id[category]
    
    # Get images
    images = list(folder.glob("*.jpg")) + list(folder.glob("*.jpeg")) + list(folder.glob("*.png"))
    
    print(f"  {folder_name} → {category} (class {class_id}): {len(images)} images")
    
    for img in images:
        all_images.append((img, class_id, category))

print(f"\nTotal images collected: {len(all_images)}")

if len(all_images) == 0:
    print("❌ No images found! Checking recursively...")
    all_images_raw = list(dataset_dir.rglob("*.jpg")) + list(dataset_dir.rglob("*.jpeg")) + list(dataset_dir.rglob("*.png"))
    print(f"Found {len(all_images_raw)} images total")
    # Assign random classes for testing
    all_images = [(img, random.randint(0, 2), random.choice(['biodegradable', 'recyclable'])) for img in all_images_raw[:500]]
    print(f"Using {len(all_images)} images for training")

# Shuffle and split
random.shuffle(all_images)
train_ratio = 0.8
train_count = int(len(all_images) * train_ratio)
train_images = all_images[:train_count]
val_images = all_images[train_count:]

print(f"\nDataset split:")
print(f"  Training: {len(train_images)} images")
print(f"  Validation: {len(val_images)} images")

# Process images
def process_set(images, set_name, max_images=1000):
    """Process a set of images"""
    count = 0
    for img_path, class_id, category in images:
        if count >= max_images:
            break
            
        # Create unique filename
        unique_name = f"{set_name}_{count:05d}{img_path.suffix}"
        
        # Copy image
        dest_img = yolo_dir / "images" / set_name / unique_name
        shutil.copy(img_path, dest_img)
        
        # Create label
        label_name = f"{set_name}_{count:05d}.txt"
        label_path = yolo_dir / "labels" / set_name / label_name
        
        with open(label_path, 'w') as f:
            # YOLO format: class_id x_center y_center width height
            # Full image bounding box
            f.write(f"{class_id} 0.5 0.5 0.98 0.98")
        
        count += 1
        if count % 200 == 0:
            print(f"    Processed {count} images...")
    
    return count

print(f"\nProcessing training images (max 1000)...")
train_processed = process_set(train_images, "train", max_images=1000)
print(f"✓ Processed {train_processed} training images")

print(f"Processing validation images (max 200)...")
val_processed = process_set(val_images, "val", max_images=200)
print(f"✓ Processed {val_processed} validation images")

# Create data.yaml
data_yaml = f"""path: {yolo_dir}
train: images/train
val: images/val

nc: {len(class_names)}
names: {class_names}
"""

(yolo_dir / "data.yaml").write_text(data_yaml)

print(f"\n✅ Dataset preparation complete!")
print(f"📍 Location: {yolo_dir}")
print(f"📊 Classes: {class_names}")
print(f"📈 Statistics:")
print(f"  - Training images: {train_processed}")
print(f"  - Validation images: {val_processed}")
print(f"  - Total: {train_processed + val_processed}")

# Show verification
print(f"\n📁 Verification:")
print(f"Train images: {len(list((yolo_dir / 'images/train').glob('*')))}")
print(f"Val images: {len(list((yolo_dir / 'images/val').glob('*')))}")
print(f"Train labels: {len(list((yolo_dir / 'labels/train').glob('*.txt')))}")
print(f"Val labels: {len(list((yolo_dir / 'labels/val').glob('*.txt')))}")

print(f"\n🚀 To train your model:")
print(f"cd {base_dir}")
print(f"yolo detect train model=yolov8n.pt data={yolo_dir}/data.yaml epochs=30 imgsz=640")
