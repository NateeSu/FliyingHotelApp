<template>
  <div class="login-container">
    <n-card class="login-card" :bordered="false">
      <div class="login-header">
        <div class="logo-container">
          <n-icon size="70" color="#3338A0">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
              <path fill="currentColor" d="M7 13c1.66 0 3-1.34 3-3S8.66 7 7 7s-3 1.34-3 3 1.34 3 3 3zm12-6h-6.18C12.4 5.84 11.3 5 10 5H7c-1.89 0-3.39 1.67-3 3.56C4.27 10.03 5.5 11 7 11v2H6c-1.1 0-2 .9-2 2v7h2v-2h12v2h2v-7c0-1.1-.9-2-2-2h-1V9c1.5 0 2.73-.97 3-2.44.39-1.89-1.11-3.56-3-3.56z"/>
            </svg>
          </n-icon>
        </div>
        <h1>เข้าสู่ระบบ</h1>
        <p>ระบบจัดการโรงแรม</p>
      </div>

      <n-form
        ref="formRef"
        :model="formValue"
        :rules="rules"
        size="large"
        :show-require-mark="false"
        @keyup.enter="handleLogin"
      >
        <n-space vertical :size="24">
          <n-form-item path="username" label="ชื่อผู้ใช้">
            <n-input
              v-model:value="formValue.username"
              placeholder="กรอกชื่อผู้ใช้"
              :disabled="authStore.isLoading"
            >
              <template #prefix>
                <n-icon>
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                    <path fill="currentColor" d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
                  </svg>
                </n-icon>
              </template>
            </n-input>
          </n-form-item>

          <n-form-item path="password" label="รหัสผ่าน">
            <n-input
              v-model:value="formValue.password"
              type="password"
              show-password-on="click"
              placeholder="กรอกรหัสผ่าน"
              :disabled="authStore.isLoading"
            >
              <template #prefix>
                <n-icon>
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                    <path fill="currentColor" d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zM9 6c0-1.66 1.34-3 3-3s3 1.34 3 3v2H9V6zm9 14H6V10h12v10zm-6-3c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2z"/>
                  </svg>
                </n-icon>
              </template>
            </n-input>
          </n-form-item>

          <n-form-item>
            <n-button
              type="primary"
              block
              size="large"
              :loading="authStore.isLoading"
              @click="handleLogin"
              style="height: 48px; font-size: 16px; font-weight: 600;"
            >
              เข้าสู่ระบบ
            </n-button>
          </n-form-item>
        </n-space>
      </n-form>

      <n-alert
        v-if="authStore.error"
        type="error"
        :title="authStore.error"
        closable
        @close="authStore.clearError"
        style="margin-top: 24px; padding: 16px; border-radius: 12px;"
      />
    </n-card>

    <div class="login-footer">
      <p>FlyingHotelApp v1.0.0</p>
      <p>© 2025 All rights reserved</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useMessage } from 'naive-ui'
import type { FormInst, FormRules } from 'naive-ui'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const message = useMessage()

const formRef = ref<FormInst | null>(null)
const formValue = ref({
  username: '',
  password: ''
})

const rules: FormRules = {
  username: [
    {
      required: true,
      message: 'กรุณากรอกชื่อผู้ใช้',
      trigger: 'blur'
    }
  ],
  password: [
    {
      required: true,
      message: 'กรุณากรอกรหัสผ่าน',
      trigger: 'blur'
    }
  ]
}

async function handleLogin() {
  try {
    await formRef.value?.validate()
    await authStore.login(formValue.value)

    message.success('เข้าสู่ระบบสำเร็จ')

    // Redirect to the page user was trying to access, or home
    const redirect = route.query.redirect as string || '/'
    router.push(redirect)
  } catch (error) {
    // Error is already set in store
    console.error('Login error:', error)
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #3338A0 0%, #1f2260 100%);
  padding: 20px;
  position: relative;
}

.login-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background:
    radial-gradient(circle at 20% 50%, rgba(252, 198, 29, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 80% 80%, rgba(197, 149, 96, 0.1) 0%, transparent 50%);
  pointer-events: none;
}

.login-card {
  width: 100%;
  max-width: 460px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  border-radius: 24px;
  padding: 48px;
  background: #F7F7F7;
  position: relative;
  z-index: 1;
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.logo-container {
  display: inline-block;
  padding: 24px;
  background: linear-gradient(135deg, #FCC61D 0%, #C59560 100%);
  border-radius: 50%;
  margin-bottom: 20px;
  box-shadow: 0 8px 24px rgba(252, 198, 29, 0.3);
}

.login-header h1 {
  margin: 20px 0 12px;
  font-size: 36px;
  font-weight: 700;
  background: linear-gradient(135deg, #3338A0 0%, #C59560 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.login-header p {
  margin: 0;
  color: #666;
  font-size: 17px;
  font-weight: 500;
  line-height: 1.5;
}

.login-footer {
  margin-top: 32px;
  text-align: center;
  color: #FCC61D;
  font-size: 14px;
  position: relative;
  z-index: 1;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.login-footer p {
  margin: 6px 0;
  opacity: 0.95;
  font-weight: 500;
  line-height: 1.6;
}

:deep(.n-form-item) {
  margin-bottom: 0;
}

:deep(.n-form-item-label) {
  font-size: 15px;
  font-weight: 600;
  color: #3338A0 !important;
  margin-bottom: 8px;
}

:deep(.n-input) {
  font-size: 15px;
  height: 48px;
}

:deep(.n-input__input) {
  height: 48px;
}

@media (max-width: 480px) {
  .login-card {
    padding: 32px 24px;
    max-width: 100%;
  }

  .login-header {
    margin-bottom: 32px;
  }

  .login-header h1 {
    font-size: 28px;
  }

  .login-header p {
    font-size: 15px;
  }

  .logo-container {
    padding: 20px;
  }

  :deep(.n-input) {
    height: 44px;
  }

  :deep(.n-input__input) {
    height: 44px;
  }
}
</style>
