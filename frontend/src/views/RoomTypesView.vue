<template>
  <div class="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 p-6">
    <!-- Header -->
    <div class="max-w-7xl mx-auto mb-8">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-4xl font-bold bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
            จัดการประเภทห้อง
          </h1>
          <p class="text-gray-600 mt-2">Room Types Management</p>
        </div>
        <button
          @click="openCreateDialog"
          class="px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl font-semibold shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200"
        >
          <span class="text-xl mr-2">+</span> เพิ่มประเภทห้องใหม่
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="roomStore.isLoading" class="max-w-7xl mx-auto">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div v-for="i in 3" :key="i" class="animate-pulse">
          <div class="bg-white rounded-2xl h-64 shadow-lg"></div>
        </div>
      </div>
    </div>

    <!-- Room Types Grid -->
    <div v-else class="max-w-7xl mx-auto">
      <div v-if="roomStore.roomTypes.length === 0" class="text-center py-16">
        <div class="text-gray-400 text-6xl mb-4">🏨</div>
        <p class="text-gray-600 text-xl">ยังไม่มีประเภทห้อง</p>
        <p class="text-gray-400 mt-2">คลิกปุ่ม "เพิ่มประเภทห้องใหม่" เพื่อเริ่มต้น</p>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="roomType in roomStore.roomTypes"
          :key="roomType.id"
          class="bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 overflow-hidden group"
        >
          <!-- Card Header -->
          <div class="bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 p-6 text-white">
            <div class="flex items-center justify-between">
              <h3 class="text-2xl font-bold">{{ roomType.name }}</h3>
              <span
                v-if="roomType.is_active"
                class="px-3 py-1 bg-white/20 backdrop-blur-sm rounded-full text-sm font-semibold"
              >
                ใช้งาน
              </span>
              <span
                v-else
                class="px-3 py-1 bg-red-500/30 backdrop-blur-sm rounded-full text-sm font-semibold"
              >
                ปิดใช้งาน
              </span>
            </div>
          </div>

          <!-- Card Body -->
          <div class="p-6 space-y-4">
            <!-- Description -->
            <p v-if="roomType.description" class="text-gray-600 line-clamp-2">
              {{ roomType.description }}
            </p>

            <!-- Details -->
            <div class="space-y-2">
              <div class="flex items-center text-gray-700">
                <span class="text-2xl mr-3">👥</span>
                <span>รองรับผู้พัก: <strong>{{ roomType.max_guests }}</strong> คน</span>
              </div>
              <div v-if="roomType.bed_type" class="flex items-center text-gray-700">
                <span class="text-2xl mr-3">🛏️</span>
                <span>{{ roomType.bed_type }}</span>
              </div>
              <div v-if="roomType.room_size_sqm" class="flex items-center text-gray-700">
                <span class="text-2xl mr-3">📐</span>
                <span>{{ roomType.room_size_sqm }} ตารางเมตร</span>
              </div>
            </div>

            <!-- Amenities -->
            <div v-if="roomType.amenities && roomType.amenities.length > 0" class="pt-4 border-t">
              <p class="text-sm font-semibold text-gray-600 mb-2">สิ่งอำนวยความสะดวก:</p>
              <div class="flex flex-wrap gap-2">
                <span
                  v-for="(amenity, idx) in roomType.amenities"
                  :key="idx"
                  class="px-3 py-1 bg-indigo-100 text-indigo-700 rounded-full text-sm"
                >
                  {{ amenity }}
                </span>
              </div>
            </div>

            <!-- Actions -->
            <div class="flex gap-2 pt-4">
              <button
                @click="openEditDialog(roomType)"
                class="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-xl font-semibold hover:bg-indigo-700 transition-colors"
              >
                แก้ไข
              </button>
              <button
                @click="confirmDelete(roomType)"
                class="px-4 py-2 bg-red-600 text-white rounded-xl font-semibold hover:bg-red-700 transition-colors"
              >
                ลบ
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
        <div class="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 p-6 text-white">
          <h2 class="text-2xl font-bold">
            {{ isEditing ? 'แก้ไขประเภทห้อง' : 'เพิ่มประเภทห้องใหม่' }}
          </h2>
        </div>

        <!-- Dialog Body -->
        <form @submit.prevent="handleSubmit" class="p-6 space-y-6">
          <!-- Name -->
          <div>
            <label class="block text-gray-700 font-semibold mb-2">
              ชื่อประเภทห้อง <span class="text-red-500">*</span>
            </label>
            <input
              v-model="formData.name"
              type="text"
              required
              placeholder="เช่น Standard, Deluxe, VIP"
              class="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:border-indigo-500 focus:outline-none transition-colors"
            />
          </div>

          <!-- Description -->
          <div>
            <label class="block text-gray-700 font-semibold mb-2">คำอธิบาย</label>
            <textarea
              v-model="formData.description"
              rows="3"
              placeholder="คำอธิบายเกี่ยวกับประเภทห้อง"
              class="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:border-indigo-500 focus:outline-none transition-colors resize-none"
            ></textarea>
          </div>

          <!-- Max Guests -->
          <div>
            <label class="block text-gray-700 font-semibold mb-2">
              จำนวนผู้พักสูงสุด <span class="text-red-500">*</span>
            </label>
            <input
              v-model.number="formData.max_guests"
              type="number"
              required
              min="1"
              max="10"
              class="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:border-indigo-500 focus:outline-none transition-colors"
            />
          </div>

          <!-- Bed Type -->
          <div>
            <label class="block text-gray-700 font-semibold mb-2">ประเภทเตียง</label>
            <input
              v-model="formData.bed_type"
              type="text"
              placeholder="เช่น เตียงคู่, เตียงคิงไซส์"
              class="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:border-indigo-500 focus:outline-none transition-colors"
            />
          </div>

          <!-- Room Size -->
          <div>
            <label class="block text-gray-700 font-semibold mb-2">ขนาดห้อง (ตารางเมตร)</label>
            <input
              v-model.number="formData.room_size_sqm"
              type="number"
              step="0.01"
              min="0"
              placeholder="เช่น 25.00"
              class="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:border-indigo-500 focus:outline-none transition-colors"
            />
          </div>

          <!-- Amenities -->
          <div>
            <label class="block text-gray-700 font-semibold mb-2">สิ่งอำนวยความสะดวก</label>
            <div class="space-y-2">
              <div v-for="(amenity, idx) in formData.amenities" :key="idx" class="flex gap-2">
                <input
                  v-model="formData.amenities[idx]"
                  type="text"
                  placeholder="เช่น ทีวี, แอร์, Wi-Fi"
                  class="flex-1 px-4 py-2 border-2 border-gray-300 rounded-xl focus:border-indigo-500 focus:outline-none transition-colors"
                />
                <button
                  type="button"
                  @click="removeAmenity(idx)"
                  class="px-4 py-2 bg-red-500 text-white rounded-xl hover:bg-red-600 transition-colors"
                >
                  ลบ
                </button>
              </div>
              <button
                type="button"
                @click="addAmenity"
                class="w-full px-4 py-2 border-2 border-dashed border-gray-300 text-gray-600 rounded-xl hover:border-indigo-500 hover:text-indigo-600 transition-colors"
              >
                + เพิ่มสิ่งอำนวยความสะดวก
              </button>
            </div>
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

          <!-- Error Message -->
          <div v-if="roomStore.error" class="p-4 bg-red-100 border border-red-300 rounded-xl text-red-700">
            {{ roomStore.error }}
          </div>

          <!-- Actions -->
          <div class="flex gap-3">
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
import { ref, onMounted } from 'vue'
import { useRoomStore } from '@/stores/room'
import type { RoomType, RoomTypeFormData } from '@/types/room'

