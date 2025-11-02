<template>
  <div class="dashboard-view">
    <!-- Header -->
    <div class="dashboard-header">
      <div class="header-content">
        <h1 class="title">แดชบอร์ดจัดการห้องพัก</h1>
        <div class="header-info">
          <div class="connection-status" :class="{ connected: isConnected }">
            <span class="dot"></span>
            <span class="text">{{ isConnected ? 'เชื่อมต่อแล้ว' : 'ไม่ได้เชื่อมต่อ' }}</span>
          </div>
          <div v-if="lastUpdated" class="last-updated">
            อัปเดตล่าสุด: {{ formatLastUpdated(lastUpdated) }}
          </div>
        </div>
      </div>

      <div class="header-actions">
        <button class="btn-refresh" @click="handleRefresh" :disabled="isLoading">
          <span class="icon">🔄</span>
          <span class="text">รีเฟรช</span>
        </button>
        <button class="btn-notifications" @click="toggleNotificationPanel">
          <span class="icon">🔔</span>
          <span v-if="hasUnread" class="badge">{{ unreadCount }}</span>
        </button>
      </div>
    </div>

    <!-- Statistics Cards -->
    <div v-if="stats" class="stats-grid">
      <!-- Total Rooms Card -->
      <div class="stat-card total">
        <div class="stat-icon">🏨</div>
        <div class="stat-content">
          <div class="stat-label">ห้องพักทั้งหมด</div>
          <div class="stat-value">{{ stats.total_rooms }}</div>
        </div>
      </div>

      <!-- Available Rooms Card -->
      <div class="stat-card available">
        <div class="stat-icon">✅</div>
        <div class="stat-content">
          <div class="stat-label">ห้องพักว่าง</div>
          <div class="stat-value">{{ stats.available_rooms }}</div>
        </div>
      </div>

      <!-- Overnight Stays Card -->
      <div class="stat-card overnight">
        <div class="stat-icon">🌙</div>
        <div class="stat-content">
          <div class="stat-label">พักค้างคืน</div>
          <div class="stat-value">{{ stats.overnight_stays }}</div>
        </div>
      </div>

      <!-- Temporary Stays Card -->
      <div class="stat-card temporary">
        <div class="stat-icon">⏰</div>
        <div class="stat-content">
          <div class="stat-label">พักชั่วคราว</div>
          <div class="stat-value">{{ stats.temporary_stays }}</div>
        </div>
      </div>

      <!-- Cleaning Rooms Card -->
      <div class="stat-card cleaning">
        <div class="stat-icon">🧹</div>
        <div class="stat-content">
          <div class="stat-label">ทำความสะอาด</div>
          <div class="stat-value">{{ stats.cleaning_rooms }}</div>
        </div>
      </div>

      <!-- Pending Maintenance Card -->
      <div class="stat-card maintenance">
        <div class="stat-icon">🔧</div>
        <div class="stat-content">
          <div class="stat-label">แจ้งซ่อม</div>
          <div class="stat-value">{{ stats.pending_maintenance_count || 0 }}</div>
        </div>
      </div>
    </div>

    <!-- Overtime Alerts -->
    <div v-if="hasOvertimeAlerts" class="overtime-section">
      <div class="section-header alert">
        <span class="icon">⚠️</span>
        <h2 class="section-title">แจ้งเตือนเกินเวลา ({{ overtimeAlerts.length }})</h2>
      </div>
      <div class="alert-list">
        <div
          v-for="alert in overtimeAlerts"
          :key="alert.room_id"
          class="alert-item"
          @click="handleAlertClick(alert)"
        >
          <div class="alert-room">ห้อง {{ alert.room_number }}</div>
          <div class="alert-details">
            <span class="customer">{{ alert.customer_name }}</span>
            <span class="type">{{ alert.stay_type === 'OVERNIGHT' ? 'ค้างคืน' : 'ชั่วคราว' }}</span>
          </div>
          <div class="alert-time">เกินเวลา {{ alert.overtime_minutes }} นาที</div>
        </div>
      </div>
    </div>

    <!-- Room Status Filter -->
    <div class="filter-section">
      <div class="filter-buttons">
        <button
          v-for="status in roomStatuses"
          :key="status.value"
          class="filter-btn"
          :class="{ active: selectedStatus === status.value }"
          @click="selectedStatus = status.value"
        >
          <span class="icon">{{ status.icon }}</span>
          <span class="label">{{ status.label }}</span>
          <span class="count">({{ getRoomCountByStatus(status.value) }})</span>
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading && rooms.length === 0" class="loading-section">
      <div class="spinner"></div>
      <p>กำลังโหลดข้อมูล...</p>
    </div>

    <!-- Room Grid -->
    <div v-else class="room-grid">
      <RoomCard
        v-for="room in filteredRooms"
        :key="room.id"
        :room="room"
        @click="handleRoomClick"
        @checkIn="handleCheckInClick"
        @checkOut="handleCheckOutClick"
        @transfer="handleTransferClick"
        @cancelBooking="handleCancelBookingClick"
        @completeHousekeeping="handleCompleteHousekeepingClick"
      />
    </div>

    <!-- Empty State -->
    <div v-if="!isLoading && filteredRooms.length === 0" class="empty-state">
      <span class="icon">🏨</span>
      <p>ไม่มีห้องที่ตรงกับตัวกรอง</p>
    </div>

    <!-- Notification Panel (Slide-in) -->
    <transition name="slide">
      <div v-if="showNotificationPanel" class="notification-overlay" @click="toggleNotificationPanel">
        <div class="notification-container" @click.stop>
          <NotificationPanel @notificationClick="handleNotificationClick" />
        </div>
      </div>
    </transition>

    <!-- Check-In Modal -->
    <CheckInModal
      v-if="selectedRoom"
      :show="showCheckInModal"
      :roomId="selectedRoom.id"
      :roomNumber="selectedRoom.room_number"
      :ratePerNight="ratePerNight"
      :ratePerSession="ratePerSession"
      :bookingId="selectedRoom.booking_id"
      :bookingCustomerName="selectedRoom.booking_customer_name"
      :bookingCustomerPhone="selectedRoom.booking_customer_phone"
      :bookingCheckInDate="selectedRoom.booking_check_in_date"
      :bookingCheckOutDate="selectedRoom.booking_check_out_date"
      :bookingDepositAmount="selectedRoom.booking_deposit_amount"
      @close="closeCheckInModal"
      @success="handleCheckInSuccess"
    />

    <!-- Check-Out Modal -->
    <CheckOutModal
      :show="showCheckOutModal"
      :checkInId="selectedRoom?.check_in_id || 0"
      @close="closeCheckOutModal"
      @success="handleCheckOutSuccess"
    />

    <!-- Room Transfer Modal -->
    <RoomTransferModal
      :show="showTransferModal"
      :currentRoom="selectedRoom"
      :checkInId="selectedRoom?.check_in_id || null"
      @update:show="showTransferModal = $event"
      @success="handleTransferSuccess"
    />

    <!-- Housekeeping Quick Complete Modal -->
    <HousekeepingQuickCompleteModal
      :show="showHousekeepingCompleteModal"
      :roomId="selectedRoom?.id || null"
      @update:show="showHousekeepingCompleteModal = $event"
      @completed="handleHousekeepingCompleted"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useDashboardStore } from '@/stores/dashboard'
