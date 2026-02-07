<template>
  <div class="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 p-6">
    <!-- Header -->
    <div class="max-w-7xl mx-auto mb-8">
      <div class="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 class="text-4xl font-bold bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
            จัดการห้องพัก
          </h1>
          <p class="text-gray-600 mt-2">Rooms Management</p>
        </div>
        <button
          @click="openCreateDialog"
          class="px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl font-semibold shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200"
        >
          <span class="text-xl mr-2">+</span> เพิ่มห้องใหม่
        </button>
      </div>

      <!-- Filters -->
      <div class="mt-6 flex flex-wrap gap-4">
        <select
          v-model="filterFloor"
          @change="applyFilters"
          class="px-4 py-2 border-2 border-gray-300 rounded-xl focus:border-indigo-500 focus:outline-none"
        >
          <option :value="null">ทุกชั้น</option>
          <option :value="1">ชั้น 1</option>
          <option :value="2">ชั้น 2</option>
        </select>

        <select
          v-model="filterStatus"
          @change="applyFilters"
          class="px-4 py-2 border-2 border-gray-300 rounded-xl focus:border-indigo-500 focus:outline-none"
        >
          <option :value="null">ทุกสถานะ</option>
          <option value="AVAILABLE">ว่าง</option>
          <option value="OCCUPIED">มีผู้พัก</option>
          <option value="CLEANING">กำลังทำความสะอาด</option>
          <option value="RESERVED">จองแล้ว</option>
          <option value="OUT_OF_SERVICE">ปิดปรับปรุง</option>
        </select>

        <select
          v-model="filterRoomType"
          @change="applyFilters"
          class="px-4 py-2 border-2 border-gray-300 rounded-xl focus:border-indigo-500 focus:outline-none"
        >
          <option :value="null">ทุกประเภท</option>
          <option v-for="rt in roomStore.roomTypes" :key="rt.id" :value="rt.id">
            {{ rt.name }}
          </option>
        </select>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="roomStore.isLoading" class="max-w-7xl mx-auto">
      <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
        <div v-for="i in 10" :key="i" class="animate-pulse">
          <div class="bg-white rounded-2xl h-48 shadow-lg"></div>
        </div>
      </div>
    </div>

    <!-- Rooms Grid -->
    <div v-else class="max-w-7xl mx-auto">
      <div v-if="roomStore.rooms.length === 0" class="text-center py-16">
        <div class="text-gray-400 text-6xl mb-4">🚪</div>
        <p class="text-gray-600 text-xl">ยังไม่มีห้องพัก</p>
        <p class="text-gray-400 mt-2">คลิกปุ่ม "เพิ่มห้องใหม่" เพื่อเริ่มต้น</p>
      </div>

      <div v-else class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
        <div
          v-for="room in roomStore.rooms"
          :key="room.id"
          :class="[
            'rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 overflow-hidden cursor-pointer group',
            getStatusClass(room.status)
          ]"
          @click="openRoomDetails(room)"
        >
          <!-- Room Number -->
          <div class="p-6 text-center">
            <div class="text-4xl font-bold mb-2">{{ room.room_number }}</div>
            <div class="text-sm opacity-90 mb-4">
              {{ room.room_type?.name || 'N/A' }}
            </div>

            <!-- Status Badge -->
            <div :class="['px-3 py-1 rounded-full text-sm font-semibold inline-block', getStatusBadgeClass(room.status)]">
              {{ getStatusLabel(room.status) }}
            </div>

            <!-- Floor -->
            <div class="mt-4 text-sm opacity-75">
              ชั้น {{ room.floor }}
            </div>

            <!-- QR Code hint -->
            <div v-if="room.qr_code" class="mt-2 text-xs opacity-60">
              🔲 {{ room.qr_code }}
            </div>
          </div>

          <!-- Quick Actions on Hover -->
          <div class="px-4 pb-4 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
            <button
              @click.stop="openEditDialog(room)"
              class="w-full px-3 py-2 bg-white/20 backdrop-blur-sm text-white rounded-lg text-sm font-semibold hover:bg-white/30 transition-colors"
            >
              แก้ไข
            </button>
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
        <div class="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 p-6 text-white">
          <h2 class="text-2xl font-bold">
            {{ isEditing ? 'แก้ไขห้องพัก' : 'เพิ่มห้องใหม่' }}
          </h2>
        </div>

        <!-- Dialog Body -->
        <form @submit.prevent="handleSubmit" class="p-6 space-y-6">
          <!-- Room Number -->
          <div>
            <label class="block text-gray-700 font-semibold mb-2">
              หมายเลขห้อง <span class="text-red-500">*</span>
            </label>
            <input
              v-model="formData.room_number"
              type="text"
              required
              placeholder="เช่น 101, 201, VIP-01"
              class="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:border-indigo-500 focus:outline-none transition-colors"
            />
          </div>

          <!-- Room Type -->
          <div>
            <label class="block text-gray-700 font-semibold mb-2">
              ประเภทห้อง <span class="text-red-500">*</span>
            </label>
            <select
              v-model.number="formData.room_type_id"
              required
              class="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:border-indigo-500 focus:outline-none transition-colors"
            >
              <option :value="0" disabled>เลือกประเภทห้อง</option>
              <option v-for="rt in roomStore.activeRoomTypes" :key="rt.id" :value="rt.id">
                {{ rt.name }}
              </option>
            </select>
          </div>

          <!-- Floor -->
          <div>
            <label class="block text-gray-700 font-semibold mb-2">
              ชั้น <span class="text-red-500">*</span>
            </label>
            <input
              v-model.number="formData.floor"
              type="number"
              required
              min="1"
              class="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:border-indigo-500 focus:outline-none transition-colors"
            />
          </div>

          <!-- Status (only when editing) -->
          <div v-if="isEditing">
            <label class="block text-gray-700 font-semibold mb-2">สถานะห้อง</label>
            <select
              v-model="formData.status"
              class="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:border-indigo-500 focus:outline-none transition-colors"
            >
              <option value="available">ว่าง</option>
              <option value="occupied">มีผู้พัก</option>
              <option value="cleaning">กำลังทำความสะอาด</option>
              <option value="reserved">จองแล้ว</option>
              <option value="out_of_service">ปิดปรับปรุง</option>
            </select>
          </div>

          <!-- Notes -->
          <div>
            <label class="block text-gray-700 font-semibold mb-2">หมายเหตุ</label>
            <textarea
              v-model="formData.notes"
              rows="3"
              placeholder="บันทึกเพิ่มเติม เช่น แอร์เสีย, ต้องซ่อม"
              class="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:border-indigo-500 focus:outline-none transition-colors resize-none"
            ></textarea>
          </div>

          <!-- Is Active -->
          <div class="flex items-center gap-3">
            <input
              v-model="formData.is_active"
              type="checkbox"
              id="is_active"
              class="w-5 h-5 text-indigo-600 rounded focus:ring-2 focus:ring-indigo-500"
            />
            <label for="is_active" class="text-gray-700 font-semibold cursor-pointer">
              เปิดใช้งาน
            </label>
          </div>

          <!-- Smart Breaker Configuration (only when editing) -->
          <div v-if="isEditing && isHAConfigured" class="border-2 border-purple-200 rounded-xl p-4 bg-purple-50">
            <div class="flex items-center gap-2 mb-4">
              <span class="text-2xl">⚡</span>
              <h3 class="text-lg font-bold text-purple-800">Smart Breaker Configuration</h3>
            </div>

            <div class="space-y-4">
              <!-- Breaker Selection -->
              <div>
                <label class="block text-gray-700 font-semibold mb-2">
                  Home Assistant Entity
                </label>
                <select
                  v-model="selectedBreakerId"
                  @change="handleBreakerChange"
                  class="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:border-purple-500 focus:outline-none transition-colors"
                >
                  <option :value="null">ไม่เชื่อมกับ breaker</option>
                  <option v-for="breaker in availableBreakers" :key="breaker.id" :value="breaker.id">
                    {{ breaker.friendly_name }} ({{ breaker.entity_id }})
                  </option>
                </select>
                <p class="text-xs text-gray-500 mt-1">
                  เลือก breaker ที่ต้องการเชื่อมกับห้องนี้
                </p>
              </div>

              <!-- Current Breaker Info -->
              <div v-if="currentRoomBreaker" class="p-3 bg-white rounded-lg border border-purple-200">
                <div class="flex items-center justify-between">
                  <div>
                    <div class="font-semibold text-gray-800">{{ currentRoomBreaker.friendly_name }}</div>
                    <div class="text-sm text-gray-600">{{ currentRoomBreaker.entity_id }}</div>
                  </div>
                  <div class="flex items-center gap-2">
                    <span :class="[
                      'px-3 py-1 rounded-full text-xs font-semibold',
                      currentRoomBreaker.is_available ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                    ]">
                      {{ currentRoomBreaker.is_available ? 'พร้อมใช้งาน' : 'ออฟไลน์' }}
                    </span>
                    <span :class="[
                      'text-2xl',
                      currentRoomBreaker.current_state === 'ON' ? '⚡' : '⚫'
                    ]">
                    </span>
                  </div>
                </div>

                <div class="mt-2 pt-2 border-t border-purple-100">
                  <div class="flex items-center gap-3">
                    <label class="flex items-center gap-2 cursor-pointer">
                      <input
                        v-model="breakerAutoControl"
                        type="checkbox"
                        class="w-4 h-4 text-purple-600 rounded focus:ring-2 focus:ring-purple-500"
                      />
                      <span class="text-sm text-gray-700">เปิดใช้งานควบคุมอัตโนมัติ</span>
                    </label>
                    <router-link
                      to="/breakers"
                      class="text-xs text-purple-600 hover:text-purple-800 underline"
                    >
                      จัดการ Breaker
                    </router-link>
                  </div>
                </div>
              </div>

              <!-- No Breaker Info -->
              <div v-else-if="selectedBreakerId === null" class="p-3 bg-gray-100 rounded-lg text-center">
                <p class="text-sm text-gray-600">ห้องนี้ยังไม่ได้เชื่อมกับ Smart Breaker</p>
                <router-link to="/breakers" class="text-sm text-purple-600 hover:text-purple-800 underline mt-1 inline-block">
                  สร้าง Breaker ใหม่
                </router-link>
              </div>
            </div>
          </div>

          <!-- HA Not Configured -->
          <div v-if="isEditing && !isHAConfigured" class="border-2 border-gray-200 rounded-xl p-4 bg-gray-50">
            <div class="flex items-center gap-2 mb-2">
              <span class="text-2xl opacity-50">⚡</span>
              <h3 class="text-lg font-bold text-gray-500">Smart Breaker</h3>
            </div>
            <p class="text-sm text-gray-500 mb-2">ยังไม่ได้ตั้งค่า Home Assistant</p>
            <router-link to="/settings" class="text-sm text-indigo-600 hover:text-indigo-800 underline">
              ตั้งค่าเลย
            </router-link>
          </div>

          <!-- Error Message -->
          <div v-if="roomStore.error" class="p-4 bg-red-100 border border-red-300 rounded-xl text-red-700">
            {{ roomStore.error }}
          </div>

          <!-- Actions -->
          <div class="flex gap-3">
            <button
              v-if="isEditing"
              type="button"
              @click="confirmDelete"
              class="px-6 py-3 bg-red-600 text-white rounded-xl font-semibold hover:bg-red-700 transition-colors"
            >
              ลบ
            </button>
            <button
              type="button"
              @click="closeDialog"
              class="flex-1 px-6 py-3 border-2 border-gray-300 text-gray-700 rounded-xl font-semibold hover:bg-gray-50 transition-colors"
            >
              ยกเลิก
            </button>
            <button
              type="submit"
              :disabled="roomStore.isLoading"
              class="flex-1 px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl font-semibold hover:shadow-lg transform hover:scale-105 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {{ roomStore.isLoading ? 'กำลังบันทึก...' : (isEditing ? 'บันทึก' : 'เพิ่ม') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoomStore } from '@/stores/room'
