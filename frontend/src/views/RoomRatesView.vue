<template>
  <div class="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 p-6">
    <!-- Header -->
    <div class="max-w-7xl mx-auto mb-8">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-4xl font-bold bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
            จัดการราคาห้อง
          </h1>
          <p class="text-gray-600 mt-2">Room Rates Management</p>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="roomStore.isLoading" class="max-w-5xl mx-auto">
      <div class="animate-pulse bg-white rounded-2xl shadow-lg p-8 h-96"></div>
    </div>

    <!-- Rate Matrix -->
    <div v-else class="max-w-5xl mx-auto">
      <div class="bg-white rounded-2xl shadow-2xl overflow-hidden">
        <!-- Table Header -->
        <div class="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 p-6 text-white">
          <h2 class="text-2xl font-bold">ตารางราคาห้องพัก</h2>
          <p class="text-white/80 mt-1">กดที่ราคาเพื่อแก้ไข</p>
        </div>

        <!-- Table Body -->
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead>
              <tr class="bg-gray-50 border-b-2 border-gray-200">
                <th class="px-6 py-4 text-left text-gray-700 font-bold">ประเภทห้อง</th>
                <th class="px-6 py-4 text-center text-gray-700 font-bold">
                  <div class="flex flex-col items-center">
                    <span class="text-2xl mb-1">🌙</span>
                    <span>ค้างคืน</span>
                    <span class="text-xs text-gray-500 mt-1">(Overnight)</span>
                  </div>
                </th>
                <th class="px-6 py-4 text-center text-gray-700 font-bold">
                  <div class="flex flex-col items-center">
                    <span class="text-2xl mb-1">⏰</span>
                    <span>ชั่วคราว</span>
                    <span class="text-xs text-gray-500 mt-1">(3 Hours)</span>
                  </div>
                </th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(row, idx) in roomStore.rateMatrix"
                :key="row.room_type_id"
                :class="idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'"
                class="border-b border-gray-200 hover:bg-indigo-50 transition-colors"
              >
                <!-- Room Type Name -->
                <td class="px-6 py-6">
                  <div class="flex items-center gap-3">
                    <div class="w-3 h-3 rounded-full bg-gradient-to-r from-indigo-500 to-purple-500"></div>
                    <span class="font-bold text-gray-800 text-lg">{{ row.room_type_name }}</span>
                  </div>
                </td>

                <!-- Overnight Rate -->
                <td class="px-6 py-6 text-center">
                  <button
                    @click="openEditRateDialog(row.room_type_id, row.room_type_name, 'OVERNIGHT', row.overnight_rate)"
                    class="group relative inline-flex flex-col items-center justify-center px-6 py-4 min-w-[140px] bg-gradient-to-br from-indigo-100 to-purple-100 hover:from-indigo-200 hover:to-purple-200 rounded-xl transition-all duration-200 transform hover:scale-105"
                  >
                    <span v-if="row.overnight_rate" class="text-3xl font-bold text-indigo-700">
                      {{ formatPrice(row.overnight_rate) }}
                    </span>
                    <span v-else class="text-gray-400 text-lg">ไม่มีราคา</span>
                    <span class="text-xs text-gray-600 mt-1">บาท/คืน</span>
                    <div class="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity bg-black/10 rounded-xl">
                      <span class="text-white font-semibold">✏️ แก้ไข</span>
                    </div>
                  </button>
                </td>

                <!-- Temporary Rate -->
                <td class="px-6 py-6 text-center">
                  <button
                    @click="openEditRateDialog(row.room_type_id, row.room_type_name, 'TEMPORARY', row.temporary_rate)"
                    class="group relative inline-flex flex-col items-center justify-center px-6 py-4 min-w-[140px] bg-gradient-to-br from-pink-100 to-purple-100 hover:from-pink-200 hover:to-purple-200 rounded-xl transition-all duration-200 transform hover:scale-105"
                  >
                    <span v-if="row.temporary_rate" class="text-3xl font-bold text-pink-700">
                      {{ formatPrice(row.temporary_rate) }}
                    </span>
                    <span v-else class="text-gray-400 text-lg">ไม่มีราคา</span>
                    <span class="text-xs text-gray-600 mt-1">บาท/3 ชม.</span>
                    <div class="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity bg-black/10 rounded-xl">
                      <span class="text-white font-semibold">✏️ แก้ไข</span>
                    </div>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Info Footer -->
        <div class="bg-gray-50 p-6 border-t-2 border-gray-200">
          <div class="flex items-start gap-3 text-gray-600">
            <span class="text-2xl">💡</span>
            <div class="text-sm">
              <p class="font-semibold mb-1">วิธีใช้งาน:</p>
              <ul class="list-disc list-inside space-y-1">
                <li>คลิกที่ราคาเพื่อแก้ไขราคาห้อง</li>
                <li>ราคาค้างคืน: สำหรับการเข้าพักตั้งแต่ 13:00 - 12:00 วันถัดไป</li>
                <li>ราคาชั่วคราว: สำหรับการเข้าพัก 3 ชั่วโมง (สามารถปรับได้ในการตั้งค่า)</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit Rate Dialog -->
    <div
      v-if="showEditDialog"
      class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50"
      @click.self="closeEditDialog"
    >
      <div class="bg-white rounded-2xl shadow-2xl max-w-md w-full">
        <!-- Dialog Header -->
        <div class="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 p-6 text-white">
          <h2 class="text-2xl font-bold">แก้ไขราคา</h2>
          <p class="text-white/80 mt-1">
            {{ editingRoomTypeName }} - {{ editingStayType === 'OVERNIGHT' ? 'ค้างคืน' : 'ชั่วคราว' }}
          </p>
        </div>

        <!-- Dialog Body -->
        <form @submit.prevent="handleUpdateRate" class="p-6 space-y-6">
          <!-- Rate Input -->
          <div>
            <label class="block text-gray-700 font-semibold mb-2">
              ราคา (บาท) <span class="text-red-500">*</span>
            </label>
            <div class="relative">
              <input
                v-model.number="editingRate"
                type="number"
                required
                min="0"
                step="0.01"
                placeholder="0.00"
                class="w-full px-4 py-4 text-2xl font-bold border-2 border-gray-300 rounded-xl focus:border-indigo-500 focus:outline-none transition-colors text-center"
              />
              <span class="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 font-semibold">บาท</span>
            </div>
            <p class="text-sm text-gray-500 mt-2 text-center">
              {{ editingStayType === 'OVERNIGHT' ? 'ราคาต่อคืน' : 'ราคาต่อ 3 ชั่วโมง' }}
            </p>
          </div>

          <!-- Current Rate Display -->
          <div v-if="originalRate" class="bg-gray-100 rounded-xl p-4 text-center">
            <p class="text-sm text-gray-600 mb-1">ราคาปัจจุบัน</p>
            <p class="text-2xl font-bold text-gray-800">{{ formatPrice(originalRate) }} บาท</p>
          </div>

          <!-- Error Message -->
          <div v-if="roomStore.error" class="p-4 bg-red-100 border border-red-300 rounded-xl text-red-700">
            {{ roomStore.error }}
          </div>

          <!-- Actions -->
          <div class="flex gap-3">
            <button
              type="button"
              @click="closeEditDialog"
              class="flex-1 px-6 py-3 border-2 border-gray-300 text-gray-700 rounded-xl font-semibold hover:bg-gray-50 transition-colors"
            >
              ยกเลิก
            </button>
            <button
              type="submit"
              :disabled="roomStore.isLoading"
              class="flex-1 px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl font-semibold hover:shadow-lg transform hover:scale-105 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {{ roomStore.isLoading ? 'กำลังบันทึก...' : 'บันทึก' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoomStore } from '@/stores/room'
