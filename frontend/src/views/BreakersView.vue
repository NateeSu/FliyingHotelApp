<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 via-cyan-50 to-teal-50 p-6">
    <!-- Header -->
    <div class="max-w-7xl mx-auto mb-8">
      <!-- HA Not Configured Warning -->
      <div v-if="statistics && statistics.total_breakers > 0 && statistics.offline_breakers === statistics.total_breakers" class="mb-6 p-4 bg-yellow-50 border-2 border-yellow-400 rounded-xl flex items-start space-x-3">
        <svg class="w-6 h-6 text-yellow-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
        </svg>
        <div class="flex-1">
          <h3 class="text-yellow-800 font-bold text-lg">⚠️ ไม่สามารถเชื่อมต่อ Home Assistant</h3>
          <p class="text-yellow-700 mt-1">
            กรุณาตั้งค่า Home Assistant URL และ Access Token ที่หน้า
            <a href="/settings" class="underline font-semibold hover:text-yellow-900">Settings</a>
            เพื่อให้ระบบสามารถควบคุม Breaker ได้
          </p>
          <p class="text-yellow-600 text-sm mt-2">
            💡 ข้อมูลที่แสดงในขณะนี้เป็นข้อมูลเก่าจาก database ไม่ใช่สถานะปัจจุบันจริง
          </p>
        </div>
      </div>

      <div class="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 class="text-4xl font-bold bg-gradient-to-r from-blue-600 via-cyan-600 to-teal-600 bg-clip-text text-transparent">
            จัดการเบรกเกอร์ไฟฟ้า
          </h1>
          <p class="text-gray-600 mt-2">Breakers Management</p>
        </div>
        <div class="flex gap-4">
          <button
            @click="handleSyncAll"
            :disabled="syncing"
            class="px-6 py-3 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-xl font-semibold shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            <svg v-if="syncing" class="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
            </svg>
            <span>{{ syncing ? 'กำลังซิงค์...' : 'ซิงค์ทั้งหมด' }}</span>
          </button>
          <button
            @click="openCreateDialog"
            class="px-6 py-3 bg-gradient-to-r from-blue-600 to-cyan-600 text-white rounded-xl font-semibold shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200"
          >
            <span class="text-xl mr-2">+</span> เพิ่ม Breaker
          </button>
        </div>
      </div>

      <!-- Statistics -->
      <div v-if="statistics" class="mt-6 grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-4">
        <div class="bg-white rounded-xl p-4 shadow-lg">
          <div class="text-2xl font-bold text-blue-600">{{ statistics.total_breakers }}</div>
          <div class="text-xs text-gray-600 mt-1">ทั้งหมด</div>
        </div>
        <div class="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-4 shadow-lg border-2 border-green-200">
          <div class="text-2xl font-bold text-green-600">{{ statistics.online_breakers }}</div>
          <div class="text-xs text-gray-600 mt-1">ออนไลน์</div>
        </div>
        <div class="bg-gradient-to-br from-red-50 to-orange-50 rounded-xl p-4 shadow-lg border-2 border-red-200">
          <div class="text-2xl font-bold text-red-600">{{ statistics.offline_breakers }}</div>
          <div class="text-xs text-gray-600 mt-1">ออฟไลน์</div>
        </div>
        <div class="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-4 shadow-lg">
          <div class="text-2xl font-bold text-green-700">{{ statistics.breakers_on }}</div>
          <div class="text-xs text-gray-600 mt-1">เปิด</div>
        </div>
        <div class="bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl p-4 shadow-lg">
          <div class="text-2xl font-bold text-gray-700">{{ statistics.breakers_off }}</div>
          <div class="text-xs text-gray-600 mt-1">ปิด</div>
        </div>
        <div class="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-4 shadow-lg">
          <div class="text-2xl font-bold text-purple-700">{{ statistics.auto_control_enabled }}</div>
          <div class="text-xs text-gray-600 mt-1">ควบคุมอัตโนมัติ</div>
        </div>
        <div class="bg-gradient-to-br from-yellow-50 to-yellow-100 rounded-xl p-4 shadow-lg">
          <div class="text-2xl font-bold text-yellow-700">{{ statistics.breakers_with_errors }}</div>
          <div class="text-xs text-gray-600 mt-1">มีข้อผิดพลาด</div>
        </div>
        <div class="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-4 shadow-lg">
          <div class="text-2xl font-bold text-blue-700">{{ statistics.avg_response_time_ms || '-' }}</div>
          <div class="text-xs text-gray-600 mt-1">Response (ms)</div>
        </div>
      </div>

      <!-- Filters -->
      <div class="mt-6 flex flex-wrap gap-4">
        <select
          v-model="filterRoomId"
          @change="applyFilters"
          class="px-4 py-2 border-2 border-gray-300 rounded-xl focus:border-blue-500 focus:outline-none"
        >
          <option :value="null">ทุกห้อง</option>
          <template v-for="breaker in breakersStore.breakers" :key="breaker.id">
            <option v-if="breaker.room_id" :value="breaker.room_id">
              ห้อง {{ breaker.room_number }}
            </option>
          </template>
        </select>

        <select
          v-model="filterState"
          @change="applyFilters"
          class="px-4 py-2 border-2 border-gray-300 rounded-xl focus:border-blue-500 focus:outline-none"
        >
          <option :value="null">ทุกสถานะ</option>
          <option value="ON">เปิด</option>
          <option value="OFF">ปิด</option>
          <option value="UNAVAILABLE">ไม่พร้อมใช้งาน</option>
        </select>

        <select
          v-model="filterAutoControl"
          @change="applyFilters"
          class="px-4 py-2 border-2 border-gray-300 rounded-xl focus:border-blue-500 focus:outline-none"
        >
          <option :value="null">ทุกโหมด</option>
          <option :value="true">ควบคุมอัตโนมัติ</option>
          <option :value="false">ควบคุมด้วยตนเอง</option>
        </select>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="breakersStore.isLoading" class="max-w-7xl mx-auto">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div v-for="i in 6" :key="i" class="animate-pulse">
          <div class="bg-white rounded-2xl h-48 shadow-lg"></div>
        </div>
      </div>
    </div>

    <!-- Breakers Grid -->
    <div v-else class="max-w-7xl mx-auto">
      <div v-if="breakersStore.breakers.length === 0" class="text-center py-16">
        <div class="text-gray-400 text-6xl mb-4">⚡</div>
        <p class="text-gray-600 text-xl">ยังไม่มี Breaker</p>
        <p class="text-gray-400 mt-2">คลิกปุ่ม "เพิ่ม Breaker" เพื่อเริ่มต้น</p>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="breaker in breakersStore.breakers"
          :key="breaker.id"
          :class="[
            'rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 overflow-hidden',
            getBreakerCardClass(breaker.current_state, breaker.is_available)
          ]"
        >
          <!-- Header -->
          <div class="p-6">
            <div class="flex items-center justify-between mb-4">
              <div>
                <h3 class="text-xl font-bold text-gray-800">{{ breaker.friendly_name }}</h3>
                <p class="text-sm text-gray-600 font-mono">{{ breaker.entity_id }}</p>
              </div>
              <div :class="['w-4 h-4 rounded-full', breaker.is_available ? 'bg-green-500 animate-pulse' : 'bg-red-500']"></div>
            </div>

            <!-- Room Info -->
            <div v-if="breaker.room_id" class="mb-4">
              <span class="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-semibold">
                🚪 ห้อง {{ breaker.room_number }} ({{ breaker.room_status }})
              </span>
            </div>
            <div v-else class="mb-4">
              <span class="px-3 py-1 bg-gray-100 text-gray-600 rounded-full text-sm">
                ไม่ได้ผูกกับห้อง
              </span>
            </div>

            <!-- Status Badge -->
            <div class="mb-4">
              <span :class="['px-4 py-2 rounded-xl text-sm font-bold inline-block', getStateBadgeClass(breaker.current_state)]">
                {{ getStateLabel(breaker.current_state) }}
              </span>
            </div>

            <!-- Auto Control -->
            <div class="flex items-center space-x-2 text-sm mb-4">
              <span :class="breaker.auto_control_enabled ? 'text-purple-600' : 'text-gray-400'">
                {{ breaker.auto_control_enabled ? '🤖 ควบคุมอัตโนมัติ' : '🎮 ควบคุมด้วยตนเอง' }}
              </span>
            </div>

            <!-- Error Info -->
            <div v-if="breaker.consecutive_errors > 0" class="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
              <p class="text-sm text-red-800">
                ⚠️ ข้อผิดพลาด: {{ breaker.consecutive_errors }} ครั้ง
              </p>
              <p v-if="breaker.last_error_message" class="text-xs text-red-600 mt-1">
                {{ breaker.last_error_message }}
              </p>
            </div>

            <!-- Last Update -->
            <div v-if="breaker.last_state_update" class="text-xs text-gray-500 mb-4">
              อัปเดตล่าสุด: {{ formatDateTime(breaker.last_state_update) }}
            </div>

            <!-- Control Buttons -->
            <div class="flex gap-2">
              <button
                @click="handleTurnOn(breaker.id)"
                :disabled="!breaker.is_available || breaker.current_state === 'ON'"
                class="flex-1 px-4 py-2 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-lg font-semibold hover:from-green-700 hover:to-emerald-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed text-sm"
              >
                เปิด
              </button>
              <button
                @click="handleTurnOff(breaker.id)"
                :disabled="!breaker.is_available || breaker.current_state === 'OFF'"
                class="flex-1 px-4 py-2 bg-gradient-to-r from-gray-600 to-gray-700 text-white rounded-lg font-semibold hover:from-gray-700 hover:to-gray-800 transition-all disabled:opacity-50 disabled:cursor-not-allowed text-sm"
              >
                ปิด
              </button>
              <button
                @click="handleSync(breaker.id)"
                class="px-4 py-2 bg-blue-100 text-blue-700 rounded-lg font-semibold hover:bg-blue-200 transition-all text-sm"
              >
                ↻
              </button>
            </div>

            <!-- Action Buttons -->
            <div class="mt-4 flex gap-2">
              <button
                @click="openEditDialog(breaker)"
                class="flex-1 px-4 py-2 bg-purple-100 text-purple-700 rounded-lg font-semibold hover:bg-purple-200 transition-all text-sm"
              >
                แก้ไข
              </button>
              <button
                @click="openLogsDialog(breaker)"
                class="flex-1 px-4 py-2 bg-cyan-100 text-cyan-700 rounded-lg font-semibold hover:bg-cyan-200 transition-all text-sm"
              >
                ประวัติ
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create/Edit Dialog -->
    <div
      v-if="showDialog"
      class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50"
      @click.self="closeDialog"
    >
      <div class="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <!-- Dialog Header -->
        <div class="bg-gradient-to-r from-blue-600 via-cyan-600 to-teal-600 p-6 text-white">
          <h2 class="text-2xl font-bold">
            {{ isEditing ? 'แก้ไข Breaker' : 'เพิ่ม Breaker ใหม่' }}
          </h2>
        </div>

        <!-- Dialog Body -->
        <form @submit.prevent="handleSubmit" class="p-6 space-y-6">
          <!-- Entity ID -->
          <div>
            <label class="block text-gray-700 font-semibold mb-2">
              Entity ID <span class="text-red-500">*</span>
            </label>
            <input
              v-model="formData.entity_id"
              type="text"
              required
              placeholder="switch.room_101_breaker"
              class="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:border-blue-500 focus:outline-none transition-colors font-mono text-sm"
            />
            <p class="text-xs text-gray-500 mt-1">รูปแบบ: domain.entity_name เช่น switch.breaker_101</p>
          </div>

          <!-- Friendly Name -->
          <div>
            <label class="block text-gray-700 font-semibold mb-2">
              ชื่อเรียก <span class="text-red-500">*</span>
            </label>
            <input
              v-model="formData.friendly_name"
              type="text"
              required
              placeholder="เบรกเกอร์ห้อง 101"
              class="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:border-blue-500 focus:outline-none transition-colors"
            />
          </div>

          <!-- Room Selection -->
          <div>
            <label class="block text-gray-700 font-semibold mb-2">
              ผูกกับห้อง
            </label>
            <select
              v-model="formData.room_id"
              class="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:border-blue-500 focus:outline-none transition-colors"
            >
              <option :value="null">-- ไม่ผูกกับห้อง --</option>
              <option v-for="room in availableRooms" :key="room.id" :value="room.id">
                {{ room.room_number }} - {{ room.room_type?.name }}
              </option>
            </select>
            <p class="text-xs text-gray-500 mt-1">แนะนำให้ผูก Breaker กับห้องเพื่อใช้งานระบบควบคุมอัตโนมัติ</p>
          </div>

          <!-- Auto Control -->
          <div class="flex items-center space-x-3 p-4 bg-purple-50 rounded-xl">
            <input
              v-model="formData.auto_control_enabled"
              type="checkbox"
              id="auto_control"
              class="w-5 h-5 text-purple-600 rounded focus:ring-2 focus:ring-purple-500"
            />
            <label for="auto_control" class="text-gray-700 font-semibold cursor-pointer">
              เปิดใช้งานระบบควบคุมอัตโนมัติ
            </label>
          </div>
          <p class="text-sm text-gray-600">
            เมื่อเปิดระบบควบคุมอัตโนมัติ: Breaker จะเปิดเมื่อห้องมีผู้พักหรือกำลังทำความสะอาด และจะปิดเมื่อห้องว่าง
          </p>

          <!-- Action Buttons -->
          <div class="flex justify-between pt-4 border-t">
            <button
              v-if="isEditing"
              type="button"
              @click="handleDelete"
              class="px-6 py-3 bg-red-100 text-red-700 rounded-xl font-semibold hover:bg-red-200 transition-colors"
            >
              ลบ Breaker
            </button>
            <div v-else></div>

            <div class="flex space-x-4">
              <button
                type="button"
                @click="closeDialog"
                class="px-6 py-3 bg-gray-200 text-gray-700 rounded-xl font-semibold hover:bg-gray-300 transition-colors"
              >
                ยกเลิก
              </button>
              <button
                type="submit"
                :disabled="submitting"
                class="px-6 py-3 bg-gradient-to-r from-blue-600 to-cyan-600 text-white rounded-xl font-semibold hover:from-blue-700 hover:to-cyan-700 transition-all shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {{ submitting ? 'กำลังบันทึก...' : 'บันทึก' }}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>

    <!-- Logs Dialog -->
    <div
      v-if="showLogsDialog"
      class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50"
      @click.self="closeLogsDialog"
    >
      <div class="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        <!-- Dialog Header -->
        <div class="bg-gradient-to-r from-cyan-600 to-teal-600 p-6 text-white">
          <h2 class="text-2xl font-bold">ประวัติการทำงาน</h2>
          <p class="text-sm opacity-90 mt-1">{{ selectedBreaker?.friendly_name }}</p>
        </div>

        <!-- Logs List -->
        <div class="flex-1 overflow-y-auto p-6 space-y-4">
          <div v-if="breakersStore.activityLogs.length === 0" class="text-center py-16 text-gray-400">
            ไม่มีประวัติการทำงาน
          </div>

          <div
            v-for="log in breakersStore.activityLogs"
            :key="log.id"
            class="bg-gray-50 rounded-xl p-4 border-l-4"
            :class="getLogBorderClass(log.status)"
          >
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <div class="flex items-center space-x-3 mb-2">
                  <span :class="['px-3 py-1 rounded-full text-xs font-bold', getActionBadgeClass(log.action)]">
                    {{ getActionLabel(log.action) }}
                  </span>
                  <span :class="['px-3 py-1 rounded-full text-xs font-bold', getTriggerBadgeClass(log.trigger_type)]">
                    {{ getTriggerLabel(log.trigger_type) }}
                  </span>
                  <span :class="['px-3 py-1 rounded-full text-xs font-bold', getStatusBadgeClass(log.status)]">
                    {{ getStatusLabel(log.status) }}
                  </span>
                </div>

                <div class="text-sm text-gray-700 space-y-1">
                  <p v-if="log.triggered_by_name">โดย: {{ log.triggered_by_name }}</p>
                  <p v-if="log.room_status_before && log.room_status_after">
                    สถานะห้อง: {{ log.room_status_before }} → {{ log.room_status_after }}
                  </p>
                  <p v-if="log.error_message" class="text-red-600">
                    ⚠️ {{ log.error_message }}
                  </p>
                  <p v-if="log.response_time_ms" class="text-gray-500">
                    เวลาตอบสนอง: {{ log.response_time_ms }}ms
                  </p>
                </div>
              </div>

              <div class="text-right text-xs text-gray-500 ml-4">
                {{ formatDateTime(log.created_at) }}
              </div>
            </div>
          </div>
        </div>

        <!-- Dialog Footer -->
        <div class="border-t p-6">
          <button
            @click="closeLogsDialog"
            class="w-full px-6 py-3 bg-gray-200 text-gray-700 rounded-xl font-semibold hover:bg-gray-300 transition-colors"
          >
            ปิด
          </button>
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
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useBreakersStore } from '@/stores/breakers'
import { useRoomStore } from '@/stores/room'
import type { Breaker, BreakerFormData, BreakerState, BreakerAction, TriggerType, ActionStatus } from '@/types/homeAssistant'
import { getBreakerStateLabel, getBreakerStateColor, getActionLabel, getTriggerTypeLabel, getActionStatusLabel } from '@/types/homeAssistant'

