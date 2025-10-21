/**
 * Customer Store (Phase 7)
 * Manages customer state and operations
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { customerApi, type CustomerResponse, type CustomerCreate, type CustomerUpdate } from '@/api/customers'

export const useCustomerStore = defineStore('customer', () => {

  // State
  const customers = ref<CustomerResponse[]>([])
  const selectedCustomer = ref<CustomerResponse | null>(null)
  const totalCustomers = ref(0)
  const loading = ref(false)
  const searchResults = ref<CustomerResponse[]>([])

  // Getters
  const getCustomerById = computed(() => {
    return (id: number) => customers.value.find(c => c.id === id)
  })

  // Actions
  async function fetchCustomers(limit: number = 100, offset: number = 0) {
    loading.value = true
    try {
      const response = await customerApi.getCustomers(limit, offset)
      customers.value = response.data
      totalCustomers.value = response.total
    } catch (error: any) {
      throw error
    } finally {
      loading.value = false
    }
  }

  async function searchCustomers(query: string, limit: number = 10) {
    if (!query || query.trim().length === 0) {
      searchResults.value = []
      return []
    }

    loading.value = true
    try {
      const results = await customerApi.searchCustomers(query, limit)
      searchResults.value = results as any
      return results
    } catch (error: any) {
      throw error
    } finally {
      loading.value = false
    }
  }

  async function createCustomer(data: CustomerCreate): Promise<CustomerResponse> {
    loading.value = true
    try {
      const newCustomer = await customerApi.createCustomer(data)
      customers.value.unshift(newCustomer)
      totalCustomers.value++
      return newCustomer
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || 'D!H*2!2#@4H!I-!9%%9I2DI'
      throw error
    } finally {
      loading.value = false
    }
  }

  async function updateCustomer(id: number, data: CustomerUpdate): Promise<CustomerResponse> {
    loading.value = true
    try {
      const updatedCustomer = await customerApi.updateCustomer(id, data)
      const index = customers.value.findIndex(c => c.id === id)
      if (index !== -1) {
        customers.value[index] = updatedCustomer
      }
      if (selectedCustomer.value?.id === id) {
        selectedCustomer.value = updatedCustomer
      }
      return updatedCustomer
    } catch (error: any) {
      throw error
    } finally {
      loading.value = false
    }
  }

  async function selectCustomer(id: number) {
    try {
      selectedCustomer.value = await customerApi.getCustomer(id)
    } catch (error: any) {
      throw error
    }
  }

  function clearSelection() {
    selectedCustomer.value = null
  }

  return {
    // State
    customers,
    selectedCustomer,
    totalCustomers,
    loading,
    searchResults,

    // Getters
    getCustomerById,

    // Actions
    fetchCustomers,
    searchCustomers,
    createCustomer,
    updateCustomer,
    selectCustomer,
    clearSelection
  }
})
