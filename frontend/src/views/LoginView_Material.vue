<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-800 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
    <!-- Animated Background -->
    <div class="absolute inset-0 overflow-hidden opacity-20">
      <div class="absolute -top-40 -right-40 w-96 h-96 bg-yellow-400 rounded-full mix-blend-multiply filter blur-3xl animate-blob"></div>
      <div class="absolute -bottom-40 -left-40 w-96 h-96 bg-blue-400 rounded-full mix-blend-multiply filter blur-3xl animate-blob animation-delay-2000"></div>
      <div class="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-pink-400 rounded-full mix-blend-multiply filter blur-3xl animate-blob animation-delay-4000"></div>
    </div>

    <!-- Login Card -->
    <div class="relative w-full max-w-md">
      <!-- Floating Effect -->
      <div class="absolute inset-0 bg-gradient-to-r from-indigo-400 to-pink-400 shadow-2xl transform rotate-3 rounded-3xl blur-sm opacity-30"></div>

      <!-- Main Card -->
      <div class="relative bg-white bg-opacity-95 backdrop-blur-xl rounded-3xl shadow-2xl p-8 sm:p-12 space-y-8 transform hover:scale-[1.01] transition-transform duration-300">
        <!-- Logo & Header -->
        <div class="text-center">
          <!-- Animated Logo -->
          <div class="relative mx-auto h-24 w-24 mb-6">
            <div class="absolute inset-0 bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 rounded-2xl animate-pulse"></div>
            <div class="absolute inset-1 bg-white rounded-2xl flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-14 w-14 text-indigo-600" viewBox="0 0 24 24" fill="currentColor">
                <path d="M7 13c1.66 0 3-1.34 3-3S8.66 7 7 7s-3 1.34-3 3 1.34 3 3 3zm12-6h-6.18C12.4 5.84 11.3 5 10 5H7c-1.89 0-3.39 1.67-3 3.56C4.27 10.03 5.5 11 7 11v2H6c-1.1 0-2 .9-2 2v7h2v-2h12v2h2v-7c0-1.1-.9-2-2-2h-1V9c1.5 0 2.73-.97 3-2.44.39-1.89-1.11-3.56-3-3.56z"/>
              </svg>
            </div>
          </div>

          <!-- Title with Gradient -->
          <h2 class="text-4xl font-extrabold mb-2">
            <span class="bg-clip-text text-transparent bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600">
              เข้าสู่ระบบ
            </span>
          </h2>
          <p class="text-gray-600 text-lg font-medium">ระบบจัดการโรงแรม FlyingHotel</p>
          <div class="mt-2 flex items-center justify-center space-x-1">
            <div class="h-1 w-8 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full"></div>
            <div class="h-1 w-8 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full"></div>
          </div>
        </div>

        <!-- Login Form -->
        <form @submit.prevent="handleLogin" class="space-y-6">
          <!-- Username Input -->
          <div class="group">
            <label for="username" class="block text-sm font-semibold text-gray-700 mb-2 ml-1">
              ชื่อผู้ใช้
            </label>
            <div class="relative">
              <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <svg class="h-5 w-5 text-gray-400 group-focus-within:text-indigo-500 transition-colors" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
                </svg>
              </div>
              <input
                id="username"
                v-model="formValue.username"
                type="text"
                required
                :disabled="authStore.isLoading"
                class="w-full pl-12 pr-4 py-4 bg-gray-50 border-2 border-gray-200 rounded-2xl focus:outline-none focus:ring-4 focus:ring-indigo-200 focus:border-indigo-500 transition-all duration-300 text-gray-900 placeholder-gray-400 disabled:bg-gray-100 disabled:cursor-not-allowed"
                placeholder="กรอกชื่อผู้ใช้"
              />
            </div>
          </div>

          <!-- Password Input -->
          <div class="group">
            <label for="password" class="block text-sm font-semibold text-gray-700 mb-2 ml-1">
              รหัสผ่าน
            </label>
            <div class="relative">
              <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <svg class="h-5 w-5 text-gray-400 group-focus-within:text-indigo-500 transition-colors" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zM9 6c0-1.66 1.34-3 3-3s3 1.34 3 3v2H9V6zm9 14H6V10h12v10zm-6-3c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2z"/>
                </svg>
              </div>
              <input
                id="password"
                v-model="formValue.password"
                type="password"
                required
                :disabled="authStore.isLoading"
                class="w-full pl-12 pr-4 py-4 bg-gray-50 border-2 border-gray-200 rounded-2xl focus:outline-none focus:ring-4 focus:ring-indigo-200 focus:border-indigo-500 transition-all duration-300 text-gray-900 placeholder-gray-400 disabled:bg-gray-100 disabled:cursor-not-allowed"
                placeholder="กรอกรหัสผ่าน"
              />
            </div>
          </div>

          <!-- Error Alert -->
          <div v-if="authStore.error" class="relative overflow-hidden bg-gradient-to-r from-red-50 to-pink-50 border-l-4 border-red-500 p-4 rounded-2xl shadow-md animate-shake">
            <div class="flex items-start">
              <div class="flex-shrink-0">
                <svg class="h-6 w-6 text-red-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                </svg>
              </div>
              <div class="ml-3 flex-1">
                <p class="text-sm font-medium text-red-800">{{ authStore.error }}</p>
              </div>
              <button @click="authStore.clearError" type="button" class="ml-auto flex-shrink-0 text-red-500 hover:text-red-700 focus:outline-none transition-colors">
                <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
              </button>
            </div>
          </div>

          <!-- Submit Button -->
          <button
            type="submit"
            :disabled="authStore.isLoading"
            class="group relative w-full flex justify-center items-center py-4 px-6 text-lg font-bold text-white bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 rounded-2xl hover:from-indigo-700 hover:via-purple-700 hover:to-pink-700 focus:outline-none focus:ring-4 focus:ring-indigo-300 disabled:opacity-50 disabled:cursor-not-allowed shadow-xl hover:shadow-2xl transform hover:-translate-y-0.5 transition-all duration-300 overflow-hidden"
          >
            <!-- Button Shine Effect -->
            <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-0 group-hover:opacity-20 transform -skew-x-12 group-hover:translate-x-full transition-transform duration-1000"></div>

            <span v-if="!authStore.isLoading" class="relative flex items-center">
              <svg class="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
              </svg>
              เข้าสู่ระบบ
            </span>
            <span v-else class="relative flex items-center">
              <svg class="animate-spin -ml-1 mr-3 h-6 w-6 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              กำลังเข้าสู่ระบบ...
            </span>
          </button>
        </form>

        <!-- Footer -->
        <div class="pt-6 border-t border-gray-200">
          <div class="text-center space-y-2">
            <p class="text-sm font-medium text-gray-600">FlyingHotelApp v1.0.0</p>
            <p class="text-xs text-gray-500">© 2025 All rights reserved</p>
          </div>
        </div>
      </div>

      <!-- Decorative Elements -->
      <div class="absolute -bottom-6 -right-6 w-24 h-24 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-full opacity-50 blur-2xl"></div>
      <div class="absolute -top-6 -left-6 w-24 h-24 bg-gradient-to-br from-blue-400 to-indigo-500 rounded-full opacity-50 blur-2xl"></div>
    </div>

    <!-- Floating Particles -->
    <div class="absolute inset-0 overflow-hidden pointer-events-none">
      <div class="particle particle-1"></div>
      <div class="particle particle-2"></div>
      <div class="particle particle-3"></div>
      <div class="particle particle-4"></div>
      <div class="particle particle-5"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const formValue = ref({
  username: '',
  password: ''
})

