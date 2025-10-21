<template>
  <n-modal
    v-model:show="showModal"
    :mask-closable="false"
    preset="card"
    :title="isEdit ? 'แก้ไขการจอง' : 'สร้างการจองใหม่'"
    class="booking-form-modal"
    style="width: 90%; max-width: 800px"
  >
    <n-form
      ref="formRef"
      :model="formData"
      :rules="rules"
      label-placement="top"
      require-mark-placement="right-hanging"
    >
      <!-- Customer Selection -->
      <n-form-item label="ลูกค้า" path="customer_id">
        <n-select
          v-model:value="formData.customer_id"
          :options="customerOptions"
          filterable
          remote
          :loading="loadingCustomers"
          @search="handleSearchCustomers"
          placeholder="เลือกหรือค้นหาลูกค้า"
          clearable
        >
          <template #empty>
            <div class="p-4 text-center">
              <p class="text-gray-500 mb-2">ไม่พบลูกค้า</p>
              <n-button size="small" @click="showCreateCustomerModal = true">
                + สร้างลูกค้าใหม่
              </n-button>
            </div>
          </template>
        </n-select>
      </n-form-item>

      <!-- Room Selection -->
      <n-form-item label="ห้อง" path="room_id">
        <n-select
          v-model:value="formData.room_id"
          :options="availableRoomOptions"
          filterable
          placeholder="เลือกห้องที่ว่าง"
          @update:value="handleRoomChange"
          :disabled="!formData.check_in_date || !formData.check_out_date"
        >
          <template #empty>
            <div class="p-4 text-center text-gray-500">
              กรุณาเลือกวันที่เข้า-ออกก่อน
            </div>
          </template>
        </n-select>
      </n-form-item>

      <!-- Date Range -->
      <n-grid cols="2" x-gap="12">
        <n-form-item-gi label="วันเข้าพัก" path="check_in_date">
          <n-date-picker
            v-model:formatted-value="formData.check_in_date"
            type="date"
            format="dd/MM/yyyy"
            value-format="yyyy-MM-dd"
            placeholder="เลือกวันเข้าพัก"
            :is-date-disabled="disablePastDates"
            @update:formatted-value="handleDateChange"
            class="w-full"
          />
        </n-form-item-gi>

        <n-form-item-gi label="วันออก" path="check_out_date">
          <n-date-picker
            v-model:formatted-value="formData.check_out_date"
            type="date"
            format="dd/MM/yyyy"
            value-format="yyyy-MM-dd"
            placeholder="เลือกวันออก"
            :is-date-disabled="disableCheckOutDates"
            @update:formatted-value="handleDateChange"
            class="w-full"
          />
        </n-form-item-gi>
      </n-grid>

      <!-- Nights & Amount -->
      <n-grid cols="3" x-gap="12">
        <n-form-item-gi label="จำนวนคืน">
          <n-input-number
            :value="numberOfNights"
            disabled
            class="w-full"
          >
            <template #suffix>คืน</template>
          </n-input-number>
        </n-form-item-gi>

        <n-form-item-gi label="ราคาต่อคืน">
          <n-input-number
            :value="roomRate"
            disabled
            :format="formatCurrency"
            class="w-full"
          >
            <template #suffix>บาท</template>
          </n-input-number>
        </n-form-item-gi>

        <n-form-item-gi label="ยอดรวม" path="total_amount">
          <n-input-number
            v-model:value="formData.total_amount"
            :min="0"
            :format="formatCurrency"
            class="w-full"
          >
            <template #suffix>บาท</template>
          </n-input-number>
        </n-form-item-gi>
      </n-grid>

      <!-- Deposit -->
      <n-form-item label="เงินมัดจำ (ไม่คืน)" path="deposit_amount">
        <n-input-number
          v-model:value="formData.deposit_amount"
          :min="0"
          :max="formData.total_amount"
          :format="formatCurrency"
          class="w-full"
        >
          <template #suffix>บาท</template>
        </n-input-number>
        <template #feedback>
          <n-text type="warning" v-if="formData.deposit_amount > 0">
            ⚠️ เงินมัดจำจะไม่สามารถคืนได้หากยกเลิกการจอง
          </n-text>
        </template>
      </n-form-item>

      <!-- Availability Check Result -->
      <n-alert
        v-if="availabilityChecked && !isAvailable"
        type="error"
        title="ห้องไม่ว่าง"
        class="mb-4"
      >
        <p class="mb-2">ห้องนี้มีการจองในช่วงเวลาที่เลือกแล้ว:</p>
        <ul class="list-disc list-inside">
          <li v-for="conflict in conflictingBookings" :key="conflict.id">
            {{ formatDateRange(conflict.check_in_date, conflict.check_out_date) }}
            - {{ conflict.customer_name }}
          </li>
        </ul>
      </n-alert>

      <n-alert
        v-else-if="availabilityChecked && isAvailable"
        type="success"
        title="ห้องว่าง"
        class="mb-4"
      >
        ห้องนี้พร้อมให้บริการในช่วงเวลาที่เลือก
      </n-alert>

      <!-- Notes -->
      <n-form-item label="หมายเหตุ">
        <n-input
          v-model:value="formData.notes"
          type="textarea"
          placeholder="หมายเหตุเพิ่มเติม (ถ้ามี)"
          :rows="3"
        />
      </n-form-item>
    </n-form>

    <template #footer>
      <div class="flex justify-end space-x-3">
        <n-button @click="handleCancel">ยกเลิก</n-button>
        <n-button
          type="primary"
          :loading="submitting"
          :disabled="!isAvailable && availabilityChecked"
          @click="handleSubmit"
        >
          {{ isEdit ? 'บันทึกการแก้ไข' : 'สร้างการจอง' }}
        </n-button>
      </div>
    </template>
  </n-modal>

  <!-- Create Customer Modal -->
  <n-modal
    v-model:show="showCreateCustomerModal"
    preset="card"
    title="สร้างลูกค้าใหม่"
    style="width: 600px"
  >
    <n-form :model="newCustomer">
      <n-form-item label="ชื่อ-นามสกุล" required>
        <n-input v-model:value="newCustomer.full_name" placeholder="ชื่อ-นามสกุล" />
      </n-form-item>
      <n-form-item label="เบอร์โทร" required>
        <n-input v-model:value="newCustomer.phone_number" placeholder="08X-XXX-XXXX" />
      </n-form-item>
    </n-form>
    <template #footer>
      <div class="flex justify-end space-x-3">
        <n-button @click="showCreateCustomerModal = false">ยกเลิก</n-button>
        <n-button type="primary" @click="handleCreateCustomer">สร้าง</n-button>
      </div>
    </template>
  </n-modal>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useMessage, type FormInst, type FormRules } from 'naive-ui'
