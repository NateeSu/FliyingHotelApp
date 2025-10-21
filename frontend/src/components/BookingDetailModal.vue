<template>
  <n-modal
    v-model:show="showModal"
    preset="card"
    title="รายละเอียดการจอง"
    class="booking-detail-modal"
    style="width: 90%; max-width: 700px"
  >
    <div v-if="booking" class="space-y-6">
      <!-- Status Badge -->
      <div class="flex items-center justify-between">
        <n-tag :type="getStatusType(booking.status)" size="large" round>
          {{ getStatusLabel(booking.status) }}
        </n-tag>
        <n-text depth="3" class="text-sm">
          รหัสการจอง: #{{ booking.id }}
        </n-text>
      </div>

      <!-- Customer Info -->
      <div class="info-section">
        <h3 class="section-title">ข้อมูลลูกค้า</h3>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <n-text depth="3" class="text-sm">ชื่อ-นามสกุล</n-text>
            <p class="font-semibold">{{ booking.customer_name }}</p>
          </div>
          <div>
            <n-text depth="3" class="text-sm">เบอร์โทร</n-text>
            <p class="font-semibold">{{ booking.customer_phone }}</p>
          </div>
        </div>
      </div>

      <!-- Room Info -->
      <div class="info-section">
        <h3 class="section-title">ข้อมูลห้อง</h3>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <n-text depth="3" class="text-sm">หมายเลขห้อง</n-text>
            <p class="font-semibold text-lg">{{ booking.room_number }}</p>
          </div>
          <div>
            <n-text depth="3" class="text-sm">ประเภทห้อง</n-text>
            <p class="font-semibold">{{ booking.room_type_name }}</p>
          </div>
        </div>
      </div>

      <!-- Booking Dates -->
      <div class="info-section">
        <h3 class="section-title">วันที่เข้าพัก</h3>
        <div class="grid grid-cols-3 gap-4">
          <div>
            <n-text depth="3" class="text-sm">เช็คอิน</n-text>
            <p class="font-semibold">{{ formatDate(booking.check_in_date) }}</p>
          </div>
          <div>
            <n-text depth="3" class="text-sm">เช็คเอาท์</n-text>
            <p class="font-semibold">{{ formatDate(booking.check_out_date) }}</p>
          </div>
          <div>
            <n-text depth="3" class="text-sm">จำนวนคืน</n-text>
            <p class="font-semibold">{{ booking.number_of_nights }} คืน</p>
          </div>
        </div>
      </div>

      <!-- Financial Details -->
      <div class="info-section">
        <h3 class="section-title">รายละเอียดการเงิน</h3>
        <div class="bg-gray-50 rounded-lg p-4 space-y-3">
          <div class="flex justify-between">
            <n-text depth="3">ยอดรวม</n-text>
            <n-text class="font-semibold">{{ formatCurrency(booking.total_amount) }} บาท</n-text>
          </div>
          <div class="flex justify-between">
            <n-text depth="3">เงินมัดจำ</n-text>
            <n-text class="font-semibold" :type="booking.deposit_amount > 0 ? 'success' : 'default'">
              {{ formatCurrency(booking.deposit_amount) }} บาท
            </n-text>
          </div>
          <n-divider style="margin: 8px 0" />
          <div class="flex justify-between text-lg">
            <n-text class="font-bold">ยอดคงเหลือ</n-text>
            <n-text class="font-bold" type="primary">
              {{ formatCurrency(booking.total_amount - booking.deposit_amount) }} บาท
            </n-text>
          </div>
        </div>
      </div>

      <!-- Notes -->
      <div v-if="booking.notes" class="info-section">
        <h3 class="section-title">หมายเหตุ</h3>
        <n-text class="whitespace-pre-wrap">{{ booking.notes }}</n-text>
      </div>

      <!-- Timeline -->
      <div class="info-section">
        <h3 class="section-title">Timeline</h3>
        <div class="space-y-2 text-sm">
          <div class="flex justify-between">
            <n-text depth="3">สร้างโดย</n-text>
            <n-text>{{ booking.creator_name }} - {{ formatDateTime(booking.created_at) }}</n-text>
          </div>
          <div class="flex justify-between">
            <n-text depth="3">แก้ไขล่าสุด</n-text>
            <n-text>{{ formatDateTime(booking.updated_at) }}</n-text>
          </div>
          <div v-if="booking.cancelled_at" class="flex justify-between">
            <n-text depth="3">ยกเลิกเมื่อ</n-text>
            <n-text type="error">{{ formatDateTime(booking.cancelled_at) }}</n-text>
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="flex justify-between">
        <div class="space-x-2">
          <n-button
            v-if="canEdit"
            type="primary"
            @click="handleEdit"
          >
            แก้ไข
          </n-button>
          <n-button
            v-if="canCancel"
            type="error"
            @click="showCancelConfirm = true"
          >
            ยกเลิกการจอง
          </n-button>
        </div>
        <n-button @click="handleClose">ปิด</n-button>
      </div>
    </template>
  </n-modal>

  <!-- Cancel Confirmation Modal -->
  <n-modal
    v-model:show="showCancelConfirm"
    preset="dialog"
    title="ยืนยันการยกเลิก"
    positive-text="ยืนยัน"
    negative-text="ยกเลิก"
    @positive-click="handleCancelBooking"
  >
    <div class="space-y-3">
      <p>คุณต้องการยกเลิกการจองนี้หรือไม่?</p>
      <n-alert v-if="booking && booking.deposit_amount > 0" type="warning" title="คำเตือน">
        เงินมัดจำ {{ formatCurrency(booking.deposit_amount) }} บาทจะไม่สามารถคืนได้
      </n-alert>
      <n-text depth="3">การดำเนินการนี้ไม่สามารถยกเลิกได้</n-text>
    </div>
  </n-modal>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { Booking } from '@/types/booking'

