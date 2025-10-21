<template>
  <n-modal
    v-model:show="visible"
    preset="card"
    :title="isEdit ? 'แก้ไขข้อมูลลูกค้า' : 'เพิ่มลูกค้าใหม่'"
    style="width: 600px"
    :mask-closable="false"
  >
    <n-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      label-placement="left"
      label-width="140"
      require-mark-placement="right-hanging"
    >
      <n-form-item label="ชื่อ-นามสกุล" path="full_name">
        <n-input
          v-model:value="formData.full_name"
          placeholder="กรอกชื่อ-นามสกุล"
          maxlength="100"
          show-count
        />
      </n-form-item>

      <n-form-item label="เบอร์โทรศัพท์" path="phone_number">
        <n-input
          v-model:value="formData.phone_number"
          placeholder="เช่น 0812345678"
          maxlength="20"
          show-count
        />
      </n-form-item>

      <n-form-item label="อีเมล" path="email">
        <n-input
          v-model:value="formData.email"
          placeholder="กรอกอีเมล (ไม่บังคับ)"
          type="email"
        />
      </n-form-item>

      <n-form-item label="เลขบัตรประชาชน" path="id_card_number">
        <n-input
          v-model:value="formData.id_card_number"
          placeholder="กรอกเลขบัตรประชาชน (ไม่บังคับ)"
          maxlength="13"
          show-count
        />
      </n-form-item>

      <n-form-item label="ที่อยู่" path="address">
        <n-input
          v-model:value="formData.address"
          type="textarea"
          placeholder="กรอกที่อยู่ (ไม่บังคับ)"
          :rows="3"
          maxlength="500"
          show-count
        />
      </n-form-item>

      <n-form-item label="หมายเหตุ" path="notes">
        <n-input
          v-model:value="formData.notes"
          type="textarea"
          placeholder="กรอกหมายเหตุ (ไม่บังคับ)"
          :rows="3"
          maxlength="500"
          show-count
        />
      </n-form-item>
    </n-form>

    <template #footer>
      <n-space justify="end">
        <n-button @click="handleCancel">ยกเลิก</n-button>
        <n-button type="primary" :loading="loading" @click="handleSubmit">
          {{ isEdit ? 'บันทึก' : 'เพิ่มลูกค้า' }}
        </n-button>
      </n-space>
    </template>
  </n-modal>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import {
  NModal,
  NForm,
  NFormItem,
  NInput,
  NButton,
  NSpace,
  type FormInst,
  type FormRules
} from 'naive-ui'
import { useCustomerStore } from '@/stores/customer'
import type { CustomerResponse, CustomerCreate, CustomerUpdate } from '@/api/customers'

const props = defineProps<{
  show: boolean
  customer?: CustomerResponse | null
}>()

const emit = defineEmits<{
  (e: 'update:show', value: boolean): void
  (e: 'success'): void
}>()

const customerStore = useCustomerStore()

const formRef = ref<FormInst | null>(null)
const loading = ref(false)

const visible = computed({
  get: () => props.show,
  set: (value) => emit('update:show', value)
})

const isEdit = computed(() => !!props.customer?.id)

// Form data
const initialFormData = {
  full_name: '',
  phone_number: '',
  email: '',
  id_card_number: '',
  address: '',
  notes: ''
}

const formData = ref<CustomerCreate>({ ...initialFormData })

// Form rules
const formRules: FormRules = {
  full_name: [
    { required: true, message: 'กรุณากรอกชื่อ-นามสกุล', trigger: ['blur', 'input'] },
    { min: 2, max: 100, message: 'กรุณากรอกชื่อ 2-100 ตัวอักษร', trigger: 'blur' }
  ],
  phone_number: [
    { required: true, message: 'กรุณากรอกเบอร์โทรศัพท์', trigger: ['blur', 'input'] },
    {
      pattern: /^0[0-9]{8,9}$/,
      message: 'กรุณากรอกเบอร์โทรศัพท์ที่ถูกต้อง (เช่น 0812345678)',
      trigger: 'blur'
    }
  ],
  email: [
    {
      type: 'email',
      message: 'กรุณากรอกอีเมลที่ถูกต้อง',
      trigger: 'blur'
    }
  ],
  id_card_number: [
    {
      pattern: /^[0-9]{13}$/,
      message: 'เลขบัตรประชาชนต้องเป็นตัวเลข 13 หลัก',
      trigger: 'blur'
    }
  ]
}

// Watch for customer changes
watch(() => props.customer, (newCustomer) => {
  if (newCustomer) {
    formData.value = {
      full_name: newCustomer.full_name,
      phone_number: newCustomer.phone_number,
      email: newCustomer.email || '',
      id_card_number: newCustomer.id_card_number || '',
      address: newCustomer.address || '',
      notes: newCustomer.notes || ''
    }
  } else {
    resetForm()
  }
}, { immediate: true })

watch(() => props.show, (newShow) => {
  if (!newShow) {
    resetForm()
  }
})

function resetForm() {
  formData.value = { ...initialFormData }
  formRef.value?.restoreValidation()
}

function handleCancel() {
  visible.value = false
  resetForm()
}

async function handleSubmit() {
  try {
    await formRef.value?.validate()

    loading.value = true

    if (isEdit.value && props.customer) {
      // Update
      const updateData: CustomerUpdate = {
        full_name: formData.value.full_name,
        phone_number: formData.value.phone_number,
        email: formData.value.email || undefined,
        id_card_number: formData.value.id_card_number || undefined,
        address: formData.value.address || undefined,
        notes: formData.value.notes || undefined
      }
      await customerStore.updateCustomer(props.customer.id, updateData)
    } else {
      // Create
      const createData: CustomerCreate = {
        full_name: formData.value.full_name,
        phone_number: formData.value.phone_number,
        email: formData.value.email || undefined,
        id_card_number: formData.value.id_card_number || undefined,
        address: formData.value.address || undefined,
        notes: formData.value.notes || undefined
      }
      await customerStore.createCustomer(createData)
    }

    visible.value = false
    emit('success')
    resetForm()
  } catch (error) {
    console.error('Form validation failed or API error:', error)
  } finally {
    loading.value = false
  }
}
</script>
