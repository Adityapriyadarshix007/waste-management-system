#!/usr/bin/env python3
from ultralytics import YOLO
import cv2
import numpy as np
import os

print("🧪 TESTING WASTE DETECTION IMPROVEMENTS")

# Test images (create simple test images)
test_cases = [
    ("Green Waste", [0, 150, 0]),  # Biodegradable (green)
    ("Blue Waste", [0, 0, 150]),   # Recyclable (blue)
    ("Mixed Waste", [100, 100, 0]), # Mixed colors
]

# Load model (test both old and new)
models_to_test = []

# Old model
if os.path.exists("../runs/detect/train5/weights/best.pt"):
    models_to_test.append(("Old Model", "../runs/detect/train5/weights/best.pt"))

# New model if exists
if os.path.exists("high_accuracy_training/waste_detector_pro/weights/best.pt"):
    models_to_test.append(("New Model", "high_accuracy_training/waste_detector_pro/weights/best.pt"))

for model_name, model_path in models_to_test:
    print(f"\n🔍 Testing: {model_name}")
    print(f"   Path: {model_path}")
    
    model = YOLO(model_path)
    print(f"   Classes: {model.names}")
    
    # Test different confidence thresholds
    for conf_threshold in [0.1, 0.25, 0.5]:
        print(f"\n   Confidence threshold: {conf_threshold}")
        
        for test_name, color in test_cases:
            # Create test image
            test_img = np.zeros((300, 300, 3), dtype=np.uint8)
            test_img[:, :] = color
            
            # Run detection
            results = model(test_img, conf=conf_threshold, verbose=False)
            
            if results[0].boxes is not None:
                boxes = results[0].boxes
                print(f"     {test_name}: {len(boxes)} detection(s)")
                for box in boxes:
                    class_id = int(box.cls[0])
                    confidence = float(box.conf[0])
                    print(f"       - {model.names[class_id]} ({confidence:.2f})")
            else:
                print(f"     {test_name}: No detections")

print("\n✅ Testing complete!")
print("\n📝 TIPS FOR BETTER DETECTION:")
print("   1. Use confidence threshold 0.25-0.3 for best results")
print("   2. Ensure good lighting when capturing images")
print("   3. Point camera directly at waste item")
print("   4. Fill most of the frame with the object")
