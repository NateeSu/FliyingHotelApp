/**
 * Products API Client (Phase 6)
 * API calls for product management
 */
import apiClient from './client'

export interface Product {
  id: number
  name: string
  category: 'room_amenity' | 'food_beverage'
  price: number
  is_chargeable: boolean
  is_active: boolean
  description: string | null
  created_at?: string
  updated_at?: string
}

export interface ProductCreate {
  name: string
  category: 'room_amenity' | 'food_beverage'
  price: number
  is_chargeable?: boolean
  description?: string | null
}

export interface ProductUpdate {
  name?: string
  category?: 'room_amenity' | 'food_beverage'
  price?: number
  is_chargeable?: boolean
  description?: string | null
  is_active?: boolean
}

export interface ProductListResponse {
  data: Product[]
  total: number
  skip: number
  limit: number
}

export const productsApi = {
  /**
   * Get all active products (for guests)
   */
  async getPublicProducts(
    skip: number = 0,
    limit: number = 100,
    category?: string
  ): Promise<ProductListResponse> {
    const response = await apiClient.get<ProductListResponse>('/products', {
      params: {
        skip,
        limit,
        category
      }
    })
    return response.data
  },

  /**
   * Get all products including inactive (admin only)
   */
  async getAdminProducts(
    skip: number = 0,
    limit: number = 100,
    includeInactive: boolean = false
  ): Promise<ProductListResponse> {
    const response = await apiClient.get<ProductListResponse>('/products/admin/all', {
      params: {
        skip,
        limit,
        include_inactive: includeInactive
      }
    })
    return response.data
  },

  /**
   * Get single product by ID
   */
  async getProduct(id: number): Promise<Product> {
    const response = await apiClient.get<Product>(`/products/${id}`)
    return response.data
  },

  /**
   * Create new product (admin only)
   */
  async createProduct(data: ProductCreate): Promise<Product> {
    const response = await apiClient.post<Product>('/products', data)
    return response.data
  },

  /**
   * Update product (admin only)
   */
  async updateProduct(id: number, data: ProductUpdate): Promise<Product> {
    const response = await apiClient.put<Product>(`/products/${id}`, data)
    return response.data
  },

  /**
   * Delete product (soft delete - admin only)
   */
  async deleteProduct(id: number): Promise<{ message: string }> {
    const response = await apiClient.delete<{ message: string }>(`/products/${id}`)
    return response.data
  }
}
