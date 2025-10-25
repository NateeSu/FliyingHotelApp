<template>
  <div class="min-h-screen bg-gray-50 p-6">
    <!-- Header -->
    <div class="mb-8 bg-gradient-to-br from-purple-600 via-pink-600 to-red-600 rounded-3xl shadow-2xl p-8 relative overflow-hidden">
      <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-10 animate-shimmer"></div>
      <div class="relative z-10">
        <h1 class="text-4xl font-bold text-white mb-2">ตั้งค่าระบบ</h1>
        <p class="text-pink-100">จัดการการตั้งค่าทั่วไปของระบบ</p>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center py-12">
      <div class="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-purple-600"></div>
    </div>

    <!-- Content -->
    <div v-else class="bg-white rounded-3xl shadow-xl overflow-hidden">
      <!-- Tabs -->
      <div class="border-b border-gray-200">
        <nav class="flex space-x-8 px-8 pt-6">
          <button
            @click="activeTab = 'general'"
            :class="[
              'pb-4 px-1 border-b-2 font-semibold text-sm transition-colors',
              activeTab === 'general'
                ? 'border-purple-600 text-purple-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            <div class="flex items-center space-x-2">
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z"/>
              </svg>
              <span>ตั้งค่าทั่วไป</span>
            </div>
          </button>
          <button
            @click="activeTab = 'telegram'"
            :class="[
              'pb-4 px-1 border-b-2 font-semibold text-sm transition-colors',
              activeTab === 'telegram'
                ? 'border-purple-600 text-purple-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            <div class="flex items-center space-x-2">
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm5.894 8.221l-1.97 9.28c-.145.658-.537.818-1.084.508l-3-2.21-1.446 1.394c-.16.16-.294.294-.602.294l.213-3.054 5.56-5.022c.242-.213-.054-.334-.373-.121L8.736 13.73l-2.98-.924c-.648-.203-.662-.648.136-.96l11.566-4.458c.538-.196 1.006.128.832.833z"/>
              </svg>
              <span>Telegram</span>
            </div>
          </button>
          <!-- More tabs can be added here in future -->
        </nav>
      </div>

      <!-- Tab Content -->
      <div class="p-8">
        <!-- General Settings Tab -->
        <div v-if="activeTab === 'general'" class="space-y-6">
          <!-- Frontend Domain -->
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-2">
              Frontend Domain URL
              <span class="text-red-500">*</span>
            </label>
            <input
              v-model="formValue.general.frontend_domain"
              type="url"
              class="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:outline-none focus:ring-4 focus:ring-purple-200 focus:border-purple-500 transition-all font-mono text-sm"
              placeholder="https://example.com หรือ http://localhost:5173"
            />
            <p class="mt-2 text-xs text-gray-500">
              URL นี้จะใช้ในลิงก์ Telegram เพื่อให้สามารถเข้าถึงระบบได้จากข้อความแจ้งเตือน
            </p>
          </div>

          <!-- Info Box -->
          <div class="bg-blue-50 border-2 border-blue-200 rounded-xl p-4">
            <div class="flex items-start space-x-3">
              <svg class="w-6 h-6 text-blue-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"/>
              </svg>
              <div class="text-sm text-blue-800">
                <p class="font-semibold mb-1">ตัวอย่าง Domain:</p>
                <ul class="list-disc list-inside space-y-1 ml-2">
                  <li>Production: <code class="bg-blue-100 px-1 rounded">https://hotel.example.com</code></li>
                  <li>Localhost: <code class="bg-blue-100 px-1 rounded">http://localhost:5173</code></li>
                  <li>IP Address: <code class="bg-blue-100 px-1 rounded">http://192.168.1.100:5173</code></li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <!-- Telegram Settings Tab -->
        <div v-if="activeTab === 'telegram'" class="space-y-6">
          <!-- Enable/Disable Toggle -->
          <div class="bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl p-6 border-2 border-purple-200">
            <div class="flex items-center justify-between">
              <div>
                <h3 class="text-lg font-bold text-gray-900 mb-1">เปิดใช้งาน Telegram</h3>
                <p class="text-sm text-gray-600">เปิด/ปิดการแจ้งเตือนผ่าน Telegram ทั้งหมด</p>
              </div>
              <label class="relative inline-flex items-center cursor-pointer">
                <input
                  v-model="formValue.telegram.enabled"
                  type="checkbox"
                  class="sr-only peer"
                />
                <div class="w-14 h-7 bg-gray-300 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-200 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[4px] after:bg-white after:rounded-full after:h-6 after:w-6 after:transition-all peer-checked:bg-purple-600"></div>
              </label>
            </div>
          </div>

          <!-- Bot Token -->
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-2">
              Telegram Bot Token
              <span class="text-red-500">*</span>
            </label>
            <input
              v-model="formValue.telegram.bot_token"
              type="text"
              class="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:outline-none focus:ring-4 focus:ring-purple-200 focus:border-purple-500 transition-all font-mono text-sm"
              placeholder="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
            />
            <p class="mt-2 text-xs text-gray-500">
              รับ Bot Token จาก <a href="https://t.me/BotFather" target="_blank" class="text-purple-600 hover:underline">@BotFather</a>
            </p>
          </div>

          <!-- Chat IDs -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Admin Chat ID -->
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-2">
                Admin Group Chat ID
              </label>
              <input
                v-model="formValue.telegram.admin_chat_id"
                type="text"
                class="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:outline-none focus:ring-4 focus:ring-purple-200 focus:border-purple-500 transition-all font-mono text-sm"
                placeholder="-1001234567890"
              />
            </div>

            <!-- Reception Chat ID -->
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-2">
                Reception Group Chat ID
              </label>
              <input
                v-model="formValue.telegram.reception_chat_id"
                type="text"
                class="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:outline-none focus:ring-4 focus:ring-purple-200 focus:border-purple-500 transition-all font-mono text-sm"
                placeholder="-1001234567890"
              />
            </div>

            <!-- Housekeeping Chat ID -->
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-2">
                Housekeeping Group Chat ID
              </label>
              <input
                v-model="formValue.telegram.housekeeping_chat_id"
                type="text"
                class="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:outline-none focus:ring-4 focus:ring-purple-200 focus:border-purple-500 transition-all font-mono text-sm"
                placeholder="-1001234567890"
              />
            </div>

            <!-- Maintenance Chat ID -->
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-2">
                Maintenance Group Chat ID
              </label>
              <input
                v-model="formValue.telegram.maintenance_chat_id"
                type="text"
                class="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:outline-none focus:ring-4 focus:ring-purple-200 focus:border-purple-500 transition-all font-mono text-sm"
                placeholder="-1001234567890"
              />
            </div>
          </div>

          <!-- Helper Text -->
          <div class="bg-blue-50 border-2 border-blue-200 rounded-xl p-4">
            <div class="flex items-start space-x-3">
              <svg class="w-6 h-6 text-blue-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"/>
              </svg>
              <div class="text-sm text-blue-800">
                <p class="font-semibold mb-1">วิธีหา Chat ID:</p>
                <ol class="list-decimal list-inside space-y-1 ml-2">
                  <li>เพิ่ม Bot เข้ากลุ่ม Telegram ที่ต้องการ</li>
                  <li>ส่งข้อความใดๆ ในกลุ่ม</li>
                  <li>เปิด: <code class="bg-blue-100 px-1 rounded">https://api.telegram.org/bot&lt;BOT_TOKEN&gt;/getUpdates</code></li>
                  <li>หา chat.id ในผลลัพธ์ (จะเป็นตัวเลขติดลบ)</li>
                </ol>
              </div>
            </div>
          </div>

          <!-- Test Connection Section -->
          <div class="bg-gray-50 rounded-xl p-6 border-2 border-gray-200">
            <h3 class="text-lg font-bold text-gray-900 mb-4">ทดสอบการเชื่อมต่อ</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <label class="block text-sm font-semibold text-gray-700 mb-2">Bot Token</label>
                <input
                  v-model="testForm.bot_token"
                  type="text"
                  class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 font-mono text-sm"
                  placeholder="ใช้ Bot Token ด้านบน"
                />
              </div>
              <div>
                <label class="block text-sm font-semibold text-gray-700 mb-2">Chat ID</label>
                <input
                  v-model="testForm.chat_id"
                  type="text"
                  class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 font-mono text-sm"
                  placeholder="กรอก Chat ID ที่ต้องการทดสอบ"
                />
              </div>
            </div>
            <button
              @click="handleTestConnection"
              :disabled="testing || !testForm.bot_token || !testForm.chat_id"
              class="w-full px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-xl font-semibold hover:from-purple-700 hover:to-pink-700 transition-all shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
            >
              <svg v-if="testing" class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span>{{ testing ? 'กำลังทดสอบ...' : 'ทดสอบการเชื่อมต่อ' }}</span>
            </button>

            <!-- Test Result -->
            <div v-if="testResult" class="mt-4">
              <div
                :class="[
                  'p-4 rounded-xl border-2',
                  testResult.success
                    ? 'bg-green-50 border-green-200'
                    : 'bg-red-50 border-red-200'
                ]"
              >
                <div class="flex items-start space-x-3">
                  <svg
                    :class="testResult.success ? 'text-green-600' : 'text-red-600'"
                    class="w-6 h-6 flex-shrink-0"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path v-if="testResult.success" fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                    <path v-else fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/>
                  </svg>
                  <div>
                    <p :class="testResult.success ? 'text-green-800' : 'text-red-800'" class="font-semibold">
                      {{ testResult.message }}
                    </p>
                    <p v-if="testResult.bot_info" class="text-sm text-gray-600 mt-1">
                      Bot: {{ testResult.bot_info.first_name }}
                      <span v-if="testResult.bot_info.username">(@{{ testResult.bot_info.username }})</span>
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="flex justify-end space-x-4 pt-4 border-t">
            <button
              @click="handleReset"
              class="px-6 py-3 bg-gray-200 text-gray-700 rounded-xl font-semibold hover:bg-gray-300 transition-colors"
            >
              รีเซ็ต
            </button>
            <button
              @click="handleSaveSettings"
              :disabled="saving"
              class="px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-xl font-semibold hover:from-purple-700 hover:to-pink-700 transition-all shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
            >
              <svg v-if="saving" class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span>{{ saving ? 'กำลังบันทึก...' : 'บันทึกการตั้งค่า' }}</span>
            </button>
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
import { getSettings, updateSettings, testTelegramConnection } from '@/api/settings'
import type { SystemSettings, TelegramTestResponse } from '@/api/settings'