import { useHomeAssistantStore } from '@/stores/homeAssistant'
import { useBreakersStore } from '@/stores/breakers'
import type { Room, RoomFormData } from '@/types/room'
import type { Breaker } from '@/types/homeAssistant'
import { RoomStatus, getRoomStatusLabel } from '@/types/room'

const roomStore = useRoomStore()
const haStore = useHomeAssistantStore()
const breakersStore = useBreakersStore()

const showDialog = ref(false)
const isEditing = ref(false)
const editingId = ref<number | null>(null)

const filterFloor = ref<number | null>(null)
const filterStatus = ref<RoomStatus | null>(null)
const filterRoomType = ref<number | null>(null)

const formData = ref<RoomFormData & { status?: RoomStatus }>({
  room_number: '',
  room_type_id: 0,
  floor: 1,
  notes: '',
  is_active: true,
  status: RoomStatus.AVAILABLE
})

const getStatusClass = (status: RoomStatus): string => {
  const classes: Record<RoomStatus, string> = {
    [RoomStatus.AVAILABLE]: 'bg-gradient-to-br from-green-400 to-green-600 text-white',
    [RoomStatus.OCCUPIED]: 'bg-gradient-to-br from-red-400 to-red-600 text-white',
    [RoomStatus.CLEANING]: 'bg-gradient-to-br from-yellow-400 to-yellow-600 text-white',
    [RoomStatus.RESERVED]: 'bg-gradient-to-br from-blue-400 to-blue-600 text-white',
    [RoomStatus.OUT_OF_SERVICE]: 'bg-gradient-to-br from-gray-400 to-gray-600 text-white'
  }
  return classes[status] || 'bg-gray-400'
}

