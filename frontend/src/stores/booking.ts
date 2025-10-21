/**
 * Booking Store (Phase 7)
 * State management for booking system
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { bookingApi } from '@/api/bookings'
import type {
  Booking,
  BookingCreate,
  BookingUpdate,
  BookingCalendarEvent,
  PublicHoliday,
  BookingFilters,
  CalendarEvent,
  RoomAvailabilityCheck
} from '@/types/booking'

export const useBookingStore = defineStore('booking', () => {
  // State
  const bookings = ref<Booking[]>([])
  const currentBooking = ref<Booking | null>(null)
  const calendarEvents = ref<CalendarEvent[]>([])
  const publicHolidays = ref<PublicHoliday[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const total = ref(0)

  // Computed
  const confirmedBookings = computed(() =>
    bookings.value.filter(b => b.status === 'confirmed')
  )

  const pendingBookings = computed(() =>
    bookings.value.filter(b => b.status === 'pending')
  )

  const todayBookings = computed(() => {
    const today = new Date().toISOString().split('T')[0]
    return bookings.value.filter(b => b.check_in_date === today)
  })

  // Actions

  /**
   * Fetch bookings with filters
   */
  async function fetchBookings(filters?: BookingFilters, skip = 0, limit = 100) {
    loading.value = true
    error.value = null

    try {
      const response = await bookingApi.getBookings(filters, skip, limit)
      bookings.value = response.data
      total.value = response.total
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'ไม่สามารถโหลดข้อมูลการจองได้'
      console.error('Error fetching bookings:', err)
    } finally {
      loading.value = false
    }
  }

  /**
   * Fetch booking by ID
   */
  async function fetchBooking(id: number) {
    loading.value = true
    error.value = null

    try {
      const booking = await bookingApi.getBooking(id)
      currentBooking.value = booking
      return booking
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'ไม่สามารถโหลดข้อมูลการจองได้'
      console.error('Error fetching booking:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Create new booking
   */
  async function createBooking(data: BookingCreate) {
    loading.value = true
    error.value = null

    try {
      const booking = await bookingApi.createBooking(data)
      bookings.value.unshift(booking)
      total.value++
      return booking
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'ไม่สามารถสร้างการจองได้'
      console.error('Error creating booking:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Update booking
   */
  async function updateBooking(id: number, data: BookingUpdate) {
    loading.value = true
    error.value = null

    try {
      const booking = await bookingApi.updateBooking(id, data)

      // Update in list
      const index = bookings.value.findIndex(b => b.id === id)
      if (index !== -1) {
        bookings.value[index] = booking
      }

      // Update current if it's the same
      if (currentBooking.value?.id === id) {
        currentBooking.value = booking
      }

      return booking
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'ไม่สามารถอัพเดทการจองได้'
      console.error('Error updating booking:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Cancel booking
   */
  async function cancelBooking(id: number) {
    loading.value = true
    error.value = null

    try {
      const booking = await bookingApi.cancelBooking(id)

      // Update in list
      const index = bookings.value.findIndex(b => b.id === id)
      if (index !== -1) {
        bookings.value[index] = booking
      }

      // Update current if it's the same
      if (currentBooking.value?.id === id) {
        currentBooking.value = booking
      }

      return booking
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'ไม่สามารถยกเลิกการจองได้'
      console.error('Error cancelling booking:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Fetch calendar events for date range
   */
  async function fetchCalendarEvents(startDate: string, endDate: string) {
    loading.value = true
    error.value = null

    try {
      const events = await bookingApi.getCalendarEvents(startDate, endDate)

      // Convert to FullCalendar format
      calendarEvents.value = events.map(event => ({
        id: event.id,
        title: event.title,
        start: event.start,
        end: event.end,
        backgroundColor: event.color,
        borderColor: event.color,
        textColor: '#ffffff',
        extendedProps: {
          bookingId: event.id,
          status: event.status,
          roomNumber: event.room_number,
          customerName: event.customer_name,
          depositAmount: event.deposit_amount,
          totalAmount: event.total_amount,
          isHoliday: false
        }
      }))

      return calendarEvents.value
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'ไม่สามารถโหลดปฏิทินได้'
      console.error('Error fetching calendar events:', err)
      return []
    } finally {
      loading.value = false
    }
  }

  /**
   * Fetch Thai public holidays for a year
   */
  async function fetchPublicHolidays(year: number) {
    loading.value = true
    error.value = null

    try {
      const holidays = await bookingApi.getPublicHolidays(year)
      publicHolidays.value = holidays

      // Add to calendar events
      const holidayEvents: CalendarEvent[] = holidays.map(holiday => ({
        id: `holiday-${holiday.date}`,
        title: `🎉 ${holiday.name}`,
        start: holiday.date,
        end: holiday.date,
        backgroundColor: '#DC2626',
        borderColor: '#DC2626',
        textColor: '#ffffff',
        allDay: true,
        display: 'background',
        extendedProps: {
          isHoliday: true,
          holidayName: holiday.name
        }
      }))

      // Merge with existing calendar events
      calendarEvents.value = [...calendarEvents.value, ...holidayEvents]

      return holidays
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'ไม่สามารถโหลดวันหยุดได้'
      console.error('Error fetching public holidays:', err)
      return []
    } finally {
      loading.value = false
    }
  }

  /**
   * Check room availability
   */
  async function checkAvailability(data: RoomAvailabilityCheck) {
    loading.value = true
    error.value = null

    try {
      const result = await bookingApi.checkAvailability(data)
      return result
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'ไม่สามารถตรวจสอบความว่างได้'
      console.error('Error checking availability:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Get booking for a room on specific date
   * Used for check-in integration
   */
  async function getBookingByRoomAndDate(roomId: number, date: string) {
    try {
      const booking = await bookingApi.getBookingByRoomAndDate(roomId, date)
      return booking
    } catch (err: any) {
      console.error('Error getting booking by room and date:', err)
      return null
    }
  }

  /**
   * Clear current booking
   */
  function clearCurrentBooking() {
    currentBooking.value = null
  }

  /**
   * Clear error
   */
  function clearError() {
    error.value = null
  }

  /**
   * Reset store
   */
  function $reset() {
    bookings.value = []
    currentBooking.value = null
    calendarEvents.value = []
    publicHolidays.value = []
    loading.value = false
    error.value = null
    total.value = 0
  }

  return {
    // State
    bookings,
    currentBooking,
    calendarEvents,
    publicHolidays,
    loading,
    error,
    total,

    // Computed
    confirmedBookings,
    pendingBookings,
    todayBookings,

    // Actions
    fetchBookings,
    fetchBooking,
    createBooking,
    updateBooking,
    cancelBooking,
    fetchCalendarEvents,
    fetchPublicHolidays,
    checkAvailability,
    getBookingByRoomAndDate,
    clearCurrentBooking,
    clearError,
    $reset
  }
})
