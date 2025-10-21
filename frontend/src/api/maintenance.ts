import api from './axios'
import type {
  MaintenanceTaskWithDetails,
  MaintenanceTaskCreate,
  MaintenanceTaskUpdate,
  MaintenanceTaskStartRequest,
  MaintenanceTaskCompleteRequest,
  MaintenanceTaskFilters,
  MaintenanceTaskListResponse,
  MaintenanceStats
} from '@/types/maintenance'

export const maintenanceApi = {
  /**
   * Get list of maintenance tasks with filters
   */
  async getTasks(
    filters?: MaintenanceTaskFilters,
    skip = 0,
    limit = 100
  ): Promise<MaintenanceTaskListResponse> {
    const params: Record<string, any> = { skip, limit }

    if (filters?.status) params.status = filters.status
    if (filters?.priority) params.priority = filters.priority
    if (filters?.category) params.category = filters.category
    if (filters?.assigned_to) params.assigned_to = filters.assigned_to
    if (filters?.room_id) params.room_id = filters.room_id

    const response = await api.get<MaintenanceTaskListResponse>('/api/v1/maintenance/', { params })
    return response.data
  },

  /**
   * Get maintenance task by ID
   */
  async getTaskById(taskId: number): Promise<MaintenanceTaskWithDetails> {
    const response = await api.get<MaintenanceTaskWithDetails>(`/api/v1/maintenance/${taskId}`)
    return response.data
  },

  /**
   * Create a new maintenance task
   */
  async createTask(data: MaintenanceTaskCreate): Promise<MaintenanceTaskWithDetails> {
    const response = await api.post<MaintenanceTaskWithDetails>('/api/v1/maintenance/', data)
    return response.data
  },

  /**
   * Update maintenance task
   */
  async updateTask(
    taskId: number,
    data: MaintenanceTaskUpdate
  ): Promise<MaintenanceTaskWithDetails> {
    const response = await api.put<MaintenanceTaskWithDetails>(`/api/v1/maintenance/${taskId}`, data)
    return response.data
  },

  /**
   * Start a maintenance task
   */
  async startTask(
    taskId: number,
    data?: MaintenanceTaskStartRequest
  ): Promise<MaintenanceTaskWithDetails> {
    const response = await api.post<MaintenanceTaskWithDetails>(
      `/api/v1/maintenance/${taskId}/start`,
      data || {}
    )
    return response.data
  },

  /**
   * Complete a maintenance task
   */
  async completeTask(
    taskId: number,
    data?: MaintenanceTaskCompleteRequest
  ): Promise<MaintenanceTaskWithDetails> {
    const response = await api.post<MaintenanceTaskWithDetails>(
      `/api/v1/maintenance/${taskId}/complete`,
      data || {}
    )
    return response.data
  },

  /**
   * Cancel a maintenance task
   */
  async cancelTask(taskId: number): Promise<MaintenanceTaskWithDetails> {
    const response = await api.post<MaintenanceTaskWithDetails>(`/api/v1/maintenance/${taskId}/cancel`)
    return response.data
  },

  /**
   * Get maintenance statistics
   */
  async getStats(): Promise<MaintenanceStats> {
    const response = await api.get<MaintenanceStats>('/api/v1/maintenance/stats/summary')
    return response.data
  }
}
