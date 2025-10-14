<template>
  <n-layout has-sider>
    <!-- Desktop Sidebar -->
    <n-layout-sider
      v-if="!isMobile"
      bordered
      collapse-mode="width"
      :collapsed-width="64"
      :width="240"
      :collapsed="collapsed"
      show-trigger
      @collapse="collapsed = true"
      @expand="collapsed = false"
    >
      <div class="logo">
        <n-icon v-if="collapsed" size="32" color="#FCC61D">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
            <path fill="currentColor" d="M7 13c1.66 0 3-1.34 3-3S8.66 7 7 7s-3 1.34-3 3 1.34 3 3 3zm12-6h-6.18C12.4 5.84 11.3 5 10 5H7c-1.89 0-3.39 1.67-3 3.56C4.27 10.03 5.5 11 7 11v2H6c-1.1 0-2 .9-2 2v7h2v-2h12v2h2v-7c0-1.1-.9-2-2-2h-1V9c1.5 0 2.73-.97 3-2.44.39-1.89-1.11-3.56-3-3.56z"/>
          </svg>
        </n-icon>
        <span v-else class="logo-text">FlyingHotelApp</span>
      </div>

      <n-menu
        :collapsed="collapsed"
        :collapsed-width="64"
        :collapsed-icon-size="22"
        :options="menuOptions"
        :value="activeKey"
        @update:value="handleMenuSelect"
      />

      <div class="sidebar-footer">
        <n-button
          v-if="!collapsed"
          block
          type="error"
          @click="handleLogout"
        >
          ออกจากระบบ
        </n-button>
        <n-button
          v-else
          circle
          type="error"
          @click="handleLogout"
        >
          <template #icon>
            <n-icon>
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                <path fill="currentColor" d="M17 7l-1.41 1.41L18.17 11H8v2h10.17l-2.58 2.58L17 17l5-5zM4 5h8V3H4c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h8v-2H4V5z"/>
              </svg>
            </n-icon>
          </template>
        </n-button>
      </div>
    </n-layout-sider>

    <!-- Mobile Drawer -->
    <n-drawer
      v-if="isMobile"
      v-model:show="showMobileMenu"
      :width="240"
      placement="left"
    >
      <n-drawer-content title="FlyingHotelApp" :native-scrollbar="false">
        <n-menu
          :options="menuOptions"
          :value="activeKey"
          @update:value="handleMenuSelect"
        />
        <template #footer>
          <n-button
            block
            type="error"
            @click="handleLogout"
          >
            ออกจากระบบ
          </n-button>
        </template>
      </n-drawer-content>
    </n-drawer>

    <n-layout>
      <!-- Header -->
      <n-layout-header bordered style="height: 64px; padding: 0 20px; display: flex; align-items: center;">
        <n-button
          v-if="isMobile"
          text
          @click="showMobileMenu = true"
        >
          <template #icon>
            <n-icon size="24">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                <path fill="currentColor" d="M3 18h18v-2H3v2zm0-5h18v-2H3v2zm0-7v2h18V6H3z"/>
              </svg>
            </n-icon>
          </template>
        </n-button>

        <div style="flex: 1;"></div>

        <n-space align="center">
          <n-dropdown :options="userMenuOptions" @select="handleUserMenuSelect">
            <n-button text>
              <template #icon>
                <n-icon size="24">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                    <path fill="currentColor" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z"/>
                  </svg>
                </n-icon>
              </template>
              {{ authStore.user?.full_name }}
            </n-button>
          </n-dropdown>
        </n-space>
      </n-layout-header>

      <!-- Content -->
      <n-layout-content
        :native-scrollbar="false"
        style="min-height: calc(100vh - 64px);"
      >
        <router-view />
      </n-layout-content>
    </n-layout>
  </n-layout>
</template>

<script setup lang="ts">
import { ref, computed, h } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useMessage, NIcon } from 'naive-ui'
import type { MenuOption } from 'naive-ui'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const message = useMessage()

const collapsed = ref(false)
const showMobileMenu = ref(false)
const isMobile = ref(window.innerWidth < 768)

// Handle window resize
window.addEventListener('resize', () => {
  isMobile.value = window.innerWidth < 768
})

// Menu options
const menuOptions = computed<MenuOption[]>(() => {
  const options: MenuOption[] = [
    {
      label: 'หน้าแรก',
      key: '/',
      icon: renderIcon('M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z')
    }
  ]

  if (authStore.isAdmin) {
    options.push({
      label: 'จัดการผู้ใช้',
      key: '/users',
      icon: renderIcon('M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z')
    })
  }

  return options
})

// User menu options
const userMenuOptions = [
  {
    label: 'โปรไฟล์',
    key: 'profile'
  },
  {
    label: 'ออกจากระบบ',
    key: 'logout'
  }
]

// Active menu key
const activeKey = computed(() => route.path)

