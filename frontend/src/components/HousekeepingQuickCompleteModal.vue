<template>
  <n-modal
    v-model:show="isVisible"
    preset="card"
    title="ปิดงานทำความสะอาด"
    :style="{ maxWidth: '600px' }"
    :bordered="false"
    :segmented="true"
  >
    <div v-if="task" class="quick-complete-content">
      <!-- Room Info -->
      <div class="room-info-banner">
        <div class="room-number">ห้อง {{ task.room_number }}</div>
        <div class="room-type">{{ task.room_type_name }}</div>
      </div>

      <!-- Task Info -->
      <div class="task-info">
        <div class="info-row">
          <span class="label">งาน:</span>
          <span class="value">{{ task.title }}</span>
        </div>
        <div v-if="task.description" class="info-row">
          <span class="label">รายละเอียด:</span>
          <span class="value">{{ task.description }}</span>
        </div>
        <div class="info-row">
          <span class="label">สถานะงาน:</span>
          <span class="value status-badge" :class="`status-${task.status.toLowerCase()}`">
            {{ task.status === 'PENDING' ? '🟡 รอดำเนินการ' : '🔵 กำลังทำ' }}
          </span>
        </div>
        <div v-if="task.started_at" class="info-row">
          <span class="label">เริ่มทำเมื่อ:</span>
          <span class="value">{{ formatDateTime(task.started_at) }}</span>
        </div>
        <div v-if="task.assigned_user_name" class="info-row">
          <span class="label">ผู้รับผิดชอบ:</span>
          <span class="value">{{ task.assigned_user_name }}</span>
        </div>
      </div>

      <!-- Completion Notes -->
      <div class="notes-section">
        <div class="section-title">บันทึกการทำงาน (ไม่บังคับ)</div>
        <n-input
          v-model:value="completionNotes"
          type="textarea"
          placeholder="บันทึกรายละเอียดการทำความสะอาด เช่น พบความเสียหาย, ของหาย, หรือสิ่งผิดปกติ"
          :autosize="{ minRows: 3, maxRows: 5 }"
          maxlength="500"
          show-count
        />
      </div>

      <!-- Maintenance Request Section -->
      <div class="maintenance-section">
        <div class="section-title">พบความเสียหายหรือต้องซ่อม?</div>
        <div class="maintenance-form">
          <div class="form-group">
            <label class="form-label">หมวดหมู่ความเสียหาย</label>
            <n-select
              v-model:value="maintenanceCategory"
              :options="categoryOptions"
              placeholder="เลือกหมวดหมู่ความเสียหาย"
              clearable
            />
          </div>

          <div class="form-group">
            <label class="form-label">รายละเอียดความเสียหาย</label>
            <n-input
              v-model:value="maintenanceDescription"
              type="textarea"
              placeholder="บรรยายความเสียหายที่พบ เช่น ท่อรั่วน้ำ, หลอดไฟเสีย, เก้าอี้หัก"
              :autosize="{ minRows: 2, maxRows: 4 }"
              maxlength="500"
              show-count
            />
          </div>

          <div class="form-group">
            <label class="form-label">ลำดับความสำคัญ</label>
            <n-select
              v-model:value="maintenancePriority"
              :options="priorityOptions"
              placeholder="เลือกลำดับความสำคัญ"
            />
          </div>

          <!-- Photos -->
          <div class="form-group">
            <label class="form-label">รูปถ่ายความเสียหาย</label>
            <div class="photo-upload-container">
              <div class="photo-input-wrapper">
                <input
                  ref="fileInputRef"
                  type="file"
                  multiple
                  accept="image/*"
                  style="display: none"
                  @change="handleFilesSelected"
                />
                <n-button @click="triggerFileInput" type="primary" size="small">
                  📷 เลือกรูปถ่าย
                </n-button>
                <p class="photo-hint">อนุญาตได้สูงสุด 5 รูป (JPG, PNG)</p>
              </div>

              <!-- Photo Preview -->
              <div v-if="selectedMaintenancePhotos.length > 0" class="photo-preview-grid">
                <div v-for="(photo, index) in selectedMaintenancePhotos" :key="index" class="photo-preview-item">
                  <img :src="photo.preview" :alt="`Photo ${index + 1}`" class="preview-image" />
                  <n-button type="error" size="small" @click="removeMaintenancePhoto(index)" class="remove-btn">
                    ✕
                  </n-button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-else class="loading-state">
      <div class="spinner"></div>
      <p>กำลังโหลดข้อมูลงาน...</p>
    </div>

    <template #footer>
      <n-space justify="end">
        <n-button @click="handleCancel" :disabled="isLoading">
          ยกเลิก
        </n-button>
        <n-button
          class="complete-btn"
          @click="handleComplete"
          :loading="isLoading"
          :disabled="!task"
        >
          ✅ ยืนยันทำเสร็จ
        </n-button>
      </n-space>
    </template>
  </n-modal>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { NModal, NSpace, NButton, NInput, NSelect, NRadioGroup, NRadio, useMessage } from 'naive-ui'
