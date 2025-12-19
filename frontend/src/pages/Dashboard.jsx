import React, { useState } from 'react'
import CameraSection from '../components/CameraSection'
import DetectionDetails from '../components/ObjectDetails'
import StatsCards from '../components/StatsCards'
import WasteCategoryCard from '../components/WasteCategoryCard'
import AnalyticsChart from '../components/AnalyticsChart'
import '../styles/dashboard.css'

const Dashboard = () => {
  const [detections, setDetections] = useState([])
  const [activeDetection, setActiveDetection] = useState(null)
  const [stats, setStats] = useState({
    totalDetections: 1247,
    accuracy: 94.2,
    recycledToday: '347kg',
    carbonSaved: '245kg',
    categories: {
      biodegradable: 35,
      recyclable: 45,
      hazardous: 12,
      nonRecyclable: 8
    }
  })

  const handleDetection = (detection) => {
    setActiveDetection(detection)
    setDetections(prev => [detection, ...prev.slice(0, 9)])
    
    // Update stats
    setStats(prev => ({
      ...prev,
      totalDetections: prev.totalDetections + 1,
      categories: {
        ...prev.categories,
        [detection.category]: (prev.categories[detection.category] || 0) + 1
      }
    }))
  }

  const wasteCategories = [
    {
      id: 1,
      name: 'Biodegradable',
      color: 'green',
      icon: '🌿',
      examples: ['Food waste', 'Paper', 'Yard trimmings', 'Wood'],
      dustbin: 'Green',
      decomposition: '2 weeks - 5 years',
      impact: 'Low (Produces compost)'
    },
    {
      id: 2,
      name: 'Recyclable',
      color: 'blue',
      icon: '♻️',
      examples: ['Plastic bottles', 'Glass', 'Metal cans', 'Cardboard'],
      dustbin: 'Blue',
      decomposition: '50 - 1000 years',
      impact: 'Medium (Saves resources)'
    },
    {
      id: 3,
      name: 'Hazardous',
      color: 'red',
      icon: '⚠️',
      examples: ['Batteries', 'Chemicals', 'Electronics', 'Medicines'],
      dustbin: 'Red',
      decomposition: '100+ years',
      impact: 'High (Toxic to environment)'
    },
    {
      id: 4,
      name: 'Non-Recyclable',
      color: 'gray',
      icon: '🚫',
      examples: ['Plastic bags', 'Ceramics', 'Composite materials', 'Styrofoam'],
      dustbin: 'Black',
      decomposition: '500+ years',
      impact: 'High (Landfill waste)'
    }
  ]

  const recentDetections = [
    { id: 1, name: 'Plastic Bottle', category: 'recyclable', confidence: 92, time: '2 min ago', color: 'blue' },
    { id: 2, name: 'Banana Peel', category: 'biodegradable', confidence: 98, time: '5 min ago', color: 'green' },
    { id: 3, name: 'Battery', category: 'hazardous', confidence: 95, time: '10 min ago', color: 'red' },
    { id: 4, name: 'Pizza Box', category: 'biodegradable', confidence: 87, time: '15 min ago', color: 'green' },
    { id: 5, name: 'Glass Jar', category: 'recyclable', confidence: 96, time: '20 min ago', color: 'blue' }
  ]

  return (
    <div className="dashboard-layout">
      {/* Navigation Header */}
      <header className="dashboard-header sticky top-0 z-50 rounded-b-3xl px-4 md:px-8 py-4 mb-6 md:mb-8">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 md:gap-0">
          <div className="flex items-center space-x-4">
            <div className="relative">
              <div className="w-12 h-12 md:w-16 md:h-16 bg-gradient-to-br from-green-500 to-blue-500 rounded-2xl flex items-center justify-center shadow-2xl recycling-symbol float-animation">
                <span className="text-2xl md:text-3xl text-white">♻️</span>
              </div>
              <div className="absolute -inset-3 md:-inset-4 bg-green-500/20 rounded-3xl blur-xl -z-10"></div>
            </div>
            <div>
              <h1 className="text-2xl md:text-4xl font-bold bg-gradient-to-r from-green-600 via-blue-600 to-purple-600 bg-clip-text text-transparent">
                EcoVision AI
              </h1>
              <p className="text-sm md:text-base text-gray-600 dark:text-gray-400">
                Intelligent Waste Management System
              </p>
            </div>
          </div>
          
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3 md:gap-4">
            <div className="relative group">
              <div className="flex items-center space-x-2 px-3 py-1.5 md:px-4 md:py-2 bg-gradient-to-r from-green-100 to-blue-100 rounded-full">
                <div className="w-2 h-2 md:w-3 md:h-3 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-xs md:text-sm font-semibold text-green-700">Live Detection</span>
              </div>
              <div className="absolute left-0 mt-2 w-56 p-3 bg-white shadow-2xl rounded-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300 z-50">
                <p className="text-sm text-gray-600">AI is actively analyzing camera feed</p>
              </div>
            </div>
            
            <button className="btn-primary flex items-center space-x-2 text-sm md:text-base">
              <svg className="w-4 h-4 md:w-5 md:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              <span>Export Report</span>
            </button>
          </div>
        </div>
      </header>

      <main className="px-4 md:px-8 pb-8 md:pb-12">
        {/* First Row: Camera + Stats - REDUCED HEIGHTS */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 md:gap-6 mb-4 md:mb-6">
          {/* Camera Section */}
          <div className="lg:col-span-2 dashboard-card">
            <div className="card-header">
              <h3>
                <span className="card-header-icon">📷</span>
                Live Object Detection
                <span className="ml-2 md:ml-3 text-xs md:text-sm px-2 py-0.5 md:px-3 md:py-1 bg-red-500 text-white rounded-full animate-pulse">
                  LIVE
                </span>
              </h3>
            </div>
            <div className="card-body h-[300px] md:h-[350px] overflow-auto">
              <CameraSection onDetection={handleDetection} />
            </div>
          </div>

          {/* Stats Section */}
          <div className="dashboard-card">
            <div className="card-header">
              <h3>
                <span className="card-header-icon">📊</span>
                System Statistics
              </h3>
            </div>
            <div className="card-body h-[300px] md:h-[350px] overflow-auto">
              <StatsCards stats={stats} />
            </div>
          </div>
        </div>

        {/* Second Row: Detection Details + Analytics - REDUCED HEIGHTS */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 md:gap-6 mb-4 md:mb-6">
          {/* Detection Details */}
          {activeDetection && (
            <div className="lg:col-span-2 dashboard-card animate-fade-in">
              <div className="card-header">
                <h3>
                  <span className="card-header-icon">🔍</span>
                  Object Analysis Report
                  <span className="ml-2 md:ml-4 text-xs md:text-sm px-2 py-0.5 md:px-3 md:py-1 bg-green-500 text-white rounded-full">
                    #{activeDetection.id?.toString()?.slice(-6) || 'N/A'}
                  </span>
                </h3>
              </div>
              <div className="card-body h-[250px] md:h-[300px] overflow-auto p-0">
                <div className="h-full">
                  <DetectionDetails detection={activeDetection} />
                </div>
              </div>
            </div>
          )}

          {/* Analytics Chart */}
          <div className={`dashboard-card ${!activeDetection ? 'lg:col-span-3' : ''}`}>
            <div className="card-header">
              <h3>
                <span className="card-header-icon">📈</span>
                Waste Distribution
              </h3>
            </div>
            <div className="card-body h-[250px] md:h-[300px] overflow-hidden">
              <div className="h-full">
                <AnalyticsChart data={stats.categories} />
              </div>
            </div>
          </div>
        </div>

        {/* Third Row: Waste Categories + Recent Detections - REDUCED HEIGHTS */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 md:gap-6 mb-4 md:mb-6">
          {/* Waste Categories */}
          <div className="lg:col-span-2 dashboard-card">
            <div className="card-header">
              <h3>
                <span className="card-header-icon">🗂️</span>
                Waste Classification Guide
              </h3>
            </div>
            <div className="card-body h-[350px] md:h-[400px] overflow-auto p-3 md:p-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {wasteCategories.map(category => (
                  <WasteCategoryCard key={category.id} category={category} />
                ))}
              </div>
            </div>
          </div>

          {/* Recent Detections */}
          <div className="dashboard-card">
            <div className="card-header">
              <h3>
                <span className="card-header-icon">🕒</span>
                Recent Activity
              </h3>
            </div>
            <div className="card-body h-[350px] md:h-[400px] p-0">
              <div className="h-full overflow-y-auto px-3 md:px-4">
                <div className="space-y-2 py-2">
                  {recentDetections.map(detection => (
                    <div 
                      key={detection.id}
                      className="flex items-center p-2 md:p-3 bg-gradient-to-r from-gray-50 to-white rounded-lg hover:shadow-md transition-shadow border border-gray-100"
                    >
                      <div className={`w-8 h-8 md:w-10 md:h-10 rounded-full flex items-center justify-center mr-2 md:mr-3 flex-shrink-0 ${
                        detection.color === 'green' ? 'bg-green-100 text-green-600' :
                        detection.color === 'blue' ? 'bg-blue-100 text-blue-600' :
                        detection.color === 'red' ? 'bg-red-100 text-red-600' :
                        'bg-gray-100 text-gray-600'
                      }`}>
                        {detection.color === 'green' ? '🌿' : 
                         detection.color === 'blue' ? '♻️' : 
                         detection.color === 'red' ? '⚠️' : '🚫'}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="font-medium text-sm md:text-base text-gray-800 truncate">{detection.name}</div>
                        <div className="flex items-center text-xs md:text-sm space-x-1 md:space-x-2">
                          <span className={`px-1.5 py-0.5 md:px-2 md:py-0.5 rounded-full whitespace-nowrap ${
                            detection.color === 'green' ? 'bg-green-100 text-green-700' :
                            detection.color === 'blue' ? 'bg-blue-100 text-blue-700' :
                            detection.color === 'red' ? 'bg-red-100 text-red-700' :
                            'bg-gray-100 text-gray-700'
                          }`}>
                            {detection.category}
                          </span>
                          <span className="text-gray-500 whitespace-nowrap">{detection.confidence}%</span>
                        </div>
                      </div>
                      <div className="text-xs text-gray-500 whitespace-nowrap flex-shrink-0 ml-1 md:ml-2">
                        {detection.time}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Fourth Row: Environmental Impact + Dustbin Status - REDUCED HEIGHTS */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-4 md:gap-6 mb-4 md:mb-6">
          {/* Environmental Impact */}
          <div className="dashboard-card">
            <div className="card-header">
              <h3>
                <span className="card-header-icon">🌍</span>
                Environmental Impact
              </h3>
            </div>
            <div className="card-body h-[180px] md:h-[220px]">
              <div className="h-full flex flex-col justify-center">
                <div className="grid grid-cols-3 gap-3 md:gap-4">
                  <div className="text-center p-3 md:p-4 bg-gradient-to-br from-green-50 to-emerald-100 rounded-xl">
                    <div className="text-xl md:text-2xl font-bold text-green-700">{stats.carbonSaved}</div>
                    <div className="text-xs md:text-sm text-green-600 mt-1">Carbon Saved</div>
                  </div>
                  <div className="text-center p-3 md:p-4 bg-gradient-to-br from-blue-50 to-cyan-100 rounded-xl">
                    <div className="text-xl md:text-2xl font-bold text-blue-700">62%</div>
                    <div className="text-xs md:text-sm text-blue-600 mt-1">Landfill Reduced</div>
                  </div>
                  <div className="text-center p-3 md:p-4 bg-gradient-to-br from-purple-50 to-violet-100 rounded-xl">
                    <div className="text-xl md:text-2xl font-bold text-purple-700">8.4</div>
                    <div className="text-xs md:text-sm text-purple-600 mt-1">Eco Score</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Dustbin Status */}
          <div className="lg:col-span-3 dashboard-card">
            <div className="card-header">
              <h3>
                <span className="card-header-icon">🗑️</span>
                Smart Dustbin Status
              </h3>
            </div>
            <div className="card-body h-[180px] md:h-[220px] overflow-auto">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4 h-full">
                {[
                  { color: 'green', name: 'Green Bin', type: 'Biodegradable', fill: 65, icon: '🌿' },
                  { color: 'blue', name: 'Blue Bin', type: 'Recyclable', fill: 82, icon: '♻️' },
                  { color: 'red', name: 'Red Bin', type: 'Hazardous', fill: 28, icon: '⚠️' },
                  { color: 'gray', name: 'Black Bin', type: 'Non-Recyclable', fill: 45, icon: '🚫' }
                ].map((bin, index) => (
                  <div key={index} className="flex flex-col items-center p-3 md:p-4 bg-gradient-to-b from-white to-gray-50 rounded-xl hover:shadow-lg transition-shadow">
                    <div className={`w-12 h-12 md:w-16 md:h-16 rounded-full flex items-center justify-center mb-2 md:mb-3 ${
                      bin.color === 'green' ? 'bg-green-100' :
                      bin.color === 'blue' ? 'bg-blue-100' :
                      bin.color === 'red' ? 'bg-red-100' :
                      'bg-gray-100'
                    }`}>
                      <span className="text-xl md:text-2xl">{bin.icon}</span>
                    </div>
                    <div className="font-semibold text-sm md:text-base text-gray-800 text-center">{bin.name}</div>
                    <div className="text-xs md:text-sm text-gray-600 text-center mb-2 md:mb-3">{bin.type}</div>
                    <div className="w-full bg-gray-200 rounded-full h-1.5 md:h-2 mb-1.5 md:mb-2">
                      <div 
                        className={`h-1.5 md:h-2 rounded-full ${
                          bin.color === 'green' ? 'bg-green-500' :
                          bin.color === 'blue' ? 'bg-blue-500' :
                          bin.color === 'red' ? 'bg-red-500' :
                          'bg-gray-500'
                        }`}
                        style={{ width: `${bin.fill}%` }}
                      ></div>
                    </div>
                    <div className="text-xs md:text-sm font-medium text-gray-700">{bin.fill}% Full</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <footer className="mt-6 md:mt-8 pt-4 md:pt-6 border-t border-gray-200">
          <div className="flex items-center justify-center space-x-2 md:space-x-4 mb-3 md:mb-4">
            <div className="w-1.5 h-1.5 md:w-2 md:h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span className="text-xs md:text-sm text-gray-600 font-medium">AI System Active • Real-time Processing</span>
            <div className="w-1.5 h-1.5 md:w-2 md:h-2 bg-green-500 rounded-full animate-pulse"></div>
          </div>
          <p className="text-center text-xs md:text-sm text-gray-600 mb-2">
            <strong>EcoVision AI Waste Management System v2.0</strong> • 
            Powered by TensorFlow, React & Computer Vision
          </p>
          <p className="text-center text-xs text-gray-400">
            📍 Smart Cities Initiative • ♻️ Saving the Planet One Detection at a Time
          </p>
        </footer>
      </main>
    </div>
  )
}

export default Dashboard