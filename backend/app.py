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
import sys
from pathlib import Path
import hashlib
import random

print("\n" + "="*70)
print("🚀 STARTING WASTE DETECTION API")
print("="*70)

# ==================== ENVIRONMENT INFO ====================
print(f"🐍 Python {sys.version}")
print(f"🖥️  Platform: {sys.platform}")
print(f"📁 Working Directory: {os.getcwd()}")

# ==================== MODEL LOADING ====================
# Try multiple model paths in order of preference
MODEL_PATHS = [
    Path("high_accuracy_training/waste_detector_pro/weights/best.pt"),
    Path("../runs/detect/train5/weights/best.pt"),
    Path("runs/detect/train/weights/best.pt"),
    Path("best.pt"),
    Path("yolov8m.pt"),
]

# Alternative model names to search for
ALTERNATIVE_NAMES = ["best.pt", "last.pt", "yolov8n.pt", "yolov8s.pt", "yolov8m.pt", "yolov8l.pt"]

print(f"\n🔍 Looking for models at:")
for path in MODEL_PATHS:
    print(f"   - {path}")

yolo_model = None
MODEL_PATH = None
model_loaded = False
model_hash = None

def find_available_models():
    """Search for all available model files"""
    found_models = []
    
    # Check primary paths first
    for path in MODEL_PATHS:
        if path.exists():
            size_mb = path.stat().st_size / 1024 / 1024
            found_models.append({
                'path': path,
                'priority': 'PRIMARY',
                'size_mb': size_mb
            })
    
    # Search in common directories
    search_dirs = [
        Path("."),
        Path("high_accuracy_training"),
        Path("runs/detect"),
        Path("../runs/detect"),
        Path("models"),
        Path("../models"),
    ]
    
    for dir_path in search_dirs:
        if dir_path.exists():
            for alt_name in ALTERNATIVE_NAMES:
                try:
                    for pt_file in dir_path.rglob(f"*{alt_name}"):
                        if any(str(pt_file) == str(m['path']) for m in found_models):
                            continue
                        size_mb = pt_file.stat().st_size / 1024 / 1024
                        found_models.append({
                            'path': pt_file,
                            'priority': 'SEARCHED',
                            'size_mb': size_mb
                        })
                except Exception as e:
                    continue
    
    return found_models

def calculate_model_hash(model_path):
    """Calculate hash of model file for caching"""
    try:
        with open(model_path, 'rb') as f:
            file_hash = hashlib.md5()
            chunk = f.read(8192)
            while chunk:
                file_hash.update(chunk)
                chunk = f.read(8192)
            return file_hash.hexdigest()[:8]
    except:
        return "unknown"

try:
    from ultralytics import YOLO, __version__ as ultralytics_version
    print(f"✅ ultralytics v{ultralytics_version} imported successfully")
    
    # Find all available models
    print("\n📂 Searching for model files...")
    available_models = find_available_models()
    
    if available_models:
        print(f"\n📊 Found {len(available_models)} model(s):")
        for i, model_info in enumerate(available_models):
            print(f"   {i+1}. {model_info['path']} ({model_info['size_mb']:.1f} MB) [{model_info['priority']}]")
    else:
        print("\n❌ No model files found locally!")
    
    # Try loading models in priority order
    for model_info in sorted(available_models, 
                             key=lambda x: (0 if x['priority'] == 'PRIMARY' else 1, -x['size_mb'])):
        try:
            model_path = model_info['path']
            print(f"\n🔄 Attempting to load: {model_path}")
            
            yolo_model = YOLO(str(model_path))
            MODEL_PATH = str(model_path)
            model_loaded = True
            model_hash = calculate_model_hash(model_path)
            
            # Test the model with minimal validation
            print(f"✅ Model loaded successfully!")
            print(f"📋 Model classes: {yolo_model.names}")
            print(f"🎯 Model type: {yolo_model.task}")
            print(f"📦 File size: {model_info['size_mb']:.1f} MB")
            print(f"🔢 Hash: {model_hash}")
            
            # Test with a small dummy inference
            print("🧪 Running quick model validation...")
            test_img = np.zeros((100, 100, 3), dtype=np.uint8)
            test_results = yolo_model(test_img, conf=0.1, verbose=False)
            print("✅ Model validation passed")
            
            break
            
        except Exception as e:
            print(f"⚠️  Failed to load {model_path}: {str(e)[:100]}")
            continue
    
    # If no local model found, try to use/download base model
    if not model_loaded:
        print("\n🔄 No local models available, attempting to use base model...")
        try:
            yolo_model = YOLO('yolov8m.pt')
            MODEL_PATH = "yolov8m.pt (auto-downloaded)"
            model_loaded = True
            model_hash = "auto-downloaded"
            print("✅ Base YOLOv8m model loaded (auto-downloaded)")
            print("💡 Train your own model for better waste detection!")
        except Exception as e:
            print(f"❌ Cannot load base model: {e}")
            print("   Check your internet connection or install models manually")
            
