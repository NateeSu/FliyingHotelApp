<template>
  <div
    class="room-card"
    :class="[
      `status-${room.status}`,
      { 'is-overtime': room.is_overtime }
    ]"
    @click="handleClick"
  >
    <!-- Room Header -->
    <div class="room-header">
      <div class="room-number">
        <span class="floor-badge">{{ room.floor }}F</span>
        <span class="number">{{ room.room_number }}</span>
      </div>
      <div class="status-badge" :class="`status-${room.status}`">
        {{ statusLabel }}
      </div>
    </div>

    <!-- Room Type -->
    <div class="room-type">
      <span class="type-name">{{ room.room_type_name }}</span>
    </div>

    <!-- Check-in Info (if occupied) -->
    <div v-if="room.status === 'occupied' && room.customer_name" class="check-in-info">
      <div class="customer-info">
        <span class="label">ผู้เข้าพัก:</span>
        <span class="value">{{ room.customer_name }}</span>
      </div>

      <div class="stay-type">
        <span class="badge" :class="`stay-${room.stay_type}`">
          {{ stayTypeLabel }}
        </span>
      </div>

      <div class="time-info">
        <div class="check-in-time">
          <span class="label">เข้าพัก:</span>
          <span class="value">{{ formatTime(room.check_in_time) }}</span>
        </div>
        <div class="expected-checkout">
          <span class="label">คาดว่าออก:</span>
          <span class="value">{{ formatTime(room.expected_check_out_time) }}</span>
        </div>
      </div>

      <!-- Overtime Alert -->
      <div v-if="room.is_overtime" class="overtime-alert">
        <span class="icon">⚠️</span>
        <span class="text">เกินเวลา {{ room.overtime_minutes }} นาที</span>
      </div>
    </div>

    <!-- Room Notes -->
    <div v-if="room.notes" class="room-notes">
      <span class="label">หมายเหตุ:</span>
      <span class="value">{{ room.notes }}</span>
    </div>

    <!-- Action Buttons -->
    <div class="action-buttons" @click.stop>
      <!-- Check-In Button (available rooms) -->
      <button
        v-if="room.status === 'available'"
        class="action-btn check-in-btn"
        @click="handleCheckIn"
      >
        <span class="icon">✓</span>
        <span class="text">เช็คอิน</span>
      </button>

      <!-- Check-Out Button (occupied rooms) -->
      <button
        v-if="room.status === 'occupied'"
        class="action-btn check-out-btn"
        @click="handleCheckOut"
      >
        <span class="icon">→</span>
        <span class="text">เช็คเอาท์</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { DashboardRoomCard } from '@/types/dashboard'
import dayjs from 'dayjs'
import 'dayjs/locale/th'

dayjs.locale('th')

// Props
interface Props {
  room: DashboardRoomCard
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  click: [room: DashboardRoomCard]
  checkIn: [room: DashboardRoomCard]
  checkOut: [room: DashboardRoomCard]
}>()

// Computed
const statusLabel = computed(() => {
  const statusMap: Record<string, string> = {
    available: 'ว่าง',
    occupied: 'มีผู้เข้าพัก',
    cleaning: 'ทำความสะอาด',
    reserved: 'จอง',
    out_of_service: 'ไม่พร้อมใช้งาน'
  }
  return statusMap[props.room.status] || props.room.status
})

const stayTypeLabel = computed(() => {
  if (!props.room.stay_type) return ''
  return props.room.stay_type === 'overnight' ? 'ค้างคืน' : 'ชั่วคราว'
})

// Methods
function formatTime(time: string | null): string {
  if (!time) return '-'
  // Show both date and time in Thai format
  return dayjs(time).format('DD/MM/YYYY HH:mm')
}

function handleClick(): void {
  emit('click', props.room)
}

function handleCheckIn(): void {
  emit('checkIn', props.room)
}

function handleCheckOut(): void {
  emit('checkOut', props.room)
}
</script>

<style scoped>
.room-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  color: white;
  position: relative;
  overflow: hidden;
}

.room-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.1);
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
}

.room-card:hover::before {
  opacity: 1;
}

.room-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 12px rgba(0, 0, 0, 0.15);
}

/* Status Color Variations */
.room-card.status-available {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
}

.room-card.status-occupied {
  background: linear-gradient(135deg, #ee0979 0%, #ff6a00 100%);
}

.room-card.status-cleaning {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.room-card.status-reserved {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.room-card.status-out_of_service {
  background: linear-gradient(135deg, #606c88 0%, #3f4c6b 100%);
}

.room-card.is-overtime {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  }
  50% {
    box-shadow: 0 0 20px rgba(255, 193, 7, 0.8);
  }
}

/* Room Header */
.room-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.room-number {
  display: flex;
  align-items: center;
  gap: 8px;
}

.floor-badge {
  background: rgba(255, 255, 255, 0.2);
  padding: 4px 8px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
}

.number {
  font-size: 28px;
  font-weight: 700;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
}

.status-badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  background: rgba(255, 255, 255, 0.3);
  backdrop-filter: blur(10px);
}

/* Room Type */
.room-type {
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.type-name {
  font-size: 14px;
  font-weight: 500;
  opacity: 0.9;
}

/* Check-in Info */
.check-in-info {
  display: flex;
  flex-direction: column;
  gap: 10px;
  background: rgba(0, 0, 0, 0.1);
  padding: 12px;
  border-radius: 12px;
  margin-top: 12px;
}

.customer-info,
.time-info > div {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
}

.label {
  opacity: 0.8;
  font-weight: 500;
}

.value {
  font-weight: 600;
}

.stay-type {
  display: flex;
  justify-content: flex-start;
}

.stay-type .badge {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  background: rgba(255, 255, 255, 0.2);
}

.stay-type .badge.stay-overnight {
  background: rgba(76, 175, 80, 0.3);
}

.stay-type .badge.stay-temporary {
  background: rgba(33, 150, 243, 0.3);
}

.time-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

/* Overtime Alert */
.overtime-alert {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: rgba(255, 193, 7, 0.3);
  border: 2px solid rgba(255, 193, 7, 0.5);
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  animation: blink 1.5s infinite;
}

@keyframes blink {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

.overtime-alert .icon {
  font-size: 16px;
}

/* Room Notes */
.room-notes {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
  font-size: 12px;
  opacity: 0.8;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

/* Action Buttons */
.action-buttons {
  margin-top: 16px;
  display: flex;
  gap: 8px;
}

.action-btn {
  flex: 1;
  padding: 12px 16px;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  background: rgba(255, 255, 255, 0.9);
  color: #111827;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.action-btn .icon {
  font-size: 16px;
}

.check-in-btn {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
}

.check-in-btn:hover {
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
}

.check-out-btn {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  color: white;
}

.check-out-btn:hover {
  background: linear-gradient(135deg, #d97706 0%, #b45309 100%);
}

/* Responsive */
@media (max-width: 768px) {
  .room-card {
    padding: 16px;
  }

  .number {
    font-size: 24px;
  }

  .check-in-info {
    padding: 10px;
  }

  .action-btn {
    padding: 10px 12px;
    font-size: 13px;
  }
}
</style>
