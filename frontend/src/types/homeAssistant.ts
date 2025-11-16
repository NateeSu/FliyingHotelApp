/**
 * Home Assistant & Breaker Management Types
 */

// Enums
export enum BreakerState {
  ON = 'ON',
  OFF = 'OFF',
  UNAVAILABLE = 'UNAVAILABLE'
}

export enum BreakerAction {
  TURN_ON = 'TURN_ON',
  TURN_OFF = 'TURN_OFF',
  STATUS_SYNC = 'STATUS_SYNC'
}

export enum TriggerType {
  AUTO = 'AUTO',
  MANUAL = 'MANUAL',
  SYSTEM = 'SYSTEM'
}

export enum ActionStatus {
  SUCCESS = 'SUCCESS',
  FAILED = 'FAILED',
  TIMEOUT = 'TIMEOUT'
}

// Home Assistant Configuration
export interface HomeAssistantConfig {
  id: number
  base_url: string
  access_token_masked: string
  is_online: boolean
  last_ping_at: string | null
  ha_version: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface HomeAssistantConfigForm {
  base_url: string
  access_token: string
}

export interface HomeAssistantTestConnectionRequest {
  base_url: string
  access_token: string
}

export interface HomeAssistantTestConnectionResponse {
  success: boolean
  message: string
  ha_version?: string
  entity_count?: number
  response_time_ms?: number
}

export interface HomeAssistantStatus {
  is_configured: boolean
  is_online: boolean
  last_ping_at: string | null
  ha_version: string | null
  base_url: string | null
}

export interface HomeAssistantEntity {
  entity_id: string
  friendly_name?: string
  state: string
  attributes?: Record<string, any>
}

// Breaker Management
export interface Breaker {
  id: number
  entity_id: string
  friendly_name: string
  room_id: number | null
  room_number: string | null
  room_status: string | null
  auto_control_enabled: boolean
  is_available: boolean
  current_state: BreakerState
  last_state_update: string | null
  consecutive_errors: number
  last_error_message: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface BreakerFormData {
  entity_id: string
  friendly_name: string
  room_id?: number | null
  auto_control_enabled: boolean
}

export interface BreakerControlResponse {
  success: boolean
  message: string
  breaker_id: number
  new_state: BreakerState
  response_time_ms?: number
}

export interface BreakerSyncResponse {
  success: boolean
  message: string
  breaker_id: number
  current_state: BreakerState
  is_available: boolean
  synced_at: string
}

// Activity Logs
export interface BreakerActivityLog {
  id: number
  breaker_id: number
  entity_id: string
  friendly_name: string
  action: BreakerAction
  trigger_type: TriggerType
  triggered_by: number | null
  triggered_by_name: string | null
  room_status_before: string | null
  room_status_after: string | null
  status: ActionStatus
  error_message: string | null
  response_time_ms: number | null
  created_at: string
}

export interface BreakerActivityLogFilter {
  breaker_id?: number
  action?: BreakerAction
  trigger_type?: TriggerType
  status?: ActionStatus
  start_date?: string
  end_date?: string
  limit?: number
  offset?: number
}

// Statistics
export interface BreakerStatistics {
  total_breakers: number
  online_breakers: number
  offline_breakers: number
  breakers_on: number
  breakers_off: number
  auto_control_enabled: number
  breakers_with_errors: number
  total_actions_today: number
  success_rate_today: number
  avg_response_time_ms: number | null
}

// Helper functions for display
export const getBreakerStateLabel = (state: BreakerState): string => {
  const labels: Record<BreakerState, string> = {
    [BreakerState.ON]: 'เปิด',
    [BreakerState.OFF]: 'ปิด',
    [BreakerState.UNAVAILABLE]: 'ไม่พร้อมใช้งาน'
  }
  return labels[state]
}

export const getBreakerStateColor = (state: BreakerState): string => {
  const colors: Record<BreakerState, string> = {
    [BreakerState.ON]: 'success',
    [BreakerState.OFF]: 'default',
    [BreakerState.UNAVAILABLE]: 'error'
  }
  return colors[state]
}

export const getTriggerTypeLabel = (type: TriggerType): string => {
  const labels: Record<TriggerType, string> = {
    [TriggerType.AUTO]: 'อัตโนมัติ',
    [TriggerType.MANUAL]: 'กดเอง',
    [TriggerType.SYSTEM]: 'ระบบ'
  }
  return labels[type]
}

export const getActionLabel = (action: BreakerAction): string => {
  const labels: Record<BreakerAction, string> = {
    [BreakerAction.TURN_ON]: 'เปิด',
    [BreakerAction.TURN_OFF]: 'ปิด',
    [BreakerAction.STATUS_SYNC]: 'ซิงค์สถานะ'
  }
  return labels[action]
}

export const getActionStatusLabel = (status: ActionStatus): string => {
  const labels: Record<ActionStatus, string> = {
    [ActionStatus.SUCCESS]: 'สำเร็จ',
    [ActionStatus.FAILED]: 'ล้มเหลว',
    [ActionStatus.TIMEOUT]: 'หมดเวลา'
  }
  return labels[status]
}
