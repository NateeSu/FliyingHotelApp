<template>
  <div v-if="show" class="modal-overlay" @click.self="handleClose">
    <div class="modal-container">
      <div class="modal-header">
        <h2>เช็คเอาท์ห้อง {{ summary?.room_number }}</h2>
        <button class="close-btn" @click="handleClose">×</button>
      </div>

      <div v-if="loadingSummary" class="modal-body loading-state">
        <div class="spinner"></div>
        <p>กำลังโหลดข้อมูล...</p>
      </div>

      <div v-else-if="checkoutSuccess" class="modal-body success-state">
        <div class="success-icon">✅</div>
        <h3>เช็คเอาท์สำเร็จ!</h3>
        <p>การเช็คเอาท์เสร็จสมบูรณ์แล้ว</p>
        <button class="btn btn-download" @click="handleDownloadReceipt">
          📄 ดาวน์โหลดใบเสร็จ
        </button>
        <button class="btn btn-close-success" @click="handleClose">
          ปิด
        </button>
      </div>

      <div v-else-if="summary" class="modal-body">
        <!-- Customer Info Section -->
        <section class="info-section">
          <h3>ข้อมูลลูกค้า</h3>
          <div class="info-row">
            <span class="label">ชื่อลูกค้า:</span>
            <span class="value">{{ summary.customer_name }}</span>
          </div>
        </section>

        <!-- Check-In Details Section -->
        <section class="info-section">
          <h3>รายละเอียดการเข้าพัก</h3>
          <div class="info-row">
            <span class="label">ประเภท:</span>
            <span class="value">
              <span class="badge" :class="summary.stay_type">
                {{ summary.stay_type === 'OVERNIGHT' ? 'ค้างคืน' : 'ชั่วคราว (3 ชม.)' }}
              </span>
            </span>
          </div>
          <div class="info-row">
            <span class="label">เวลาเช็คอิน:</span>
            <span class="value">{{ formatDateTime(summary.check_in_time) }}</span>
          </div>
          <div class="info-row">
            <span class="label">เวลาที่ควรเช็คเอาท์:</span>
            <span class="value">{{ formatDateTime(summary.expected_check_out_time) }}</span>
          </div>
          <div class="info-row">
            <span class="label">เวลาเช็คเอาท์จริง:</span>
            <span class="value">{{ formatDateTime(summary.actual_check_out_time) }}</span>
          </div>
        </section>

        <!-- Overtime Alert (if applicable) -->
        <div v-if="summary.is_overtime" class="overtime-alert">
          <div class="alert-icon">⚠️</div>
          <div class="alert-content">
            <div class="alert-title">เกินเวลา!</div>
            <div class="alert-message">
              เกินเวลา {{ summary.overtime_minutes }} นาที ({{ formatOvertimeHours(summary.overtime_minutes) }})
            </div>
          </div>
        </div>

        <!-- Payment Breakdown Section -->
        <section class="breakdown-section">
          <h3>รายละเอียดค่าใช้จ่าย</h3>

          <div class="breakdown-row">
            <span>ค่าห้องพักฐาน:</span>
            <span class="amount">{{ formatCurrency(summary.base_amount) }}</span>
          </div>

          <div v-if="summary.is_overtime" class="breakdown-row highlight">
            <span>ค่าเกินเวลา:</span>
            <span class="amount">{{ formatCurrency(summary.overtime_charge) }}</span>
          </div>

          <!-- Extra Charges Input -->
          <div class="form-group">
            <label>ค่าใช้จ่ายเพิ่มเติม (ถ้ามี)</label>
            <input
              v-model.number="formData.extra_charges"
              type="number"
              class="form-input"
              min="0"
              step="1"
              placeholder="0"
            />
            <small class="hint">เช่น มินิบาร์, ค่าเสียหาย</small>
          </div>

          <!-- Show extra charges in breakdown if > 0 -->
          <div v-if="formData.extra_charges && formData.extra_charges > 0" class="breakdown-row">
            <span>ค่าใช้จ่ายเพิ่มเติม:</span>
            <span class="amount">{{ formatCurrency(formData.extra_charges) }}</span>
          </div>

          <!-- Discount Input -->
          <div class="form-group">
            <label>ส่วนลด (ถ้ามี)</label>
            <input
              v-model.number="formData.discount_amount"
              type="number"
              class="form-input"
              min="0"
              step="1"
              placeholder="0"
            />
          </div>

          <div v-if="formData.discount_amount > 0" class="form-group">
            <label>เหตุผลการให้ส่วนลด</label>
            <input
              v-model="formData.discount_reason"
              type="text"
              class="form-input"
              placeholder="ระบุเหตุผล..."
            />
          </div>

          <!-- Show discount in breakdown if > 0 -->
          <div v-if="formData.discount_amount && formData.discount_amount > 0" class="breakdown-row discount">
            <span>ส่วนลด:</span>
            <span class="amount">-{{ formatCurrency(formData.discount_amount) }}</span>
          </div>

          <div class="breakdown-divider"></div>

          <div class="breakdown-row total">
            <span>ยอดรวมทั้งหมด:</span>
            <span class="amount">{{ formatCurrency(finalTotal) }}</span>
          </div>
        </section>

        <!-- Payment Method Section -->
        <section class="form-section">
          <h3>วิธีชำระเงิน</h3>
          <div class="payment-method-selector">
            <button
              :class="['payment-btn', { active: formData.payment_method === 'CASH' }]"
              @click="formData.payment_method = 'CASH'"
            >
              💵 เงินสด
            </button>
            <button
              :class="['payment-btn', { active: formData.payment_method === 'TRANSFER' }]"
              @click="formData.payment_method = 'TRANSFER'"
            >
              🏦 โอนเงิน
            </button>
            <button
              :class="['payment-btn', { active: formData.payment_method === 'CREDIT_CARD' }]"
              @click="formData.payment_method = 'CREDIT_CARD'"
            >
              💳 บัตรเครดิต
            </button>
          </div>
        </section>

        <!-- Payment Notes -->
        <section class="form-section">
          <div class="form-group">
            <label>หมายเหตุการชำระเงิน</label>
            <textarea
              v-model="formData.payment_notes"
              class="form-input"
              rows="2"
              placeholder="บันทึกเพิ่มเติม..."
            ></textarea>
          </div>
        </section>
      </div>

      <div v-if="!checkoutSuccess" class="modal-footer">
        <button class="btn btn-cancel" @click="handleClose" :disabled="loading">
          ยกเลิก
        </button>
        <button class="btn btn-primary" @click="handleSubmit" :disabled="loading || !summary">
          <span v-if="loading">กำลังเช็คเอาท์...</span>
          <span v-else>เช็คเอาท์และรับชำระเงิน</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useToast } from 'vue-toastification'