const getStatusBadgeClass = (status: RoomStatus): string => {
  const classes: Record<RoomStatus, string> = {
    [RoomStatus.AVAILABLE]: 'bg-white/30 text-white',
    [RoomStatus.OCCUPIED]: 'bg-white/30 text-white',
    [RoomStatus.CLEANING]: 'bg-white/30 text-white',
    [RoomStatus.RESERVED]: 'bg-white/30 text-white',
    [RoomStatus.OUT_OF_SERVICE]: 'bg-white/30 text-white'
  }
  return classes[status] || 'bg-white/20 text-white'
}

const getStatusLabel = (status: RoomStatus): string => {
  return getRoomStatusLabel(status)
}

// Breaker-related state
const selectedBreakerId = ref<number | null>(null)
const breakerAutoControl = ref(true)

// Computed
const isHAConfigured = computed(() => haStore.status?.is_configured || false)

const availableBreakers = computed(() => {
  // Breakers ที่ยังไม่ได้ link กับห้องอื่น หรือ link กับห้องปัจจุบัน
  return breakersStore.breakers.filter(b =>
    b.room_id === null || b.room_id === editingId.value
  )
})

const currentRoomBreaker = computed(() => {
  if (!selectedBreakerId.value) return null
  return breakersStore.breakers.find(b => b.id === selectedBreakerId.value)
})

