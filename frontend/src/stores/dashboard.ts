/**
 * Dashboard Store (Phase 3)
 * State management for dashboard data
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { dashboardApi } from '@/api/dashboard'
import { maintenanceApi } from '@/api/maintenance'
import type {
  DashboardRoomCard,
  DashboardStats,
  OvertimeAlert
} from '@/types/dashboard'
import type { WebSocketMessage, RoomStatusChangedEventData } from '@/types/websocket'

export const useDashboardStore = defineStore('dashboard', () => {
  // State
  const rooms = ref<DashboardRoomCard[]>([])
  const stats = ref<DashboardStats | null>(null)
  const overtimeAlerts = ref<OvertimeAlert[]>([])
  const lastUpdated = ref<string | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Computed
  const availableRooms = computed(() =>
    rooms.value.filter(room => room.status === 'AVAILABLE')
  )

  const occupiedRooms = computed(() =>
    rooms.value.filter(room => room.status === 'OCCUPIED')
  )

  const cleaningRooms = computed(() =>
    rooms.value.filter(room => room.status === 'CLEANING')
  )

  const reservedRooms = computed(() =>
    rooms.value.filter(room => room.status === 'RESERVED')
  )

  const outOfServiceRooms = computed(() =>
    rooms.value.filter(room => room.status === 'OUT_OF_SERVICE')
  )

  const overtimeRooms = computed(() =>
    rooms.value.filter(room => room.is_overtime)
  )

  const hasOvertimeAlerts = computed(() => overtimeAlerts.value.length > 0)

  const occupancyRate = computed(() => stats.value?.occupancy_rate || 0)

  // Actions
  async function fetchDashboard(): Promise<void> {
    try {
      isLoading.value = true
      error.value = null

      const response = await dashboardApi.getDashboard()

      rooms.value = response.rooms
      stats.value = response.stats
      lastUpdated.value = response.last_updated
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'ไม่สามารถโหลดข้อมูล Dashboard ได้'
      console.error('Error fetching dashboard:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function fetchRooms(): Promise<void> {
    try {
      isLoading.value = true
      error.value = null

      const data = await dashboardApi.getRooms()
      rooms.value = data
      lastUpdated.value = new Date().toISOString()
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'ไม่สามารถโหลดข้อมูลห้องได้'
      console.error('Error fetching rooms:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function fetchStats(): Promise<void> {
    try {
      error.value = null

      const data = await dashboardApi.getStats()
      stats.value = data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'ไม่สามารถโหลดสถิติได้'
      console.error('Error fetching stats:', err)
      throw err
    }
  }

  async function fetchOvertimeAlerts(): Promise<void> {
    try {
      error.value = null

      const response = await dashboardApi.getOvertimeAlerts()
      overtimeAlerts.value = response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'ไม่สามารถโหลดรายการเกินเวลาได้'
      console.error('Error fetching overtime alerts:', err)
      throw err
    }
  }

  async function fetchMaintenanceStats(): Promise<void> {
    try {
      error.value = null

      const maintenanceStats = await maintenanceApi.getStats()

      // Add pending maintenance count to stats
      if (stats.value) {
        stats.value.pending_maintenance_count =
          maintenanceStats.pending_tasks + maintenanceStats.in_progress_tasks
      }
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'ไม่สามารถโหลดข้อมูลงานซ่อมได้'
      console.error('Error fetching maintenance stats:', err)
      // Don't throw - maintenance stats is optional
    }
  }

  /**
   * Handle room status change from WebSocket
   */
  function handleRoomStatusChange(data: RoomStatusChangedEventData): void {
    console.log('Room status change event received:', data)

    // Refresh rooms to get updated status and check-in info
    // This ensures customer data is always up-to-date
    fetchRooms()
    fetchStats()

    // Update last updated time
    lastUpdated.value = new Date().toISOString()
  }

  /**
   * Handle overtime alert from WebSocket
   */
  function handleOvertimeAlert(alert: OvertimeAlert): void {
    // Check if alert already exists
    const existingIndex = overtimeAlerts.value.findIndex(
      a => a.room_id === alert.room_id
    )

    if (existingIndex !== -1) {
      // Update existing alert
      overtimeAlerts.value[existingIndex] = alert
    } else {
      // Add new alert
      overtimeAlerts.value.push(alert)
    }

    // Update room overtime status
    const roomIndex = rooms.value.findIndex(room => room.id === alert.room_id)
    if (roomIndex !== -1) {
      rooms.value[roomIndex].is_overtime = true
      rooms.value[roomIndex].overtime_minutes = alert.overtime_minutes
    }
  }

  /**
   * Handle check-in event from WebSocket
   */
  function handleCheckIn(data: any): void {
    // Refresh rooms to get updated check-in info
    fetchRooms()
    fetchStats()
  }

  /**
   * Handle check-out event from WebSocket
   */
  function handleCheckOut(data: any): void {
    // Refresh rooms to get updated status
    fetchRooms()
    fetchStats()

    // Remove overtime alert if exists
    overtimeAlerts.value = overtimeAlerts.value.filter(
      alert => alert.room_id !== data.room_id
    )
  }

  /**
   * Get room by ID
   */
  function getRoomById(roomId: number): DashboardRoomCard | undefined {
    return rooms.value.find(room => room.id === roomId)
  }

  /**
   * Get room by room number
   */
  function getRoomByNumber(roomNumber: string): DashboardRoomCard | undefined {
    return rooms.value.find(room => room.room_number === roomNumber)
  }

  /**
   * Clear error message
   */
  function clearError(): void {
    error.value = null
  }

  /**
   * Handle room transfer event from WebSocket
   */
  function handleRoomTransfer(data: any): void {
    console.log('Room transfer event received:', data)

    // Refresh rooms to get updated status
    fetchRooms()
    fetchStats()
  }

  /**
   * Refresh all dashboard data
   */
  async function refresh(): Promise<void> {
    await fetchDashboard()
    await Promise.all([
      fetchOvertimeAlerts(),
      fetchMaintenanceStats()
    ])
  }

  return {
    // State
    rooms,
    stats,
    overtimeAlerts,
    lastUpdated,
    isLoading,
    error,

    // Computed
    availableRooms,
    occupiedRooms,
    cleaningRooms,
    reservedRooms,
    outOfServiceRooms,
    overtimeRooms,
    hasOvertimeAlerts,
    occupancyRate,

    // Actions
    fetchDashboard,
    fetchRooms,
    fetchStats,
    fetchOvertimeAlerts,
    fetchMaintenanceStats,
    handleRoomStatusChange,
    handleOvertimeAlert,
    handleCheckIn,
    handleCheckOut,
    handleRoomTransfer,
    getRoomById,
    getRoomByNumber,
    clearError,
    refresh
  }
})
