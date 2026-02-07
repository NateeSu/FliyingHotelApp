<template>
  <n-modal
    v-model:show="isVisible"
    preset="card"
    title="เพิ่มงานซ่อมบำรุง"
    :style="{ maxWidth: '700px' }"
    :bordered="false"
    :segmented="true"
  >
    <n-form
      ref="formRef"
      :model="formData"
      :rules="rules"
      label-placement="top"
      require-mark-placement="left"
    >
      <!-- Room Selection -->
      <n-form-item label="ห้อง" path="room_id" required>
        <n-select
          v-model:value="formData.room_id"
          :options="roomOptions"
          placeholder="เลือกห้อง"
          filterable
          :loading="loadingRooms"
        />
      </n-form-item>

      <!-- Title -->
      <n-form-item label="หัวข้อ" path="title" required>
        <n-input
          v-model:value="formData.title"
          placeholder="เช่น แอร์เสีย, ก๊อกน้ำรั่ว"
          maxlength="200"
          show-count
        />
      </n-form-item>

      <!-- Description -->
      <n-form-item label="รายละเอียด" path="description">
        <n-input
          v-model:value="formData.description"
          type="textarea"
          placeholder="รายละเอียดเพิ่มเติม..."
          :rows="3"
          maxlength="500"
          show-count
        />
      </n-form-item>

      <!-- Category -->
      <n-form-item label="ประเภทงาน" path="category" required>
        <n-select
          v-model:value="formData.category"
          :options="categoryOptions"
          placeholder="เลือกประเภทงาน"
        />
      </n-form-item>

      <!-- Priority -->
      <n-form-item label="ลำดับความสำคัญ" path="priority" required>
        <n-select
          v-model:value="formData.priority"
          :options="priorityOptions"
          placeholder="เลือกลำดับความสำคัญ"
        />
      </n-form-item>

      <!-- Photos -->
      <n-form-item label="รูปถ่าย" path="photos">
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
            <n-button @click="triggerFileInput" type="primary">
              📷 เลือกรูปถ่าย
            </n-button>
            <p class="text-xs text-gray-500 mt-2">อนุญาตได้สูงสุด 5 รูป (JPG, PNG)</p>
          </div>

          <!-- Photo Preview -->
          <div v-if="selectedPhotos.length > 0" class="photo-preview-grid">
            <div v-for="(photo, index) in selectedPhotos" :key="index" class="photo-preview-item">
              <img :src="photo.preview" :alt="`Photo ${index + 1}`" class="preview-image" />
              <n-button type="error" size="small" @click="removePhoto(index)" style="position: absolute; top: 4px; right: 4px;">
                ✕
              </n-button>
            </div>
          </div>
        </div>
      </n-form-item>
    </n-form>

    <template #footer>
      <n-space justify="end">
        <n-button @click="handleCancel">ยกเลิก</n-button>
        <n-button type="primary" @click="handleSubmit" :loading="submitting">
          บันทึก
        </n-button>
      </n-space>
    </template>
  </n-modal>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import {
  NModal,
  NForm,
  NFormItem,
  NInput,
  NSelect,
  NButton,
  NSpace,
  useMessage,
  type FormInst,
  type FormRules
} from 'naive-ui'
import { useDashboardStore } from '@/stores/dashboard'
import { useAuthStore } from '@/stores/auth'
import type { MaintenanceTaskCreate, MaintenanceTaskCategory, MaintenanceTaskPriority } from '@/types/maintenance'
import api from '@/api/client'

// Props & Emits
const props = defineProps<{
  show: boolean
}>()

const emit = defineEmits<{
  'update:show': [value: boolean]
  'created': []
}>()

// Stores
const message = useMessage()
const dashboardStore = useDashboardStore()
const authStore = useAuthStore()

// State
const formRef = ref<FormInst | null>(null)
const submitting = ref(false)
const loadingRooms = ref(false)
const fileInputRef = ref<HTMLInputElement | null>(null)
const selectedPhotos = ref<Array<{ file: File; preview: string }>>([])

const formData = ref<MaintenanceTaskCreate>({
  room_id: undefined as any,
  title: '',
  description: '',
  category: undefined as any,
  priority: 'MEDIUM'
})

// Computed
const isVisible = computed({
  get: () => props.show,
  set: (value) => emit('update:show', value)
})

const roomOptions = computed(() => {
  return dashboardStore.rooms.map((room) => ({
    label: `${room.room_number} - ${room.room_type?.name || 'ไม่ระบุ'}`,
    value: room.id
  }))
})

const categoryOptions = [
  { label: '🚰 ประปา', value: 'PLUMBING' },
  { label: '⚡ ไฟฟ้า', value: 'ELECTRICAL' },
  { label: '❄️ เครื่องปรับอากาศ', value: 'HVAC' },
  { label: '🪑 เฟอร์นิเจอร์', value: 'FURNITURE' },
  { label: '📺 เครื่องใช้ไฟฟ้า', value: 'APPLIANCE' },
  { label: '🏢 อาคาร', value: 'BUILDING' },
  { label: '🔧 อื่นๆ', value: 'OTHER' }
]

