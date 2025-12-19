import os
import shutil
import random
from pathlib import Path
from sklearn.model_selection import train_test_split

print("=== Preparing Kaggle Waste Dataset for YOLO ===")

# Paths
base_dir = Path("/Users/adityapriyadarshi/Desktop/waste-management-system/backend")
dataset_dir = base_dir / "kaggle_dataset"
yolo_dir = base_dir / "kaggle_yolo"

# Create YOLO structure
(yolo_dir / "images/train").mkdir(parents=True, exist_ok=True)
(yolo_dir / "images/val").mkdir(parents=True, exist_ok=True)
(yolo_dir / "labels/train").mkdir(parents=True, exist_ok=True)
(yolo_dir / "labels/val").mkdir(parents=True, exist_ok=True)

# Check dataset structure
print("Looking for dataset structure...")

# Common Kaggle waste dataset structures
possible_structures = [
    dataset_dir / "DATASET",  # Original structure
    dataset_dir / "TRAIN",    # Alternative
    dataset_dir / "train",    # lowercase
    dataset_dir / "data",     # Another common
    dataset_dir,              # Direct in extracted folder
]

found_structure = None
for structure in possible_structures:
    if structure.exists():
        found_structure = structure
        print(f"✓ Found dataset at: {structure}")
        break

if not found_structure:
    print("❌ Could not find dataset structure. Checking contents...")
    items = list(dataset_dir.iterdir())
    for item in items:
        print(f"  {item.name}")
    exit(1)

# Find class folders
class_folders = []
for item in found_structure.iterdir():
    if item.is_dir() and not item.name.startswith('.'):
        class_folders.append(item)

print(f"Found {len(class_folders)} class folders: {[f.name for f in class_folders]}")

# Map to your 3 categories
category_mapping = {
    # Biodegradable/Organic
    'O': 'biodegradable', 'organic': 'biodegradable', 'O_': 'biodegradable',
    'biodegradable': 'biodegradable', 'food': 'biodegradable',
    
    # Recyclable
    'R': 'recyclable', 'recyclable': 'recyclable', 'R_': 'recyclable',
    'plastic': 'recyclable', 'metal': 'recyclable', 'glass': 'recyclable',
    'paper': 'recyclable', 'cardboard': 'recyclable',
    
    # Hazardous
    'H': 'hazardous', 'hazardous': 'hazardous', 'H_': 'hazardous',
    'battery': 'hazardous', 'e-waste': 'hazardous', 'medical': 'hazardous',
}

# Class names for YOLO
class_names = ['biodegradable', 'recyclable', 'hazardous']
class_to_id = {name: idx for idx, name in enumerate(class_names)}

# Process each class
all_images = []
for class_folder in class_folders:
    class_name = class_folder.name.lower()
    
    # Determine category
    yolo_category = 'biodegradable'  # default
    for key, value in category_mapping.items():
        if key.lower() in class_name:
            yolo_category = value
            break
    
    if yolo_category not in class_to_id:
        print(f"  Skipping unknown category: {class_name}")
        continue
    
    class_id = class_to_id[yolo_category]
    
    # Get images
    images = list(class_folder.glob("*.jpg")) + list(class_folder.glob("*.png")) + list(class_folder.glob("*.jpeg"))
    
    if not images:
        # Check subdirectories
        for subfolder in class_folder.iterdir():
            if subfolder.is_dir():
                images.extend(list(subfolder.glob("*.jpg")))
                images.extend(list(subfolder.glob("*.png")))
                images.extend(list(subfolder.glob("*.jpeg")))
    
    print(f"  {class_name}: {len(images)} images → {yolo_category}")
    
    for img_path in images:
        all_images.append((img_path, class_id, yolo_category))

print(f"\nTotal images found: {len(all_images)}")

if len(all_images) == 0:
    print("❌ No images found! Checking structure...")
    # Try to find images recursively
    images = list(dataset_dir.rglob("*.jpg")) + list(dataset_dir.rglob("*.png")) + list(dataset_dir.rglob("*.jpeg"))
    print(f"Found {len(images)} images recursively")
    # Use first 100 for testing
    all_images = [(img, 0, 'biodegradable') for img in images[:100]]

# Split train/val
random.shuffle(all_images)
split_idx = int(len(all_images) * 0.8)
train_images = all_images[:split_idx]
val_images = all_images[split_idx:]

print(f"\nSplit: {len(train_images)} train, {len(val_images)} validation")

# Process and copy images
def process_images(images, split_name):
    count = 0
    for img_path, class_id, category in images:
        # Copy image
        dest_img = yolo_dir / "images" / split_name / img_path.name
        shutil.copy(img_path, dest_img)
        
        # Create label (full image bounding box)
        label_path = yolo_dir / "labels" / split_name / f"{img_path.stem}.txt"
        with open(label_path, 'w') as f:
            # Format: class_id x_center y_center width height
            # For classification (not detection), use full image
            f.write(f"{class_id} 0.5 0.5 0.98 0.98")
        
        count += 1
    
    return count

print("\nProcessing training images...")
train_count = process_images(train_images, "train")
print(f"✓ Processed {train_count} training images")

print("Processing validation images...")
val_count = process_images(val_images, "val")
print(f"✓ Processed {val_count} validation images")

# Create data.yaml
data_yaml = f"""path: {yolo_dir}
train: images/train
val: images/val

nc: {len(class_names)}
names: {class_names}
"""

(yolo_dir / "data.yaml").write_text(data_yaml)

print(f"\n✅ Dataset prepared successfully!")
print(f"📍 Location: {yolo_dir}")
print(f"📊 Classes: {class_names}")
print(f"📁 Train images: {train_count}")
print(f"📁 Val images: {val_count}")

print(f"\nTo train your model, run:")
print(f"cd {base_dir}")
print(f"yolo task=detect mode=train model=yolov8n.pt data={yolo_dir}/data.yaml epochs=50 imgsz=640")
