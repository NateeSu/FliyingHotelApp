/**
 * WebSocket Types (Phase 3)
 * TypeScript interfaces for WebSocket messages
 */

export enum WebSocketEventType {
  CONNECTED = 'connected',
  ROOM_STATUS_CHANGED = 'room_status_changed',
  OVERTIME_ALERT = 'overtime_alert',
  CHECK_IN = 'check_in',
  CHECK_OUT = 'check_out',
  NOTIFICATION = 'notification'
}

export interface WebSocketMessage<T = any> {
  event: WebSocketEventType | string
  data: T
  timestamp?: string
}

export interface ConnectedEventData {
  client_id: string
  message: string
}

export interface RoomStatusChangedEventData {
  room_id: number
  old_status: string
  new_status: string
  room_data?: any
}

export interface OvertimeAlertEventData {
  room_id: number
  room_number: string
  guest_name: string
  overtime_minutes: number
  stay_type: string
}

export interface CheckInEventData {
  room_id: number
  room_number: string
  customer_name: string
  stay_type: string
}

export interface CheckOutEventData {
  room_id: number
  room_number: string
}

export interface NotificationEventData {
  notification_type: string
  target_role: string
  title: string
  message: string
  room_id?: number
}

export interface WebSocketConnectionState {
  connected: boolean
  connecting: boolean
  error: string | null
  client_id: string | null
}
