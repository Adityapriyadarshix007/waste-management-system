import os
import shutil
import glob

def get_file_structure(root_dir):
    """Print file structure"""
    print("📁 Current Backend Structure:")
    print("=" * 50)
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Skip virtual environment
        if 'venv' in dirpath or '__pycache__' in dirpath:
            continue
            
        level = dirpath.replace(root_dir, '').count(os.sep)
        indent = ' ' * 2 * level
        print(f'{indent}{os.path.basename(dirpath)}/')
        
        subindent = ' ' * 2 * (level + 1)
        for filename in sorted(filenames):
            if not filename.endswith(('.py', '.json', '.h5', '.keras', '.txt', '.md')):
                continue
            print(f'{subindent}{filename}')

def clean_unnecessary_files(root_dir):
    """Remove unnecessary files"""
    print("\n🧹 Cleaning unnecessary files...")
    
    # Files to keep (essential for the project)
    essential_files = {
        'app.py',
        'requirements.txt',
        'model/predict.py',
        'model/waste_model_final.h5',
        'model/waste_model_final.keras',
        'model/class_indices.json',
        'model/training/train_model.py',
        'model/training/collect_data.py',
        'routes/__init__.py',
        'uploads/.gitkeep'
    }
    
    # Directories to keep
    essential_dirs = {
        'model',
        'model/training',
        'routes',
        'uploads',
        'dataset',
        'dataset/train',
        'dataset/test'
    }
    
    deleted_count = 0
    
    # Clean empty/unnecessary files
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Skip venv
        if 'venv' in dirpath:
            continue
            
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            rel_path = os.path.relpath(filepath, root_dir)
            
            # Skip essential files
            if rel_path in essential_files:
                continue
                
            # Remove empty Python files
            if filename.endswith('.py') and os.path.getsize(filepath) == 0:
                print(f"  Removing empty file: {rel_path}")
                os.remove(filepath)
                deleted_count += 1
            
            # Remove .pyc files
            elif filename.endswith('.pyc'):
                print(f"  Removing compiled file: {rel_path}")
                os.remove(filepath)
                deleted_count += 1
            
            # Remove duplicate model files (keep only one)
            elif filename == 'waste_model.h5' and 'waste_model_final.h5' in essential_files:
                print(f"  Removing duplicate model: {rel_path}")
                os.remove(filepath)
                deleted_count += 1
    
    # Clean empty directories
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
        if 'venv' in dirpath or '__pycache__' in dirpath:
            continue
            
        rel_path = os.path.relpath(dirpath, root_dir)
        
        # Remove empty directories (except essential ones)
        if (not os.listdir(dirpath) and 
            rel_path not in essential_dirs and
            rel_path != '.'):
            print(f"  Removing empty directory: {rel_path}")
            try:
                os.rmdir(dirpath)
            except:
                pass
    
    return deleted_count

def organize_dataset():
    """Organize dataset directory"""
    print("\n📊 Checking dataset...")
    
    # Check if dataset exists
    if not os.path.exists('dataset'):
        print("  No dataset directory found")
        return
    
    # Create proper structure if needed
    categories = ['plastic', 'paper', 'glass', 'metal', 'organic', 'hazardous']
    
    for split in ['train', 'test']:
        for category in categories:
            os.makedirs(f'dataset/{split}/{category}', exist_ok=True)
    
    # Count images
    total_images = 0
    for split in ['train', 'test']:
        split_path = f'dataset/{split}'
        if os.path.exists(split_path):
            for category in categories:
                cat_path = f'{split_path}/{category}'
                if os.path.exists(cat_path):
                    images = [f for f in os.listdir(cat_path) 
                             if f.endswith(('.jpg', '.png', '.jpeg'))]
                    total_images += len(images)
                    if len(images) > 0:
                        print(f"  {split}/{category}: {len(images)} images")
    
    print(f"  Total dataset images: {total_images}")

if __name__ == "__main__":
    root_dir = '.'
    
    # Get current structure
    get_file_structure(root_dir)
    
    # Clean files
    deleted = clean_unnecessary_files(root_dir)
    print(f"\n✅ Removed {deleted} unnecessary files")
    
    # Organize dataset
    organize_dataset()
    
    print("\n🎯 Essential files remaining:")
    print("-" * 30)
    print("app.py                    # Main Flask application")
    print("requirements.txt          # Python dependencies")
    print("model/predict.py          # Prediction model")
    print("model/waste_model_final.h5 # Trained model")
    print("model/class_indices.json  # Class mappings")
    print("model/training/           # Training scripts")
    print("routes/                   # API routes")
    print("uploads/                  # Upload directory")
    print("dataset/                  # Training dataset")
