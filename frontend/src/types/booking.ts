/**
 * Booking Types (Phase 7)
 * TypeScript interfaces for booking system
 */

export type BookingStatus = 'pending' | 'confirmed' | 'checked_in' | 'completed' | 'cancelled'

export interface Booking {
  id: number
  customer_id: number
  room_id: number
  check_in_date: string // ISO date string
  check_out_date: string // ISO date string
  number_of_nights: number
  total_amount: number
  deposit_amount: number
  status: BookingStatus
  notes?: string
  created_by: number
  created_at: string
  updated_at: string
  cancelled_at?: string

  // Related data
  customer_name?: string
  customer_phone?: string
  room_number?: string
  room_type_name?: string
  creator_name?: string
}

export interface BookingCreate {
  customer_id: number
  room_id: number
  check_in_date: string
  check_out_date: string
  total_amount: number
  deposit_amount?: number
  notes?: string
}

export interface BookingUpdate {
  check_in_date?: string
  check_out_date?: string
  total_amount?: number
  deposit_amount?: number
  notes?: string
}

export interface BookingListResponse {
  data: Booking[]
  total: number
  skip: number
  limit: number
}

export interface BookingCalendarEvent {
  id: number
  title: string
  start: string // ISO date
  end: string // ISO date
  color: string
  status: string
  room_number: string
  customer_name: string
  deposit_amount: number
  total_amount: number
}

export interface PublicHoliday {
  date: string // ISO date
  name: string // Thai name
  name_en: string // English name
}

export interface RoomAvailabilityCheck {
  room_id: number
  check_in_date: string
  check_out_date: string
  exclude_booking_id?: number
}

export interface RoomAvailabilityResponse {
  available: boolean
  conflicting_bookings: Booking[]
}

export interface BookingStats {
  total_bookings: number
  pending: number
  confirmed: number
  checked_in: number
  completed: number
  cancelled: number
  total_revenue: number
  total_deposits: number
}

// Calendar event for FullCalendar
export interface CalendarEvent {
  id: string | number
  title: string
  start: string | Date
  end: string | Date
  backgroundColor?: string
  borderColor?: string
  textColor?: string
  extendedProps?: {
    bookingId?: number
    status?: string
    roomNumber?: string
    customerName?: string
    depositAmount?: number
    totalAmount?: number
    isHoliday?: boolean
    holidayName?: string
  }
}

// Booking filters
export interface BookingFilters {
  status?: BookingStatus
  room_id?: number
  customer_id?: number
  start_date?: string
  end_date?: string
}
