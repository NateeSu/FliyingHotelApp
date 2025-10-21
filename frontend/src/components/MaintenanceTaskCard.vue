<template>
  <div
    class="task-card"
    :class="[
      `status-${task.status}`,
      `priority-${task.priority}`
    ]"
    @click="$emit('click', task)"
  >
    <!-- Header --  >
    <div class="task-header">
      <div class="room-info">
        <span class="room-number">ห้อง {{ task.room_number }}</span>
        <span class="room-type">{{ task.room_type_name }}</span>
      </div>
      <div class="priority-badge" :class="`priority-${task.priority}`">
        {{ priorityLabel }}
      </div>
    </div>

    <!-- Category Badge -->
    <div class="category-badge" :class="`category-${task.category}`">
      {{ categoryLabel }}
    </div>

    <!-- Status Badge -->
    <div class="status-badge" :class="`status-${task.status}`">
      {{ statusLabel }}
    </div>

    <!-- Task Info -->
    <div class="task-info">
      <div class="task-title">{{ task.title }}</div>
      <div v-if="task.description" class="task-description">
        {{ task.description }}
      </div>
    </div>

    <!-- Assignment Info -->
    <div v-if="task.assigned_user_name" class="assignment-info">
      <span class="label">ผู้รับผิดชอบ:</span>
      <span class="value">{{ task.assigned_user_name }}</span>
    </div>

    <!-- Time Info -->
    <div class="time-info">
      <div class="time-row">
        <span class="label">สร้างเมื่อ:</span>
        <span class="value">{{ formatDateTime(task.created_at) }}</span>
      </div>
      <div v-if="task.started_at" class="time-row">
        <span class="label">เริ่มเมื่อ:</span>
        <span class="value">{{ formatDateTime(task.started_at) }}</span>
      </div>
      <div v-if="task.completed_at" class="time-row">
        <span class="label">เสร็จเมื่อ:</span>
        <span class="value">{{ formatDateTime(task.completed_at) }}</span>
      </div>
      <div v-if="task.duration_minutes" class="time-row">
        <span class="label">ระยะเวลา:</span>
        <span class="value">{{ task.duration_minutes }} นาที</span>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="action-buttons" @click.stop>
      <n-button
        v-if="task.status === 'pending'"
        type="primary"
        @click="$emit('start', task.id)"
        block
      >
        ▶️ เริ่มทำงาน
      </n-button>

      <n-button
        v-if="task.status === 'in_progress'"
        type="success"
        @click="$emit('complete', task.id)"
        block
      >
        ✅ ทำเสร็จ
      </n-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { NButton } from 'naive-ui'
import type { MaintenanceTaskWithDetails } from '@/types/maintenance'
import dayjs from 'dayjs'
import 'dayjs/locale/th'

dayjs.locale('th')

interface Props {
  task: MaintenanceTaskWithDetails
}

const props = defineProps<Props>()

interface Emits {
  click: [task: MaintenanceTaskWithDetails]
  start: [taskId: number]
  complete: [taskId: number]
}

defineEmits<Emits>()

const statusLabel = computed(() => {
  const statusMap: Record<string, string> = {
    pending: 'รอดำเนินการ',
    in_progress: 'กำลังทำ',
    completed: 'เสร็จสิ้น',
    cancelled: 'ยกเลิก'
  }
  return statusMap[props.task.status] || props.task.status
})

const priorityLabel = computed(() => {
  const priorityMap: Record<string, string> = {
    urgent: '🔴 ด่วนมาก',
    high: '🟠 สูง',
    medium: '🟡 ปานกลาง',
    low: '🟢 ต่ำ'
  }
  return priorityMap[props.task.priority] || props.task.priority
})

const categoryLabel = computed(() => {
  const categoryMap: Record<string, string> = {
    plumbing: '🚰 ประปา',
    electrical: '⚡ ไฟฟ้า',
    hvac: '❄️ เครื่องปรับอากาศ',
    furniture: '🪑 เฟอร์นิเจอร์',
    appliance: '📺 เครื่องใช้ไฟฟ้า',
    building: '🏢 อาคาร',
    other: '🔧 อื่นๆ'
  }
  return categoryMap[props.task.category] || props.task.category
})

function formatDateTime(datetime: string | null): string {
  if (!datetime) return '-'
  return dayjs(datetime).format('DD/MM/YYYY HH:mm')
}
</script>

<style scoped>
.task-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-left: 4px solid var(--color-navy);
}

.task-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

.task-card.priority-urgent {
  border-left-color: #f44336;
}

.task-card.priority-high {
  border-left-color: #ff9800;
}

.task-card.priority-medium {
  border-left-color: #ffc107;
}

.task-card.priority-low {
  border-left-color: #4caf50;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.room-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.room-number {
  font-size: 24px;
  font-weight: 700;
  color: var(--color-navy);
}

.room-type {
  font-size: 12px;
  color: #666;
  font-weight: 500;
}

.priority-badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
}

.priority-badge.priority-urgent {
  background: rgba(244, 67, 54, 0.15);
  color: #d32f2f;
}

.priority-badge.priority-high {
  background: rgba(255, 152, 0, 0.15);
  color: #f57c00;
}

.priority-badge.priority-medium {
  background: rgba(255, 193, 7, 0.15);
  color: #f57f17;
}

.priority-badge.priority-low {
  background: rgba(76, 175, 80, 0.15);
  color: #388e3c;
}

.category-badge {
  display: inline-block;
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 8px;
  background: rgba(51, 56, 160, 0.1);
  color: var(--color-navy);
}

.status-badge {
  display: inline-block;
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 12px;
}

.status-badge.status-pending {
  background: rgba(255, 193, 7, 0.2);
  color: #f57f17;
}

.status-badge.status-in_progress {
  background: rgba(33, 150, 243, 0.2);
  color: #1976d2;
}

.status-badge.status-completed {
  background: rgba(76, 175, 80, 0.2);
  color: #388e3c;
}

.status-badge.status-cancelled {
  background: rgba(158, 158, 158, 0.2);
  color: #616161;
}

.task-info {
  margin-bottom: 16px;
}

.task-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-navy);
  margin-bottom: 8px;
}

.task-description {
  font-size: 14px;
  color: #666;
  line-height: 1.5;
}

.assignment-info {
  padding: 12px;
  background: rgba(51, 56, 160, 0.05);
  border-radius: 8px;
  margin-bottom: 16px;
  font-size: 14px;
}

.assignment-info .label {
  color: #666;
  font-weight: 500;
  margin-right: 8px;
}

.assignment-info .value {
  color: var(--color-navy);
  font-weight: 600;
}

.time-info {
  background: #f5f5f5;
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 16px;
}

.time-row {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  margin-bottom: 6px;
}

.time-row:last-child {
  margin-bottom: 0;
}

.time-row .label {
  color: #666;
  font-weight: 500;
}

.time-row .value {
  color: var(--color-navy);
  font-weight: 600;
}

.action-buttons {
  margin-top: 16px;
}

@media (max-width: 768px) {
  .task-card {
    padding: 16px;
  }

  .room-number {
    font-size: 20px;
  }
}
</style>
