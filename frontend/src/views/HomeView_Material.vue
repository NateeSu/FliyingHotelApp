<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-indigo-50">
    <!-- Hero Section with Animated Background -->
    <div class="relative overflow-hidden bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 pb-32">
      <!-- Decorative Elements -->
      <div class="absolute inset-0 opacity-20">
        <div class="absolute top-0 left-0 w-96 h-96 bg-yellow-400 rounded-full mix-blend-multiply filter blur-3xl animate-blob"></div>
        <div class="absolute top-0 right-0 w-96 h-96 bg-pink-400 rounded-full mix-blend-multiply filter blur-3xl animate-blob animation-delay-2000"></div>
        <div class="absolute bottom-0 left-1/2 w-96 h-96 bg-blue-400 rounded-full mix-blend-multiply filter blur-3xl animate-blob animation-delay-4000"></div>
      </div>

      <div class="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-12 pb-24">
        <!-- Welcome Header -->
        <div class="text-center mb-12">
          <div class="inline-flex items-center justify-center p-2 bg-white bg-opacity-20 backdrop-blur-lg rounded-2xl mb-6">
            <div class="flex items-center space-x-3 px-6 py-3">
              <div class="w-12 h-12 bg-white rounded-xl flex items-center justify-center shadow-lg">
                <svg class="w-7 h-7 text-indigo-600" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
                </svg>
              </div>
              <div class="text-left">
                <p class="text-sm text-white text-opacity-90 font-medium">ยินดีต้อนรับ</p>
                <p class="text-xl font-bold text-white">{{ authStore.user?.full_name }}</p>
              </div>
            </div>
          </div>

          <h1 class="text-5xl font-extrabold text-white mb-4 drop-shadow-lg">
            แดชบอร์ดหลัก
          </h1>
          <p class="text-xl text-white text-opacity-90 font-medium">
            {{ getRoleText(authStore.user?.role) }}
          </p>
        </div>

        <!-- Stats Cards -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <!-- Stat Card 1 -->
          <div class="group bg-white bg-opacity-95 backdrop-blur-xl rounded-3xl p-6 shadow-xl hover:shadow-2xl transform hover:-translate-y-2 transition-all duration-300">
            <div class="flex items-center justify-between mb-4">
              <div class="w-14 h-14 bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform">
                <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                </svg>
              </div>
              <span class="text-3xl font-bold text-gray-900">50</span>
            </div>
            <p class="text-gray-600 font-semibold text-lg">ห้องพักทั้งหมด</p>
            <div class="mt-2 h-1 w-full bg-gray-200 rounded-full overflow-hidden">
              <div class="h-full bg-gradient-to-r from-blue-500 to-blue-600 rounded-full" style="width: 75%"></div>
            </div>
          </div>

          <!-- Stat Card 2 -->
          <div class="group bg-white bg-opacity-95 backdrop-blur-xl rounded-3xl p-6 shadow-xl hover:shadow-2xl transform hover:-translate-y-2 transition-all duration-300">
            <div class="flex items-center justify-between mb-4">
              <div class="w-14 h-14 bg-gradient-to-br from-green-500 to-green-600 rounded-2xl flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform">
                <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <span class="text-3xl font-bold text-gray-900">35</span>
            </div>
            <p class="text-gray-600 font-semibold text-lg">ห้องว่าง</p>
            <div class="mt-2 h-1 w-full bg-gray-200 rounded-full overflow-hidden">
              <div class="h-full bg-gradient-to-r from-green-500 to-green-600 rounded-full" style="width: 70%"></div>
            </div>
          </div>

          <!-- Stat Card 3 -->
          <div class="group bg-white bg-opacity-95 backdrop-blur-xl rounded-3xl p-6 shadow-xl hover:shadow-2xl transform hover:-translate-y-2 transition-all duration-300">
            <div class="flex items-center justify-between mb-4">
              <div class="w-14 h-14 bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform">
                <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <span class="text-3xl font-bold text-gray-900">15</span>
            </div>
            <p class="text-gray-600 font-semibold text-lg">ห้องมีผู้เข้าพัก</p>
            <div class="mt-2 h-1 w-full bg-gray-200 rounded-full overflow-hidden">
              <div class="h-full bg-gradient-to-r from-purple-500 to-purple-600 rounded-full" style="width: 30%"></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 -mt-20 pb-12">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- User Info Card -->
        <div class="lg:col-span-2 space-y-8">
          <!-- Profile Card -->
          <div class="bg-white rounded-3xl shadow-xl p-8 transform hover:shadow-2xl transition-all duration-300">
            <div class="flex items-center space-x-4 mb-6">
              <div class="w-16 h-16 bg-gradient-to-br from-indigo-500 to-purple-500 rounded-2xl flex items-center justify-center">
                <svg class="w-9 h-9 text-white" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
                </svg>
              </div>
              <div>
                <h2 class="text-2xl font-bold text-gray-900">ข้อมูลผู้ใช้</h2>
                <p class="text-gray-500">รายละเอียดบัญชีของคุณ</p>
              </div>
            </div>

            <div class="space-y-4">
              <!-- Info Row -->
              <div class="flex items-center justify-between p-4 bg-gray-50 rounded-2xl hover:bg-gray-100 transition-colors">
                <div class="flex items-center space-x-3">
                  <svg class="w-5 h-5 text-indigo-600" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
                  </svg>
                  <span class="text-gray-600 font-medium">ชื่อผู้ใช้</span>
                </div>
                <span class="text-gray-900 font-semibold">{{ authStore.user?.username }}</span>
              </div>

              <!-- Role Badge -->
              <div class="flex items-center justify-between p-4 bg-gray-50 rounded-2xl hover:bg-gray-100 transition-colors">
                <div class="flex items-center space-x-3">
                  <svg class="w-5 h-5 text-indigo-600" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
                  </svg>
                  <span class="text-gray-600 font-medium">บทบาท</span>
                </div>
                <span :class="getRoleBadgeClass(authStore.user?.role)" class="px-4 py-2 rounded-xl font-semibold text-sm">
                  {{ getRoleText(authStore.user?.role) }}
                </span>
              </div>

              <!-- Status -->
              <div class="flex items-center justify-between p-4 bg-gray-50 rounded-2xl hover:bg-gray-100 transition-colors">
                <div class="flex items-center space-x-3">
                  <svg class="w-5 h-5 text-indigo-600" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                  </svg>
                  <span class="text-gray-600 font-medium">สถานะ</span>
                </div>
                <span class="inline-flex items-center px-4 py-2 rounded-xl bg-green-100 text-green-700 font-semibold text-sm">
                  <span class="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></span>
                  ใช้งานอยู่
                </span>
              </div>
            </div>
          </div>

          <!-- System Status Card -->
          <div class="bg-white rounded-3xl shadow-xl p-8 transform hover:shadow-2xl transition-all duration-300">
            <div class="flex items-center space-x-4 mb-6">
              <div class="w-16 h-16 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-2xl flex items-center justify-center">
                <svg class="w-9 h-9 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01" />
                </svg>
              </div>
              <div>
                <h2 class="text-2xl font-bold text-gray-900">สถานะระบบ</h2>
                <p class="text-gray-500">ตรวจสอบการเชื่อมต่อ</p>
              </div>
            </div>

            <!-- Status Alert -->
            <div v-if="backendStatus" :class="backendStatus.type === 'success' ? 'bg-green-50 border-green-500' : 'bg-red-50 border-red-500'" class="border-l-4 p-4 rounded-2xl mb-4">
              <div class="flex items-center">
                <svg v-if="backendStatus.type === 'success'" class="w-6 h-6 text-green-500 mr-3" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                </svg>
                <svg v-else class="w-6 h-6 text-red-500 mr-3" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                </svg>
                <p :class="backendStatus.type === 'success' ? 'text-green-700' : 'text-red-700'" class="font-semibold">
                  {{ backendStatus.message }}
                </p>
              </div>
            </div>

            <button
              @click="checkBackend"
              :disabled="checking"
              class="w-full bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 text-white font-bold py-4 px-6 rounded-2xl shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
            >
              <svg v-if="!checking" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              <svg v-else class="animate-spin h-6 w-6" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span>{{ checking ? 'กำลังตรวจสอบ...' : 'ตรวจสอบการเชื่อมต่อ' }}</span>
            </button>
          </div>
        </div>

        <!-- Quick Actions Sidebar -->
        <div class="lg:col-span-1 space-y-6">
          <!-- Admin Menu -->
          <div v-if="authStore.isAdmin" class="bg-gradient-to-br from-indigo-600 to-purple-600 rounded-3xl shadow-xl p-8 text-white transform hover:scale-105 transition-transform duration-300">
            <div class="w-16 h-16 bg-white bg-opacity-20 backdrop-blur-lg rounded-2xl flex items-center justify-center mb-6 mx-auto">
              <svg class="w-9 h-9" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
              </svg>
            </div>
            <h3 class="text-2xl font-bold mb-2 text-center">เมนูผู้ดูแลระบบ</h3>
            <p class="text-white text-opacity-90 mb-6 text-center">จัดการผู้ใช้และระบบ</p>
            <button
              @click="$router.push('/users')"
              class="w-full bg-white text-indigo-600 font-bold py-4 px-6 rounded-2xl shadow-lg hover:shadow-xl transform hover:-translate-y-1 transition-all duration-300 flex items-center justify-center space-x-2"
            >
              <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                <path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/>
              </svg>
              <span>จัดการผู้ใช้</span>
            </button>
          </div>

          <!-- Phase 3: Dashboard (Critical Feature) -->
          <div v-if="authStore.isAdmin || authStore.user?.role?.toLowerCase() === 'reception'" class="bg-gradient-to-br from-blue-600 to-indigo-600 rounded-3xl shadow-xl p-8 text-white transform hover:scale-105 transition-transform duration-300">
            <div class="w-16 h-16 bg-white bg-opacity-20 backdrop-blur-lg rounded-2xl flex items-center justify-center mb-6 mx-auto">
              <svg class="w-9 h-9" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <h3 class="text-2xl font-bold mb-2 text-center">แดชบอร์ดห้องพัก</h3>
            <p class="text-white text-opacity-90 mb-6 text-center">ดูสถานะห้องแบบเรียลไทม์</p>
            <button
              @click="$router.push('/dashboard')"
              class="w-full bg-white text-blue-600 font-bold py-4 px-6 rounded-2xl shadow-lg hover:shadow-xl transform hover:-translate-y-1 transition-all duration-300 flex items-center justify-center space-x-2"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
              <span>เปิดแดชบอร์ด</span>
            </button>
          </div>

          <!-- Phase 2: Room Management Menu -->
          <div v-if="authStore.isAdmin || authStore.user?.role?.toLowerCase() === 'reception'" class="bg-white rounded-3xl shadow-xl p-6">
            <div class="flex items-center space-x-3 mb-6">
              <div class="w-12 h-12 bg-gradient-to-br from-green-500 to-blue-500 rounded-xl flex items-center justify-center">
                <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                </svg>
              </div>
              <div>
                <h3 class="text-lg font-bold text-gray-900">จัดการห้องพัก</h3>
                <p class="text-sm text-gray-500">Room Management</p>
              </div>
            </div>

            <div class="space-y-3">
              <button
                @click="$router.push('/rooms')"
                class="w-full flex items-center justify-between p-4 bg-gradient-to-r from-green-50 to-blue-50 hover:from-green-100 hover:to-blue-100 rounded-xl transition-all duration-200 group"
              >
                <div class="flex items-center space-x-3">
                  <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                  </svg>
                  <span class="font-semibold text-gray-700">ห้องพัก</span>
                </div>
                <svg class="w-5 h-5 text-gray-400 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </button>

              <button
                v-if="authStore.isAdmin"
                @click="$router.push('/room-types')"
                class="w-full flex items-center justify-between p-4 bg-gradient-to-r from-purple-50 to-pink-50 hover:from-purple-100 hover:to-pink-100 rounded-xl transition-all duration-200 group"
              >
                <div class="flex items-center space-x-3">
                  <svg class="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                  </svg>
                  <span class="font-semibold text-gray-700">ประเภทห้อง</span>
                </div>
                <svg class="w-5 h-5 text-gray-400 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </button>

              <button
                v-if="authStore.isAdmin"
                @click="$router.push('/room-rates')"
                class="w-full flex items-center justify-between p-4 bg-gradient-to-r from-yellow-50 to-orange-50 hover:from-yellow-100 hover:to-orange-100 rounded-xl transition-all duration-200 group"
              >
                <div class="flex items-center space-x-3">
                  <svg class="w-5 h-5 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span class="font-semibold text-gray-700">ราคาห้อง</span>
                </div>
                <svg class="w-5 h-5 text-gray-400 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </button>
            </div>
          </div>

          <!-- Time Widget -->
          <div class="bg-white rounded-3xl shadow-xl p-8">
            <div class="text-center">
              <div class="w-16 h-16 bg-gradient-to-br from-pink-500 to-orange-500 rounded-2xl flex items-center justify-center mb-4 mx-auto">
                <svg class="w-9 h-9 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <p class="text-gray-500 font-medium mb-2">เวลาปัจจุบัน</p>
              <p class="text-3xl font-bold text-gray-900">{{ currentTime }}</p>
              <p class="text-gray-500 mt-2">{{ currentDate }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import axios from '@/api/axios'

const authStore = useAuthStore()
const backendStatus = ref<{ type: 'success' | 'error', message: string } | null>(null)
const checking = ref(false)
const currentTime = ref('')
const currentDate = ref('')

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

function getRoleBadgeClass(role?: string): string {
  const roleKey = role?.toLowerCase()
  const classMap: Record<string, string> = {
    admin: 'bg-red-100 text-red-700',
    reception: 'bg-blue-100 text-blue-700',
    housekeeping: 'bg-green-100 text-green-700',
    maintenance: 'bg-yellow-100 text-yellow-700'
  }
  return classMap[roleKey || ''] || 'bg-gray-100 text-gray-700'
}

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

function updateTime() {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString('th-TH', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
  currentDate.value = now.toLocaleDateString('th-TH', { year: 'numeric', month: 'long', day: 'numeric' })
}

let timeInterval: number

onMounted(() => {
  updateTime()
  timeInterval = setInterval(updateTime, 1000) as unknown as number
})

onUnmounted(() => {
  if (timeInterval) {
    clearInterval(timeInterval)
  }
})
</script>

<style scoped>
@keyframes blob {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  25% {
    transform: translate(20px, -50px) scale(1.1);
  }
  50% {
    transform: translate(-20px, 20px) scale(0.9);
  }
  75% {
    transform: translate(50px, 10px) scale(1.05);
  }
}

.animate-blob {
  animation: blob 7s infinite cubic-bezier(0.4, 0, 0.6, 1);
}

.animation-delay-2000 {
  animation-delay: 2s;
}

.animation-delay-4000 {
  animation-delay: 4s;
}
</style>
