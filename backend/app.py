from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import time
import numpy as np
from PIL import Image
import io
import base64
import traceback
import cv2

print("\n" + "="*70)
print("🚀 STARTING WASTE DETECTION API")
print("="*70)

# ==================== MODEL LOADING ====================
# Use relative path from backend directory
ABSOLUTE_MODEL_PATH = "../runs/detect/train5/weights/best.pt"

print(f"🔍 Looking for model at: {ABSOLUTE_MODEL_PATH}")

yolo_model = None
MODEL_PATH = None
model_loaded = False

try:
    from ultralytics import YOLO
    print("✅ ultralytics imported successfully")
    
    if os.path.exists(ABSOLUTE_MODEL_PATH):
        print(f"📏 File size: {os.path.getsize(ABSOLUTE_MODEL_PATH) / 1024 / 1024:.1f} MB")
        yolo_model = YOLO(ABSOLUTE_MODEL_PATH)
        MODEL_PATH = ABSOLUTE_MODEL_PATH
        model_loaded = True
        print(f"✅ YOLOv8 MODEL LOADED SUCCESSFULLY!")
        print(f"📊 Model classes: {yolo_model.names}")
        print(f"📋 Available classes: {list(yolo_model.names.values())}")
    else:
        print(f"❌ Model not found at: {ABSOLUTE_MODEL_PATH}")
        print("   Searching in current directory...")
        if os.path.exists("best.pt"):
            yolo_model = YOLO("best.pt")
            MODEL_PATH = "best.pt"
            model_loaded = True
            print("✅ Loaded model from current directory")
            
except ImportError as e:
    print(f"❌ CANNOT IMPORT ULTRALYTICS: {e}")
    print("   Install with: pip install ultralytics")
except Exception as e:
    print(f"❌ UNEXPECTED ERROR: {e}")
    traceback.print_exc()

print(f"\n🤖 MODEL STATUS: {'LOADED ✅' if model_loaded else 'NOT LOADED ❌'}")
if model_loaded:
    print(f"📍 Path: {MODEL_PATH}")
print("="*70 + "\n")

# ==================== FLASK APP ====================
app = Flask(__name__)
CORS(app)

# Class configuration based on YOUR ACTUAL trained classes
# Your model only has 2 classes: 0: 'biodegradable', 1: 'recyclable'
CLASS_CONFIG = {
    "biodegradable": {
        "name": "Biodegradable",
        "dustbinColor": "Green",
        "icon": "🍌",
        "color": "#10b981",
        "examples": ["Banana Peel", "Food Waste", "Vegetable Scraps", "Apple Core", "Egg Shells"]
    },
    "recyclable": {
        "name": "Recyclable", 
        "dustbinColor": "Blue",
        "icon": "♻️",
        "color": "#3b82f6",
        "examples": ["Plastic Bottle", "Soda Can", "Glass Bottle", "Cardboard", "Paper Bag"]
    }
}

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def process_yolo_prediction(results):
    """Convert YOLOv8 results to frontend format"""
    detections = []
    
    print(f"\n=== Processing YOLO Results ===")
    
    if not results or len(results) == 0:
        print("❌ No results from YOLO")
        return detections
    
    if results[0].boxes is None:
        print("❌ No boxes detected by YOLO")
        return detections
    
    boxes = results[0].boxes
    print(f"✅ YOLO found {len(boxes)} boxes")
    
    for i, box in enumerate(boxes):
        try:
            # Extract data
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            confidence = float(box.conf[0].cpu().numpy())
            class_id = int(box.cls[0].cpu().numpy())
            
            # Get class name from model
            if hasattr(yolo_model, 'names') and class_id in yolo_model.names:
                class_name = yolo_model.names[class_id].lower()
                print(f"  Box {i}: {class_name} ({confidence:.1%})")
            else:
                class_name = f"class_{class_id}"
                print(f"  Box {i}: Unknown class {class_id} ({confidence:.1%})")
            
            # Map class name to category (your model only has biodegradable/recyclable)
            category = class_name  # Already 'biodegradable' or 'recyclable'
            
            # Get random example object name
            import random
            object_names = CLASS_CONFIG.get(category, {}).get('examples', [f"{category.capitalize()} Item"])
            object_name = random.choice(object_names)
            
            # Create detection object
            detection = {
                'id': f"{int(time.time())}_{i}",
                'class': class_name,
                'name': object_name,
                'category': category,
                'confidence': round(confidence * 100, 1),
                'confidence_raw': confidence,
                'dustbinColor': CLASS_CONFIG.get(category, {}).get('dustbinColor', 'Gray'),
                'description': f"{object_name} detected with {round(confidence * 100, 1)}% confidence.",
                'properties': {
                    'material': class_name.capitalize(),
                    'decomposition_time': '2-6 weeks' if category == 'biodegradable' else '50-500 years',
                    'recycling_tips': 'Compost in green bin' if category == 'biodegradable' else 'Rinse and recycle in blue bin',
                    'detection_time': time.strftime('%H:%M:%S')
                },
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'icon': CLASS_CONFIG.get(category, {}).get('icon', '🗑️'),
                'color': CLASS_CONFIG.get(category, {}).get('color', '#666666'),
                'bbox': {
                    'x': float(x1),
                    'y': float(y1),
                    'width': float(x2 - x1),
                    'height': float(y2 - y1),
                    'confidence': round(confidence * 100, 1)
                }
            }
            
            detections.append(detection)
            
        except Exception as e:
            print(f"❌ Error processing box {i}: {e}")
            traceback.print_exc()
            continue
    
    return detections

