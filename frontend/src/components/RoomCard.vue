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
      <div class="status-badges">
        <div class="status-badge" :class="`status-${room.status}`">
          {{ statusLabel }}
        </div>
        <!-- Stay Type Badge (if occupied or overtime) -->
        <div v-if="(room.status === 'OCCUPIED' || room.status === 'OCCUPIED_OVERTIME') && room.stay_type" class="stay-type-badge" :class="`stay-${room.stay_type}`">
          {{ stayTypeLabel }}
        </div>
      </div>
    </div>

    <!-- Room Type -->
    <div class="room-type">
      <span class="type-name">{{ room.room_type_name }}</span>
    </div>

    <!-- Booking Info (if reserved) -->
    <div v-if="room.status === 'RESERVED' && room.booking_customer_name" class="booking-info">
      <div class="customer-info">
        <span class="label">ผู้จอง:</span>
        <span class="value">{{ room.booking_customer_name }}</span>
      </div>

      <div class="booking-dates">
        <div class="date-info">
          <span class="label">เข้าพัก:</span>
          <span class="value">{{ formatDate(room.booking_check_in_date) }}</span>
        </div>
        <div class="date-info">
          <span class="label">ออก:</span>
          <span class="value">{{ formatDate(room.booking_check_out_date) }}</span>
        </div>
      </div>

      <div v-if="room.booking_deposit_amount" class="deposit-info">
        <span class="label">มัดจำ:</span>
        <span class="value">฿{{ formatCurrency(room.booking_deposit_amount) }}</span>
      </div>
    </div>

    <!-- Check-in Info (if occupied or overtime) -->
    <div v-if="(room.status === 'OCCUPIED' || room.status === 'OCCUPIED_OVERTIME') && room.customer_name" class="check-in-info">
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

      <!-- Overtime Cutoff Warning (for OCCUPIED_OVERTIME status) -->
      <div v-if="room.status === 'OCCUPIED_OVERTIME'" class="overtime-cutoff-alert">
        <span class="icon">🔌</span>
        <span class="text">หมดเวลาเข้าพัก - ตัดไฟอัตโนมัติแล้ว</span>
      </div>
    </div>

    <!-- Room Notes -->
    <div v-if="room.notes" class="room-notes">
      <span class="label">หมายเหตุ:</span>
      <span class="value">{{ room.notes }}</span>
    </div>

    <!-- Breaker Status -->
    <div v-if="breaker" class="breaker-status">
      <div class="breaker-header">
        <span class="icon">⚡</span>
        <span class="label">เบรกเกอร์:</span>
      </div>
      <div class="breaker-state" :class="`state-${breakerStatusClass}`">
        <span class="status-dot"></span>
        <span class="status-text">{{ breakerStatusLabel }}</span>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="action-buttons" @click.stop>
      <!-- Check-In Button (available rooms) -->
      <button
        v-if="room.status === 'AVAILABLE'"
        class="action-btn check-in-btn"
        @click="handleCheckIn"
      >
        <span class="icon">✓</span>
        <span class="text">เช็คอิน</span>
      </button>

      <!-- Reserved Room Actions -->
      <template v-if="room.status === 'RESERVED'">
        <!-- Check-In from Booking Button -->
        <button
          class="action-btn check-in-btn"
          @click="handleCheckIn"
        >
          <span class="icon">✓</span>
          <span class="text">เช็คอิน</span>
        </button>

        <!-- Cancel Booking Button -->
        <button
          class="action-btn cancel-btn"
          @click="handleCancelBooking"
        >
          <span class="icon">✕</span>
          <span class="text">ยกเลิกจอง</span>
        </button>
      </template>

      <!-- Occupied Room Actions -->
      <template v-if="room.status === 'OCCUPIED'">
        <!-- Transfer Room Button -->
        <button
          class="action-btn transfer-btn"
          @click="handleTransfer"
        >
          <span class="icon">↔</span>
          <span class="text">ย้ายห้อง</span>
        </button>

        <!-- Check-Out Button -->
        <button
          class="action-btn check-out-btn"
          @click="handleCheckOut"
        >
          <span class="icon">→</span>
          <span class="text">เช็คเอาท์</span>
        </button>
      </template>

      <!-- Overtime Room Actions (only check-out) -->
      <template v-if="room.status === 'OCCUPIED_OVERTIME'">
        <!-- Check-Out Button (urgent) -->
        <button
          class="action-btn check-out-btn urgent"
          @click="handleCheckOut"
        >
          <span class="icon">→</span>
          <span class="text">เช็คเอาท์ (ด่วน)</span>
        </button>
      </template>

      <!-- Cleaning Room Actions -->
      <template v-if="room.status === 'CLEANING'">
        <!-- Complete Housekeeping Button -->
        <button
          class="action-btn complete-housekeeping-btn"
          @click="handleCompleteHousekeeping"
        >
          <span class="icon">✅</span>
          <span class="text">ปิดงานทำความสะอาด</span>
        </button>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { DashboardRoomCard } from '@/types/dashboard'
