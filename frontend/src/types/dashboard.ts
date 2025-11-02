/**
 * Dashboard Types (Phase 3)
 * TypeScript interfaces for dashboard data structures
 */

export enum StayType {
  OVERNIGHT = 'OVERNIGHT',
  TEMPORARY = 'TEMPORARY'
}

export interface DashboardRoomCard {
  // Room information
  id: number
  room_number: string
  floor: number
  status: string

  // Room type information
  room_type_id: number
  room_type_name: string
  room_type_description: string | null

  // Room rate information (for booking form)
  overnight_rate: number | null
  temporary_rate: number | null

  // Check-in information (if occupied)
  check_in_id: number | null
  customer_name: string | null
  customer_phone: string | null
  stay_type: StayType | null
  check_in_time: string | null
  expected_check_out_time: string | null

  // Booking information (if reserved) - Phase 7
  booking_id: number | null
  booking_customer_name: string | null
  booking_customer_phone: string | null
  booking_check_in_date: string | null
  booking_check_out_date: string | null
  booking_deposit_amount: number | null

  // Overtime information
  is_overtime: boolean
  overtime_minutes: number | null

  // Additional info
  qr_code: string | null
  notes: string | null
  is_active: boolean
}

export interface DashboardStats {
  total_rooms: number
  available_rooms: number
  occupied_rooms: number
  cleaning_rooms: number
  reserved_rooms: number
  out_of_service_rooms: number
  occupancy_rate: number // Percentage

  // Check-in statistics
  total_check_ins_today: number
  overnight_stays: number
  temporary_stays: number

  // Revenue statistics (today)
  revenue_today: string // Decimal as string

  // Maintenance statistics
  pending_maintenance_count?: number // Tasks not completed
}

export interface DashboardResponse {
  rooms: DashboardRoomCard[]
  stats: DashboardStats
  last_updated: string
}

export interface OvertimeAlert {
  room_id: number
  room_number: string
  check_in_id: number
  customer_name: string
  stay_type: StayType
  expected_check_out_time: string
  overtime_minutes: number
  created_at: string
}

export interface OvertimeAlertsResponse {
  data: OvertimeAlert[]
  total: number
}