@app.route('/')
def home():
    return jsonify({
        'message': 'Waste Classification API',
        'model_status': 'LOADED' if model_loaded else 'MOCK MODE',
        'model_path': MODEL_PATH if model_loaded else 'None',
        'classes': list(yolo_model.names.values()) if model_loaded else [],
        'available_classes': CLASS_CONFIG,
        'endpoints': {
            '/detect': 'POST - Detect waste from base64 image (for React)',
            '/detect_multiple': 'POST - Detect waste from file upload',
            '/test_model': 'GET - Test model with sample images',
            '/health': 'GET - Health check',
            '/classes': 'GET - Get available classes'
        }
    })

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'model_loaded': model_loaded,
        'model_path': MODEL_PATH,
        'available_classes': list(yolo_model.names.values()) if model_loaded else [],
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    })

@app.route('/classes', methods=['GET'])
def get_classes():
    """Get available waste classes"""
    return jsonify({
        'success': True,
        'model_classes': list(yolo_model.names.values()) if model_loaded else [],
        'frontend_classes': CLASS_CONFIG,
        'tips': {
            'biodegradable': 'Point camera at food waste, banana peels, vegetable scraps',
            'recyclable': 'Point camera at plastic bottles, cans, cardboard, glass'
        }
    })

@app.route('/test', methods=['GET'])
def test_endpoint():
    """Simple test endpoint"""
    return jsonify({
        'success': True,
        'message': 'API is working!',
        'model_loaded': model_loaded,
        'model_classes': list(yolo_model.names.values()) if model_loaded else [],
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    })

