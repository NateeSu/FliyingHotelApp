/**
 * Housekeeping API Client (Phase 5)
 * API calls for housekeeping task management
 */
import { apiClient } from './client'
import type {
  HousekeepingTaskWithDetails,
  HousekeepingTaskCreate,
  HousekeepingTaskUpdate,
  HousekeepingTaskStartRequest,
  HousekeepingTaskCompleteRequest,
  HousekeepingStats,
  HousekeepingTaskListResponse,
  HousekeepingTaskFilters
} from '@/types/housekeeping'

const BASE_PATH = '/housekeeping'

export const housekeepingApi = {
  /**
   * Get list of housekeeping tasks with filters
   */
  async getTasks(filters?: HousekeepingTaskFilters, skip = 0, limit = 100): Promise<HousekeepingTaskListResponse> {
    const params: any = { skip, limit }

    if (filters?.status) params.status = filters.status
    if (filters?.priority) params.priority = filters.priority
    if (filters?.assigned_to) params.assigned_to = filters.assigned_to
    if (filters?.room_id) params.room_id = filters.room_id

    const response = await apiClient.get<HousekeepingTaskListResponse>(BASE_PATH, { params })
    return response.data
  },

  /**
   * Get task by ID
   */
  async getTaskById(taskId: number): Promise<HousekeepingTaskWithDetails> {
    const response = await apiClient.get<HousekeepingTaskWithDetails>(`${BASE_PATH}/${taskId}`)
    return response.data
  },

  /**
   * Create new housekeeping task
   */
  async createTask(data: HousekeepingTaskCreate): Promise<HousekeepingTaskWithDetails> {
    const response = await apiClient.post<HousekeepingTaskWithDetails>(BASE_PATH, data)
    return response.data
  },

  /**
   * Update housekeeping task
   */
  async updateTask(taskId: number, data: HousekeepingTaskUpdate): Promise<HousekeepingTaskWithDetails> {
    const response = await apiClient.put<HousekeepingTaskWithDetails>(`${BASE_PATH}/${taskId}`, data)
    return response.data
  },

  /**
   * Start housekeeping task
   */
  async startTask(taskId: number, data?: HousekeepingTaskStartRequest): Promise<HousekeepingTaskWithDetails> {
    const response = await apiClient.post<HousekeepingTaskWithDetails>(
      `${BASE_PATH}/${taskId}/start`,
      data || {}
    )
    return response.data
  },

  /**
   * Complete housekeeping task
   */
  async completeTask(
    taskId: number,
    data?: HousekeepingTaskCompleteRequest
  ): Promise<HousekeepingTaskWithDetails> {
    const response = await apiClient.post<HousekeepingTaskWithDetails>(
      `${BASE_PATH}/${taskId}/complete`,
      data || {}
    )
    return response.data
  },

  /**
   * Get housekeeping statistics
   */
  async getStats(): Promise<HousekeepingStats> {
    const response = await apiClient.get<HousekeepingStats>(`${BASE_PATH}/stats/summary`)
    return response.data
  }
}