// Stores
const breakersStore = useBreakersStore()
const roomStore = useRoomStore()

// State
const showDialog = ref(false)
const showLogsDialog = ref(false)
const isEditing = ref(false)
const submitting = ref(false)
const syncing = ref(false)
const selectedBreaker = ref<Breaker | null>(null)
const autoRefreshInterval = ref<number | null>(null)

const formData = ref<BreakerFormData>({
  entity_id: '',
  friendly_name: '',
  room_id: null,
  auto_control_enabled: true
})

// Filters
const filterRoomId = ref<number | null>(null)
const filterState = ref<BreakerState | null>(null)
const filterAutoControl = ref<boolean | null>(null)

// Statistics
const statistics = ref(null)

// Toast
const toast = ref({
  show: false,
  type: 'success' as 'success' | 'error',
  message: ''
})

// Computed
const availableRooms = computed(() => {
  // Get all rooms
  return roomStore.rooms || []
})

// Functions

function showToast(type: 'success' | 'error', message: string) {
  toast.value = { show: true, type, message }
  setTimeout(() => {
    toast.value.show = false
  }, 3000)
}

function getBreakerCardClass(state: BreakerState, isAvailable: boolean) {
  if (!isAvailable) return 'bg-gradient-to-br from-gray-100 to-gray-200 border-2 border-gray-300'

  switch (state) {
    case 'ON':
      return 'bg-gradient-to-br from-green-50 to-emerald-50 border-2 border-green-200'
    case 'OFF':
      return 'bg-white border-2 border-gray-200'
    case 'UNAVAILABLE':
      return 'bg-gradient-to-br from-red-50 to-orange-50 border-2 border-red-200'
    default:
      return 'bg-white border-2 border-gray-200'
  }
}

