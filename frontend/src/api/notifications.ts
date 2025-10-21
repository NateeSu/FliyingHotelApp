/**
 * Notification API Client (Phase 3)
 * API calls for notification management
 */
import apiClient from './client'
import type {
  Notification,
  NotificationCreate,
  NotificationListResponse,
  NotificationMarkAllReadResponse,
  UnreadCountResponse
} from '@/types/notification'

const BASE_PATH = '/api/v1/notifications'

export interface GetNotificationsParams {
  limit?: number
  offset?: number
  unread_only?: boolean
}

export const notificationsApi = {
  /**
   * Get notifications for current user's role
   */
  async getNotifications(params?: GetNotificationsParams): Promise<NotificationListResponse> {
    const response = await apiClient.get<NotificationListResponse>(BASE_PATH, { params })
    return response.data
  },

  /**
   * Get count of unread notifications
   */
  async getUnreadCount(): Promise<number> {
    const response = await apiClient.get<UnreadCountResponse>(`${BASE_PATH}/unread-count`)
    return response.data.unread_count
  },

  /**
   * Mark a notification as read
   */
  async markAsRead(notificationId: number): Promise<Notification> {
    const response = await apiClient.patch<Notification>(
      `${BASE_PATH}/${notificationId}/read`
    )
    return response.data
  },

  /**
   * Mark all notifications as read for current user's role
   */
  async markAllAsRead(): Promise<NotificationMarkAllReadResponse> {
    const response = await apiClient.post<NotificationMarkAllReadResponse>(
      `${BASE_PATH}/mark-all-read`
    )
    return response.data
  },

  /**
   * Create a new notification (Admin only)
   */
  async createNotification(data: NotificationCreate): Promise<Notification> {
    const response = await apiClient.post<Notification>(BASE_PATH, data)
    return response.data
  }
}