import { checkInApi, type CheckOutRequest, type CheckOutSummary } from '@/api/check-ins'

const toast = useToast()

interface Props {
  show: boolean
  checkInId: number
}

const props = defineProps<Props>()

const emit = defineEmits<{
  close: []
  success: []
}>()

// Summary data
const summary = ref<CheckOutSummary | null>(null)
const loadingSummary = ref(false)

// Form data
const formData = ref<CheckOutRequest>({
  extra_charges: 0,
  discount_amount: 0,
  discount_reason: '',
  payment_method: 'CASH',
  payment_notes: '',
  customer_name: undefined,
  phone_number: undefined,
  customer_email: undefined,
  customer_address: undefined
})

// Calculate final total
const finalTotal = computed(() => {
  if (!summary.value) return 0

  const baseAmount = Number(summary.value.base_amount) || 0
  const overtimeCharge = Number(summary.value.overtime_charge) || 0
  const extraCharges = Number(formData.value.extra_charges) || 0
  const discountAmount = Number(formData.value.discount_amount) || 0

  const total = baseAmount + overtimeCharge + extraCharges - discountAmount

  return Math.max(0, total) // Ensure non-negative
})

// Load checkout summary
const loadCheckoutSummary = async () => {
  if (!props.checkInId) return

  loadingSummary.value = true
  try {
    summary.value = await checkInApi.getCheckoutSummary(props.checkInId)
  } catch (error: any) {
    console.error('Failed to load checkout summary:', error)
    const errorMessage = error.response?.data?.detail || 'ไม่สามารถโหลดข้อมูลได้'
    toast.error(errorMessage)
    emit('close')
  } finally {
    loadingSummary.value = false
  }
}

