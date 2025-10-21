<template>
  <div class="products-page p-6">
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900 mb-2">🛍️ จัดการสินค้า</h1>
      <p class="text-gray-600">จัดการสินค้าที่สามารถให้สั่งได้</p>
    </div>

    <!-- Filter Controls -->
    <div class="bg-white rounded-lg shadow-md p-4 mb-6">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <!-- Search -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">ค้นหา</label>
          <n-input
            v-model:value="searchQuery"
            placeholder="ค้นหาชื่อสินค้า"
            clearable
            @input="handleSearch"
          />
        </div>

        <!-- Category Filter -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">หมวดหมู่</label>
          <n-select
            v-model:value="selectedCategory"
            :options="categoryOptions"
            clearable
            placeholder="ทั้งหมด"
            @update:value="handleSearch"
          />
        </div>

        <!-- Status Filter -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">สถานะ</label>
          <n-select
            v-model:value="showInactive"
            :options="[
              { label: 'สินค้าที่ใช้งาน', value: 'false' },
              { label: 'ทั้งหมด', value: 'true' }
            ]"
            @update:value="handleSearch"
          />
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="flex gap-2 mt-4">
        <n-button type="primary" @click="openCreateModal">
          ➕ เพิ่มสินค้าใหม่
        </n-button>
        <n-button @click="loadProducts" :loading="loading">
          🔄 รีเฟรช
        </n-button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center py-12">
      <n-spin size="large" description="กำลังโหลด..." />
    </div>

    <!-- Products Table -->
    <div v-else class="bg-white rounded-lg shadow-md overflow-hidden">
      <n-data-table
        :columns="columns"
        :data="products"
        :pagination="pagination"
        :loading="loading"
        @update:page="handlePageChange"
        striped
      />
    </div>

    <!-- Error State -->
    <div v-if="errorMessage" class="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
      <p class="text-red-800">⚠️ {{ errorMessage }}</p>
    </div>

    <!-- Empty State -->
    <div v-if="!loading && products.length === 0 && !errorMessage" class="text-center py-12 text-gray-500">
      <p class="text-lg">ไม่พบสินค้า</p>
    </div>

    <!-- Product Form Modal -->
    <ProductFormModal
      v-model:show="showFormModal"
      :product="selectedProduct"
      @success="handleProductSaved"
    />

    <!-- Delete Confirmation Modal -->
    <n-modal
      v-model:show="showDeleteModal"
      title="ยืนยันการลบ"
      preset="dialog"
      positive-text="ลบ"
      negative-text="ยกเลิก"
      type="warning"
      @positive-click="confirmDelete"
    >
      <p>คุณแน่ใจว่าต้องการลบสินค้า <strong>{{ productToDelete?.name }}</strong> หรือไม่?</p>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, h } from 'vue'
import { useMessage } from 'naive-ui'
import { NButton, NInput, NSelect, NDataTable, NSpin, NModal } from 'naive-ui'
import { productsApi, type Product } from '@/api/products'
import ProductFormModal from '@/components/ProductFormModal.vue'

const message = useMessage()

// State
const products = ref<Product[]>([])
const loading = ref(false)
const searchQuery = ref('')
const selectedCategory = ref<string | null>(null)
const showInactive = ref<string>('false')
const showFormModal = ref(false)
const showDeleteModal = ref(false)
const selectedProduct = ref<Product | null>(null)
const productToDelete = ref<Product | null>(null)
const errorMessage = ref<string | null>(null)

// Pagination
const pagination = ref({
  page: 1,
  pageSize: 20,
  pageCount: 1,
  prefix(info: any) {
    return `รวม ${info.itemCount} รายการ`
  }
})

const categoryOptions = [
  { label: 'สิ่งอำนวยความสะดวกห้องพัก', value: 'room_amenity' },
  { label: 'อาหารและเครื่องดื่ม', value: 'food_beverage' }
]

