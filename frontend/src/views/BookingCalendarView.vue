<template>
  <div class="booking-calendar-page">
    <!-- Header -->
    <div class="header-section">
      <div class="flex items-center justify-between mb-6">
        <div>
          <h1 class="text-3xl font-bold text-gray-900">ปฏิทินการจอง</h1>
          <p class="text-gray-600 mt-1">จัดการการจองห้องพัก</p>
        </div>
        <n-button type="primary" size="large" @click="showCreateModal = true">
          <template #icon>
            <n-icon><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path d="M10.75 4.75a.75.75 0 00-1.5 0v4.5h-4.5a.75.75 0 000 1.5h4.5v4.5a.75.75 0 001.5 0v-4.5h4.5a.75.75 0 000-1.5h-4.5v-4.5z"/>
            </svg></n-icon>
          </template>
          สร้างการจอง
        </n-button>
      </div>
    </div>

    <!-- Calendar -->
    <div class="calendar-container bg-white rounded-xl shadow-lg p-6">
      <FullCalendar
        ref="calendarRef"
        :options="calendarOptions"
      />
    </div>

    <!-- Create/Edit Booking Modal -->
    <BookingFormModal
      v-model:show="showFormModal"
      :booking="selectedBooking"
      :preselected-date="preselectedDate"
      @saved="handleBookingSaved"
    />

    <!-- Booking Detail Modal -->
    <BookingDetailModal
      v-model:show="showDetailModal"
      :booking="selectedBooking"
      @edit="handleEdit"
      @cancel="handleCancelBooking"
      @close="showDetailModal = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useMessage } from 'naive-ui'
import FullCalendar from '@fullcalendar/vue3'
import dayGridPlugin from '@fullcalendar/daygrid'
import interactionPlugin from '@fullcalendar/interaction'
import { useBookingStore } from '@/stores/booking'
import BookingFormModal from '@/components/BookingFormModal.vue'
import BookingDetailModal from '@/components/BookingDetailModal.vue'
import type { CalendarOptions, EventClickArg, DateSelectArg } from '@fullcalendar/core'
import type { Booking } from '@/types/booking'

const message = useMessage()
const bookingStore = useBookingStore()

// Refs
const calendarRef = ref()
const showFormModal = ref(false)
const showDetailModal = ref(false)
const showCreateModal = ref(false)
const selectedBooking = ref<Booking | null>(null)
const preselectedDate = ref<string | null>(null)

// Calendar options
const calendarOptions = computed<CalendarOptions>(() => ({
  plugins: [dayGridPlugin, interactionPlugin],
  initialView: 'dayGridMonth',
  locale: 'th',
  headerToolbar: {
    left: 'prev,next today',
    center: 'title',
    right: 'dayGridMonth,dayGridWeek'
  },
  buttonText: {
    today: 'วันนี้',
    month: 'เดือน',
    week: 'สัปดาห์',
    day: 'วัน'
  },
  events: bookingStore.calendarEvents,
  editable: false,
  selectable: true,
  selectMirror: true,
  dayMaxEvents: true,
  weekends: true,
  height: 'auto',
  eventClick: handleEventClick,
  select: handleDateSelect,
  datesSet: handleDatesSet,
  eventTimeFormat: {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false
  }
}))

// Event handlers

/**
 * Handle event click (booking click)
 */
async function handleEventClick(info: EventClickArg) {
  const { extendedProps } = info.event

  // If it's a holiday, show info
  if (extendedProps.isHoliday) {
    message.info(`วันหยุด: ${extendedProps.holidayName}`)
    return
  }

  // If it's a booking, show details
  if (extendedProps.bookingId) {
    try {
      const booking = await bookingStore.fetchBooking(extendedProps.bookingId)
      selectedBooking.value = booking
      showDetailModal.value = true
    } catch (error) {
      message.error('ไม่สามารถโหลดรายละเอียดการจองได้')
    }
  }
}

/**
 * Handle date select (create new booking)
 */
function handleDateSelect(selectInfo: DateSelectArg) {
  const { start, end } = selectInfo

  // Set preselected dates
  preselectedDate.value = start.toISOString().split('T')[0]

  // Open create modal
  selectedBooking.value = null
  showFormModal.value = true

  // Clear selection
  selectInfo.view.calendar.unselect()
}