import { useHousekeepingStore } from '@/stores/housekeeping'
import { useMaintenanceStore } from '@/stores/maintenance'
import type { HousekeepingTaskWithDetails } from '@/types/housekeeping'
import type { MaintenanceTaskCreate } from '@/types/maintenance'
import dayjs from 'dayjs'
import 'dayjs/locale/th'

dayjs.locale('th')

interface Props {
  show: boolean
  roomId: number | null
}

const props = defineProps<Props>()

interface Emits {
  (e: 'update:show', value: boolean): void
  (e: 'completed'): void
}

const emit = defineEmits<Emits>()

const message = useMessage()
const housekeepingStore = useHousekeepingStore()
const maintenanceStore = useMaintenanceStore()

const isLoading = ref(false)
const completionNotes = ref('')
const task = ref<HousekeepingTaskWithDetails | null>(null)
const fileInputRef = ref<HTMLInputElement | null>(null)

// Maintenance request fields
const maintenanceCategory = ref<string | null>(null)
const maintenanceDescription = ref('')
const maintenancePriority = ref<'URGENT' | 'HIGH' | 'MEDIUM' | 'LOW'>('MEDIUM')
const selectedMaintenancePhotos = ref<Array<{ file: File; preview: string }>>([])

// Category options (matching backend enums)
const categoryOptions = [
  { label: '🔧 ท่อและปั้มน้ำ', value: 'PLUMBING' },
  { label: '⚡ ระบบไฟฟ้า', value: 'ELECTRICAL' },
  { label: '❄️ ระบบปรับอากาศ', value: 'HVAC' },
  { label: '🛋️ เฟอร์นิเจอร์', value: 'FURNITURE' },
  { label: '🔌 เครื่องใช้ไฟฟ้า', value: 'APPLIANCE' },
  { label: '🏢 โครงสร้างอาคาร', value: 'BUILDING' },
  { label: '📝 อื่นๆ', value: 'OTHER' }
]

// Priority options (matching backend enums)
const priorityOptions = [
  { label: '🔴 ด่วนมาก', value: 'URGENT' },
  { label: '🟠 สูง', value: 'HIGH' },
  { label: '🟡 ปานกลาง', value: 'MEDIUM' },
  { label: '🟢 ต่ำ', value: 'LOW' }
]

const isVisible = computed({
  get: () => props.show,
  set: (value) => emit('update:show', value)
})

// Fetch task when modal opens
watch(() => props.show, async (newValue) => {
  if (newValue && props.roomId) {
    await fetchTaskForRoom(props.roomId)
  } else {
    // Reset when modal closes
    task.value = null
    completionNotes.value = ''
    maintenanceCategory.value = null
    maintenanceDescription.value = ''
    maintenancePriority.value = 'MEDIUM'
    // Clean up blob URLs
    selectedMaintenancePhotos.value.forEach((photo) => {
      if (photo.preview.startsWith('blob:')) {
        URL.revokeObjectURL(photo.preview)
      }
    })
    selectedMaintenancePhotos.value = []
  }
})