import type { Breaker } from '@/types/homeAssistant'
import dayjs from 'dayjs'
import 'dayjs/locale/th'

dayjs.locale('th')

// Props
interface Props {
  room: DashboardRoomCard
  breaker?: Breaker
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  click: [room: DashboardRoomCard]
  checkIn: [room: DashboardRoomCard]
  checkOut: [room: DashboardRoomCard]
  transfer: [room: DashboardRoomCard]
  cancelBooking: [room: DashboardRoomCard]
  completeHousekeeping: [room: DashboardRoomCard]
}>()

// Computed
const statusLabel = computed(() => {
  const statusMap: Record<string, string> = {
    AVAILABLE: 'ว่าง',
    OCCUPIED: 'มีผู้เข้าพัก',
    CLEANING: 'ทำความสะอาด',
    RESERVED: 'จอง',
    OUT_OF_SERVICE: 'ไม่พร้อมใช้งาน',
    OCCUPIED_OVERTIME: 'หมดเวลาเข้าพัก'
  }
  return statusMap[props.room.status] || props.room.status
})

const stayTypeLabel = computed(() => {
  if (!props.room.stay_type) return ''
  return props.room.stay_type === 'OVERNIGHT' ? 'ค้างคืน' : 'ชั่วคราว'
})

const breakerStatusLabel = computed(() => {
  if (!props.breaker) return null
  if (!props.breaker.is_available) return 'ไม่พร้อมใช้งาน'
  if (props.breaker.current_state === 'ON') return 'เปิด'
  if (props.breaker.current_state === 'OFF') return 'ปิด'
  return 'ไม่ทราบสถานะ'
})

const breakerStatusClass = computed(() => {
  if (!props.breaker) return null
  if (!props.breaker.is_available) return 'unavailable'
  if (props.breaker.current_state === 'ON') return 'on'
  if (props.breaker.current_state === 'OFF') return 'off'
  return 'unknown'
})

// Methods
function formatTime(time: string | null): string {
  if (!time) return '-'
  // Show both date and time in Thai format
  return dayjs(time).format('DD/MM/YYYY HH:mm')
}

function formatDate(date: string | null): string {
  if (!date) return '-'
  // Show date only in Thai format
  return dayjs(date).format('DD/MM/YYYY')
}

