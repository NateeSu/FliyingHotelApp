<template>
  <n-modal
    v-model:show="isVisible"
    preset="card"
    title="ย้ายห้องพัก"
    :style="{ maxWidth: '600px' }"
    :bordered="false"
    :segmented="true"
    @after-leave="resetForm"
  >
    <n-spin :show="isLoading">
      <n-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-placement="top"
        require-mark-placement="right-hanging"
      >
        <!-- Current Room Info -->
        <n-alert type="info" :bordered="false" style="margin-bottom: 16px">
          <template #header>
            <strong>ข้อมูลห้องปัจจุบัน</strong>
          </template>
          <n-space vertical>
            <div>
              <n-text strong>ห้อง:</n-text> {{ props.currentRoom?.room_number }}
              <n-tag :type="getRoomTypeColor(props.currentRoom?.room_type_name)" size="small" style="margin-left: 8px">
                {{ props.currentRoom?.room_type_name }}
              </n-tag>
            </div>
            <div v-if="props.currentRoom?.customer_name">
              <n-text strong>ลูกค้า:</n-text> {{ props.currentRoom?.customer_name }}
            </div>
          </n-space>
        </n-alert>

        <!-- New Room Selection -->
        <n-form-item label="ห้องใหม่" path="new_room_id">
          <n-select
            v-model:value="formData.new_room_id"
            :options="availableRoomsOptions"
            placeholder="เลือกห้องใหม่"
            filterable
            :loading="isLoadingRooms"
            clearable
          >
            <template #empty>
              <n-empty description="ไม่พบห้องว่างในประเภทเดียวกัน">
                <template #icon>
                  <n-icon>
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                      <path fill="currentColor" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
                    </svg>
                  </n-icon>
                </template>
              </n-empty>
            </template>
          </n-select>
        </n-form-item>

        <!-- Transfer Reason -->
        <n-form-item label="เหตุผลในการย้ายห้อง (ไม่บังคับ)" path="reason">
          <n-input
            v-model:value="formData.reason"
            type="textarea"
            placeholder="เช่น: แอร์เสีย, ลูกค้าขอย้าย, ห้องมีปัญหา"
            :autosize="{ minRows: 2, maxRows: 4 }"
            maxlength="500"
            show-count
          />
        </n-form-item>

        <!-- Warning -->
        <n-alert type="warning" :bordered="false">
          <template #header>
            <strong>คำเตือน</strong>
          </template>
          <ul style="margin: 0; padding-left: 20px">
            <li>ข้อมูลลูกค้าและค่าใช้จ่ายจะถูกย้ายไปห้องใหม่ทั้งหมด</li>
            <li>ห้องเดิมจะถูกเปลี่ยนสถานะเป็น "กำลังทำความสะอาด"</li>
            <li>ระบบจะสร้างงานทำความสะอาดอัตโนมัติ (Phase 5)</li>
          </ul>
        </n-alert>
      </n-form>
    </n-spin>

    <template #footer>
      <n-space justify="end">
        <n-button @click="handleCancel" :disabled="isLoading">
          ยกเลิก
        </n-button>
        <n-button
          type="primary"
          @click="handleSubmit"
          :loading="isLoading"
          :disabled="!formData.new_room_id"
        >
          ยืนยันการย้ายห้อง
        </n-button>
      </n-space>
    </template>
  </n-modal>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import {
  NModal,
  NForm,
  NFormItem,
  NSelect,
  NInput,
  NButton,
  NSpace,
  NAlert,
  NText,
  NTag,
  NEmpty,
  NIcon,
  NSpin,
  useMessage,
  type FormInst,
  type FormRules
} from 'naive-ui'
import { useDashboardStore } from '@/stores/dashboard'
import { checkInApi, type RoomTransferRequest } from '@/api/check-ins'
import type { DashboardRoomCard } from '@/types/dashboard'

interface Props {
  show: boolean
  currentRoom: DashboardRoomCard | null
  checkInId: number | null
}

const props = defineProps<Props>()

interface Emits {
  (e: 'update:show', value: boolean): void
  (e: 'success'): void
}

const emit = defineEmits<Emits>()

// Stores
const dashboardStore = useDashboardStore()
const message = useMessage()

// Form
const formRef = ref<FormInst | null>(null)
const formData = ref<RoomTransferRequest>({
  new_room_id: null as unknown as number,
  reason: ''
})

const rules: FormRules = {
  new_room_id: {
    required: true,
    type: 'number',
    message: 'กรุณาเลือกห้องใหม่',
    trigger: 'change'
  }
}

// State
const isLoading = ref(false)
const isLoadingRooms = ref(false)

// Computed
const isVisible = computed({
  get: () => props.show,
  set: (value) => emit('update:show', value)
})

/**
 * Get available rooms (same room type, status = available)
 */
const availableRoomsOptions = computed(() => {
  if (!props.currentRoom) return []

  const currentRoomTypeId = props.currentRoom.room_type_id

  return dashboardStore.availableRooms
    .filter(room =>
      room.room_type_id === currentRoomTypeId &&
      room.id !== props.currentRoom?.id
    )
    .map(room => ({
      label: `ห้อง ${room.room_number} - ${room.room_type_name}`,
      value: room.id
    }))
})

/**
 * Get room type color tag
 */
function getRoomTypeColor(roomType?: string): 'primary' | 'success' | 'warning' | 'error' {
  if (!roomType) return 'primary'

  const lowerType = roomType.toLowerCase()
  if (lowerType.includes('vip') || lowerType.includes('deluxe')) return 'warning'
  if (lowerType.includes('standard')) return 'primary'
  if (lowerType.includes('suite')) return 'error'

  return 'success'
}

/**
 * Handle form submission
 */
async function handleSubmit() {
  if (!formRef.value || !props.checkInId) return

  try {
    await formRef.value.validate()

    isLoading.value = true

    const response = await checkInApi.transferRoom(props.checkInId, formData.value)

    message.success(response.message || 'ย้ายห้องสำเร็จ')

    emit('success')
    emit('update:show', false)

    // Refresh dashboard
    await dashboardStore.fetchRooms()
    await dashboardStore.fetchStats()
  } catch (error: any) {
    console.error('Room transfer error:', error)

    if (error?.errors) {
      // Validation error
      return
    }

    const errorMessage = error?.response?.data?.detail || error?.message || 'เกิดข้อผิดพลาดในการย้ายห้อง'
    message.error(errorMessage)
  } finally {
    isLoading.value = false
  }
}

/**
 * Handle cancel
 */
function handleCancel() {
  emit('update:show', false)
}

/**
 * Reset form
 */
function resetForm() {
  formData.value = {
    new_room_id: null as unknown as number,
    reason: ''
  }
  formRef.value?.restoreValidation()
}

// Watch for modal open to reset form
watch(() => props.show, (newValue) => {
  if (newValue) {
    resetForm()
  }
})
</script>

<style scoped>
:deep(.n-card__content) {
  padding-top: 20px;
}

:deep(.n-form-item-label) {
  font-weight: 500;
}
</style>
