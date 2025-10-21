import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { maintenanceApi } from '@/api/maintenance'
import type {
  MaintenanceTaskWithDetails,
  MaintenanceTaskFilters,
  MaintenanceStats,
  MaintenanceTaskCreate,
  MaintenanceTaskUpdate
} from '@/types/maintenance'

export const useMaintenanceStore = defineStore('maintenance', () => {
  // State
  const tasks = ref<MaintenanceTaskWithDetails[]>([])
  const stats = ref<MaintenanceStats | null>(null)
  const isLoading = ref(false)
  const filters = ref<MaintenanceTaskFilters>({})

  // Computed
  const pendingTasks = computed(() =>
    tasks.value.filter(task => task.status === 'pending')
  )

  const inProgressTasks = computed(() =>
    tasks.value.filter(task => task.status === 'in_progress')
  )

  const completedTasks = computed(() =>
    tasks.value.filter(task => task.status === 'completed')
  )

  const urgentTasks = computed(() =>
    tasks.value.filter(task => task.priority === 'urgent' && task.status !== 'completed')
  )

  // Actions
  async function fetchTasks(customFilters?: MaintenanceTaskFilters, skip = 0, limit = 100): Promise<void> {
    try {
      isLoading.value = true
      const filtersToUse = customFilters || filters.value
      const response = await maintenanceApi.getTasks(filtersToUse, skip, limit)
      tasks.value = response.tasks
    } catch (error) {
      console.error('Failed to fetch maintenance tasks:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  async function fetchStats(): Promise<void> {
    try {
      stats.value = await maintenanceApi.getStats()
    } catch (error) {
      console.error('Failed to fetch maintenance stats:', error)
      throw error
    }
  }

  async function getTaskById(taskId: number): Promise<MaintenanceTaskWithDetails> {
    try {
      return await maintenanceApi.getTaskById(taskId)
    } catch (error) {
      console.error(`Failed to fetch maintenance task ${taskId}:`, error)
      throw error
    }
  }

  async function createTask(taskData: MaintenanceTaskCreate): Promise<MaintenanceTaskWithDetails> {
    try {
      const newTask = await maintenanceApi.createTask(taskData)
      // Refresh tasks and stats
      await Promise.all([fetchTasks(), fetchStats()])
      return newTask
    } catch (error) {
      console.error('Failed to create maintenance task:', error)
      throw error
    }
  }

  async function updateTask(taskId: number, taskData: MaintenanceTaskUpdate): Promise<MaintenanceTaskWithDetails> {
    try {
      const updatedTask = await maintenanceApi.updateTask(taskId, taskData)
      // Update in local state
      const index = tasks.value.findIndex(t => t.id === taskId)
      if (index !== -1) {
        tasks.value[index] = updatedTask
      }
      return updatedTask
    } catch (error) {
      console.error(`Failed to update maintenance task ${taskId}:`, error)
      throw error
    }
  }

  async function startTask(taskId: number): Promise<void> {
    try {
      const updatedTask = await maintenanceApi.startTask(taskId)
      // Update in local state
      const index = tasks.value.findIndex(t => t.id === taskId)
      if (index !== -1) {
        tasks.value[index] = updatedTask
      }
      // Refresh stats
      await fetchStats()
    } catch (error) {
      console.error(`Failed to start maintenance task ${taskId}:`, error)
      throw error
    }
  }

  async function completeTask(taskId: number, notes?: string): Promise<void> {
    try {
      const updatedTask = await maintenanceApi.completeTask(taskId, notes ? { notes } : undefined)
      // Update in local state
      const index = tasks.value.findIndex(t => t.id === taskId)
      if (index !== -1) {
        tasks.value[index] = updatedTask
      }
      // Refresh stats
      await fetchStats()
    } catch (error) {
      console.error(`Failed to complete maintenance task ${taskId}:`, error)
      throw error
    }
  }

  async function cancelTask(taskId: number): Promise<void> {
    try {
      const updatedTask = await maintenanceApi.cancelTask(taskId)
      // Update in local state
      const index = tasks.value.findIndex(t => t.id === taskId)
      if (index !== -1) {
        tasks.value[index] = updatedTask
      }
      // Refresh stats
      await fetchStats()
    } catch (error) {
      console.error(`Failed to cancel maintenance task ${taskId}:`, error)
      throw error
    }
  }

  function setFilters(newFilters: MaintenanceTaskFilters): void {
    filters.value = newFilters
  }

  function clearFilters(): void {
    filters.value = {}
  }

  async function refresh(): Promise<void> {
    await Promise.all([fetchTasks(), fetchStats()])
  }

  // Handle WebSocket events
  function handleTaskEvent(eventType: string, data: any): void {
    switch (eventType) {
      case 'maintenance_task_created':
      case 'maintenance_task_updated':
      case 'maintenance_task_started':
      case 'maintenance_task_completed':
      case 'maintenance_task_cancelled':
        // Refresh tasks and stats when any task event occurs
        refresh()
        break
    }
  }

  return {
    // State
    tasks,
    stats,
    isLoading,
    filters,

    // Computed
    pendingTasks,
    inProgressTasks,
    completedTasks,
    urgentTasks,

    // Actions
    fetchTasks,
    fetchStats,
    getTaskById,
    createTask,
    updateTask,
    startTask,
    completeTask,
    cancelTask,
    setFilters,
    clearFilters,
    refresh,
    handleTaskEvent
  }
})
