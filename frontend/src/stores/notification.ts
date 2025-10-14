/**
 * Notification Store (Phase 3)
 * State management for notifications
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { notificationsApi } from '@/api/notifications'
import type {
  Notification,
  NotificationCreate
} from '@/types/notification'
import type { NotificationEventData } from '@/types/websocket'

export const useNotificationStore = defineStore('notification', () => {
  // State
  const notifications = ref<Notification[]>([])
  const unreadCount = ref(0)
  const total = ref(0)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Pagination
  const currentPage = ref(1)
  const itemsPerPage = ref(20)

  // Computed
  const unreadNotifications = computed(() =>
    notifications.value.filter(n => !n.is_read)
  )

  const readNotifications = computed(() =>
    notifications.value.filter(n => n.is_read)
  )

  const hasUnread = computed(() => unreadCount.value > 0)

  const offset = computed(() => (currentPage.value - 1) * itemsPerPage.value)

  const totalPages = computed(() => Math.ceil(total.value / itemsPerPage.value))

  // Actions
  async function fetchNotifications(unreadOnly = false): Promise<void> {
    try {
      isLoading.value = true
      error.value = null

      const response = await notificationsApi.getNotifications({
        limit: itemsPerPage.value,
        offset: offset.value,
        unread_only: unreadOnly
      })

      notifications.value = response.data
      total.value = response.total
      unreadCount.value = response.unread_count
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'ไม่สามารถโหลดการแจ้งเตือนได้'
      console.error('Error fetching notifications:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function fetchUnreadCount(): Promise<void> {
    try {
      error.value = null
      const count = await notificationsApi.getUnreadCount()
      unreadCount.value = count
    } catch (err: any) {
      console.error('Error fetching unread count:', err)
      // Don't throw error for count fetch failure
    }
  }

  async function markAsRead(notificationId: number): Promise<void> {
    try {
      error.value = null

      const updated = await notificationsApi.markAsRead(notificationId)

      // Update in local state
      const index = notifications.value.findIndex(n => n.id === notificationId)
      if (index !== -1) {
        notifications.value[index] = updated
        if (updated.is_read) {
          unreadCount.value = Math.max(0, unreadCount.value - 1)
        }
      }
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'ไม่สามารถทำเครื่องหมายว่าอ่านแล้ว'
      console.error('Error marking notification as read:', err)
      throw err
    }
  }

  async function markAllAsRead(): Promise<void> {
    try {
      isLoading.value = true
      error.value = null

      const response = await notificationsApi.markAllAsRead()

      // Update all notifications in local state
      notifications.value = notifications.value.map(n => ({
        ...n,
        is_read: true,
        read_at: new Date().toISOString()
      }))

      unreadCount.value = 0

      return response
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'ไม่สามารถทำเครื่องหมายทั้งหมดว่าอ่านแล้ว'
      console.error('Error marking all notifications as read:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function createNotification(data: NotificationCreate): Promise<Notification> {
    try {
      error.value = null

      const notification = await notificationsApi.createNotification(data)

      // Add to local state
      notifications.value.unshift(notification)
      total.value++

      return notification
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'ไม่สามารถสร้างการแจ้งเตือนได้'
      console.error('Error creating notification:', err)
      throw err
    }
  }

  /**
   * Handle new notification from WebSocket
   */
  function handleNewNotification(data: NotificationEventData): void {
    // Create notification object
    const notification: Notification = {
      id: Date.now(), // Temporary ID, will be replaced when fetched
      notification_type: data.notification_type as any,
      target_role: data.target_role as any,
      title: data.title,
      message: data.message,
      room_id: data.room_id || null,
      related_booking_id: null,
      related_check_in_id: null,
      is_read: false,
      read_at: null,
      telegram_sent: false,
      telegram_message_id: null,
      created_at: new Date().toISOString()
    }

    // Add to beginning of list
    notifications.value.unshift(notification)
    unreadCount.value++
    total.value++

    // Show browser notification if permitted
    showBrowserNotification(data.title, data.message)

    // Optionally refetch to get real notification with correct ID
    // This can be done in background
    setTimeout(() => {
      fetchUnreadCount()
    }, 1000)
  }

  /**
   * Show browser notification
   */
  function showBrowserNotification(title: string, message: string): void {
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification(title, {
        body: message,
        icon: '/favicon.ico',
        badge: '/favicon.ico'
      })
    }
  }

  /**
   * Request browser notification permission
   */
  async function requestNotificationPermission(): Promise<boolean> {
    if ('Notification' in window) {
      const permission = await Notification.requestPermission()
      return permission === 'granted'
    }
    return false
  }

  /**
   * Go to next page
   */
  function nextPage(): void {
    if (currentPage.value < totalPages.value) {
      currentPage.value++
    }
  }

  /**
   * Go to previous page
   */
  function prevPage(): void {
    if (currentPage.value > 1) {
      currentPage.value--
    }
  }

  /**
   * Go to specific page
   */
  function goToPage(page: number): void {
    if (page >= 1 && page <= totalPages.value) {
      currentPage.value = page
    }
  }

  /**
   * Clear error message
   */
  function clearError(): void {
    error.value = null
  }

  /**
   * Refresh notifications
   */
  async function refresh(): Promise<void> {
    await fetchNotifications()
    await fetchUnreadCount()
  }

  return {
    // State
    notifications,
    unreadCount,
    total,
    isLoading,
    error,
    currentPage,
    itemsPerPage,

    // Computed
    unreadNotifications,
    readNotifications,
    hasUnread,
    offset,
    totalPages,

    // Actions
    fetchNotifications,
    fetchUnreadCount,
    markAsRead,
    markAllAsRead,
    createNotification,
    handleNewNotification,
    showBrowserNotification,
    requestNotificationPermission,
    nextPage,
    prevPage,
    goToPage,
    clearError,
    refresh
  }
})