// Table columns
const columns = computed(() => [
  {
    title: 'ID',
    key: 'id',
    width: 60
  },
  {
    title: 'ชื่อสินค้า',
    key: 'name',
    minWidth: 150
  },
  {
    title: 'หมวดหมู่',
    key: 'category',
    render: (row: Product) => {
      const categoryMap: Record<string, string> = {
        room_amenity: 'สิ่งอำนวยความสะดวก',
        food_beverage: 'อาหารและเครื่องดื่ม'
      }
      return categoryMap[row.category] || row.category
    },
    width: 150
  },
  {
    title: 'ราคา (฿)',
    key: 'price',
    render: (row: Product) => {
      return new Intl.NumberFormat('th-TH', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      }).format(row.price)
    },
    width: 100
  },
  {
    title: 'คำอธิบาย',
    key: 'description',
    render: (row: Product) => row.description || '-',
    minWidth: 150,
    ellipsis: true
  },
  {
    title: 'คิดค่าใช้',
    key: 'is_chargeable',
    render: (row: Product) => (row.is_chargeable ? '✅' : '❌'),
    width: 80
  },
  {
    title: 'สถานะ',
    key: 'is_active',
    render: (row: Product) => (row.is_active ? '✅ ใช้งาน' : '❌ ปิด'),
    width: 100
  },
  {
    title: 'การกระทำ',
    key: 'actions',
    width: 120,
    render: (row: Product) => {
      return h('div', { class: 'flex gap-2' }, [
        h(
          NButton,
          {
            text: true,
            type: 'primary',
            size: 'small',
            onClick: () => openEditModal(row)
          },
          { default: () => '✏️ แก้ไข' }
        ),
        h(
          NButton,
          {
            text: true,
            type: 'error',
            size: 'small',
            onClick: () => openDeleteModal(row)
          },
          { default: () => '🗑️ ลบ' }
        )
      ])
    }
  }
])

onMounted(() => {
  loadProducts()
})

async function loadProducts() {
  try {
    loading.value = true
    errorMessage.value = null
    const includeInactive = showInactive.value === 'true'
    const response = await productsApi.getAdminProducts(
      (pagination.value.page - 1) * pagination.value.pageSize,
      pagination.value.pageSize,
      includeInactive
    )

    let filteredProducts = response.data

    // Filter by search query
    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase()
      filteredProducts = filteredProducts.filter(p =>
        p.name.toLowerCase().includes(query) ||
        (p.description?.toLowerCase() || '').includes(query)
      )
    }

    // Filter by category
    if (selectedCategory.value) {
      filteredProducts = filteredProducts.filter(p => p.category === selectedCategory.value)
    }

    products.value = filteredProducts
    pagination.value.pageCount = Math.ceil(response.total / pagination.value.pageSize)
  } catch (error: any) {
    const errorDetail = error.response?.data?.detail || 'ไม่สามารถโหลดสินค้าได้'
    errorMessage.value = errorDetail
    message.error(errorDetail)
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  pagination.value.page = 1
  loadProducts()
}

function handlePageChange(page: number) {
  pagination.value.page = page
  loadProducts()
}

function openCreateModal() {
  selectedProduct.value = null
  showFormModal.value = true
}

function openEditModal(product: Product) {
  selectedProduct.value = product
  showFormModal.value = true
}

function openDeleteModal(product: Product) {
  productToDelete.value = product
  showDeleteModal.value = true
}

async function confirmDelete() {
  if (!productToDelete.value) return

  try {
    await productsApi.deleteProduct(productToDelete.value.id)
    message.success('ลบสินค้าเรียบร้อย')
    showDeleteModal.value = false
    productToDelete.value = null
    loadProducts()
  } catch (error: any) {
    message.error(error.response?.data?.detail || 'ไม่สามารถลบสินค้าได้')
  }
}

function handleProductSaved() {
  showFormModal.value = false
  selectedProduct.value = null
  message.success('บันทึกสินค้าเรียบร้อย')
  loadProducts()
}
</script>

<style scoped>
.products-page {
  min-height: 100vh;
  background-color: #f5f5f5;
}

/* Mobile optimization */
@media (max-width: 640px) {
  .products-page {
    padding: 1rem;
  }

  .grid {
    grid-template-columns: 1fr;
  }
}
</style>
