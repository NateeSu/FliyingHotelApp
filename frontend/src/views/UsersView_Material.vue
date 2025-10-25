<template>
  <div class="min-h-screen bg-gray-50 p-6">
    <!-- Header -->
    <div class="mb-8 bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-600 rounded-3xl shadow-2xl p-8 relative overflow-hidden">
      <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-10 animate-shimmer"></div>
      <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 relative z-10">
        <div>
          <h1 class="text-4xl font-bold text-white mb-2">จัดการผู้ใช้</h1>
          <p class="text-indigo-100">จัดการข้อมูลผู้ใช้งานในระบบ</p>
        </div>
        <button
          @click="openCreateModal"
          class="flex items-center space-x-2 px-6 py-3 bg-white text-indigo-600 rounded-xl font-semibold shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 transition-all duration-200"
        >
          <svg class="w-5 h-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
            <path d="M15 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm-9-2V7H4v3H1v2h3v3h2v-3h3v-2H6zm9 4c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
          </svg>
          <span>เพิ่มผู้ใช้</span>
        </button>
      </div>
    </div>

    <!-- Users Table -->
    <div class="bg-white rounded-3xl shadow-xl overflow-hidden">
      <div v-if="loading" class="p-12 flex justify-center items-center">
        <div class="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-indigo-600"></div>
      </div>

      <div v-else class="overflow-x-auto">
        <table class="min-w-full">
          <thead class="bg-gradient-to-r from-indigo-600 to-purple-600">
            <tr>
              <th class="px-6 py-4 text-left text-sm font-bold text-white uppercase tracking-wider">ชื่อผู้ใช้</th>
              <th class="px-6 py-4 text-left text-sm font-bold text-white uppercase tracking-wider">ชื่อ-นามสกุล</th>
              <th class="px-6 py-4 text-left text-sm font-bold text-white uppercase tracking-wider">บทบาท</th>
              <th class="px-6 py-4 text-left text-sm font-bold text-white uppercase tracking-wider">สถานะ</th>
              <th class="px-6 py-4 text-center text-sm font-bold text-white uppercase tracking-wider">การดำเนินการ</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr v-for="user in users" :key="user.id" class="hover:bg-indigo-50 transition-colors">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="w-10 h-10 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold shadow-md">
                    {{ user.username.charAt(0).toUpperCase() }}
                  </div>
                  <div class="ml-4">
                    <div class="text-sm font-semibold text-gray-900">{{ user.username }}</div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">{{ user.full_name }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="getRoleBadgeClass(user.role)" class="px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full">
                  {{ getRoleLabel(user.role) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'" class="px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full">
                  {{ user.is_active ? 'ใช้งาน' : 'ระงับ' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-center">
                <div class="flex justify-center space-x-2">
                  <button
                    @click="openEditModal(user)"
                    class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-medium text-sm shadow-md hover:shadow-lg"
                  >
                    แก้ไข
                  </button>
                  <button
                    @click="openDeleteModal(user)"
                    class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium text-sm shadow-md hover:shadow-lg"
                  >
                    ลบ
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>

        <div v-if="users.length === 0" class="text-center py-12">
          <p class="text-gray-500 text-lg">ไม่พบข้อมูลผู้ใช้</p>
        </div>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <transition name="modal">
      <div
        v-if="showModal"
        class="fixed inset-0 z-50 overflow-y-auto"
        @click.self="closeModal"
      >
        <div class="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:p-0">
          <!-- Backdrop -->
          <div class="fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm transition-opacity"></div>

          <!-- Modal -->
          <div class="relative inline-block align-bottom bg-white rounded-3xl text-left overflow-hidden shadow-2xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
            <!-- Header -->
            <div class="bg-gradient-to-r from-indigo-600 to-purple-600 px-8 py-6">
              <h3 class="text-2xl font-bold text-white">
                {{ editingUser ? 'แก้ไขผู้ใช้' : 'เพิ่มผู้ใช้' }}
              </h3>
            </div>

            <!-- Form -->
            <div class="px-8 py-6 space-y-6">
              <!-- Username -->
              <div>
                <label class="block text-sm font-semibold text-gray-700 mb-2">ชื่อผู้ใช้</label>
                <input
                  v-model="formValue.username"
                  type="text"
                  :disabled="!!editingUser"
                  class="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:outline-none focus:ring-4 focus:ring-indigo-200 focus:border-indigo-500 transition-all disabled:bg-gray-100 disabled:cursor-not-allowed"
                  placeholder="กรอกชื่อผู้ใช้"
                />
              </div>

              <!-- Password -->
              <div v-if="!editingUser">
                <label class="block text-sm font-semibold text-gray-700 mb-2">รหัสผ่าน</label>
                <input
                  v-model="formValue.password"
                  type="password"
                  class="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:outline-none focus:ring-4 focus:ring-indigo-200 focus:border-indigo-500 transition-all"
                  placeholder="กรอกรหัสผ่าน"
                />
              </div>

              <!-- Full Name -->
              <div>
                <label class="block text-sm font-semibold text-gray-700 mb-2">ชื่อ-นามสกุล</label>
                <input
                  v-model="formValue.full_name"
                  type="text"
                  class="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:outline-none focus:ring-4 focus:ring-indigo-200 focus:border-indigo-500 transition-all"
                  placeholder="กรอกชื่อ-นามสกุล"
                />
              </div>

              <!-- Role -->
              <div>
                <label class="block text-sm font-semibold text-gray-700 mb-2">บทบาท</label>
                <select
                  v-model="formValue.role"
                  class="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:outline-none focus:ring-4 focus:ring-indigo-200 focus:border-indigo-500 transition-all"
                >
                  <option value="admin">ผู้ดูแลระบบ</option>
                  <option value="reception">แผนกต้อนรับ</option>
                  <option value="housekeeping">แผนกแม่บ้าน</option>
                  <option value="maintenance">แผนกซ่อมบำรุง</option>
                </select>
              </div>

              <!-- Telegram User ID -->
              <div>
                <label class="block text-sm font-semibold text-gray-700 mb-2">Telegram User ID</label>
                <input
                  v-model="formValue.telegram_user_id"
                  type="text"
                  class="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:outline-none focus:ring-4 focus:ring-indigo-200 focus:border-indigo-500 transition-all"
                  placeholder="กรอก Telegram User ID (ถ้ามี)"
                />
              </div>

              <!-- Status -->
              <div class="flex items-center space-x-3">
                <label class="relative inline-flex items-center cursor-pointer">
                  <input
                    v-model="formValue.is_active"
                    type="checkbox"
                    class="sr-only peer"
                  />
                  <div class="w-14 h-7 bg-gray-300 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-indigo-200 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[4px] after:bg-white after:rounded-full after:h-6 after:w-6 after:transition-all peer-checked:bg-indigo-600"></div>
                  <span class="ml-3 text-sm font-semibold text-gray-700">
                    {{ formValue.is_active ? 'ใช้งาน' : 'ระงับ' }}
                  </span>
                </label>
              </div>
            </div>

            <!-- Footer -->
            <div class="bg-gray-50 px-8 py-4 flex justify-end space-x-3">
              <button
                @click="closeModal"
                class="px-6 py-2.5 bg-gray-200 text-gray-700 rounded-xl font-semibold hover:bg-gray-300 transition-colors"
              >
                ยกเลิก
              </button>
              <button
                @click="handleSaveUser"
                :disabled="saving"
                class="px-6 py-2.5 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl font-semibold hover:from-indigo-700 hover:to-purple-700 transition-all shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
              >
                <svg v-if="saving" class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span>{{ saving ? 'กำลังบันทึก...' : 'บันทึก' }}</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </transition>

    <!-- Delete Confirmation Modal -->
    <transition name="modal">
      <div
        v-if="showDeleteModal"
        class="fixed inset-0 z-50 overflow-y-auto"
        @click.self="closeDeleteModal"
      >
        <div class="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:p-0">
          <!-- Backdrop -->
          <div class="fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm transition-opacity"></div>

          <!-- Modal -->
          <div class="relative inline-block align-bottom bg-white rounded-3xl text-left overflow-hidden shadow-2xl transform transition-all sm:my-8 sm:align-middle sm:max-w-md sm:w-full">
            <div class="bg-white px-8 py-6">
              <div class="flex items-start space-x-4">
                <div class="flex-shrink-0 w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
                  <svg class="w-6 h-6 text-red-600" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
                  </svg>
                </div>
                <div class="flex-1">
                  <h3 class="text-xl font-bold text-gray-900 mb-2">ยืนยันการลบ</h3>
                  <p class="text-gray-600">คุณแน่ใจหรือไม่ว่าต้องการลบผู้ใช้นี้? การดำเนินการนี้ไม่สามารถย้อนกลับได้</p>
                </div>
              </div>
            </div>
            <div class="bg-gray-50 px-8 py-4 flex justify-end space-x-3">
              <button
                @click="closeDeleteModal"
                :disabled="saving"
                class="px-6 py-2.5 bg-gray-200 text-gray-700 rounded-xl font-semibold hover:bg-gray-300 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                ยกเลิก
              </button>
              <button
                @click="handleConfirmDelete"
                :disabled="saving"
                class="px-6 py-2.5 bg-gradient-to-r from-red-500 to-pink-600 text-white rounded-xl font-semibold hover:from-red-600 hover:to-pink-700 transition-all shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
              >
                <svg v-if="saving" class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span>{{ saving ? 'กำลังลบ...' : 'ลบ' }}</span>
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
        <svg class="w-6 h-6 text-white" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
          <path v-if="toast.type === 'success'" d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
          <path v-else d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
        </svg>
        <span class="text-white font-medium">{{ toast.message }}</span>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from '@/api/axios'
import type { User } from '@/stores/auth'

// State
const users = ref<User[]>([])
const loading = ref(false)
const saving = ref(false)
const showModal = ref(false)
const showDeleteModal = ref(false)
const editingUser = ref<User | null>(null)
const deletingUser = ref<User | null>(null)

const formValue = ref({
  username: '',
  password: '',
  full_name: '',
  role: 'reception' as 'admin' | 'reception' | 'housekeeping' | 'maintenance',
  telegram_user_id: '',
  is_active: true
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

// Fetch users
async function fetchUsers() {
  loading.value = true
  try {
    const response = await axios.get<User[]>('/api/v1/users/')
    users.value = response.data
  } catch (error: any) {
    showToast('error', error.response?.data?.detail || 'ไม่สามารถโหลดข้อมูลผู้ใช้ได้')
  } finally {
    loading.value = false
  }
}

// Open create modal
function openCreateModal() {
  editingUser.value = null
  formValue.value = {
    username: '',
    password: '',
    full_name: '',
    role: 'reception',
    telegram_user_id: '',
    is_active: true
  }
  showModal.value = true
}

// Open edit modal
function openEditModal(user: User) {
  editingUser.value = user
  formValue.value = {
    username: user.username,
    password: '',
    full_name: user.full_name,
    role: user.role.toLowerCase() as any,
    telegram_user_id: user.telegram_user_id || '',
    is_active: user.is_active
  }
  showModal.value = true
}

// Close modal
function closeModal() {
  showModal.value = false
  editingUser.value = null
}

// Open delete modal
function openDeleteModal(user: User) {
  deletingUser.value = user
  showDeleteModal.value = true
}

// Close delete modal
function closeDeleteModal() {
  showDeleteModal.value = false
  deletingUser.value = null
}

// Save user
async function handleSaveUser() {
  if (!formValue.value.username || !formValue.value.full_name) {
    showToast('error', 'กรุณากรอกข้อมูลให้ครบถ้วน')
    return
  }

  if (!editingUser.value && !formValue.value.password) {
    showToast('error', 'กรุณากรอกรหัสผ่าน')
    return
  }

  saving.value = true
  try {
    const payload: any = {
      username: formValue.value.username,
      full_name: formValue.value.full_name,
      role: formValue.value.role,
      telegram_user_id: formValue.value.telegram_user_id || null,
      is_active: formValue.value.is_active
    }

    if (!editingUser.value && formValue.value.password) {
      payload.password = formValue.value.password
    }

    if (editingUser.value) {
      await axios.put(`/api/v1/users/${editingUser.value.id}`, payload)
      showToast('success', 'แก้ไขผู้ใช้สำเร็จ')
    } else {
      await axios.post('/api/v1/users/', payload)
      showToast('success', 'เพิ่มผู้ใช้สำเร็จ')
    }

    await fetchUsers()
    closeModal()
  } catch (error: any) {
    let errorMsg = 'เกิดข้อผิดพลาด'
    if (error.response?.data?.detail) {
      const detail = error.response.data.detail
      if (Array.isArray(detail)) {
        errorMsg = detail.map((err: any) => err.msg || err.message).join(', ')
      } else if (typeof detail === 'string') {
        errorMsg = detail
      }
    }
    showToast('error', errorMsg)
  } finally {
    saving.value = false
  }
}

// Confirm delete
async function handleConfirmDelete() {
  if (!deletingUser.value) return

  saving.value = true
  try {
    await axios.delete(`/api/v1/users/${deletingUser.value.id}`)
    showToast('success', 'ลบผู้ใช้สำเร็จ')
    await fetchUsers()
    closeDeleteModal()
  } catch (error: any) {
    let errorMsg = 'ไม่สามารถลบผู้ใช้ได้'
    if (error.response?.data?.detail) {
      const detail = error.response.data.detail
      if (Array.isArray(detail)) {
        errorMsg = detail.map((err: any) => err.msg || err.message).join(', ')
      } else if (typeof detail === 'string') {
        errorMsg = detail
      }
    } else if (error.message) {
      errorMsg = error.message
    }
    console.error('Delete error:', error)
    showToast('error', errorMsg)
  } finally {
    saving.value = false
  }
}

// Get role label
function getRoleLabel(role: string): string {
  const roleMap: Record<string, string> = {
    admin: 'ผู้ดูแลระบบ',
    reception: 'แผนกต้อนรับ',
    housekeeping: 'แผนกแม่บ้าน',
    maintenance: 'แผนกซ่อมบำรุง'
  }
  return roleMap[role.toLowerCase()] || 'ไม่ทราบ'
}

// Get role badge class
function getRoleBadgeClass(role: string): string {
  const roleClasses: Record<string, string> = {
    admin: 'bg-red-100 text-red-800',
    reception: 'bg-blue-100 text-blue-800',
    housekeeping: 'bg-green-100 text-green-800',
    maintenance: 'bg-yellow-100 text-yellow-800'
  }
  return roleClasses[role.toLowerCase()] || 'bg-gray-100 text-gray-800'
}

// Lifecycle
onMounted(() => {
  fetchUsers()
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
