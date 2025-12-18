import React, { useState, useRef, useEffect } from 'react';
import Webcam from 'react-webcam';
import { Camera, Upload, RotateCw, X, Loader2, CheckCircle } from 'lucide-react';
import { wasteAPI } from '../services/api';

const CameraSection = ({ onSingleDetection, onObjectsDetected }) => {
  const webcamRef = useRef(null);
  const [image, setImage] = useState(null);
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [mode, setMode] = useState('single');
  const [isUploading, setIsUploading] = useState(false);
  const [predictionResults, setPredictionResults] = useState([]);
  const [detectionCount, setDetectionCount] = useState(0);
  const [detectionHistory, setDetectionHistory] = useState([]);
  const [backendStatus, setBackendStatus] = useState('checking');
  const [error, setError] = useState(null);

  // Check backend health on component mount
  useEffect(() => {
    checkBackendHealth();
  }, []);

  const checkBackendHealth = async () => {
    try {
      console.log('Checking backend health...');
      const response = await wasteAPI.checkHealth();
      console.log('Health response:', response);
      
      // FIXED: Axios returns response.data, not response directly
      const healthData = response.data || response;
      
      console.log('Health data:', healthData);
      
      if (healthData.status === 'healthy') {
        setBackendStatus('connected');
        setError(null);
        console.log('✅ Backend connected successfully');
      } else {
        setBackendStatus('error');
        setError(`Backend error: ${healthData.message || 'Unknown error'}`);
        console.log('❌ Backend not healthy:', healthData);
      }
    } catch (err) {
      console.error('Backend connection error:', err);
      setBackendStatus('disconnected');
      setError('Cannot connect to backend. Make sure it\'s running on port 5001');
    }
  };

  // Start camera
  const startCamera = () => {
    setIsCameraActive(true);
    setError(null);
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
      setError(null);
    }
  };

  // Retake image
  const retakeImage = () => {
    setImage(null);
    setPredictionResults([]);
    setError(null);
  };

  // REAL detection for single/multiple objects
  const detectObjects = async () => {
    if (!image) {
      setError('Please capture an image first!');
      return;
    }

    if (backendStatus !== 'connected') {
      setError('Backend is not connected. Please check if the server is running.');
      await checkBackendHealth();
      return;
    }

    setIsUploading(true);
    setError(null);

    try {
      console.log('Sending image to backend...');
      const response = await wasteAPI.detectWaste(image);
      const data = response.data;
      
      console.log('Backend detection response:', data);

      if (data.success) {
        // Process the real detections from YOLOv8
        const processedResults = data.detections.map((detection, index) => ({
          id: Date.now() + index,
          class: detection.class || 'unknown',
          confidence: detection.confidence ? (detection.confidence / 100) : 0.5,
          name: detection.name || (detection.class ? detection.class.charAt(0).toUpperCase() + detection.class.slice(1) : 'Unknown'),
          category: detection.category || (detection.class === 'recyclable' ? 'recyclable' : 'biodegradable'),
          timestamp: new Date().toLocaleString(),
          bbox: detection.bbox || {},
          description: detection.description || `${detection.class || 'Object'} detected with ${Math.round((detection.confidence || 50))}% confidence.`
        }));

        setPredictionResults(processedResults);
        
        // Update detection count and history
        const newDetections = processedResults.length;
        setDetectionCount(prev => prev + newDetections);
        
        const detectionDataArray = processedResults.map(obj => ({
          id: obj.id,
          name: obj.name,
          category: obj.category,
          confidence: Math.round(obj.confidence * 100),
          dustbinColor: obj.category === 'recyclable' ? 'Blue' : 
                       obj.category === 'biodegradable' ? 'Green' : 'Black',
          description: obj.description,
          timestamp: obj.timestamp
        }));

        setDetectionHistory(prev => [...detectionDataArray, ...prev.slice(0, 9 - newDetections)]);
        
        // Call parent callbacks if provided
        if (mode === 'single' && processedResults.length > 0 && onSingleDetection) {
          onSingleDetection(detectionDataArray[0]);
        } else if (mode === 'multi' && onObjectsDetected) {
          onObjectsDetected(detectionDataArray);
        }

        setError(null);
      } else {
        setError(data.error || 'Detection failed');
      }
    } catch (err) {
      console.error('Detection error:', err);
      console.error('Error details:', err.response?.data || err.message);
      setError(`Failed to process image: ${err.message}`);
    } finally {
      setIsUploading(false);
    }
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
    return colors[type?.toLowerCase()] || 'bg-gray-100 border-gray-200 text-gray-800';
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
      setError(null);
    }
  };

  // Get backend status indicator
  const getStatusIndicator = () => {
    switch (backendStatus) {
      case 'connected':
        return { text: '✅ Backend Connected', color: 'bg-green-500' };
      case 'checking':
        return { text: '🔄 Checking Backend...', color: 'bg-yellow-500' };
      case 'error':
        return { text: '❌ Backend Error', color: 'bg-red-500' };
      default:
        return { text: '❌ Backend Disconnected', color: 'bg-red-500' };
    }
  };

  const status = getStatusIndicator();

  return (
    <div className="space-y-6">
      {/* Backend Status */}
      <div className={`text-white px-4 py-3 rounded-lg ${status.color}`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <span className="font-medium">{status.text}</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-sm opacity-90">
              Port: 5001 • Model: {backendStatus === 'connected' ? 'Loaded' : 'Offline'}
            </span>
            <button 
              onClick={checkBackendHealth}
              className="text-sm bg-white bg-opacity-20 hover:bg-opacity-30 px-3 py-1 rounded transition"
            >
              Refresh
            </button>
          </div>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          <div className="flex items-center">
            <span className="mr-2">⚠️</span>
            <span>{error}</span>
          </div>
          {backendStatus === 'disconnected' && (
            <div className="mt-2 text-sm">
              Make sure your backend is running with: <code className="bg-gray-100 px-2 py-1 rounded">python app.py</code>
            </div>
          )}
        </div>
      )}

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
              onUserMediaError={(err) => setError(`Camera error: ${err.message}`)}
            />
          ) : (
            <img 
              src={image} 
              alt="Captured" 
              className="w-full h-full object-cover"
            />
          )
        ) : (
          <div className="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-gray-900 to-black">
            <div className="text-center">
              <div className="text-6xl mb-4 opacity-60">📷</div>
              <div className="text-white text-xl font-medium mb-2">Camera is OFF</div>
              {backendStatus !== 'connected' ? (
                <div className="text-white text-sm opacity-75">
                  Connect backend first to enable camera
                </div>
              ) : (
                <div className="text-white text-sm opacity-75">
                  Click "Start Camera" to begin
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Camera Controls */}
      <div className="flex flex-wrap gap-4">
        {!isCameraActive ? (
          <button
            onClick={startCamera}
            disabled={backendStatus !== 'connected'}
            className="bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold py-3 px-6 rounded-lg flex items-center space-x-3 shadow-lg transition-all"
          >
            <Camera className="h-5 w-5" />
            <span>Start Camera</span>
          </button>
        ) : (
          <>
            {!image ? (
              <button
                onClick={captureImage}
                className="bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white font-bold py-3 px-6 rounded-lg flex items-center space-x-3 flex-1 min-w-[200px] shadow-lg transition-all"
              >
                <Camera className="h-5 w-5" />
                <span>Capture Image</span>
              </button>
            ) : (
              <>
                <button
                  onClick={retakeImage}
                  className="bg-gradient-to-r from-gray-500 to-gray-600 hover:from-gray-600 hover:to-gray-700 text-white font-bold py-3 px-6 rounded-lg flex items-center space-x-3 shadow transition-all"
                >
                  <RotateCw className="h-5 w-5" />
                  <span>Retake</span>
                </button>
                <button
                  onClick={detectObjects}
                  disabled={isUploading || backendStatus !== 'connected'}
                  className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-bold py-3 px-6 rounded-lg flex items-center space-x-3 flex-1 min-w-[200px] shadow-lg transition-all disabled:opacity-50"
                >
                  {isUploading ? (
                    <>
                      <Loader2 className="h-5 w-5 animate-spin" />
                      <span>AI Processing...</span>
                    </>
                  ) : (
                    <>
                      <Upload className="h-5 w-5" />
                      <span>{mode === 'single' ? 'Detect Object' : 'Detect Objects'}</span>
                    </>
                  )}
                </button>
              </>
            )}
            <button
              onClick={stopCamera}
              className="bg-gradient-to-r from-red-500 to-pink-600 hover:from-red-600 hover:to-pink-700 text-white font-bold py-3 px-6 rounded-lg flex items-center space-x-3 shadow transition-all"
            >
              <X className="h-5 w-5" />
              <span>Stop Camera</span>
            </button>
          </>
        )}
      </div>

      {/* Results Display */}
      {predictionResults.length > 0 && (
        <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-lg">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-2xl font-bold text-gray-800 flex items-center">
                <CheckCircle className="h-7 w-7 text-green-500 mr-3" />
                AI Detection Results
              </h3>
              <p className="text-gray-600 mt-1">
                Found {predictionResults.length} object{predictionResults.length > 1 ? 's' : ''} • YOLOv8 Model
              </p>
            </div>
            <div className="px-4 py-2 bg-blue-50 text-blue-700 rounded-lg font-medium">
              Real AI Detection
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {predictionResults.map((result, index) => (
              <div key={result.id} className="p-5 border border-gray-200 rounded-xl hover:shadow-md transition">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h4 className="font-bold text-lg text-gray-800">{result.name}</h4>
                    <div className="flex items-center space-x-2 mt-1">
                      <span className={`px-3 py-1 rounded-full text-xs font-bold ${getWasteColor(result.class)}`}>
                        {result.class.toUpperCase()}
                      </span>
                      <span className="text-sm text-gray-500">{result.category}</span>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-gray-800">
                      {Math.round(result.confidence * 100)}%
                    </div>
                    <div className="text-xs text-gray-500">AI Confidence</div>
                  </div>
                </div>
                
                <div className="mt-4">
                  <div className="flex justify-between text-sm text-gray-600 mb-1">
                    <span>Confidence Level</span>
                    <span>{Math.round(result.confidence * 100)}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2.5">
                    <div 
                      className={`h-2.5 rounded-full ${
                        result.confidence > 0.7 ? 'bg-green-500' :
                        result.confidence > 0.4 ? 'bg-yellow-500' : 'bg-red-500'
                      }`}
                      style={{ width: `${result.confidence * 100}%` }}
                    ></div>
                  </div>
                </div>
                
                {result.description && (
                  <p className="mt-4 text-sm text-gray-600 bg-gray-50 p-3 rounded-lg">
                    {result.description}
                  </p>
                )}
                
                {result.bbox && (
                  <div className="mt-3 text-xs text-gray-500">
                    Bounding Box: x:{result.bbox.x?.toFixed(1)} y:{result.bbox.y?.toFixed(1)} w:{result.bbox.width?.toFixed(1)} h:{result.bbox.height?.toFixed(1)}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Data Management */}
      <div className="border-t border-gray-200 pt-8">
        <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
          <div>
            <h3 className="text-2xl font-bold text-gray-800">Detection History</h3>
            <p className="text-gray-600">Track your waste detection records</p>
          </div>
          <div className="flex flex-wrap gap-3">
            <button
              onClick={exportToCSV}
              disabled={detectionHistory.length === 0}
              className="bg-gradient-to-r from-green-500 to-teal-600 hover:from-green-600 hover:to-teal-700 text-white font-medium py-2.5 px-5 rounded-lg flex items-center space-x-2 shadow transition disabled:opacity-50"
            >
              <span>📥</span>
              <span>Export CSV</span>
            </button>
            
            <button
              onClick={clearData}
              disabled={detectionHistory.length === 0}
              className="bg-gradient-to-r from-red-500 to-rose-600 hover:from-red-600 hover:to-rose-700 text-white font-medium py-2.5 px-5 rounded-lg flex items-center space-x-2 shadow transition disabled:opacity-50"
            >
              <span>🗑️</span>
              <span>Clear Data</span>
            </button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-6 rounded-2xl border border-blue-200">
            <div className="text-4xl font-bold text-gray-800">{detectionCount}</div>
            <div className="text-blue-700 font-medium mt-2">Total Detections</div>
            <div className="text-sm text-gray-600 mt-1">Objects detected by AI</div>
          </div>
          <div className="bg-gradient-to-br from-green-50 to-green-100 p-6 rounded-2xl border border-green-200">
            <div className="text-4xl font-bold text-gray-800">
              {detectionHistory.length > 0 
                ? Math.round(detectionHistory.reduce((sum, item) => sum + item.confidence, 0) / detectionHistory.length)
                : 0}%
            </div>
            <div className="text-green-700 font-medium mt-2">Avg AI Confidence</div>
            <div className="text-sm text-gray-600 mt-1">Average detection accuracy</div>
          </div>
          <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-6 rounded-2xl border border-purple-200">
            <div className="text-4xl font-bold text-gray-800">{detectionHistory.length}</div>
            <div className="text-purple-700 font-medium mt-2">Records</div>
            <div className="text-sm text-gray-600 mt-1">Historical detection entries</div>
          </div>
        </div>

        {/* Recent Detections Table */}
        {detectionHistory.length > 0 && (
          <div className="bg-white rounded-xl border border-gray-200 p-6 shadow">
            <h4 className="text-lg font-bold text-gray-800 mb-4">Recent Detections</h4>
            <div className="overflow-x-auto rounded-lg border border-gray-100">
              <table className="min-w-full">
                <thead>
                  <tr className="bg-gray-50">
                    <th className="text-left py-4 px-6 text-gray-700 font-semibold">Time</th>
                    <th className="text-left py-4 px-6 text-gray-700 font-semibold">Object</th>
                    <th className="text-left py-4 px-6 text-gray-700 font-semibold">Category</th>
                    <th className="text-left py-4 px-6 text-gray-700 font-semibold">AI Confidence</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {detectionHistory.slice(0, 5).map((item) => (
                    <tr key={item.id} className="hover:bg-gray-50 transition">
                      <td className="py-4 px-6">
                        <div className="text-gray-700 font-medium">{item.timestamp.split(',')[1]?.trim() || item.timestamp}</div>
                      </td>
                      <td className="py-4 px-6">
                        <div className="font-semibold text-gray-800">{item.name}</div>
                      </td>
                      <td className="py-4 px-6">
                        <span className={`px-3 py-1.5 rounded-full text-sm font-medium ${
                          item.category === 'recyclable' ? 'bg-blue-100 text-blue-800 border border-blue-200' :
                          item.category === 'biodegradable' ? 'bg-green-100 text-green-800 border border-green-200' :
                          'bg-red-100 text-red-800 border border-red-200'
                        }`}>
                          {item.category}
                        </span>
                      </td>
                      <td className="py-4 px-6">
                        <div className="flex items-center">
                          <div className="w-24 bg-gray-200 rounded-full h-2.5 mr-3">
                            <div 
                              className={`h-2.5 rounded-full ${
                                item.confidence > 70 ? 'bg-green-500' :
                                item.confidence > 40 ? 'bg-yellow-500' : 'bg-red-500'
                              }`}
                              style={{ width: `${item.confidence}%` }}
                            ></div>
                          </div>
                          <span className={`font-bold ${
                            item.confidence > 70 ? 'text-green-600' :
                            item.confidence > 40 ? 'text-yellow-600' : 'text-red-600'
                          }`}>
                            {item.confidence}%
                          </span>
                        </div>
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