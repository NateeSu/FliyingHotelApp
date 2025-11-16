<template>
  <div class="orders-page p-6">
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900 mb-2">📦 คำสั่งซื้อ</h1>
      <p class="text-gray-600">จัดการคำสั่งซื้อของแขก</p>
    </div>

    <!-- Filter Controls -->
    <div class="bg-white rounded-lg shadow-md p-4 mb-6">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <!-- Status Filter -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">สถานะ</label>
          <n-select
            v-model:value="filters.status"
            :options="statusOptions"
            clearable
            placeholder="ทั้งหมด"
          />
        </div>

        <!-- Room Filter -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">ห้องพัก</label>
          <n-input-number
            v-model:value="filters.roomId"
            placeholder="ทั้งหมด"
            clearable
          />
        </div>

        <!-- Date Range -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">จากวันที่</label>
          <n-date-picker
            v-model:value="filters.dateFrom"
            type="date"
            placeholder="เลือกวันที่"
            clearable
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">ถึงวันที่</label>
          <n-date-picker
            v-model:value="filters.dateTo"
            type="date"
            placeholder="เลือกวันที่"
            clearable
          />
        </div>
      </div>

      <!-- Filter Buttons -->
      <div class="flex gap-2 mt-4">
        <n-button type="primary" @click="searchOrders">
          🔍 ค้นหา
        </n-button>
        <n-button @click="resetFilters">
          ↺ รีเซ็ต
        </n-button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center py-12">
      <n-spin size="large" description="กำลังโหลด..." />
    </div>

    <!-- Orders Table -->
    <div v-else class="bg-white rounded-lg shadow-md overflow-hidden">
      <n-data-table
        :columns="columns"
        :data="orders"
        :pagination="pagination"
        :loading="loading"
        @update:page="handlePageChange"
        striped
      />
    </div>

    <!-- Empty State -->
    <div v-if="!loading && orders.length === 0" class="text-center py-12 text-gray-500">
      <p class="text-lg">ไม่พบคำสั่งซื้อ</p>
    </div>

    <!-- Status Update Modal -->
    <n-modal
      v-model:show="showStatusModal"
      title="อัปเดตสถานะ"
      preset="dialog"
      positive-text="ยืนยัน"
      negative-text="ยกเลิก"
      @positive-click="updateOrderStatus"
    >
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            สถานะใหม่
          </label>
          <n-select
            v-model:value="selectedStatus"
            :options="statusOptions"
            placeholder="เลือกสถานะ"
          />
        </div>
      </div>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import apiClient from '@/api/client'

const message = useMessage()

// State
const orders = ref<any[]>([])
const loading = ref(false)
const showStatusModal = ref(false)
const selectedOrderId = ref<number | null>(null)
const selectedStatus = ref<string | null>(null)

// Filters
const filters = ref({
  status: null,
  roomId: null,
  dateFrom: null,
  dateTo: null
})

// Pagination
const pagination = ref({
  page: 1,
  pageSize: 20,
  pageCount: 1,
  prefix(info) {
    return `รวม ${info.itemCount} รายการ`
  }
})

// Status options
const statusOptions = [
  { label: '⏳ รอดำเนินการ', value: 'PENDING' },
  { label: '✅ ส่งแล้ว', value: 'DELIVERED' },
  { label: '✔️ เสร็จสิ้น', value: 'COMPLETED' }
]

