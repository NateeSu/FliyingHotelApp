import axios from 'axios'
import router from '@/router'
import { useAuthStore } from '@/stores/auth'

// Create axios instance
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor - Add auth token to all requests
apiClient.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    const token = authStore.token || localStorage.getItem('access_token')

    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    // If the data is FormData, remove Content-Type header
    // Browser will set it automatically with the correct boundary
    if (config.data instanceof FormData) {
      delete config.headers['Content-Type']
    }

    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor - Handle errors globally
apiClient.interceptors.response.use(
  (response) => {
    return response
  },
  async (error) => {
    if (error.response?.status === 401) {
      // Unauthorized - clear auth and redirect to login
      const authStore = useAuthStore()
      await authStore.logout()
      router.push('/login')
    }

    return Promise.reject(error)
  }
)

export default apiClient
