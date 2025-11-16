/**
 * Home Assistant & Breaker Management API Client
 */
import axios from './client'
import type {
  HomeAssistantConfig,
  HomeAssistantConfigForm,
  HomeAssistantTestConnectionRequest,
  HomeAssistantTestConnectionResponse,
  HomeAssistantStatus,
  HomeAssistantEntity,
  Breaker,
  BreakerFormData,
  BreakerControlResponse,
  BreakerSyncResponse,
  BreakerActivityLog,
  BreakerActivityLogFilter,
  BreakerStatistics
} from '@/types/homeAssistant'

// Home Assistant Configuration API
export const homeAssistantApi = {
  /**
   * Get current Home Assistant configuration (Admin only)
   */
  getConfig: () =>
    axios.get<HomeAssistantConfig>('/home-assistant/config'),

  /**
   * Create or update Home Assistant configuration (Admin only)
   */
  saveConfig: (data: HomeAssistantConfigForm) =>
    axios.post<HomeAssistantConfig>('/home-assistant/config', data),

  /**
   * Update Home Assistant configuration partially (Admin only)
   */
  updateConfig: (data: Partial<HomeAssistantConfigForm>) =>
    axios.put<HomeAssistantConfig>('/home-assistant/config', data),

  /**
   * Delete Home Assistant configuration (Admin only)
   */
  deleteConfig: () =>
    axios.delete('/home-assistant/config'),

  /**
   * Test connection without saving (Admin only)
   */
  testConnection: (data: HomeAssistantTestConnectionRequest) =>
    axios.post<HomeAssistantTestConnectionResponse>('/home-assistant/test-connection', data),

  /**
   * Get current connection status (All roles)
   */
  getStatus: () =>
    axios.get<HomeAssistantStatus>('/home-assistant/status'),

  /**
   * Get all entities from Home Assistant (Admin only)
   */
  getEntities: (params?: { domain_filter?: string }) =>
    axios.get<{ entities: HomeAssistantEntity[]; total: number }>('/home-assistant/entities', { params })
}

// Breaker Management API
export const breakersApi = {
  /**
   * Get all breakers
   */
  getAll: (params?: {
    skip?: number
    limit?: number
    room_id?: number
    auto_control_enabled?: boolean
    current_state?: string
    is_active?: boolean
  }) =>
    axios.get<{ breakers: Breaker[]; total: number }>('/breakers/', { params }),

  /**
   * Get breaker by ID
   */
  getById: (id: number) =>
    axios.get<Breaker>(`/breakers/${id}`),

  /**
   * Create new breaker (Admin only)
   */
  create: (data: BreakerFormData) =>
    axios.post<Breaker>('/breakers/', data),

  /**
   * Update breaker (Admin only)
   */
  update: (id: number, data: Partial<BreakerFormData>) =>
    axios.put<Breaker>(`/breakers/${id}`, data),

  /**
   * Delete breaker (Admin only)
   */
  delete: (id: number) =>
    axios.delete(`/breakers/${id}`),

  /**
   * Turn on breaker manually (Admin, Reception)
   */
  turnOn: (id: number, reason?: string) =>
    axios.post<BreakerControlResponse>(`/breakers/${id}/turn-on`, { reason }),

  /**
   * Turn off breaker manually (Admin, Reception)
   */
  turnOff: (id: number, reason?: string) =>
    axios.post<BreakerControlResponse>(`/breakers/${id}/turn-off`, { reason }),

  /**
   * Sync breaker status from Home Assistant
   */
  syncStatus: (id: number) =>
    axios.post<BreakerSyncResponse>(`/breakers/${id}/sync-status`),

  /**
   * Sync all breakers (Admin only)
   */
  syncAll: () =>
    axios.post<{ success: boolean; message: string; total: number; success_count: number; failed_count: number }>('/breakers/sync-all'),

  /**
   * Get activity logs for a breaker
   */
  getLogs: (id: number, params?: Omit<BreakerActivityLogFilter, 'breaker_id'>) =>
    axios.get<{ logs: BreakerActivityLog[]; total: number }>(`/breakers/${id}/logs`, { params }),

  /**
   * Get all activity logs
   */
  getAllLogs: (params?: BreakerActivityLogFilter) =>
    axios.get<{ logs: BreakerActivityLog[]; total: number }>('/breakers/logs/all', { params }),

  /**
   * Get breaker statistics
   */
  getStatistics: () =>
    axios.get<BreakerStatistics>('/breakers/stats/overview')
}