// Format helpers
const formatDateTime = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleString('th-TH', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('th-TH', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(amount)
}

const formatOvertimeHours = (minutes: number) => {
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60

  if (hours === 0) {
    return `${mins} นาที`
  } else if (mins === 0) {
    return `${hours} ชั่วโมง`
  } else {
    return `${hours} ชั่วโมง ${mins} นาที`
  }
}

// Submit checkout
const loading = ref(false)

const checkoutSuccess = ref(false)
const completedCheckInId = ref<number | null>(null)

const handleSubmit = async () => {
  if (!props.checkInId || !summary.value) return

  // Validate discount reason if discount is given
  if ((formData.value.discount_amount || 0) > 0 && !formData.value.discount_reason) {
    toast.warning('กรุณาระบุเหตุผลการให้ส่วนลด')
    return
  }

  loading.value = true
  try {
    await checkInApi.processCheckout(props.checkInId, formData.value)

    // Show success toast
    toast.success('✅ เช็คเอาท์สำเร็จ!')

    // Mark as success and store check-in ID for receipt download
    checkoutSuccess.value = true
    completedCheckInId.value = props.checkInId

    // Emit success event (don't wait for it)
    try {
      emit('success')
    } catch (emitError) {
      console.error('Error in success handler:', emitError)
    }

  } catch (error: any) {
    console.error('Checkout error:', error)
    const errorMessage = error.response?.data?.detail || 'เกิดข้อผิดพลาดในการเช็คเอาท์'
    toast.error(errorMessage)
  } finally {
    loading.value = false
  }
}

const handleDownloadReceipt = async () => {
  if (!completedCheckInId.value) return

  try {
    await checkInApi.downloadReceipt(completedCheckInId.value)
    toast.info('📄 กำลังเปิดใบเสร็จ...')
  } catch (error: any) {
    console.error('Download receipt error:', error)
    toast.error('เกิดข้อผิดพลาดในการเปิดใบเสร็จ')
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
    extra_charges: 0,
    discount_amount: 0,
    discount_reason: '',
    payment_method: 'CASH',
    payment_notes: '',
    customer_name: undefined,
    phone_number: undefined,
    customer_email: undefined,
    customer_address: undefined
  }
  summary.value = null
  checkoutSuccess.value = false
  completedCheckInId.value = null
}

// Watch for show change
watch(() => props.show, (newShow) => {
  if (newShow) {
    loadCheckoutSummary()
  }
})

// Load on mount if already shown
onMounted(() => {
  if (props.show) {
    loadCheckoutSummary()
  }
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

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 24px 32px;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
}

.spinner {
  width: 48px;
  height: 48px;
  border: 4px solid #e5e7eb;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-state p {
  color: #6b7280;
  font-size: 15px;
}

/* Success State */
.success-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  text-align: center;
}

.success-icon {
  font-size: 72px;
  margin-bottom: 20px;
  animation: scaleIn 0.5s ease-out;
}

@keyframes scaleIn {
  0% {
    transform: scale(0);
    opacity: 0;
  }
  50% {
    transform: scale(1.2);
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

.success-state h3 {
  margin: 0 0 12px;
  font-size: 24px;
  font-weight: 600;
  color: #10b981;
}

.success-state p {
  margin: 0 0 32px;
  color: #6b7280;
  font-size: 15px;
}

.btn-download {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  padding: 14px 32px;
  margin-bottom: 12px;
  width: 250px;
  font-size: 16px;
}

.btn-download:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(59, 130, 246, 0.3);
}

.btn-close-success {
  background: #f3f4f6;
  color: #374151;
  padding: 12px 32px;
  width: 250px;
}

.btn-close-success:hover {
  background: #e5e7eb;
}

/* Info Section */
.info-section {
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e5e7eb;
}

.info-section h3 {
  margin: 0 0 16px;
  font-size: 16px;
  font-weight: 600;
  color: #374151;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  font-size: 14px;
}

.info-row .label {
  color: #6b7280;
  font-weight: 500;
}

.info-row .value {
  color: #111827;
  font-weight: 600;
  text-align: right;
}

.badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 600;
}

.badge.overnight {
  background: #dbeafe;
  color: #1e40af;
}

.badge.temporary {
  background: #fef3c7;
  color: #92400e;
}

/* Overtime Alert */
.overtime-alert {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  border: 2px solid #f59e0b;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  gap: 12px;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.9; }
}

.alert-icon {
  font-size: 32px;
}

.alert-title {
  font-weight: 700;
  font-size: 16px;
  color: #92400e;
  margin-bottom: 4px;
}

.alert-message {
  font-size: 14px;
  color: #78350f;
}

/* Breakdown Section */
.breakdown-section {
  background: #f9fafb;
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 24px;
}

.breakdown-section h3 {
  margin: 0 0 16px;
  font-size: 16px;
  font-weight: 600;
  color: #374151;
}

.breakdown-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  font-size: 15px;
  color: #374151;
}

.breakdown-row.highlight {
  color: #dc2626;
  font-weight: 600;
}

.breakdown-row.discount {
  color: #059669;
  font-weight: 600;
}

.breakdown-row.discount .amount {
  color: #059669;
}

.breakdown-row .amount {
  font-weight: 600;
  font-size: 16px;
}

.breakdown-divider {
  border-top: 2px dashed #d1d5db;
  margin: 16px 0;
}

.breakdown-row.total {
  font-size: 18px;
  font-weight: 700;
  color: #111827;
  padding-top: 16px;
}

.breakdown-row.total .amount {
  font-size: 24px;
  color: #059669;
}

/* Form Section */
.form-section {
  margin-bottom: 24px;
}

.form-section h3 {
  margin: 0 0 16px;
  font-size: 16px;
  font-weight: 600;
  color: #374151;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #374151;
  font-size: 14px;
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

textarea.form-input {
  resize: vertical;
  min-height: 60px;
}

.hint {
  display: block;
  margin-top: 6px;
  font-size: 12px;
  color: #9ca3af;
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
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(16, 185, 129, 0.3);
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

  .payment-method-selector {
    grid-template-columns: 1fr;
  }
}
</style>
