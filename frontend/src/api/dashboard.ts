/**
 * Dashboard API Client (Phase 3)
 * API calls for dashboard data
 */
import apiClient from './client'
import type {
  DashboardResponse,
  DashboardRoomCard,
  DashboardStats,
  OvertimeAlertsResponse
} from '@/types/dashboard'

const BASE_PATH = '/dashboard'

export const dashboardApi = {
  /**
   * Get complete dashboard data (rooms + stats)
   */
  async getDashboard(): Promise<DashboardResponse> {
    const response = await apiClient.get<DashboardResponse>(BASE_PATH)
    return response.data
  },

  /**
   * Get all rooms with check-in details
   */
  async getRooms(): Promise<DashboardRoomCard[]> {
    const response = await apiClient.get<DashboardRoomCard[]>(`${BASE_PATH}/rooms`)
    return response.data
  },

  /**
   * Get dashboard statistics
   */
  async getStats(): Promise<DashboardStats> {
    const response = await apiClient.get<DashboardStats>(`${BASE_PATH}/stats`)
    return response.data
  },

  /**
   * Get overtime alerts
   */
  async getOvertimeAlerts(): Promise<OvertimeAlertsResponse> {
    const response = await apiClient.get<OvertimeAlertsResponse>(`${BASE_PATH}/overtime-alerts`)
    return response.data
  }
}