@app.route('/test_model', methods=['GET'])
def test_model():
    """Test the model with sample images"""
    try:
        if not model_loaded:
            return jsonify({
                'success': False,
                'error': 'Model not loaded',
                'detections': []
            }), 500
        
        print("\n🧪 Testing model with different confidence thresholds...")
        
        # Create a simple test image (solid colors)
        test_cases = []
        
        # Test 1: Green image (biodegradable-like)
        green_img = np.zeros((300, 300, 3), dtype=np.uint8)
        green_img[:, :] = [0, 150, 0]  # Green
        
        # Test 2: Blue image (recyclable-like)
        blue_img = np.zeros((300, 300, 3), dtype=np.uint8)
        blue_img[:, :] = [0, 0, 150]  # Blue
        
        test_images = [
            ('green_test', green_img, 'biodegradable-like'),
            ('blue_test', blue_img, 'recyclable-like')
        ]
        
        results = []
        
        for name, img, description in test_images:
            for conf_threshold in [0.05, 0.1, 0.15, 0.2]:
                yolo_results = yolo_model(img, conf=conf_threshold, verbose=False)
                detections = process_yolo_prediction(yolo_results)
                
                results.append({
                    'test_name': name,
                    'description': description,
                    'confidence_threshold': conf_threshold,
                    'detections_found': len(detections),
                    'detections': detections
                })
        
        return jsonify({
            'success': True,
            'test_results': results,
            'model_info': {
                'classes': list(yolo_model.names.values()),
                'path': MODEL_PATH,
                'recommended_confidence': 0.15
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/detect', methods=['POST'])
def detect_from_base64():
    """MAIN ENDPOINT FOR REACT - Accepts base64 image"""
    try:
        if not model_loaded:
            return jsonify({
                'success': False,
                'error': 'Model not loaded. Check server console.',
                'detections': [],
                'model_info': {'loaded': False}
            }), 500
        
        data = request.json
        if not data or 'image' not in data:
            return jsonify({'error': 'No image data provided'}), 400
        
        print("\n📸 ===== NEW DETECTION REQUEST =====")
        print(f"📦 Request received at: {time.strftime('%H:%M:%S')}")
        
        # Decode base64 image
        image_data = data['image']
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        image_np = np.array(image)
        
        print(f"📐 Original image size: {image.width}x{image.height}")
        
        # Resize if too large (better for YOLO)
        max_size = 640
        if image.width > max_size or image.height > max_size:
            scale = min(max_size / image.width, max_size / image.height)
            new_width = int(image.width * scale)
            new_height = int(image.height * scale)
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            image_np = np.array(image)
            print(f"📐 Resized to: {new_width}x{new_height}")
        
        print(f"🔍 Running YOLOv8 inference...")
        
        # Try multiple confidence thresholds
        confidence_thresholds = [0.05, 0.1, 0.15, 0.2]
        best_detections = []
        best_threshold = 0.1
        
        for conf in confidence_thresholds:
            results = yolo_model(image_np, conf=conf, verbose=False)
            detections = process_yolo_prediction(results)
            
            if len(detections) > len(best_detections):
                best_detections = detections
                best_threshold = conf
            
            print(f"  Threshold {conf}: {len(detections)} detections")
        
        print(f"✅ Using threshold {best_threshold}: {len(best_detections)} detections")
        
        # Count by category
        waste_counts = {}
        for detection in best_detections:
            category = detection['category']
            waste_counts[category] = waste_counts.get(category, 0) + 1
        
        # Prepare response
        response = {
            'success': True,
            'detections': best_detections,
            'waste_counts': waste_counts,
            'total_detections': len(best_detections),
            'model_used': 'yolov8',
            'confidence_threshold_used': best_threshold,
            'image_info': {
                'original_size': f"{image.width}x{image.height}",
                'processed_size': f"{image_np.shape[1]}x{image_np.shape[0]}"
            },
            'model_info': {
                'classes': list(yolo_model.names.values()),
                'recommended_items': {
                    'biodegradable': ['Banana peel', 'Food waste', 'Vegetable scraps'],
                    'recyclable': ['Plastic bottle', 'Soda can', 'Cardboard box']
                }
            },
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Add tips if no detections
        if len(best_detections) == 0:
            response['tips'] = [
                'Try pointing camera at actual waste items',
                'Ensure good lighting',
                'Try different angles',
                'Lower confidence threshold (currently tried: ' + ', '.join([str(c) for c in confidence_thresholds]) + ')',
                'Your model is trained for: ' + ', '.join(list(yolo_model.names.values()))
            ]
        
        print(f"🎯 Detection complete: {len(best_detections)} objects found")
        print(f"📊 Waste counts: {waste_counts}")
        print("="*50)
        
        return jsonify(response)
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'detections': [],
            'model_info': {'loaded': model_loaded}
        }), 500

@app.route('/detect_multiple', methods=['POST'])
def detect_multiple():
    """Original endpoint for file uploads"""
    try:
        if not model_loaded:
            return jsonify({
                'success': False,
                'error': 'Model not loaded',
                'detections': []
            }), 500
        
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        
        # Read image
        img_bytes = file.read()
        image = Image.open(io.BytesIO(img_bytes)).convert('RGB')
        image_np = np.array(image)
        
        # Run inference with lower confidence
        results = yolo_model(image_np, conf=0.1)
        
        # Process results
        detections = process_yolo_prediction(results)
        
        return jsonify({
            'success': True,
            'detections': detections,
            'count': len(detections)
        })
        
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

if __name__ == '__main__':
    port = 5001
    
    print(f"\n{'='*70}")
    print(f"🌐 API STARTING ON PORT {port}")
    print(f"{'='*70}")
    print(f"📡 URL: http://localhost:{port}")
    print(f"🔗 Test: http://localhost:{port}/test")
    print(f"🔗 Health: http://localhost:{port}/health")
    print(f"🔗 Classes: http://localhost:{port}/classes")
    print(f"🔗 Model Test: http://localhost:{port}/test_model")
    
    if model_loaded:
        print(f"\n✅ READY FOR DETECTION")
        print(f"   Model: YOLOv8 ({MODEL_PATH})")
        print(f"   Classes: {list(yolo_model.names.values())}")
        print(f"   Total classes: {len(yolo_model.names)}")
        print(f"\n📱 Frontend should send POST requests to:")
        print(f"   http://localhost:{port}/detect")
        print(f"   with JSON: {{'image': 'base64_string_here'}}")
        print(f"\n💡 TIPS:")
        print(f"   - Model only detects: {', '.join(list(yolo_model.names.values()))}")
        print(f"   - Point camera at actual waste items")
        print(f"   - Try confidence thresholds: 0.05, 0.1, 0.15")
    else:
        print(f"\n❌ MODEL NOT LOADED")
        print(f"   Check: {ABSOLUTE_MODEL_PATH}")
        print(f"   Expected path relative to backend/: ../runs/detect/train5/weights/best.pt")
    
    print(f"{'='*70}\n")
    
    app.run(host='0.0.0.0', port=port, debug=True)