// Handle menu select
function handleMenuSelect(key: string) {
  router.push(key)
  if (isMobile.value) {
    showMobileMenu.value = false
  }
}

// Handle user menu select
function handleUserMenuSelect(key: string) {
  if (key === 'logout') {
    handleLogout()
  }
}

// Handle logout
async function handleLogout() {
  try {
    await authStore.logout()
    message.success('ออกจากระบบสำเร็จ')
    router.push('/login')
  } catch (error) {
    message.error('เกิดข้อผิดพลาดในการออกจากระบบ')
  }
}

// Render icon helper
function renderIcon(path: string) {
  return () => h(NIcon, null, {
    default: () => h('svg', {
      xmlns: 'http://www.w3.org/2000/svg',
      viewBox: '0 0 24 24'
    }, [
      h('path', {
        fill: 'currentColor',
        d: path
      })
    ])
  })
}
</script>

<style scoped>
.logo {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 700;
  background: linear-gradient(135deg, #3338A0 0%, #1f2260 100%);
  color: #FCC61D;
  border-bottom: 3px solid #FCC61D;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.logo-text {
  background: linear-gradient(135deg, #FCC61D 0%, #C59560 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.sidebar-footer {
  position: absolute;
  bottom: 20px;
  left: 16px;
  right: 16px;
}

:deep(.n-layout-sider) {
  position: relative;
  background: #F7F7F7 !important;
  border-right: 2px solid #3338A0 !important;
}

:deep(.n-layout-sider .n-menu) {
  background: transparent !important;
}

:deep(.n-layout-sider .n-menu .n-menu-item) {
  margin: 4px 8px;
  border-radius: 8px;
}

:deep(.n-layout-sider .n-menu .n-menu-item.n-menu-item--selected) {
  background: linear-gradient(135deg, #3338A0 0%, #2a2d80 100%) !important;
  color: #FCC61D !important;
  font-weight: 600;
}

:deep(.n-layout-sider .n-menu .n-menu-item.n-menu-item--selected .n-menu-item-content) {
  color: #FCC61D !important;
}

:deep(.n-layout-sider .n-menu .n-menu-item.n-menu-item--selected .n-menu-item-content__icon) {
  color: #FCC61D !important;
}

:deep(.n-layout-sider .n-menu .n-menu-item .n-menu-item-content) {
  color: #3338A0 !important;
  font-weight: 500;
}

:deep(.n-layout-sider .n-menu .n-menu-item:hover) {
  background: rgba(51, 56, 160, 0.1) !important;
}

:deep(.n-layout-header) {
  background: linear-gradient(90deg, #3338A0 0%, #2a2d80 100%) !important;
  color: #F7F7F7 !important;
  border-bottom: 3px solid #FCC61D !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

:deep(.n-layout-header .n-button) {
  color: #FCC61D !important;
  font-weight: 600;
}

:deep(.n-layout-header .n-button:hover) {
  color: #F7F7F7 !important;
}

:deep(.n-layout-header .n-button .n-button__content) {
  color: #FCC61D !important;
}

:deep(.n-dropdown-menu) {
  background: #F7F7F7 !important;
}

:deep(.n-dropdown-option) {
  color: #3338A0 !important;
}

:deep(.n-dropdown-option:hover) {
  background: rgba(51, 56, 160, 0.1) !important;
}

:deep(.n-layout-content) {
  background: #F7F7F7 !important;
}

/* Drawer styles for mobile */
:deep(.n-drawer) {
  background: #F7F7F7 !important;
}

:deep(.n-drawer .n-drawer-header) {
  background: linear-gradient(135deg, #3338A0 0%, #2a2d80 100%);
  color: #FCC61D !important;
  font-weight: 700;
  border-bottom: 3px solid #FCC61D;
}

:deep(.n-drawer .n-drawer-header__main) {
  color: #FCC61D !important;
}

:deep(.n-drawer .n-drawer-body-content-wrapper) {
  background: #F7F7F7 !important;
}

:deep(.n-drawer .n-menu) {
  background: transparent !important;
}

:deep(.n-drawer .n-menu .n-menu-item) {
  color: #3338A0 !important;
}

:deep(.n-drawer .n-menu .n-menu-item.n-menu-item--selected) {
  background: linear-gradient(135deg, #3338A0 0%, #2a2d80 100%) !important;
  color: #FCC61D !important;
}

:deep(.n-drawer .n-menu .n-menu-item.n-menu-item--selected .n-menu-item-content) {
  color: #FCC61D !important;
}

/* Message and Notification */
:deep(.n-message .n-message__icon) {
  color: #C59560 !important;
}

:deep(.n-message .n-message__content) {
  color: #3338A0 !important;
  font-weight: 600;
}

:deep(.n-notification .n-notification-main__header) {
  color: #3338A0 !important;
  font-weight: 700;
}

:deep(.n-notification .n-notification-main__content) {
  color: #3338A0 !important;
}
</style>