function getStateBadgeClass(state: BreakerState) {
  switch (state) {
    case 'ON':
      return 'bg-green-500 text-white'
    case 'OFF':
      return 'bg-gray-400 text-white'
    case 'UNAVAILABLE':
      return 'bg-red-500 text-white'
    default:
      return 'bg-gray-400 text-white'
  }
}

function getStateLabel(state: BreakerState) {
  return getBreakerStateLabel(state)
}

function getActionBadgeClass(action: BreakerAction) {
  switch (action) {
    case 'TURN_ON':
      return 'bg-green-100 text-green-800'
    case 'TURN_OFF':
      return 'bg-gray-100 text-gray-800'
    case 'STATUS_SYNC':
      return 'bg-blue-100 text-blue-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

function getTriggerBadgeClass(trigger: TriggerType) {
  switch (trigger) {
    case 'AUTO':
      return 'bg-purple-100 text-purple-800'
    case 'MANUAL':
      return 'bg-blue-100 text-blue-800'
    case 'SYSTEM':
      return 'bg-cyan-100 text-cyan-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

function getStatusBadgeClass(status: ActionStatus) {
  switch (status) {
    case 'SUCCESS':
      return 'bg-green-100 text-green-800'
    case 'FAILED':
      return 'bg-red-100 text-red-800'
    case 'TIMEOUT':
      return 'bg-yellow-100 text-yellow-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

function getLogBorderClass(status: ActionStatus) {
  switch (status) {
    case 'SUCCESS':
      return 'border-green-400'
    case 'FAILED':
      return 'border-red-400'
    case 'TIMEOUT':
      return 'border-yellow-400'
    default:
      return 'border-gray-400'
  }
}

function getTriggerLabel(trigger: TriggerType) {
  return getTriggerTypeLabel(trigger)
}

function getStatusLabel(status: ActionStatus) {
  return getActionStatusLabel(status)
}

function formatDateTime(dateStr: string) {
  return new Date(dateStr).toLocaleString('th-TH', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

async function fetchData() {
  try {
    await Promise.all([
      breakersStore.fetchBreakers(),
      roomStore.fetchRooms(),
      fetchStatistics()
    ])
  } catch (error: any) {
    showToast('error', 'ไม่สามารถโหลดข้อมูลได้')
  }
}

async function autoSyncStatus() {
  try {
    // Sync all breakers with Home Assistant silently (also fetches updated data)
    await breakersStore.syncAll(true)

    // Refresh statistics
    await fetchStatistics()
  } catch (error: any) {
    // Silent error - don't show toast during auto-refresh
    console.error('Auto-sync error:', error)
  }
}

async function fetchStatistics() {
  try {
    statistics.value = await breakersStore.fetchStatistics()
  } catch (error) {
    // Ignore error
  }
}

function applyFilters() {
  const params: any = {}
  if (filterRoomId.value !== null) params.room_id = filterRoomId.value
  if (filterState.value !== null) params.current_state = filterState.value
  if (filterAutoControl.value !== null) params.auto_control_enabled = filterAutoControl.value

  breakersStore.fetchBreakers(params)
}

function openCreateDialog() {
  isEditing.value = false
  formData.value = {
    entity_id: '',
    friendly_name: '',
    room_id: null,
    auto_control_enabled: true
  }
  showDialog.value = true
}

function openEditDialog(breaker: Breaker) {
  isEditing.value = true
  selectedBreaker.value = breaker
  formData.value = {
    entity_id: breaker.entity_id,
    friendly_name: breaker.friendly_name,
    room_id: breaker.room_id,
    auto_control_enabled: breaker.auto_control_enabled
  }
  showDialog.value = true
}

function closeDialog() {
  showDialog.value = false
  selectedBreaker.value = null
}

async function handleSubmit() {
  submitting.value = true
  try {
    if (isEditing.value && selectedBreaker.value) {
      await breakersStore.updateBreaker(selectedBreaker.value.id, formData.value)
      showToast('success', 'อัปเดต Breaker สำเร็จ')
    } else {
      await breakersStore.createBreaker(formData.value)
      showToast('success', 'เพิ่ม Breaker สำเร็จ')
    }
    closeDialog()

    // Refresh data without throwing error to prevent duplicate error toast
    fetchData().catch(err => {
      console.error('Failed to refresh data after create/update:', err)
      // Error is silently ignored here since the create/update was successful
    })
  } catch (error: any) {
    showToast('error', error.response?.data?.detail || 'เกิดข้อผิดพลาด')
  } finally {
    submitting.value = false
  }
}

async function handleDelete() {
  if (!selectedBreaker.value) return

  if (!confirm(`คุณต้องการลบ Breaker "${selectedBreaker.value.friendly_name}" ใช่หรือไม่?`)) {
    return
  }

  submitting.value = true
  try {
    await breakersStore.deleteBreaker(selectedBreaker.value.id)
    showToast('success', 'ลบ Breaker สำเร็จ')
    closeDialog()
    await fetchData()
  } catch (error: any) {
    showToast('error', error.response?.data?.detail || 'ไม่สามารถลบได้')
  } finally {
    submitting.value = false
  }
}

async function handleTurnOn(breakerId: number) {
  try {
    await breakersStore.turnOn(breakerId)
    showToast('success', 'กำลังเปิด Breaker')
    await fetchData()
  } catch (error: any) {
    showToast('error', error.response?.data?.detail || 'ไม่สามารถเปิดได้')
  }
}

async function handleTurnOff(breakerId: number) {
  try {
    await breakersStore.turnOff(breakerId)
    showToast('success', 'กำลังปิด Breaker')
    await fetchData()
  } catch (error: any) {
    showToast('error', error.response?.data?.detail || 'ไม่สามารถปิดได้')
  }
}

async function handleSync(breakerId: number) {
  try {
    await breakersStore.syncStatus(breakerId)
    showToast('success', 'ซิงค์สถานะสำเร็จ')
    await fetchData()
  } catch (error: any) {
    showToast('error', error.response?.data?.detail || 'ไม่สามารถซิงค์ได้')
  }
}

async function handleSyncAll() {
  syncing.value = true
  try {
    await breakersStore.syncAll()
    showToast('success', 'ซิงค์ทั้งหมดสำเร็จ')
    await fetchData()
  } catch (error: any) {
    showToast('error', error.response?.data?.detail || 'ไม่สามารถซิงค์ได้')
  } finally {
    syncing.value = false
  }
}

async function openLogsDialog(breaker: Breaker) {
  selectedBreaker.value = breaker
  showLogsDialog.value = true
  try {
    await breakersStore.fetchLogs(breaker.id)
  } catch (error: any) {
    showToast('error', 'ไม่สามารถโหลดประวัติได้')
  }
}

function closeLogsDialog() {
  showLogsDialog.value = false
  selectedBreaker.value = null
}

// Lifecycle
onMounted(() => {
  fetchData()

  // Auto-sync with Home Assistant every 10 seconds
  autoRefreshInterval.value = window.setInterval(() => {
    autoSyncStatus()
  }, 10000)
})

onUnmounted(() => {
  // Clear auto-refresh interval
  if (autoRefreshInterval.value !== null) {
    clearInterval(autoRefreshInterval.value)
    autoRefreshInterval.value = null
  }
})
</script>

<style scoped>
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
