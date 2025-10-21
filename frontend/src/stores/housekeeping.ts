/**
 * Housekeeping Store (Phase 5)
 * State management for housekeeping tasks
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { housekeepingApi } from '@/api/housekeeping'
import type {
  HousekeepingTaskWithDetails,
  HousekeepingStats,
  HousekeepingTaskFilters,
  HousekeepingTaskStatus,
  HousekeepingTaskPriority
} from '@/types/housekeeping'

export const useHousekeepingStore = defineStore('housekeeping', () => {
  // State
  const tasks = ref<HousekeepingTaskWithDetails[]>([])
  const stats = ref<HousekeepingStats | null>(null)
  const currentTask = ref<HousekeepingTaskWithDetails | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const total = ref(0)

  // Filters
  const filters = ref<HousekeepingTaskFilters>({})

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

  const highPriorityTasks = computed(() =>
    tasks.value.filter(task => task.priority === 'high' && task.status !== 'completed')
  )

  // Actions
  async function fetchTasks(
    customFilters?: HousekeepingTaskFilters,
    skip = 0,
    limit = 100
  ): Promise<void> {
    try {
      isLoading.value = true
      error.value = null

      const activeFilters = customFilters || filters.value
      const response = await housekeepingApi.getTasks(activeFilters, skip, limit)

      tasks.value = response.data
      total.value = response.total
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'ไม่สามารถโหลดข้อมูลงานได้'
      console.error('Error fetching housekeeping tasks:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function fetchTaskById(taskId: number): Promise<HousekeepingTaskWithDetails> {
    try {
      isLoading.value = true
      error.value = null

      const task = await housekeepingApi.getTaskById(taskId)
      currentTask.value = task

      // Update task in list if exists
      const index = tasks.value.findIndex(t => t.id === taskId)
      if (index !== -1) {
        tasks.value[index] = task
      }

      return task
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'ไม่สามารถโหลดข้อมูลงานได้'
      console.error('Error fetching task:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function fetchStats(): Promise<void> {
    try {
      error.value = null

      const data = await housekeepingApi.getStats()
      stats.value = data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'ไม่สามารถโหลดสถิติได้'
      console.error('Error fetching stats:', err)
      throw err
    }
  }

  async function startTask(taskId: number): Promise<void> {
    try {
      isLoading.value = true
      error.value = null

      const updatedTask = await housekeepingApi.startTask(taskId)

      // Update task in list
      const index = tasks.value.findIndex(t => t.id === taskId)
      if (index !== -1) {
        tasks.value[index] = updatedTask
      }

      currentTask.value = updatedTask

      // Refresh stats
      await fetchStats()
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'ไม่สามารถเริ่มงานได้'
      console.error('Error starting task:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function completeTask(taskId: number, notes?: string): Promise<void> {
    try {
      isLoading.value = true
      error.value = null

      const updatedTask = await housekeepingApi.completeTask(taskId, { notes })

      // Update task in list
      const index = tasks.value.findIndex(t => t.id === taskId)
      if (index !== -1) {
        tasks.value[index] = updatedTask
      }

      currentTask.value = updatedTask

      // Refresh stats
      await fetchStats()
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'ไม่สามารถทำงานให้เสร็จได้'
      console.error('Error completing task:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function assignTask(taskId: number, userId: number): Promise<void> {
    try {
      isLoading.value = true
      error.value = null

      const updatedTask = await housekeepingApi.updateTask(taskId, { assigned_to: userId })

      // Update task in list
      const index = tasks.value.findIndex(t => t.id === taskId)
      if (index !== -1) {
        tasks.value[index] = updatedTask
      }

      currentTask.value = updatedTask
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'ไม่สามารถมอบหมายงานได้'
      console.error('Error assigning task:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function updateTaskPriority(taskId: number, priority: HousekeepingTaskPriority): Promise<void> {
    try {
      isLoading.value = true
      error.value = null

      const updatedTask = await housekeepingApi.updateTask(taskId, { priority })

      // Update task in list
      const index = tasks.value.findIndex(t => t.id === taskId)
      if (index !== -1) {
        tasks.value[index] = updatedTask
      }

      currentTask.value = updatedTask
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'ไม่สามารถเปลี่ยนลำดับความสำคัญได้'
      console.error('Error updating task priority:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Handle housekeeping task events from WebSocket
   */
  function handleTaskEvent(eventType: string, data: any): void {
    console.log('Housekeeping task event:', eventType, data)

    if (eventType === 'housekeeping_task_created') {
      // Refresh task list when new task is created
      fetchTasks()
      fetchStats()
    } else if (eventType === 'housekeeping_task_updated' ||
               eventType === 'housekeeping_task_started' ||
               eventType === 'housekeeping_task_completed') {
      // Refresh specific task
      if (data.task_id) {
        fetchTaskById(data.task_id).catch(() => {
          // If fetch fails, just refresh the whole list
          fetchTasks()
        })
      }
      fetchStats()
    }
  }

  /**
   * Set filters
   */
  function setFilters(newFilters: HousekeepingTaskFilters): void {
    filters.value = newFilters
  }

  /**
   * Clear filters
   */
  function clearFilters(): void {
    filters.value = {}
  }

  /**
   * Clear error
   */
  function clearError(): void {
    error.value = null
  }

  /**
   * Refresh all data
   */
  async function refresh(): Promise<void> {
    await Promise.all([
      fetchTasks(),
      fetchStats()
    ])
  }

  return {
    // State
    tasks,
    stats,
    currentTask,
    isLoading,
    error,
    total,
    filters,

    // Computed
    pendingTasks,
    inProgressTasks,
    completedTasks,
    urgentTasks,
    highPriorityTasks,

    // Actions
    fetchTasks,
    fetchTaskById,
    fetchStats,
    startTask,
    completeTask,
    assignTask,
    updateTaskPriority,
    handleTaskEvent,
    setFilters,
    clearFilters,
    clearError,
    refresh
  }
})
