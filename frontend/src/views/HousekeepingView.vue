<template>
  <div class="housekeeping-view">
    <!-- Header with Stats -->
    <div class="header">
      <h1 class="title">งานทำความสะอาด</h1>

      <div class="stats-cards" v-if="housekeepingStore.stats">
        <div class="stat-card pending">
          <div class="stat-icon">⏳</div>
          <div class="stat-content">
            <div class="stat-label">รอดำเนินการ</div>
            <div class="stat-value">{{ housekeepingStore.stats.pending_tasks }}</div>
          </div>
        </div>

        <div class="stat-card in-progress">
          <div class="stat-icon">🔄</div>
          <div class="stat-content">
            <div class="stat-label">กำลังทำ</div>
            <div class="stat-value">{{ housekeepingStore.stats.in_progress_tasks }}</div>
          </div>
        </div>

        <div class="stat-card completed">
          <div class="stat-icon">✅</div>
          <div class="stat-content">
            <div class="stat-label">เสร็จวันนี้</div>
            <div class="stat-value">{{ housekeepingStore.stats.completed_today }}</div>
          </div>
        </div>

        <div class="stat-card avg-time">
          <div class="stat-icon">⏱️</div>
          <div class="stat-content">
            <div class="stat-label">เวลาเฉลี่ย</div>
            <div class="stat-value">
              {{ housekeepingStore.stats.avg_duration_minutes?.toFixed(0) || '-' }} นาที
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="filters">
      <n-space>
        <n-select
          v-model:value="selectedStatus"
          :options="statusOptions"
          placeholder="สถานะ"
          clearable
          style="width: 200px"
          @update:value="handleFilterChange"
        />

        <n-select
          v-model:value="selectedPriority"
          :options="priorityOptions"
          placeholder="ลำดับความสำคัญ"
          clearable
          style="width: 200px"
          @update:value="handleFilterChange"
        />

        <n-button @click="handleRefresh" :loading="housekeepingStore.isLoading">
          🔄 รีเฟรช
        </n-button>
      </n-space>
    </div>

    <!-- Task List -->
    <div class="tasks-container">
      <n-spin :show="housekeepingStore.isLoading">
        <div v-if="housekeepingStore.tasks.length === 0" class="empty-state">
          <div class="empty-icon">🧹</div>
          <div class="empty-text">ไม่มีงานทำความสะอาด</div>
        </div>

        <div v-else class="tasks-grid">
          <TaskCard
            v-for="task in housekeepingStore.tasks"
            :key="task.id"
            :task="task"
            @click="handleTaskClick(task)"
            @start="handleStartTask"
            @complete="handleCompleteTask"
          />
        </div>
      </n-spin>
    </div>

    <!-- Task Detail Modal -->
    <TaskDetailModal
      v-model:show="showDetailModal"
      :task="selectedTask"
      @start="handleStartTask"
      @complete="handleCompleteTask"
      @updated="handleTaskUpdated"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { NSpace, NSelect, NButton, NSpin, useMessage } from 'naive-ui'
import { useHousekeepingStore } from '@/stores/housekeeping'
import TaskCard from '@/components/TaskCard.vue'
import TaskDetailModal from '@/components/TaskDetailModal.vue'
import type { HousekeepingTaskWithDetails, HousekeepingTaskStatus, HousekeepingTaskPriority } from '@/types/housekeeping'

const message = useMessage()
const housekeepingStore = useHousekeepingStore()

// State
const selectedStatus = ref<HousekeepingTaskStatus | null>(null)
const selectedPriority = ref<HousekeepingTaskPriority | null>(null)
const showDetailModal = ref(false)
const selectedTask = ref<HousekeepingTaskWithDetails | null>(null)

// Options
const statusOptions = [
  { label: 'รอดำเนินการ', value: 'pending' },
  { label: 'กำลังทำ', value: 'in_progress' },
  { label: 'เสร็จสิ้น', value: 'completed' },
  { label: 'ยกเลิก', value: 'cancelled' }
]

const priorityOptions = [
  { label: '🔴 ด่วนมาก', value: 'urgent' },
  { label: '🟠 สูง', value: 'high' },
  { label: '🟡 ปานกลาง', value: 'medium' },
  { label: '🟢 ต่ำ', value: 'low' }
]

// Methods
async function loadData() {
  try {
    await Promise.all([
      housekeepingStore.fetchTasks(),
      housekeepingStore.fetchStats()
    ])
  } catch (error: any) {
    message.error('ไม่สามารถโหลดข้อมูลได้')
  }
}

function handleFilterChange() {
  const filters: any = {}
  if (selectedStatus.value) filters.status = selectedStatus.value
  if (selectedPriority.value) filters.priority = selectedPriority.value

  housekeepingStore.setFilters(filters)
  housekeepingStore.fetchTasks()
}

function handleRefresh() {
  housekeepingStore.refresh()
}

function handleTaskClick(task: HousekeepingTaskWithDetails) {
  selectedTask.value = task
  showDetailModal.value = true
}

async function handleStartTask(taskId: number) {
  try {
    await housekeepingStore.startTask(taskId)
    message.success('เริ่มทำงานแล้ว')
  } catch (error: any) {
    message.error(error.response?.data?.detail || 'ไม่สามารถเริ่มงานได้')
  }
}

async function handleCompleteTask(taskId: number, notes?: string) {
  try {
    await housekeepingStore.completeTask(taskId, notes)
    message.success('ทำงานเสร็จแล้ว ห้องพร้อมให้บริการ')
  } catch (error: any) {
    message.error(error.response?.data?.detail || 'ไม่สามารถทำงานให้เสร็จได้')
  }
}

function handleTaskUpdated() {
  housekeepingStore.fetchTasks()
  housekeepingStore.fetchStats()
}

// Lifecycle
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.housekeeping-view {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.header {
  margin-bottom: 32px;
}

.title {
  font-size: 32px;
  font-weight: 700;
  color: var(--color-navy);
  margin-bottom: 24px;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: linear-gradient(135deg, #3338A0 0%, #2a2d80 100%);
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 4px 12px rgba(51, 56, 160, 0.2);
  transition: transform 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
}

.stat-card.pending {
  background: linear-gradient(135deg, #FCC61D 0%, #C59560 100%);
}

.stat-card.in-progress {
  background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
}

.stat-card.completed {
  background: linear-gradient(135deg, #4CAF50 0%, #388E3C 100%);
}

.stat-card.avg-time {
  background: linear-gradient(135deg, #9C27B0 0%, #7B1FA2 100%);
}

.stat-icon {
  font-size: 48px;
}

.stat-content {
  flex: 1;
}

.stat-label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 4px;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: white;
}

.filters {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
}

.tasks-container {
  min-height: 400px;
}

.tasks-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.empty-state {
  text-align: center;
  padding: 80px 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.empty-icon {
  font-size: 80px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.empty-text {
  font-size: 18px;
  color: #999;
  font-weight: 500;
}

@media (max-width: 768px) {
  .housekeeping-view {
    padding: 16px;
  }

  .title {
    font-size: 24px;
  }

  .stats-cards {
    grid-template-columns: 1fr;
  }

  .tasks-grid {
    grid-template-columns: 1fr;
  }
}
</style>
