<template>
  <div v-if="show" class="modal-overlay" @click.self="handleClose">
    <div class="modal-container">
      <div class="modal-header">
        <h2>เช็คอินห้อง {{ roomNumber }}</h2>
        <button class="close-btn" @click="handleClose">×</button>
      </div>

      <!-- Booking Info Alert -->
      <div v-if="bookingId" class="booking-alert">
        <div class="alert-icon">📋</div>
        <div class="alert-content">
          <div class="alert-title">เช็คอินจากการจอง</div>
          <div class="alert-message">
            ข้อมูลถูกนำมาจากการจอง #{{ bookingId }} |
            เงินมัดจำ: ฿{{ bookingDepositAmount?.toLocaleString('th-TH', { minimumFractionDigits: 2 }) || '0.00' }}
            (จะหักออกจากยอดรวม)
          </div>
        </div>
      </div>

      <div class="modal-body">
        <!-- Step 1: Customer Information -->
        <section class="form-section">
          <h3>ข้อมูลลูกค้า</h3>

          <!-- Customer Form Fields -->
          <div class="form-row">
            <div class="form-group">
              <label>ชื่อ-นามสกุล <span class="required">*</span></label>
              <input
                v-model="formData.customer.full_name"
                type="text"
                class="form-input"
                placeholder="ชื่อ-นามสกุล"
                required
              />
            </div>
            <div class="form-group">
              <label>เบอร์โทรศัพท์ <span class="required">*</span></label>
              <input
                v-model="formData.customer.phone_number"
                type="tel"
                class="form-input"
                placeholder="0812345678"
                inputmode="numeric"
                pattern="[0-9]*"
                @input="sanitizePhoneNumber"
                required
              />
              <div v-if="phoneNumberError" class="error-message">{{ phoneNumberError }}</div>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>อีเมล</label>
              <input
                v-model="formData.customer.email"
                type="text"
                class="form-input"
                placeholder="email@example.com (ไม่จำเป็น)"
                inputmode="email"
              />
            </div>
            <div class="form-group">
              <label>เลขบัตรประชาชน</label>
              <input
                v-model="formData.customer.id_card_number"
                type="text"
                class="form-input"
                placeholder="1234567890123"
              />
            </div>
          </div>
        </section>

        <!-- Step 2: Check-In Details -->
        <section class="form-section">
          <h3>รายละเอียดการเช็คอิน</h3>

          <!-- Stay Type Selection -->
          <div class="form-group">
            <label>ประเภทการเข้าพัก <span class="required">*</span></label>
            <div class="stay-type-selector">
              <button
                :class="['stay-type-btn', { active: formData.checkIn.stay_type === 'overnight' }]"
                @click="formData.checkIn.stay_type = 'overnight'"
              >
                <div class="icon">🌙</div>
                <div class="label">ค้างคืน</div>
              </button>
              <button
                :class="['stay-type-btn', { active: formData.checkIn.stay_type === 'temporary' }]"
                @click="formData.checkIn.stay_type = 'temporary'"
              >
                <div class="icon">⏱️</div>
                <div class="label">ชั่วคราว (3 ชม.)</div>
              </button>
            </div>
          </div>

          <!-- Number of Nights (for overnight) -->
          <div v-if="formData.checkIn.stay_type === 'overnight'" class="form-row">
            <div class="form-group">
              <label>จำนวนคืน <span class="required">*</span></label>
              <input
                v-model.number="formData.checkIn.number_of_nights"
                type="number"
                class="form-input"
                min="1"
                placeholder="1"
              />
            </div>
            <div class="form-group">
              <label>จำนวนผู้เข้าพัก</label>
              <input
                v-model.number="formData.checkIn.number_of_guests"
                type="number"
                class="form-input"
                min="1"
                placeholder="1"
              />
            </div>
          </div>

          <!-- Number of Guests (for temporary) -->
          <div v-else class="form-group">
            <label>จำนวนผู้เข้าพัก</label>
            <input
              v-model.number="formData.checkIn.number_of_guests"
              type="number"
              class="form-input"
              min="1"
              placeholder="1"
            />
          </div>

          <!-- Payment Method -->
          <div class="form-group">
            <label>วิธีชำระเงิน <span class="required">*</span></label>
            <div class="payment-method-selector">
              <button
                :class="['payment-btn', { active: formData.checkIn.payment_method === 'cash' }]"
                @click="formData.checkIn.payment_method = 'cash'"
              >
                💵 เงินสด
              </button>
              <button
                :class="['payment-btn', { active: formData.checkIn.payment_method === 'transfer' }]"
                @click="formData.checkIn.payment_method = 'transfer'"
              >
                🏦 โอนเงิน
              </button>
              <button
                :class="['payment-btn', { active: formData.checkIn.payment_method === 'credit_card' }]"
                @click="formData.checkIn.payment_method = 'credit_card'"
              >
                💳 บัตรเครดิต
              </button>
            </div>
          </div>

          <!-- Notes -->
          <div class="form-group">
            <label>หมายเหตุ</label>
            <textarea
              v-model="formData.checkIn.notes"
              class="form-input"
              rows="3"
              placeholder="บันทึกเพิ่มเติม..."
            ></textarea>
          </div>
        </section>

        <!-- Calculated Summary -->
        <section class="summary-section">
          <h3>สรุปค่าใช้จ่าย</h3>
          <div class="summary-row">
            <span>ค่าห้อง:</span>
            <span class="amount">{{ calculatedAmount }} บาท</span>
          </div>
          <div v-if="formData.checkIn.stay_type === 'overnight'" class="summary-detail">
            {{ formData.checkIn.number_of_nights || 1 }} คืน × {{ ratePerNight }} บาท
          </div>
          <div v-else class="summary-detail">
            1 รอบ (3 ชั่วโมง)
          </div>
        </section>
      </div>

      <div class="modal-footer">
        <button class="btn btn-cancel" @click="handleClose" :disabled="loading">
          ยกเลิก
        </button>
        <button class="btn btn-primary" @click="handleSubmit" :disabled="loading || !isFormValid">
          <span v-if="loading">กำลังเช็คอิน...</span>
          <span v-else>เช็คอิน</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useToast } from 'vue-toastification'
