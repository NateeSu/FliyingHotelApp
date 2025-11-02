export enum MaintenanceTaskStatus {
  PENDING = 'PENDING',
  IN_PROGRESS = 'IN_PROGRESS',
  COMPLETED = 'COMPLETED',
  CANCELLED = 'CANCELLED'
}

export enum MaintenanceTaskPriority {
  URGENT = 'URGENT',
  HIGH = 'HIGH',
  MEDIUM = 'MEDIUM',
  LOW = 'LOW'
}

export enum MaintenanceTaskCategory {
  PLUMBING = 'PLUMBING',
  ELECTRICAL = 'ELECTRICAL',
  HVAC = 'HVAC',
  FURNITURE = 'FURNITURE',
  APPLIANCE = 'APPLIANCE',
  BUILDING = 'BUILDING',
  OTHER = 'OTHER'
}

export interface MaintenanceTask {
  id: number
  room_id: number
  category: MaintenanceTaskCategory
  title: string
  description: string | null
  priority: MaintenanceTaskPriority
  status: MaintenanceTaskStatus
  assigned_to: number | null
  created_by: number
  completed_by: number | null
  notes: string | null
  created_at: string
  updated_at: string | null
  started_at: string | null
  completed_at: string | null
  duration_minutes: number | null
}

export interface MaintenanceTaskWithDetails extends MaintenanceTask {
  room_number: string
  room_type_name: string
  assigned_user_name: string | null
  creator_name: string
  completer_name: string | null
}

export interface MaintenanceTaskCreate {
  room_id: number
  category: MaintenanceTaskCategory
  title: string
  description?: string
  priority: MaintenanceTaskPriority
  assigned_to?: number | null
  notes?: string
  photos?: File[]
}

export interface MaintenanceTaskUpdate {
  category?: MaintenanceTaskCategory
  title?: string
  description?: string
  priority?: MaintenanceTaskPriority
  assigned_to?: number
  notes?: string
}

export interface MaintenanceTaskStartRequest {
  started_at?: string
}

export interface MaintenanceTaskCompleteRequest {
  completed_at?: string
  notes?: string
}

export interface MaintenanceTaskFilters {
  status?: MaintenanceTaskStatus
  priority?: MaintenanceTaskPriority
  category?: MaintenanceTaskCategory
  assigned_to?: number
  room_id?: number
}

export interface MaintenanceTaskListResponse {
  tasks: MaintenanceTaskWithDetails[]
  total: number
  skip: number
  limit: number
}

export interface MaintenanceStats {
  total_tasks: number
  pending_tasks: number
  in_progress_tasks: number
  completed_today: number
  avg_duration_minutes: number | null
  by_category: Record<string, number>
  by_priority: Record<string, number>
}