// State
const activeTab = ref('telegram')
const loading = ref(false)
const saving = ref(false)
const testing = ref(false)

const formValue = ref<SystemSettings>({
  telegram: {
    bot_token: '',
    admin_chat_id: '',
    reception_chat_id: '',
    housekeeping_chat_id: '',
    maintenance_chat_id: '',
    enabled: false
  },
  general: {
    frontend_domain: 'http://localhost:5173'
  }
})

const originalSettings = ref<SystemSettings | null>(null)

const testForm = ref({
  bot_token: '',
  chat_id: ''
})

const testResult = ref<TelegramTestResponse | null>(null)

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

// Fetch settings
async function fetchSettings() {
  loading.value = true
  try {
    const settings = await getSettings()
    formValue.value = JSON.parse(JSON.stringify(settings))
    originalSettings.value = JSON.parse(JSON.stringify(settings))

    // Pre-fill test form with current bot token
    testForm.value.bot_token = settings.telegram.bot_token
  } catch (error: any) {
    showToast('error', error.response?.data?.detail || 'ไม่สามารถโหลดการตั้งค่าได้')
  } finally {
    loading.value = false
  }
}

// Save settings
async function handleSaveSettings() {
  saving.value = true
  try {
    const updated = await updateSettings(formValue.value)
    formValue.value = JSON.parse(JSON.stringify(updated))
    originalSettings.value = JSON.parse(JSON.stringify(updated))
    showToast('success', 'บันทึกการตั้งค่าสำเร็จ')
  } catch (error: any) {
    showToast('error', error.response?.data?.detail || 'ไม่สามารถบันทึกการตั้งค่าได้')
  } finally {
    saving.value = false
  }
}

// Reset to original
function handleReset() {
  if (originalSettings.value) {
    formValue.value = JSON.parse(JSON.stringify(originalSettings.value))
    showToast('success', 'รีเซ็ตการตั้งค่าเรียบร้อย')
  }
}

// Test Telegram connection
async function handleTestConnection() {
  testing.value = true
  testResult.value = null
  try {
    const result = await testTelegramConnection(testForm.value.bot_token, testForm.value.chat_id)
    testResult.value = result
  } catch (error: any) {
    testResult.value = {
      success: false,
      message: error.response?.data?.detail || 'ไม่สามารถทดสอบการเชื่อมต่อได้'
    }
  } finally {
    testing.value = false
  }
}

// Lifecycle
onMounted(() => {
  fetchSettings()
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