interface Props {
  show: boolean
  booking: Booking | null
}

const props = defineProps<Props>()
const emit = defineEmits<{
  (e: 'update:show', value: boolean): void
  (e: 'edit', booking: Booking): void
  (e: 'cancel', bookingId: number): void
  (e: 'close'): void
}>()

// State
const showCancelConfirm = ref(false)

// Computed
const showModal = computed({
  get: () => props.show,
  set: (value) => emit('update:show', value)
})

const canEdit = computed(() => {
  if (!props.booking) return false
  return ['pending', 'confirmed'].includes(props.booking.status)
})

const canCancel = computed(() => {
  if (!props.booking) return false
  return ['pending', 'confirmed'].includes(props.booking.status)
})

// Methods
function getStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    pending: 'รอยืนยัน',
    confirmed: 'ยืนยันแล้ว',
    checked_in: 'เช็คอินแล้ว',
    completed: 'เสร็จสิ้น',
    cancelled: 'ยกเลิกแล้ว'
  }
  return labels[status] || status
}

function getStatusType(status: string): any {
  const types: Record<string, any> = {
    pending: 'info',
    confirmed: 'success',
    checked_in: 'warning',
    completed: 'default',
    cancelled: 'error'
  }
  return types[status] || 'default'
}

function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleDateString('th-TH', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

function formatDateTime(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleDateString('th-TH', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function formatCurrency(value: number): string {
  return new Intl.NumberFormat('th-TH', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value)
}

function handleEdit() {
  if (props.booking) {
    emit('edit', props.booking)
  }
}

function handleCancelBooking() {
  if (props.booking) {
    emit('cancel', props.booking.id)
  }
  showCancelConfirm.value = false
}

function handleClose() {
  emit('close')
}
</script>

<style scoped>
.info-section {
  padding-bottom: 1rem;
  border-bottom: 1px solid #f0f0f0;
}

.info-section:last-child {
  border-bottom: none;
}

.section-title {
  font-size: 1rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 0.75rem;
}

.booking-detail-modal :deep(.n-card__content) {
  padding: 1.5rem;
}
</style>
