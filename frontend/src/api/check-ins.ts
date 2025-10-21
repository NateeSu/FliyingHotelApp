/**
 * Check-In API Client (Phase 4)
 * Handles check-in and check-out operations
 */
import apiClient from './client'

const BASE_PATH = '/check-ins'

export interface CheckInCreateData {
  room_id: number
  stay_type: 'overnight' | 'temporary'
  number_of_nights?: number
  number_of_guests?: number
  check_in_time?: string // ISO datetime
  booking_id?: number
  deposit_amount?: number
  payment_method: 'cash' | 'transfer' | 'credit_card'
  notes?: string
}

export interface CustomerData {
  full_name: string
  phone_number: string
  email?: string
  id_card_number?: string
  address?: string
  notes?: string
}

export interface CheckInResponse {
  id: number
  room_id: number
  customer_id: number
  booking_id?: number
  stay_type: 'overnight' | 'temporary'
  number_of_nights?: number
  number_of_guests: number
  check_in_time: string
  expected_check_out_time: string
  actual_check_out_time?: string
  is_overtime: boolean
  overtime_minutes?: number
  overtime_charge: number
  base_amount: number
  extra_charges: number
  discount_amount: number
  discount_reason?: string
  total_amount: number
  payment_method?: 'cash' | 'transfer' | 'credit_card'
  payment_slip_url?: string
  status: 'checked_in' | 'checked_out'
  notes?: string
  created_by: number
  checked_out_by?: number
  created_at: string
  updated_at: string
}

export interface CheckOutRequest {
  actual_check_out_time?: string // ISO datetime
  extra_charges?: number
  discount_amount?: number
  discount_reason?: string
  payment_method: 'cash' | 'transfer' | 'credit_card'
  payment_notes?: string
}

export interface CheckOutSummary {
  check_in_id: number
  room_number: string
  customer_name: string
  stay_type: 'overnight' | 'temporary'
  check_in_time: string
  expected_check_out_time: string
  actual_check_out_time: string
  base_amount: number
  is_overtime: boolean
  overtime_minutes?: number
  overtime_charge: number
  extra_charges: number
  discount_amount: number
  total_amount: number
}

export const checkInApi = {
  /**
   * Create a new check-in
   */
  async createCheckIn(
    checkInData: CheckInCreateData,
    customerData: CustomerData
  ): Promise<CheckInResponse> {
    const response = await apiClient.post<CheckInResponse>(BASE_PATH, {
      ...checkInData,
      customer_data: customerData
    })
    return response.data
  },

  /**
   * Get check-in by ID
   */
  async getCheckIn(checkInId: number): Promise<CheckInResponse> {
    const response = await apiClient.get<CheckInResponse>(`${BASE_PATH}/${checkInId}`)
    return response.data
  },

  /**
   * Get active check-in for a room
   */
  async getActiveCheckInByRoom(roomId: number): Promise<CheckInResponse> {
    const response = await apiClient.get<CheckInResponse>(`${BASE_PATH}/room/${roomId}/active`)
    return response.data
  },

  /**
   * Get checkout summary with calculated amounts
   */
  async getCheckoutSummary(checkInId: number): Promise<CheckOutSummary> {
    const response = await apiClient.get<CheckOutSummary>(
      `${BASE_PATH}/${checkInId}/checkout-summary`
    )
    return response.data
  },

  /**
   * Process check-out
   */
  async processCheckout(
    checkInId: number,
    checkoutData: CheckOutRequest
  ): Promise<CheckInResponse> {
    const response = await apiClient.post<CheckInResponse>(
      `${BASE_PATH}/${checkInId}/checkout`,
      checkoutData
    )
    return response.data
  },

  /**
   * Preview PDF receipt in new window (can download from there)
   */
  async downloadReceipt(checkInId: number): Promise<void> {
    const response = await apiClient.get(`${BASE_PATH}/${checkInId}/generate-receipt`, {
      responseType: 'blob'
    })

    // Create blob URL for preview
    const blob = new Blob([response.data], { type: 'application/pdf' })
    const url = window.URL.createObjectURL(blob)

    // Open in new window for preview
    const newWindow = window.open(url, '_blank')

    if (!newWindow) {
      // If popup blocked, fallback to download
      const link = document.createElement('a')
      link.href = url

      const contentDisposition = response.headers['content-disposition']
      let filename = `receipt_${checkInId}.pdf`
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="?(.+)"?/)
        if (filenameMatch) {
          filename = filenameMatch[1]
        }
      }

      link.setAttribute('download', filename)
      document.body.appendChild(link)
      link.click()
      link.remove()
    }

    // Clean up blob URL after a delay (to allow window to load)
    setTimeout(() => {
      window.URL.revokeObjectURL(url)
    }, 100)
  },

  /**
   * Upload payment slip image
   */
  async uploadPaymentSlip(checkInId: number, file: File): Promise<{ message: string; file_url: string }> {
    const formData = new FormData()
    formData.append('file', file)

    const response = await apiClient.post<{ message: string; file_url: string }>(
      `${BASE_PATH}/${checkInId}/upload-slip`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }
    )
    return response.data
  }
}
