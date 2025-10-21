<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-indigo-50 pb-12">
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

        <!-- Real-time Stats Cards -->
        <div v-if="loading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div v-for="i in 4" :key="i" class="bg-white bg-opacity-95 backdrop-blur-xl rounded-3xl p-6 shadow-xl">
            <div class="animate-pulse">
              <div class="h-14 w-14 bg-gray-300 rounded-2xl mb-4"></div>
              <div class="h-8 bg-gray-300 rounded w-20 mb-2"></div>
              <div class="h-4 bg-gray-300 rounded w-32"></div>
            </div>
          </div>
        </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <!-- Total Rooms Card -->
          <div class="group bg-white bg-opacity-95 backdrop-blur-xl rounded-3xl p-6 shadow-xl hover:shadow-2xl transform hover:-translate-y-2 transition-all duration-300">
            <div class="flex items-center justify-between mb-4">
              <div class="w-14 h-14 bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform">
                <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                </svg>
              </div>
              <span class="text-3xl font-bold text-gray-900">{{ stats.totalRooms }}</span>
            </div>
            <p class="text-gray-600 font-semibold text-lg">ห้องพักทั้งหมด</p>
            <div class="mt-2 h-1 w-full bg-gray-200 rounded-full overflow-hidden">
              <div class="h-full bg-gradient-to-r from-blue-500 to-blue-600 rounded-full" style="width: 100%"></div>
            </div>
          </div>

          <!-- Available Rooms Card -->
          <div class="group bg-white bg-opacity-95 backdrop-blur-xl rounded-3xl p-6 shadow-xl hover:shadow-2xl transform hover:-translate-y-2 transition-all duration-300">
            <div class="flex items-center justify-between mb-4">
              <div class="w-14 h-14 bg-gradient-to-br from-green-500 to-green-600 rounded-2xl flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform">
                <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <span class="text-3xl font-bold text-gray-900">{{ stats.availableRooms }}</span>
            </div>
            <p class="text-gray-600 font-semibold text-lg">ห้องว่าง</p>
            <div class="mt-2 h-1 w-full bg-gray-200 rounded-full overflow-hidden">
              <div class="h-full bg-gradient-to-r from-green-500 to-green-600 rounded-full" :style="`width: ${stats.availablePercentage}%`"></div>
            </div>
          </div>

          <!-- Occupied Rooms Card -->
          <div class="group bg-white bg-opacity-95 backdrop-blur-xl rounded-3xl p-6 shadow-xl hover:shadow-2xl transform hover:-translate-y-2 transition-all duration-300">
            <div class="flex items-center justify-between mb-4">
              <div class="w-14 h-14 bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform">
                <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
              <span class="text-3xl font-bold text-gray-900">{{ stats.occupiedRooms }}</span>
            </div>
            <p class="text-gray-600 font-semibold text-lg">ห้องมีผู้เข้าพัก</p>
            <div class="mt-2 h-1 w-full bg-gray-200 rounded-full overflow-hidden">
              <div class="h-full bg-gradient-to-r from-purple-500 to-purple-600 rounded-full" :style="`width: ${stats.occupiedPercentage}%`"></div>
            </div>
          </div>

          <!-- Revenue Card (Today) -->
          <div class="group bg-white bg-opacity-95 backdrop-blur-xl rounded-3xl p-6 shadow-xl hover:shadow-2xl transform hover:-translate-y-2 transition-all duration-300">
            <div class="flex items-center justify-between mb-4">
              <div class="w-14 h-14 bg-gradient-to-br from-yellow-500 to-orange-500 rounded-2xl flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform">
                <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <span class="text-2xl font-bold text-gray-900">฿{{ stats.totalRevenue.toLocaleString('th-TH') }}</span>
            </div>
            <p class="text-gray-600 font-semibold text-lg">รายได้รวม (20 วัน)</p>
            <div class="mt-2 h-1 w-full bg-gray-200 rounded-full overflow-hidden">
              <div class="h-full bg-gradient-to-r from-yellow-500 to-orange-500 rounded-full" style="width: 85%"></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 -mt-20">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Main Column -->
        <div class="lg:col-span-2 space-y-8">
          <!-- Quick Access Features -->
          <div class="bg-white rounded-3xl shadow-xl p-8">
            <div class="flex items-center space-x-4 mb-6">
              <div class="w-16 h-16 bg-gradient-to-br from-indigo-500 to-purple-500 rounded-2xl flex items-center justify-center">
                <svg class="w-9 h-9 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <div>
                <h2 class="text-2xl font-bold text-gray-900">เข้าถึงฟีเจอร์หลักอย่างรวดเร็ว</h2>
                <p class="text-gray-500">ฟีเจอร์สำคัญของระบบ PMS</p>
              </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <!-- Dashboard -->
              <button
                v-if="authStore.isAdmin || authStore.hasRole(['RECEPTION'])"
                @click="$router.push('/dashboard')"
                class="group p-6 bg-gradient-to-br from-blue-50 to-indigo-50 hover:from-blue-100 hover:to-indigo-100 rounded-2xl transition-all duration-300 transform hover:-translate-y-1 hover:shadow-lg border-2 border-transparent hover:border-blue-500"
              >
                <div class="flex items-center space-x-4">
                  <div class="w-12 h-12 bg-blue-500 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
                    <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                  </div>
                  <div class="text-left">
                    <p class="font-bold text-gray-900 text-lg">แดชบอร์ดห้องพัก</p>
                    <p class="text-sm text-gray-600">เช็คอิน/เช็คเอาท์แบบเรียลไทม์</p>
                  </div>
                </div>
              </button>

              <!-- Bookings -->
              <button
                v-if="authStore.isAdmin || authStore.hasRole(['RECEPTION'])"
                @click="$router.push('/bookings')"
                class="group p-6 bg-gradient-to-br from-purple-50 to-pink-50 hover:from-purple-100 hover:to-pink-100 rounded-2xl transition-all duration-300 transform hover:-translate-y-1 hover:shadow-lg border-2 border-transparent hover:border-purple-500"
              >
                <div class="flex items-center space-x-4">
                  <div class="w-12 h-12 bg-purple-500 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
                    <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <div class="text-left">
                    <p class="font-bold text-gray-900 text-lg">ปฏิทินจองห้อง</p>
                    <p class="text-sm text-gray-600">จัดการการจองล่วงหน้า</p>
                  </div>
                </div>
              </button>

              <!-- Reports -->
              <button
                v-if="authStore.isAdmin || authStore.hasRole(['RECEPTION'])"
                @click="$router.push('/reports')"
                class="group p-6 bg-gradient-to-br from-green-50 to-emerald-50 hover:from-green-100 hover:to-emerald-100 rounded-2xl transition-all duration-300 transform hover:-translate-y-1 hover:shadow-lg border-2 border-transparent hover:border-green-500"
              >
                <div class="flex items-center space-x-4">
                  <div class="w-12 h-12 bg-green-500 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
                    <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <div class="text-left">
                    <p class="font-bold text-gray-900 text-lg">รายงานและสถิติ</p>
                    <p class="text-sm text-gray-600">วิเคราะห์รายได้และอัตราเข้าพัก</p>
                  </div>
                </div>
              </button>

              <!-- Customers -->
              <button
                v-if="authStore.isAdmin || authStore.hasRole(['RECEPTION'])"
                @click="$router.push('/customers')"
                class="group p-6 bg-gradient-to-br from-yellow-50 to-orange-50 hover:from-yellow-100 hover:to-orange-100 rounded-2xl transition-all duration-300 transform hover:-translate-y-1 hover:shadow-lg border-2 border-transparent hover:border-yellow-500"
              >
                <div class="flex items-center space-x-4">
                  <div class="w-12 h-12 bg-yellow-500 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
                    <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                    </svg>
                  </div>
                  <div class="text-left">
                    <p class="font-bold text-gray-900 text-lg">ฐานข้อมูลลูกค้า</p>
                    <p class="text-sm text-gray-600">CRM และประวัติการเข้าพัก</p>
                  </div>
                </div>
              </button>

              <!-- Housekeeping -->
              <button
                v-if="authStore.isAdmin || authStore.hasRole(['RECEPTION', 'HOUSEKEEPING'])"
                @click="$router.push('/housekeeping')"
                class="group p-6 bg-gradient-to-br from-teal-50 to-cyan-50 hover:from-teal-100 hover:to-cyan-100 rounded-2xl transition-all duration-300 transform hover:-translate-y-1 hover:shadow-lg border-2 border-transparent hover:border-teal-500"
              >
                <div class="flex items-center space-x-4">
                  <div class="w-12 h-12 bg-teal-500 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
                    <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                    </svg>
                  </div>
                  <div class="text-left">
                    <p class="font-bold text-gray-900 text-lg">งานแม่บ้าน</p>
                    <p class="text-sm text-gray-600">จัดการทำความสะอาด</p>
                  </div>
                </div>
              </button>

              <!-- Maintenance -->
              <button
                v-if="authStore.isAdmin || authStore.hasRole(['RECEPTION', 'MAINTENANCE'])"
                @click="$router.push('/maintenance')"
                class="group p-6 bg-gradient-to-br from-red-50 to-rose-50 hover:from-red-100 hover:to-rose-100 rounded-2xl transition-all duration-300 transform hover:-translate-y-1 hover:shadow-lg border-2 border-transparent hover:border-red-500"
              >
                <div class="flex items-center space-x-4">
                  <div class="w-12 h-12 bg-red-500 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
                    <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                  </div>
                  <div class="text-left">
                    <p class="font-bold text-gray-900 text-lg">งานซ่อมบำรุง</p>
                    <p class="text-sm text-gray-600">แจ้งซ่อมและติดตาม</p>
                  </div>
                </div>
              </button>

              <!-- Products & Orders -->
              <button
                v-if="authStore.isAdmin || authStore.hasRole(['RECEPTION'])"
                @click="$router.push('/products')"
                class="group p-6 bg-gradient-to-br from-indigo-50 to-blue-50 hover:from-indigo-100 hover:to-blue-100 rounded-2xl transition-all duration-300 transform hover:-translate-y-1 hover:shadow-lg border-2 border-transparent hover:border-indigo-500"
              >
                <div class="flex items-center space-x-4">
                  <div class="w-12 h-12 bg-indigo-500 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
                    <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
                    </svg>
                  </div>
                  <div class="text-left">
                    <p class="font-bold text-gray-900 text-lg">สินค้าและออเดอร์</p>
                    <p class="text-sm text-gray-600">จัดการสินค้าและคำสั่งซื้อ</p>
                  </div>
                </div>
              </button>

              <!-- Settings -->
              <button
                v-if="authStore.isAdmin"
                @click="$router.push('/settings')"
                class="group p-6 bg-gradient-to-br from-gray-50 to-slate-50 hover:from-gray-100 hover:to-slate-100 rounded-2xl transition-all duration-300 transform hover:-translate-y-1 hover:shadow-lg border-2 border-transparent hover:border-gray-500"
              >
                <div class="flex items-center space-x-4">
                  <div class="w-12 h-12 bg-gray-700 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
                    <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                  </div>
                  <div class="text-left">
                    <p class="font-bold text-gray-900 text-lg">ตั้งค่าระบบ</p>
                    <p class="text-sm text-gray-600">กำหนดค่าและ Telegram</p>
                  </div>
                </div>
              </button>
            </div>
          </div>

          <!-- User Info Card -->
          <div class="bg-white rounded-3xl shadow-xl p-8">
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
              <!-- Username -->
              <div class="flex items-center justify-between p-4 bg-gray-50 rounded-2xl hover:bg-gray-100 transition-colors">
                <div class="flex items-center space-x-3">
                  <svg class="w-5 h-5 text-indigo-600" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
                  </svg>
                  <span class="text-gray-600 font-medium">ชื่อผู้ใช้</span>
                </div>
                <span class="text-gray-900 font-semibold">{{ authStore.user?.username }}</span>
              </div>

              <!-- Role -->
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
        </div>

        <!-- Sidebar -->
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

          <!-- Room Management Menu -->
          <div v-if="authStore.isAdmin || authStore.hasRole(['RECEPTION'])" class="bg-white rounded-3xl shadow-xl p-6">
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
const loading = ref(true)
const currentTime = ref('')
const currentDate = ref('')

