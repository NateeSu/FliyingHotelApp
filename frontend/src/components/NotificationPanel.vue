<template>
  <div class="notification-panel">
    <!-- Header -->
    <div class="panel-header">
      <div class="title-section">
        <h3 class="title">การแจ้งเตือน</h3>
        <span v-if="hasUnread" class="unread-badge">{{ unreadCount }}</span>
      </div>

      <div class="actions">
        <button
          v-if="hasUnread"
          class="btn-mark-all"
          @click="handleMarkAllRead"
          :disabled="isLoading"
        >
          อ่านทั้งหมด
        </button>
        <button class="btn-refresh" @click="handleRefresh" :disabled="isLoading">
          <span class="icon">🔄</span>
        </button>
      </div>
    </div>

    <!-- Filter Tabs -->
    <div class="filter-tabs">
      <button
        class="tab"
        :class="{ active: showUnreadOnly === false }"
        @click="showUnreadOnly = false"
      >
        ทั้งหมด
      </button>
      <button
        class="tab"
        :class="{ active: showUnreadOnly === true }"
        @click="showUnreadOnly = true"
      >
        ยังไม่อ่าน
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading && notifications.length === 0" class="loading-state">
      <div class="spinner"></div>
      <p>กำลังโหลด...</p>
    </div>

    <!-- Empty State -->
    <div
      v-else-if="!isLoading && notifications.length === 0"
      class="empty-state"
    >
      <span class="icon">🔔</span>
      <p>{{ showUnreadOnly ? 'ไม่มีการแจ้งเตือนที่ยังไม่อ่าน' : 'ไม่มีการแจ้งเตือน' }}</p>
    </div>

    <!-- Notification List -->
    <div v-else class="notification-list">
      <div
        v-for="notification in displayedNotifications"
        :key="notification.id"
        class="notification-item"
        :class="{ unread: !notification.is_read }"
        @click="handleNotificationClick(notification)"
      >
        <!-- Icon based on type -->
        <div class="notification-icon" :class="`type-${notification.notification_type}`">
          {{ getNotificationIcon(notification.notification_type) }}
        </div>

        <!-- Content -->
        <div class="notification-content">
          <div class="notification-title">{{ notification.title }}</div>
          <div class="notification-message">{{ notification.message }}</div>
          <div class="notification-time">{{ formatTime(notification.created_at) }}</div>
        </div>

        <!-- Unread Indicator -->
        <div v-if="!notification.is_read" class="unread-indicator"></div>
      </div>
    </div>

    <!-- Load More Button -->
    <div v-if="hasMore && !isLoading" class="load-more-section">
      <button class="btn-load-more" @click="handleLoadMore">
        โหลดเพิ่มเติม
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useNotificationStore } from '@/stores/notification'
import { storeToRefs } from 'pinia'
import type { Notification } from '@/types/notification'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import 'dayjs/locale/th'

dayjs.extend(relativeTime)
dayjs.locale('th')

// Store
const notificationStore = useNotificationStore()
const {
  notifications,
  unreadCount,
  total,
  isLoading,
  currentPage,
  totalPages
} = storeToRefs(notificationStore)

// Local State
const showUnreadOnly = ref(false)

// Computed
const hasUnread = computed(() => unreadCount.value > 0)

const displayedNotifications = computed(() => {
  if (showUnreadOnly.value) {
    return notificationStore.unreadNotifications
  }
  return notifications.value
})

const hasMore = computed(() => currentPage.value < totalPages.value)

// Methods
async function handleRefresh(): Promise<void> {
  try {
    await notificationStore.refresh()
  } catch (error) {
    console.error('Error refreshing notifications:', error)
  }
}

async function handleMarkAllRead(): Promise<void> {
  try {
    await notificationStore.markAllAsRead()
  } catch (error) {
    console.error('Error marking all as read:', error)
  }
}

async function handleNotificationClick(notification: Notification): Promise<void> {
  if (!notification.is_read) {
    try {
      await notificationStore.markAsRead(notification.id)
    } catch (error) {
      console.error('Error marking notification as read:', error)
    }
  }

  // Emit event for parent to handle navigation
  emit('notificationClick', notification)
}

async function handleLoadMore(): Promise<void> {
  notificationStore.nextPage()
  await notificationStore.fetchNotifications(showUnreadOnly.value)
}

function getNotificationIcon(type: string): string {
  const iconMap: Record<string, string> = {
    room_status_change: '🏠',
    overtime_alert: '⚠️',
    booking_reminder: '📅',
    housekeeping_task: '🧹',
    maintenance_request: '🔧',
    check_in: '✅',
    check_out: '👋',
    system_alert: '🔔'
  }
  return iconMap[type] || '🔔'
}

function formatTime(time: string): string {
  return dayjs(time).fromNow()
}

// Emits
const emit = defineEmits<{
  notificationClick: [notification: Notification]
}>()

// Watch for filter changes
watch(showUnreadOnly, async (newValue) => {
  notificationStore.currentPage = 1
  await notificationStore.fetchNotifications(newValue)
})

// Lifecycle
onMounted(async () => {
  await notificationStore.fetchNotifications()
})
</script>

<style scoped>
.notification-panel {
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  max-height: 600px;
}

/* Header */
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e0e0e0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.title-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.title {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}

.unread-badge {
  background: rgba(255, 255, 255, 0.3);
  color: white;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.actions {
  display: flex;
  gap: 8px;
}

.btn-mark-all,
.btn-refresh {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn-mark-all:hover,
.btn-refresh:hover {
  background: rgba(255, 255, 255, 0.3);
}

.btn-mark-all:disabled,
.btn-refresh:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-refresh {
  padding: 8px 12px;
}

.btn-refresh .icon {
  font-size: 16px;
}

/* Filter Tabs */
.filter-tabs {
  display: flex;
  padding: 12px 20px;
  gap: 8px;
  border-bottom: 1px solid #e0e0e0;
  background: #f5f5f5;
}

.tab {
  padding: 8px 16px;
  border: none;
  background: transparent;
  color: #666;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.tab.active {
  background: white;
  color: #667eea;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* Loading State */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: #666;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #999;
}

.empty-state .icon {
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.empty-state p {
  font-size: 14px;
  margin: 0;
}

/* Notification List */
.notification-list {
  flex: 1;
  overflow-y: auto;
}

.notification-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 16px 20px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.notification-item:hover {
  background: #f9f9f9;
}

.notification-item.unread {
  background: #f0f4ff;
}

.notification-item.unread:hover {
  background: #e6edff;
}

.notification-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  font-size: 20px;
  flex-shrink: 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-title {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
}

.notification-message {
  font-size: 13px;
  color: #666;
  margin-bottom: 6px;
  line-height: 1.4;
}

.notification-time {
  font-size: 12px;
  color: #999;
}

.unread-indicator {
  width: 8px;
  height: 8px;
  background: #667eea;
  border-radius: 50%;
  flex-shrink: 0;
  margin-top: 6px;
}

/* Load More Section */
.load-more-section {
  padding: 16px 20px;
  border-top: 1px solid #e0e0e0;
  text-align: center;
  background: #f9f9f9;
}

.btn-load-more {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 10px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn-load-more:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

/* Responsive */
@media (max-width: 768px) {
  .notification-panel {
    max-height: 500px;
  }

  .panel-header {
    padding: 16px;
  }

  .title {
    font-size: 16px;
  }

  .btn-mark-all {
    font-size: 12px;
    padding: 6px 12px;
  }

  .notification-item {
    padding: 12px 16px;
  }

  .notification-icon {
    width: 36px;
    height: 36px;
    font-size: 18px;
  }
}
</style>