except ImportError as e:
    print(f"\n❌ CANNOT IMPORT ULTRALYTICS: {e}")
    print("\n💡 Install with:")
    print("   pip install ultralytics")
    print("   or")
    print("   pip install ultralytics==8.0.0")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ UNEXPECTED ERROR: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*70)
if model_loaded:
    print(f"🚀 MODEL READY: {Path(MODEL_PATH).name} ({model_hash})")
else:
    print("⚠️  NO MODEL LOADED - Limited functionality")
print("="*70 + "\n")

# ==================== FLASK APP ====================
app = Flask(__name__)
CORS(app)

# ==================== WASTE CONFIGURATION ====================
CLASS_CONFIG = {
    "biodegradable": {
        "name": "Biodegradable",
        "dustbinColor": "Green",
        "dustbinName": "Green Bin (Compost)",
        "icon": "🍃",
        "color": "#10b981",
        "disposal_instructions": [
            "Place in GREEN compost bin",
            "Can be composted at home or facility",
            "Breaks down naturally in 2-6 weeks",
            "Do not mix with recyclables or hazardous waste"
        ],
        "examples": ["Food waste", "Vegetable scraps", "Fruit peels", "Coffee grounds"]
    },
    "recyclable": {
        "name": "Recyclable", 
        "dustbinColor": "Blue",
        "dustbinName": "Blue Bin (Recycling)",
        "icon": "♻️",
        "color": "#3b82f6",
        "disposal_instructions": [
            "Place in BLUE recycling bin",
            "Rinse if dirty, remove caps/lids",
            "Flatten to save space",
            "Check local recycling rules"
        ],
        "examples": ["Plastic bottles", "Aluminum cans", "Glass jars", "Cardboard"]
    },
    "hazardous": {
        "name": "Hazardous",
        "dustbinColor": "Red",
        "dustbinName": "Red Bin (Hazardous)",
        "icon": "⚠️",
        "color": "#ef4444",
        "disposal_instructions": [
            "Place in RED hazardous waste bin",
            "DO NOT mix with regular waste",
            "Handle with care - wear gloves if needed",
            "Take to special collection points"
        ],
        "examples": ["Batteries", "Electronics", "Medicines", "Paint cans"]
    },
    "non_recyclable": {
        "name": "Non-Recyclable",
        "dustbinColor": "Black",
        "dustbinName": "Black Bin (General Waste)",
        "icon": "🗑️",
        "color": "#374151",
        "disposal_instructions": [
            "Place in BLACK general waste bin",
            "For landfill disposal only",
            "Minimize usage when possible",
            "Ensure waste is properly bagged"
        ],
        "examples": ["Plastic bags", "Ceramics", "Styrofoam", "Sanitary products"]
    }
}

