import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from '@/api/axios'

export interface User {
  id: number
  username: string
  full_name: string
  role: string // Support both uppercase and lowercase from backend
  telegram_user_id: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: User
}

export const useAuthStore = defineStore('auth', () => {
  // State
  const token = ref<string | null>(localStorage.getItem('access_token'))
  const user = ref<User | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Computed
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const isAdmin = computed(() => user.value?.role?.toLowerCase() === 'admin')
  const isReception = computed(() => user.value?.role?.toLowerCase() === 'reception')
  const isHousekeeping = computed(() => user.value?.role?.toLowerCase() === 'housekeeping')
  const isMaintenance = computed(() => user.value?.role?.toLowerCase() === 'maintenance')

  // Actions
  async function login(credentials: LoginRequest): Promise<void> {
    try {
      isLoading.value = true
      error.value = null

      const response = await axios.post<LoginResponse>(
        '/api/v1/auth/login',
        credentials
      )

      const { access_token, user: userData } = response.data

      // Save token
      token.value = access_token
      localStorage.setItem('access_token', access_token)

      // Save user
      user.value = userData
      localStorage.setItem('user', JSON.stringify(userData))
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'เข้าสู่ระบบไม่สำเร็จ'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function logout(): Promise<void> {
    try {
      isLoading.value = true
      error.value = null

      // Call logout endpoint
      await axios.post('/api/v1/auth/logout')
    } catch (err: any) {
      // Even if logout fails, clear local state
      console.error('Logout error:', err)
    } finally {
      // Clear state
      token.value = null
      user.value = null
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
      isLoading.value = false
    }
  }

  async function fetchCurrentUser(): Promise<void> {
    try {
      isLoading.value = true
      error.value = null

      const response = await axios.get<User>('/api/v1/auth/me')
      user.value = response.data
      localStorage.setItem('user', JSON.stringify(response.data))
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'ไม่สามารถโหลดข้อมูลผู้ใช้ได้'
      // If unauthorized, clear auth state
      if (err.response?.status === 401) {
        await logout()
      }
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function initAuth(): Promise<void> {
    // Try to restore user from localStorage
    const savedUser = localStorage.getItem('user')
    if (savedUser && token.value) {
      try {
        user.value = JSON.parse(savedUser)
        // Verify token is still valid by fetching current user
        await fetchCurrentUser()
      } catch (err) {
        // If verification fails, clear auth state
        await logout()
      }
    }
  }

  function hasRole(roles: string[]): boolean {
    if (!user.value) return false
    // Check both lowercase and uppercase versions
    const userRole = user.value.role.toLowerCase()
    const normalizedRoles = roles.map(r => r.toLowerCase())
    return normalizedRoles.includes(userRole)
  }

  function clearError(): void {
    error.value = null
  }

  return {
    // State
    token,
    user,
    isLoading,
    error,
    // Computed
    isAuthenticated,
    isAdmin,
    isReception,
    isHousekeeping,
    isMaintenance,
    // Actions
    login,
    logout,
    fetchCurrentUser,
    initAuth,
    hasRole,
    clearError,
  }
})