// Breaker methods
const handleBreakerChange = async () => {
  if (!selectedBreakerId.value) {
    breakerAutoControl.value = true
    return
  }

  const breaker = breakersStore.breakers.find(b => b.id === selectedBreakerId.value)
  if (breaker) {
    breakerAutoControl.value = breaker.auto_control_enabled
  }
}

const loadBreakerData = async () => {
  if (!isHAConfigured.value) return

  try {
    await Promise.all([
      haStore.fetchStatus(),
      breakersStore.fetchBreakers()
    ])

    // Load current breaker for this room
    if (editingId.value) {
      const roomBreaker = breakersStore.breakers.find(b => b.room_id === editingId.value)
      if (roomBreaker) {
        selectedBreakerId.value = roomBreaker.id
        breakerAutoControl.value = roomBreaker.auto_control_enabled
      }
    }
  } catch (error) {
    console.error('Error loading breaker data:', error)
  }
}

const saveBreakerConfig = async () => {
  if (!isEditing.value || !editingId.value) return

  try {
    // If breaker changed
    const currentBreaker = breakersStore.breakers.find(b => b.room_id === editingId.value)

    if (currentBreaker && currentBreaker.id !== selectedBreakerId.value) {
      // Unlink old breaker
      await breakersStore.update(currentBreaker.id, {
        room_id: null,
        auto_control_enabled: currentBreaker.auto_control_enabled
      })
    }

    if (selectedBreakerId.value) {
      // Link new breaker
      await breakersStore.update(selectedBreakerId.value, {
        room_id: editingId.value,
        auto_control_enabled: breakerAutoControl.value
      })
    }
  } catch (error) {
    console.error('Error saving breaker config:', error)
    throw error
  }
}

