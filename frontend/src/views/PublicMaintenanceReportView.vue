<template>
  <div class="min-h-screen bg-gradient-to-br from-orange-50 via-red-50 to-pink-50 py-8 px-4">
    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center min-h-[400px]">
      <div class="text-center">
        <svg class="animate-spin h-16 w-16 text-orange-600 mx-auto mb-4" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <p class="text-xl font-semibold text-gray-700">กำลังโหลด...</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="max-w-2xl mx-auto">
      <div class="bg-white rounded-3xl shadow-2xl p-8 text-center">
        <div class="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-6">
          <svg class="w-10 h-10 text-red-600" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/>
          </svg>
        </div>
        <h2 class="text-2xl font-bold text-gray-900 mb-2">เกิดข้อผิดพลาด</h2>
        <p class="text-gray-600">{{ error }}</p>
      </div>
    </div>

    <!-- Form -->
    <div v-else class="max-w-2xl mx-auto">
      <!-- Header -->
      <div class="text-center mb-8">
        <div class="w-20 h-20 bg-gradient-to-br from-orange-500 to-red-500 rounded-3xl flex items-center justify-center mx-auto mb-4 shadow-xl">
          <svg class="w-10 h-10 text-white" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
          </svg>
        </div>
        <h1 class="text-4xl font-bold bg-gradient-to-r from-orange-600 to-red-600 bg-clip-text text-transparent mb-2">
          แจ้งซ่อมบำรุง
        </h1>
        <p class="text-gray-600">แจ้งอุปกรณ์ชำรุดหรือต้องการซ่อมแซม</p>
      </div>

      <!-- Room Info (if available) -->
      <div v-if="roomInfo" class="bg-white rounded-3xl shadow-xl p-6 mb-6">
        <h3 class="text-lg font-bold text-gray-900 mb-3">ข้อมูลห้อง</h3>
        <div class="flex items-center space-x-3">
          <div class="w-12 h-12 bg-gradient-to-br from-orange-500 to-red-500 rounded-xl flex items-center justify-center">
            <svg class="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z"/>
            </svg>
          </div>
          <div>
            <p class="text-2xl font-bold text-gray-900">{{ roomInfo.room_number }}</p>
            <p class="text-sm text-gray-600">{{ roomInfo.room_type_name }}</p>
          </div>
        </div>
      </div>

      <!-- Form -->
      <div class="bg-white rounded-3xl shadow-2xl p-8">
        <form @submit.prevent="handleSubmit">
          <!-- Category -->
          <div class="mb-6">
            <label class="block text-sm font-bold text-gray-900 mb-2">
              ประเภทงานซ่อม <span class="text-red-500">*</span>
            </label>
            <select
              v-model="formData.category"
              required
              class="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:outline-none focus:ring-4 focus:ring-orange-200 focus:border-orange-500 transition-all text-lg"
            >
              <option value="">-- เลือกประเภทงาน --</option>
              <option value="plumbing">🚰 ประปา</option>
              <option value="electrical">⚡ ไฟฟ้า</option>
              <option value="hvac">❄️ เครื่องปรับอากาศ</option>
              <option value="furniture">🪑 เฟอร์นิเจอร์</option>
              <option value="appliance">📺 เครื่องใช้ไฟฟ้า</option>
              <option value="building">🏢 อาคาร</option>
              <option value="other">🔧 อื่นๆ</option>
            </select>
          </div>

          <!-- Title -->
          <div class="mb-6">
            <label class="block text-sm font-bold text-gray-900 mb-2">
              หัวข้อ <span class="text-red-500">*</span>
            </label>
            <input
              v-model="formData.title"
              type="text"
              required
              maxlength="200"
              placeholder="เช่น แอร์เสีย, ก๊อกน้ำรั่ว, หลอดไฟไม่ติด"
              class="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:outline-none focus:ring-4 focus:ring-orange-200 focus:border-orange-500 transition-all text-lg"
            />
            <p class="text-xs text-gray-500 mt-1">{{ formData.title.length }}/200 ตัวอักษร</p>
          </div>

          <!-- Description -->
          <div class="mb-6">
            <label class="block text-sm font-bold text-gray-900 mb-2">
              รายละเอียด
            </label>
            <textarea
              v-model="formData.description"
              rows="4"
              maxlength="500"
              placeholder="รายละเอียดเพิ่มเติมเกี่ยวกับความชำรุด..."
              class="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:outline-none focus:ring-4 focus:ring-orange-200 focus:border-orange-500 transition-all"
            ></textarea>
            <p class="text-xs text-gray-500 mt-1">{{ formData.description.length }}/500 ตัวอักษร</p>
          </div>

          <!-- Priority -->
          <div class="mb-8">
            <label class="block text-sm font-bold text-gray-900 mb-2">
              ลำดับความสำคัญ <span class="text-red-500">*</span>
            </label>
            <select
              v-model="formData.priority"
              required
              class="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:outline-none focus:ring-4 focus:ring-orange-200 focus:border-orange-500 transition-all text-lg"
            >
              <option value="urgent">🔴 ด่วนมาก</option>
              <option value="high">🟠 สูง</option>
              <option value="medium">🟡 ปานกลาง</option>
              <option value="low">🟢 ต่ำ</option>
            </select>
          </div>

          <!-- Buttons -->
          <div class="flex space-x-3">
            <button
              v-if="fromHousekeeping"
              type="button"
              @click="goBack"
              class="flex-1 px-6 py-4 bg-gray-200 text-gray-700 rounded-xl font-bold text-lg hover:bg-gray-300 transition-colors"
            >
              ย้อนกลับ
            </button>
            <button
              type="submit"
              :disabled="submitting"
              class="flex-1 px-6 py-4 bg-gradient-to-r from-orange-500 to-red-500 text-white rounded-xl font-bold text-lg hover:from-orange-600 hover:to-red-600 transition-all shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
            >
              <svg v-if="submitting" class="animate-spin h-6 w-6" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span>{{ submitting ? 'กำลังบันทึก...' : 'แจ้งซ่อม' }}</span>
            </button>
          </div>
        </form>
      </div>

      <!-- Info Note -->
      <div v-if="fromHousekeeping" class="mt-6 bg-blue-50 border-2 border-blue-200 rounded-2xl p-4">
        <div class="flex items-start space-x-3">
          <svg class="w-6 h-6 text-blue-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"/>
          </svg>
          <div>
            <p class="text-sm font-semibold text-blue-900">หมายเหตุ</p>
            <p class="text-xs text-blue-700 mt-1">
              หลังจากแจ้งซ่อมเรียบร้อย คุณสามารถกลับไปยืนยันการทำความสะอาดเสร็จสิ้นได้
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Toast Notifications -->
    <transition name="toast">
      <div
        v-if="toast.show"
        :class="[
          'fixed top-6 right-6 z-50 px-6 py-4 rounded-xl shadow-2xl flex items-center space-x-3 max-w-md',
          toast.type === 'success' ? 'bg-green-500' : 'bg-red-500'
        ]"
      >
        <svg class="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20">
          <path v-if="toast.type === 'success'" fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
          <path v-else fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/>
        </svg>
        <span class="text-white font-medium">{{ toast.message }}</span>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const router = useRouter()

