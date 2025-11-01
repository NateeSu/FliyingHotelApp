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
import api from '@/api/axios'

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

function resetForm() {
  formData.value = {
    room_id: undefined as any,
    title: '',
    description: '',
    category: undefined as any,
    priority: 'MEDIUM'
  }
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

    // Call API to create maintenance task
    const response = await api.post('/api/v1/maintenance/', formData.value)

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
</style>
