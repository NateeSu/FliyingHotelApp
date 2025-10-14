# Bug Fix: Role Display Issue

## วันที่แก้ไข
2025-10-12

## ปัญหา
เมื่อ login เข้าสู่ระบบ พบว่าการแสดงบทบาท (Role) แสดงเป็น **"ไม่ทราบ"** แม้ว่าผู้ใช้จะเป็น admin

## สาเหตุ
Backend API ส่งค่า `role` มาเป็น **lowercase** (`"admin"`, `"reception"`, etc.) แต่ Frontend กำลังมองหาค่าเป็น **UPPERCASE** (`"ADMIN"`, `"RECEPTION"`, etc.)

### ตัวอย่าง Response จาก Backend:
```json
{
  "user": {
    "username": "admin",
    "role": "admin",  // ← lowercase
    "full_name": "ผู้ดูแลระบบ"
  }
}
```

### การตรวจสอบ Frontend:
```typescript
// เดิม - จะไม่เจอเพราะมองหา UPPERCASE เท่านั้น
const roleMap = {
  ADMIN: 'ผู้ดูแลระบบ',
  RECEPTION: 'แผนกต้อนรับ',
  ...
}
```

## การแก้ไข

### 1. ไฟล์: `frontend/src/stores/auth.ts`

#### เปลี่ยน User Interface
```typescript
// Before
export interface User {
  role: 'ADMIN' | 'RECEPTION' | 'HOUSEKEEPING' | 'MAINTENANCE'
}

// After
export interface User {
  role: string // Support both uppercase and lowercase from backend
}
```

#### แก้ไข Computed Properties
```typescript
// Before
const isAdmin = computed(() => user.value?.role === 'ADMIN')
const isReception = computed(() => user.value?.role === 'RECEPTION')
const isHousekeeping = computed(() => user.value?.role === 'HOUSEKEEPING')
const isMaintenance = computed(() => user.value?.role === 'MAINTENANCE')

// After - ใช้ toLowerCase() เพื่อ normalize
const isAdmin = computed(() => user.value?.role?.toLowerCase() === 'admin')
const isReception = computed(() => user.value?.role?.toLowerCase() === 'reception')
const isHousekeeping = computed(() => user.value?.role?.toLowerCase() === 'housekeeping')
const isMaintenance = computed(() => user.value?.role?.toLowerCase() === 'maintenance')
```

#### แก้ไข hasRole Function
```typescript
// Before
function hasRole(roles: string[]): boolean {
  if (!user.value) return false
  return roles.includes(user.value.role)
}

// After - normalize ทั้ง user role และ roles array
function hasRole(roles: string[]): boolean {
  if (!user.value) return false
  const userRole = user.value.role.toLowerCase()
  const normalizedRoles = roles.map(r => r.toLowerCase())
  return normalizedRoles.includes(userRole)
}
```

### 2. ไฟล์: `frontend/src/views/HomeView.vue`

#### แก้ไข getRoleText Function
```typescript
// Before - มีเฉพาะ UPPERCASE
function getRoleText(role?: string): string {
  const roleMap: Record<string, string> = {
    ADMIN: 'ผู้ดูแลระบบ',
    RECEPTION: 'แผนกต้อนรับ',
    HOUSEKEEPING: 'แผนกแม่บ้าน',
    MAINTENANCE: 'แผนกซ่อมบำรุง'
  }
  return roleMap[role || ''] || 'ไม่ทราบ'
}

// After - รองรับทั้ง uppercase และ lowercase
function getRoleText(role?: string): string {
  const roleMap: Record<string, string> = {
    ADMIN: 'ผู้ดูแลระบบ',
    admin: 'ผู้ดูแลระบบ',
    RECEPTION: 'แผนกต้อนรับ',
    reception: 'แผนกต้อนรับ',
    HOUSEKEEPING: 'แผนกแม่บ้าน',
    housekeeping: 'แผนกแม่บ้าน',
    MAINTENANCE: 'แผนกซ่อมบำรุง',
    maintenance: 'แผนกซ่อมบำรุง'
  }
  return roleMap[role || ''] || 'ไม่ทราบ'
}
```

