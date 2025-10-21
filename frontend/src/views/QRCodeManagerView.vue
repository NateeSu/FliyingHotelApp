<template>
  <div class="qrcode-manager-page p-6">
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900 mb-2">🎫 QR Code Manager</h1>
      <p class="text-gray-600">จัดการ QR codes สำหรับห้องพัก</p>
    </div>

    <!-- Controls -->
    <div class="flex gap-4 mb-6 flex-wrap">
      <n-button type="primary" @click="printAllQRCodes">
        <template #icon>
          <n-icon>
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
              <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V5h14v14zm-5.04-6.71l-2.75 3.54h2.86v2.5h3v-2.5h2.86l-2.75-3.54 1.96-2.36H17v-2.5h-3v2.5h-2.86l2.75 3.54z"/>
            </svg>
          </n-icon>
        </template>
        🖨️ พิมพ์ทั้งหมด
      </n-button>

      <n-button @click="downloadAllQRCodes">
        <template #icon>
          <n-icon>
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
              <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
            </svg>
          </n-icon>
        </template>
        ⬇️ ดาวน์โหลดทั้งหมด
      </n-button>

      <n-button @click="refreshQRCodes" :loading="loading">
        <template #icon>
          <n-icon>
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
              <path d="M7 7h10v3l4-4-4-4v3H5v6h2V7zm10 10H7v-3l-4 4 4 4v-3h12v-6h-2v4z"/>
            </svg>
          </n-icon>
        </template>
        🔄 รีเฟรช
      </n-button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center py-12">
      <n-spin size="large" description="กำลังโหลด QR codes..." />
    </div>

    <!-- QR Codes Grid -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="qr in qrCodes"
        :key="qr.room_id"
        class="bg-white rounded-lg shadow-lg p-6 flex flex-col items-center"
      >
        <!-- Room Info -->
        <div class="w-full mb-4 text-center">
          <h3 class="text-lg font-bold text-gray-900">ห้อง {{ qr.room_number || 'ไม่พบ' }}</h3>
          <p class="text-sm text-gray-500">ชั้น {{ qr.floor || '-' }}</p>
          <p class="text-xs text-gray-400 mt-1">ID: {{ qr.room_id }}</p>
        </div>

        <!-- QR Code Image -->
        <div class="bg-white p-4 border-2 border-gray-300 rounded mb-4">
          <img
            :src="qr.qr_code_base64"
            :alt="`QR Code for room ${qr.room_number}`"
            class="w-48 h-48"
          />
        </div>

        <!-- QR Code URL -->
        <div class="w-full mb-4 text-center">
          <p class="text-xs text-gray-500 break-all mb-2">{{ qr.qr_url }}</p>
          <n-button
            size="small"
            secondary
            @click="copyToClipboard(qr.qr_url)"
          >
            📋 คัดลอก URL
          </n-button>
        </div>

        <!-- Actions -->
        <div class="w-full flex gap-2">
          <n-button
            type="primary"
            block
            size="small"
            @click="downloadQRCode(qr)"
          >
            ⬇️ ดาวน์โหลด
          </n-button>
          <n-button
            secondary
            block
            size="small"
            @click="printQRCode(qr)"
          >
            🖨️ พิมพ์
          </n-button>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="!loading && qrCodes.length === 0" class="text-center py-12">
      <p class="text-lg text-gray-500">ไม่พบห้องพัก</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import apiClient from '@/api/client'

const message = useMessage()

// State
const qrCodes = ref<any[]>([])
const loading = ref(false)

// Load QR codes on mount
onMounted(() => {
  refreshQRCodes()
})

// Load all QR codes
async function refreshQRCodes() {
  try {
    loading.value = true
    const response = await apiClient.get('/public/qrcode/all-rooms')
    console.log('QR Codes Response:', response.data)
    console.log('First QR Code:', response.data[0])

    // Sort by floor then room_number for correct display order
    const sorted = response.data.sort((a, b) => {
      if (a.floor !== b.floor) {
        return a.floor - b.floor
      }
      return parseInt(a.room_number) - parseInt(b.room_number)
    })

    qrCodes.value = sorted
  } catch (error: any) {
    message.error('ไม่สามารถโหลด QR codes ได้')
    console.error('Error loading QR codes:', error)
  } finally {
    loading.value = false
  }
}