WASTE_BINS = {
    "biodegradable": {
        "name": "Green Bin",
        "color": "#10b981",
        "icon": "🍃",
        "description": "For compostable organic waste",
        "acceptable_items": [
            "Food scraps",
            "Vegetable peels", 
            "Fruit waste",
            "Coffee grounds",
            "Egg shells",
            "Tea bags",
            "Garden waste"
        ],
        "not_acceptable": [
            "Plastic bags",
            "Metal",
            "Glass",
            "Hazardous materials"
        ]
    },
    "recyclable": {
        "name": "Blue Bin",
        "color": "#3b82f6",
        "icon": "♻️",
        "description": "For recyclable materials",
        "acceptable_items": [
            "Plastic bottles",
            "Aluminum cans",
            "Glass bottles",
            "Cardboard boxes",
            "Newspapers",
            "Clean paper"
        ],
        "not_acceptable": [
            "Food-contaminated items",
            "Plastic bags",
            "Styrofoam",
            "Broken glass"
        ]
    },
    "hazardous": {
        "name": "Red Bin",
        "color": "#ef4444",
        "icon": "⚠️",
        "description": "For hazardous and special waste",
        "acceptable_items": [
            "Batteries",
            "Electronics",
            "Medications",
            "Paint and solvents",
            "Chemicals"
        ],
        "not_acceptable": [
            "Regular household waste",
            "Food waste",
            "Recyclables",
            "Biodegradable items"
        ]
    },
    "non_recyclable": {
        "name": "Black Bin",
        "color": "#374151",
        "icon": "🗑️",
        "description": "For non-recyclable general waste",
        "acceptable_items": [
            "Plastic bags",
            "Ceramics",
            "Styrofoam",
            "Sanitary products",
            "Broken glassware"
        ],
        "not_acceptable": [
            "Hazardous waste",
            "Recyclables",
            "Biodegradable waste",
            "Large electronics"
        ]
    }
}

WASTE_GUIDE = {
    "summary": "Understanding proper waste disposal categories",
    "bins": [
        {
            "name": "Green Bin",
            "color": "Green",
            "icon": "🍃",
            "category": "Biodegradable Waste",
            "description": "Food scraps, paper, garden waste, wood, leaves, organic materials",
            "tips": ["Compost within 2-6 weeks", "Suitable for organic recycling"]
        },
        {
            "name": "Blue Bin",
            "color": "Blue",
            "icon": "♻️",
            "category": "Recyclable Waste",
            "description": "Plastic bottles, glass, metal cans, cardboard, paper, aluminum",
            "tips": ["Can be processed & reused", "Clean and dry before disposal"]
        },
        {
            "name": "Red Bin",
            "color": "Red",
            "icon": "⚠️",
            "category": "Hazardous Waste",
            "description": "Batteries, chemicals, electronics, medicines, paint, solvents",
            "tips": ["Special disposal required", "Do not mix with regular waste"]
        },
        {
            "name": "Black Bin",
            "color": "Black",
            "icon": "🗑️",
            "category": "Non-Recyclable",
            "description": "Plastic bags, ceramics, composite materials, styrofoam, sanitary",
            "tips": ["Landfill disposal only", "Minimize usage"]
        }
    ]
}

# Ensure upload directory exists
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ==================== HELPER FUNCTIONS ====================
def get_category_from_class(class_name):
    """Map detected class name to waste category"""
    class_name_lower = class_name.lower()
    
    # Biodegradable items
    biodegradable_items = ['banana', 'apple', 'fruit', 'vegetable', 'food', 'organic', 'compost', 'leaf', 'grass', 'wood', 'coffee', 'egg', 'tea', 'garden', 'plant']
    
    # Recyclable items
    recyclable_items = ['plastic', 'bottle', 'can', 'glass', 'jar', 'cardboard', 'box', 'paper', 'newspaper', 'magazine', 'aluminum', 'metal', 'container']
    
    # Hazardous items
    hazardous_items = ['battery', 'electronic', 'phone', 'laptop', 'medicine', 'chemical', 'paint', 'oil', 'toxic', 'thermometer', 'bulb', 'light']
    
    # Non-recyclable items
    non_recyclable_items = ['plastic_bag', 'bag', 'styrofoam', 'foam', 'ceramic', 'broken', 'diaper', 'sanitary', 'tissue', 'wipe', 'cigarette', 'wrapper', 'chip']
    
    # Check which category the object belongs to
    for item in biodegradable_items:
        if item in class_name_lower:
            return 'biodegradable'
    
    for item in recyclable_items:
        if item in class_name_lower:
            return 'recyclable'
    
    for item in hazardous_items:
        if item in class_name_lower:
            return 'hazardous'
    
    for item in non_recyclable_items:
        if item in class_name_lower:
            return 'non_recyclable'
    
    # Default based on common patterns
    if any(word in class_name_lower for word in ['food', 'fruit', 'veg']):
        return 'biodegradable'
    elif any(word in class_name_lower for word in ['plastic', 'bottle', 'can']):
        return 'recyclable'
    elif any(word in class_name_lower for word in ['battery', 'electronic']):
        return 'hazardous'
    else:
        return 'non_recyclable'

