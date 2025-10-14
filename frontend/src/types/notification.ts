/**
 * Notification Types (Phase 3)
 * TypeScript interfaces for notification data structures
 */

export enum NotificationType {
  ROOM_STATUS_CHANGE = 'room_status_change',
  OVERTIME_ALERT = 'overtime_alert',
  BOOKING_REMINDER = 'booking_reminder',
  HOUSEKEEPING_TASK = 'housekeeping_task',
  MAINTENANCE_REQUEST = 'maintenance_request',
  CHECK_IN = 'check_in',
  CHECK_OUT = 'check_out',
  SYSTEM_ALERT = 'system_alert'
}

export enum TargetRole {
  ADMIN = 'ADMIN',
  RECEPTION = 'RECEPTION',
  HOUSEKEEPING = 'HOUSEKEEPING',
  MAINTENANCE = 'MAINTENANCE'
}

export interface Notification {
  id: number
  notification_type: NotificationType
  target_role: TargetRole
  title: string
  message: string
  room_id: number | null
  related_booking_id: number | null
  related_check_in_id: number | null
  is_read: boolean
  read_at: string | null
  telegram_sent: boolean
  telegram_message_id: string | null
  created_at: string
}

export interface NotificationCreate {
  notification_type: NotificationType
  target_role: TargetRole
  title: string
  message: string
  room_id?: number
  related_booking_id?: number
  related_check_in_id?: number
}

export interface NotificationListResponse {
  data: Notification[]
  total: number
  unread_count: number
}

export interface NotificationMarkAllReadResponse {
  marked_count: number
  message: string
}

export interface UnreadCountResponse {
  unread_count: number
}
