/**
 * Housekeeping Types (Phase 5)
 * TypeScript type definitions for housekeeping system
 */

export enum HousekeepingTaskStatus {
  PENDING = 'PENDING',
  IN_PROGRESS = 'IN_PROGRESS',
  COMPLETED = 'COMPLETED',
  CANCELLED = 'CANCELLED'
}

export enum HousekeepingTaskPriority {
  LOW = 'LOW',
  MEDIUM = 'MEDIUM',
  HIGH = 'HIGH',
  URGENT = 'URGENT'
}

export interface HousekeepingTask {
  id: number
  room_id: number
  check_in_id: number | null
  assigned_to: number | null
  status: HousekeepingTaskStatus
  priority: HousekeepingTaskPriority
  title: string
  description: string | null
  notes: string | null
  created_at: string
  started_at: string | null
  completed_at: string | null
  duration_minutes: number | null
  created_by: number
  completed_by: number | null
  updated_at: string
}

export interface HousekeepingTaskWithDetails extends HousekeepingTask {
  room_number: string
  room_type_name: string
  assigned_user_name: string | null
  creator_name: string
  completer_name: string | null
}

export interface HousekeepingTaskCreate {
  room_id: number
  check_in_id?: number | null
  title: string
  description?: string | null
  priority?: HousekeepingTaskPriority
  assigned_to?: number | null
  notes?: string | null
}

export interface HousekeepingTaskUpdate {
  status?: HousekeepingTaskStatus
  priority?: HousekeepingTaskPriority
  assigned_to?: number | null
  notes?: string | null
}

export interface HousekeepingTaskStartRequest {
  started_at?: string | null
}

export interface HousekeepingTaskCompleteRequest {
  completed_at?: string | null
  notes?: string | null
}

export interface HousekeepingStats {
  total_tasks: number
  pending_tasks: number
  in_progress_tasks: number
  completed_today: number
  avg_duration_minutes: number | null
}

export interface HousekeepingTaskListResponse {
  data: HousekeepingTaskWithDetails[]
  total: number
}

// Filter options for task list
export interface HousekeepingTaskFilters {
  status?: HousekeepingTaskStatus
  priority?: HousekeepingTaskPriority
  assigned_to?: number
  room_id?: number
}