async function fetchTaskForRoom(roomId: number): Promise<void> {
  try {
    isLoading.value = true

    // Fetch all PENDING or IN_PROGRESS tasks for this room
    await housekeepingStore.fetchTasks({
      room_id: roomId
    })

    // Get PENDING or IN_PROGRESS task for this room (prioritize IN_PROGRESS first)
    const inProgressTasks = housekeepingStore.tasks.filter(
      t => t.room_id === roomId && t.status === 'IN_PROGRESS'
    )

    const pendingTasks = housekeepingStore.tasks.filter(
      t => t.room_id === roomId && t.status === 'PENDING'
    )

    // Use IN_PROGRESS if exists, otherwise use PENDING
    const availableTasks = inProgressTasks.length > 0 ? inProgressTasks : pendingTasks

    if (availableTasks.length > 0) {
      task.value = availableTasks[0]
    } else {
      message.error('ไม่พบงานทำความสะอาดสำหรับห้องนี้')
      handleCancel()
    }
  } catch (error: any) {
    console.error('Error fetching housekeeping task:', error)
    message.error('ไม่สามารถโหลดข้อมูลงานได้')
    handleCancel()
  } finally {
    isLoading.value = false
  }
}

function formatDateTime(datetime: string | null): string {
  if (!datetime) return '-'
  return dayjs(datetime).format('DD/MM/YYYY HH:mm น.')
}

function triggerFileInput() {
  fileInputRef.value?.click()
}

function handleFilesSelected(event: Event) {
  const input = event.target as HTMLInputElement
  const files = Array.from(input.files || [])

  if (selectedMaintenancePhotos.value.length + files.length > 5) {
    message.error('อนุญาตได้สูงสุด 5 รูป')
    return
  }

  files.forEach((file) => {
    // Validate file type
    if (!file.type.startsWith('image/')) {
      message.error('กรุณาเลือกเฉพาะไฟล์รูปภาพ')
      return
    }

    // Create preview
    const reader = new FileReader()
    reader.onload = (e) => {
      selectedMaintenancePhotos.value.push({
        file,
        preview: e.target?.result as string
      })
    }
    reader.readAsDataURL(file)
  })

  // Reset input
  if (input) input.value = ''
}

function removeMaintenancePhoto(index: number) {
  const photo = selectedMaintenancePhotos.value[index]
  if (photo.preview.startsWith('blob:')) {
    URL.revokeObjectURL(photo.preview)
  }
  selectedMaintenancePhotos.value.splice(index, 1)
}

async function handleComplete(): Promise<void> {
  if (!task.value) return

  try {
    isLoading.value = true

    // If task is PENDING, start it first before completing
    if (task.value.status === 'PENDING') {
      await housekeepingStore.startTask(task.value.id)
    }

    // Complete the housekeeping task
    await housekeepingStore.completeTask(
      task.value.id,
      completionNotes.value || undefined
    )

    message.success(`ปิดงานทำความสะอาดห้อง ${task.value.room_number} สำเร็จ`)

    // Create maintenance task if category is selected
    if (maintenanceCategory.value && maintenanceDescription.value.trim()) {
      try {
        // Use FormData to support file uploads
        const formDataWithFiles = new FormData()
        formDataWithFiles.append('room_id', String(task.value.room_id))
        formDataWithFiles.append('title', maintenanceDescription.value.substring(0, 100)) // Use first 100 chars as title
        formDataWithFiles.append('description', maintenanceDescription.value)
        formDataWithFiles.append('category', maintenanceCategory.value)
        formDataWithFiles.append('priority', maintenancePriority.value)

        // Add photos
        selectedMaintenancePhotos.value.forEach((photo) => {
          formDataWithFiles.append('photos', photo.file)
        })

        // Call maintenance API with FormData (path will be prepended with /api/v1 by baseURL)
        const api = (await import('@/api/client')).default
        await api.post('/maintenance/', formDataWithFiles)

        message.success(`สร้างงานซ่อมห้อง ${task.value.room_number} สำเร็จ`)
      } catch (error: any) {
        console.error('Error creating maintenance task:', error)
        console.error('Error response:', error.response?.data)
        message.warning(
          'ปิดงานทำความสะอาดสำเร็จ แต่ไม่สามารถสร้างงานซ่อมได้: ' +
          (error.response?.data?.detail || 'Unknown error')
        )
      }
    }

    // Emit completed event to refresh dashboard
    emit('completed')

    // Close modal
    handleCancel()
  } catch (error: any) {
    console.error('Error completing housekeeping task:', error)
    message.error(
      error.response?.data?.detail || 'ไม่สามารถปิดงานทำความสะอาดได้'
    )
  } finally {
    isLoading.value = false
  }
}

