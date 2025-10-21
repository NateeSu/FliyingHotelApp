/**
 * Customer API Client (Phase 4)
 * Handles customer management and search
 */
import apiClient from './client'

const BASE_PATH = '/customers'

export interface CustomerSearchResult {
  id: number
  full_name: string
  phone_number: string
  email?: string
  total_visits: number
  last_visit_date?: string
}

export interface CustomerResponse {
  id: number
  full_name: string
  phone_number: string
  email?: string
  id_card_number?: string
  address?: string
  total_visits: number
  total_spent: number
  last_visit_date?: string
  notes?: string
  created_at: string
  updated_at: string
}

export interface CustomerCreate {
  full_name: string
  phone_number: string
  email?: string
  id_card_number?: string
  address?: string
  notes?: string
}

export interface CustomerUpdate {
  full_name?: string
  phone_number?: string
  email?: string
  id_card_number?: string
  address?: string
  notes?: string
}

export interface CustomerListResponse {
  data: CustomerResponse[]
  total: number
}

export const customerApi = {
  /**
   * Search customers by name or phone (autocomplete)
   */
  async searchCustomers(query: string, limit: number = 10): Promise<CustomerSearchResult[]> {
    const response = await apiClient.get<CustomerSearchResult[]>(`${BASE_PATH}/search`, {
      params: { q: query, limit }
    })
    return response.data
  },

  /**
   * Get all customers with pagination
   */
  async getCustomers(limit: number = 100, offset: number = 0): Promise<CustomerListResponse> {
    const response = await apiClient.get<CustomerListResponse>(BASE_PATH, {
      params: { limit, offset }
    })
    return response.data
  },

  /**
   * Get customer by ID
   */
  async getCustomer(customerId: number): Promise<CustomerResponse> {
    const response = await apiClient.get<CustomerResponse>(`${BASE_PATH}/${customerId}`)
    return response.data
  },

  /**
   * Create a new customer
   */
  async createCustomer(customerData: CustomerCreate): Promise<CustomerResponse> {
    const response = await apiClient.post<CustomerResponse>(BASE_PATH, customerData)
    return response.data
  },

  /**
   * Update customer information
   */
  async updateCustomer(
    customerId: number,
    customerData: CustomerUpdate
  ): Promise<CustomerResponse> {
    const response = await apiClient.put<CustomerResponse>(
      `${BASE_PATH}/${customerId}`,
      customerData
    )
    return response.data
  },

  /**
   * Get customer visit history
   */
  async getCustomerHistory(customerId: number, limit: number = 10): Promise<any> {
    const response = await apiClient.get(`${BASE_PATH}/${customerId}/history`, {
      params: { limit }
    })
    return response.data
  }
}
