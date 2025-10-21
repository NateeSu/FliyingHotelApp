<template>
  <div class="guest-order-page">
    <!-- Header -->
    <div class="header bg-gradient-to-r from-blue-500 to-blue-600 text-white p-4 sticky top-0 z-10">
      <div class="max-w-2xl mx-auto">
        <h1 class="text-2xl font-bold">🍽️ สั่งของในห้อง</h1>
        <p class="text-blue-100 mt-1">ห้อง {{ roomId }}</p>
      </div>
    </div>

    <!-- Main Content -->
    <div class="max-w-2xl mx-auto p-4">
      <!-- Check-in Status Alert -->
      <n-alert
        v-if="checkInStatus"
        type="success"
        title="✅ ยินดีต้อนรับ"
        class="mb-4"
      >
        <p>สวัสดีคุณ {{ checkInStatus.customer_name }}</p>
      </n-alert>

      <!-- Loading State -->
      <div v-if="loading" class="flex justify-center items-center py-12">
        <n-spin size="large" description="กำลังโหลด..." />
      </div>

      <!-- Error State -->
      <n-alert
        v-if="error"
        type="error"
        title="❌ เกิดข้อผิดพลาด"
        class="mb-4"
      >
        {{ error }}
      </n-alert>

      <!-- Products List -->
      <div v-if="!loading && !error" class="space-y-3">
        <h2 class="text-lg font-bold text-gray-800 mb-4">📦 เลือกสินค้า</h2>

        <div
          v-for="product in products"
          :key="product.id"
          class="bg-white rounded-lg border border-gray-200 p-4 flex items-center justify-between"
        >
          <div class="flex-1">
            <h3 class="font-semibold text-gray-900">{{ product.name }}</h3>
            <p v-if="product.description" class="text-sm text-gray-500">
              {{ product.description }}
            </p>
            <p class="text-lg font-bold text-blue-600 mt-1">
              ฿ {{ formatPrice(product.price) }}
            </p>
          </div>

          <!-- Quantity Controls -->
          <div class="flex items-center gap-2 ml-4">
            <n-button
              strong
              secondary
              circle
              @click="decreaseQuantity(product.id)"
              :disabled="!quantities[product.id] || quantities[product.id] === 0"
            >
              −
            </n-button>
            <input
              :value="quantities[product.id] || 0"
              type="number"
              readonly
              class="w-12 text-center border border-gray-300 rounded py-1"
            />
            <n-button strong secondary circle @click="increaseQuantity(product.id)">
              +
            </n-button>
          </div>
        </div>
      </div>

      <!-- Order Summary -->
      <div v-if="!loading && !error && hasItems" class="mt-8 bg-white rounded-lg border border-gray-300 p-4">
        <h2 class="font-bold text-lg text-gray-900 mb-4">🛒 สรุปการสั่ง</h2>

        <!-- Items Summary -->
        <div class="space-y-2 mb-4 pb-4 border-b border-gray-200">
          <div
            v-for="(qty, productId) in quantities"
            :key="productId"
            v-show="qty > 0"
            class="flex justify-between text-sm"
          >
            <span>{{ getProductName(productId) }} × {{ qty }}</span>
            <span>฿ {{ formatPrice(getProductTotal(productId, qty)) }}</span>
          </div>
        </div>

        <!-- Total -->
        <div class="flex justify-between items-center mb-6">
          <span class="text-xl font-bold">รวมทั้งสิ้น:</span>
          <span class="text-2xl font-bold text-blue-600">฿ {{ formatPrice(totalAmount) }}</span>
        </div>

        <!-- Submit Button -->
        <n-button
          type="primary"
          size="large"
          block
          :loading="submitting"
          @click="submitOrder"
        >
          ✅ ยืนยันการสั่ง
        </n-button>
      </div>

      <!-- Empty State -->
      <div
        v-if="!loading && !error && !hasItems"
        class="text-center py-12 text-gray-500"
      >
        <p class="text-lg">ยังไม่ได้เลือกสินค้า</p>
        <p class="text-sm mt-2">เลือกสินค้าด้านบนเพื่อเริ่มสั่ง</p>
      </div>
    </div>

    <!-- Success Modal -->
    <n-dialog
      v-model:show="showSuccessDialog"
      type="success"
      title="✅ สั่งของสำเร็จ!"
      preset="dialog"
      :positive-text="`ตกลง`"
      @positive-click="handleSuccessClose"
    >
      <template #default>
        <div>
          <p class="mb-2">สั่งของเรียบร้อยแล้ว</p>
          <p class="text-sm text-gray-600">
            เบอร์ order: <span class="font-semibold">#{{ successOrderId }}</span>
          </p>
          <p class="text-sm text-gray-600 mt-1">
            โปรดรอรับสินค้าใจห้องของคุณ
          </p>
        </div>
      </template>
    </n-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useMessage } from 'naive-ui'