def get_object_name(detected_class):
    """Convert YOLO class names to proper object names"""
    detected_class_lower = detected_class.lower()
    
    object_names = {
        # Biodegradable items
        'banana': 'Banana Peel',
        'apple': 'Apple Core',
        'fruit': 'Fruit Waste',
        'vegetable': 'Vegetable Scraps',
        'food': 'Food Waste',
        'organic': 'Organic Waste',
        'compost': 'Compostable Material',
        'leaf': 'Leaves',
        'grass': 'Grass Clippings',
        'wood': 'Wood Chips',
        'coffee': 'Coffee Grounds',
        'egg': 'Egg Shells',
        'tea': 'Tea Bag',
        'garden': 'Garden Waste',
        
        # Recyclable items
        'plastic': 'Plastic Item',
        'bottle': 'Plastic Bottle',
        'can': 'Aluminum Can',
        'glass': 'Glass Bottle',
        'jar': 'Glass Jar',
        'cardboard': 'Cardboard Box',
        'box': 'Cardboard Box',
        'paper': 'Paper',
        'newspaper': 'Newspaper',
        'magazine': 'Magazine',
        'aluminum': 'Aluminum Can',
        'metal': 'Metal Container',
        'container': 'Container',
        
        # Hazardous items
        'battery': 'Battery',
        'electronic': 'Electronic Device',
        'phone': 'Mobile Phone',
        'laptop': 'Laptop',
        'medicine': 'Medicine',
        'chemical': 'Chemical Container',
        'paint': 'Paint Can',
        'oil': 'Motor Oil',
        'toxic': 'Toxic Substance',
        'thermometer': 'Thermometer',
        'bulb': 'Light Bulb',
        'light': 'Light Bulb',
        
        # Non-recyclable items
        'plastic_bag': 'Plastic Bag',
        'bag': 'Plastic Bag',
        'styrofoam': 'Styrofoam',
        'foam': 'Styrofoam',
        'ceramic': 'Ceramic Plate',
        'broken': 'Broken Item',
        'diaper': 'Diaper',
        'sanitary': 'Sanitary Product',
        'tissue': 'Used Tissue',
        'wipe': 'Cleaning Wipe',
        'cigarette': 'Cigarette Butt',
        'wrapper': 'Chip Bag',
        'chip': 'Chip Bag'
    }
    
    # Check for exact matches first
    if detected_class_lower in object_names:
        return object_names[detected_class_lower]
    
    # Check for partial matches
    for key, value in object_names.items():
        if key in detected_class_lower:
            return value
    
    # Default: capitalize and format
    return detected_class.replace('_', ' ').title()

def process_yolo_prediction(results):
    """Convert YOLOv8 results to frontend format"""
    detections = []
    
    if not results or len(results) == 0:
        return detections
    
    if results[0].boxes is None:
        return detections
    
    boxes = results[0].boxes
    
    for i, box in enumerate(boxes):
        try:
            # Extract data
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            confidence = float(box.conf[0].cpu().numpy())
            class_id = int(box.cls[0].cpu().numpy())
            
            # Get class name from model
            if hasattr(yolo_model, 'names') and class_id in yolo_model.names:
                detected_class = yolo_model.names[class_id]
                print(f"  Object {i}: {detected_class} ({confidence:.1%})")
            else:
                detected_class = f"class_{class_id}"
                print(f"  Object {i}: Unknown class {class_id} ({confidence:.1%})")
            
            # Get proper object name
            object_name = get_object_name(detected_class)
            
            # Map detected object to waste category
            category = get_category_from_class(detected_class)
            
            # Get bin information
            class_info = CLASS_CONFIG.get(category, {})
            bin_info = WASTE_BINS.get(category, {})
            
            # Create detection object
            detection = {
                'id': f"{int(time.time())}_{i}_{hashlib.md5(f'{x1}{y1}{x2}{y2}'.encode()).hexdigest()[:6]}",
                'class': detected_class,
                'name': object_name,
                'category': category,
                'confidence': round(confidence * 100, 1),
                'confidence_raw': confidence,
                'dustbinColor': class_info.get('dustbinColor', 'Black'),
                'dustbinName': class_info.get('dustbinName', 'General Waste Bin'),
                'description': f"Detected: {object_name}. Belongs in {class_info.get('dustbinName', 'appropriate bin')}.",
                'properties': {
                    'material': object_name,
                    'detection_time': time.strftime('%H:%M:%S')
                },
                'disposal_instructions': class_info.get('disposal_instructions', [
                    f"Place in {class_info.get('dustbinName', 'appropriate bin')}"
                ]),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'icon': class_info.get('icon', '🗑️'),
                'color': class_info.get('color', '#666666'),
                'bbox': {
                    'x': float(x1),
                    'y': float(y1),
                    'width': float(x2 - x1),
                    'height': float(y2 - y1),
                    'confidence': round(confidence * 100, 1)
                },
                'bin_info': bin_info
            }
            
            detections.append(detection)
            print(f"    → Classified as: {object_name} → {category.upper()} → {class_info.get('dustbinName')}")
            
        except Exception as e:
            print(f"❌ Error processing box {i}: {e}")
            continue
    
    return detections

