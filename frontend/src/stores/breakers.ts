/**
 * Breakers Store
 * Manages breaker devices and activity logs
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  Breaker,
  BreakerFormData,
  BreakerActivityLog,
  BreakerActivityLogFilter,
  BreakerStatistics,
  BreakerState
} from '@/types/homeAssistant'
import { breakersApi } from '@/api/homeAssistant'

export const useBreakersStore = defineStore('breakers', () => {
  // State
  const breakers = ref<Breaker[]>([])
  const currentBreaker = ref<Breaker | null>(null)
  const activityLogs = ref<BreakerActivityLog[]>([])
  const statistics = ref<BreakerStatistics | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const breakersOnline = computed(() =>
    breakers.value.filter(b => b.is_available && b.is_active)
  )

  const breakersOff = computed(() =>
    breakers.value.filter(b => b.current_state === 'OFF' && b.is_available)
  )

  const breakersOn = computed(() =>
    breakers.value.filter(b => b.current_state === 'ON' && b.is_available)
  )

  const breakersWithErrors = computed(() =>
    breakers.value.filter(b => b.consecutive_errors >= 3)
  )

  const breakersByRoom = computed(() => {
    const map = new Map<number, Breaker>()
    breakers.value.forEach(breaker => {
      if (breaker.room_id) {
        map.set(breaker.room_id, breaker)
      }
    })
    return map
  })

  // Helper function to handle errors
  const handleError = (err: any, defaultMessage: string) => {
    error.value = err.response?.data?.detail || defaultMessage
    console.error('Breakers Store error:', err)
    throw err
  }

  // Actions

  /**
   * Fetch all breakers
   */
  const fetchBreakers = async (params?: {
    room_id?: number
    auto_control_enabled?: boolean
    current_state?: BreakerState
    is_active?: boolean
    silent?: boolean
  }) => {
    const silent = params?.silent || false
    if (!silent) {
      isLoading.value = true
    }
    error.value = null
    try {
      const response = await breakersApi.getAll(params)
      breakers.value = response.data.breakers
      return response.data
    } catch (err: any) {
      if (!silent) {
        handleError(err, 'เกิดข้อผิดพลาดในการดึงข้อมูล breakers')
      } else {
        console.error('Silent fetch error:', err)
      }
    } finally {
      if (!silent) {
        isLoading.value = false
      }
    }
  }

  /**
   * Fetch breaker by ID
   */
  const fetchBreakerById = async (id: number) => {
    isLoading.value = true
    error.value = null
    try {
      const response = await breakersApi.getById(id)
      currentBreaker.value = response.data
      return response.data
    } catch (err: any) {
      handleError(err, 'เกิดข้อผิดพลาดในการดึงข้อมูล breaker')
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Create new breaker
   */
  const createBreaker = async (data: BreakerFormData) => {
    isLoading.value = true
    error.value = null
    try {
      const response = await breakersApi.create(data)
      breakers.value.push(response.data)
      return response.data
    } catch (err: any) {
      handleError(err, 'เกิดข้อผิดพลาดในการสร้าง breaker')
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Update breaker
   */
  const updateBreaker = async (id: number, data: Partial<BreakerFormData>) => {
    isLoading.value = true
    error.value = null
    try {
      const response = await breakersApi.update(id, data)
      const index = breakers.value.findIndex(b => b.id === id)
      if (index !== -1) {
        breakers.value[index] = response.data
      }
      if (currentBreaker.value?.id === id) {
        currentBreaker.value = response.data
      }
      return response.data
    } catch (err: any) {
      handleError(err, 'เกิดข้อผิดพลาดในการอัปเดต breaker')
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Delete breaker
   */
  const deleteBreaker = async (id: number) => {
    isLoading.value = true
    error.value = null
    try {
      await breakersApi.delete(id)
      breakers.value = breakers.value.filter(b => b.id !== id)
      if (currentBreaker.value?.id === id) {
        currentBreaker.value = null
      }
    } catch (err: any) {
      handleError(err, 'เกิดข้อผิดพลาดในการลบ breaker')
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Turn on breaker
   */
  const turnOn = async (id: number, reason?: string) => {
    error.value = null
    try {
      const response = await breakersApi.turnOn(id, reason)
      // Update local state
      const breaker = breakers.value.find(b => b.id === id)
      if (breaker) {
        breaker.current_state = response.data.new_state
      }
      if (currentBreaker.value?.id === id) {
        currentBreaker.value.current_state = response.data.new_state
      }
      return response.data
    } catch (err: any) {
      handleError(err, 'เกิดข้อผิดพลาดในการเปิด breaker')
    }
  }

  /**
   * Turn off breaker
   */
  const turnOff = async (id: number, reason?: string) => {
    error.value = null
    try {
      const response = await breakersApi.turnOff(id, reason)
      // Update local state
      const breaker = breakers.value.find(b => b.id === id)
      if (breaker) {
        breaker.current_state = response.data.new_state
      }
      if (currentBreaker.value?.id === id) {
        currentBreaker.value.current_state = response.data.new_state
      }
      return response.data
    } catch (err: any) {
      handleError(err, 'เกิดข้อผิดพลาดในการปิด breaker')
    }
  }

  /**
   * Sync breaker status
   */
  const syncStatus = async (id: number) => {
    error.value = null
    try {
      const response = await breakersApi.syncStatus(id)
      // Update local state with all synced fields
      const breaker = breakers.value.find(b => b.id === id)
      if (breaker) {
        breaker.current_state = response.data.current_state
        breaker.is_available = response.data.is_available
        breaker.last_state_update = response.data.synced_at
        breaker.consecutive_errors = response.data.consecutive_errors
        breaker.last_error_message = response.data.last_error_message
      }
      if (currentBreaker.value?.id === id) {
        currentBreaker.value.current_state = response.data.current_state
        currentBreaker.value.is_available = response.data.is_available
        currentBreaker.value.last_state_update = response.data.synced_at
        currentBreaker.value.consecutive_errors = response.data.consecutive_errors
        currentBreaker.value.last_error_message = response.data.last_error_message
      }
      return response.data
    } catch (err: any) {
      handleError(err, 'เกิดข้อผิดพลาดในการซิงค์สถานะ breaker')
    }
  }

  /**
   * Sync all breakers
   */
  const syncAll = async (silent: boolean = false) => {
    if (!silent) {
      isLoading.value = true
    }
    error.value = null
    try {
      const response = await breakersApi.syncAll()
      // Refresh all breakers after sync
      await fetchBreakers({ silent })
      return response.data
    } catch (err: any) {
      if (!silent) {
        handleError(err, 'เกิดข้อผิดพลาดในการซิงค์ breakers ทั้งหมด')
      } else {
        console.error('Silent sync error:', err)
      }
    } finally {
      if (!silent) {
        isLoading.value = false
      }
    }
  }

  /**
   * Fetch activity logs
   */
  const fetchLogs = async (breakerId?: number, filter?: BreakerActivityLogFilter) => {
    isLoading.value = true
    error.value = null
    try {
      let response
      if (breakerId) {
        response = await breakersApi.getLogs(breakerId, filter)
      } else {
        response = await breakersApi.getAllLogs(filter)
      }
      activityLogs.value = response.data.logs
      return response.data
    } catch (err: any) {
      handleError(err, 'เกิดข้อผิดพลาดในการดึง activity logs')
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Fetch statistics
   */
  const fetchStatistics = async () => {
    error.value = null
    try {
      const response = await breakersApi.getStatistics()
      statistics.value = response.data
      return response.data
    } catch (err: any) {
      handleError(err, 'เกิดข้อผิดพลาดในการดึงสถิติ')
    }
  }

  /**
   * Get breaker by room ID
   */
  const getBreakerByRoomId = (roomId: number): Breaker | undefined => {
    return breakersByRoom.value.get(roomId)
  }

  /**
   * Clear error
   */
  const clearError = () => {
    error.value = null
  }

  return {
    // State
    breakers,
    currentBreaker,
    activityLogs,
    statistics,
    isLoading,
    error,

    // Getters
    breakersOnline,
    breakersOff,
    breakersOn,
    breakersWithErrors,
    breakersByRoom,

    // Actions
    fetchBreakers,
    fetchBreakerById,
    createBreaker,
    updateBreaker,
    deleteBreaker,
    turnOn,
    turnOff,
    syncStatus,
    syncAll,
    fetchLogs,
    fetchStatistics,
    getBreakerByRoomId,
    clearError
  }
})
