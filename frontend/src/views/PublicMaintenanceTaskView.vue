<template>
  <div class="min-h-screen bg-gradient-to-br from-orange-50 via-yellow-50 to-red-50 p-4 md:p-8">
    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center min-h-screen">
      <div class="text-center">
        <div class="animate-spin rounded-full h-20 w-20 border-t-4 border-b-4 border-orange-600 mx-auto mb-4"></div>
        <p class="text-gray-600 font-medium">กำลังโหลดข้อมูล...</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="max-w-2xl mx-auto mt-20">
      <div class="bg-white rounded-3xl shadow-2xl p-8 text-center">
        <div class="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg class="w-10 h-10 text-red-600" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/>
          </svg>
        </div>
        <h2 class="text-2xl font-bold text-gray-900 mb-2">เกิดข้อผิดพลาด</h2>
        <p class="text-gray-600">{{ error }}</p>
      </div>
    </div>

    <!-- Task Detail -->
    <div v-else-if="task" class="max-w-4xl mx-auto">
      <!-- Header -->
      <div class="bg-gradient-to-br from-orange-600 via-yellow-600 to-red-600 rounded-3xl shadow-2xl p-8 mb-6 relative overflow-hidden">
        <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-10 animate-shimmer"></div>
        <div class="relative z-10">
          <div class="flex items-center justify-between mb-4">
            <h1 class="text-3xl md:text-4xl font-bold text-white">งานซ่อมบำรุง</h1>
            <span :class="getStatusBadgeClass(task.status)" class="px-4 py-2 rounded-xl font-bold text-sm shadow-lg">
              {{ getStatusLabel(task.status) }}
            </span>
          </div>
          <div class="flex items-center space-x-3 text-white">
            <svg class="w-8 h-8" fill="currentColor" viewBox="0 0 24 24">
              <path d="M22.7 19l-9.1-9.1c.9-2.3.4-5-1.5-6.9-2-2-5-2.4-7.4-1.3L9 6 6 9 1.6 4.7C.4 7.1.9 10.1 2.9 12.1c1.9 1.9 4.6 2.4 6.9 1.5l9.1 9.1c.4.4 1 .4 1.4 0l2.3-2.3c.5-.4.5-1.1.1-1.4z"/>
            </svg>
            <div>
              <p class="text-xl font-bold">ห้อง {{ task.room?.room_number }}</p>
              <p class="text-orange-100">{{ task.room?.room_type?.name }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Task Information Card -->
      <div class="bg-white rounded-3xl shadow-2xl p-8 mb-6">
        <h2 class="text-2xl font-bold text-gray-900 mb-6 flex items-center">
          <svg class="w-7 h-7 mr-3 text-orange-600" fill="currentColor" viewBox="0 0 20 20">
            <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z"/>
            <path fill-rule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3zm-3 4a1 1 0 100 2h.01a1 1 0 100-2H7zm3 0a1 1 0 100 2h3a1 1 0 100-2h-3z" clip-rule="evenodd"/>
          </svg>
          รายละเอียดงาน
        </h2>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Title -->
          <div class="md:col-span-2">
            <label class="block text-sm font-semibold text-gray-500 mb-1">หัวข้องาน</label>
            <p class="text-lg font-bold text-gray-900">{{ task.title }}</p>
          </div>

          <!-- Description -->
          <div v-if="task.description" class="md:col-span-2">
            <label class="block text-sm font-semibold text-gray-500 mb-1">รายละเอียด</label>
            <p class="text-gray-700">{{ task.description }}</p>
          </div>

          <!-- Category -->
          <div>
            <label class="block text-sm font-semibold text-gray-500 mb-1">ประเภท</label>
            <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold bg-purple-100 text-purple-800">
              {{ getCategoryLabel(task.category) }}
            </span>
          </div>

          <!-- Priority -->
          <div>
            <label class="block text-sm font-semibold text-gray-500 mb-1">ลำดับความสำคัญ</label>
            <span :class="getPriorityBadgeClass(task.priority)" class="inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold">
              {{ getPriorityLabel(task.priority) }}
            </span>
          </div>

          <!-- Assigned To -->
          <div v-if="task.assigned_user">
            <label class="block text-sm font-semibold text-gray-500 mb-1">มอบหมายให้</label>
            <p class="text-gray-900 font-medium">{{ task.assigned_user.full_name }}</p>
          </div>

          <!-- Created At -->
          <div>
            <label class="block text-sm font-semibold text-gray-500 mb-1">สร้างเมื่อ</label>
            <p class="text-gray-900">{{ formatDateTime(task.created_at) }}</p>
          </div>

          <!-- Started At -->
          <div v-if="task.started_at">
            <label class="block text-sm font-semibold text-gray-500 mb-1">เริ่มงานเมื่อ</label>
            <p class="text-gray-900">{{ formatDateTime(task.started_at) }}</p>
          </div>

          <!-- Completed At -->
          <div v-if="task.completed_at" class="md:col-span-2">
            <label class="block text-sm font-semibold text-gray-500 mb-1">เสร็จสิ้นเมื่อ</label>
            <p class="text-gray-900">{{ formatDateTime(task.completed_at) }}</p>
            <p v-if="task.duration_minutes" class="text-sm text-gray-600 mt-1">
              ใช้เวลา: {{ task.duration_minutes }} นาที
            </p>
          </div>

          <!-- Notes -->
          <div v-if="task.notes" class="md:col-span-2">
            <label class="block text-sm font-semibold text-gray-500 mb-1">หมายเหตุ</label>
            <p class="text-gray-700 whitespace-pre-wrap">{{ task.notes }}</p>
          </div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="bg-white rounded-3xl shadow-2xl p-8">
        <h3 class="text-xl font-bold text-gray-900 mb-4">ดำเนินการ</h3>

        <!-- Start Task Button -->
        <button
          v-if="task.status === 'pending'"
          @click="handleStartTask"
          :disabled="processing"
          class="w-full mb-4 px-6 py-4 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-xl font-bold text-lg hover:from-green-600 hover:to-emerald-700 transition-all shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-3"
        >
          <svg v-if="processing" class="animate-spin h-6 w-6" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <svg v-else class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clip-rule="evenodd"/>
          </svg>
          <span>{{ processing ? 'กำลังเริ่มงาน...' : 'เริ่มทำงาน' }}</span>
        </button>

        <!-- Complete Task Button -->
        <button
          v-if="task.status === 'in_progress'"
          @click="showCompleteModal = true"
          class="w-full mb-4 px-6 py-4 bg-gradient-to-r from-orange-500 to-red-600 text-white rounded-xl font-bold text-lg hover:from-orange-600 hover:to-red-700 transition-all shadow-lg hover:shadow-xl flex items-center justify-center space-x-3"
        >
          <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
          </svg>
          <span>ซ่อมบำรุงเสร็จสิ้น</span>
        </button>

        <!-- Completed Badge -->
        <div v-if="task.status === 'completed'" class="text-center py-4">
          <div class="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg class="w-10 h-10 text-green-600" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
            </svg>
          </div>
          <p class="text-xl font-bold text-gray-900">งานเสร็จสิ้นแล้ว</p>
          <p class="text-gray-600">ขอบคุณสำหรับการทำงาน</p>
        </div>
      </div>
    </div>

    <!-- Complete Task Modal -->
    <transition name="modal">
      <div
        v-if="showCompleteModal"
        class="fixed inset-0 z-50 overflow-y-auto"
        @click.self="showCompleteModal = false"
      >
        <div class="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:p-0">
          <!-- Backdrop -->
          <div class="fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm transition-opacity"></div>

          <!-- Modal -->
          <div class="relative inline-block align-bottom bg-white rounded-3xl text-left overflow-hidden shadow-2xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
            <!-- Header -->
            <div class="bg-gradient-to-r from-orange-600 to-red-600 px-8 py-6">
              <h3 class="text-2xl font-bold text-white">ยืนยันการทำงานเสร็จสิ้น</h3>
            </div>

            <!-- Form -->
            <div class="px-8 py-6">
              <label class="block text-sm font-semibold text-gray-700 mb-2">หมายเหตุ (ถ้ามี)</label>
              <textarea
                v-model="completeNotes"
                rows="4"
                class="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:outline-none focus:ring-4 focus:ring-orange-200 focus:border-orange-500 transition-all"
                placeholder="เช่น ซ่อมแซมเรียบร้อยแล้ว, ต้องเปลี่ยนอุปกรณ์..."
              ></textarea>
            </div>

            <!-- Footer -->
            <div class="bg-gray-50 px-8 py-4 flex justify-end space-x-3">
              <button
                @click="showCompleteModal = false"
                class="px-6 py-2.5 bg-gray-200 text-gray-700 rounded-xl font-semibold hover:bg-gray-300 transition-colors"
              >
                ยกเลิก
              </button>
              <button
                @click="handleCompleteTask"
                :disabled="processing"
                class="px-6 py-2.5 bg-gradient-to-r from-orange-600 to-red-600 text-white rounded-xl font-semibold hover:from-orange-700 hover:to-red-700 transition-all shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
              >
                <svg v-if="processing" class="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span>{{ processing ? 'กำลังบันทึก...' : 'ยืนยัน' }}</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </transition>

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
import { useRoute } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const taskId = route.params.taskId as string

// State
const task = ref<any>(null)
const loading = ref(true)
const error = ref('')
const processing = ref(false)
const showCompleteModal = ref(false)
const completeNotes = ref('')

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

// Fetch task
async function fetchTask() {
  loading.value = true
  error.value = ''

  try {
    const response = await axios.get(`http://localhost:8000/api/v1/public/maintenance/tasks/${taskId}`)
    task.value = response.data
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'ไม่สามารถโหลดข้อมูลงานได้'
  } finally {
    loading.value = false
  }
}

// Start task
async function handleStartTask() {
  processing.value = true

  try {
    await axios.post(`http://localhost:8000/api/v1/public/maintenance/tasks/${taskId}/start`, {})
    showToast('success', 'เริ่มงานเรียบร้อยแล้ว')
    await fetchTask()
  } catch (err: any) {
    showToast('error', err.response?.data?.detail || 'ไม่สามารถเริ่มงานได้')
  } finally {
    processing.value = false
  }
}

// Complete task
async function handleCompleteTask() {
  processing.value = true

  try {
    await axios.post(`http://localhost:8000/api/v1/public/maintenance/tasks/${taskId}/complete`, {
      notes: completeNotes.value || undefined
    })
    showToast('success', 'ทำงานเสร็จสิ้นเรียบร้อยแล้ว')
    showCompleteModal.value = false
    await fetchTask()
  } catch (err: any) {
    showToast('error', err.response?.data?.detail || 'ไม่สามารถบันทึกการทำงานเสร็จสิ้นได้')
  } finally {
    processing.value = false
  }
}

// Format datetime
function formatDateTime(dateString: string): string {
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('th-TH', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date)
}

// Status labels and styles
function getStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    pending: 'รอดำเนินการ',
    in_progress: 'กำลังทำงาน',
    completed: 'เสร็จสิ้น',
    cancelled: 'ยกเลิก'
  }
  return labels[status] || status
}