def optimize_image_for_detection(image_np, target_size=640):
    """Optimize image for YOLO detection"""
    height, width = image_np.shape[:2]
    
    # Calculate scale factor
    scale = min(target_size / width, target_size / height)
    
    if scale < 1:
        new_width = int(width * scale)
        new_height = int(height * scale)
        image_np = cv2.resize(image_np, (new_width, new_height), interpolation=cv2.INTER_AREA)
    
    return image_np

# ==================== API ROUTES ====================
@app.route('/')
def home():
    return jsonify({
        'message': 'Waste Classification API',
        'model_status': 'LOADED' if model_loaded else 'NOT LOADED',
        'model_path': MODEL_PATH,
        'model_hash': model_hash,
        'classes': list(yolo_model.names.values()) if model_loaded else [],
        'available_classes': CLASS_CONFIG,
        'waste_bins': WASTE_BINS,
        'waste_guide': WASTE_GUIDE,
        'endpoints': {
            '/detect': 'POST - Detect waste from base64 image',
            '/health': 'GET - Health check',
            '/classes': 'GET - Get available classes',
            '/model-info': 'GET - Get model information',
            '/bin-info/<type>': 'GET - Get bin information',
            '/waste-guide': 'GET - Get waste classification guide',
            '/stats': 'GET - Get waste statistics'
        }
    })

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'model_loaded': model_loaded,
        'model_path': MODEL_PATH,
        'model_hash': model_hash,
        'available_classes': list(yolo_model.names.values()) if model_loaded else [],
        'bins_configured': len(WASTE_BINS)
    })