import axios from 'axios'

const route = useRoute()
const message = useMessage()

// State
const roomId = ref<number>(0)
const checkInStatus = ref<any>(null)
const products = ref<any[]>([])
const quantities = ref<Record<number, number>>({})
const loading = ref(true)
const error = ref<string | null>(null)
const submitting = ref(false)
const showSuccessDialog = ref(false)
const successOrderId = ref(0)

// Get room ID from route
onMounted(() => {
  roomId.value = parseInt(route.params.roomId as string, 10)
  if (!roomId.value) {
    error.value = 'ไม่พบหมายเลขห้อง'
    loading.value = false
    return
  }

  loadData()
})

// Load check-in status and products
async function loadData() {
  try {
    loading.value = true
    error.value = null

    // Check if guest is checked in
    const statusResponse = await axios.get(`/api/v1/public/guest/room/${roomId.value}/check-in-status`)
    checkInStatus.value = statusResponse.data

    // Load products
    const productsResponse = await axios.get('/api/v1/public/guest/products')
    products.value = productsResponse.data
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'ไม่สามารถโหลดข้อมูลได้'
    console.error('Error loading data:', err)
  } finally {
    loading.value = false
  }
}

// Quantity management
function increaseQuantity(productId: number) {
  quantities.value[productId] = (quantities.value[productId] || 0) + 1
}

function decreaseQuantity(productId: number) {
  if (quantities.value[productId] && quantities.value[productId] > 0) {
    quantities.value[productId]--
  }
}

// Calculate totals
const hasItems = computed(() => {
  return Object.values(quantities.value).some(qty => qty > 0)
})

const totalAmount = computed(() => {
  return Object.entries(quantities.value).reduce((sum, [productId, qty]) => {
    if (qty > 0) {
      const product = products.value.find(p => p.id === parseInt(productId))
      if (product) {
        sum += product.price * qty
      }
    }
    return sum
  }, 0)
})

function getProductName(productId: string | number): string {
  const product = products.value.find(p => p.id === parseInt(productId as string))
  return product?.name || 'สินค้า'
}

function getProductTotal(productId: string | number, qty: number): number {
  const product = products.value.find(p => p.id === parseInt(productId as string))
  return (product?.price || 0) * qty
}

function formatPrice(price: number): string {
  return new Intl.NumberFormat('th-TH').format(Math.floor(price * 100) / 100)
}

// Submit order
async function submitOrder() {
  try {
    submitting.value = true

    const orderItems = Object.entries(quantities.value)
      .filter(([, qty]) => qty > 0)
      .map(([productId, quantity]) => ({
        product_id: parseInt(productId),
        quantity
      }))

    if (orderItems.length === 0) {
      message.error('กรุณาเลือกสินค้า')
      return
    }

    const response = await axios.post(`/api/v1/public/guest/room/${roomId.value}/order`, {
      items: orderItems
    })

    successOrderId.value = response.data.order_id
    showSuccessDialog.value = true

    // Reset quantities
    quantities.value = {}
  } catch (err: any) {
    message.error(err.response?.data?.detail || 'ไม่สามารถสั่งของได้')
    console.error('Error submitting order:', err)
  } finally {
    submitting.value = false
  }
}

function handleSuccessClose() {
  showSuccessDialog.value = false
  // Reset page
  quantities.value = {}
}
</script>

<style scoped>
.guest-order-page {
  min-height: 100vh;
  background-color: #f5f5f5;
}

.header {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* Mobile optimization */
@media (max-width: 640px) {
  .guest-order-page {
    padding: 0;
  }
}
</style>
