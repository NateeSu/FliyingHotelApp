<template>
  <div class="min-h-screen bg-gray-50 p-6">
    <!-- Header -->
    <div class="mb-8 bg-gradient-to-br from-purple-600 via-indigo-600 to-blue-600 rounded-3xl shadow-2xl p-8 relative overflow-hidden">
      <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-10 animate-shimmer"></div>
      <div class="relative z-10 flex items-center justify-between">
        <div>
          <h1 class="text-4xl font-bold text-white mb-2">📊 รายงานและสถิติ</h1>
          <p class="text-indigo-100">ภาพรวมข้อมูลและการวิเคราะห์</p>
        </div>

        <!-- Date Range Picker -->
        <div class="bg-white/20 backdrop-blur-sm rounded-2xl p-4">
          <div class="flex items-center space-x-4">
            <div>
              <label class="block text-xs text-white/80 mb-1">จาก</label>
              <input
                v-model="dateRange.start"
                type="date"
                class="px-3 py-2 rounded-lg text-sm bg-white text-gray-900"
              />
            </div>
            <div>
              <label class="block text-xs text-white/80 mb-1">ถึง</label>
              <input
                v-model="dateRange.end"
                type="date"
                class="px-3 py-2 rounded-lg text-sm bg-white text-gray-900"
              />
            </div>
            <button
              @click="loadReports"
              class="mt-5 px-4 py-2 bg-white text-purple-600 rounded-lg font-medium hover:bg-gray-100 transition-colors"
            >
              🔄 รีเฟรช
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center py-12">
      <div class="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-purple-600"></div>
    </div>

    <!-- Content -->
    <div v-else>
      <!-- Quick Stats Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div
          v-for="(stat, index) in quickStats"
          :key="index"
          class="bg-white rounded-2xl shadow-lg p-6 border-l-4 hover:shadow-xl transition-shadow"
          :class="getCardBorderColor(index)"
        >
          <div class="flex items-center justify-between mb-2">
            <div class="text-sm font-medium text-gray-600">{{ stat.label }}</div>
            <div
              v-if="stat.trend"
              :class="getTrendColor(stat.trend)"
              class="text-2xl"
            >
              {{ getTrendIcon(stat.trend) }}
            </div>
          </div>
          <div class="text-3xl font-bold text-gray-900">{{ stat.value }}</div>
          <div v-if="stat.change !== null" class="text-xs text-gray-500 mt-1">
            {{ stat.change > 0 ? '+' : '' }}{{ stat.change }}% vs ก่อนหน้า
          </div>
        </div>
      </div>

      <!-- Charts Section -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <!-- Revenue Chart -->
        <div class="bg-white rounded-2xl shadow-lg p-6">
          <h3 class="text-lg font-bold text-gray-900 mb-4">📈 รายได้รายวัน</h3>
          <LineChart
            v-if="revenueChartData.labels.length > 0"
            :labels="revenueChartData.labels"
            :datasets="revenueChartData.datasets"
            :height="300"
          />
          <div v-else class="text-center text-gray-500 py-12">
            ไม่มีข้อมูล
          </div>
        </div>

        <!-- Occupancy Chart -->
        <div class="bg-white rounded-2xl shadow-lg p-6">
          <h3 class="text-lg font-bold text-gray-900 mb-4">🏨 อัตราเข้าพักรายวัน</h3>
          <LineChart
            v-if="occupancyChartData.labels.length > 0"
            :labels="occupancyChartData.labels"
            :datasets="occupancyChartData.datasets"
            :height="300"
          />
          <div v-else class="text-center text-gray-500 py-12">
            ไม่มีข้อมูล
          </div>
        </div>
      </div>

      <!-- More Charts -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Payment Method Distribution -->
        <div class="bg-white rounded-2xl shadow-lg p-6">
          <h3 class="text-lg font-bold text-gray-900 mb-4">💰 ช่องทางชำระเงิน</h3>
          <PieChart
            v-if="paymentMethodChartData.labels.length > 0"
            :labels="paymentMethodChartData.labels"
            :data="paymentMethodChartData.data"
            :height="250"
            :doughnut="true"
          />
          <div v-else class="text-center text-gray-500 py-12">
            ไม่มีข้อมูล
          </div>
        </div>

        <!-- Stay Type Distribution -->
        <div class="bg-white rounded-2xl shadow-lg p-6">
          <h3 class="text-lg font-bold text-gray-900 mb-4">🛏️ ประเภทการพัก</h3>
          <PieChart
            v-if="stayTypeChartData.labels.length > 0"
            :labels="stayTypeChartData.labels"
            :data="stayTypeChartData.data"
            :height="250"
            :doughnut="true"
          />
          <div v-else class="text-center text-gray-500 py-12">
            ไม่มีข้อมูล
          </div>
        </div>

        <!-- Room Status Distribution -->
        <div class="bg-white rounded-2xl shadow-lg p-6">
          <h3 class="text-lg font-bold text-gray-900 mb-4">🚪 สถานะห้องพัก</h3>
          <PieChart
            v-if="roomStatusChartData.labels.length > 0"
            :labels="roomStatusChartData.labels"
            :data="roomStatusChartData.data"
            :height="250"
            :backgroundColor="['#10b981', '#ef4444', '#f59e0b', '#3b82f6', '#6b7280']"
          />
          <div v-else class="text-center text-gray-500 py-12">
            ไม่มีข้อมูล
          </div>
        </div>
      </div>

      <!-- Top Customers -->
      <div class="bg-white rounded-2xl shadow-lg p-6 mt-6">
        <h3 class="text-lg font-bold text-gray-900 mb-4">👥 ลูกค้าประจำ (Top 10)</h3>
        <div v-if="topCustomers.length > 0" class="overflow-x-auto">
          <table class="w-full">
            <thead>
              <tr class="border-b-2 border-gray-200">
                <th class="text-left py-3 px-4 text-sm font-semibold text-gray-700">อันดับ</th>
                <th class="text-left py-3 px-4 text-sm font-semibold text-gray-700">ชื่อ-นามสกุล</th>
                <th class="text-left py-3 px-4 text-sm font-semibold text-gray-700">เบอร์โทร</th>
                <th class="text-right py-3 px-4 text-sm font-semibold text-gray-700">ยอดใช้จ่ายรวม</th>
                <th class="text-center py-3 px-4 text-sm font-semibold text-gray-700">จำนวนครั้ง</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(customer, index) in topCustomers"
                :key="customer.customer_id"
                class="border-b border-gray-100 hover:bg-gray-50"
              >
                <td class="py-3 px-4 text-sm">
                  <span class="font-bold text-purple-600">{{ index + 1 }}</span>
                </td>
                <td class="py-3 px-4 text-sm font-medium">{{ customer.full_name }}</td>
                <td class="py-3 px-4 text-sm text-gray-600">{{ customer.phone_number }}</td>
                <td class="py-3 px-4 text-sm text-right font-semibold text-green-600">
                  ฿{{ customer.total_spending.toLocaleString('th-TH', { minimumFractionDigits: 2 }) }}
                </td>
                <td class="py-3 px-4 text-sm text-center">
                  <span class="bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-xs font-medium">
                    {{ customer.visit_count }} ครั้ง
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="text-center text-gray-500 py-12">
          ไม่มีข้อมูลลูกค้า
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { reportsApi } from '@/api/reports'
import type { QuickStat, TopCustomer } from '@/api/reports'
import LineChart from '@/components/charts/LineChart.vue'
import PieChart from '@/components/charts/PieChart.vue'