function getStatusBadgeClass(status: string): string {
  const classes: Record<string, string> = {
    pending: 'bg-yellow-100 text-yellow-800',
    in_progress: 'bg-blue-100 text-blue-800',
    completed: 'bg-green-100 text-green-800',
    cancelled: 'bg-red-100 text-red-800'
  }
  return classes[status] || 'bg-gray-100 text-gray-800'
}

// Category labels
function getCategoryLabel(category: string): string {
  const labels: Record<string, string> = {
    electrical: 'ไฟฟ้า',
    plumbing: 'ประปา',
    air_conditioning: 'เครื่องปรับอากาศ',
    furniture: 'เฟอร์นิเจอร์',
    electronics: 'อุปกรณ์อิเล็กทรอนิกส์',
    other: 'อื่นๆ'
  }
  return labels[category] || category
}

// Priority labels and styles
function getPriorityLabel(priority: string): string {
  const labels: Record<string, string> = {
    low: 'ต่ำ',
    medium: 'ปานกลาง',
    high: 'สูง',
    urgent: 'ด่วนมาก'
  }
  return labels[priority] || priority
}

function getPriorityBadgeClass(priority: string): string {
  const classes: Record<string, string> = {
    low: 'bg-gray-100 text-gray-800',
    medium: 'bg-blue-100 text-blue-800',
    high: 'bg-orange-100 text-orange-800',
    urgent: 'bg-red-100 text-red-800'
  }
  return classes[priority] || 'bg-gray-100 text-gray-800'
}

// Lifecycle
onMounted(() => {
  fetchTask()
})
</script>

<style scoped>
/* Shimmer animation */
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

/* Modal transition */
.modal-enter-active,
.modal-leave-active {
  transition: all 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from > div > div,
.modal-leave-to > div > div {
  transform: scale(0.9);
}

/* Toast transition */
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateX(100%);
}
</style>
