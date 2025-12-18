import React from 'react'

function ObjectDetails({ object }) {
  if (!object) return null;

  return (
    <div className="p-6 bg-white rounded-xl shadow-lg border border-gray-200">
      <h3 className="text-2xl font-bold mb-4 text-gray-800">Object Details</h3>
      
      <div className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <p className="font-semibold text-gray-700">Name:</p>
            <p className="text-lg font-bold text-gray-900">{object.name}</p>
          </div>
          <div>
            <p className="font-semibold text-gray-700">Category:</p>
            <p className="text-lg font-bold text-gray-900 capitalize">{object.category}</p>
          </div>
        </div>
        
        <div>
          <p className="font-semibold text-gray-700">Confidence:</p>
          <div className="flex items-center space-x-3">
            <div className="w-full h-3 bg-gray-200 rounded-full overflow-hidden">
              <div 
                className="h-full bg-gradient-to-r from-green-400 to-blue-500 rounded-full"
                style={{ width: `${object.confidence}%` }}
              ></div>
            </div>
            <span className="font-bold text-gray-900">{object.confidence}%</span>
          </div>
        </div>
        
        {object.description && (
          <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
            <p className="font-semibold text-blue-700 mb-2">Disposal Instructions:</p>
            <p className="text-blue-800">{object.description}</p>
          </div>
        )}
        
        {object.timestamp && (
          <div className="text-sm text-gray-500">
            Detected: {object.timestamp}
          </div>
        )}
      </div>
    </div>
  )
}

export default ObjectDetails;
