/**
 * Booking API Client (Phase 7)
 * API calls for booking management
 */
import api from './axios'
import type {
  Booking,
  BookingCreate,
  BookingUpdate,
  BookingListResponse,
  BookingCalendarEvent,
  PublicHoliday,
  RoomAvailabilityCheck,
  RoomAvailabilityResponse,
  BookingFilters
} from '@/types/booking'

export const bookingApi = {
  /**
   * Create a new booking
   */
  async createBooking(data: BookingCreate): Promise<Booking> {
    const response = await api.post<Booking>('/api/v1/bookings/', data)
    return response.data
  },

  /**
   * Get list of bookings with filters
   */
  async getBookings(filters?: BookingFilters, skip = 0, limit = 100): Promise<BookingListResponse> {
    const params: any = { skip, limit }

    if (filters) {
      if (filters.status) params.status = filters.status
      if (filters.room_id) params.room_id = filters.room_id
      if (filters.customer_id) params.customer_id = filters.customer_id
      if (filters.start_date) params.start_date = filters.start_date
      if (filters.end_date) params.end_date = filters.end_date
    }

    const response = await api.get<BookingListResponse>('/api/v1/bookings/', { params })
    return response.data
  },

  /**
   * Get booking by ID
   */
  async getBooking(id: number): Promise<Booking> {
    const response = await api.get<Booking>(`/api/v1/bookings/${id}`)
    return response.data
  },

  /**
   * Update booking
   */
  async updateBooking(id: number, data: BookingUpdate): Promise<Booking> {
    const response = await api.put<Booking>(`/api/v1/bookings/${id}`, data)
    return response.data
  },

  /**
   * Cancel booking
   */
  async cancelBooking(id: number): Promise<Booking> {
    const response = await api.delete<Booking>(`/api/v1/bookings/${id}`)
    return response.data
  },

  /**
   * Get calendar events (bookings) for date range
   */
  async getCalendarEvents(startDate: string, endDate: string): Promise<BookingCalendarEvent[]> {
    const response = await api.get<BookingCalendarEvent[]>('/api/v1/bookings/calendar/events', {
      params: {
        start_date: startDate,
        end_date: endDate
      }
    })
    return response.data
  },

  /**
   * Get Thai public holidays for a year
   */
  async getPublicHolidays(year: number): Promise<PublicHoliday[]> {
    const response = await api.get<PublicHoliday[]>(`/api/v1/bookings/calendar/public-holidays/${year}`)
    return response.data
  },

  /**
   * Check room availability for date range
   */
  async checkAvailability(data: RoomAvailabilityCheck): Promise<RoomAvailabilityResponse> {
    const response = await api.post<RoomAvailabilityResponse>('/api/v1/bookings/check-availability', data)
    return response.data
  },

  /**
   * Get booking for a room on a specific date
   * Used for check-in integration
   */
  async getBookingByRoomAndDate(roomId: number, date: string): Promise<Booking | null> {
    try {
      const response = await api.get<BookingListResponse>('/api/v1/bookings/', {
        params: {
          room_id: roomId,
          start_date: date,
          end_date: date,
          status: 'confirmed',
          limit: 1
        }
      })

      if (response.data.data && response.data.data.length > 0) {
        return response.data.data[0]
      }

      return null
    } catch (error) {
      console.error('Error getting booking by room and date:', error)
      return null
    }
  }
}

export default bookingApi
