<template>
  <div class="breaker-stats-card" :class="{ offline: !isOnline }">
    <div class="card-header">
      <div class="header-left">
        <span class="icon">⚡</span>
        <h3 class="title">Smart Breakers</h3>
      </div>
      <div class="connection-badge" :class="{ connected: isOnline }">
        <span class="dot"></span>
        <span class="text">{{ isOnline ? 'เชื่อมต่อ' : 'ออฟไลน์' }}</span>
      </div>
    </div>

    <div v-if="isLoading" class="loading-state">
      <div class="spinner-small"></div>
      <span>กำลังโหลด...</span>
    </div>

    <div v-else-if="!isConfigured" class="not-configured">
      <span class="icon-large">🔌</span>
      <p class="message">ยังไม่ได้ตั้งค่า Home Assistant</p>
      <router-link to="/settings" class="btn-setup">ตั้งค่าเลย</router-link>
    </div>

    <div v-else class="stats-content">
      <div class="stat-row">
        <div class="stat-item">
          <div class="stat-label">ทั้งหมด</div>
          <div class="stat-value total">{{ statistics?.total_breakers || 0 }}</div>
        </div>
        <div class="stat-item">
          <div class="stat-label">พร้อมใช้งาน</div>
          <div class="stat-value online">{{ statistics?.online_breakers || 0 }}</div>
        </div>
      </div>

      <div class="stat-row">
        <div class="stat-item">
          <div class="stat-label">⚡ เปิดอยู่</div>
          <div class="stat-value on">{{ statistics?.breakers_on || 0 }}</div>
        </div>
        <div class="stat-item">
          <div class="stat-label">⚫ ปิดอยู่</div>
          <div class="stat-value off">{{ statistics?.breakers_off || 0 }}</div>
        </div>
      </div>

      <div v-if="statistics && statistics.recent_errors > 0" class="error-alert">
        <span class="icon">⚠️</span>
        <span class="text">มี {{ statistics.recent_errors }} ข้อผิดพลาด</span>
      </div>

      <div class="card-footer">
        <router-link to="/breakers" class="btn-view-details">
          ดูรายละเอียด
          <span class="arrow">→</span>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useHomeAssistantStore } from '@/stores/homeAssistant'
import { useBreakersStore } from '@/stores/breakers'
import { storeToRefs } from 'pinia'

// Stores
const haStore = useHomeAssistantStore()
const breakersStore = useBreakersStore()

const { status: haStatus } = storeToRefs(haStore)
const { statistics } = storeToRefs(breakersStore)

// Local state
const isLoading = ref(false)

// Computed
const isConfigured = computed(() => haStatus.value?.is_configured || false)
const isOnline = computed(() => haStatus.value?.is_online || false)

// Methods
const loadData = async () => {
  if (!isConfigured.value) return

  isLoading.value = true
  try {
    await Promise.all([
      haStore.fetchStatus(),
      breakersStore.fetchStatistics()
    ])
  } catch (error) {
    console.error('Error loading breaker stats:', error)
  } finally {
    isLoading.value = false
  }
}

// Auto refresh every 30 seconds
let refreshInterval: number | null = null

onMounted(async () => {
  await loadData()

  // Set up auto refresh
  refreshInterval = window.setInterval(() => {
    loadData()
  }, 30000) // 30 seconds
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})
</script>

<style scoped>
.breaker-stats-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  padding: 20px;
  color: white;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.breaker-stats-card::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
  pointer-events: none;
}

.breaker-stats-card.offline {
  background: linear-gradient(135deg, #718096 0%, #4a5568 100%);
  opacity: 0.8;
}

.breaker-stats-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  position: relative;
  z-index: 1;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-left .icon {
  font-size: 24px;
  filter: drop-shadow(0 2px 4px rgba(0,0,0,0.2));
}

.title {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  text-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.connection-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  font-size: 12px;
  backdrop-filter: blur(10px);
}

.connection-badge .dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #cbd5e0;
  animation: pulse 2s infinite;
}

.connection-badge.connected .dot {
  background: #48bb78;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.connection-badge .text {
  font-weight: 500;
}

/* Loading State */
.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 40px 0;
  position: relative;
  z-index: 1;
}

.spinner-small {
  width: 20px;
  height: 20px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Not Configured State */
.not-configured {
  text-align: center;
  padding: 20px 0;
  position: relative;
  z-index: 1;
}

.not-configured .icon-large {
  font-size: 48px;
  display: block;
  margin-bottom: 12px;
  opacity: 0.7;
}

.not-configured .message {
  margin: 0 0 16px 0;
  font-size: 14px;
  opacity: 0.9;
}

.btn-setup {
  display: inline-block;
  padding: 8px 20px;
  background: rgba(255, 255, 255, 0.25);
  border-radius: 20px;
  color: white;
  text-decoration: none;
  font-weight: 500;
  font-size: 14px;
  transition: all 0.2s ease;
  backdrop-filter: blur(10px);
}

.btn-setup:hover {
  background: rgba(255, 255, 255, 0.35);
  transform: translateY(-2px);
}

/* Stats Content */
.stats-content {
  position: relative;
  z-index: 1;
}

.stat-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 12px;
}

.stat-item {
  text-align: center;
  padding: 12px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  backdrop-filter: blur(10px);
}

.stat-label {
  font-size: 12px;
  opacity: 0.9;
  margin-bottom: 4px;
  font-weight: 500;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  text-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.stat-value.total {
  color: #fff;
}

.stat-value.online {
  color: #9ae6b4;
}

.stat-value.on {
  color: #fbbf24;
}

.stat-value.off {
  color: #e2e8f0;
}

/* Error Alert */
.error-alert {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 8px 12px;
  background: rgba(245, 101, 101, 0.3);
  border-radius: 8px;
  font-size: 13px;
  margin-bottom: 12px;
  backdrop-filter: blur(10px);
}

.error-alert .icon {
  font-size: 16px;
}

/* Card Footer */
.card-footer {
  margin-top: 12px;
}

.btn-view-details {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 10px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  color: white;
  text-decoration: none;
  font-weight: 600;
  font-size: 14px;
  transition: all 0.2s ease;
  backdrop-filter: blur(10px);
}

.btn-view-details:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateX(4px);
}

.btn-view-details .arrow {
  transition: transform 0.2s ease;
}

.btn-view-details:hover .arrow {
  transform: translateX(4px);
}

/* Responsive */
@media (max-width: 768px) {
  .breaker-stats-card {
    padding: 16px;
  }

  .title {
    font-size: 16px;
  }

  .stat-value {
    font-size: 20px;
  }

  .stat-row {
    gap: 8px;
  }

  .stat-item {
    padding: 10px;
  }
}
</style>
