<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Sidebar for Desktop -->
    <aside
      v-if="!isMobile"
      :class="[
        'fixed left-0 top-0 h-screen bg-white shadow-material-xl transition-all duration-300 z-40',
        collapsed ? 'w-20' : 'w-64'
      ]"
    >
      <!-- Logo -->
      <div class="h-16 flex items-center justify-center bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-600 relative overflow-hidden">
        <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-10 animate-shimmer"></div>
        <svg v-if="collapsed" class="h-10 w-10 text-white relative z-10" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
          <path d="M7 13c1.66 0 3-1.34 3-3S8.66 7 7 7s-3 1.34-3 3 1.34 3 3 3zm12-6h-6.18C12.4 5.84 11.3 5 10 5H7c-1.89 0-3.39 1.67-3 3.56C4.27 10.03 5.5 11 7 11v2H6c-1.1 0-2 .9-2 2v7h2v-2h12v2h2v-7c0-1.1-.9-2-2-2h-1V9c1.5 0 2.73-.97 3-2.44.39-1.89-1.11-3.56-3-3.56z"/>
        </svg>
        <span v-else class="text-xl font-bold text-white relative z-10">FlyingHotel</span>
      </div>

      <!-- Toggle Button -->
      <button
        @click="collapsed = !collapsed"
        class="absolute -right-3 top-20 w-6 h-6 bg-indigo-600 rounded-full flex items-center justify-center text-white shadow-lg hover:bg-indigo-700 transition-colors z-50"
      >
        <svg class="w-4 h-4" :class="{ 'rotate-180': collapsed }" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
          <path d="M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z"/>
        </svg>
      </button>

      <!-- Navigation Menu -->
      <nav class="mt-6 px-3 space-y-2 overflow-y-auto" style="max-height: calc(100vh - 180px);">
        <!-- Regular menu items -->
        <template v-for="item in menuItems" :key="item.label">
          <!-- Submenu Group -->
          <div v-if="item.children" class="relative">
            <!-- Submenu Header (Collapsible) -->
            <button
              @click="toggleSubmenu(item.label)"
              :class="[
                'w-full flex items-center px-4 py-3 rounded-xl transition-all duration-200 cursor-pointer group relative',
                'text-gray-700 hover:bg-gradient-to-r hover:from-indigo-50 hover:to-purple-50'
              ]"
            >
              <svg class="w-6 h-6 flex-shrink-0" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                <path :d="item.icon"/>
              </svg>
              <span v-if="!collapsed" class="ml-3 font-medium">{{ item.label }}</span>
              <svg
                v-if="!collapsed"
                class="ml-auto w-5 h-5 transition-transform duration-300"
                :class="{ 'rotate-180': expandedMenus.includes(item.label) }"
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
              >
                <path d="M19 14l-7 7m0 0l-7-7m7 7V3" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>

            <!-- Submenu Items -->
            <transition
              enter-active-class="transition-all duration-300 ease-out"
              leave-active-class="transition-all duration-300 ease-in"
              enter-from-class="opacity-0 max-h-0"
              enter-to-class="opacity-100 max-h-96"
              leave-from-class="opacity-100 max-h-96"
              leave-to-class="opacity-0 max-h-0"
            >
              <div v-if="expandedMenus.includes(item.label)" class="overflow-hidden">
                <router-link
                  v-for="subitem in item.children"
                  :key="subitem.path"
                  :to="subitem.path"
                  v-slot="{ isActive }"
                  custom
                >
                  <a
                    @click="navigateTo(subitem.path)"
                    :class="[
                      'flex items-center px-4 py-3 ml-4 rounded-lg transition-all duration-200 cursor-pointer group mt-1',
                      isActive
                        ? 'bg-gradient-to-r from-indigo-100 to-purple-100 text-indigo-700 border-l-4 border-indigo-600'
                        : 'text-gray-600 hover:bg-indigo-50 border-l-4 border-transparent'
                    ]"
                  >
                    <svg class="w-5 h-5 flex-shrink-0" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                      <path :d="subitem.icon"/>
                    </svg>
                    <span v-if="!collapsed" class="ml-3 font-medium text-sm">{{ subitem.label }}</span>
                    <div v-if="!collapsed && isActive" class="ml-auto">
                      <div class="w-2 h-2 bg-indigo-600 rounded-full animate-pulse"></div>
                    </div>
                  </a>
                </router-link>
              </div>
            </transition>
          </div>

          <!-- Regular menu item -->
          <router-link
            v-else
            :to="item.path"
            v-slot="{ isActive }"
            custom
          >
            <a
              @click="navigateTo(item.path)"
              :class="[
                'flex items-center px-4 py-3 rounded-xl transition-all duration-200 cursor-pointer group',
                isActive
                  ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-lg'
                  : 'text-gray-700 hover:bg-gradient-to-r hover:from-indigo-50 hover:to-purple-50'
              ]"
            >
              <svg class="w-6 h-6 flex-shrink-0" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                <path :d="item.icon"/>
              </svg>
              <span v-if="!collapsed" class="ml-3 font-medium">{{ item.label }}</span>
              <div v-if="!collapsed && isActive" class="ml-auto">
                <div class="w-2 h-2 bg-white rounded-full animate-pulse"></div>
              </div>
            </a>
          </router-link>
        </template>
      </nav>

      <!-- Logout Button -->
      <div class="absolute bottom-6 left-0 right-0 px-3">
        <button
          @click="handleLogout"
          :class="[
            'w-full flex items-center justify-center px-4 py-3 rounded-xl bg-gradient-to-r from-red-500 to-pink-600 text-white font-medium shadow-lg hover:from-red-600 hover:to-pink-700 transition-all duration-200 transform hover:-translate-y-0.5 hover:shadow-xl',
            collapsed ? 'px-0' : ''
          ]"
        >
          <svg class="w-6 h-6" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
            <path d="M17 7l-1.41 1.41L18.17 11H8v2h10.17l-2.58 2.58L17 17l5-5zM4 5h8V3H4c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h8v-2H4V5z"/>
          </svg>
          <span v-if="!collapsed" class="ml-3">ออกจากระบบ</span>
        </button>
      </div>
    </aside>

    <!-- Mobile Menu Button -->
    <button
      v-if="isMobile"
      @click="showMobileMenu = true"
      class="fixed top-4 left-4 z-50 w-12 h-12 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-full flex items-center justify-center text-white shadow-xl hover:shadow-2xl transition-all"
    >
      <svg class="w-6 h-6" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
        <path d="M3 18h18v-2H3v2zm0-5h18v-2H3v2zm0-7v2h18V6H3z"/>
      </svg>
    </button>

    <!-- Mobile Drawer -->
    <transition name="drawer">
      <div
        v-if="isMobile && showMobileMenu"
        class="fixed inset-0 z-50"
      >
        <!-- Backdrop -->
        <div
          class="absolute inset-0 bg-black bg-opacity-50 backdrop-blur-sm"
          @click="showMobileMenu = false"
        ></div>

        <!-- Drawer -->
        <div class="absolute left-0 top-0 bottom-0 w-80 bg-white shadow-2xl">
          <!-- Header -->
          <div class="h-16 flex items-center justify-between px-6 bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-600">
            <span class="text-xl font-bold text-white">FlyingHotel</span>
            <button
              @click="showMobileMenu = false"
              class="w-8 h-8 rounded-full bg-white bg-opacity-20 flex items-center justify-center text-white hover:bg-opacity-30 transition-all"
            >
              <svg class="w-5 h-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
              </svg>
            </button>
          </div>

          <!-- Menu -->
          <nav class="mt-4 px-4 space-y-2">
            <template v-for="item in menuItems" :key="item.label">
              <!-- Submenu (with children) -->
              <div v-if="item.children">
                <button
                  @click="toggleSubmenu(item.label)"
                  class="w-full flex items-center justify-between px-4 py-3 rounded-xl text-gray-700 hover:bg-gradient-to-r hover:from-indigo-50 hover:to-purple-50 transition-all duration-200 cursor-pointer"
                >
                  <div class="flex items-center">
                    <svg class="w-6 h-6" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                      <path :d="item.icon"/>
                    </svg>
                    <span class="ml-3 font-medium">{{ item.label }}</span>
                  </div>
                  <svg
                    class="w-5 h-5 transition-transform duration-200"
                    :class="{ 'rotate-180': expandedMenus.includes(item.label) }"
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 24 24"
                    fill="currentColor"
                  >
                    <path d="M7.41 8.59L12 13.17l4.59-4.58L18 10l-6 6-6-6 1.41-1.41z"/>
                  </svg>
                </button>

                <!-- Submenu items -->
                <transition
                  enter-active-class="transition-all duration-200 ease-out"
                  leave-active-class="transition-all duration-200 ease-in"
                  enter-from-class="opacity-0 max-h-0"
                  enter-to-class="opacity-100 max-h-96"
                  leave-from-class="opacity-100 max-h-96"
                  leave-to-class="opacity-0 max-h-0"
                >
                  <div v-if="expandedMenus.includes(item.label)" class="overflow-hidden">
                    <router-link
                      v-for="subitem in item.children"
                      :key="subitem.path"
                      :to="subitem.path!"
                      v-slot="{ isActive }"
                      custom
                    >
                      <a
                        @click="navigateTo(subitem.path!); showMobileMenu = false"
                        :class="[
                          'flex items-center px-4 py-3 ml-4 rounded-lg transition-all duration-200 cursor-pointer mt-1',
                          isActive
                            ? 'bg-gradient-to-r from-indigo-100 to-purple-100 text-indigo-700 border-l-4 border-indigo-600'
                            : 'text-gray-600 hover:bg-indigo-50 border-l-4 border-transparent'
                        ]"
                      >
                        <svg class="w-5 h-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                          <path :d="subitem.icon"/>
                        </svg>
                        <span class="ml-3 font-medium text-sm">{{ subitem.label }}</span>
                      </a>
                    </router-link>
                  </div>
                </transition>
              </div>

              <!-- Regular menu item -->
              <router-link
                v-else
                :to="item.path!"
                v-slot="{ isActive }"
                custom
              >
                <a
                  @click="navigateTo(item.path!); showMobileMenu = false"
                  :class="[
                    'flex items-center px-4 py-3 rounded-xl transition-all duration-200 cursor-pointer',
                    isActive
                      ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-lg'
                      : 'text-gray-700 hover:bg-gradient-to-r hover:from-indigo-50 hover:to-purple-50'
                  ]"
                >
                  <svg class="w-6 h-6" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                    <path :d="item.icon"/>
                  </svg>
                  <span class="ml-3 font-medium">{{ item.label }}</span>
                </a>
              </router-link>
            </template>
          </nav>

          <!-- Logout -->
          <div class="absolute bottom-6 left-4 right-4">
            <button
              @click="handleLogout"
              class="w-full flex items-center justify-center px-4 py-3 rounded-xl bg-gradient-to-r from-red-500 to-pink-600 text-white font-medium shadow-lg hover:from-red-600 hover:to-pink-700 transition-all"
            >
              <svg class="w-6 h-6" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                <path d="M17 7l-1.41 1.41L18.17 11H8v2h10.17l-2.58 2.58L17 17l5-5zM4 5h8V3H4c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h8v-2H4V5z"/>
              </svg>
              <span class="ml-3">ออกจากระบบ</span>
            </button>
          </div>
        </div>
      </div>
    </transition>

    <!-- Main Content -->
    <main
      :class="[
        'transition-all duration-300',
        isMobile ? 'ml-0' : (collapsed ? 'ml-20' : 'ml-64')
      ]"
    >
      <!-- Top Bar -->
      <header class="h-16 bg-white shadow-md flex items-center justify-between px-6 sticky top-0 z-30">
        <div class="flex items-center space-x-4">
          <h1 class="text-xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
            {{ currentPageTitle }}
          </h1>
        </div>

        <!-- User Menu -->
        <div class="relative">
          <button
            @click="showUserMenu = !showUserMenu"
            class="flex items-center space-x-3 px-4 py-2 rounded-xl hover:bg-gray-100 transition-all"
          >
            <div class="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white font-bold shadow-lg">
              {{ userInitials }}
            </div>
            <div class="text-left hidden sm:block">
              <div class="font-semibold text-gray-900">{{ authStore.user?.full_name }}</div>
              <div class="text-sm text-gray-500">{{ roleLabel }}</div>
            </div>
            <svg class="w-5 h-5 text-gray-400 transition-transform" :class="{ 'rotate-180': showUserMenu }" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
              <path d="M7.41 8.59L12 13.17l4.59-4.58L18 10l-6 6-6-6 1.41-1.41z"/>
            </svg>
          </button>

          <!-- Dropdown -->
          <transition name="dropdown">
            <div
              v-if="showUserMenu"
              v-click-outside="() => showUserMenu = false"
              class="absolute right-0 mt-2 w-56 bg-white rounded-xl shadow-2xl py-2 border border-gray-100 z-50"
              style="z-index: 9999;"
            >
              <div class="px-4 py-3 border-b border-gray-100">
                <div class="font-semibold text-gray-900">{{ authStore.user?.full_name }}</div>
                <div class="text-sm text-gray-500">{{ authStore.user?.username }}</div>
              </div>

              <button
                @click="openEditProfile"
                class="w-full text-left px-4 py-3 text-gray-700 hover:bg-indigo-50 transition-colors flex items-center space-x-2 border-b border-gray-100"
              >
                <svg class="w-5 h-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25z M20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/>
                </svg>
                <span class="font-medium">แก้ไขโปรไฟล์</span>
              </button>

              <button
                @click="openChangePassword"
                class="w-full text-left px-4 py-3 text-gray-700 hover:bg-indigo-50 transition-colors flex items-center space-x-2 border-b border-gray-100"
              >
                <svg class="w-5 h-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M18 8h-1V6c0-2.76-2.24-5-5-5s-5 2.24-5 5v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zM9 6c0-1.66 1.34-3 3-3s3 1.34 3 3v2H9V6zm9 14H6V10h12v10zm-6-3c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2z"/>
                </svg>
                <span class="font-medium">เปลี่ยนรหัสผ่าน</span>
              </button>

              <button
                @click="handleLogout"
                class="w-full text-left px-4 py-3 text-red-600 hover:bg-red-50 transition-colors flex items-center space-x-2"
              >
                <svg class="w-5 h-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M17 7l-1.41 1.41L18.17 11H8v2h10.17l-2.58 2.58L17 17l5-5zM4 5h8V3H4c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h8v-2H4V5z"/>
                </svg>
                <span class="font-medium">ออกจากระบบ</span>
              </button>
            </div>
          </transition>
        </div>
      </header>

      <!-- Page Content -->
      <div class="p-6">
        <router-view />
      </div>
    </main>

    <!-- Edit Profile Modal -->
    <div v-if="showEditProfileModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md mx-4 p-8">
        <h2 class="text-2xl font-bold text-gray-900 mb-6">แก้ไขโปรไฟล์</h2>

        <div class="space-y-4">
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-2">ชื่อ</label>
            <input
              v-model="editProfileForm.full_name"
              type="text"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="กรอกชื่อของคุณ"
            />
          </div>

          <div class="flex gap-3 pt-6">
            <button
              @click="showEditProfileModal = false"
              class="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors"
            >
              ยกเลิก
            </button>
            <button
              @click="saveProfileChanges"
              class="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 transition-colors"
            >
              บันทึก
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Change Password Modal -->
    <div v-if="showChangePasswordModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md mx-4 p-8">
        <h2 class="text-2xl font-bold text-gray-900 mb-6">เปลี่ยนรหัสผ่าน</h2>

        <div class="space-y-4">
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-2">รหัสผ่านปัจจุบัน</label>
            <input
              v-model="changePasswordForm.current_password"
              type="password"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="กรอกรหัสผ่านปัจจุบัน"
            />
          </div>

          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-2">รหัสผ่านใหม่</label>
            <input
              v-model="changePasswordForm.new_password"
              type="password"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="กรอกรหัสผ่านใหม่"
            />
          </div>

          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-2">ยืนยันรหัสผ่านใหม่</label>
            <input
              v-model="changePasswordForm.confirm_password"
              type="password"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="ยืนยันรหัสผ่านใหม่"
            />
          </div>

          <div class="flex gap-3 pt-6">
            <button
              @click="showChangePasswordModal = false"
              class="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors"
            >
              ยกเลิก
            </button>
            <button
              @click="changePassword"
              class="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 transition-colors"
            >
              เปลี่ยน
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useMessage } from 'naive-ui'
import { useAuthStore } from '@/stores/auth'
import axios from '@/api/axios'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const message = useMessage()

