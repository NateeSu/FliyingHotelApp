<template>
  <n-modal
    v-model:show="showModal"
    :title="isEditing ? 'แก้ไขสินค้า' : 'เพิ่มสินค้าใหม่'"
    preset="card"
    style="width: 500px"
    :mask-closable="false"
    @positive-click="submitForm"
    @negative-click="closeModal"
    positive-text="บันทึก"
    negative-text="ยกเลิก"
  >
    <n-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      label-placement="left"
      label-width="100px"
      require-mark-placement="right"
    >
      <!-- Product Name -->
      <n-form-item label="ชื่อสินค้า" path="name">
        <n-input
          v-model:value="formData.name"
          placeholder="กรอกชื่อสินค้า"
          clearable
        />
      </n-form-item>

      <!-- Category -->
      <n-form-item label="หมวดหมู่" path="category">
        <n-select
          v-model:value="formData.category"
          :options="categoryOptions"
          placeholder="เลือกหมวดหมู่"
        />
      </n-form-item>

      <!-- Price -->
      <n-form-item label="ราคา" path="price">
        <n-input-number
          v-model:value="formData.price"
          placeholder="กรอกราคา"
          :min="0"
          :step="0.01"
          :precision="2"
        />
      </n-form-item>

      <!-- Description -->
      <n-form-item label="คำอธิบาย" path="description">
        <n-input
          v-model:value="formData.description"
          placeholder="กรอกคำอธิบาย (ไม่บังคับ)"
          type="textarea"
          :rows="3"
          clearable
        />
      </n-form-item>

      <!-- Chargeable -->
      <n-form-item label="คิดค่าใช้" path="is_chargeable">
        <n-switch v-model:value="formData.is_chargeable" />
      </n-form-item>

      <!-- Active Status (only for edit) -->
      <n-form-item v-if="isEditing" label="สถานะ" path="is_active">
        <n-switch v-model:value="formData.is_active" />
      </n-form-item>
    </n-form>
  </n-modal>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { FormInst } from 'naive-ui'
import { NModal, NForm, NFormItem, NInput, NInputNumber, NSelect, NSwitch } from 'naive-ui'
import type { Product, ProductCreate, ProductUpdate } from '@/api/products'
import { productsApi } from '@/api/products'

const props = defineProps<{
  show: boolean
  product?: Product
}>()

const emit = defineEmits<{
  'update:show': [value: boolean]
  success: [product: Product]
}>()

const formRef = ref<FormInst | null>(null)

const categoryOptions = [
  { label: 'สิ่งอำนวยความสะดวกห้องพัก', value: 'room_amenity' },
  { label: 'อาหารและเครื่องดื่ม', value: 'food_beverage' }
]

const formData = ref<ProductCreate & { is_active?: boolean }>({
  name: '',
  category: 'food_beverage',
  price: 0,
  is_chargeable: true,
  description: null,
  is_active: true
})

const formRules = {
  name: [
    { required: true, message: 'กรุณากรอกชื่อสินค้า', trigger: 'blur' },
    { min: 1, max: 255, message: 'ชื่อสินค้าต้องไม่เกิน 255 ตัวอักษร', trigger: 'blur' }
  ],
  category: [
    { required: true, message: 'กรุณาเลือกหมวดหมู่', trigger: 'change' }
  ],
  price: [
    { required: true, message: 'กรุณากรอกราคา', trigger: 'blur' },
    { type: 'number', message: 'ราคาต้องเป็นตัวเลข', trigger: 'blur' }
  ]
}

const isEditing = computed(() => !!props.product)

const showModal = computed({
  get: () => props.show,
  set: (value) => emit('update:show', value)
})

// Watch for product changes and populate form
watch(
  () => props.product,
  (newProduct) => {
    if (newProduct) {
      formData.value = {
        name: newProduct.name,
        category: newProduct.category,
        price: newProduct.price,
        is_chargeable: newProduct.is_chargeable,
        description: newProduct.description,
        is_active: newProduct.is_active
      }
    } else {
      formData.value = {
        name: '',
        category: 'food_beverage',
        price: 0,
        is_chargeable: true,
        description: null,
        is_active: true
      }
    }
  },
  { immediate: true }
)

async function submitForm() {
  try {
    if (!formRef.value) return

    await formRef.value.validate()

    if (isEditing.value && props.product) {
      // Update product
      const updateData: ProductUpdate = {
        name: formData.value.name,
        category: formData.value.category,
        price: formData.value.price,
        is_chargeable: formData.value.is_chargeable,
        description: formData.value.description,
        is_active: formData.value.is_active
      }
      const updatedProduct = await productsApi.updateProduct(props.product.id, updateData)
      emit('success', updatedProduct)
    } else {
      // Create product
      const createData: ProductCreate = {
        name: formData.value.name,
        category: formData.value.category,
        price: formData.value.price,
        is_chargeable: formData.value.is_chargeable,
        description: formData.value.description
      }
      const newProduct = await productsApi.createProduct(createData)
      emit('success', newProduct)
    }

    closeModal()
  } catch (error) {
    console.error('Error submitting product form:', error)
  }
}

function closeModal() {
  showModal.value = false
}
</script>
