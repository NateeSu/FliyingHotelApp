<template>
  <div class="home-container">
    <n-space vertical :size="32">
      <div class="welcome-header">
        <n-h1>ยินดีต้อนรับ {{ authStore.user?.full_name }}</n-h1>
        <n-text depth="3">{{ getRoleText(authStore.user?.role) }}</n-text>
      </div>

      <n-grid :cols="1" :x-gap="24" :y-gap="24" responsive="screen">
        <n-gi :span="1">
          <n-card title="ข้อมูลผู้ใช้" :bordered="false" class="info-card">
            <n-descriptions :column="1" :label-style="{ width: '140px' }">
              <n-descriptions-item label="ชื่อผู้ใช้">
                {{ authStore.user?.username }}
              </n-descriptions-item>
              <n-descriptions-item label="ชื่อ-นามสกุล">
                {{ authStore.user?.full_name }}
              </n-descriptions-item>
              <n-descriptions-item label="บทบาท">
                <n-tag :type="getRoleColor(authStore.user?.role)" size="medium">
                  {{ getRoleText(authStore.user?.role) }}
                </n-tag>
              </n-descriptions-item>
              <n-descriptions-item label="สถานะ">
                <n-tag :type="authStore.user?.is_active ? 'success' : 'error'" size="medium">
                  {{ authStore.user?.is_active ? 'ใช้งาน' : 'ระงับ' }}
                </n-tag>
              </n-descriptions-item>
            </n-descriptions>
          </n-card>
        </n-gi>

        <n-gi :span="1">
          <n-card title="สถานะระบบ" :bordered="false" class="info-card">
            <n-space vertical :size="16">
              <n-alert type="success" title="ระบบทำงานปกติ">
                Frontend เชื่อมต่อสำเร็จ
              </n-alert>
              <n-button type="primary" @click="checkBackend" :loading="checking" size="large" block>
                ตรวจสอบการเชื่อมต่อ Backend
              </n-button>
              <n-alert v-if="backendStatus" :type="backendStatus.type">
                {{ backendStatus.message }}
              </n-alert>
            </n-space>
          </n-card>
        </n-gi>

        <n-gi v-if="authStore.isAdmin" :span="1">
          <n-card title="เมนูจัดการ" :bordered="false" class="info-card">
            <n-space :size="16">
              <n-button type="primary" @click="$router.push('/users')" size="large">
                <template #icon>
                  <n-icon>
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                      <path fill="currentColor" d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/>
                    </svg>
                  </n-icon>
                </template>
                จัดการผู้ใช้
              </n-button>
            </n-space>
          </n-card>
        </n-gi>
      </n-grid>
    </n-space>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import axios from '@/api/axios'

const authStore = useAuthStore()
const backendStatus = ref<{ type: 'success' | 'error', message: string } | null>(null)
const checking = ref(false)

const checkBackend = async () => {
  checking.value = true
  try {
    const response = await axios.get('/health')
    backendStatus.value = {
      type: 'success',
      message: `✓ Backend เชื่อมต่อสำเร็จ - สถานะ: ${response.data.status}`
    }
  } catch (error) {
    backendStatus.value = {
      type: 'error',
      message: '✗ ไม่สามารถเชื่อมต่อ Backend ได้'
    }
  } finally {
    checking.value = false
  }
}

function getRoleText(role?: string): string {
  const roleMap: Record<string, string> = {
    ADMIN: 'ผู้ดูแลระบบ',
    admin: 'ผู้ดูแลระบบ',
    RECEPTION: 'แผนกต้อนรับ',
    reception: 'แผนกต้อนรับ',
    HOUSEKEEPING: 'แผนกแม่บ้าน',
    housekeeping: 'แผนกแม่บ้าน',
    MAINTENANCE: 'แผนกซ่อมบำรุง',
    maintenance: 'แผนกซ่อมบำรุง'
  }
  return roleMap[role || ''] || 'ไม่ทราบ'
}

function getRoleColor(role?: string): 'success' | 'info' | 'warning' | 'error' {
  const roleKey = role?.toUpperCase()
  const colorMap: Record<string, 'success' | 'info' | 'warning' | 'error'> = {
    ADMIN: 'error',
    RECEPTION: 'info',
    HOUSEKEEPING: 'success',
    MAINTENANCE: 'warning'
  }
  return colorMap[roleKey || ''] || 'info'
}
</script>

<style scoped>
.home-container {
  padding: 32px;
  max-width: 1400px;
  margin: 0 auto;
}

.welcome-header {
  text-align: center;
  padding: 48px 32px;
  background: linear-gradient(135deg, #3338A0 0%, #2a2d80 100%);
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(51, 56, 160, 0.3);
  margin-bottom: 8px;
}

.welcome-header h1 {
  margin-bottom: 12px;
  color: #FCC61D !important;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  font-size: 38px !important;
  line-height: 1.3;
}

.welcome-header :deep(.n-text) {
  color: #C59560 !important;
  font-size: 20px;
  font-weight: 500;
  line-height: 1.5;
}

.info-card {
  height: 100%;
}

:deep(.n-card) {
  border: 2px solid #3338A0;
  border-radius: 16px;
  box-shadow: 0 4px 16px rgba(51, 56, 160, 0.15);
  transition: all 0.3s ease;
}

:deep(.n-card:hover) {
  box-shadow: 0 8px 28px rgba(51, 56, 160, 0.25);
  transform: translateY(-4px);
}

:deep(.n-card .n-card-header) {
  background: linear-gradient(135deg, #3338A0 0%, #2a2d80 100%);
  color: #FCC61D !important;
  font-weight: 700;
  font-size: 20px;
  padding: 20px 28px;
  border-radius: 14px 14px 0 0;
}

:deep(.n-card .n-card-header .n-card-header__main) {
  color: #FCC61D !important;
}

:deep(.n-card .n-card-header__extra) {
  color: #FCC61D !important;
}

:deep(.n-card .n-card__content) {
  color: #3338A0;
  padding: 28px;
}

:deep(.n-descriptions) {
  margin-top: 4px;
}

:deep(.n-descriptions-item) {
  padding: 16px 0;
}

:deep(.n-descriptions-item:not(:last-child)) {
  border-bottom: 1px solid rgba(51, 56, 160, 0.1);
}

:deep(.n-descriptions-item-label) {
  color: #3338A0 !important;
  font-weight: 600;
  font-size: 15px;
  padding-right: 24px;
}

:deep(.n-descriptions-item-content) {
  color: #3338A0 !important;
  font-weight: 500;
  font-size: 15px;
}

:deep(.n-alert) {
  padding: 16px 20px;
  border-radius: 12px;
}

:deep(.n-alert__icon) {
  color: #C59560 !important;
  margin-right: 12px;
}

:deep(.n-alert .n-alert__content) {
  color: #3338A0 !important;
}

:deep(.n-button) {
  padding: 0 24px;
  height: 44px;
  font-size: 16px;
}

:deep(.n-tag) {
  font-weight: 600;
  padding: 8px 16px;
  font-size: 14px;
  border-radius: 8px;
}

@media (max-width: 768px) {
  .home-container {
    padding: 20px;
  }

  .welcome-header {
    padding: 32px 20px;
  }

  .welcome-header h1 {
    font-size: 28px !important;
  }

  .welcome-header :deep(.n-text) {
    font-size: 16px;
  }

  :deep(.n-card .n-card__content) {
    padding: 20px;
  }
}
</style>