@app.route('/model-info', methods=['GET'])
def model_info():
    """Get detailed model information"""
    if not model_loaded:
        return jsonify({
            'status': 'no_model',
            'message': 'No model is currently loaded'
        })
    
    model_data = {
        'status': 'loaded',
        'model_path': MODEL_PATH,
        'model_name': Path(MODEL_PATH).name,
        'model_hash': model_hash,
        'num_classes': len(yolo_model.names),
        'classes': yolo_model.names,
        'class_list': list(yolo_model.names.values()),
        'device': str(yolo_model.device),
        'task': yolo_model.task if hasattr(yolo_model, 'task') else 'detection',
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Add model stats if available
    try:
        model_data['model_size_mb'] = round(os.path.getsize(MODEL_PATH) / 1024 / 1024, 1)
    except:
        pass
    
    return jsonify(model_data)

@app.route('/classes', methods=['GET'])
def get_classes():
    """Get available waste classes"""
    return jsonify({
        'success': True,
        'model_classes': list(yolo_model.names.values()) if model_loaded else [],
        'frontend_classes': CLASS_CONFIG,
        'waste_bins': WASTE_BINS,
        'waste_guide': WASTE_GUIDE,
        'tips': {
            'biodegradable': 'Point camera at food waste, banana peels, vegetable scraps',
            'recyclable': 'Point camera at plastic bottles, cans, cardboard, glass',
            'hazardous': 'Point camera at batteries, electronics, chemicals',
            'non_recyclable': 'Point camera at plastic bags, ceramics, styrofoam'
        }
    })

@app.route('/bin-info/<bin_type>', methods=['GET'])
def get_bin_info(bin_type):
    """Get detailed information about a specific waste bin type"""
    if bin_type not in WASTE_BINS:
        return jsonify({
            'success': False,
            'error': f"Bin type '{bin_type}' not found. Available types: {list(WASTE_BINS.keys())}"
        }), 404
    
    bin_info = WASTE_BINS[bin_type].copy()
    bin_info['success'] = True
    bin_info['type'] = bin_type
    
    return jsonify(bin_info)

@app.route('/all-bin-info', methods=['GET'])
def get_all_bin_info():
    """Get information about all waste bins"""
    return jsonify({
        'success': True,
        'bins': WASTE_BINS,
        'count': len(WASTE_BINS),
        'waste_guide': WASTE_GUIDE,
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    })

@app.route('/waste-guide', methods=['GET'])
def get_waste_guide():
    """Get comprehensive waste classification guide"""
    return jsonify({
        'success': True,
        'guide': WASTE_GUIDE,
        'bins': WASTE_BINS,
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    })

@app.route('/stats', methods=['GET'])
def get_waste_stats():
    """Get waste statistics and information"""
    return jsonify({
        'success': True,
        'stats': {
            'total_bins': 4,
            'bins': [
                {'name': 'Green Bin', 'items': len(WASTE_BINS['biodegradable']['acceptable_items']), 'color': '#10b981'},
                {'name': 'Blue Bin', 'items': len(WASTE_BINS['recyclable']['acceptable_items']), 'color': '#3b82f6'},
                {'name': 'Red Bin', 'items': len(WASTE_BINS['hazardous']['acceptable_items']), 'color': '#ef4444'},
                {'name': 'Black Bin', 'items': len(WASTE_BINS['non_recyclable']['acceptable_items']), 'color': '#374151'}
            ],
            'total_acceptable_items': sum(len(bin['acceptable_items']) for bin in WASTE_BINS.values()),
            'decomposition_times': {
                'biodegradable': '2-6 weeks',
                'recyclable': '50-500 years',
                'hazardous': 'Indefinite (requires special handling)',
                'non_recyclable': '100-1000+ years'
            }
        },
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    })

@app.route('/test', methods=['GET'])
def test_endpoint():
    """Simple test endpoint"""
    return jsonify({
        'success': True,
        'message': 'API is working!',
        'model_loaded': model_loaded,
        'model_classes': list(yolo_model.names.values()) if model_loaded else [],
        'class_config': CLASS_CONFIG,
        'bin_config': WASTE_BINS,
        'waste_guide': WASTE_GUIDE,
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'model_path': MODEL_PATH
    })

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
        
        print(f"\n📸 ===== NEW DETECTION REQUEST =====")
        print(f"📦 Request received at: {time.strftime('%H:%M:%S')}")
        
        start_time = time.time()
        
        # Decode base64 image
        image_data = data['image']
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        image_np = np.array(image)
        
        print(f"📐 Original image size: {image.width}x{image.height}")
        
        # Optimize image for detection
        image_np = optimize_image_for_detection(image_np, target_size=640)
        print(f"📐 Optimized size: {image_np.shape[1]}x{image_np.shape[0]}")
        
        print(f"🔍 Running YOLOv8 object detection...")
        
        # Get confidence threshold from request or use default
        confidence_threshold = float(data.get('confidence', 0.25))
        
        # Run inference
        inference_start = time.time()
        results = yolo_model(image_np, conf=confidence_threshold, verbose=False)
        inference_time = time.time() - inference_start
        
        # Process results
        detections = process_yolo_prediction(results)
        
        # Count by category
        waste_counts = {}
        bins_used = []
        
        for detection in detections:
            category = detection['category']
            waste_counts[category] = waste_counts.get(category, 0) + 1
            
            # Track unique bins used
            bin_name = detection.get('dustbinName', 'General Bin')
            if bin_name not in bins_used:
                bins_used.append(bin_name)
        
        total_time = time.time() - start_time
        
        print(f"✅ Object detection complete: {len(detections)} objects found")
        print(f"📊 Waste counts: {waste_counts}")
        print(f"🗑️  Bins needed: {bins_used}")
        print(f"⏱️  Detection time: {inference_time:.2f}s, Total time: {total_time:.2f}s")
        print("="*50)
        
        # Prepare bin summary
        bin_summary = []
        for category, count in waste_counts.items():
            bin_info = WASTE_BINS.get(category, {})
            bin_summary.append({
                'category': category,
                'count': count,
                'bin_name': bin_info.get('name', 'General Bin'),
                'bin_color': bin_info.get('color', '#666666'),
                'bin_icon': bin_info.get('icon', '🗑️')
            })
        
        # Prepare response
        response = {
            'success': True,
            'detections': detections,
            'waste_counts': waste_counts,
            'bin_summary': bin_summary,
            'bins_needed': bins_used,
            'total_detections': len(detections),
            'performance': {
                'inference_time_ms': round(inference_time * 1000, 2),
                'total_time_ms': round(total_time * 1000, 2),
                'confidence_threshold_used': confidence_threshold
            },
            'image_info': {
                'original_size': f"{image.width}x{image.height}",
                'processed_size': f"{image_np.shape[1]}x{image_np.shape[0]}"
            },
            'model_info': {
                'model_name': Path(MODEL_PATH).name,
                'model_hash': model_hash,
                'classes': list(yolo_model.names.values()),
                'bins_available': list(WASTE_BINS.keys())
            },
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Add tips if no detections
        if len(detections) == 0:
            response['tips'] = [
                'Try pointing camera at actual waste objects',
                'Ensure good lighting',
                'Try different angles',
                f'Try lower confidence threshold (current: {confidence_threshold})',
                'Point camera at: plastic bottles, food waste, batteries, etc.'
            ]
        
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

# ==================== ERROR HANDLERS ====================
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found', 'success': False}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error', 'success': False}), 500

