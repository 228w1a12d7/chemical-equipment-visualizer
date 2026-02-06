import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Token ${token}`;
  }
  return config;
});

// Handle unauthorized responses
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Don't redirect on auth endpoints - let them handle their own errors
    const url = error.config?.url || '';
    const isAuthEndpoint = url.includes('/auth/');
    
    // Only redirect for 401 on protected endpoints, NOT on login/register
    if (error.response?.status === 401 && !isAuthEndpoint) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  register: (data) => api.post('/auth/register/', data),
  login: (data) => api.post('/auth/login/', data),
  logout: () => api.post('/auth/logout/'),
  getCurrentUser: () => api.get('/auth/user/'),
};

// Data API
export const dataAPI = {
  uploadCSV: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/upload/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  getHistory: () => api.get('/datasets/'),
  getDataset: (id) => api.get(`/datasets/${id}/`),
  deleteDataset: (id) => api.delete(`/datasets/${id}/delete/`),
  downloadPDF: (id) => api.get(`/datasets/${id}/pdf/`, { responseType: 'blob' }),
  downloadCSV: (id) => api.get(`/datasets/${id}/csv/`, { responseType: 'blob' }),
  
  // Equipment CRUD operations
  getEquipmentList: (datasetId, filters = {}) => {
    const params = new URLSearchParams();
    if (filters.startDate) params.append('start_date', filters.startDate);
    if (filters.endDate) params.append('end_date', filters.endDate);
    return api.get(`/datasets/${datasetId}/equipment/?${params.toString()}`);
  },
  addEquipment: (datasetId, equipmentData) => 
    api.post(`/datasets/${datasetId}/equipment/add/`, equipmentData),
  updateEquipment: (datasetId, equipmentId, equipmentData) => 
    api.put(`/datasets/${datasetId}/equipment/${equipmentId}/`, equipmentData),
  deleteEquipment: (datasetId, equipmentId) => 
    api.delete(`/datasets/${datasetId}/equipment/${equipmentId}/`),
};

export default api;