import { useBookingStore } from '@/stores/booking'
import { useDashboardStore } from '@/stores/dashboard'
import { customerApi } from '@/api/customers'
import type { Booking, BookingCreate, BookingUpdate } from '@/types/booking'

interface Props {
  show: boolean
  booking?: Booking | null
  preselectedDate?: string | null
}

const props = defineProps<Props>()
const emit = defineEmits<{
  (e: 'update:show', value: boolean): void
  (e: 'saved'): void
}>()

const message = useMessage()
const bookingStore = useBookingStore()
const dashboardStore = useDashboardStore()

// Refs
const formRef = ref<FormInst | null>(null)
const submitting = ref(false)
const loadingCustomers = ref(false)
const showCreateCustomerModal = ref(false)
const availabilityChecked = ref(false)
const isAvailable = ref(true)
const conflictingBookings = ref<Booking[]>([])

// Get default dates (today and tomorrow)
const getDefaultDates = () => {
  const today = new Date()
  const tomorrow = new Date(today)
  tomorrow.setDate(tomorrow.getDate() + 1)

  return {
    check_in: today.toISOString().split('T')[0],
    check_out: tomorrow.toISOString().split('T')[0]
  }
}

// Form data
const formData = ref<BookingCreate>({
  customer_id: 0,
  room_id: 0,
  check_in_date: getDefaultDates().check_in,
  check_out_date: getDefaultDates().check_out,
  total_amount: 0,
  deposit_amount: 0,
  notes: ''
})

