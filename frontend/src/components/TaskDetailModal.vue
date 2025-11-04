<template>
  <n-modal
    v-model:show="isVisible"
    preset="card"
    title="รายละเอียดงานทำความสะอาด"
    :style="{ maxWidth: '700px' }"
    :bordered="false"
    :segmented="true"
  >
    <div v-if="task" class="task-detail">
      <!-- Room Info -->
      <div class="section">
        <div class="section-title">ข้อมูลห้อง</div>
        <div class="info-grid">
          <div class="info-item">
            <span class="label">ห้อง:</span>
            <span class="value room-number">{{ task.room_number }}</span>
          </div>
          <div class="info-item">
            <span class="label">ประเภท:</span>
            <span class="value">{{ task.room_type_name }}</span>
          </div>
        </div>
      </div>

      <!-- Task Info -->
      <div class="section">
        <div class="section-title">ข้อมูลงาน</div>
        <div class="info-grid">
          <div class="info-item full-width">
            <span class="label">สถานะ:</span>
            <n-tag :type="getStatusType(task.status)" size="medium">
              {{ getStatusLabel(task.status) }}
            </n-tag>
          </div>
          <div class="info-item full-width">
            <span class="label">ลำดับความสำคัญ:</span>
            <n-tag :type="getPriorityType(task.priority)" size="medium">
              {{ getPriorityLabel(task.priority) }}
            </n-tag>
          </div>
          <div class="info-item full-width">
            <span class="label">หัวข้อ:</span>
            <span class="value">{{ task.title }}</span>
          </div>
          <div v-if="task.description" class="info-item full-width">
            <span class="label">รายละเอียด:</span>
            <span class="value">{{ task.description }}</span>
          </div>
        </div>
      </div>

      <!-- Assignment Info -->
      <div class="section">
        <div class="section-title">ผู้รับผิดชอบ</div>
        <div class="info-grid">
          <div class="info-item">
            <span class="label">มอบหมายให้:</span>
            <span class="value">{{ task.assigned_user_name || 'ยังไม่มอบหมาย' }}</span>
          </div>
          <div class="info-item">
            <span class="label">สร้างโดย:</span>
            <span class="value">{{ task.creator_name }}</span>
          </div>
          <div v-if="task.completer_name" class="info-item">
            <span class="label">ทำเสร็จโดย:</span>
            <span class="value">{{ task.completer_name }}</span>
          </div>
        </div>
      </div>

      <!-- Time Info -->
      <div class="section">
        <div class="section-title">เวลา</div>
        <div class="info-grid">
          <div class="info-item">
            <span class="label">สร้างเมื่อ:</span>
            <span class="value">{{ formatDateTime(task.created_at) }}</span>
          </div>
          <div v-if="task.started_at" class="info-item">
            <span class="label">เริ่มเมื่อ:</span>
            <span class="value">{{ formatDateTime(task.started_at) }}</span>
          </div>
          <div v-if="task.completed_at" class="info-item">
            <span class="label">เสร็จเมื่อ:</span>
            <span class="value">{{ formatDateTime(task.completed_at) }}</span>
          </div>
          <div v-if="task.duration_minutes" class="info-item">
            <span class="label">ระยะเวลา:</span>
            <span class="value highlight">{{ task.duration_minutes }} นาที</span>
          </div>
        </div>
      </div>

      <!-- Notes -->
      <div v-if="task.notes" class="section">
        <div class="section-title">หมายเหตุ</div>
        <div class="notes-content">{{ task.notes }}</div>
      </div>

      <!-- Completion Notes Input (for completing task) -->
      <div v-if="task.status === 'IN_PROGRESS'" class="section">
        <div class="section-title">บันทึกการทำงาน</div>
        <n-input
          v-model:value="completionNotes"
          type="textarea"
          placeholder="บันทึกรายละเอียดการทำความสะอาด เช่น พบความเสียหาย, ของหาย, หรือสิ่งผิดปกติ (ไม่บังคับ)"
          :autosize="{ minRows: 3, maxRows: 5 }"
          maxlength="500"
          show-count
        />
      </div>
    </div>

    <template #footer>
      <n-space justify="end">
        <n-button @click="handleClose">
          ปิด
        </n-button>

        <n-button
          v-if="task && task.status === 'PENDING'"
          type="primary"
          @click="handleStart"
          :loading="isLoading"
        >
          ▶️ เริ่มทำงาน
        </n-button>

        <n-button
          v-if="task && task.status === 'IN_PROGRESS'"
          type="success"
          @click="handleComplete"
          :loading="isLoading"
        >
          ✅ ทำเสร็จ
        </n-button>
      </n-space>
    </template>
  </n-modal>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { NModal, NSpace, NButton, NTag, NInput } from 'naive-ui'