const collapsed = ref(false)
const showMobileMenu = ref(false)
const showUserMenu = ref(false)
const isMobile = ref(false)
const expandedMenus = ref<string[]>([])
const showEditProfileModal = ref(false)
const showChangePasswordModal = ref(false)
const editProfileForm = ref({
  full_name: authStore.user?.full_name || ''
})
const changePasswordForm = ref({
  current_password: '',
  new_password: '',
  confirm_password: ''
})

// Check mobile
const checkMobile = () => {
  isMobile.value = window.innerWidth < 768
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})

// Menu items
const menuItems = computed(() => {
  interface MenuItem {
    label: string
    path?: string
    icon: string
    children?: MenuItem[]
  }

  const items: MenuItem[] = []

  // Home page - for Admin only (Reception goes straight to Dashboard)
  if (authStore.isAdmin) {
    items.push({
      label: 'หน้าแรก',
      path: '/',
      icon: 'M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z'
    })
  }

  // Dashboard - for Admin and Reception
  if (authStore.isAdmin || authStore.hasRole(['RECEPTION'])) {
    items.push({
      label: 'แดชบอร์ด',
      path: '/dashboard',
      icon: 'M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z'
    })
  }

  // Booking System - for Admin and Reception (Phase 7)
  if (authStore.isAdmin || authStore.hasRole(['RECEPTION'])) {
    items.push({
      label: 'จองห้อง',
      path: '/bookings',
      icon: 'M19 4h-1V2h-2v2H8V2H6v2H5c-1.11 0-1.99.9-1.99 2L3 20c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 16H5V10h14v10zM9 14H7v-2h2v2zm4 0h-2v-2h2v2zm4 0h-2v-2h2v2zm-8 4H7v-2h2v2zm4 0h-2v-2h2v2zm4 0h-2v-2h2v2z'
    })
  }

  // Customer Management - for Admin and Reception (Phase 7)
  if (authStore.isAdmin || authStore.hasRole(['RECEPTION'])) {
    items.push({
      label: 'ข้อมูลลูกค้า',
      path: '/customers',
      icon: 'M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z'
    })
  }

  // Housekeeping - for Admin, Reception and Housekeeping
  if (authStore.isAdmin || authStore.hasRole(['HOUSEKEEPING', 'RECEPTION'])) {
    items.push({
      label: 'งานทำความสะอาด',
      path: '/housekeeping',
      icon: 'M7 13c1.66 0 3-1.34 3-3S8.66 7 7 7s-3 1.34-3 3 1.34 3 3 3zm12-6h-6.18C12.4 5.84 11.3 5 10 5H7c-1.89 0-3.39 1.67-3 3.56C4.27 10.03 5.5 11 7 11v2H6c-1.1 0-2 .9-2 2v7h2v-2h12v2h2v-7c0-1.1-.9-2-2-2h-1V9c1.5 0 2.73-.97 3-2.44.39-1.89-1.11-3.56-3-3.56z'
    })
  }

  // Maintenance - for Admin, Reception and Maintenance
  if (authStore.isAdmin || authStore.hasRole(['MAINTENANCE', 'RECEPTION'])) {
    items.push({
      label: 'งานซ่อมบำรุง',
      path: '/maintenance',
      icon: 'M22.7 19l-9.1-9.1c.9-2.3.4-5-1.5-6.9-2-2-5-2.4-7.4-1.3L9 6 6 9 1.6 4.7C.4 7.1.9 10.1 2.9 12.1c1.9 1.9 4.6 2.4 6.9 1.5l9.1 9.1c.4.4 1 .4 1.4 0l2.3-2.3c.5-.4.5-1.1.1-1.4z'
    })
  }

  // Reports - for Admin and Reception (Phase 8)
  if (authStore.isAdmin || authStore.hasRole(['RECEPTION'])) {
    items.push({
      label: 'รายงาน',
      path: '/reports',
      icon: 'M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z'
    })
  }

  // Admin-only items
  if (authStore.isAdmin) {
    // Room Management submenu
    const roomItems: MenuItem[] = [
      {
        label: 'ประเภทห้อง',
        path: '/room-types',
        icon: 'M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z'
      },
      {
        label: 'จัดการห้อง',
        path: '/rooms',
        icon: 'M7 13c1.66 0 3-1.34 3-3S8.66 7 7 7s-3 1.34-3 3 1.34 3 3 3zm12-6h-6.18C12.4 5.84 11.3 5 10 5H7c-1.89 0-3.39 1.67-3 3.56C4.27 10.03 5.5 11 7 11v2H6c-1.1 0-2 .9-2 2v7h2v-2h12v2h2v-7c0-1.1-.9-2-2-2h-1V9c1.5 0 2.73-.97 3-2.44.39-1.89-1.11-3.56-3-3.56z'
      },
      {
        label: 'อัตราค่าห้อง',
        path: '/room-rates',
        icon: 'M11.8 10.9c-2.27-.59-3-1.2-3-2.15 0-1.09 1.01-1.85 2.7-1.85 1.78 0 2.44.85 2.5 2.1h2.21c-.07-1.72-1.12-3.3-3.21-3.81V3h-3v2.16c-1.94.42-3.5 1.68-3.5 3.61 0 2.31 1.91 3.46 4.7 4.13 2.5.6 3 1.48 3 2.41 0 .69-.49 1.79-2.7 1.79-2.06 0-2.87-.92-2.98-2.1h-2.2c.12 2.19 1.76 3.42 3.68 3.83V21h3v-2.15c1.95-.37 3.5-1.5 3.5-3.55 0-2.84-2.43-3.81-4.7-4.4z'
      }
    ]

    items.push({
      label: 'จัดการห้องพัก',
      icon: 'M19 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4l1-1h4l1 1h4a2 2 0 012 2v14a2 2 0 01-2 2zm-3-15H8a3 3 0 100 6 3 3 0 000-6z',
      children: roomItems
    })

    // Products & Orders submenu
    const productsItems: MenuItem[] = [
      {
        label: 'จัดการ QR Code',
        path: '/qrcode-manager',
        icon: 'M3 11h8V3H3v8zm0 8h8v-8H3v8zm8-16h8V3h-8v8zm0 8h8v-8h-8v8zM9 9H5V5h4v4zm0 8H5v-4h4v4zm8 0h-4v-4h4v4zm0-8h-4V5h4v4z'
      },
      {
        label: 'จัดการสินค้า',
        path: '/products',
        icon: 'M7 18c-1.1 0-1.99.9-1.99 2S5.9 22 7 22s2-.9 2-2-.9-2-2-2zM1 2v2h2l3.6 7.59-1.35 2.45c-.16.28-.25.61-.25.96 0 1.1.9 2 2 2h12v-2H7.42c-.14 0-.25-.11-.25-.25l.03-.12.9-1.63h7.45c.75 0 1.41-.41 1.75-1.03l3.58-6.49c.08-.14.12-.31.12-.48 0-.55-.45-1-1-1H5.21l-.94-2H1zm16 16c-1.1 0-1.99.9-1.99 2s.89 2 1.99 2 2-.9 2-2-.9-2-2-2z'
      },
      {
        label: 'คำสั่งซื้อ',
        path: '/orders',
        icon: 'M9 8h-3v2h3v-2zm0 5h-3v2h3v-2zm0 5h-3v2h3v-2zm5-15h-1v-2h-2v2h-6v2h14v-2h-5zm2 5v10c0 1.1-.9 2-2 2h-10c-1.1 0-2-.9-2-2v-10h16zm-11 3h-2v8h2v-8zm4 0h-2v8h2v-8zm4 0h-2v8h2v-8z'
      }
    ]

    items.push({
      label: 'สินค้า & ออเดอร์',
      icon: 'M16 6H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2zm0 12H4V8h12v10zm-5-7h4v2h-4zm0 4h4v2h-4zM5 11h2v6H5z',
      children: productsItems
    })

    // System Administration submenu (ADMIN only items)
    const adminItems: MenuItem[] = [
      {
        label: 'จัดการผู้ใช้',
        path: '/users',
        icon: 'M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z'
      },
      {
        label: 'ตั้งค่าระบบ',
        path: '/settings',
        icon: 'M19.14 12.94c.04-.3.06-.61.06-.94 0-.32-.02-.64-.07-.94l2.03-1.58c.18-.14.23-.41.12-.61l-1.92-3.32c-.12-.22-.37-.29-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94L14.4 2.81c-.04-.24-.24-.41-.48-.41h-3.84c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96c-.22-.08-.47 0-.59.22L2.74 8.87c-.12.21-.08.47.12.61l2.03 1.58c-.05.3-.09.63-.09.94s.02.64.07.94l-2.03 1.58c-.18.14-.23.41-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z'
      }
    ]

    items.push({
      label: 'ระบบ',
      icon: 'M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2V17zm4 0h-2V5h2V17zm4 0h-2v-4h2V17z',
      children: adminItems
    })
  }

  // Smart Breakers - for Admin and Reception
  if (authStore.isAdmin || authStore.hasRole(['RECEPTION'])) {
    // Find "ระบบ" menu to add Smart Breakers as submenu
    const systemMenu = items.find(item => item.label === 'ระบบ')

    if (systemMenu && systemMenu.children) {
      // Add Smart Breakers at the beginning of system submenu
      systemMenu.children.unshift({
        label: 'Smart Breakers',
        path: '/breakers',
        icon: 'M11.5 1L2 6v2h19V6l-9.5-5zM12 13c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm-9 7h18v-2h-18v2zm0-4h18v-2h-18v2zm0-6v2h3.42c-.43-.63-.67-1.4-.67-2.21 0-.83.26-1.59.7-2.21H3v2.42zm7 0c0-1.53 1.24-2.77 2.77-2.77s2.77 1.24 2.77 2.77-1.24 2.77-2.77 2.77S10 11.53 10 10zm11 0v-2h-3.43c.43.63.67 1.4.67 2.21 0 .83-.26 1.59-.7 2.21H21V10z'
      })
    } else if (!systemMenu) {
      // If no system menu exists (for Reception), create it
      const breakersItems: MenuItem[] = [{
        label: 'Smart Breakers',
        path: '/breakers',
        icon: 'M11.5 1L2 6v2h19V6l-9.5-5zM12 13c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm-9 7h18v-2h-18v2zm0-4h18v-2h-18v2zm0-6v2h3.42c-.43-.63-.67-1.4-.67-2.21 0-.83.26-1.59.7-2.21H3v2.42zm7 0c0-1.53 1.24-2.77 2.77-2.77s2.77 1.24 2.77 2.77-1.24 2.77-2.77 2.77S10 11.53 10 10zm11 0v-2h-3.43c.43.63.67 1.4.67 2.21 0 .83-.26 1.59-.7 2.21H21V10z'
      }]

      items.push({
        label: 'ระบบ',
        icon: 'M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2V17zm4 0h-2V5h2V17zm4 0h-2v-4h2V17z',
        children: breakersItems
      })
    }
  }

  return items
})

