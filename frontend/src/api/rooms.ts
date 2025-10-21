/**
 * Room Management API Client (Phase 2)
 */
import axios from './client'
import type {
  RoomType,
  RoomTypeWithStats,
  RoomTypeFormData,
  Room,
  RoomFormData,
  RoomStatusFormData,
  RoomRate,
  RoomRateFormData,
  RoomRateMatrix,
  RoomStatus,
  StayType
} from '@/types/room'

// Room Types API
export const roomTypesApi = {
  /**
   * Get all room types
   */
  getAll: (params?: { skip?: number; limit?: number; is_active?: boolean }) =>
    axios.get<RoomType[]>('/api/v1/room-types/', { params }),

  /**
   * Get room type by ID
   */
  getById: (id: number) =>
    axios.get<RoomType>(`/api/v1/room-types/${id}`),

  /**
   * Get room type with statistics
   */
  getWithStats: (id: number) =>
    axios.get<RoomTypeWithStats>(`/api/v1/room-types/${id}/stats`),

  /**
   * Create new room type (Admin only)
   */
  create: (data: RoomTypeFormData) =>
    axios.post<RoomType>('/api/v1/room-types/', data),

  /**
   * Update room type (Admin only)
   */
  update: (id: number, data: Partial<RoomTypeFormData>) =>
    axios.patch<RoomType>(`/api/v1/room-types/${id}`, data),

  /**
   * Delete room type (Admin only)
   */
  delete: (id: number) =>
    axios.delete(`/api/v1/room-types/${id}`)
}

// Rooms API
export const roomsApi = {
  /**
   * Get all rooms with filters
   */
  getAll: (params?: {
    skip?: number
    limit?: number
    floor?: number
    status?: RoomStatus
    room_type_id?: number
    is_active?: boolean
  }) =>
    axios.get<Room[]>('/api/v1/rooms/', { params }),

  /**
   * Get available rooms
   */
  getAvailable: (roomTypeId?: number) =>
    axios.get<Room[]>('/api/v1/rooms/available', {
      params: roomTypeId ? { room_type_id: roomTypeId } : undefined
    }),

  /**
   * Get rooms by floor
   */
  getByFloor: (floor: number) =>
    axios.get<Room[]>(`/api/v1/rooms/floor/${floor}`),

  /**
   * Get room by ID
   */
  getById: (id: number) =>
    axios.get<Room>(`/api/v1/rooms/${id}`),

  /**
   * Create new room (Admin only)
   */
  create: (data: RoomFormData) =>
    axios.post<Room>('/api/v1/rooms/', data),

  /**
   * Update room (Admin only)
   */
  update: (id: number, data: Partial<RoomFormData>) =>
    axios.patch<Room>(`/api/v1/rooms/${id}`, data),

  /**
   * Update room status (Admin, Reception, Housekeeping)
   */
  updateStatus: (id: number, status: RoomStatus) =>
    axios.patch<Room>(`/api/v1/rooms/${id}/status`, { status }),

  /**
   * Delete room (Admin only)
   */
  delete: (id: number) =>
    axios.delete(`/api/v1/rooms/${id}`)
}

// Room Rates API
export const roomRatesApi = {
  /**
   * Get all room rates with filters
   */
  getAll: (params?: {
    skip?: number
    limit?: number
    room_type_id?: number
    stay_type?: StayType
    is_active?: boolean
  }) =>
    axios.get<RoomRate[]>('/api/v1/room-rates/', { params }),

  /**
   * Get rate matrix for UI display
   */
  getMatrix: () =>
    axios.get<RoomRateMatrix[]>('/api/v1/room-rates/matrix'),

  /**
   * Get current rate for specific room type and stay type
   */
  getCurrent: (roomTypeId: number, stayType: StayType, checkDate?: string) =>
    axios.get<RoomRate>('/api/v1/room-rates/current', {
      params: {
        room_type_id: roomTypeId,
        stay_type: stayType,
        check_date: checkDate
      }
    }),

  /**
   * Get room rate by ID
   */
  getById: (id: number) =>
    axios.get<RoomRate>(`/api/v1/room-rates/${id}`),

  /**
   * Create new room rate (Admin only)
   */
  create: (data: RoomRateFormData) =>
    axios.post<RoomRate>('/api/v1/room-rates/', data),

  /**
   * Update room rate (Admin only)
   */
  update: (id: number, data: Partial<RoomRateFormData>) =>
    axios.patch<RoomRate>(`/api/v1/room-rates/${id}`, data),

  /**
   * Delete room rate (Admin only)
   */
  delete: (id: number) =>
    axios.delete(`/api/v1/room-rates/${id}`)
}
