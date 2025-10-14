<template>
  <div class="users-container">
    <n-space vertical :size="32">
      <div class="page-header">
        <n-h2>จัดการผู้ใช้</n-h2>
        <n-button type="primary" @click="showCreateModal = true" size="large">
          <template #icon>
            <n-icon>
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                <path fill="currentColor" d="M15 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm-9-2V7H4v3H1v2h3v3h2v-3h3v-2H6zm9 4c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
              </svg>
            </n-icon>
          </template>
          เพิ่มผู้ใช้
        </n-button>
      </div>

      <n-card :bordered="false" class="table-card">
        <n-data-table
          :columns="columns"
          :data="users"
          :loading="loading"
          :pagination="pagination"
          :bordered="false"
        />
      </n-card>
    </n-space>

    <!-- Create/Edit User Modal -->
    <n-modal
      v-model:show="showCreateModal"
      preset="card"
      :title="editingUser ? 'แก้ไขผู้ใช้' : 'เพิ่มผู้ใช้'"
      style="width: 600px; max-width: 90vw;"
      class="user-modal"
    >
      <n-form
        ref="formRef"
        :model="formValue"
        :rules="formRules"
        label-placement="top"
        :show-require-mark="false"
      >
        <n-space vertical :size="20">
          <n-form-item label="ชื่อผู้ใช้" path="username">
            <n-input
              v-model:value="formValue.username"
              placeholder="กรอกชื่อผู้ใช้"
              :disabled="!!editingUser"
              size="large"
            />
          </n-form-item>

          <n-form-item v-if="!editingUser" label="รหัสผ่าน" path="password">
            <n-input
              v-model:value="formValue.password"
              type="password"
              show-password-on="click"
              placeholder="กรอกรหัสผ่าน"
              size="large"
            />
          </n-form-item>

          <n-form-item label="ชื่อ-นามสกุล" path="full_name">
            <n-input
              v-model:value="formValue.full_name"
              placeholder="กรอกชื่อ-นามสกุล"
              size="large"
            />
          </n-form-item>

          <n-form-item label="บทบาท" path="role">
            <n-select
              v-model:value="formValue.role"
              :options="roleOptions"
              placeholder="เลือกบทบาท"
              size="large"
            />
          </n-form-item>

          <n-form-item label="Telegram User ID" path="telegram_user_id">
            <n-input
              v-model:value="formValue.telegram_user_id"
              placeholder="กรอก Telegram User ID (ถ้ามี)"
              size="large"
            />
          </n-form-item>

          <n-form-item label="สถานะ" path="is_active">
            <n-switch v-model:value="formValue.is_active">
              <template #checked>ใช้งาน</template>
              <template #unchecked>ระงับ</template>
            </n-switch>
          </n-form-item>
        </n-space>
      </n-form>

      <template #footer>
        <n-space justify="end" :size="12">
          <n-button @click="handleCancelEdit" size="large">ยกเลิก</n-button>
          <n-button type="primary" :loading="saving" @click="handleSaveUser" size="large">
            บันทึก
          </n-button>
        </n-space>
      </template>
    </n-modal>

    <!-- Delete Confirmation -->
    <n-modal
      v-model:show="showDeleteModal"
      preset="dialog"
      title="ยืนยันการลบ"
      content="คุณแน่ใจหรือไม่ว่าต้องการลบผู้ใช้นี้?"
      positive-text="ลบ"
      negative-text="ยกเลิก"
      @positive-click="handleConfirmDelete"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, h, onMounted } from 'vue'
import { useMessage, NButton, NSpace, NTag, NIcon } from 'naive-ui'
import type { DataTableColumns, FormInst, FormRules } from 'naive-ui'
import axios from '@/api/axios'
import type { User } from '@/stores/auth'

const message = useMessage()

// State
const users = ref<User[]>([])
const loading = ref(false)
const saving = ref(false)
const showCreateModal = ref(false)
const showDeleteModal = ref(false)
const editingUser = ref<User | null>(null)
const deletingUserId = ref<number | null>(null)

const formRef = ref<FormInst | null>(null)
const formValue = ref({
  username: '',
  password: '',
  full_name: '',
  role: 'reception' as 'admin' | 'reception' | 'housekeeping' | 'maintenance',
  telegram_user_id: '',
  is_active: true
})

// Role options
const roleOptions = [
  { label: 'ผู้ดูแลระบบ', value: 'admin' },
  { label: 'แผนกต้อนรับ', value: 'reception' },
  { label: 'แผนกแม่บ้าน', value: 'housekeeping' },
  { label: 'แผนกซ่อมบำรุง', value: 'maintenance' }
]

