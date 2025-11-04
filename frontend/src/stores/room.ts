/**
 * Room Management Store (Phase 2)
 * Manages state for room types, rooms, and room rates
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  RoomType,
  RoomTypeWithStats,
  RoomTypeFormData,
  Room,
  RoomFormData,
  RoomRate,
  RoomRateFormData,
  RoomRateMatrix,
  RoomStatus,
  StayType
} from '@/types/room'
import { roomTypesApi, roomsApi, roomRatesApi } from '@/api/rooms'

export const useRoomStore = defineStore('room', () => {
  // State
  const roomTypes = ref<RoomType[]>([])
  const rooms = ref<Room[]>([])
  const roomRates = ref<RoomRate[]>([])
  const rateMatrix = ref<RoomRateMatrix[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const activeRoomTypes = computed(() =>
    roomTypes.value.filter(rt => rt.is_active)
  )

  const availableRooms = computed(() =>
    rooms.value.filter(r => r.status === 'AVAILABLE' && r.is_active)
  )

  const roomsByFloor = computed(() => {
    const grouped = new Map<number, Room[]>()
    rooms.value.forEach(room => {
      if (!grouped.has(room.floor)) {
        grouped.set(room.floor, [])
      }
      grouped.get(room.floor)!.push(room)
    })
    return grouped
  })

  const roomsByStatus = computed(() => {
    const grouped = new Map<RoomStatus, Room[]>()
    rooms.value.forEach(room => {
      if (!grouped.has(room.status)) {
        grouped.set(room.status, [])
      }
      grouped.get(room.status)!.push(room)
    })
    return grouped
  })

  // Helper function to handle errors
  const handleError = (err: any, defaultMessage: string) => {
    error.value = err.response?.data?.detail || defaultMessage
    console.error('Store error:', err)
    throw err
  }

  // Room Types Actions
  const fetchRoomTypes = async (params?: { skip?: number; limit?: number; is_active?: boolean }) => {
    isLoading.value = true
    error.value = null
    try {
      const response = await roomTypesApi.getAll(params)
      roomTypes.value = response.data
    } catch (err: any) {
      handleError(err, 'เกิดข้อผิดพลาดในการดึงข้อมูลประเภทห้อง')
    } finally {
      isLoading.value = false
    }
  }

  const createRoomType = async (data: RoomTypeFormData) => {
    isLoading.value = true
    error.value = null
    try {
      const response = await roomTypesApi.create(data)
      roomTypes.value.push(response.data)
      return response.data
    } catch (err: any) {
      handleError(err, 'เกิดข้อผิดพลาดในการสร้างประเภทห้อง')
    } finally {
      isLoading.value = false
    }
  }

  const updateRoomType = async (id: number, data: Partial<RoomTypeFormData>) => {
    isLoading.value = true
    error.value = null
    try {
      const response = await roomTypesApi.update(id, data)
      const index = roomTypes.value.findIndex(rt => rt.id === id)
      if (index !== -1) {
        roomTypes.value[index] = response.data
      }
      return response.data
    } catch (err: any) {
      handleError(err, 'เกิดข้อผิดพลาดในการแก้ไขประเภทห้อง')
    } finally {
      isLoading.value = false
    }
  }

  const deleteRoomType = async (id: number) => {
    isLoading.value = true
    error.value = null
    try {
      await roomTypesApi.delete(id)
      roomTypes.value = roomTypes.value.filter(rt => rt.id !== id)
    } catch (err: any) {
      handleError(err, 'เกิดข้อผิดพลาดในการลบประเภทห้อง')
    } finally {
      isLoading.value = false
    }
  }

  // Rooms Actions
  const fetchRooms = async (params?: {
    skip?: number
    limit?: number
    floor?: number
    status?: RoomStatus
    room_type_id?: number
    is_active?: boolean
  }) => {
    isLoading.value = true
    error.value = null
    try {
      const response = await roomsApi.getAll(params)
      rooms.value = response.data
    } catch (err: any) {
      handleError(err, 'เกิดข้อผิดพลาดในการดึงข้อมูลห้องพัก')
    } finally {
      isLoading.value = false
    }
  }

  const fetchAvailableRooms = async (roomTypeId?: number) => {
    isLoading.value = true
    error.value = null
    try {
      const response = await roomsApi.getAvailable(roomTypeId)
      return response.data
    } catch (err: any) {
      handleError(err, 'เกิดข้อผิดพลาดในการดึงข้อมูลห้องว่าง')
    } finally {
      isLoading.value = false
    }
  }

  const fetchRoomsByFloor = async (floor: number) => {
    isLoading.value = true
    error.value = null
    try {
      const response = await roomsApi.getByFloor(floor)
      return response.data
    } catch (err: any) {
      handleError(err, 'เกิดข้อผิดพลาดในการดึงข้อมูลห้องพัก')
    } finally {
      isLoading.value = false
    }
  }

  const createRoom = async (data: RoomFormData) => {
    isLoading.value = true
    error.value = null
    try {
      const response = await roomsApi.create(data)
      rooms.value.push(response.data)
      return response.data
    } catch (err: any) {
      handleError(err, 'เกิดข้อผิดพลาดในการสร้างห้องพัก')
    } finally {
      isLoading.value = false
    }
  }

  const updateRoom = async (id: number, data: Partial<RoomFormData>) => {
    isLoading.value = true
    error.value = null
    try {
      const response = await roomsApi.update(id, data)
      const index = rooms.value.findIndex(r => r.id === id)
      if (index !== -1) {
        rooms.value[index] = response.data
      }
      return response.data
    } catch (err: any) {
      handleError(err, 'เกิดข้อผิดพลาดในการแก้ไขห้องพัก')
    } finally {
      isLoading.value = false
    }
  }

  const updateRoomStatus = async (id: number, status: RoomStatus) => {
    isLoading.value = true
    error.value = null
    try {
      const response = await roomsApi.updateStatus(id, status)
      const index = rooms.value.findIndex(r => r.id === id)
      if (index !== -1) {
        rooms.value[index] = response.data
      }
      return response.data
    } catch (err: any) {
      handleError(err, 'เกิดข้อผิดพลาดในการอัปเดตสถานะห้อง')
    } finally {
      isLoading.value = false
    }
  }

  const deleteRoom = async (id: number) => {
    isLoading.value = true
    error.value = null
    try {
      await roomsApi.delete(id)
      rooms.value = rooms.value.filter(r => r.id !== id)
    } catch (err: any) {
      handleError(err, 'เกิดข้อผิดพลาดในการลบห้องพัก')
    } finally {
      isLoading.value = false
    }
  }

  // Room Rates Actions
  const fetchRoomRates = async (params?: {
    skip?: number
    limit?: number
    room_type_id?: number
    stay_type?: StayType
    is_active?: boolean
  }) => {
    isLoading.value = true
    error.value = null
    try {
      const response = await roomRatesApi.getAll(params)
      roomRates.value = response.data
    } catch (err: any) {
      handleError(err, 'เกิดข้อผิดพลาดในการดึงข้อมูลราคาห้อง')
    } finally {
      isLoading.value = false
    }
  }

  const fetchRateMatrix = async () => {
    isLoading.value = true
    error.value = null
    try {
      const response = await roomRatesApi.getMatrix()
      rateMatrix.value = response.data
    } catch (err: any) {
      handleError(err, 'เกิดข้อผิดพลาดในการดึงข้อมูลราคาห้อง')
    } finally {
      isLoading.value = false
    }
  }

  const createRoomRate = async (data: RoomRateFormData) => {
    isLoading.value = true
    error.value = null
    try {
      const response = await roomRatesApi.create(data)
      roomRates.value.push(response.data)
      return response.data
    } catch (err: any) {
      handleError(err, 'เกิดข้อผิดพลาดในการสร้างราคาห้อง')
    } finally {
      isLoading.value = false
    }
  }

  const updateRoomRate = async (id: number, data: Partial<RoomRateFormData>) => {
    isLoading.value = true
    error.value = null
    try {
      const response = await roomRatesApi.update(id, data)
      const index = roomRates.value.findIndex(rr => rr.id === id)
      if (index !== -1) {
        roomRates.value[index] = response.data
      }
      return response.data
    } catch (err: any) {
      handleError(err, 'เกิดข้อผิดพลาดในการแก้ไขราคาห้อง')
    } finally {
      isLoading.value = false
    }
  }

  const deleteRoomRate = async (id: number) => {
    isLoading.value = true
    error.value = null
    try {
      await roomRatesApi.delete(id)
      roomRates.value = roomRates.value.filter(rr => rr.id !== id)
    } catch (err: any) {
      handleError(err, 'เกิดข้อผิดพลาดในการลบราคาห้อง')
    } finally {
      isLoading.value = false
    }
  }

  const clearError = () => {
    error.value = null
  }

  return {
    // State
    roomTypes,
    rooms,
    roomRates,
    rateMatrix,
    isLoading,
    error,
    // Getters
    activeRoomTypes,
    availableRooms,
    roomsByFloor,
    roomsByStatus,
    // Actions - Room Types
    fetchRoomTypes,
    createRoomType,
    updateRoomType,
    deleteRoomType,
    // Actions - Rooms
    fetchRooms,
    fetchAvailableRooms,
    fetchRoomsByFloor,
    createRoom,
    updateRoom,
    updateRoomStatus,
    deleteRoom,
    // Actions - Room Rates
    fetchRoomRates,
    fetchRateMatrix,
    createRoomRate,
    updateRoomRate,
    deleteRoomRate,
    // Utilities
    clearError
  }
})
