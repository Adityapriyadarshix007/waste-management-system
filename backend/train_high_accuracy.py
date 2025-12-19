#!/usr/bin/env python3
from ultralytics import YOLO
import os
import time
import yaml

print("="*70)
print("🎯 HIGH-ACCURACY WASTE DETECTION TRAINING")
print("="*70)

# Load dataset info
with open("kaggle_yolo/data.yaml", 'r') as f:
    data = yaml.safe_load(f)

print(f"\n📦 Dataset: {data['names']}")
print(f"📊 Classes: {data['nc']}")

# Decide which model to use
MODEL_CHOICE = "yolov8m.pt"  # Medium size for good accuracy
# Alternatives: 
# - "yolov8n.pt" (fastest, less accurate)
# - "yolov8s.pt" (small)
# - "yolov8m.pt" (medium) ← RECOMMENDED
# - "yolov8l.pt" (large, most accurate but slow)

print(f"\n🤖 Using model: {MODEL_CHOICE}")
print("   (yolov8m gives best balance of speed and accuracy)")

# Check if we have existing model to continue training
existing_model = "../runs/detect/train5/weights/best.pt"
use_pretrained = False

if os.path.exists(existing_model):
    print(f"\n📂 Found existing model: {existing_model}")
    choice = input("Continue training from existing model? (y/n): ").lower()
    if choice == 'y':
        model = YOLO(existing_model)
        print("🔄 Continuing training from existing model...")
        use_pretrained = True
    else:
        model = YOLO(MODEL_CHOICE)
        print("🆕 Starting fresh training...")
else:
    model = YOLO(MODEL_CHOICE)
    print("\n🆕 Starting fresh training (no existing model found)...")

print(f"\n✅ Model loaded: {MODEL_CHOICE if not use_pretrained else 'existing model'}")
print(f"📊 Model classes: {model.names}")

# Training configuration for HIGH ACCURACY
config = {
    'data': 'kaggle_yolo/data.yaml',
    'epochs': 150,  # More epochs for better learning
    'imgsz': 640,
    'batch': 4,  # Smaller batch for CPU
    'patience': 50,  # Wait longer before stopping
    'lr0': 0.01,  # Learning rate
    'lrf': 0.01,
    'momentum': 0.937,
    'weight_decay': 0.0005,
    
    # Data augmentation (CRITICAL for accuracy)
    'hsv_h': 0.015,  # Hue augmentation
    'hsv_s': 0.7,    # Saturation augmentation
    'hsv_v': 0.4,    # Value augmentation
    'degrees': 10.0, # Rotation
    'translate': 0.1, # Translation
    'scale': 0.5,    # Scaling
    'shear': 0.0,    # Shearing
    'perspective': 0.0,
    'flipud': 0.0,
    'fliplr': 0.5,   # Horizontal flip (50% chance)
    'mosaic': 1.0,   # Mosaic augmentation
    'mixup': 0.0,
    'copy_paste': 0.0,
    
    # Model parameters
    'box': 7.5,
    'cls': 0.5,
    'dfl': 1.5,
    'pose': 12.0,
    'kobj': 1.0,
    'label_smoothing': 0.0,
    'nbs': 64,
    
    # Training settings
    'val': True,
    'save': True,
    'save_period': 10,  # Save checkpoint every 10 epochs
    'cache': False,
    'device': 'cpu',  # Change to 'cuda' if you have GPU
    'workers': 4,
    'project': 'high_accuracy_training',
    'name': 'waste_detector_pro',
    'exist_ok': True,
    'pretrained': True,
    'optimizer': 'AdamW',  # Better optimizer
    'verbose': True,
    'seed': 42,
    'deterministic': True,
    'cos_lr': True,  # Cosine learning rate scheduler
    'close_mosaic': 10,  # Disable mosaic last 10 epochs
    'resume': use_pretrained,
    'amp': True,  # Automatic Mixed Precision
}

print("\n⚙️ TRAINING CONFIGURATION:")
print("-"*40)
for key, value in sorted(config.items()):
    if key in ['hsv_h', 'hsv_s', 'hsv_v', 'degrees', 'translate', 'scale', 'fliplr', 'mosaic']:
        print(f"   {key}: {value} ✅ (Data Augmentation)")
    elif key in ['epochs', 'batch', 'patience', 'lr0']:
        print(f"   {key}: {value} ⭐ (Critical Parameter)")
    else:
        print(f"   {key}: {value}")

print("\n📈 EXPECTED IMPROVEMENTS:")
print("   1. Better detection of small objects")
print("   2. Higher accuracy in different lighting")
print("   3. More robust to object orientation")
print("   4. Better generalization to new waste items")

print("\n⏳ Training will take 1-3 hours depending on your CPU")
print("   Monitor progress below...")
print("="*70)

try:
    # Start training
    start_time = time.time()
    results = model.train(**config)
    end_time = time.time()
    
    training_time = (end_time - start_time) / 60  # in minutes
    print(f"\n✅ TRAINING COMPLETE!")
    print(f"   Time: {training_time:.1f} minutes")
    print(f"   Epochs completed: {results.epoch}")
    
    # Validate the model
    print(f"\n🧪 RUNNING VALIDATION...")
    metrics = model.val()
    
    print(f"\n📊 FINAL MODEL PERFORMANCE:")
    print(f"   mAP50-95: {metrics.box.map:.3f} (Higher is better)")
    print(f"   mAP50: {metrics.box.map50:.3f} (Primary metric)")
    print(f"   Precision: {metrics.box.p:.3f}")
    print(f"   Recall: {metrics.box.r:.3f}")
    
    # Save best model path
    best_model_path = "high_accuracy_training/waste_detector_pro/weights/best.pt"
    
    if os.path.exists(best_model_path):
        size_mb = os.path.getsize(best_model_path) / (1024 * 1024)
        print(f"\n💾 BEST MODEL SAVED:")
        print(f"   Path: {best_model_path}")
        print(f"   Size: {size_mb:.1f} MB")
        
        print(f"\n🎯 TO USE THIS MODEL IN YOUR APP:")
        print(f"   1. Update app.py line: ABSOLUTE_MODEL_PATH = '../backend/high_accuracy_training/waste_detector_pro/weights/best.pt'")
        print(f"   2. Restart backend: python app.py")
        
    # Performance interpretation
    print(f"\n📈 INTERPRETING RESULTS:")
    if metrics.box.map50 >= 0.8:
        print("   🎉 EXCELLENT! Model accuracy >80%")
        print("   Your system will detect waste very accurately!")
    elif metrics.box.map50 >= 0.6:
        print("   👍 GOOD! Model accuracy 60-80%")
        print("   Your system will detect waste reasonably well")
    elif metrics.box.map50 >= 0.4:
        print("   ⚠️ FAIR! Model accuracy 40-60%")
        print("   May need more training data or epochs")
    else:
        print("   ❌ NEEDS IMPROVEMENT! Model accuracy <40%")
        print("   Consider: More data, different model, longer training")
        
except KeyboardInterrupt:
    print(f"\n⚠️ Training interrupted by user")
    print(f"   Partial results saved in high_accuracy_training/")
except Exception as e:
    print(f"\n❌ Training error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
print("🎯 NEXT STEPS:")
print("   1. Update app.py with new model path")
print("   2. Test with camera on actual waste items")
print("   3. If accuracy is still low, collect more training images")
print("="*70)