// New customer form
const newCustomer = ref({
  full_name: '',
  phone_number: ''
})

// Customer options
const customerOptions = ref<any[]>([])
const roomRate = ref(0)

// Computed
const showModal = computed({
  get: () => props.show,
  set: (value) => emit('update:show', value)
})

const isEdit = computed(() => !!props.booking)

const numberOfNights = computed(() => {
  if (!formData.value.check_in_date || !formData.value.check_out_date) return 0
  const start = new Date(formData.value.check_in_date)
  const end = new Date(formData.value.check_out_date)
  const diffTime = Math.abs(end.getTime() - start.getTime())
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  return diffDays
})

const availableRoomOptions = computed(() => {
  return dashboardStore.rooms
    .filter(room => room.status === 'available' || room.id === formData.value.room_id)
    .map(room => ({
      label: `${room.room_number} - ${room.room_type_name}`,
      value: room.id,
      disabled: false
    }))
})

// Form rules
const rules: FormRules = {
  customer_id: [
    { required: true, message: 'กรุณาเลือกลูกค้า', type: 'number', trigger: 'change' }
  ],
  room_id: [
    { required: true, message: 'กรุณาเลือกห้อง', type: 'number', trigger: 'change' }
  ],
  check_in_date: [
    { required: true, message: 'กรุณาเลือกวันเข้าพัก', trigger: 'change' }
  ],
  check_out_date: [
    { required: true, message: 'กรุณาเลือกวันออก', trigger: 'change' }
  ],
  total_amount: [
    { required: true, message: 'กรุณาระบุยอดรวม', type: 'number', trigger: 'change' }
  ]
}

// Methods

function formatCurrency(value: number | null) {
  if (value === null) return ''
  return new Intl.NumberFormat('th-TH').format(value)
}

function formatDateRange(start: string, end: string) {
  const startDate = new Date(start)
  const endDate = new Date(end)
  return `${startDate.toLocaleDateString('th-TH')} - ${endDate.toLocaleDateString('th-TH')}`
}

function disablePastDates(ts: number) {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  return ts < today.getTime()
}

function disableCheckOutDates(ts: number) {
  if (!formData.value.check_in_date) return true
  const checkInDate = new Date(formData.value.check_in_date)
  checkInDate.setHours(0, 0, 0, 0)
  return ts <= checkInDate.getTime()
}

async function handleSearchCustomers(query: string) {
  if (!query) return

  loadingCustomers.value = true
  try {
    const response = await customerApi.searchCustomers(query)
    customerOptions.value = response.data.map(customer => ({
      label: `${customer.full_name} (${customer.phone_number})`,
      value: customer.id
    }))
  } catch (error) {
    console.error('Error searching customers:', error)
  } finally {
    loadingCustomers.value = false
  }
}

async function handleCreateCustomer() {
  if (!newCustomer.value.full_name || !newCustomer.value.phone_number) {
    message.error('กรุณากรอกข้อมูลให้ครบถ้วน')
    return
  }

  try {
    const customer = await customerApi.createCustomer(newCustomer.value)
    formData.value.customer_id = customer.id
    customerOptions.value.push({
      label: `${customer.full_name} (${customer.phone_number})`,
      value: customer.id
    })
    showCreateCustomerModal.value = false
    newCustomer.value = { full_name: '', phone_number: '' }
    message.success('สร้างลูกค้าเรียบร้อยแล้ว')
  } catch (error: any) {
    message.error(error.response?.data?.detail || 'ไม่สามารถสร้างลูกค้าได้')
  }
}

