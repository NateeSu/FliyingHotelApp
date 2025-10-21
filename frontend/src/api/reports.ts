/**
 * Reports API Client (Phase 8)
 * API calls for reports and analytics
 */
import apiClient from './client'

// ============================================================================
// Types
// ============================================================================

export interface RevenueByPeriod {
  period: string
  revenue: number
  count: number
}

export interface RevenueReport {
  total_revenue: number
  total_transactions: number
  average_transaction: number
  by_payment_method: Record<string, number>
  by_stay_type: Record<string, number>
  by_period: RevenueByPeriod[]
  start_date: string
  end_date: string
}

export interface OccupancyByPeriod {
  period: string
  occupancy_rate: number
  occupied_rooms: number
  total_rooms: number
}

export interface RoomStatusDistribution {
  available: number
  occupied: number
  cleaning: number
  reserved: number
  out_of_service: number
}

export interface OccupancyReport {
  occupancy_rate: number
  total_rooms: number
  occupied_rooms: number
  available_rooms: number
  room_status_distribution: RoomStatusDistribution
  by_period: OccupancyByPeriod[]
  start_date: string
  end_date: string
}

export interface BookingByPeriod {
  period: string
  total_bookings: number
  confirmed: number
  cancelled: number
  checked_in: number
}

export interface BookingReport {
  total_bookings: number
  confirmed_bookings: number
  cancelled_bookings: number
  checked_in_bookings: number
  cancellation_rate: number
  conversion_rate: number
  total_deposit: number
  by_period: BookingByPeriod[]
  start_date: string
  end_date: string
}

export interface TopCustomer {
  customer_id: number
  full_name: string
  phone_number: string
  total_spending: number
  visit_count: number
  last_visit: string | null
}

export interface CustomerReport {
  top_customers: TopCustomer[]
  total_customers: number
  new_customers: number
  returning_customers: number
}

export interface QuickStat {
  label: string
  value: string
  change: number | null
  trend: 'up' | 'down' | 'neutral' | null
}

export interface SummaryReport {
  total_revenue: number
  revenue_vs_previous: number | null
  occupancy_rate: number
  occupancy_vs_previous: number | null
  total_checkins: number
  total_checkouts: number
  total_bookings: number
  bookings_vs_previous: number | null
  total_customers: number
  new_customers: number
  quick_stats: QuickStat[]
  start_date: string
  end_date: string
}

// ============================================================================
// API Functions
// ============================================================================

export const reportsApi = {
  /**
   * Get revenue report
   */
  async getRevenueReport(
    startDate: string,
    endDate: string,
    groupBy: 'day' | 'month' = 'day'
  ): Promise<RevenueReport> {
    const response = await apiClient.get<RevenueReport>('/reports/revenue', {
      params: {
        start_date: startDate,
        end_date: endDate,
        group_by: groupBy
      }
    })
    return response.data
  },

  /**
   * Get occupancy report
   */
  async getOccupancyReport(
    startDate: string,
    endDate: string
  ): Promise<OccupancyReport> {
    const response = await apiClient.get<OccupancyReport>('/reports/occupancy', {
      params: {
        start_date: startDate,
        end_date: endDate
      }
    })
    return response.data
  },

  /**
   * Get booking report
   */
  async getBookingReport(
    startDate: string,
    endDate: string
  ): Promise<BookingReport> {
    const response = await apiClient.get<BookingReport>('/reports/bookings', {
      params: {
        start_date: startDate,
        end_date: endDate
      }
    })
    return response.data
  },

  /**
   * Get customer report
   */
  async getCustomerReport(limit: number = 10): Promise<CustomerReport> {
    const response = await apiClient.get<CustomerReport>('/reports/customers', {
      params: { limit }
    })
    return response.data
  },

  /**
   * Get summary report (for dashboard)
   */
  async getSummaryReport(
    startDate?: string,
    endDate?: string
  ): Promise<SummaryReport> {
    const response = await apiClient.get<SummaryReport>('/reports/summary', {
      params: {
        start_date: startDate,
        end_date: endDate
      }
    })
    return response.data
  }
}
