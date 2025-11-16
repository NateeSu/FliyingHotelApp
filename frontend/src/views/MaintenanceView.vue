<template>
  <div class="maintenance-view">
    <!-- Header with Stats -->
    <div class="header">
      <h1 class="title">งานซ่อมบำรุง</h1>

      <div class="stats-cards" v-if="maintenanceStore.stats">
        <div class="stat-card pending">
          <div class="stat-icon">⏳</div>
          <div class="stat-content">
            <div class="stat-label">รอดำเนินการ</div>
            <div class="stat-value">{{ maintenanceStore.stats.pending_tasks }}</div>
          </div>
        </div>

        <div class="stat-card in-progress">
          <div class="stat-icon">🔧</div>
          <div class="stat-content">
            <div class="stat-label">กำลังทำ</div>
            <div class="stat-value">{{ maintenanceStore.stats.in_progress_tasks }}</div>
          </div>
        </div>

        <div class="stat-card completed">
          <div class="stat-icon">✅</div>
          <div class="stat-content">
            <div class="stat-label">เสร็จวันนี้</div>
            <div class="stat-value">{{ maintenanceStore.stats.completed_today }}</div>
          </div>
        </div>

        <div class="stat-card avg-time">
          <div class="stat-icon">⏱️</div>
          <div class="stat-content">
            <div class="stat-label">เวลาเฉลี่ย</div>
            <div class="stat-value">
              {{ maintenanceStore.stats.avg_duration_minutes?.toFixed(0) || '-' }} นาที
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="filters">
      <n-space justify="space-between" style="width: 100%">
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

          <n-select
            v-model:value="selectedCategory"
            :options="categoryOptions"
            placeholder="ประเภทงาน"
            clearable
            style="width: 200px"
            @update:value="handleFilterChange"
          />

          <n-button @click="handleRefresh" :loading="maintenanceStore.isLoading">
            🔄 รีเฟรช
          </n-button>
        </n-space>

        <n-button type="primary" @click="showCreateModal = true">
          ➕ เพิ่มงานซ่อม
        </n-button>
      </n-space>
    </div>

    <!-- Task List -->
    <div class="tasks-container">
      <n-spin :show="maintenanceStore.isLoading">
        <div v-if="maintenanceStore.tasks.length === 0" class="empty-state">
          <div class="empty-icon">🔧</div>
          <div class="empty-text">ไม่มีงานซ่อมบำรุง</div>
        </div>

        <div v-else class="tasks-grid">
          <MaintenanceTaskCard
            v-for="task in maintenanceStore.tasks"
            :key="task.id"
            :task="task"
            @click="handleTaskClick(task)"
            @start="handleStartTask"
            @complete="handleCompleteTask"
          />
        </div>
      </n-spin>
    </div>

    <!-- Create Task Modal -->
    <MaintenanceCreateModal
      v-model:show="showCreateModal"
      @created="handleTaskCreated"
    />

    <!-- Task Detail Modal -->
    <MaintenanceTaskModal
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
import { useMaintenanceStore } from '@/stores/maintenance'
import MaintenanceTaskCard from '@/components/MaintenanceTaskCard.vue'
import MaintenanceTaskModal from '@/components/MaintenanceTaskModal.vue'
import MaintenanceCreateModal from '@/components/MaintenanceCreateModal.vue'
import type {
  MaintenanceTaskWithDetails,
  MaintenanceTaskStatus,
  MaintenanceTaskPriority,
  MaintenanceTaskCategory
} from '@/types/maintenance'

const message = useMessage()
const maintenanceStore = useMaintenanceStore()

// State
const selectedStatus = ref<MaintenanceTaskStatus | null>(null)
const selectedPriority = ref<MaintenanceTaskPriority | null>(null)
const selectedCategory = ref<MaintenanceTaskCategory | null>(null)
const showCreateModal = ref(false)
const showDetailModal = ref(false)
const selectedTask = ref<MaintenanceTaskWithDetails | null>(null)

// Options
const statusOptions = [
  { label: 'รอดำเนินการ', value: 'PENDING' },
  { label: 'กำลังทำ', value: 'IN_PROGRESS' },
  { label: 'เสร็จสิ้น', value: 'COMPLETED' },
  { label: 'ยกเลิก', value: 'CANCELLED' }
]

const priorityOptions = [
  { label: '🔴 ด่วนมาก', value: 'URGENT' },
  { label: '🟠 สูง', value: 'HIGH' },
  { label: '🟡 ปานกลาง', value: 'MEDIUM' },
  { label: '🟢 ต่ำ', value: 'LOW' }
]

const categoryOptions = [
  { label: '🚰 ประปา', value: 'PLUMBING' },
  { label: '⚡ ไฟฟ้า', value: 'ELECTRICAL' },
  { label: '❄️ เครื่องปรับอากาศ', value: 'HVAC' },
  { label: '🪑 เฟอร์นิเจอร์', value: 'FURNITURE' },
  { label: '📺 เครื่องใช้ไฟฟ้า', value: 'APPLIANCE' },
  { label: '🏢 อาคาร', value: 'BUILDING' },
  { label: '🔧 อื่นๆ', value: 'OTHER' }
]

// Methods
async function loadData() {
  try {
    await Promise.all([
      maintenanceStore.fetchTasks(),
      maintenanceStore.fetchStats()
    ])
  } catch (error: any) {
    message.error('ไม่สามารถโหลดข้อมูลได้')
  }
}

function handleFilterChange() {
  const filters: any = {}
  if (selectedStatus.value) filters.status = selectedStatus.value
  if (selectedPriority.value) filters.priority = selectedPriority.value
  if (selectedCategory.value) filters.category = selectedCategory.value

  maintenanceStore.setFilters(filters)
  maintenanceStore.fetchTasks()
}

function handleRefresh() {
  maintenanceStore.refresh()
}

function handleTaskClick(task: MaintenanceTaskWithDetails) {
  selectedTask.value = task
  showDetailModal.value = true
}

async function handleStartTask(taskId: number) {
  try {
    await maintenanceStore.startTask(taskId)
    message.success('เริ่มทำงานแล้ว')
  } catch (error: any) {
    message.error(error.response?.data?.detail || 'ไม่สามารถเริ่มงานได้')
  }
}

async function handleCompleteTask(taskId: number, notes?: string) {
  try {
    await maintenanceStore.completeTask(taskId, notes)
    message.success('ทำงานเสร็จแล้ว')
  } catch (error: any) {
    message.error(error.response?.data?.detail || 'ไม่สามารถทำงานให้เสร็จได้')
  }
}

function handleTaskUpdated() {
  maintenanceStore.fetchTasks()
  maintenanceStore.fetchStats()
}

function handleTaskCreated() {
  message.success('เพิ่มงานซ่อมบำรุงสำเร็จ')
  maintenanceStore.fetchTasks()
  maintenanceStore.fetchStats()
}

// Lifecycle
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.maintenance-view {
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
  .maintenance-view {
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