/**
 * Handle calendar date range change
 */
async function handleDatesSet(dateInfo: any) {
  const start = dateInfo.start.toISOString().split('T')[0]
  const end = dateInfo.end.toISOString().split('T')[0]

  // Fetch events for this date range
  await fetchCalendarData(start, end)
}

/**
 * Fetch calendar data (bookings + holidays)
 */
async function fetchCalendarData(startDate: string, endDate: string) {
  try {
    // Fetch bookings
    await bookingStore.fetchCalendarEvents(startDate, endDate)

    // Fetch holidays for current year
    const currentYear = new Date().getFullYear()
    await bookingStore.fetchPublicHolidays(currentYear)

  } catch (error) {
    message.error('ไม่สามารถโหลดข้อมูลปฏิทินได้')
  }
}

/**
 * Handle booking saved (created or updated)
 */
async function handleBookingSaved() {
  showFormModal.value = false
  showCreateModal.value = false
  selectedBooking.value = null
  preselectedDate.value = null

  // Refresh calendar
  const calendarApi = calendarRef.value?.getApi()
  if (calendarApi) {
    const view = calendarApi.view
    const start = view.currentStart.toISOString().split('T')[0]
    const end = view.currentEnd.toISOString().split('T')[0]
    await fetchCalendarData(start, end)
  }

  message.success('บันทึกการจองเรียบร้อยแล้ว')
}

/**
 * Handle edit booking
 */
function handleEdit(booking: Booking) {
  selectedBooking.value = booking
  showDetailModal.value = false
  showFormModal.value = true
}

/**
 * Handle cancel booking
 */
async function handleCancelBooking(bookingId: number) {
  try {
    await bookingStore.cancelBooking(bookingId)
    showDetailModal.value = false
    selectedBooking.value = null

    // Refresh calendar
    const calendarApi = calendarRef.value?.getApi()
    if (calendarApi) {
      const view = calendarApi.view
      const start = view.currentStart.toISOString().split('T')[0]
      const end = view.currentEnd.toISOString().split('T')[0]
      await fetchCalendarData(start, end)
    }

    message.success('ยกเลิกการจองเรียบร้อยแล้ว')
  } catch (error) {
    message.error('ไม่สามารถยกเลิกการจองได้')
  }
}

// Lifecycle
onMounted(async () => {
  // Initial load will be triggered by handleDatesSet
})

// Watch for create modal
import { watch } from 'vue'
watch(showCreateModal, (newVal) => {
  if (newVal) {
    selectedBooking.value = null
    preselectedDate.value = null
    showFormModal.value = true
    showCreateModal.value = false
  }
})
</script>

<style scoped>
.booking-calendar-page {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.header-section {
  margin-bottom: 2rem;
}

.calendar-container {
  min-height: 600px;
}

/* FullCalendar customization */
:deep(.fc) {
  font-family: 'Prompt', 'Sarabun', sans-serif;
}

:deep(.fc-toolbar-title) {
  font-size: 1.5rem;
  font-weight: 700;
  color: #111827;
}

:deep(.fc-button) {
  padding: 0.5rem 1rem;
  font-weight: 600;
  text-transform: none;
}

:deep(.fc-button-primary) {
  background-color: #3B82F6;
  border-color: #3B82F6;
}

:deep(.fc-button-primary:hover) {
  background-color: #2563EB;
  border-color: #2563EB;
}

:deep(.fc-button-primary:disabled) {
  background-color: #93C5FD;
  border-color: #93C5FD;
}

:deep(.fc-day-today) {
  background-color: #FEF3C7 !important;
}

:deep(.fc-event) {
  cursor: pointer;
  border-radius: 4px;
  padding: 2px 4px;
  font-size: 0.875rem;
  font-weight: 500;
}

:deep(.fc-event:hover) {
  opacity: 0.9;
}

:deep(.fc-daygrid-event-dot) {
  display: none;
}

/* Mobile responsive */
@media (max-width: 768px) {
  .booking-calendar-page {
    padding: 1rem;
  }

  :deep(.fc-toolbar) {
    flex-direction: column;
    gap: 0.5rem;
  }

  :deep(.fc-toolbar-chunk) {
    display: flex;
    justify-content: center;
  }

  :deep(.fc-toolbar-title) {
    font-size: 1.25rem;
  }
}
</style>
