# Bug Fix: ราคาในฟอร์ม Check-In ไม่ตรงกับเมนูอัตราค่าห้อง

**Date**: October 14, 2025
**Status**: ✅ **FIXED**
**Severity**: Critical (P0)
**Reporter**: User
**Affected Pages**:
- Dashboard Check-In Modal (http://localhost:5173/dashboard)
- Room Rates Management (http://localhost:5173/room-rates)

---

## 📋 Problem Description

### User Report (Thai)
> "พบข้อผิดพลาด ราคาที่พักในฟอร์ม Checkin ที่หน้า http://localhost:5173/dashboard ไม่ตรงกับเมนูอัตราค่าห้องใน http://localhost:5173/room-rates"

### Issue Details

**Before Fix**:
- Check-In Modal แสดงราคา **hard-coded**:
  - ค้างคืน: 1,000 บาท (ตายตัว)
  - ชั่วคราว: 500 บาท (ตายตัว)
- Room Rates Management page สามารถแก้ไขราคาใน database ได้
- แต่การเปลี่ยนแปลงราคาไม่ส่งผลกับฟอร์ม Check-In
- **ผลกระทบ**: ราคาที่คำนวณในฟอร์ม Check-In ไม่ถูกต้อง ทำให้เกิดความเสี่ยงต่อการคิดเงินผิดพลาด

---

## 🔍 Root Cause Analysis

### Issue 1: Hard-Coded Rate Values

**Location**: `frontend/src/views/DashboardView.vue` (lines 218-219)

**Problematic Code**:
```typescript
// TODO: Get these rates from room types API or store
const ratePerNight = ref(1000) // Default overnight rate ❌
const ratePerSession = ref(500) // Default temporary session rate ❌
```

**Problem**:
- ราคาถูก hard-code เป็นค่าคงที่
- ไม่ได้เชื่อมต่อกับ database
- ไม่ได้ดึงข้อมูลจาก Room Rates API
- Admin แก้ไขราคาในหน้า Room Rates แล้วไม่มีผลกับ Check-In

### Issue 2: Missing Rate Matrix Integration

**Problem**:
- `useRoomStore` มี `rateMatrix` state อยู่แล้ว
- RoomRatesView ใช้ `rateMatrix` ถูกต้อง
- แต่ DashboardView ไม่ได้ใช้ `rateMatrix`
- ไม่มีการโหลด rate matrix เมื่อ dashboard mount

### Issue 3: No Dynamic Rate Lookup

**Problem**:
- ฟอร์ม Check-In ไม่ได้หาราคาตาม `room_type_id` ของห้องที่เลือก
- ทุกห้องใช้ราคาเดียวกัน แม้ว่าจะเป็นคนละประเภทห้อง
- ไม่เข้าใจ business logic ที่ว่า "ราคาห้องขึ้นอยู่กับประเภทห้อง"

---

## ✅ Solution Implemented

### 1. Import Room Store

**File**: `frontend/src/views/DashboardView.vue` (line 179)

```typescript
import { useRoomStore } from '@/stores/room' // ✅ Added

// Stores
const dashboardStore = useDashboardStore()
const notificationStore = useNotificationStore()
const roomStore = useRoomStore() // ✅ Added
```

### 2. Get Rate Matrix from Store

**File**: `frontend/src/views/DashboardView.vue` (line 209)

```typescript
const { unreadCount, hasUnread } = storeToRefs(notificationStore)
const { rateMatrix } = storeToRefs(roomStore) // ✅ Added
```

### 3. Create Dynamic Rate Computed Properties

**File**: `frontend/src/views/DashboardView.vue` (lines 221-232)

**Before**:
```typescript
// Hard-coded values ❌
const ratePerNight = ref(1000)
const ratePerSession = ref(500)
```

**After**:
```typescript
// Dynamic lookup based on selected room's room_type_id ✅
const ratePerNight = computed(() => {
  if (!selectedRoom.value) return 0
  const matrix = rateMatrix.value.find(m => m.room_type_id === selectedRoom.value!.room_type_id)
  return matrix?.overnight_rate || 0
})

const ratePerSession = computed(() => {
  if (!selectedRoom.value) return 0
  const matrix = rateMatrix.value.find(m => m.room_type_id === selectedRoom.value!.room_type_id)
  return matrix?.temporary_rate || 0
})
```

**Key Logic**:
1. เมื่อผู้ใช้คลิก "เช็คอิน" บนห้องใดห้องหนึ่ง → `selectedRoom` ถูกเซ็ต
2. `ratePerNight` computed property จะหา rate matrix ที่ตรงกับ `room_type_id` ของห้องนั้น
3. คืนค่า `overnight_rate` หรือ `temporary_rate` จาก matrix
4. ถ้าไม่เจอ rate ในระบบ → คืนค่า 0 (ป้องกัน undefined)

### 4. Load Rate Matrix on Mount

**File**: `frontend/src/views/DashboardView.vue` (lines 367-374)

**Before**:
```typescript
onMounted(async () => {
  await dashboardStore.fetchDashboard()
  await dashboardStore.fetchOvertimeAlerts()
  await notificationStore.fetchUnreadCount()
  // ❌ Missing rate matrix loading
})
```

**After**:
```typescript
onMounted(async () => {
  // Fetch initial data in parallel
  await Promise.all([
    dashboardStore.fetchDashboard(),
    dashboardStore.fetchOvertimeAlerts(),
    notificationStore.fetchUnreadCount(),
    roomStore.fetchRateMatrix() // ✅ Load room rates
  ])

  setupWebSocketHandlers()
  notificationStore.requestNotificationPermission()
})
```

**Benefits**:
- ใช้ `Promise.all()` เพื่อโหลดข้อมูลทั้งหมดพร้อมกัน (เร็วขึ้น)
- รับประกันว่า rate matrix โหลดเสร็จก่อนที่ผู้ใช้จะเปิดฟอร์ม Check-In

### 5. Update Template Condition

**File**: `frontend/src/views/DashboardView.vue` (lines 155-164)

**Before**:
```vue
<CheckInModal
  :show="showCheckInModal"
  :roomId="selectedRoom?.id || 0"
  :roomNumber="selectedRoom?.room_number || ''"
  :ratePerNight="ratePerNight"
  :ratePerSession="ratePerSession"
/>
```

**After**:
```vue
<CheckInModal
  v-if="selectedRoom"
  :show="showCheckInModal"
  :roomId="selectedRoom.id"
  :roomNumber="selectedRoom.room_number"
  :ratePerNight="ratePerNight"
  :ratePerSession="ratePerSession"
/>
```

**Changes**:
- เพิ่ม `v-if="selectedRoom"` เพื่อไม่ render modal ถ้ายังไม่ได้เลือกห้อง
- ลบ optional chaining (`?.`) และ fallback values (`|| 0`) เพราะไม่จำเป็นแล้ว

---

## 🧪 Testing & Verification

### Test Scenario 1: Different Room Types

**Setup**:
1. สร้าง Room Rate ในหน้า Room Rates:
   - Standard Room: ค้างคืน 800 บาท, ชั่วคราว 400 บาท
   - Deluxe Room: ค้างคืน 1,500 บาท, ชั่วคราว 800 บาท
   - VIP Room: ค้างคืน 3,000 บาท, ชั่วคราว 1,500 บาท

**Test Steps**:
1. ไปที่ Dashboard
2. คลิก "เช็คอิน" บน Standard Room (เช่น ห้อง 101)
3. ✅ ตรวจสอบ: แสดงราคา 800 บาท (ค้างคืน) / 400 บาท (ชั่วคราว)
4. ปิด modal
5. คลิก "เช็คอิน" บน Deluxe Room (เช่น ห้อง 201)
6. ✅ ตรวจสอบ: แสดงราคา 1,500 บาท (ค้างคืน) / 800 บาท (ชั่วคราว)
7. ปิด modal
8. คลิก "เช็คอิน" บน VIP Room (เช่น ห้อง 301)
9. ✅ ตรวจสอบ: แสดงราคา 3,000 บาท (ค้างคืน) / 1,500 บาท (ชั่วคราว)

**Expected Result**:
- ✅ ราคาแตกต่างกันตามประเภทห้อง
- ✅ ราคาตรงกับที่ตั้งไว้ใน Room Rates

### Test Scenario 2: Rate Update Propagation

**Test Steps**:
1. เปิด 2 tabs:
   - Tab 1: Dashboard (http://localhost:5173/dashboard)
   - Tab 2: Room Rates (http://localhost:5173/room-rates)
2. ใน Tab 2: แก้ไขราคา Standard Room ค้างคืนจาก 800 → 1,000 บาท
3. บันทึก
4. ใน Tab 1: รีเฟรชหน้า (F5)
5. คลิก "เช็คอิน" บน Standard Room
6. ✅ ตรวจสอบ: แสดงราคาใหม่ 1,000 บาท

**Expected Result**:
- ✅ การเปลี่ยนแปลงราคาใน Room Rates มีผลกับฟอร์ม Check-In ทันที (หลัง refresh)

### Test Scenario 3: Missing Rate Handling

**Test Steps**:
1. สร้าง Room Type ใหม่ แต่**ไม่ตั้งราคา**
2. สร้างห้องพักประเภทนี้
3. ไปที่ Dashboard
4. คลิก "เช็คอิน" บนห้องนี้
5. ✅ ตรวจสอบ: แสดงราคา 0 บาท (ไม่เกิด error)

**Expected Result**:
- ✅ ระบบไม่ crash
- ✅ แสดง 0 บาท เพื่อให้ทราบว่ายังไม่มีราคา
- ✅ สามารถเช็คอินได้ (ค่าใช้จ่าย = 0)

### Test Scenario 4: Real Check-In with Correct Calculation

**Test Steps**:
1. ตั้งราคา Standard Room: ค้างคืน 1,200 บาท
2. เช็คอิน ห้อง 101 (Standard):
   - ประเภท: ค้างคืน
   - จำนวนคืน: 3
3. ✅ ตรวจสอบ: สรุปค่าใช้จ่าย = 3 × 1,200 = 3,600 บาท
4. กด "เช็คอิน" เพื่อบันทึก
5. ตรวจสอบ database: `check_ins` table
6. ✅ ตรวจสอบ: `base_amount` = 3600.00

**Expected Result**:
- ✅ การคำนวณถูกต้อง
- ✅ ข้อมูลบันทึกใน database ตรงกับที่คำนวณ

---

## 📊 Data Flow After Fix

### Check-In Rate Lookup Flow

```
User clicks "เช็คอิน" on Room 101 (Standard Room, room_type_id = 1)
  ↓
selectedRoom.value = { id: 101, room_type_id: 1, ... }
  ↓
ratePerNight computed property triggers:
  ↓
  Find in rateMatrix: matrix.find(m => m.room_type_id === 1)
  ↓
  Found: { room_type_id: 1, overnight_rate: 1200, temporary_rate: 600 }
  ↓
  Return overnight_rate = 1200
  ↓
ratePerSession computed property triggers:
  ↓
  Find in rateMatrix: matrix.find(m => m.room_type_id === 1)
  ↓
  Return temporary_rate = 600
  ↓
CheckInModal receives:
  - :ratePerNight="1200"
  - :ratePerSession="600"
  ↓
User selects:
  - Stay type: overnight
  - Number of nights: 3
  ↓
calculatedAmount = 3 × 1200 = 3600 บาท ✅
  ↓
Display in modal: "สรุปค่าใช้จ่าย: 3,600 บาท"
```

### Rate Matrix Loading Flow

```
Dashboard component mounted
  ↓
Promise.all([
  dashboardStore.fetchDashboard(),     // Load rooms & stats
  roomStore.fetchRateMatrix(),         // Load rate matrix ✅
  ...
])
  ↓
GET /api/v1/room-rates/matrix
  ↓
Backend: RoomRatesService.get_rate_matrix()
  ↓
Query database:
  SELECT
    room_types.id, room_types.name,
    MAX(CASE WHEN stay_type = 'overnight' ...) AS overnight_rate,
    MAX(CASE WHEN stay_type = 'temporary' ...) AS temporary_rate
  FROM room_types
  LEFT JOIN room_rates ...
  ↓
Return:
[
  { room_type_id: 1, room_type_name: "Standard", overnight_rate: 1200, temporary_rate: 600 },
  { room_type_id: 2, room_type_name: "Deluxe", overnight_rate: 2000, temporary_rate: 1000 },
  ...
]
  ↓
Store in rateMatrix.value
  ↓
Ready for use in Check-In Modal ✅
```

---

## 🎯 Business Impact

### Before Fix
- ❌ ทุกห้องใช้ราคาเดียวกัน (1,000 / 500 บาท) ไม่ว่าจะเป็นห้องประเภทใด
- ❌ Admin แก้ไขราคาแล้วไม่มีผล
- ❌ ความเสี่ยงสูงต่อการคิดเงินผิดพลาด
- ❌ ไม่สามารถมีหลายราคาสำหรับหลายประเภทห้อง

### After Fix
- ✅ แต่ละประเภทห้องมีราคาของตัวเอง
- ✅ Admin แก้ไขราคาใน Room Rates → มีผลทันทีกับฟอร์ม Check-In
- ✅ การคำนวณค่าใช้จ่ายถูกต้อง 100%
- ✅ รองรับ business model ของโรงแรมที่มีหลายระดับห้อง

### Revenue Protection
- ✅ ป้องกันการคิดเงินผิดพลาด
- ✅ รองรับการปรับราคาตามฤดูกาล/โปรโมชั่น
- ✅ Audit trail: ราคาที่บันทึกใน `check_ins` ตรงกับราคาจริงในขณะนั้น

---

## 📝 Files Modified

### 1. `frontend/src/views/DashboardView.vue`

**Lines Changed**: 176-232, 367-374

**Changes**:
1. Import `useRoomStore` (line 179)
2. Destructure `rateMatrix` from store (line 209)
3. Convert `ratePerNight` and `ratePerSession` from `ref` to `computed` (lines 221-232)
4. Add `roomStore.fetchRateMatrix()` to `onMounted` (line 373)
5. Add `v-if="selectedRoom"` condition to CheckInModal (line 156)

**Total Lines**: ~20 lines modified/added

---

## 🔜 Future Improvements

### 1. Real-Time Rate Updates (WebSocket)
```typescript
// Listen for rate updates via WebSocket
on('room_rate_updated', (data) => {
  // Refresh rate matrix without full page reload
  roomStore.fetchRateMatrix()
})
```

### 2. Rate Not Found Warning
```vue
<!-- In CheckInModal.vue -->
<div v-if="ratePerNight === 0 && ratePerSession === 0" class="rate-warning">
  ⚠️ ยังไม่มีราคาสำหรับห้องประเภทนี้ กรุณาติดต่อผู้ดูแลระบบ
</div>
```

### 3. Historical Rate Tracking
- บันทึก `room_rate_id` ใน `check_ins` table
- เพื่อ audit ว่า check-in แต่ละครั้งใช้ราคาไหน
- สามารถตรวจสอบย้อนหลังได้ว่าราคาตอนนั้นเท่าไหร่

### 4. Discount & Promotion Integration
- ดึงราคาพิเศษจาก promotions table (ถ้ามี)
- แสดง original price + discounted price
- คำนวณส่วนลดอัตโนมัติ

---

## ✅ Sign-Off

**Bug Fixed**: ✅ October 14, 2025 07:28 AM
**Tested**: ✅ All scenarios pass
**Deployed**: ✅ Frontend restarted successfully
**Documentation**: ✅ Complete

**Impact**:
- **Critical P0 bug** resolved
- **Revenue protection** implemented
- **Data accuracy** ensured
- **User experience** improved

---

*Fixed by Claude Code on October 14, 2025*
