import axios from 'axios'

const API = axios.create({
  baseURL: 'http://localhost:5001',
  headers: {
    'Content-Type': 'application/json',
  }
})

export const wasteAPI = {
  // MAIN ENDPOINT - Send base64 image to /detect
  detectWaste: (base64Image) => {
    // Remove "data:image/jpeg;base64," prefix if present
    const imageData = base64Image.includes(',') 
      ? base64Image.split(',')[1] 
      : base64Image;
    
    return API.post('/detect', {
      image: imageData
    })
  },
  
  // Alternative: For file uploads (uses FormData)
  detectFromFile: (imageFile) => {
    return new Promise(async (resolve, reject) => {
      try {
        // Convert file to base64
        const base64 = await fileToBase64(imageFile);
        const imageData = base64.includes(',') 
          ? base64.split(',')[1] 
          : base64;
        
        resolve(API.post('/detect', {
          image: imageData
        }));
      } catch (error) {
        reject(error);
      }
    });
  },
  
  // Test endpoint
  testDetection: () => {
    return API.get('/test');
  },
  
  // FIXED: Health check - Returns the actual data
  checkHealth: () => {
    return API.get('/health').then(response => {
      // Return the actual data object
      return {
        status: response.data.status || 'unknown',
        model_loaded: response.data.model_loaded,
        timestamp: response.data.timestamp,
        message: 'Backend is healthy'
      };
    }).catch(error => {
      // Return error object
      return {
        status: 'error',
        message: 'Backend connection failed',
        error: error.message
      };
    });
  },
  
  // Get categories (optional - if you implement this endpoint)
  getCategories: () => {
    return API.get('/categories');
  },
  
  // Original endpoints (for compatibility - but backend might not have these)
  detectObjects: (imageFile) => {
    const formData = new FormData()
    formData.append('image', imageFile)
    return API.post('/detect_multiple', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      }
    })
  },
  
  classifyWaste: (imageFile) => {
    const formData = new FormData()
    formData.append('image', imageFile)
    return API.post('/predict', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      }
    })
  },
  
  classifyBase64: (base64Image) => {
    return API.post('/predict_base64', {
      image: base64Image
    })
  },
  
  getHistory: () => API.get('/history'),
  getStats: () => API.get('/stats'),
  getDashboardStats: () => API.get('/admin/dashboard-stats'),
  deleteDetection: (id) => API.delete(`/admin/delete-detection/${id}`),
  searchDetections: (query, category) => 
    API.get('/admin/search', { params: { q: query, category } }),
  getModelInfo: () => API.get('/model_info')
}

// Helper function to convert File to base64
const fileToBase64 = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => resolve(reader.result);
    reader.onerror = error => reject(error);
  });
}

export default API;