// Copy URL to clipboard
async function copyToClipboard(text: string) {
  try {
    await navigator.clipboard.writeText(text)
    message.success('คัดลอก URL เรียบร้อย')
  } catch {
    message.error('ไม่สามารถคัดลอก URL ได้')
  }
}

// Download single QR code
function downloadQRCode(qr: any) {
  try {
    const link = document.createElement('a')
    link.href = qr.qr_code_base64
    link.download = `QR-Room-${qr.room_number}.png`
    link.click()
    message.success(`ดาวน์โหลด QR code ห้อง ${qr.room_number} เรียบร้อย`)
  } catch (error) {
    message.error('ไม่สามารถดาวน์โหลด QR code ได้')
  }
}

// Download all QR codes as ZIP (simplified: download as individual files)
async function downloadAllQRCodes() {
  try {
    for (const qr of qrCodes.value) {
      // Add small delay between downloads
      await new Promise(resolve => setTimeout(resolve, 200))
      downloadQRCode(qr)
    }
    message.success('เริ่มดาวน์โหลด QR codes ทั้งหมด')
  } catch (error) {
    message.error('เกิดข้อผิดพลาดในการดาวน์โหลด')
  }
}

// Print QR code
function printQRCode(qr: any) {
  try {
    const printWindow = window.open('', '', 'height=400,width=400')
    if (printWindow) {
      printWindow.document.write(`
        <html>
          <head>
            <title>QR Code - ห้อง ${qr.room_number}</title>
            <style>
              body { text-align: center; font-family: Arial, sans-serif; }
              h1 { margin: 20px 0; }
              img { max-width: 300px; }
              p { margin-top: 20px; font-size: 14px; }
            </style>
          </head>
          <body>
            <h1>ห้อง ${qr.room_number}</h1>
            <img src="${qr.qr_code_base64}" />
            <p>สแกน QR code เพื่อสั่งของ</p>
          </body>
        </html>
      `)
      printWindow.document.close()
      setTimeout(() => {
        printWindow.print()
        printWindow.close()
      }, 250)
      message.success(`พิมพ์ QR code ห้อง ${qr.room_number} เรียบร้อย`)
    }
  } catch (error) {
    message.error('ไม่สามารถพิมพ์ QR code ได้')
  }
}

// Print all QR codes
function printAllQRCodes() {
  try {
    const printWindow = window.open('', '', 'height=600,width=800')
    if (printWindow) {
      let html = `
        <html>
          <head>
            <title>All QR Codes</title>
            <style>
              body { font-family: Arial, sans-serif; margin: 20px; }
              .page-break { page-break-after: always; }
              .qr-item {
                display: inline-block;
                text-align: center;
                margin: 20px;
                page-break-inside: avoid;
              }
              .qr-item h2 { margin: 10px 0; font-size: 18px; }
              .qr-item img { width: 200px; height: 200px; }
              .qr-item p { margin: 10px 0; font-size: 12px; }
            </style>
          </head>
          <body>
      `

      qrCodes.value.forEach((qr, index) => {
        if (index > 0 && index % 4 === 0) {
          html += '<div class="page-break"></div>'
        }
        html += `
          <div class="qr-item">
            <h2>ห้อง ${qr.room_number}</h2>
            <img src="${qr.qr_code_base64}" />
            <p>สแกน QR code เพื่อสั่งของ</p>
          </div>
        `
      })

      html += `
          </body>
        </html>
      `

      printWindow.document.write(html)
      printWindow.document.close()
      setTimeout(() => {
        printWindow.print()
        printWindow.close()
      }, 250)
      message.success('พิมพ์ QR codes ทั้งหมด')
    }
  } catch (error) {
    message.error('ไม่สามารถพิมพ์ QR codes ได้')
  }
}
</script>

<style scoped>
.qrcode-manager-page {
  min-height: 100vh;
  background-color: #f5f5f5;
}

/* Mobile optimization */
@media (max-width: 640px) {
  .qrcode-manager-page {
    padding: 1rem;
  }

  .grid {
    grid-template-columns: 1fr;
  }
}
</style>