// Form rules
const formRules: FormRules = {
  username: [
    { required: true, message: 'กรุณากรอกชื่อผู้ใช้', trigger: 'blur' }
  ],
  password: [
    { required: !editingUser.value, message: 'กรุณากรอกรหัสผ่าน', trigger: 'blur' }
  ],
  full_name: [
    { required: true, message: 'กรุณากรอกชื่อ-นามสกุล', trigger: 'blur' }
  ],
  role: [
    { required: true, message: 'กรุณาเลือกบทบาท', trigger: 'change' }
  ]
}

// Pagination
const pagination = {
  pageSize: 10
}

// Columns
const columns: DataTableColumns<User> = [
  {
    title: 'ชื่อผู้ใช้',
    key: 'username'
  },
  {
    title: 'ชื่อ-นามสกุล',
    key: 'full_name'
  },
  {
    title: 'บทบาท',
    key: 'role',
    render: (row) => {
      const roleMap: Record<string, { text: string; type: 'success' | 'info' | 'warning' | 'error' }> = {
        ADMIN: { text: 'ผู้ดูแลระบบ', type: 'error' },
        admin: { text: 'ผู้ดูแลระบบ', type: 'error' },
        RECEPTION: { text: 'แผนกต้อนรับ', type: 'info' },
        reception: { text: 'แผนกต้อนรับ', type: 'info' },
        HOUSEKEEPING: { text: 'แผนกแม่บ้าน', type: 'success' },
        housekeeping: { text: 'แผนกแม่บ้าน', type: 'success' },
        MAINTENANCE: { text: 'แผนกซ่อมบำรุง', type: 'warning' },
        maintenance: { text: 'แผนกซ่อมบำรุง', type: 'warning' }
      }
      const role = roleMap[row.role] || { text: 'ไม่ทราบ', type: 'info' }
      return h(NTag, { type: role.type }, { default: () => role.text })
    }
  },
  {
    title: 'สถานะ',
    key: 'is_active',
    render: (row) => h(
      NTag,
      { type: row.is_active ? 'success' : 'error' },
      { default: () => row.is_active ? 'ใช้งาน' : 'ระงับ' }
    )
  },
  {
    title: 'การดำเนินการ',
    key: 'actions',
    render: (row) => h(
      NSpace,
      { size: 12 },
      {
        default: () => [
          h(
            NButton,
            {
              size: 'medium',
              onClick: () => handleEditUser(row)
            },
            { default: () => 'แก้ไข' }
          ),
          h(
            NButton,
            {
              size: 'medium',
              type: 'error',
              onClick: () => handleDeleteUser(row.id)
            },
            { default: () => 'ลบ' }
          )
        ]
      }
    )
  }
]

// Fetch users
async function fetchUsers() {
  loading.value = true
  try {
    const response = await axios.get<User[]>('/api/v1/users/')
    users.value = response.data
  } catch (error: any) {
    message.error(error.response?.data?.detail || 'ไม่สามารถโหลดข้อมูลผู้ใช้ได้')
  } finally {
    loading.value = false
  }
}

// Handle edit user
function handleEditUser(user: User) {
  editingUser.value = user
  formValue.value = {
    username: user.username,
    password: '',
    full_name: user.full_name,
    role: user.role.toLowerCase() as any, // Normalize to lowercase for form
    telegram_user_id: user.telegram_user_id || '',
    is_active: user.is_active
  }
  showCreateModal.value = true
}

// Handle delete user
function handleDeleteUser(userId: number) {
  deletingUserId.value = userId
  showDeleteModal.value = true
}

// Handle confirm delete
async function handleConfirmDelete() {
  if (!deletingUserId.value) return

  try {
    await axios.delete(`/api/v1/users/${deletingUserId.value}`)
    message.success('ลบผู้ใช้สำเร็จ')
    await fetchUsers()
  } catch (error: any) {
    message.error(error.response?.data?.detail || 'ไม่สามารถลบผู้ใช้ได้')
  } finally {
    showDeleteModal.value = false
    deletingUserId.value = null
  }
}

