import React from 'react';

const BinVisualization = ({ detections }) => {
  if (!detections || detections.length === 0) {
    return null;
  }

  // Count items per bin category
  const binCounts = detections.reduce((acc, detection) => {
    const category = detection.category?.toLowerCase() || 'non_recyclable';
    acc[category] = (acc[category] || 0) + 1;
    return acc;
  }, {});

  // Define bin data with all 4 categories
  const binData = [
    { 
      category: 'biodegradable', 
      name: 'Green Bin', 
      icon: '🍃', 
      count: binCounts.biodegradable || 0, 
      color: '#10b981',
      description: 'Compostable organic waste'
    },
    { 
      category: 'recyclable', 
      name: 'Blue Bin', 
      icon: '♻️', 
      count: binCounts.recyclable || 0, 
      color: '#3b82f6',
      description: 'Recyclable materials'
    },
    { 
      category: 'hazardous', 
      name: 'Red Bin', 
      icon: '⚠️', 
      count: binCounts.hazardous || 0, 
      color: '#ef4444',
      description: 'Hazardous waste'
    },
    { 
      category: 'non_recyclable', 
      name: 'Black Bin', 
      icon: '🗑️', 
      count: binCounts.non_recyclable || 0, 
      color: '#374151',
      description: 'General waste'
    }
  ];

  const totalItems = detections.length;

  // Calculate percentages
  binData.forEach(bin => {
    bin.percentage = totalItems > 0 ? Math.round((bin.count / totalItems) * 100) : 0;
  });

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-lg mt-6">
      <h3 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
        <span className="mr-2">📊</span>
        Waste Distribution Analysis
      </h3>
      
      {/* Summary Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {binData.map((bin, index) => (
          <div key={index} className="text-center p-4 rounded-lg border" style={{ borderColor: bin.color }}>
            <div 
              className="w-16 h-16 rounded-full mx-auto flex items-center justify-center text-white text-2xl mb-3"
              style={{ backgroundColor: bin.color }}
            >
              {bin.icon}
            </div>
            <h4 className="font-bold text-lg mb-1">{bin.name}</h4>
            <div className="text-3xl font-bold mb-1">{bin.count}</div>
            <div className="text-sm text-gray-600">
              {bin.percentage}% of total
            </div>
          </div>
        ))}
      </div>
      
      {/* Progress Bars */}
      <div className="space-y-4">
        <h4 className="font-medium text-gray-700 text-lg mb-3">Waste Distribution by Bin</h4>
        {binData.map((bin, index) => (
          <div key={index} className="space-y-2">
            <div className="flex justify-between items-center">
              <div className="flex items-center">
                <span 
                  className="w-4 h-4 rounded mr-2"
                  style={{ backgroundColor: bin.color }}
                ></span>
                <span className="font-medium">{bin.name}</span>
                <span className="text-sm text-gray-500 ml-2">({bin.description})</span>
              </div>
              <div className="text-right">
                <span className="font-bold">{bin.count} items</span>
                <span className="text-gray-500 ml-2">({bin.percentage}%)</span>
              </div>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div 
                className="h-3 rounded-full transition-all duration-500"
                style={{ 
                  width: `${bin.percentage}%`,
                  backgroundColor: bin.color 
                }}
              ></div>
            </div>
          </div>
        ))}
      </div>
      
      {/* Recommendations */}
      <div className="mt-8 pt-6 border-t border-gray-200">
        <h4 className="font-medium text-gray-700 text-lg mb-3">🏆 Environmental Impact</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-green-50 border border-green-200 p-4 rounded-lg">
            <div className="flex items-center mb-2">
              <span className="text-green-600 mr-2">✅</span>
              <span className="font-medium text-green-800">Positive Impact</span>
            </div>
            <p className="text-sm text-green-700">
              {binCounts.recyclable || 0} items can be recycled and {binCounts.biodegradable || 0} items can be composted.
              This reduces landfill waste by {(binCounts.recyclable || 0) + (binCounts.biodegradable || 0)} items!
            </p>
          </div>
          <div className="bg-blue-50 border border-blue-200 p-4 rounded-lg">
            <div className="flex items-center mb-2">
              <span className="text-blue-600 mr-2">💡</span>
              <span className="font-medium text-blue-800">Sorting Tips</span>
            </div>
            <ul className="text-sm text-blue-700 space-y-1">
              <li>• Ensure recyclables are clean and dry</li>
              <li>• Separate hazardous waste for special disposal</li>
              <li>• Compost biodegradable items when possible</li>
              <li>• Minimize non-recyclable waste</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

// Make sure this is a default export
export default BinVisualization;