const roomStore = useRoomStore()

const showDialog = ref(false)
const isEditing = ref(false)
const editingId = ref<number | null>(null)

const formData = ref<RoomTypeFormData>({
  name: '',
  description: '',
  amenities: [],
  max_guests: 2,
  bed_type: '',
  room_size_sqm: undefined,
  is_active: true
})

const resetForm = () => {
  formData.value = {
    name: '',
    description: '',
    amenities: [],
    max_guests: 2,
    bed_type: '',
    room_size_sqm: undefined,
    is_active: true
  }
  roomStore.clearError()
}

const openCreateDialog = () => {
  resetForm()
  isEditing.value = false
  editingId.value = null
  showDialog.value = true
}

const openEditDialog = (roomType: RoomType) => {
  formData.value = {
    name: roomType.name,
    description: roomType.description || '',
    amenities: roomType.amenities ? [...roomType.amenities] : [],
    max_guests: roomType.max_guests,
    bed_type: roomType.bed_type || '',
    room_size_sqm: roomType.room_size_sqm,
    is_active: roomType.is_active
  }
  isEditing.value = true
  editingId.value = roomType.id
  showDialog.value = true
}

const closeDialog = () => {
  showDialog.value = false
  resetForm()
}

const addAmenity = () => {
  formData.value.amenities!.push('')
}

const removeAmenity = (index: number) => {
  formData.value.amenities!.splice(index, 1)
}

const handleSubmit = async () => {
  try {
    // Filter out empty amenities
    const dataToSubmit = {
      ...formData.value,
      amenities: formData.value.amenities?.filter(a => a.trim() !== '')
    }

    if (isEditing.value && editingId.value) {
      await roomStore.updateRoomType(editingId.value, dataToSubmit)
    } else {
      await roomStore.createRoomType(dataToSubmit)
    }
    closeDialog()
  } catch (error) {
    // Error is handled in store
  }
}

const confirmDelete = async (roomType: RoomType) => {
  if (confirm(`คุณต้องการลบประเภทห้อง "${roomType.name}" ใช่หรือไม่?`)) {
    try {
      await roomStore.deleteRoomType(roomType.id)
    } catch (error) {
      alert(roomStore.error || 'ไม่สามารถลบประเภทห้องได้')
    }
  }
}

onMounted(() => {
  roomStore.fetchRoomTypes()
})
</script>