// Current page title
const currentPageTitle = computed(() => {
  const item = menuItems.value.find(i => i.path === route.path)
  return item?.label || 'FlyingHotel'
})

// User initials
const userInitials = computed(() => {
  const name = authStore.user?.full_name || 'U'
  return name.charAt(0).toUpperCase()
})

// Role label
const roleLabel = computed(() => {
  const roleMap: Record<string, string> = {
    admin: 'ผู้ดูแลระบบ',
    reception: 'แผนกต้อนรับ',
    housekeeping: 'แผนกแม่บ้าน',
    maintenance: 'แผนกซ่อมบำรุง'
  }
  return roleMap[authStore.user?.role || ''] || 'ผู้ใช้'
})

// Toggle submenu
function toggleSubmenu(label: string) {
  const index = expandedMenus.value.indexOf(label)
  if (index > -1) {
    expandedMenus.value.splice(index, 1)
  } else {
    expandedMenus.value.push(label)
  }
}

// Navigate
function navigateTo(path: string) {
  router.push(path)
}

// Open edit profile modal
function openEditProfile() {
  editProfileForm.value.full_name = authStore.user?.full_name || ''
  showEditProfileModal.value = true
  showUserMenu.value = false
}

// Save profile changes
async function saveProfileChanges() {
  try {
    const response = await axios.put('/auth/profile', {
      full_name: editProfileForm.value.full_name
    })

    if (response.status === 200) {
      authStore.user!.full_name = editProfileForm.value.full_name
      showEditProfileModal.value = false
      message.success('อัปเดตโปรไฟล์เรียบร้อย')
    }
  } catch (error: any) {
    console.error('Error updating profile:', error)
    const errorMessage = error.response?.data?.detail || 'ไม่สามารถอัปเดตโปรไฟล์ได้'
    message.error(errorMessage)
  }
}