async function handleRoomChange(roomId: number) {
  const room = dashboardStore.rooms.find(r => r.id === roomId)
  if (room) {
    roomRate.value = room.overnight_rate || 0
    calculateTotalAmount()
  }
}

function handleDateChange() {
  availabilityChecked.value = false
  calculateTotalAmount()
  checkAvailability()
}

function calculateTotalAmount() {
  if (numberOfNights.value > 0 && roomRate.value > 0) {
    formData.value.total_amount = numberOfNights.value * roomRate.value
  }
}

async function checkAvailability() {
  if (!formData.value.room_id || !formData.value.check_in_date || !formData.value.check_out_date) {
    return
  }

  try {
    const result = await bookingStore.checkAvailability({
      room_id: formData.value.room_id,
      check_in_date: formData.value.check_in_date,
      check_out_date: formData.value.check_out_date,
      exclude_booking_id: props.booking?.id
    })

    availabilityChecked.value = true
    isAvailable.value = result.available
    conflictingBookings.value = result.conflicting_bookings
  } catch (error) {
    console.error('Error checking availability:', error)
  }
}

async function handleSubmit() {
  if (!formRef.value) return

  try {
    await formRef.value.validate()

    submitting.value = true

    if (isEdit.value && props.booking) {
      // Update
      const updateData: BookingUpdate = {
        check_in_date: formData.value.check_in_date,
        check_out_date: formData.value.check_out_date,
        total_amount: formData.value.total_amount,
        deposit_amount: formData.value.deposit_amount,
        notes: formData.value.notes
      }
      await bookingStore.updateBooking(props.booking.id, updateData)
      message.success('แก้ไขการจองเรียบร้อยแล้ว')
    } else {
      // Create
      await bookingStore.createBooking(formData.value)
      message.success('สร้างการจองเรียบร้อยแล้ว')
    }

    emit('saved')
    resetForm()
  } catch (error: any) {
    if (error?.errors) {
      // Validation error
      return
    }
    message.error(error?.message || 'ไม่สามารถบันทึกการจองได้')
  } finally {
    submitting.value = false
  }
}

function handleCancel() {
  showModal.value = false
  resetForm()
}

function resetForm() {
  formData.value = {
    customer_id: 0,
    room_id: 0,
    check_in_date: '',
    check_out_date: '',
    total_amount: 0,
    deposit_amount: 0,
    notes: ''
  }
  roomRate.value = 0
  availabilityChecked.value = false
  isAvailable.value = true
  conflictingBookings.value = []
}

// Watch for modal open
watch(() => props.show, (newVal) => {
  if (newVal) {
    if (props.booking) {
      // Edit mode
      formData.value = {
        customer_id: props.booking.customer_id,
        room_id: props.booking.room_id,
        check_in_date: props.booking.check_in_date,
        check_out_date: props.booking.check_out_date,
        total_amount: props.booking.total_amount,
        deposit_amount: props.booking.deposit_amount,
        notes: props.booking.notes || ''
      }

      // Load customer
      if (props.booking.customer_name) {
        customerOptions.value = [{
          label: `${props.booking.customer_name} (${props.booking.customer_phone})`,
          value: props.booking.customer_id
        }]
      }

      // Load room rate
      const room = dashboardStore.rooms.find(r => r.id === props.booking!.room_id)
      if (room) {
        roomRate.value = room.overnight_rate || 0
      }
    } else if (props.preselectedDate) {
      // Create mode with preselected date
      formData.value.check_in_date = props.preselectedDate
    }
  }
})

onMounted(async () => {
  // Load rooms if not loaded
  if (dashboardStore.rooms.length === 0) {
    await dashboardStore.fetchRooms()
  }
})
</script>

<style scoped>
.booking-form-modal :deep(.n-form-item-label) {
  font-weight: 600;
}
</style>
