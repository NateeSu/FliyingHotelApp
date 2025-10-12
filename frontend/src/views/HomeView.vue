<template>
  <n-space vertical align="center" justify="center" style="min-height: 100vh; padding: 20px;">
    <n-h1>ยินดีต้อนรับสู่ FlyingHotelApp</n-h1>
    <n-text>ระบบบริหารจัดการโรงแรมขนาดเล็ก</n-text>
    <n-card title="สถานะระบบ" style="max-width: 600px;">
      <n-space vertical>
        <n-alert type="success" title="ระบบทำงานปกติ">
          Frontend เชื่อมต่อสำเร็จ
        </n-alert>
        <n-button type="primary" @click="checkBackend">
          ตรวจสอบการเชื่อมต่อ Backend
        </n-button>
        <n-text v-if="backendStatus" :type="backendStatus.type">
          {{ backendStatus.message }}
        </n-text>
      </n-space>
    </n-card>
  </n-space>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { NSpace, NH1, NText, NCard, NAlert, NButton } from 'naive-ui'
import axios from 'axios'

const backendStatus = ref<{ type: 'success' | 'error', message: string } | null>(null)

const checkBackend = async () => {
  try {
    const response = await axios.get('http://localhost:8000/health')
    backendStatus.value = {
      type: 'success',
      message: `✓ Backend เชื่อมต่อสำเร็จ - สถานะ: ${response.data.status}`
    }
  } catch (error) {
    backendStatus.value = {
      type: 'error',
      message: '✗ ไม่สามารถเชื่อมต่อ Backend ได้'
    }
  }
}
</script>