import { StayType } from '@/types/room'

const roomStore = useRoomStore()

const showEditDialog = ref(false)
const editingRoomTypeId = ref<number>(0)
const editingRoomTypeName = ref('')
const editingStayType = ref<'OVERNIGHT' | 'TEMPORARY'>('OVERNIGHT')
const editingRate = ref<number>(0)
const originalRate = ref<number | null>(null)

const formatPrice = (price: number): string => {
  return new Intl.NumberFormat('th-TH', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2
  }).format(price)
}

const openEditRateDialog = (
  roomTypeId: number,
  roomTypeName: string,
  stayType: 'OVERNIGHT' | 'TEMPORARY',
  currentRate?: number
) => {
  editingRoomTypeId.value = roomTypeId
  editingRoomTypeName.value = roomTypeName
  editingStayType.value = stayType
  editingRate.value = currentRate || 0
  originalRate.value = currentRate || null
  showEditDialog.value = true
  roomStore.clearError()
}

const closeEditDialog = () => {
  showEditDialog.value = false
  editingRoomTypeId.value = 0
  editingRoomTypeName.value = ''
  editingRate.value = 0
  originalRate.value = null
}

const handleUpdateRate = async () => {
  try {
    const stayTypeEnum = editingStayType.value === 'OVERNIGHT' ? StayType.OVERNIGHT : StayType.TEMPORARY

    // Check if rate already exists
    const existingRate = roomStore.rateMatrix.find(
      row => row.room_type_id === editingRoomTypeId.value
    )

    const rateId = editingStayType.value === 'OVERNIGHT'
      ? existingRate?.overnight_rate_id
      : existingRate?.temporary_rate_id

    if (rateId) {
      // Update existing rate
      await roomStore.updateRoomRate(rateId, {
        rate: editingRate.value
      })
    } else {
      // Create new rate
      await roomStore.createRoomRate({
        room_type_id: editingRoomTypeId.value,
        stay_type: stayTypeEnum,
        rate: editingRate.value,
        effective_from: new Date().toISOString().split('T')[0],
        is_active: true
      })
    }
  } catch (error) {
    // Show error but don't stop the flow
    console.error('Rate update error:', error)
  } finally {
    // Always refresh matrix and close dialog, even if there was an error
    try {
      await roomStore.fetchRateMatrix()
    } catch (refreshError) {
      console.error('Matrix refresh error:', refreshError)
    }
    closeEditDialog()
  }
}

onMounted(async () => {
  await roomStore.fetchRoomTypes()
  await roomStore.fetchRateMatrix()
})
</script>
