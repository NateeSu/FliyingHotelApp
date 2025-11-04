/**
 * Room Management Types (Phase 2)
 */

// Enums
export enum RoomStatus {
  AVAILABLE = 'AVAILABLE',
  OCCUPIED = 'OCCUPIED',
  CLEANING = 'CLEANING',
  RESERVED = 'RESERVED',
  OUT_OF_SERVICE = 'OUT_OF_SERVICE'
}

export enum StayType {
  OVERNIGHT = 'OVERNIGHT',
  TEMPORARY = 'TEMPORARY'
}

// Room Type Interfaces
export interface RoomType {
  id: number
  name: string
  description?: string
  amenities?: string[]
  max_guests: number
  bed_type?: string
  room_size_sqm?: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface RoomTypeWithStats extends RoomType {
  total_rooms: number
  available_rooms: number
}

// Room Interfaces
export interface Room {
  id: number
  room_number: string
  room_type_id: number
  room_type?: RoomType
  floor: number
  status: RoomStatus
  qr_code?: string
  notes?: string
  is_active: boolean
  created_at: string
  updated_at: string
}

// Room Rate Interfaces
export interface RoomRate {
  id: number
  room_type_id: number
  room_type?: RoomType
  stay_type: StayType
  rate: number
  effective_from: string
  effective_to?: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface RoomRateMatrix {
  room_type_id: number
  room_type_name: string
  overnight_rate?: number
  temporary_rate?: number
  overnight_rate_id?: number
  temporary_rate_id?: number
}

// Form Data Interfaces
export interface RoomTypeFormData {
  name: string
  description?: string
  amenities?: string[]
  max_guests: number
  bed_type?: string
  room_size_sqm?: number
  is_active: boolean
}

export interface RoomFormData {
  room_number: string
  room_type_id: number
  floor: number
  notes?: string
  is_active: boolean
}

export interface RoomStatusFormData {
  status: RoomStatus
}

export interface RoomRateFormData {
  room_type_id: number
  stay_type: StayType
  rate: number
  effective_from: string
  effective_to?: string
  is_active: boolean
}

// Helper functions
export function getRoomStatusLabel(status: RoomStatus): string {
  const labels: Record<RoomStatus, string> = {
    [RoomStatus.AVAILABLE]: 'ว่าง',
    [RoomStatus.OCCUPIED]: 'มีผู้พัก',
    [RoomStatus.CLEANING]: 'กำลังทำความสะอาด',
    [RoomStatus.RESERVED]: 'จองแล้ว',
    [RoomStatus.OUT_OF_SERVICE]: 'ปิดปรับปรุง'
  }
  return labels[status]
}

export function getRoomStatusColor(status: RoomStatus): string {
  const colors: Record<RoomStatus, string> = {
    [RoomStatus.AVAILABLE]: 'green',
    [RoomStatus.OCCUPIED]: 'red',
    [RoomStatus.CLEANING]: 'yellow',
    [RoomStatus.RESERVED]: 'blue',
    [RoomStatus.OUT_OF_SERVICE]: 'gray'
  }
  return colors[status]
}

export function getStayTypeLabel(stayType: StayType): string {
  const labels: Record<StayType, string> = {
    [StayType.OVERNIGHT]: 'ค้างคืน',
    [StayType.TEMPORARY]: 'ชั่วคราว'
  }
  return labels[stayType]
}
