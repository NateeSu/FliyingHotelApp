<template>
  <div class="customers-view">
    <n-card title="ข้อมูลลูกค้า">
      <template #header-extra>
        <n-button type="primary" @click="showCreateModal = true">
          <template #icon>
            <n-icon><PersonAddOutline /></n-icon>
          </template>
          เพิ่มลูกค้าใหม่
        </n-button>
      </template>

      <!-- Search -->
      <n-space vertical :size="16">
        <n-input
          v-model:value="searchQuery"
          placeholder="ค้นหาชื่อหรือเบอร์โทรศัพท์"
          clearable
          @input="handleSearch"
        >
          <template #prefix>
            <n-icon><SearchOutline /></n-icon>
          </template>
        </n-input>

        <!-- Customer Table -->
        <n-data-table
          :columns="columns"
          :data="customers"
          :loading="loading"
          :pagination="pagination"
          :bordered="false"
          striped
        />
      </n-space>
    </n-card>

    <!-- Create/Edit Modal -->
    <CustomerFormModal
      v-model:show="showCreateModal"
      :customer="selectedCustomer"
      @success="handleSuccess"
    />

    <!-- Customer Detail Modal -->
    <n-modal
      v-model:show="showDetailModal"
      preset="card"
      title="ข้อมูลลูกค้า"
      style="width: 600px"
    >
      <n-descriptions
        v-if="selectedCustomer"
        :column="1"
        bordered
        label-placement="left"
      >
        <n-descriptions-item label="ชื่อ-นามสกุล">
          {{ selectedCustomer.full_name }}
        </n-descriptions-item>
        <n-descriptions-item label="เบอร์โทรศัพท์">
          {{ selectedCustomer.phone_number }}
        </n-descriptions-item>
        <n-descriptions-item label="อีเมล" v-if="selectedCustomer.email">
          {{ selectedCustomer.email }}
        </n-descriptions-item>
        <n-descriptions-item label="เลขบัตรประชาชน" v-if="selectedCustomer.id_card_number">
          {{ selectedCustomer.id_card_number }}
        </n-descriptions-item>
        <n-descriptions-item label="ที่อยู่" v-if="selectedCustomer.address">
          {{ selectedCustomer.address }}
        </n-descriptions-item>
        <n-descriptions-item label="จำนวนครั้งที่เข้าพัก">
          {{ selectedCustomer.total_visits }} ครั้ง
        </n-descriptions-item>
        <n-descriptions-item label="ยอดใช้จ่ายรวม">
          {{ formatCurrency(selectedCustomer.total_spent) }}
        </n-descriptions-item>
        <n-descriptions-item label="ครั้งล่าสุด" v-if="selectedCustomer.last_visit_date">
          {{ formatDate(selectedCustomer.last_visit_date) }}
        </n-descriptions-item>
        <n-descriptions-item label="หมายเหตุ" v-if="selectedCustomer.notes">
          {{ selectedCustomer.notes }}
        </n-descriptions-item>
      </n-descriptions>

      <template #footer>
        <n-space justify="end">
          <n-button @click="showDetailModal = false">ปิด</n-button>
          <n-button type="primary" @click="handleEdit">แก้ไข</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, h } from 'vue'
import {
  NCard,
  NButton,
  NIcon,
  NInput,
  NSpace,
  NDataTable,
  NModal,
  NDescriptions,
  NDescriptionsItem,
  NTag,
  type DataTableColumns
} from 'naive-ui'
import {
  PersonAddOutline,
  SearchOutline,
  Eye,
  CreateOutline
} from '@vicons/ionicons5'
import { useCustomerStore } from '@/stores/customer'
import CustomerFormModal from '@/components/CustomerFormModal.vue'
import type { CustomerResponse } from '@/api/customers'

const customerStore = useCustomerStore()

// State
const searchQuery = ref('')
const showCreateModal = ref(false)
const showDetailModal = ref(false)
const selectedCustomer = ref<CustomerResponse | null>(null)
const loading = ref(false)

// Pagination
const pagination = {
  pageSize: 20
}

// Table columns
const columns: DataTableColumns<CustomerResponse> = [
  {
    title: 'ชื่อ-นามสกุล',
    key: 'full_name',
    minWidth: 200
  },
  {
    title: 'เบอร์โทรศัพท์',
    key: 'phone_number',
    width: 150
  },
  {
    title: 'อีเมล',
    key: 'email',
    width: 200,
    render: (row) => row.email || '-'
  },
  {
    title: 'จำนวนครั้ง',
    key: 'total_visits',
    width: 120,
    align: 'center',
    render: (row) => h(NTag, { type: 'info', size: 'small' }, { default: () => `${row.total_visits} ครั้ง` })
  },
  {
    title: 'ยอดใช้จ่ายรวม',
    key: 'total_spent',
    width: 150,
    align: 'right',
    render: (row) => formatCurrency(row.total_spent)
  },
  {
    title: 'การจัดการ',
    key: 'actions',
    width: 150,
    align: 'center',
    render: (row) => h(
      NSpace,
      { justify: 'center' },
      {
        default: () => [
          h(
            NButton,
            {
              size: 'small',
              onClick: () => handleViewDetail(row)
            },
            {
              icon: () => h(NIcon, null, { default: () => h(Eye) }),
              default: () => 'ดู'
            }
          ),
          h(
            NButton,
            {
              size: 'small',
              type: 'primary',
              onClick: () => handleEditCustomer(row)
            },
            {
              icon: () => h(NIcon, null, { default: () => h(CreateOutline) }),
              default: () => 'แก้ไข'
            }
          )
        ]
      }
    )
  }
]

// Computed
const customers = ref<CustomerResponse[]>([])

// Methods
function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('th-TH', {
    style: 'currency',
    currency: 'THB'
  }).format(amount)
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('th-TH', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

let searchTimeout: ReturnType<typeof setTimeout> | null = null
function handleSearch() {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }

  searchTimeout = setTimeout(async () => {
    if (searchQuery.value.trim()) {
      loading.value = true
      try {
        const results = await customerStore.searchCustomers(searchQuery.value)
        customers.value = results as any
      } finally {
        loading.value = false
      }
    } else {
      await loadCustomers()
    }
  }, 300)
}

function handleViewDetail(customer: CustomerResponse) {
  selectedCustomer.value = customer
  showDetailModal.value = true
}

function handleEditCustomer(customer: CustomerResponse) {
  selectedCustomer.value = customer
  showCreateModal.value = true
}

function handleEdit() {
  showDetailModal.value = false
  showCreateModal.value = true
}

async function handleSuccess() {
  await loadCustomers()
  selectedCustomer.value = null
}

async function loadCustomers() {
  loading.value = true
  try {
    await customerStore.fetchCustomers()
    customers.value = customerStore.customers
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadCustomers()
})
</script>

<style scoped>
.customers-view {
  padding: 24px;
}
</style>