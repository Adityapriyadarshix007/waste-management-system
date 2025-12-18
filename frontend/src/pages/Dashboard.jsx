import React, { useState, useEffect } from 'react'
import CameraSection from '../components/CameraSection'
import DetectionDetails from '../components/DetectionDetails'
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
      <header className="dashboard-header sticky top-0 z-50 rounded-b-3xl px-8 py-4 mb-8">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="relative">
              <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-blue-500 rounded-2xl flex items-center justify-center shadow-2xl recycling-symbol float-animation">
                <span className="text-3xl text-white">♻️</span>
              </div>
              <div className="absolute -inset-4 bg-green-500/20 rounded-3xl blur-xl -z-10"></div>
            </div>
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-green-600 via-blue-600 to-purple-600 bg-clip-text text-transparent">
                EcoVision AI
              </h1>
              <p className="text-gray-600 dark:text-gray-400">
                Intelligent Waste Management & Classification System
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="relative group">
              <div className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-green-100 to-blue-100 rounded-full">
                <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                <span className="font-semibold text-green-700">Live Detection Active</span>
              </div>
              <div className="absolute left-0 mt-2 w-64 p-3 bg-white shadow-2xl rounded-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300 z-50">
                <p className="text-sm text-gray-600">AI is actively analyzing camera feed for waste objects</p>
              </div>
            </div>
            
            <button className="btn-primary flex items-center space-x-2">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              <span>Export Report</span>
            </button>
          </div>
        </div>
      </header>

      <main className="px-8 pb-12">
        <div className="dashboard-grid">
          {/* Camera Section Card */}
          <div className="dashboard-card col-span-2">
            <div className="card-header">
              <h3>
                <span className="card-header-icon">📷</span>
                Live Object Detection
                <span className="ml-3 text-sm px-3 py-1 bg-red-500 text-white rounded-full animate-pulse">
                  LIVE
                </span>
              </h3>
            </div>
            <div className="card-body">
              <CameraSection onDetection={handleDetection} />
            </div>
          </div>

          {/* Stats Cards */}
          <div className="dashboard-card">
            <div className="card-header">
              <h3>
                <span className="card-header-icon">📊</span>
                System Statistics
              </h3>
            </div>
            <div className="card-body">
              <StatsCards stats={stats} />
            </div>
          </div>

          {/* Detection Details */}
          {activeDetection && (
            <div className="dashboard-card col-span-2 animate-fade-in">
              <div className="card-header">
                <h3>
                  <span className="card-header-icon">🔍</span>
                  Object Analysis Report
                  <span className="ml-4 text-sm px-3 py-1 bg-green-500 text-white rounded-full">
                    #{activeDetection.id.toString().slice(-6)}
                  </span>
                </h3>
              </div>
              <div className="card-body">
                <DetectionDetails detection={activeDetection} />
              </div>
            </div>
          )}

          {/* Analytics Chart */}
          <div className="dashboard-card">
            <div className="card-header">
              <h3>
                <span className="card-header-icon">📈</span>
                Waste Distribution
              </h3>
            </div>
            <div className="card-body">
              <AnalyticsChart data={stats.categories} />
            </div>
          </div>

          {/* Waste Categories */}
          <div className="dashboard-card col-span-2">
            <div className="card-header">
              <h3>
                <span className="card-header-icon">🗂️</span>
                Waste Classification Guide
              </h3>
            </div>
            <div className="card-body">
              <div className="waste-categories-grid">
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
                Recent Detections
              </h3>
            </div>
            <div className="card-body">
              <div className="recent-detections-list">
                {recentDetections.map(detection => (
                  <div 
                    key={detection.id}
                    className={`detection-item category-${detection.color}`}
                  >
                    <div className={`detection-icon bg-${detection.color}-500`}>
                      {detection.color === 'green' ? '🌿' : 
                       detection.color === 'blue' ? '♻️' : 
                       detection.color === 'red' ? '⚠️' : '🚫'}
                    </div>
                    <div className="detection-info">
                      <div className="detection-name">{detection.name}</div>
                      <div className="detection-meta">
                        <span className={`badge-${detection.color}`}>
                          {detection.category}
                        </span>
                        <span className="text-gray-500">{detection.confidence}%</span>
                      </div>
                    </div>
                    <div className="detection-time">{detection.time}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Environmental Impact */}
          <div className="dashboard-card">
            <div className="card-header">
              <h3>
                <span className="card-header-icon">🌍</span>
                Environmental Impact
              </h3>
            </div>
            <div className="card-body">
              <div className="environmental-impact">
                <div className="impact-metrics">
                  <div className="impact-metric">
                    <div className="impact-value">{stats.carbonSaved}</div>
                    <div className="impact-label">Carbon Saved</div>
                  </div>
                  <div className="impact-metric">
                    <div className="impact-value">62%</div>
                    <div className="impact-label">Landfill Reduced</div>
                  </div>
                  <div className="impact-metric">
                    <div className="impact-value">8.4</div>
                    <div className="impact-label">Eco Score</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Dustbin Status */}
          <div className="dashboard-card col-span-2">
            <div className="card-header">
              <h3>
                <span className="card-header-icon">🗑️</span>
                Smart Dustbin Status
              </h3>
            </div>
            <div className="card-body">
              <div className="dustbin-status-grid">
                <div className="dustbin-card green">
                  <div className="dustbin-icon green">
                    <span>🌿</span>
                  </div>
                  <div className="dustbin-name">Green Bin</div>
                  <div className="dustbin-type">Biodegradable Waste</div>
                  <div className="progress-bar-custom">
                    <div className="progress-fill-custom green" style={{ width: '65%' }}></div>
                  </div>
                  <div className="text-sm text-gray-500">65% Full</div>
                </div>

                <div className="dustbin-card blue">
                  <div className="dustbin-icon blue">
                    <span>♻️</span>
                  </div>
                  <div className="dustbin-name">Blue Bin</div>
                  <div className="dustbin-type">Recyclable Waste</div>
                  <div className="progress-bar-custom">
                    <div className="progress-fill-custom blue" style={{ width: '82%' }}></div>
                  </div>
                  <div className="text-sm text-gray-500">82% Full</div>
                </div>

                <div className="dustbin-card red">
                  <div className="dustbin-icon red">
                    <span>⚠️</span>
                  </div>
                  <div className="dustbin-name">Red Bin</div>
                  <div className="dustbin-type">Hazardous Waste</div>
                  <div className="progress-bar-custom">
                    <div className="progress-fill-custom red" style={{ width: '28%' }}></div>
                  </div>
                  <div className="text-sm text-gray-500">28% Full</div>
                </div>

                <div className="dustbin-card gray">
                  <div className="dustbin-icon gray">
                    <span>🚫</span>
                  </div>
                  <div className="dustbin-name">Black Bin</div>
                  <div className="dustbin-type">Non-Recyclable</div>
                  <div className="progress-bar-custom">
                    <div className="progress-fill-custom gray" style={{ width: '45%' }}></div>
                  </div>
                  <div className="text-sm text-gray-500">45% Full</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <footer className="dashboard-footer">
          <div className="flex items-center justify-center space-x-4 mb-4">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span className="text-gray-600 font-medium">AI System Active • Processing in Real-time</span>
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
          </div>
          <p className="footer-text">
            <strong>EcoVision AI Waste Management System v2.0</strong> • 
            Powered by TensorFlow, React & Computer Vision • 
            Reducing Environmental Impact Since 2024
          </p>
          <p className="text-sm text-gray-400 mt-2">
            📍 Smart Cities Initiative • ♻️ Saving the Planet One Detection at a Time
          </p>
        </footer>
      </main>
    </div>
  )
}

export default Dashboard