import { useNotificationStore } from '@/stores/notification'
import { useRoomStore } from '@/stores/room'
import { useBookingStore } from '@/stores/booking'
import { storeToRefs } from 'pinia'
import { useWebSocket } from '@/composables/useWebSocket'
import RoomCard from '@/components/RoomCard.vue'
import NotificationPanel from '@/components/NotificationPanel.vue'
import CheckInModal from '@/components/CheckInModal.vue'
import CheckOutModal from '@/components/CheckOutModal.vue'
import RoomTransferModal from '@/components/RoomTransferModal.vue'
import HousekeepingQuickCompleteModal from '@/components/HousekeepingQuickCompleteModal.vue'
import type { DashboardRoomCard, OvertimeAlert } from '@/types/dashboard'
import type { Notification } from '@/types/notification'
import dayjs from 'dayjs'
import 'dayjs/locale/th'

dayjs.locale('th')

// Stores
const dashboardStore = useDashboardStore()
const notificationStore = useNotificationStore()
const roomStore = useRoomStore()
const bookingStore = useBookingStore()

const {
  rooms,
  stats,
  overtimeAlerts,
  lastUpdated,
  isLoading,
  hasOvertimeAlerts
} = storeToRefs(dashboardStore)

const { unreadCount, hasUnread } = storeToRefs(notificationStore)