// State
const loading = ref(false)
const dateRange = ref({
  start: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
  end: new Date().toISOString().split('T')[0]
})

const quickStats = ref<QuickStat[]>([])
const topCustomers = ref<TopCustomer[]>([])

const revenueChartData = ref({
  labels: [] as string[],
  datasets: [{
    label: 'รายได้ (บาท)',
    data: [] as number[],
    borderColor: '#8b5cf6',
    backgroundColor: 'rgba(139, 92, 246, 0.1)'
  }]
})

const occupancyChartData = ref({
  labels: [] as string[],
  datasets: [{
    label: 'อัตราเข้าพัก (%)',
    data: [] as number[],
    borderColor: '#3b82f6',
    backgroundColor: 'rgba(59, 130, 246, 0.1)'
  }]
})

const paymentMethodChartData = ref({
  labels: [] as string[],
  data: [] as number[]
})

const stayTypeChartData = ref({
  labels: [] as string[],
  data: [] as number[]
})

const roomStatusChartData = ref({
  labels: [] as string[],
  data: [] as number[]
})

// Load all reports
async function loadReports() {
  try {
    loading.value = true

    // Load summary
    const summary = await reportsApi.getSummaryReport(dateRange.value.start, dateRange.value.end)
    quickStats.value = summary.quick_stats

    // Load revenue report
    const revenue = await reportsApi.getRevenueReport(dateRange.value.start, dateRange.value.end, 'day')
    revenueChartData.value = {
      labels: revenue.by_period.map(p => p.period),
      datasets: [{
        label: 'รายได้ (บาท)',
        data: revenue.by_period.map(p => p.revenue),
        borderColor: '#8b5cf6',
        backgroundColor: 'rgba(139, 92, 246, 0.1)'
      }]
    }

    // Payment method chart
    paymentMethodChartData.value = {
      labels: Object.keys(revenue.by_payment_method).map(translatePaymentMethod),
      data: Object.values(revenue.by_payment_method)
    }

    // Stay type chart
    stayTypeChartData.value = {
      labels: Object.keys(revenue.by_stay_type).map(translateStayType),
      data: Object.values(revenue.by_stay_type)
    }

    // Load occupancy report
    const occupancy = await reportsApi.getOccupancyReport(dateRange.value.start, dateRange.value.end)
    occupancyChartData.value = {
      labels: occupancy.by_period.map(p => p.period),
      datasets: [{
        label: 'อัตราเข้าพัก (%)',
        data: occupancy.by_period.map(p => p.occupancy_rate),
        borderColor: '#3b82f6',
        backgroundColor: 'rgba(59, 130, 246, 0.1)'
      }]
    }

    // Room status chart
    const statusDist = occupancy.room_status_distribution
    roomStatusChartData.value = {
      labels: ['ว่าง', 'เข้าพัก', 'ทำความสะอาด', 'จอง', 'ปิดปรับปรุง'],
      data: [
        statusDist.available,
        statusDist.occupied,
        statusDist.cleaning,
        statusDist.reserved,
        statusDist.out_of_service
      ]
    }

    // Load customer report
    const customers = await reportsApi.getCustomerReport(10)
    topCustomers.value = customers.top_customers

  } catch (error) {
    console.error('Error loading reports:', error)
  } finally {
    loading.value = false
  }
}

function translatePaymentMethod(method: string): string {
  const map: Record<string, string> = {
    'cash': 'เงินสด',
    'transfer': 'โอนเงิน',
    'credit_card': 'บัตรเครดิต',
    'qr_code': 'QR Code'
  }
  return map[method] || method
}

function translateStayType(type: string): string {
  const map: Record<string, string> = {
    'overnight': 'ค้างคืน',
    'temporary': 'ชั่วคราว'
  }
  return map[type] || type
}

function getCardBorderColor(index: number): string {
  const colors = [
    'border-purple-500',
    'border-blue-500',
    'border-green-500',
    'border-orange-500'
  ]
  return colors[index % colors.length]
}

function getTrendColor(trend: string): string {
  if (trend === 'up') return 'text-green-500'
  if (trend === 'down') return 'text-red-500'
  return 'text-gray-400'
}

function getTrendIcon(trend: string): string {
  if (trend === 'up') return '↗'
  if (trend === 'down') return '↘'
  return '→'
}

onMounted(() => {
  loadReports()
})
</script>

<style scoped>
@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

.animate-shimmer {
  animation: shimmer 3s infinite;
}
</style>