#### แก้ไข getRoleColor Function
```typescript
// Before
function getRoleColor(role?: string): 'success' | 'info' | 'warning' | 'error' {
  const colorMap: Record<string, 'success' | 'info' | 'warning' | 'error'> = {
    ADMIN: 'error',
    RECEPTION: 'info',
    HOUSEKEEPING: 'success',
    MAINTENANCE: 'warning'
  }
  return colorMap[role || ''] || 'info'
}

// After - normalize ด้วย toUpperCase()
function getRoleColor(role?: string): 'success' | 'info' | 'warning' | 'error' {
  const roleKey = role?.toUpperCase()
  const colorMap: Record<string, 'success' | 'info' | 'warning' | 'error'> = {
    ADMIN: 'error',
    RECEPTION: 'info',
    HOUSEKEEPING: 'success',
    MAINTENANCE: 'warning'
  }
  return colorMap[roleKey || ''] || 'info'
}
```

### 3. ไฟล์: `frontend/src/views/UsersView.vue`

#### แก้ไข Role Mapping ใน Data Table
```typescript
// Before - มีเฉพาะ UPPERCASE
const roleMap: Record<string, { text: string; type: ... }> = {
  ADMIN: { text: 'ผู้ดูแลระบบ', type: 'error' },
  RECEPTION: { text: 'แผนกต้อนรับ', type: 'info' },
  HOUSEKEEPING: { text: 'แผนกแม่บ้าน', type: 'success' },
  MAINTENANCE: { text: 'แผนกซ่อมบำรุง', type: 'warning' }
}

// After - รองรับทั้ง uppercase และ lowercase
const roleMap: Record<string, { text: string; type: ... }> = {
  ADMIN: { text: 'ผู้ดูแลระบบ', type: 'error' },
  admin: { text: 'ผู้ดูแลระบบ', type: 'error' },
  RECEPTION: { text: 'แผนกต้อนรับ', type: 'info' },
  reception: { text: 'แผนกต้อนรับ', type: 'info' },
  HOUSEKEEPING: { text: 'แผนกแม่บ้าน', type: 'success' },
  housekeeping: { text: 'แผนกแม่บ้าน', type: 'success' },
  MAINTENANCE: { text: 'แผนกซ่อมบำรุง', type: 'warning' },
  maintenance: { text: 'แผนกซ่อมบำรุง', type: 'warning' }
}
```

#### แก้ไข handleEditUser Function
```typescript
// Before
function handleEditUser(user: User) {
  formValue.value = {
    ...
    role: user.role,
    ...
  }
}

// After - normalize เป็น UPPERCASE สำหรับ form
function handleEditUser(user: User) {
  formValue.value = {
    ...
    role: user.role.toUpperCase() as any, // Normalize to uppercase for form
    ...
  }
}
```

## สรุปไฟล์ที่แก้ไข

1. ✅ `frontend/src/stores/auth.ts`
   - User interface: role type เป็น string
   - Computed properties: ใช้ toLowerCase()
   - hasRole(): normalize array

2. ✅ `frontend/src/views/HomeView.vue`
   - getRoleText(): รองรับทั้ง 2 case
   - getRoleColor(): ใช้ toUpperCase()

3. ✅ `frontend/src/views/UsersView.vue`
   - Role mapping: เพิ่ม lowercase keys
   - handleEditUser(): normalize ก่อนใส่ form

## วิธีทดสอบ

### 1. ทดสอบ Login
```bash
# Login with admin account
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Response should show:
{
  "user": {
    "role": "admin"  // lowercase
  }
}
```

### 2. ทดสอบ Frontend
1. เปิด browser ไปที่ http://localhost:5173
2. Login ด้วย admin/admin123
3. ตรวจสอบหน้า Home:
   - ✅ Welcome header แสดง "ผู้ดูแลระบบ" (ไม่ใช่ "ไม่ทราบ")
   - ✅ Card ข้อมูลผู้ใช้แสดงบทบาท "ผู้ดูแลระบบ" พร้อม tag สีแดง
   - ✅ เมนู "จัดการผู้ใช้" แสดง (เพราะ isAdmin = true)

### 3. ทดสอบ User Management
1. คลิกไปที่ "จัดการผู้ใช้"
2. ตรวจสอบตาราง:
   - ✅ คอลัมน์ "บทบาท" แสดง "ผู้ดูแลระบบ"
   - ✅ Tag สีแดงแสดงถูกต้อง