const { rateMatrix } = storeToRefs(roomStore)

// WebSocket
const { isConnected, on } = useWebSocket()

// Local State
const selectedStatus = ref<string | null>(null)
const showNotificationPanel = ref(false)
const showCheckInModal = ref(false)
const showCheckOutModal = ref(false)
const showTransferModal = ref(false)
const showHousekeepingCompleteModal = ref(false)
const selectedRoom = ref<DashboardRoomCard | null>(null)

// Get room rates based on selected room
const ratePerNight = computed(() => {
  if (!selectedRoom.value) return 0
  const matrix = rateMatrix.value.find(m => m.room_type_id === selectedRoom.value!.room_type_id)
  return matrix?.overnight_rate || 0
})

const ratePerSession = computed(() => {
  if (!selectedRoom.value) return 0
  const matrix = rateMatrix.value.find(m => m.room_type_id === selectedRoom.value!.room_type_id)
  return matrix?.temporary_rate || 0
})

// Room Status Options (UPPERCASE to match backend)
const roomStatuses = [
  { value: null, label: 'ทั้งหมด', icon: '🏨' },
  { value: 'AVAILABLE', label: 'ว่าง', icon: '✅' },
  { value: 'OCCUPIED', label: 'มีผู้เข้าพัก', icon: '🛏️' },
  { value: 'CLEANING', label: 'ทำความสะอาด', icon: '🧹' },
  { value: 'RESERVED', label: 'จอง', icon: '📅' },
  { value: 'OUT_OF_SERVICE', label: 'ไม่พร้อมใช้', icon: '⚠️' }
]

// Computed
const filteredRooms = computed(() => {
  if (!selectedStatus.value) {
    return rooms.value
  }
  return rooms.value.filter(room => room.status === selectedStatus.value)
})

// Methods
async function handleRefresh(): Promise<void> {
  try {
    await dashboardStore.refresh()
  } catch (error) {
    console.error('Error refreshing dashboard:', error)
  }
}

function handleRoomClick(room: DashboardRoomCard): void {
  console.log('Room clicked:', room)
  // General room click - could show room details in future
}

async function handleCheckInClick(room: DashboardRoomCard): Promise<void> {
  selectedRoom.value = room

  // Phase 7: For reserved rooms, booking data is already in the room object
  // No need to fetch separately
  showCheckInModal.value = true
}

async function handleCancelBookingClick(room: DashboardRoomCard): Promise<void> {
  if (!room.booking_id) {
    console.error('No booking ID found for room:', room)
    return
  }

  // Confirm cancellation
  const confirmed = window.confirm(
    `ยืนยันการยกเลิกการจองห้อง ${room.room_number}?\n\n` +
    `ผู้จอง: ${room.booking_customer_name}\n` +
    `เข้าพัก: ${room.booking_check_in_date} - ${room.booking_check_out_date}\n` +
    `มัดจำ: ฿${room.booking_deposit_amount?.toLocaleString('th-TH', { minimumFractionDigits: 2 }) || '0.00'}\n\n` +
    `หมายเหตุ: เงินมัดจำจะไม่สามารถคืนได้`
  )

  if (!confirmed) {
    return
  }

  try {
    await bookingStore.cancelBooking(room.booking_id)

    // Refresh dashboard to show updated room status
    await dashboardStore.refresh()

    alert(`ยกเลิกการจองห้อง ${room.room_number} สำเร็จ`)
  } catch (error: any) {
    console.error('Error cancelling booking:', error)
    alert(`เกิดข้อผิดพลาดในการยกเลิกการจอง: ${error.message || 'Unknown error'}`)
  }
}

function handleCheckOutClick(room: DashboardRoomCard): void {
  selectedRoom.value = room
  showCheckOutModal.value = true
}