const priorityOptions = [
  { label: '🔴 ด่วนมาก', value: 'URGENT' },
  { label: '🟠 สูง', value: 'HIGH' },
  { label: '🟡 ปานกลาง', value: 'MEDIUM' },
  { label: '🟢 ต่ำ', value: 'LOW' }
]

// Validation Rules
const rules: FormRules = {
  room_id: [
    {
      required: true,
      type: 'number',
      message: 'กรุณาเลือกห้อง',
      trigger: 'change'
    }
  ],
  title: [
    {
      required: true,
      message: 'กรุณากรอกหัวข้อ',
      trigger: 'blur'
    },
    {
      min: 3,
      max: 200,
      message: 'หัวข้อต้องมี 3-200 ตัวอักษร',
      trigger: 'blur'
    }
  ],
  category: [
    {
      required: true,
      message: 'กรุณาเลือกประเภทงาน',
      trigger: 'change'
    }
  ],
  priority: [
    {
      required: true,
      message: 'กรุณาเลือกลำดับความสำคัญ',
      trigger: 'change'
    }
  ]
}

// Methods
async function loadRooms() {
  loadingRooms.value = true
  try {
    await dashboardStore.fetchRooms()
  } catch (error) {
    message.error('ไม่สามารถโหลดข้อมูลห้องได้')
  } finally {
    loadingRooms.value = false
  }
}

function triggerFileInput() {
  fileInputRef.value?.click()
}

function handleFilesSelected(event: Event) {
  const input = event.target as HTMLInputElement
  const files = Array.from(input.files || [])
  
  if (selectedPhotos.value.length + files.length > 5) {
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
      selectedPhotos.value.push({
        file,
        preview: e.target?.result as string
      })
    }
    reader.readAsDataURL(file)
  })
  
  // Reset input
  if (input) input.value = ''
}

function removePhoto(index: number) {
  const photo = selectedPhotos.value[index]
  if (photo.preview.startsWith('blob:')) {
    URL.revokeObjectURL(photo.preview)
  }
  selectedPhotos.value.splice(index, 1)
}

function resetForm() {
  formData.value = {
    room_id: undefined as any,
    title: '',
    description: '',
    category: undefined as any,
    priority: 'MEDIUM'
  }
  // Clean up blob URLs
  selectedPhotos.value.forEach((photo) => {
    if (photo.preview.startsWith('blob:')) {
      URL.revokeObjectURL(photo.preview)
    }
  })
  selectedPhotos.value = []
  formRef.value?.restoreValidation()
}

function handleCancel() {
  resetForm()
  isVisible.value = false
}

async function handleSubmit() {
  try {
    await formRef.value?.validate()

    submitting.value = true

    // Prepare FormData for file upload
    const formDataWithFiles = new FormData()
    formDataWithFiles.append('room_id', String(formData.value.room_id))
    formDataWithFiles.append('title', formData.value.title)
    formDataWithFiles.append('description', formData.value.description || '')
    formDataWithFiles.append('category', formData.value.category)
    formDataWithFiles.append('priority', formData.value.priority)
    
    // Add photos
    selectedPhotos.value.forEach((photo) => {
      formDataWithFiles.append('photos', photo.file)
    })

    // Call API to create maintenance task
    // Note: Don't set Content-Type header manually for FormData
    // Browser will automatically set it with the correct boundary parameter
    const response = await api.post('/maintenance/', formDataWithFiles)

    message.success('เพิ่มงานซ่อมบำรุงสำเร็จ')
    emit('created')
    resetForm()
    isVisible.value = false
  } catch (error: any) {
    if (error?.errors) {
      // Validation error from n-form
      return
    }
    message.error(error.response?.data?.detail || 'ไม่สามารถเพิ่มงานซ่อมบำรุงได้')
  } finally {
    submitting.value = false
  }
}

// Watchers
watch(
  () => props.show,
  (newVal) => {
    if (newVal) {
      loadRooms()
    }
  }
)

// Lifecycle
onMounted(() => {
  if (dashboardStore.rooms.length === 0) {
    loadRooms()
  }
})
</script>

<style scoped>
:deep(.n-form-item-label) {
  font-weight: 600;
  color: var(--color-navy);
}

:deep(.n-input),
:deep(.n-select) {
  border-radius: 8px;
}

:deep(.n-button) {
  border-radius: 8px;
  font-weight: 600;
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

.text-xs {
  font-size: 12px;
}

.text-gray-500 {
  color: #999;
}

.mt-2 {
  margin-top: 8px;
}

.photo-preview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 12px;
  margin-top: 12px;
}

.photo-preview-item {
  position: relative;
  width: 100%;
  aspect-ratio: 1;
  border-radius: 8px;
  overflow: hidden;
  background: #f5f5f5;
  border: 2px solid #e0e0e0;
}

.preview-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
</style>
