import React from 'react'

const ObjectDetails = ({ object }) => {
  if (!object) return null

  const getCategoryColor = (category) => {
    switch(category) {
      case 'biodegradable': return 'border-green-500 bg-green-50 text-green-800'
      case 'recyclable': return 'border-blue-500 bg-blue-50 text-blue-800'
      case 'hazardous': return 'border-red-500 bg-red-50 text-red-800'
      default: return 'border-gray-500 bg-gray-50 text-gray-800'
    }
  }

  const colorClass = getCategoryColor(object.category)

  return (
    <div className={`p-6 rounded-xl border-2 ${colorClass} shadow-lg`}>
      <h3 className="text-2xl font-bold mb-4">Object Details</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h4 className="font-semibold text-gray-700 mb-2">Identification</h4>
          <div className="space-y-3">
            <p className="text-lg font-bold">{object.name}</p>
            <p className="text-sm">Confidence: <span className="font-bold">{object.confidence}%</span></p>
            <div className="inline-block px-3 py-1 rounded-full bg-white">
              {object.category}
            </div>
          </div>
        </div>
        
        <div>
          <h4 className="font-semibold text-gray-700 mb-2">Disposal Instructions</h4>
          <div className="space-y-3">
            <p className="text-lg">
              🗑️ Dispose in <strong>{object.dustbinColor || 'Appropriate'} Bin</strong>
            </p>
            <p className="text-sm">{object.description || 'Follow proper disposal guidelines'}</p>
          </div>
        </div>
      </div>

      {object.properties && (
        <div className="mt-6 pt-6 border-t border-gray-300">
          <h4 className="font-semibold text-gray-700 mb-3">Properties</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {Object.entries(object.properties).map(([key, value]) => (
              <div key={key} className="flex justify-between p-2 bg-white/50 rounded">
                <span className="text-gray-600">{key}:</span>
                <span className="font-medium">{value}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default ObjectDetails