3. คลิก "แก้ไข" บน admin user:
   - ✅ Dropdown บทบาทแสดง "ผู้ดูแลระบบ" (ADMIN)
   - ✅ สามารถบันทึกได้

## ผลลัพธ์

### ก่อนแก้ไข:
- ❌ บทบาทแสดง "ไม่ทราบ"
- ❌ เมนู "จัดการผู้ใช้" ไม่แสดง (isAdmin = false)
- ❌ Tag ไม่แสดงสีที่ถูกต้อง

### หลังแก้ไข:
- ✅ บทบาทแสดง "ผู้ดูแลระบบ" ถูกต้อง
- ✅ เมนู "จัดการผู้ใช้" แสดง (isAdmin = true)
- ✅ Tag แสดงสีแดงถูกต้อง
- ✅ ทุกฟังก์ชันทำงานปกติ

## Best Practices ที่ได้เรียนรู้

### 1. Case-Insensitive Comparison
เมื่อเปรียบเทียบ string ที่อาจมาจาก source ต่างกัน ควร normalize ก่อนเสมอ:
```typescript
// Good
if (role.toLowerCase() === 'admin') { ... }

// Bad
if (role === 'admin') { ... } // อาจไม่ตรงกับ 'ADMIN'
```

### 2. Defensive Programming
สร้าง mapping ที่รองรับทั้ง uppercase และ lowercase:
```typescript
const roleMap = {
  ADMIN: 'ผู้ดูแลระบบ',
  admin: 'ผู้ดูแลระบบ',  // รองรับทั้ง 2 แบบ
  ...
}
```

### 3. Type Safety
ใช้ string type แทน union type เมื่อต้องรองรับหลาย format:
```typescript
// Flexible
role: string

// Rigid
role: 'ADMIN' | 'RECEPTION'  // จะ error ถ้าได้ 'admin'
```

### 4. Normalization Points
Normalize data ที่ boundaries:
- Input: normalize ก่อนส่ง API
- Output: normalize หลังได้รับจาก API
- Comparison: normalize ก่อนเปรียบเทียบ

## Alternative Solutions (ไม่ได้ใช้)

### Option 1: แก้ Backend
แก้ backend ให้ส่ง UPPERCASE เสมอ:
```python
# backend/app/schemas/user.py
class UserResponse(BaseModel):
    role: str

    @validator('role')
    def uppercase_role(cls, v):
        return v.upper()
```
**ข้อเสีย**: ต้องแก้ backend และ redeploy

### Option 2: Transform ใน Axios Interceptor
```typescript
axios.interceptors.response.use(response => {
  if (response.data.user?.role) {
    response.data.user.role = response.data.user.role.toUpperCase()
  }
  return response
})
```
**ข้อเสีย**: Global effect, อาจกระทบส่วนอื่น

### Option 3 (ที่เลือกใช้): Frontend Flexible
Frontend รองรับทั้ง uppercase และ lowercase
**ข้อดี**:
- ไม่ต้องแก้ backend
- Forward compatible
- Defensive programming

## Prevention

### 1. API Contract Testing
เพิ่ม test ตรวจสอบ format ของ role:
```typescript
describe('Login API', () => {
  it('should return role in expected format', async () => {
    const response = await login('admin', 'admin123')
    expect(['admin', 'ADMIN']).toContain(response.user.role)
  })
})
```

### 2. Type Guards
สร้าง type guard สำหรับ validate role:
```typescript
function isValidRole(role: string): boolean {
  const validRoles = ['admin', 'reception', 'housekeeping', 'maintenance']
  return validRoles.includes(role.toLowerCase())
}
```

### 3. Documentation
เขียนเอกสาร API specification ชัดเจน:
```yaml
# api-spec.yaml
User:
  role:
    type: string
    enum: [admin, reception, housekeeping, maintenance]
    description: "Role in lowercase"
```

---

**แก้ไขโดย**: Claude Code
**วันที่**: 2025-10-12
**สถานะ**: ✅ แก้ไขเสร็จสมบูรณ์
**Tested**: ✅ ทดสอบผ่านแล้ว
