import React, { useState, useRef, useEffect } from 'react';
import Webcam from 'react-webcam';
import { Camera, Upload, RotateCw, X, Loader2, CheckCircle } from 'lucide-react';

const CameraSection = ({ onSingleDetection, onObjectsDetected }) => {
  const webcamRef = useRef(null);
  const [image, setImage] = useState(null);
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [mode, setMode] = useState('single'); // 'single' or 'multi'
  const [isUploading, setIsUploading] = useState(false);
  const [predictionResults, setPredictionResults] = useState([]);
  const [detectionCount, setDetectionCount] = useState(0);
  const [detectionHistory, setDetectionHistory] = useState([]);

  // Start camera
  const startCamera = () => {
    setIsCameraActive(true);
  };

  // Stop camera
  const stopCamera = () => {
    setIsCameraActive(false);
    setImage(null);
    setPredictionResults([]);
  };

  // Capture image
  const captureImage = () => {
    if (webcamRef.current) {
      const imageSrc = webcamRef.current.getScreenshot();
      setImage(imageSrc);
      setPredictionResults([]);
    }
  };

  // Retake image
  const retakeImage = () => {
    setImage(null);
    setPredictionResults([]);
  };

  // Mock detection for single object
  const detectSingleObject = () => {
    if (!image) {
      alert('Please capture an image first!');
      return;
    }

    setIsUploading(true);

    // Simulate AI processing
    setTimeout(() => {
      const mockResults = [
        {
          id: Date.now(),
          class: 'plastic',
          confidence: 0.92,
          name: 'Plastic Bottle',
          category: 'recyclable',
          timestamp: new Date().toLocaleString(),
          all_predictions: {
            plastic: 0.92,
            paper: 0.05,
            glass: 0.02,
            metal: 0.01
          }
        }
      ];

      const detectionData = {
        id: mockResults[0].id,
        name: mockResults[0].name,
        category: mockResults[0].category,
        confidence: Math.round(mockResults[0].confidence * 100),
        dustbinColor: mockResults[0].category === 'recyclable' ? 'Blue' : 
                      mockResults[0].category === 'biodegradable' ? 'Green' :
                      mockResults[0].category === 'hazardous' ? 'Red' : 'Black',
        description: `${mockResults[0].name} detected with ${Math.round(mockResults[0].confidence * 100)}% confidence.`,
        timestamp: mockResults[0].timestamp
      };

      setPredictionResults(mockResults);
      setDetectionCount(prev => prev + 1);
      setDetectionHistory(prev => [detectionData, ...prev.slice(0, 9)]);
      
      if (onSingleDetection) {
        onSingleDetection(detectionData);
      }
      
      setIsUploading(false);
    }, 1500);
  };

  // Mock detection for multiple objects
  const detectMultipleObjects = () => {
    if (!image) {
      alert('Please capture an image first!');
      return;
    }

    setIsUploading(true);

    // Simulate AI processing for multiple objects
    setTimeout(() => {
      const mockResults = [
        {
          id: Date.now() + 1,
          class: 'plastic',
          confidence: 0.92,
          name: 'Plastic Bottle',
          category: 'recyclable',
          timestamp: new Date().toLocaleString(),
          all_predictions: {
            plastic: 0.92,
            paper: 0.05,
            glass: 0.02,
            metal: 0.01
          }
        },
        {
          id: Date.now() + 2,
          class: 'paper',
          confidence: 0.87,
          name: 'Pizza Box',
          category: 'biodegradable',
          timestamp: new Date().toLocaleString(),
          all_predictions: {
            paper: 0.87,
            plastic: 0.08,
            glass: 0.03,
            metal: 0.02
          }
        },
        {
          id: Date.now() + 3,
          class: 'metal',
          confidence: 0.95,
          name: 'Soda Can',
          category: 'recyclable',
          timestamp: new Date().toLocaleString(),
          all_predictions: {
            metal: 0.95,
            plastic: 0.03,
            glass: 0.01,
            paper: 0.01
          }
        }
      ];

      const detectionDataArray = mockResults.map(obj => ({
        id: obj.id,
        name: obj.name,
        category: obj.category,
        confidence: Math.round(obj.confidence * 100),
        dustbinColor: obj.category === 'recyclable' ? 'Blue' : 
                     obj.category === 'biodegradable' ? 'Green' :
                     obj.category === 'hazardous' ? 'Red' : 'Black',
        description: `${obj.name} detected with ${Math.round(obj.confidence * 100)}% confidence.`,
        timestamp: obj.timestamp
      }));

      setPredictionResults(mockResults);
      setDetectionCount(prev => prev + mockResults.length);
      setDetectionHistory(prev => [...detectionDataArray, ...prev.slice(0, 9 - mockResults.length)]);
      
      if (onObjectsDetected) {
        onObjectsDetected(detectionDataArray);
      }
      
      setIsUploading(false);
    }, 2000);
  };

  // Get color based on waste type
  const getWasteColor = (type) => {
    const colors = {
      plastic: 'bg-blue-100 border-blue-200 text-blue-800',
      paper: 'bg-yellow-100 border-yellow-200 text-yellow-800',
      glass: 'bg-green-100 border-green-200 text-green-800',
      metal: 'bg-gray-100 border-gray-200 text-gray-800',
      organic: 'bg-amber-100 border-amber-200 text-amber-800',
      hazardous: 'bg-red-100 border-red-200 text-red-800',
      recyclable: 'bg-blue-100 border-blue-200 text-blue-800',
      biodegradable: 'bg-green-100 border-green-200 text-green-800'
    };
    return colors[type.toLowerCase()] || 'bg-gray-100 border-gray-200 text-gray-800';
  };

  // Export to CSV
  const exportToCSV = () => {
    if (detectionHistory.length === 0) {
      alert('No detection data to export!');
      return;
    }

    const headers = ['Timestamp', 'Object Name', 'Category', 'Confidence %', 'Dustbin Color'];
    const csvRows = [
      headers.join(','),
      ...detectionHistory.map(item => [
        `"${item.timestamp}"`,
        `"${item.name}"`,
        `"${item.category}"`,
        item.confidence,
        `"${item.dustbinColor}"`
      ].join(','))
    ];

    const csvContent = csvRows.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    
    link.setAttribute('href', url);
    link.setAttribute('download', `waste_detection_${new Date().getTime()}.csv`);
    link.style.visibility = 'hidden';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Clear all data
  const clearData = () => {
    if (window.confirm('Are you sure you want to clear all detection data?')) {
      setDetectionHistory([]);
      setDetectionCount(0);
      setPredictionResults([]);
    }
  };

  return (
    <div className="space-y-6">
      {/* Mode Selection */}
      <div className="flex flex-wrap gap-3">
        <button
          onClick={() => setMode('single')}
          className={`px-6 py-3 rounded-xl font-bold transition-all ${
            mode === 'single' 
              ? 'bg-gradient-to-r from-green-500 to-emerald-600 text-white shadow-lg' 
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          📦 Single Object
        </button>
        <button
          onClick={() => setMode('multi')}
          className={`px-6 py-3 rounded-xl font-bold transition-all ${
            mode === 'multi' 
              ? 'bg-gradient-to-r from-blue-500 to-indigo-600 text-white shadow-lg' 
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          📦📦 Multiple Objects
        </button>
      </div>

      {/* Camera Container */}
      <div className="relative h-[500px] bg-black rounded-xl overflow-hidden border-2 border-gray-700">
        {isCameraActive ? (
          !image ? (
            <Webcam
              ref={webcamRef}
              audio={false}
              screenshotFormat="image/jpeg"
              videoConstraints={{
                facingMode: 'environment',
                width: { ideal: 1280 },
                height: { ideal: 720 }
              }}
              className="w-full h-full object-cover"
            />
          ) : (
            <img 
              src={image} 
              alt="Captured" 
              className="w-full h-full object-cover"
            />
          )
        ) : (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center">
              <div className="text-6xl mb-4 opacity-50">📷</div>
              <div className="text-white text-xl font-medium">Camera is OFF</div>
            </div>
          </div>
        )}
      </div>

      {/* Camera Controls */}
      <div className="flex flex-wrap gap-4">
        {!isCameraActive ? (
          <button
            onClick={startCamera}
            className="bg-blue-500 hover:bg-blue-600 text-white font-bold py-3 px-6 rounded-lg flex items-center space-x-3"
          >
            <Camera className="h-5 w-5" />
            <span>Start Camera</span>
          </button>
        ) : (
          <>
            {!image ? (
              <button
                onClick={captureImage}
                className="bg-green-500 hover:bg-green-600 text-white font-bold py-3 px-6 rounded-lg flex items-center space-x-3 flex-1 min-w-[200px]"
              >
                <Camera className="h-5 w-5" />
                <span>Capture Image</span>
              </button>
            ) : (
              <>
                <button
                  onClick={retakeImage}
                  className="bg-gray-500 hover:bg-gray-600 text-white font-bold py-3 px-6 rounded-lg flex items-center space-x-3"
                >
                  <RotateCw className="h-5 w-5" />
                  <span>Retake</span>
                </button>
                <button
                  onClick={mode === 'single' ? detectSingleObject : detectMultipleObjects}
                  disabled={isUploading}
                  className="bg-blue-500 hover:bg-blue-600 text-white font-bold py-3 px-6 rounded-lg flex items-center space-x-3 flex-1 min-w-[200px] disabled:opacity-50"
                >
                  {isUploading ? (
                    <>
                      <Loader2 className="h-5 w-5 animate-spin" />
                      <span>Analyzing...</span>
                    </>
                  ) : (
                    <>
                      <Upload className="h-5 w-5" />
                      <span>{mode === 'single' ? 'Detect Object' : 'Detect Multiple Objects'}</span>
                    </>
                  )}
                </button>
              </>
            )}
            <button
              onClick={stopCamera}
              className="bg-red-500 hover:bg-red-600 text-white font-bold py-3 px-6 rounded-lg flex items-center space-x-3"
            >
              <X className="h-5 w-5" />
              <span>Stop Camera</span>
            </button>
          </>
        )}
      </div>

      {/* Results Display */}
      {predictionResults.length > 0 && (
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h3 className="text-xl font-bold mb-4 flex items-center">
            <CheckCircle className="h-6 w-6 text-green-500 mr-2" />
            Detection Results ({predictionResults.length} object{predictionResults.length > 1 ? 's' : ''})
          </h3>
          
          <div className="space-y-4">
            {predictionResults.map((result, index) => (
              <div key={result.id} className="p-4 border border-gray-200 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <div>
                    <h4 className="font-bold text-lg">{result.name}</h4>
                    <p className="text-gray-600 text-sm">{result.category}</p>
                  </div>
                  <span className={`px-3 py-1 rounded-full font-bold ${getWasteColor(result.class)}`}>
                    {result.class.toUpperCase()}
                  </span>
                </div>
                <div className="mt-2">
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-sm text-gray-600">Confidence</span>
                    <span className="font-bold">{Math.round(result.confidence * 100)}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-blue-500 h-2 rounded-full"
                      style={{ width: `${result.confidence * 100}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Data Management */}
      <div className="border-t border-gray-200 pt-6">
        <div className="flex flex-wrap items-center justify-between gap-4 mb-4">
          <h3 className="text-xl font-bold text-gray-800">Detection History</h3>
          <div className="flex flex-wrap gap-3">
            <button
              onClick={exportToCSV}
              disabled={detectionHistory.length === 0}
              className="bg-green-500 hover:bg-green-600 text-white font-medium py-2 px-4 rounded-lg flex items-center space-x-2 disabled:opacity-50"
            >
              <span>📥</span>
              <span>Export CSV</span>
            </button>
            
            <button
              onClick={clearData}
              disabled={detectionHistory.length === 0}
              className="bg-red-500 hover:bg-red-600 text-white font-medium py-2 px-4 rounded-lg flex items-center space-x-2 disabled:opacity-50"
            >
              <span>🗑️</span>
              <span>Clear Data</span>
            </button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
            <div className="text-2xl font-bold text-gray-800">{detectionCount}</div>
            <div className="text-sm text-gray-600">Total Detections</div>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
            <div className="text-2xl font-bold text-gray-800">
              {detectionHistory.length > 0 
                ? Math.round(detectionHistory.reduce((sum, item) => sum + item.confidence, 0) / detectionHistory.length)
                : 0}%
            </div>
            <div className="text-sm text-gray-600">Avg Confidence</div>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
            <div className="text-2xl font-bold text-gray-800">{detectionHistory.length}</div>
            <div className="text-sm text-gray-600">Records</div>
          </div>
        </div>

        {/* Recent Detections Table */}
        {detectionHistory.length > 0 && (
          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="overflow-x-auto">
              <table className="min-w-full">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-2 px-3 text-gray-600 font-medium">Time</th>
                    <th className="text-left py-2 px-3 text-gray-600 font-medium">Object</th>
                    <th className="text-left py-2 px-3 text-gray-600 font-medium">Category</th>
                    <th className="text-left py-2 px-3 text-gray-600 font-medium">Confidence</th>
                  </tr>
                </thead>
                <tbody>
                  {detectionHistory.slice(0, 5).map((item) => (
                    <tr key={item.id} className="border-b border-gray-100 last:border-b-0">
                      <td className="py-2 px-3 text-gray-700 text-sm">
                        {item.timestamp.split(',')[1]?.trim() || item.timestamp}
                      </td>
                      <td className="py-2 px-3 font-medium text-gray-800">{item.name}</td>
                      <td className="py-2 px-3">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          item.category === 'recyclable' ? 'bg-blue-100 text-blue-800' :
                          item.category === 'biodegradable' ? 'bg-green-100 text-green-800' :
                          'bg-red-100 text-red-800'
                        }`}>
                          {item.category}
                        </span>
                      </td>
                      <td className="py-2 px-3">
                        <span className="font-medium">{item.confidence}%</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CameraSection;