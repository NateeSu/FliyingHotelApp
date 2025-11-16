/**
 * Home Assistant Store
 * Manages Home Assistant configuration and status
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  HomeAssistantConfig,
  HomeAssistantConfigForm,
  HomeAssistantTestConnectionRequest,
  HomeAssistantTestConnectionResponse,
  HomeAssistantStatus,
  HomeAssistantEntity
} from '@/types/homeAssistant'
import { homeAssistantApi } from '@/api/homeAssistant'

export const useHomeAssistantStore = defineStore('homeAssistant', () => {
  // State
  const config = ref<HomeAssistantConfig | null>(null)
  const status = ref<HomeAssistantStatus | null>(null)
  const entities = ref<HomeAssistantEntity[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const isConfigured = computed(() => status.value?.is_configured || false)
  const isOnline = computed(() => status.value?.is_online || false)
  const haVersion = computed(() => status.value?.ha_version)
  const baseUrl = computed(() => status.value?.base_url)

  // Helper function to handle errors
  const handleError = (err: any, defaultMessage: string) => {
    error.value = err.response?.data?.detail || defaultMessage
    console.error('HomeAssistant Store error:', err)
    throw err
  }

  // Actions

  /**
   * Fetch current configuration
   */
  const fetchConfig = async () => {
    isLoading.value = true
    error.value = null
    try {
      const response = await homeAssistantApi.getConfig()
      config.value = response.data
      return response.data
    } catch (err: any) {
      // If not configured, don't treat as error
      if (err.response?.status === 400) {
        config.value = null
        error.value = null
        return null
      }
      handleError(err, 'เกิดข้อผิดพลาดในการดึงข้อมูลการตั้งค่า Home Assistant')
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Fetch connection status
   */
  const fetchStatus = async () => {
    error.value = null
    try {
      const response = await homeAssistantApi.getStatus()
      status.value = response.data
      return response.data
    } catch (err: any) {
      handleError(err, 'เกิดข้อผิดพลาดในการตรวจสอบสถานะ Home Assistant')
    }
  }

  /**
   * Save configuration
   */
  const saveConfig = async (data: HomeAssistantConfigForm) => {
    isLoading.value = true
    error.value = null
    try {
      const response = await homeAssistantApi.saveConfig(data)
      config.value = response.data
      // Refresh status
      await fetchStatus()
      return response.data
    } catch (err: any) {
      handleError(err, 'เกิดข้อผิดพลาดในการบันทึกการตั้งค่า Home Assistant')
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Update configuration
   */
  const updateConfig = async (data: Partial<HomeAssistantConfigForm>) => {
    isLoading.value = true
    error.value = null
    try {
      const response = await homeAssistantApi.updateConfig(data)
      config.value = response.data
      await fetchStatus()
      return response.data
    } catch (err: any) {
      handleError(err, 'เกิดข้อผิดพลาดในการอัปเดตการตั้งค่า Home Assistant')
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Delete configuration
   */
  const deleteConfig = async () => {
    isLoading.value = true
    error.value = null
    try {
      await homeAssistantApi.deleteConfig()
      config.value = null
      await fetchStatus()
    } catch (err: any) {
      handleError(err, 'เกิดข้อผิดพลาดในการลบการตั้งค่า Home Assistant')
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Test connection
   */
  const testConnection = async (data: HomeAssistantTestConnectionRequest): Promise<HomeAssistantTestConnectionResponse> => {
    isLoading.value = true
    error.value = null
    try {
      const response = await homeAssistantApi.testConnection(data)
      return response.data
    } catch (err: any) {
      handleError(err, 'เกิดข้อผิดพลาดในการทดสอบการเชื่อมต่อ')
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Fetch entities
   */
  const fetchEntities = async (domainFilter?: string) => {
    isLoading.value = true
    error.value = null
    try {
      const response = await homeAssistantApi.getEntities({ domain_filter: domainFilter })
      entities.value = response.data.entities
      return response.data
    } catch (err: any) {
      handleError(err, 'เกิดข้อผิดพลาดในการดึงรายการ entities')
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Clear error
   */
  const clearError = () => {
    error.value = null
  }

  return {
    // State
    config,
    status,
    entities,
    isLoading,
    error,

    // Getters
    isConfigured,
    isOnline,
    haVersion,
    baseUrl,

    // Actions
    fetchConfig,
    fetchStatus,
    saveConfig,
    updateConfig,
    deleteConfig,
    testConnection,
    fetchEntities,
    clearError
  }
})
