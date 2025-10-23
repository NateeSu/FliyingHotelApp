<template>
  <div class="min-h-screen bg-gray-50 p-6">
    <!-- Header -->
    <div class="mb-8 bg-gradient-to-br from-purple-600 via-indigo-600 to-blue-600 rounded-3xl shadow-2xl p-8 relative overflow-hidden">
      <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-10 animate-shimmer"></div>
      <div class="relative z-10">
        <h1 class="text-4xl font-bold text-white mb-2">📊 รายงานการเข้าพัก</h1>
        <p class="text-indigo-100">รายงานและสถิติการเข้าพัก</p>
      </div>
    </div>

    <!-- Filter Section -->
    <div class="bg-white rounded-2xl shadow-lg p-6 mb-6">
      <div class="flex flex-col md:flex-row gap-4 items-end">
        <!-- Period Type Selector -->
        <div class="flex-1">
          <label class="block text-sm font-semibold text-gray-700 mb-2">ช่วงเวลา</label>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-2">
            <button
              @click="setPeriodType('last_night')"
              :class="[
                'px-4 py-2 rounded-lg font-medium transition-all',
                periodType === 'last_night'
                  ? 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white shadow-lg'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              ]"
            >
              คืนล่าสุด
            </button>
            <button
              @click="setPeriodType('day')"
              :class="[
                'px-4 py-2 rounded-lg font-medium transition-all',
                periodType === 'day'
                  ? 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white shadow-lg'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              ]"
            >
              รายวัน
            </button>
            <button
              @click="setPeriodType('week')"
              :class="[
                'px-4 py-2 rounded-lg font-medium transition-all',
                periodType === 'week'
                  ? 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white shadow-lg'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              ]"
            >
              รายสัปดาห์
            </button>
            <button
              @click="setPeriodType('month')"
              :class="[
                'px-4 py-2 rounded-lg font-medium transition-all',
                periodType === 'month'
                  ? 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white shadow-lg'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              ]"
            >
              รายเดือน
            </button>
          </div>
        </div>

        <!-- Date Range Picker -->
        <div class="flex-1">
          <label class="block text-sm font-semibold text-gray-700 mb-2">วันที่เริ่มต้น</label>
          <input
            v-model="dateRange.start"
            type="date"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
          />
        </div>

        <div class="flex-1">
          <label class="block text-sm font-semibold text-gray-700 mb-2">วันที่สิ้นสุด</label>
          <input
            v-model="dateRange.end"
            type="date"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
          />
        </div>

        <!-- Refresh Button -->
        <button
          @click="loadData"
          :disabled="loading"
          class="px-6 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-lg font-medium hover:from-purple-700 hover:to-indigo-700 transition-all shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span v-if="loading">🔄 กำลังโหลด...</span>
          <span v-else>🔍 ค้นหา</span>
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center py-12">
      <div class="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-purple-600"></div>
    </div>

    <!-- Content -->
    <div v-else>
      <!-- Summary Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <!-- Total Check-ins Card -->
        <div class="bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl shadow-xl p-6 text-white">
          <div class="flex items-center justify-between mb-4">
            <div class="text-sm font-medium opacity-90">จำนวนการเข้าพักทั้งหมด</div>
            <div class="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
              <span class="text-2xl">🏨</span>
            </div>
          </div>
          <div class="text-4xl font-bold mb-2">{{ checkInsData.total_count.toLocaleString() }}</div>
          <div class="text-sm opacity-75">รายการ</div>
        </div>

        <!-- Total Revenue Card -->
        <div class="bg-gradient-to-br from-green-500 to-green-600 rounded-2xl shadow-xl p-6 text-white">
          <div class="flex items-center justify-between mb-4">
            <div class="text-sm font-medium opacity-90">รายได้ทั้งหมด</div>
            <div class="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
              <span class="text-2xl">💰</span>
            </div>
          </div>
          <div class="text-4xl font-bold mb-2">฿{{ formatCurrency(checkInsData.total_revenue) }}</div>
          <div class="text-sm opacity-75">บาท</div>
        </div>
      </div>

      <!-- Check-ins Table -->
      <div class="bg-white rounded-2xl shadow-lg overflow-hidden">
        <div class="p-6 border-b border-gray-200">
          <h2 class="text-xl font-bold text-gray-900">รายการการเข้าพัก</h2>
          <p class="text-sm text-gray-500 mt-1">คลิกที่แถวเพื่อดูรายละเอียด</p>
        </div>

        <div class="overflow-x-auto">
          <table v-if="checkInsData.check_ins.length > 0" class="w-full">
            <thead class="bg-gray-50">
              <tr>
                <th class="text-left py-4 px-6 text-sm font-semibold text-gray-700">ห้อง</th>
                <th class="text-left py-4 px-6 text-sm font-semibold text-gray-700">ลูกค้า</th>
                <th class="text-left py-4 px-6 text-sm font-semibold text-gray-700">ประเภท</th>
                <th class="text-left py-4 px-6 text-sm font-semibold text-gray-700">เช็คอิน</th>
                <th class="text-left py-4 px-6 text-sm font-semibold text-gray-700">เช็คเอาท์</th>
                <th class="text-right py-4 px-6 text-sm font-semibold text-gray-700">ยอดเงิน</th>
                <th class="text-center py-4 px-6 text-sm font-semibold text-gray-700">สถานะ</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="checkIn in checkInsData.check_ins"
                :key="checkIn.id"
                @click="showCheckInDetails(checkIn)"
                class="border-b border-gray-100 hover:bg-purple-50 cursor-pointer transition-colors"
              >
                <td class="py-4 px-6">
                  <div class="font-semibold text-gray-900">{{ checkIn.room_number }}</div>
                  <div class="text-xs text-gray-500">{{ checkIn.room_type_name }}</div>
                </td>
                <td class="py-4 px-6">
                  <div class="font-medium text-gray-900">{{ checkIn.customer_name }}</div>
                  <div class="text-xs text-gray-500">{{ checkIn.customer_phone }}</div>
                </td>
                <td class="py-4 px-6">
                  <span
                    :class="[
                      'inline-flex items-center px-3 py-1 rounded-full text-xs font-medium',
                      checkIn.stay_type === 'overnight'
                        ? 'bg-blue-100 text-blue-800'
                        : 'bg-purple-100 text-purple-800'
                    ]"
                  >
                    {{ translateStayType(checkIn.stay_type) }}
                  </span>
                </td>
                <td class="py-4 px-6">
                  <div class="text-sm text-gray-900">{{ formatDateTime(checkIn.check_in_time) }}</div>
                </td>
                <td class="py-4 px-6">
                  <div class="text-sm text-gray-900">
                    {{ checkIn.check_out_time ? formatDateTime(checkIn.check_out_time) : '-' }}
                  </div>
                </td>
                <td class="py-4 px-6 text-right">
                  <div class="font-semibold text-green-600">฿{{ formatCurrency(checkIn.total_amount) }}</div>
                </td>
                <td class="py-4 px-6 text-center">
                  <span
                    :class="[
                      'inline-flex items-center px-3 py-1 rounded-full text-xs font-medium',
                      checkIn.status === 'checked_out'
                        ? 'bg-gray-100 text-gray-800'
                        : 'bg-green-100 text-green-800'
                    ]"
                  >
                    {{ translateStatus(checkIn.status) }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>

          <!-- Empty State -->
          <div v-else class="text-center py-12">
            <div class="text-6xl mb-4">📭</div>
            <div class="text-xl font-semibold text-gray-700 mb-2">ไม่พบข้อมูล</div>
            <div class="text-gray-500">ไม่มีรายการเข้าพักในช่วงเวลาที่เลือก</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Check-in Details Modal -->
    <div
      v-if="selectedCheckIn"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 p-4"
      @click.self="closeDetailsModal"
    >
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <!-- Modal Header -->
        <div class="sticky top-0 bg-gradient-to-br from-purple-600 to-indigo-600 text-white p-6 rounded-t-2xl">
          <div class="flex items-center justify-between">
            <div>
              <h2 class="text-2xl font-bold">รายละเอียดการเข้าพัก</h2>
              <p class="text-purple-100 text-sm mt-1">ID: {{ selectedCheckIn.id }}</p>
            </div>
            <button
              @click="closeDetailsModal"
              class="w-10 h-10 rounded-full bg-white/20 hover:bg-white/30 flex items-center justify-center transition-colors"
            >
              <span class="text-2xl">×</span>
            </button>
          </div>
        </div>

        <!-- Modal Content -->
        <div class="p-6 space-y-6">
          <!-- Room Info -->
          <div class="bg-gray-50 rounded-xl p-4">
            <h3 class="text-sm font-semibold text-gray-700 mb-3">ข้อมูลห้องพัก</h3>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <div class="text-xs text-gray-500">หมายเลขห้อง</div>
                <div class="font-semibold text-gray-900">{{ selectedCheckIn.room_number }}</div>
              </div>
              <div>
                <div class="text-xs text-gray-500">ประเภทห้อง</div>
                <div class="font-semibold text-gray-900">{{ selectedCheckIn.room_type_name }}</div>
              </div>
            </div>
          </div>

          <!-- Customer Info -->
          <div class="bg-gray-50 rounded-xl p-4">
            <h3 class="text-sm font-semibold text-gray-700 mb-3">ข้อมูลลูกค้า</h3>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <div class="text-xs text-gray-500">ชื่อ-นามสกุล</div>
                <div class="font-semibold text-gray-900">{{ selectedCheckIn.customer_name }}</div>
              </div>
              <div>
                <div class="text-xs text-gray-500">เบอร์โทร</div>
                <div class="font-semibold text-gray-900">{{ selectedCheckIn.customer_phone }}</div>
              </div>
            </div>
          </div>

          <!-- Stay Info -->
          <div class="bg-gray-50 rounded-xl p-4">
            <h3 class="text-sm font-semibold text-gray-700 mb-3">ข้อมูลการพัก</h3>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <div class="text-xs text-gray-500">ประเภทการพัก</div>
                <div class="font-semibold text-gray-900">{{ translateStayType(selectedCheckIn.stay_type) }}</div>
              </div>
              <div>
                <div class="text-xs text-gray-500">จำนวนผู้เข้าพัก</div>
                <div class="font-semibold text-gray-900">{{ selectedCheckIn.number_of_guests }} คน</div>
              </div>
              <div v-if="selectedCheckIn.number_of_nights">
                <div class="text-xs text-gray-500">จำนวนคืน</div>
                <div class="font-semibold text-gray-900">{{ selectedCheckIn.number_of_nights }} คืน</div>
              </div>
              <div>
                <div class="text-xs text-gray-500">สถานะ</div>
                <div>
                  <span
                    :class="[
                      'inline-flex items-center px-3 py-1 rounded-full text-xs font-medium',
                      selectedCheckIn.status === 'checked_out'
                        ? 'bg-gray-100 text-gray-800'
                        : 'bg-green-100 text-green-800'
                    ]"
                  >
                    {{ translateStatus(selectedCheckIn.status) }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- Time Info -->
          <div class="bg-gray-50 rounded-xl p-4">
            <h3 class="text-sm font-semibold text-gray-700 mb-3">เวลา</h3>
            <div class="space-y-3">
              <div class="flex justify-between items-center">
                <div class="text-sm text-gray-600">เช็คอิน</div>
                <div class="font-semibold text-gray-900">{{ formatDateTime(selectedCheckIn.check_in_time) }}</div>
              </div>
              <div v-if="selectedCheckIn.expected_check_out_time" class="flex justify-between items-center">
                <div class="text-sm text-gray-600">เช็คเอาท์ที่คาดหวัง</div>
                <div class="font-medium text-gray-700">{{ formatDateTime(selectedCheckIn.expected_check_out_time) }}</div>
              </div>
              <div v-if="selectedCheckIn.check_out_time" class="flex justify-between items-center">
                <div class="text-sm text-gray-600">เช็คเอาท์จริง</div>
                <div class="font-semibold text-gray-900">{{ formatDateTime(selectedCheckIn.check_out_time) }}</div>
              </div>
            </div>
          </div>

          <!-- Payment Info -->
          <div class="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-4 border-2 border-green-200">
            <h3 class="text-sm font-semibold text-gray-700 mb-3">ข้อมูลการชำระเงิน</h3>
            <div class="space-y-3">
              <div class="flex justify-between items-center">
                <div class="text-sm text-gray-600">วิธีชำระเงิน</div>
                <div class="font-semibold text-gray-900">{{ translatePaymentMethod(selectedCheckIn.payment_method) }}</div>
              </div>
              <div class="flex justify-between items-center pt-3 border-t-2 border-green-200">
                <div class="text-lg font-semibold text-gray-900">ยอดเงินรวม</div>
                <div class="text-2xl font-bold text-green-600">฿{{ formatCurrency(selectedCheckIn.total_amount) }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Modal Footer -->
        <div class="p-6 border-t border-gray-200">
          <button
            @click="closeDetailsModal"
            class="w-full px-6 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-lg font-medium hover:from-purple-700 hover:to-indigo-700 transition-all shadow-lg"
          >
            ปิด
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { reportsApi, type CheckInListItem, type CheckInsListResponse } from '@/api/reports'
import dayjs from 'dayjs'

// State
const loading = ref(false)
const periodType = ref<'last_night' | 'day' | 'week' | 'month'>('last_night')
const dateRange = ref({
  start: '',
  end: ''
})

const checkInsData = ref<CheckInsListResponse>({
  check_ins: [],
  total_count: 0,
  total_revenue: 0,
  start_date: '',
  end_date: ''
})

const selectedCheckIn = ref<CheckInListItem | null>(null)

// Set period type and auto-adjust dates
function setPeriodType(type: 'last_night' | 'day' | 'week' | 'month') {
  periodType.value = type
  const now = dayjs()

  if (type === 'last_night') {
    // Last night: from 12:00 yesterday to 12:00 today
    const yesterday = now.subtract(1, 'day')
    dateRange.value.start = yesterday.format('YYYY-MM-DD')
    dateRange.value.end = now.format('YYYY-MM-DD')
  } else if (type === 'day') {
    // Today only
    dateRange.value.start = now.format('YYYY-MM-DD')
    dateRange.value.end = now.format('YYYY-MM-DD')
  } else if (type === 'week') {
    // Last 7 days
    dateRange.value.start = now.subtract(6, 'day').format('YYYY-MM-DD')
    dateRange.value.end = now.format('YYYY-MM-DD')
  } else if (type === 'month') {
    // Current month
    dateRange.value.start = now.startOf('month').format('YYYY-MM-DD')
    dateRange.value.end = now.format('YYYY-MM-DD')
  }

  loadData()
}

// Load data
async function loadData() {
  try {
    loading.value = true
    checkInsData.value = await reportsApi.getCheckInsList(
      dateRange.value.start,
      dateRange.value.end
    )
  } catch (error) {
    console.error('Error loading check-ins list:', error)
  } finally {
    loading.value = false
  }
}

// Show check-in details modal
function showCheckInDetails(checkIn: CheckInListItem) {
  selectedCheckIn.value = checkIn
}

// Close details modal
function closeDetailsModal() {
  selectedCheckIn.value = null
}

// Translations
function translateStayType(type: string): string {
  const map: Record<string, string> = {
    'overnight': 'ค้างคืน',
    'temporary': 'ชั่วคราว'
  }
  return map[type] || type
}

function translateStatus(status: string): string {
  const map: Record<string, string> = {
    'checked_in': 'เข้าพัก',
    'checked_out': 'เช็คเอาท์แล้ว'
  }
  return map[status] || status
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

// Formatters
function formatCurrency(value: number | string): string {
  const num = typeof value === 'string' ? parseFloat(value) : value
  return num.toLocaleString('th-TH', { minimumFractionDigits: 2 })
}

function formatDateTime(datetime: string | null): string {
  if (!datetime) return '-'
  return dayjs(datetime).format('DD/MM/YYYY HH:mm')
}

// Initialize
onMounted(() => {
  setPeriodType('last_night')
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