async function handleLogin() {
  try {
    await authStore.login(formValue.value)
    const redirect = route.query.redirect as string || '/'
    router.push(redirect)
  } catch (error) {
    console.error('Login error:', error)
  }
}
</script>

<style scoped>
/* Blob Animation */
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

/* Shake Animation for Error */
@keyframes shake {
  0%, 100% {
    transform: translateX(0);
  }
  10%, 30%, 50%, 70%, 90% {
    transform: translateX(-5px);
  }
  20%, 40%, 60%, 80% {
    transform: translateX(5px);
  }
}

.animate-shake {
  animation: shake 0.5s ease-in-out;
}

/* Floating Particles */
.particle {
  position: absolute;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.8), rgba(255, 255, 255, 0.2));
  border-radius: 50%;
  pointer-events: none;
}

.particle-1 {
  width: 8px;
  height: 8px;
  top: 20%;
  left: 20%;
  animation: float 6s ease-in-out infinite;
}

.particle-2 {
  width: 12px;
  height: 12px;
  top: 60%;
  left: 80%;
  animation: float 8s ease-in-out infinite 1s;
}

.particle-3 {
  width: 6px;
  height: 6px;
  top: 80%;
  left: 30%;
  animation: float 7s ease-in-out infinite 2s;
}

.particle-4 {
  width: 10px;
  height: 10px;
  top: 40%;
  left: 70%;
  animation: float 9s ease-in-out infinite 1.5s;
}

.particle-5 {
  width: 8px;
  height: 8px;
  top: 10%;
  left: 90%;
  animation: float 6s ease-in-out infinite 3s;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0) translateX(0);
    opacity: 0;
  }
  10% {
    opacity: 1;
  }
  90% {
    opacity: 1;
  }
  50% {
    transform: translateY(-100px) translateX(50px);
  }
}

/* Smooth Transitions */
* {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

input:focus {
  transform: translateY(-2px);
}
</style>
