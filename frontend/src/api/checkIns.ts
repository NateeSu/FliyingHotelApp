/**
 * Check-Ins API Client (Phase 4)
 * API calls for check-in operations
 */
import apiClient from './client'

const BASE_PATH = '/check-ins'

export interface RoomTransferRequest {
  new_room_id: number
  reason?: string
}

export interface RoomTransferResponse {
  check_in_id: number
  old_room_id: number
  old_room_number: string
  new_room_id: number
  new_room_number: string
  transferred_by: number
  transferred_at: string
  reason?: string
  message: string
}

export const checkInsApi = {
  /**
   * Transfer room for a check-in
   */
  async transferRoom(
    checkInId: number,
    data: RoomTransferRequest
  ): Promise<RoomTransferResponse> {
    const response = await apiClient.post<RoomTransferResponse>(
      `${BASE_PATH}/${checkInId}/transfer-room`,
      data
    )
    return response.data
  }
}
