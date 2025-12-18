import os
import json
import shutil
from PIL import Image
import numpy as np

print("Organizing TACO dataset for waste classification...")

# TACO annotations path
annotations_path = 'TACO/data/annotations.json'

# Create our dataset structure
categories = {
    'plastic': ['plastic', 'bottle', 'container', 'bag', 'wrapper'],
    'paper': ['paper', 'cardboard', 'newspaper', 'carton'],
    'glass': ['glass', 'bottle', 'jar'],
    'metal': ['metal', 'can', 'aluminum', 'foil'],
    'organic': ['food', 'fruit', 'vegetable', 'organic'],
    'hazardous': ['battery', 'electronic', 'chemical', 'hazardous']
}

# Create directories
for split in ['train', 'test']:
    for category in categories.keys():
        os.makedirs(f'dataset/{split}/{category}', exist_ok=True)

# Load TACO annotations
with open(annotations_path, 'r') as f:
    data = json.load(f)

print(f"Total images in TACO: {len(data['images'])}")
print(f"Total annotations in TACO: {len(data['annotations'])}")

# Map TACO categories to our categories
category_map = {}
for cat in data['categories']:
    cat_name = cat['name'].lower()
    for our_cat, keywords in categories.items():
        if any(keyword in cat_name for keyword in keywords):
            category_map[cat['id']] = our_cat
            break
    else:
        category_map[cat['id']] = 'plastic'  # default

# Organize images
image_count = 0
for img_info in data['images']:
    img_id = img_info['id']
    img_path = os.path.join('TACO/data', img_info['file_name'])
    
    # Find annotations for this image
    img_annotations = [ann for ann in data['annotations'] if ann['image_id'] == img_id]
    
    if not img_annotations:
        continue
    
    # Get dominant category
    categories_in_image = [category_map[ann['category_id']] for ann in img_annotations]
    if not categories_in_image:
        continue
    
    from collections import Counter
    dominant_category = Counter(categories_in_image).most_common(1)[0][0]
    
    # Split into train/test (80/20)
    split = 'train' if image_count % 5 != 0 else 'test'
    
    # Copy image
    dest_dir = f'dataset/{split}/{dominant_category}'
    dest_path = os.path.join(dest_dir, f'image_{image_count:04d}.jpg')
    
    try:
        # Copy the image
        shutil.copy(img_path, dest_path)
        image_count += 1
        
        if image_count % 100 == 0:
            print(f"Processed {image_count} images...")
            
    except Exception as e:
        print(f"Error copying {img_path}: {e}")

print(f"\n✅ Organized {image_count} images into dataset/ directory")
print("\nDataset structure created:")
for split in ['train', 'test']:
    print(f"\n{split.upper()}:")
    for category in categories.keys():
        count = len(os.listdir(f'dataset/{split}/{category}'))
        print(f"  {category}: {count} images")