import { checkInApi, type CheckInCreateData, type CustomerData } from '@/api/check-ins'
import { customerApi, type CustomerSearchResult } from '@/api/customers'
import dayjs from 'dayjs'

const toast = useToast()

interface Props {
  show: boolean
  roomId: number
  roomNumber: string
  ratePerNight?: number // For overnight
  ratePerSession?: number // For temporary
  // Booking data (Phase 7) - for prefilling when checking in from booking
  bookingId?: number | null
  bookingCustomerName?: string | null
  bookingCustomerPhone?: string | null
  bookingCheckInDate?: string | null
  bookingCheckOutDate?: string | null
  bookingDepositAmount?: number | null
}

const props = defineProps<Props>()

const emit = defineEmits<{
  close: []
  success: [checkInId: number]
}>()

// Form data
const formData = ref({
  customer: {
    full_name: props.bookingCustomerName || '',
    phone_number: props.bookingCustomerPhone || '',
    email: '',
    id_card_number: '',
    address: '',
    notes: ''
  } as CustomerData,
  checkIn: {
    room_id: props.roomId,
    stay_type: 'overnight' as 'overnight' | 'temporary',
    number_of_nights: 1,
    number_of_guests: 1,
    payment_method: 'cash' as 'cash' | 'transfer' | 'credit_card',
    notes: '',
    booking_id: props.bookingId || undefined
  } as CheckInCreateData
})

// Phone number validation
const phoneNumberError = ref('')