// Table columns
const columns = [
  {
    title: 'ID',
    key: 'id',
    width: 60
  },
  {
    title: 'สินค้า',
    key: 'product_id',
    render: (row) => {
      return `สินค้า #${row.product_id}`
    }
  },
  {
    title: 'จำนวน',
    key: 'quantity',
    width: 80
  },
  {
    title: 'ราคา/หน่วย',
    key: 'unit_price',
    render: (row) => {
      return `฿${formatPrice(row.unit_price)}`
    }
  },
  {
    title: 'รวม',
    key: 'total_price',
    render: (row) => {
      return `฿${formatPrice(row.total_price)}`
    }
  },
  {
    title: 'สถานะ',
    key: 'status',
    render: (row) => {
      const statusMap = {
        PENDING: '⏳ รอดำเนินการ',
        DELIVERED: '✅ ส่งแล้ว',
        COMPLETED: '✔️ เสร็จสิ้น'
      }
      return statusMap[row.status] || row.status
    }
  },
  {
    title: 'เวลาสั่ง',
    key: 'ordered_at',
    render: (row) => {
      return formatDateTime(row.ordered_at)
    }
  },
  {
    title: 'การกระทำ',
    key: 'actions',
    width: 150,
    render: (row) => {
      return h('div', { class: 'flex gap-2' }, [
        h(
          NButton,
          {
            text: true,
            type: 'primary',
            size: 'small',
            onClick: () => openStatusModal(row)
          },
          { default: () => '✏️ สถานะ' }
        ),
        h(
          NButton,
          {
            text: true,
            type: 'success',
            size: 'small',
            onClick: () => completeOrder(row.id),
            disabled: row.status === 'COMPLETED'
          },
          { default: () => '✔️ เสร็จ' }
        )
      ])
    }
  }
]

// Import h from vue for render function
import { h } from 'vue'
import { NButton } from 'naive-ui'

// Load orders on mount
onMounted(() => {
  searchOrders()
})

// Search orders
async function searchOrders() {
  try {
    loading.value = true

    let dateFrom = ''
    let dateTo = ''

    if (filters.value.dateFrom) {
      const from = new Date(filters.value.dateFrom)
      dateFrom = from.toISOString().split('T')[0]
    }

    if (filters.value.dateTo) {
      const to = new Date(filters.value.dateTo)
      dateTo = to.toISOString().split('T')[0]
    }

    const response = await apiClient.get('/orders', {
      params: {
        skip: (pagination.value.page - 1) * pagination.value.pageSize,
        limit: pagination.value.pageSize,
        status: filters.value.status || undefined,
        room_id: filters.value.roomId || undefined,
        date_from: dateFrom || undefined,
        date_to: dateTo || undefined
      }
    })

    orders.value = response.data.orders
    pagination.value.pageCount = Math.ceil(response.data.total / pagination.value.pageSize)
  } catch (error: any) {
    message.error(error.response?.data?.detail || 'ไม่สามารถโหลดคำสั่งซื้อได้')
  } finally {
    loading.value = false
  }
}

// Reset filters
function resetFilters() {
  filters.value = {
    status: null,
    roomId: null,
    dateFrom: null,
    dateTo: null
  }
  pagination.value.page = 1
  searchOrders()
}

// Handle page change
function handlePageChange(page: number) {
  pagination.value.page = page
  searchOrders()
}

// Open status modal
function openStatusModal(order: any) {
  selectedOrderId.value = order.id
  selectedStatus.value = order.status
  showStatusModal.value = true
}

// Update order status
async function updateOrderStatus() {
  if (!selectedOrderId.value || !selectedStatus.value) return

  try {
    await apiClient.put(`/orders/${selectedOrderId.value}/status?new_status=${selectedStatus.value}`)
    message.success('อัปเดตสถานะเรียบร้อย')
    showStatusModal.value = false
    searchOrders()
  } catch (error: any) {
    message.error(error.response?.data?.detail || 'ไม่สามารถอัปเดตสถานะได้')
  }
}

// Complete order
async function completeOrder(orderId: number) {
  try {
    await apiClient.post(`/orders/${orderId}/complete`)
    message.success('ทำเครื่องหมายเสร็จสิ้นเรียบร้อย')
    searchOrders()
  } catch (error: any) {
    message.error(error.response?.data?.detail || 'ไม่สามารถทำเครื่องหมายเสร็จสิ้นได้')
  }
}

// Format price
function formatPrice(price: number): string {
  return new Intl.NumberFormat('th-TH', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(price)
}

// Format date time
function formatDateTime(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleDateString('th-TH', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped>
.orders-page {
  min-height: 100vh;
  background-color: #f5f5f5;
}

/* Mobile optimization */
@media (max-width: 640px) {
  .orders-page {
    padding: 1rem;
  }

  .grid {
    grid-template-columns: 1fr;
  }
}
</style>