// Handle save user
async function handleSaveUser() {
  try {
    await formRef.value?.validate()
    saving.value = true

    const payload: any = {
      username: formValue.value.username,
      full_name: formValue.value.full_name,
      role: formValue.value.role,
      telegram_user_id: formValue.value.telegram_user_id || null,
      is_active: formValue.value.is_active
    }

    if (!editingUser.value && formValue.value.password) {
      payload.password = formValue.value.password
    }

    if (editingUser.value) {
      // Update user
      await axios.put(`/api/v1/users/${editingUser.value.id}`, payload)
      message.success('แก้ไขผู้ใช้สำเร็จ')
    } else {
      // Create user
      await axios.post('/api/v1/users/', payload)
      message.success('เพิ่มผู้ใช้สำเร็จ')
    }

    await fetchUsers()
    handleCancelEdit()
  } catch (error: any) {
    // Handle error message (could be string or array)
    let errorMsg = 'เกิดข้อผิดพลาด'
    if (error.response?.data?.detail) {
      const detail = error.response.data.detail
      if (Array.isArray(detail)) {
        // Pydantic validation error (array of errors)
        errorMsg = detail.map((err: any) => err.msg || err.message).join(', ')
      } else if (typeof detail === 'string') {
        // Simple string error
        errorMsg = detail
      }
    }
    message.error(errorMsg)
  } finally {
    saving.value = false
  }
}

// Handle cancel edit
function handleCancelEdit() {
  showCreateModal.value = false
  editingUser.value = null
  formValue.value = {
    username: '',
    password: '',
    full_name: '',
    role: 'reception',
    telegram_user_id: '',
    is_active: true
  }
}

// Lifecycle
onMounted(() => {
  fetchUsers()
})
</script>

<style scoped>
.users-container {
  padding: 32px;
  max-width: 1600px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 32px 40px;
  background: linear-gradient(135deg, #3338A0 0%, #2a2d80 100%);
  border-radius: 16px;
  box-shadow: 0 4px 16px rgba(51, 56, 160, 0.3);
}

.page-header h2 {
  margin: 0;
  color: #FCC61D !important;
  font-size: 32px;
  font-weight: 700;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.table-card {
  box-shadow: 0 4px 16px rgba(51, 56, 160, 0.15) !important;
}

:deep(.n-card) {
  border: 2px solid #3338A0;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(51, 56, 160, 0.15);
}

:deep(.n-card .n-card__content) {
  padding: 32px;
}

:deep(.n-data-table) {
  border-radius: 8px;
}

:deep(.n-data-table .n-data-table-thead .n-data-table-th) {
  background: linear-gradient(135deg, #3338A0 0%, #2a2d80 100%) !important;
  color: #FCC61D !important;
  font-weight: 700;
  font-size: 16px;
  padding: 20px 16px !important;
  border: none !important;
}

:deep(.n-data-table .n-data-table-tbody .n-data-table-td) {
  padding: 16px !important;
  font-size: 15px;
}

:deep(.n-data-table .n-data-table-tbody .n-data-table-tr:hover) {
  background: rgba(51, 56, 160, 0.05);
}

:deep(.n-modal .n-card-header) {
  background: linear-gradient(135deg, #3338A0 0%, #2a2d80 100%);
  color: #FCC61D !important;
  font-weight: 700;
  font-size: 22px;
  padding: 24px 32px;
}

:deep(.n-modal .n-card-header .n-card-header__main) {
  color: #FCC61D !important;
}

:deep(.n-modal .n-card-header .n-card-header__extra) {
  color: #FCC61D !important;
}

:deep(.n-modal .n-card__content) {
  padding: 32px !important;
}

:deep(.n-modal .n-card__footer) {
  padding: 20px 32px !important;
}

:deep(.n-dialog .n-dialog__title) {
  color: #3338A0 !important;
  font-weight: 700;
}

:deep(.n-dialog .n-dialog__content) {
  color: #3338A0 !important;
}

:deep(.n-form-item) {
  margin-bottom: 4px;
}

:deep(.n-form-item-label) {
  color: #3338A0 !important;
  font-weight: 600;
  font-size: 15px;
  margin-bottom: 8px;
}

:deep(.n-input) {
  font-size: 15px;
}

:deep(.n-tag) {
  font-weight: 600;
  padding: 6px 14px;
  font-size: 14px;
}

:deep(.n-button) {
  padding: 0 24px;
  font-size: 15px;
}

:deep(.n-button .n-button__content) {
  gap: 8px;
}

@media (max-width: 768px) {
  .users-container {
    padding: 20px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
    padding: 24px;
  }

  .page-header h2 {
    font-size: 24px;
  }

  :deep(.n-card .n-card__content) {
    padding: 20px;
  }
}
</style>