const sanitizePhoneNumber = () => {
  const phone = formData.value.customer.phone_number
  const phoneDigitsOnly = phone.replace(/\D/g, '')

  if (phoneDigitsOnly !== phone) {
    formData.value.customer.phone_number = phoneDigitsOnly
  }

  // Validate phone number
  if (phoneDigitsOnly && phoneDigitsOnly.length < 9) {
    phoneNumberError.value = 'เบอร์โทรศัพท์ต้องมีอย่างน้อย 9 หลัก'
  } else if (phoneDigitsOnly && phoneDigitsOnly.length > 15) {
    formData.value.customer.phone_number = phoneDigitsOnly.slice(0, 15)
    phoneNumberError.value = 'เบอร์โทรศัพท์ไม่ต้องเกิน 15 หลัก'
  } else {
    phoneNumberError.value = ''
  }
}

// Calculated amount
const calculatedAmount = computed(() => {
  if (formData.value.checkIn.stay_type === 'overnight') {
    const nights = formData.value.checkIn.number_of_nights || 1
    const rate = props.ratePerNight || 0
    return nights * rate
  } else {
    return props.ratePerSession || 0
  }
})

// Form validation
const isFormValid = computed(() => {
  const customer = formData.value.customer
  const checkIn = formData.value.checkIn

  if (!customer.full_name || !customer.phone_number) return false
  if (!checkIn.payment_method) return false
  if (checkIn.stay_type === 'overnight' && (!checkIn.number_of_nights || checkIn.number_of_nights < 1)) return false

  return true
})

// Submit
const loading = ref(false)

const handleSubmit = async () => {
  if (!isFormValid.value) return

  loading.value = true
  try {
    // Ensure room_id is set
    formData.value.checkIn.room_id = props.roomId

    // Prepare customer data - convert empty email to undefined
    const customerData = {
      ...formData.value.customer,
      email: formData.value.customer.email?.trim() || undefined,
      id_card_number: formData.value.customer.id_card_number?.trim() || undefined,
      address: formData.value.customer.address?.trim() || undefined,
      notes: formData.value.customer.notes?.trim() || undefined
    }

    const response = await checkInApi.createCheckIn(
      formData.value.checkIn,
      customerData
    )

    // Show success toast
    toast.success('✅ เช็คอินสำเร็จ!')

    // Emit success event (don't wait for it)
    try {
      emit('success', response.id)
    } catch (emitError) {
      console.error('Error in success handler:', emitError)
    }

    // Reset loading and close modal immediately
    loading.value = false
    emit('close')
    resetForm()
  } catch (error: any) {
    console.error('Check-in error:', error)
    const errorMessage = error.response?.data?.detail || 'เกิดข้อผิดพลาดในการเช็คอิน'
    toast.error(errorMessage)
    loading.value = false
  }
}

const handleClose = () => {
  if (!loading.value) {
    emit('close')
    resetForm()
  }
}

const resetForm = () => {
  formData.value = {
    customer: {
      full_name: '',
      phone_number: '',
      email: '',
      id_card_number: '',
      address: '',
      notes: ''
    },
    checkIn: {
      room_id: props.roomId,
      stay_type: 'overnight',
      number_of_nights: 1,
      number_of_guests: 1,
      payment_method: 'cash',
      notes: ''
    }
  }
  phoneNumberError.value = ''
}

// Prefill form data from booking when modal opens
onMounted(() => {
  prefillFromBooking()
})

// Watch for show prop to prefill when modal opens
watch(() => props.show, (isShowing) => {
  if (isShowing) {
    prefillFromBooking()
  }
})

const prefillFromBooking = () => {
  if (props.bookingId && props.bookingCustomerName && props.bookingCustomerPhone) {
    // Prefill customer data
    formData.value.customer.full_name = props.bookingCustomerName
    formData.value.customer.phone_number = props.bookingCustomerPhone

    // Calculate number of nights from booking dates
    if (props.bookingCheckInDate && props.bookingCheckOutDate) {
      const checkInDate = dayjs(props.bookingCheckInDate)
      const checkOutDate = dayjs(props.bookingCheckOutDate)
      const nights = checkOutDate.diff(checkInDate, 'day')

      formData.value.checkIn.number_of_nights = nights > 0 ? nights : 1
      formData.value.checkIn.stay_type = 'overnight'
    }

    // Set booking_id for linking
    formData.value.checkIn.booking_id = props.bookingId

    // Show toast to inform user
    toast.info(`📋 นำข้อมูลจากการจองมาใส่ให้แล้ว (เงินมัดจำ: ฿${props.bookingDepositAmount?.toLocaleString('th-TH', { minimumFractionDigits: 2 }) || '0.00'})`)
  }
}