// Get query parameters
const roomId = ref<number | null>(null)
const fromHousekeeping = ref(false)
const housekeepingTaskId = ref<string | null>(null)

// State
const loading = ref(true)
const error = ref('')
const submitting = ref(false)
const roomInfo = ref<any>(null)

const formData = ref({
  room_id: 0,
  title: '',
  description: '',
  category: '',
  priority: 'high' // Default to high priority for housekeeping-reported issues
})

const toast = ref({
  show: false,
  type: 'success' as 'success' | 'error',
  message: ''
})

// Show toast
function showToast(type: 'success' | 'error', message: string) {
  toast.value = { show: true, type, message }
  setTimeout(() => {
    toast.value.show = false
  }, 3000)
}

// Fetch room info (from query params, no API call needed)
function loadRoomInfoFromParams() {
  if (!roomId.value) {
    error.value = 'ไม่พบข้อมูลห้อง'
    loading.value = false
    return
  }

  // Get room info from query parameters (passed from housekeeping page)
  const roomNumber = route.query.room_number as string
  const roomTypeName = route.query.room_type_name as string

  if (roomNumber) {
    roomInfo.value = {
      id: roomId.value,
      room_number: roomNumber,
      room_type_name: roomTypeName || 'ไม่ระบุ'
    }
    formData.value.room_id = roomId.value
  } else {
    // If no room info in params, we can't display properly
    error.value = 'ไม่พบข้อมูลห้อง กรุณาเข้าผ่านลิงก์จากหน้างานทำความสะอาด'
  }

  loading.value = false
}

// Submit form
async function handleSubmit() {
  if (!formData.value.title || !formData.value.category) {
    showToast('error', 'กรุณากรอกข้อมูลให้ครบถ้วน')
    return
  }

  submitting.value = true

  try {
    await axios.post('http://localhost:8000/api/v1/public/maintenance/report', formData.value)
    showToast('success', 'แจ้งซ่อมเรียบร้อยแล้ว')

    // Wait for toast to show, then redirect
    setTimeout(() => {
      if (fromHousekeeping.value && housekeepingTaskId.value) {
        // Go back to housekeeping task
        window.location.href = `http://localhost:5173/public/housekeeping/tasks/${housekeepingTaskId.value}`
      } else {
        // Reset form for new report
        formData.value.title = ''
        formData.value.description = ''
        formData.value.category = ''
      }
    }, 2000)
  } catch (err: any) {
    showToast('error', err.response?.data?.detail || 'ไม่สามารถแจ้งซ่อมได้')
  } finally {
    submitting.value = false
  }
}

// Go back to housekeeping task
function goBack() {
  if (housekeepingTaskId.value) {
    window.location.href = `http://localhost:5173/public/housekeeping/tasks/${housekeepingTaskId.value}`
  } else {
    window.history.back()
  }
}

// Lifecycle
onMounted(() => {
  // Parse query parameters
  const roomIdParam = route.query.room_id
  const fromHousekeepingParam = route.query.from_housekeeping
  const taskIdParam = route.query.task_id

  if (roomIdParam) {
    roomId.value = parseInt(roomIdParam as string)
  }

  fromHousekeeping.value = fromHousekeepingParam === 'true'

  if (taskIdParam) {
    housekeepingTaskId.value = taskIdParam as string
  }

  loadRoomInfoFromParams()
})
</script>

<style scoped>
/* Toast animation */
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateY(-20px);
}

.toast-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}
</style>