import type { HousekeepingTaskWithDetails } from '@/types/housekeeping'
import dayjs from 'dayjs'
import 'dayjs/locale/th'

dayjs.locale('th')

interface Props {
  show: boolean
  task: HousekeepingTaskWithDetails | null
}

const props = defineProps<Props>()

interface Emits {
  (e: 'update:show', value: boolean): void
  (e: 'start', taskId: number): void
  (e: 'complete', taskId: number, notes?: string): void
  (e: 'updated'): void
}

const emit = defineEmits<Emits>()

const isLoading = ref(false)
const completionNotes = ref('')
const showCompletionNotes = ref(false)

const isVisible = computed({
  get: () => props.show,
  set: (value) => emit('update:show', value)
})

function getStatusLabel(status: string): string {
  const statusMap: Record<string, string> = {
    PENDING: 'รอดำเนินการ',
    IN_PROGRESS: 'กำลังทำ',
    COMPLETED: 'เสร็จสิ้น',
    CANCELLED: 'ยกเลิก'
  }
  return statusMap[status] || status
}

function getStatusType(status: string): 'warning' | 'info' | 'success' | 'default' {
  const typeMap: Record<string, 'warning' | 'info' | 'success' | 'default'> = {
    PENDING: 'warning',
    IN_PROGRESS: 'info',
    COMPLETED: 'success',
    CANCELLED: 'default'
  }
  return typeMap[status] || 'default'
}

function getPriorityLabel(priority: string): string {
  const priorityMap: Record<string, string> = {
    URGENT: '🔴 ด่วนมาก',
    HIGH: '🟠 สูง',
    MEDIUM: '🟡 ปานกลาง',
    LOW: '🟢 ต่ำ'
  }
  return priorityMap[priority] || priority
}

function getPriorityType(priority: string): 'error' | 'warning' | 'info' | 'success' {
  const typeMap: Record<string, 'error' | 'warning' | 'info' | 'success'> = {
    URGENT: 'error',
    HIGH: 'warning',
    MEDIUM: 'info',
    LOW: 'success'
  }
  return typeMap[priority] || 'info'
}

function formatDateTime(datetime: string | null): string {
  if (!datetime) return '-'
  return dayjs(datetime).format('DD/MM/YYYY HH:mm น.')
}

function handleStart() {
  if (!props.task) return
  emit('start', props.task.id)
  emit('updated')
  handleClose()
}

function handleComplete() {
  if (!props.task) return

  if (!showCompletionNotes.value) {
    showCompletionNotes.value = true
    return
  }

  emit('complete', props.task.id, completionNotes.value || undefined)
  emit('updated')
  handleClose()
}

function handleClose() {
  showCompletionNotes.value = false
  completionNotes.value = ''
  emit('update:show', false)
}

watch(() => props.show, (newValue) => {
  if (!newValue) {
    showCompletionNotes.value = false
    completionNotes.value = ''
  }
})
</script>

<style scoped>
.task-detail {
  padding: 4px 0;
}

.section {
  margin-bottom: 24px;
}

.section:last-child {
  margin-bottom: 0;
}

.section-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--color-navy);
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 2px solid var(--color-gold);
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-item.full-width {
  grid-column: 1 / -1;
}

.label {
  font-size: 13px;
  color: #666;
  font-weight: 500;
}

.value {
  font-size: 15px;
  color: var(--color-navy);
  font-weight: 600;
}

.value.room-number {
  font-size: 24px;
  color: var(--color-gold);
}

.value.highlight {
  color: var(--color-gold);
  font-size: 18px;
}

.notes-content {
  padding: 16px;
  background: #f5f5f5;
  border-radius: 8px;
  font-size: 14px;
  color: var(--color-navy);
  line-height: 1.6;
  white-space: pre-wrap;
}

@media (max-width: 768px) {
  .info-grid {
    grid-template-columns: 1fr;
  }

  .info-item.full-width {
    grid-column: 1;
  }
}
</style>