function handleTransferClick(room: DashboardRoomCard): void {
  selectedRoom.value = room
  showTransferModal.value = true
}

function closeCheckInModal(): void {
  showCheckInModal.value = false
  selectedRoom.value = null
}

function closeCheckOutModal(): void {
  showCheckOutModal.value = false
  selectedRoom.value = null
}

async function handleCheckInSuccess(checkInId: number): Promise<void> {
  console.log('Check-in successful:', checkInId)
  // Refresh dashboard to show updated room status
  await dashboardStore.refresh()
}

async function handleCheckOutSuccess(): Promise<void> {
  console.log('Check-out successful')
  // Refresh dashboard to show updated room status
  await dashboardStore.refresh()
}

async function handleTransferSuccess(): Promise<void> {
  console.log('Room transfer successful')
  // Refresh dashboard to show updated room statuses
  await dashboardStore.refresh()
}

function handleCompleteHousekeepingClick(room: DashboardRoomCard): void {
  selectedRoom.value = room
  showHousekeepingCompleteModal.value = true
}

async function handleHousekeepingCompleted(): Promise<void> {
  console.log('Housekeeping task completed')
  // Refresh dashboard to show updated room status (should change from CLEANING to AVAILABLE)
  await dashboardStore.refresh()
  selectedRoom.value = null
}

function handleAlertClick(alert: OvertimeAlert): void {
  console.log('Alert clicked:', alert)
  // Find the room and open checkout modal
  const room = rooms.value.find(r => r.id === alert.room_id)
  if (room) {
    handleCheckOutClick(room)
  }
}

function handleNotificationClick(notification: Notification): void {
  console.log('Notification clicked:', notification)
  toggleNotificationPanel()
  // TODO: Handle navigation based on notification type
}

function toggleNotificationPanel(): void {
  showNotificationPanel.value = !showNotificationPanel.value
}

function getRoomCountByStatus(status: string | null): number {
  if (!status) {
    return rooms.value.length
  }
  return rooms.value.filter(room => room.status === status).length
}

function formatLastUpdated(time: string): string {
  return dayjs(time).format('HH:mm:ss')
}

function formatCurrency(value: string | number): string {
  const num = typeof value === 'string' ? parseFloat(value) : value
  return num.toLocaleString('th-TH', { minimumFractionDigits: 2 })
}

// WebSocket Event Handlers
function setupWebSocketHandlers(): void {
  // Room status changed
  on('room_status_changed', (data) => {
    console.log('Room status changed:', data)
    dashboardStore.handleRoomStatusChange(data)
  })

  // Overtime alert
  on('overtime_alert', (data) => {
    console.log('Overtime alert:', data)
    dashboardStore.handleOvertimeAlert(data)
  })

  // Check-in
  on('check_in', (data) => {
    console.log('Check-in event:', data)
    dashboardStore.handleCheckIn(data)
  })

  // Check-out
  on('check_out', (data) => {
    console.log('Check-out event:', data)
    dashboardStore.handleCheckOut(data)
  })

  // Room transfer
  on('room_transferred', (data) => {
    console.log('Room transferred event:', data)
    dashboardStore.handleRoomTransfer(data)
  })

  // Notification
  on('notification', (data) => {
    console.log('New notification:', data)
    notificationStore.handleNewNotification(data)
  })
}

// Lifecycle
onMounted(async () => {
  // Fetch initial data
  await Promise.all([
    dashboardStore.fetchDashboard(),
    dashboardStore.fetchOvertimeAlerts(),
    dashboardStore.fetchMaintenanceStats(),
    notificationStore.fetchUnreadCount(),
    roomStore.fetchRateMatrix() // Load room rates
  ])

  // Setup WebSocket handlers
  setupWebSocketHandlers()

  // Request notification permission
  notificationStore.requestNotificationPermission()
})

onUnmounted(() => {
  // Cleanup if needed
})
</script>

<style scoped>
.dashboard-view {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 24px;
}

/* Header */
.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  background: white;
  padding: 24px;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.header-content {
  flex: 1;
}