const resetForm = () => {
  formData.value = {
    room_number: '',
    room_type_id: 0,
    floor: 1,
    notes: '',
    is_active: true,
    status: RoomStatus.AVAILABLE
  }
  selectedBreakerId.value = null
  breakerAutoControl.value = true
  roomStore.clearError()
}

const openCreateDialog = () => {
  resetForm()
  isEditing.value = false
  editingId.value = null
  showDialog.value = true
}

const openEditDialog = async (room: Room) => {
  formData.value = {
    room_number: room.room_number,
    room_type_id: room.room_type_id,
    floor: room.floor,
    notes: room.notes || '',
    is_active: room.is_active,
    status: room.status
  }
  isEditing.value = true
  editingId.value = room.id
  showDialog.value = true

  // Load breaker data
  await loadBreakerData()
}

const openRoomDetails = (room: Room) => {
  openEditDialog(room)
}

const closeDialog = () => {
  showDialog.value = false
  resetForm()
}

const applyFilters = async () => {
  await roomStore.fetchRooms({
    floor: filterFloor.value || undefined,
    status: filterStatus.value || undefined,
    room_type_id: filterRoomType.value || undefined
  })
}

const handleSubmit = async () => {
  // Validate required fields
  if (!formData.value.room_type_id || formData.value.room_type_id === 0) {
    roomStore.error = 'กรุณาเลือกประเภทห้อง'
    return
  }

  try {
    const dataToSubmit = {
      room_number: formData.value.room_number,
      room_type_id: formData.value.room_type_id,
      floor: formData.value.floor,
      notes: formData.value.notes,
      is_active: formData.value.is_active
    }

    if (isEditing.value && editingId.value) {
      await roomStore.updateRoom(editingId.value, {
        ...dataToSubmit,
        status: formData.value.status
      })

      // Save breaker configuration
      await saveBreakerConfig()
    } else {
      await roomStore.createRoom(dataToSubmit)
    }
    closeDialog()
  } catch (error) {
    // Error is handled in store
  }
}

const confirmDelete = async () => {
  if (editingId.value && confirm(`คุณต้องการลบห้อง "${formData.value.room_number}" ใช่หรือไม่?`)) {
    try {
      await roomStore.deleteRoom(editingId.value)
      closeDialog()
    } catch (error) {
      alert(roomStore.error || 'ไม่สามารถลบห้องได้')
    }
  }
}

onMounted(async () => {
  await roomStore.fetchRoomTypes()
  await roomStore.fetchRooms()
})
</script>