function formatCurrency(value: number | string): string {
  const num = typeof value === 'string' ? parseFloat(value) : value
  return num.toLocaleString('th-TH', { minimumFractionDigits: 2 })
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

function handleTransfer(): void {
  emit('transfer', props.room)
}

function handleCancelBooking(): void {
  emit('cancelBooking', props.room)
}

function handleCompleteHousekeeping(): void {
  emit('completeHousekeeping', props.room)
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
/* Status Color Variations - ตามมาตรฐาน PRD */

/* ห้องว่าง - เขียวสดใส */
.room-card.status-AVAILABLE {
  background: linear-gradient(135deg, #4CAF50 0%, #66BB6A 100%);
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
}

.room-card.status-AVAILABLE:hover {
  box-shadow: 0 8px 20px rgba(76, 175, 80, 0.4);
}

/* ห้องมีผู้พัก - แดงสด */
.room-card.status-OCCUPIED {
  background: linear-gradient(135deg, #F44336 0%, #E57373 100%);
  box-shadow: 0 4px 12px rgba(244, 67, 54, 0.3);
}

.room-card.status-OCCUPIED:hover {
  box-shadow: 0 8px 20px rgba(244, 67, 54, 0.4);
}

/* ห้องทำความสะอาด - เหลืองทอง */
.room-card.status-CLEANING {
  background: linear-gradient(135deg, #FFC107 0%, #FFD54F 100%);
  box-shadow: 0 4px 12px rgba(255, 193, 7, 0.3);
  color: #333 !important;
}

.room-card.status-CLEANING:hover {
  box-shadow: 0 8px 20px rgba(255, 193, 7, 0.4);
}

.room-card.status-CLEANING .status-badge,
.room-card.status-CLEANING .floor-badge {
  background: rgba(0, 0, 0, 0.15);
  color: #333;
}

/* ห้องจอง - ฟ้าสดใส */
.room-card.status-RESERVED {
  background: linear-gradient(135deg, #2196F3 0%, #64B5F6 100%);
  box-shadow: 0 4px 12px rgba(33, 150, 243, 0.3);
}

.room-card.status-RESERVED:hover {
  box-shadow: 0 8px 20px rgba(33, 150, 243, 0.4);
}

/* ห้องไม่พร้อมใช้ - เทา */
.room-card.status-OUT_OF_SERVICE {
  background: linear-gradient(135deg, #9E9E9E 0%, #BDBDBD 100%);
  box-shadow: 0 4px 12px rgba(158, 158, 158, 0.3);
  opacity: 0.85;
}

.room-card.status-OUT_OF_SERVICE:hover {
  box-shadow: 0 8px 20px rgba(158, 158, 158, 0.4);
}

/* ห้องหมดเวลา - แดงเข้มเตือนด่วน */
.room-card.status-OCCUPIED_OVERTIME {
  background: linear-gradient(135deg, #DC143C 0%, #8B0000 100%);
  box-shadow: 0 4px 12px rgba(220, 20, 60, 0.5);
  animation: pulse-overtime 2s infinite;
}

.room-card.status-OCCUPIED_OVERTIME:hover {
  box-shadow: 0 8px 20px rgba(220, 20, 60, 0.7);
}

@keyframes pulse-overtime {
  0%, 100% {
    box-shadow: 0 4px 12px rgba(220, 20, 60, 0.5);
  }
  50% {
    box-shadow: 0 0 25px rgba(220, 20, 60, 0.9), 0 0 40px rgba(220, 20, 60, 0.6);
  }
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
  align-items: flex-start;
  margin-bottom: 12px;
  gap: 8px;
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

.status-badges {
  display: flex;
  flex-direction: column;
  gap: 6px;
  align-items: flex-end;
}

.status-badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  background: rgba(255, 255, 255, 0.3);
  backdrop-filter: blur(10px);
  white-space: nowrap;
}

.stay-type-badge {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 700;
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(10px);
  white-space: nowrap;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

/* Stay Type Badge Colors */
.stay-type-badge.stay-OVERNIGHT {
  background: rgba(76, 175, 80, 0.4);
  border-color: rgba(76, 175, 80, 0.6);
  color: #fff;
}

.stay-type-badge.stay-TEMPORARY {
  background: rgba(33, 150, 243, 0.4);
  border-color: rgba(33, 150, 243, 0.6);
  color: #fff;
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

/* Booking Info (for reserved rooms) */
.booking-info {
  display: flex;
  flex-direction: column;
  gap: 10px;
  background: rgba(0, 0, 0, 0.1);
  padding: 12px;
  border-radius: 12px;
  margin-top: 12px;
}

.booking-dates {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.date-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
}

.deposit-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  padding-top: 8px;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
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

/* Overtime Cutoff Alert (for OCCUPIED_OVERTIME status) */
.overtime-cutoff-alert {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  background: linear-gradient(135deg, #DC143C 0%, #8B0000 100%);
  border: 2px solid rgba(255, 255, 255, 0.5);
  border-radius: 10px;
  font-size: 14px;
  font-weight: 700;
  animation: blink-urgent 1s infinite;
  box-shadow: 0 0 15px rgba(220, 20, 60, 0.7);
  color: white;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.5);
}

@keyframes blink-urgent {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.85;
    transform: scale(1.02);
  }
}

.overtime-cutoff-alert .icon {
  font-size: 18px;
  filter: drop-shadow(0 0 3px rgba(255, 255, 255, 0.8));
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

/* Breaker Status */
.breaker-status {
  margin-top: 12px;
  padding: 12px 14px;
  background: rgba(0, 0, 0, 0.25);
  border-radius: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.breaker-header {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.95);
}

.breaker-header .icon {
  font-size: 18px;
  filter: drop-shadow(0 0 4px rgba(255, 255, 255, 0.5));
}

.breaker-state {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  border-radius: 14px;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.3px;
}

.breaker-state .status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  animation: pulse-dot 2s infinite;
}

@keyframes pulse-dot {
  0%, 100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.3);
    opacity: 0.7;
  }
}

.breaker-state.state-on {
  background: linear-gradient(135deg, #00E676 0%, #00C853 100%);
  border: 2px solid #00E676;
  color: #fff;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
  box-shadow: 0 0 15px rgba(0, 230, 118, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.3);
}

.breaker-state.state-on .status-dot {
  background: #fff;
  box-shadow: 0 0 12px rgba(255, 255, 255, 0.9), 0 0 20px rgba(0, 230, 118, 0.8);
}

.breaker-state.state-off {
  background: linear-gradient(135deg, #FF5252 0%, #D32F2F 100%);
  border: 2px solid #FF5252;
  color: #fff;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
  box-shadow: 0 0 15px rgba(255, 82, 82, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.breaker-state.state-off .status-dot {
  background: #fff;
  box-shadow: 0 0 8px rgba(255, 255, 255, 0.8);
  animation: none;
}

.breaker-state.state-unavailable,
.breaker-state.state-unknown {
  background: linear-gradient(135deg, #757575 0%, #616161 100%);
  border: 2px solid #757575;
  color: #fff;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.breaker-state.state-unavailable .status-dot,
.breaker-state.state-unknown .status-dot {
  background: #BDBDBD;
  animation: none;
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

.check-out-btn.urgent {
  background: linear-gradient(135deg, #DC143C 0%, #8B0000 100%);
  animation: pulse-btn 1.5s infinite;
  box-shadow: 0 0 15px rgba(220, 20, 60, 0.6);
}

.check-out-btn.urgent:hover {
  background: linear-gradient(135deg, #8B0000 0%, #640000 100%);
  box-shadow: 0 0 20px rgba(220, 20, 60, 0.8);
}

@keyframes pulse-btn {
  0%, 100% {
    transform: translateY(0);
    box-shadow: 0 0 15px rgba(220, 20, 60, 0.6);
  }
  50% {
    transform: translateY(-3px);
    box-shadow: 0 0 25px rgba(220, 20, 60, 0.9);
  }
}

.transfer-btn {
  background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%);
  color: white;
}

.transfer-btn:hover {
  background: linear-gradient(135deg, #6d28d9 0%, #5b21b6 100%);
}

.cancel-btn {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
}

.cancel-btn:hover {
  background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
}

.complete-housekeeping-btn {
  background: linear-gradient(135deg, #8B4513 0%, #A0522D 100%);
  color: white;
  width: 100%;
  font-weight: 700;
  box-shadow: 0 2px 8px rgba(139, 69, 19, 0.4);
}

.complete-housekeeping-btn:hover {
  background: linear-gradient(135deg, #654321 0%, #8B4513 100%);
  box-shadow: 0 4px 12px rgba(139, 69, 19, 0.6);
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