// Watch for room changes
watch(() => props.roomId, (newRoomId) => {
  formData.value.checkIn.room_id = newRoomId
})
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.modal-container {
  background: white;
  border-radius: 16px;
  width: 90%;
  max-width: 700px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.modal-header {
  padding: 24px 32px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #111827;
}

.close-btn {
  background: none;
  border: none;
  font-size: 32px;
  color: #6b7280;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  transition: all 0.2s;
}

.close-btn:hover {
  background: #f3f4f6;
  color: #111827;
}

/* Booking Alert */
.booking-alert {
  display: flex;
  gap: 12px;
  padding: 16px 32px;
  background: linear-gradient(135deg, #e0f2fe 0%, #dbeafe 100%);
  border-bottom: 2px solid #3b82f6;
  align-items: flex-start;
}

.alert-icon {
  font-size: 24px;
  flex-shrink: 0;
}

.alert-content {
  flex: 1;
}

.alert-title {
  font-size: 14px;
  font-weight: 600;
  color: #1e40af;
  margin-bottom: 4px;
}

.alert-message {
  font-size: 13px;
  color: #1e3a8a;
  line-height: 1.4;
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 24px 32px;
}

.form-section {
  margin-bottom: 32px;
}

.form-section h3 {
  margin: 0 0 20px;
  font-size: 18px;
  font-weight: 600;
  color: #374151;
  padding-bottom: 12px;
  border-bottom: 2px solid #e5e7eb;
}

.form-group {
  margin-bottom: 20px;
  position: relative;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #374151;
  font-size: 14px;
}

.required {
  color: #ef4444;
}

.form-input {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 15px;
  transition: all 0.2s;
  font-family: inherit;
}

.form-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-input::placeholder {
  color: #9ca3af;
}

textarea.form-input {
  resize: vertical;
  min-height: 80px;
}

.error-message {
  color: #ef4444;
  font-size: 13px;
  margin-top: 6px;
  display: block;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}


/* Stay Type Selector */
.stay-type-selector {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.stay-type-btn {
  padding: 16px;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  background: white;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.stay-type-btn:hover {
  border-color: #3b82f6;
  background: #eff6ff;
}

.stay-type-btn.active {
  border-color: #3b82f6;
  background: #3b82f6;
  color: white;
}

.stay-type-btn .icon {
  font-size: 32px;
}

.stay-type-btn .label {
  font-weight: 600;
  font-size: 14px;
}

/* Payment Method Selector */
.payment-method-selector {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.payment-btn {
  padding: 12px 16px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  background: white;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 14px;
  font-weight: 500;
}

.payment-btn:hover {
  border-color: #10b981;
  background: #ecfdf5;
}

.payment-btn.active {
  border-color: #10b981;
  background: #10b981;
  color: white;
}

/* Summary Section */
.summary-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  border-radius: 12px;
  color: white;
}

.summary-section h3 {
  margin: 0 0 16px;
  font-size: 16px;
  font-weight: 600;
  border: none;
  padding: 0;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 8px;
}

.amount {
  font-size: 28px;
  font-weight: 700;
}

.summary-detail {
  font-size: 13px;
  opacity: 0.9;
}

/* Modal Footer */
.modal-footer {
  padding: 20px 32px;
  border-top: 1px solid #e5e7eb;
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.btn {
  padding: 12px 32px;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-cancel {
  background: #f3f4f6;
  color: #374151;
}

.btn-cancel:hover:not(:disabled) {
  background: #e5e7eb;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
}

/* Responsive */
@media (max-width: 768px) {
  .modal-container {
    width: 95%;
    max-height: 95vh;
  }

  .modal-header,
  .modal-body,
  .modal-footer {
    padding-left: 20px;
    padding-right: 20px;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  .payment-method-selector {
    grid-template-columns: 1fr;
  }
}
</style>