// Open change password modal
function openChangePassword() {
  changePasswordForm.value = {
    current_password: '',
    new_password: '',
    confirm_password: ''
  }
  showChangePasswordModal.value = true
  showUserMenu.value = false
}

// Change password
async function changePassword() {
  if (changePasswordForm.value.new_password !== changePasswordForm.value.confirm_password) {
    message.error('รหัสผ่านใหม่ไม่ตรงกัน')
    return
  }

  if (changePasswordForm.value.new_password.length < 6) {
    message.error('รหัสผ่านต้องมีความยาวอย่างน้อย 6 ตัวอักษร')
    return
  }

  try {
    const response = await axios.post('/auth/change-password', {
      current_password: changePasswordForm.value.current_password,
      new_password: changePasswordForm.value.new_password
    })

    if (response.status === 200) {
      showChangePasswordModal.value = false
      message.success('เปลี่ยนรหัสผ่านเรียบร้อย')
    }
  } catch (error: any) {
    console.error('Error changing password:', error)
    const errorMessage = error.response?.data?.detail || 'ไม่สามารถเปลี่ยนรหัสผ่านได้'
    message.error(errorMessage)
  }
}

// Logout
async function handleLogout() {
  await authStore.logout()
  router.push('/login')
}

// Click outside directive
const vClickOutside = {
  mounted(el: any, binding: any) {
    el.clickOutsideEvent = (event: Event) => {
      if (!(el === event.target || el.contains(event.target))) {
        binding.value()
      }
    }
    document.addEventListener('click', el.clickOutsideEvent)
  },
  unmounted(el: any) {
    document.removeEventListener('click', el.clickOutsideEvent)
  }
}
</script>

<style scoped>
/* Shimmer animation */
@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

.animate-shimmer {
  animation: shimmer 3s infinite;
}

/* Drawer transition */
.drawer-enter-active,
.drawer-leave-active {
  transition: all 0.3s ease;
}

.drawer-enter-from,
.drawer-leave-to {
  opacity: 0;
}

.drawer-enter-from .absolute.left-0,
.drawer-leave-to .absolute.left-0 {
  transform: translateX(-100%);
}

/* Dropdown transition */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.2s ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* Scrollbar */
::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: linear-gradient(to bottom, #6366f1, #a855f7);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(to bottom, #4f46e5, #9333ea);
}
</style>