.title {
  font-size: 28px;
  font-weight: 700;
  margin: 0 0 8px 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.header-info {
  display: flex;
  gap: 16px;
  align-items: center;
  font-size: 14px;
  color: #666;
}

.connection-status {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  border-radius: 12px;
  background: #f5f5f5;
}

.connection-status.connected {
  background: #e8f5e9;
  color: #2e7d32;
}

.connection-status .dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #999;
}

.connection-status.connected .dot {
  background: #4caf50;
  animation: pulse-dot 2s infinite;
}

@keyframes pulse-dot {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.header-actions {
  display: flex;
  gap: 12px;
}

.btn-refresh,
.btn-notifications {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border: none;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
  position: relative;
}

.btn-refresh:hover,
.btn-notifications:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-refresh:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-notifications .badge {
  position: absolute;
  top: -6px;
  right: -6px;
  background: #ff4444;
  color: white;
  font-size: 11px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 10px;
  min-width: 20px;
  text-align: center;
}

/* Statistics Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.stat-icon {
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* Stat Card Colors */
.stat-card.total .stat-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-card.available .stat-icon {
  background: linear-gradient(135deg, #4CAF50 0%, #66BB6A 100%);
}

.stat-card.overnight .stat-icon {
  background: linear-gradient(135deg, #2196F3 0%, #42A5F5 100%);
}

.stat-card.temporary .stat-icon {
  background: linear-gradient(135deg, #FF9800 0%, #FFB74D 100%);
}

.stat-card.cleaning .stat-icon {
  background: linear-gradient(135deg, #FFC107 0%, #FFD54F 100%);
}

.stat-card.maintenance .stat-icon {
  background: linear-gradient(135deg, #F44336 0%, #EF5350 100%);
}

.stat-content {
  flex: 1;
}

.stat-label {
  font-size: 13px;
  color: #666;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #333;
}

/* Overtime Section */
.overtime-section {
  background: #fff3cd;
  border: 2px solid #ffc107;
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 24px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.section-header .icon {
  font-size: 24px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}

.alert-list {
  display: grid;
  gap: 12px;
}

.alert-item {
  background: white;
  border-radius: 12px;
  padding: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.alert-item:hover {
  transform: translateX(4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.alert-room {
  font-size: 18px;
  font-weight: 700;
  color: #333;
}

.alert-details {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-left: 16px;
}

.alert-time {
  font-size: 14px;
  font-weight: 600;
  color: #f57c00;
}

/* Filter Section */
.filter-section {
  background: white;
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.filter-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.filter-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  background: white;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
}

.filter-btn:hover {
  border-color: #667eea;
  background: #f5f7ff;
}

.filter-btn.active {
  border-color: #667eea;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.filter-btn .count {
  opacity: 0.7;
  font-size: 12px;
}

/* Loading Section */
.loading-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  color: #666;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Room Grid */
.room-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  background: white;
  border-radius: 16px;
  color: #999;
}

.empty-state .icon {
  font-size: 64px;
  margin-bottom: 16px;
  opacity: 0.5;
}

/* Notification Overlay */
.notification-overlay {
  position: fixed;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1000;
  display: flex;
  justify-content: flex-end;
}

.notification-container {
  width: 400px;
  max-width: 90vw;
  background: white;
  box-shadow: -4px 0 20px rgba(0, 0, 0, 0.2);
}

/* Slide Transition */
.slide-enter-active,
.slide-leave-active {
  transition: opacity 0.3s ease;
}

.slide-enter-from,
.slide-leave-to {
  opacity: 0;
}

.slide-enter-active .notification-container,
.slide-leave-active .notification-container {
  transition: transform 0.3s ease;
}

.slide-enter-from .notification-container,
.slide-leave-to .notification-container {
  transform: translateX(100%);
}

/* Responsive */
@media (max-width: 768px) {
  .dashboard-view {
    padding: 16px;
  }

  .dashboard-header {
    flex-direction: column;
    gap: 16px;
  }

  .header-actions {
    width: 100%;
    justify-content: flex-end;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .room-grid {
    grid-template-columns: 1fr;
  }

  .filter-buttons {
    flex-direction: column;
  }

  .filter-btn {
    width: 100%;
    justify-content: space-between;
  }
}
</style>