# ==================== MAIN EXECUTION ====================
if __name__ == '__main__':
    port = 5001
    
    print(f"\n{'='*70}")
    print(f"🌐 API STARTING ON PORT {port}")
    print(f"{'='*70}")
    print(f"📡 URL: http://localhost:{port}")
    print(f"🔗 Test: http://localhost:{port}/test")
    print(f"🔗 Health: http://localhost:{port}/health")
    print(f"🔗 Model Info: http://localhost:{port}/model-info")
    print(f"🔗 Classes: http://localhost:{port}/classes")
    print(f"🔗 Waste Guide: http://localhost:{port}/waste-guide")
    print(f"🔗 Stats: http://localhost:{port}/stats")
    print(f"🔗 Bin Info: http://localhost:{port}/bin-info/biodegradable")
    print(f"🔗 All Bin Info: http://localhost:{port}/all-bin-info")
    
    if model_loaded:
        print(f"\n✅ READY FOR OBJECT DETECTION")
        print(f"   Model: {Path(MODEL_PATH).name} ({model_hash})")
        print(f"   Classes: {list(yolo_model.names.values())}")
        print(f"   Total classes: {len(yolo_model.names)}")
        print(f"   Bins configured: {len(WASTE_BINS)}")
        print(f"\n📱 Frontend should send POST requests to:")
        print(f"   http://localhost:{port}/detect")
        print(f"   with JSON: {{'image': 'base64_string_here', 'confidence': 0.25}}")
        print(f"\n🗑️  WASTE BINS CONFIGURED (4 Bins):")
        print(f"   1. 🍃 GREEN BIN: Biodegradable waste")
        print(f"   2. ♻️ BLUE BIN: Recyclable materials")
        print(f"   3. ⚠️ RED BIN: Hazardous waste")
        print(f"   4. 🗑️ BLACK BIN: Non-recyclable general waste")
        print(f"\n💡 Model detects: {', '.join(list(yolo_model.names.values()))}")
        print(f"{'='*70}\n")
    else:
        print(f"\n❌ MODEL NOT LOADED")
        print(f"   Please check console for loading errors")
        print(f"   Models searched in: {', '.join([str(p) for p in MODEL_PATHS])}")
        print(f"{'='*70}\n")
    
    app.run(host='0.0.0.0', port=port, debug=True)