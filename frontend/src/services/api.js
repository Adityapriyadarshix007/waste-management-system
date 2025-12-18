import axios from 'axios'

const API = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  }
})

export const wasteAPI = {
  detectObjects: (imageFile) => {
    const formData = new FormData()
    formData.append('image', imageFile)
    return API.post('/detect-objects', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      }
    })
  },
  
  classifyWaste: (imageFile) => {
    const formData = new FormData()
    formData.append('image', imageFile)
    return API.post('/classify', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      }
    })
  },
  
  getHistory: () => API.get('/history'),
  
  getStats: () => API.get('/stats'),
  
  getDashboardStats: () => API.get('/admin/dashboard-stats'),
  
  deleteDetection: (id) => API.delete(`/admin/delete-detection/${id}`),
  
  searchDetections: (query, category) => 
    API.get('/admin/search', { params: { q: query, category } })
}

export default API