interface Stats {
  totalRooms: number
  availableRooms: number
  occupiedRooms: number
  cleaningRooms: number
  reservedRooms: number
  outOfServiceRooms: number
  totalRevenue: number
  totalCheckins: number
  occupancyRate: number
  availablePercentage: number
  occupiedPercentage: number
}

const stats = ref<Stats>({
  totalRooms: 0,
  availableRooms: 0,
  occupiedRooms: 0,
  cleaningRooms: 0,
  reservedRooms: 0,
  outOfServiceRooms: 0,
  totalRevenue: 0,
  totalCheckins: 0,
  occupancyRate: 0,
  availablePercentage: 0,
  occupiedPercentage: 0
})

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

async function loadStats() {
  try {
    loading.value = true

    // Get room statistics from occupancy report
    const today = new Date().toISOString().split('T')[0]
    const response = await axios.get(`/reports/occupancy?start_date=${today}&end_date=${today}`)

    const roomStatus = response.data.room_status_distribution
    const totalRooms = response.data.total_rooms
    const occupiedRooms = roomStatus.occupied
    const availableRooms = roomStatus.available

    // Get revenue from reports
    const startDate = new Date(Date.now() - 20 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
    const summaryResponse = await axios.get(`/reports/summary?start_date=${startDate}&end_date=${today}`)

    stats.value = {
      totalRooms: totalRooms,
      availableRooms: availableRooms,
      occupiedRooms: occupiedRooms,
      cleaningRooms: roomStatus.cleaning,
      reservedRooms: roomStatus.reserved,
      outOfServiceRooms: roomStatus.out_of_service,
      totalRevenue: summaryResponse.data.total_revenue || 0,
      totalCheckins: summaryResponse.data.total_checkins || 0,
      occupancyRate: response.data.occupancy_rate || 0,
      availablePercentage: totalRooms > 0 ? (availableRooms / totalRooms * 100) : 0,
      occupiedPercentage: totalRooms > 0 ? (occupiedRooms / totalRooms * 100) : 0
    }
  } catch (error) {
    console.error('Error loading stats:', error)
  } finally {
    loading.value = false
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
  loadStats()
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