function handleCancel(): void {
  completionNotes.value = ''
  maintenanceCategory.value = null
  maintenanceDescription.value = ''
  maintenancePriority.value = 'MEDIUM'
  // Clean up blob URLs
  selectedMaintenancePhotos.value.forEach((photo) => {
    if (photo.preview.startsWith('blob:')) {
      URL.revokeObjectURL(photo.preview)
    }
  })
  selectedMaintenancePhotos.value = []
  task.value = null
  emit('update:show', false)
}
</script>

<style scoped>
.quick-complete-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.room-info-banner {
  background: linear-gradient(135deg, #FFC107 0%, #FFD54F 100%);
  padding: 20px;
  border-radius: 12px;
  text-align: center;
  color: #333;
}

.room-number {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 4px;
}

.room-type {
  font-size: 16px;
  font-weight: 500;
  opacity: 0.8;
}

.task-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
  background: #f5f5f5;
  padding: 16px;
  border-radius: 8px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
  min-width: 120px;
}

.value {
  font-size: 14px;
  color: #333;
  font-weight: 600;
  text-align: right;
  flex: 1;
}

.value.status-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 13px;
}

.value.status-badge.status-pending {
  background: #fff3cd;
  color: #856404;
}

.value.status-badge.status-in_progress {
  background: #d1ecf1;
  color: #0c5460;
}

.notes-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.section-title {
  font-size: 15px;
  font-weight: 600;
  color: #333;
}

.maintenance-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
  background: #fff8f0;
  border-left: 4px solid #ff6b6b;
  border-radius: 8px;
}

.maintenance-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.photo-upload-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.photo-input-wrapper {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 8px;
}

.photo-hint {
  font-size: 12px;
  color: #999;
  margin: 0;
}

.photo-preview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
  gap: 8px;
}

.photo-preview-item {
  position: relative;
  width: 100%;
  aspect-ratio: 1;
  border-radius: 8px;
  overflow: hidden;
  border: 2px solid #e0e0e0;
}

.preview-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.remove-btn {
  position: absolute !important;
  top: 4px !important;
  right: 4px !important;
  padding: 2px 6px !important;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: #666;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #FFC107;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Complete Button - Match CLEANING room card yellow theme */
:deep(.complete-btn) {
  background: linear-gradient(135deg, #FFC107 0%, #FFD54F 100%) !important;
  color: #333 !important;
  font-weight: 600 !important;
  border: none !important;
  box-shadow: 0 2px 8px rgba(255, 193, 7, 0.3) !important;
  transition: all 0.3s ease !important;
}

:deep(.complete-btn:hover:not(:disabled)) {
  background: linear-gradient(135deg, #FFB300 0%, #FFC107 100%) !important;
  box-shadow: 0 4px 12px rgba(255, 193, 7, 0.5) !important;
  transform: translateY(-2px) !important;
}

:deep(.complete-btn:active:not(:disabled)) {
  transform: translateY(0) !important;
}

:deep(.complete-btn:disabled) {
  opacity: 0.6 !important;
  cursor: not-allowed !important;
}

@media (max-width: 768px) {
  .room-number {
    font-size: 28px;
  }

  .info-row {
    flex-direction: column;
    gap: 4px;
  }

  .label {
    min-width: auto;
  }

  .value {
    text-align: left;
  }
}
</style>
