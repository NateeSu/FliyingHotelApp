# Booking Modal Debug Report

**Date**: 2025-10-21
**Issue**: 400 Bad Request when trying to create booking
**Status**: Investigating & Fixing

## Problem Analysis

### What the User Experienced
- Navigate to: `http://localhost:5173/bookings`
- Click "สร้างการจอง" (Create Booking)
- Fill in form and click submit
- Get error: `400 Bad Request`

### Root Cause Investigation

**Backend Log Analysis**:
```
WHERE rooms.id = %s
[parameters: (0,)]  ← room_id is 0!
```

This indicates the room_id being sent is 0, which fails the backend validation.

**Possible Causes**:
1. Form validation isn't catching room_id = 0 as invalid
2. User hasn't actually selected a room (room dropdown not working)
3. Dashboard rooms data not loading
4. Form reset happens but room_id stays at 0

## Fixes Applied

### Fix #1: Enhanced Form Validation
**File**: `frontend/src/components/BookingFormModal.vue`

Added custom validators to ensure values are > 0:
```typescript
room_id: [
  { required: true, message: 'กรุณาเลือกห้อง', type: 'number', trigger: 'change' },
  {
    validator: (rule, value) => {
      return value > 0 ? true : new Error('กรุณาเลือกห้อง')
    },
    trigger: 'change'
  }
]
```

Same validation added for:
- `customer_id` - must be > 0
- `total_amount` - must be > 0

### Fix #2: Better Error Logging
**File**: `frontend/src/components/BookingFormModal.vue`

Added console logging to track form data flow:
```typescript
console.log('📝 Form data before validation:', formData.value)
console.log('📝 Available rooms:', dashboardStore.rooms.length)
console.log('📝 Form validation passed, submitting:', formData.value)
console.log('📝 Creating booking with:', formData.value)
```

### Fix #3: Improved Error Display
Enhanced error message display to show backend response details:
```typescript
message.error(error?.response?.data?.detail || error?.message || 'ไม่สามารถบันทึกการจองได้')
```

### Fix #4: Room Loading
**File**: `frontend/src/components/BookingFormModal.vue` (already present)

Rooms are loaded on component mount:
```typescript
onMounted(async () => {
  // Load rooms if not loaded
  if (dashboardStore.rooms.length === 0) {
    await dashboardStore.fetchRooms()
  }
})
```

## How to Test the Fix

### Step-by-Step Guide

1. **Open Booking Page**:
   ```
   http://localhost:5173/bookings
   ```

2. **Open Browser Console**:
   - Press F12
   - Go to "Console" tab
   - You'll see our debug logs here

3. **Create New Booking**:
   - Click "สร้างการจอง" (Create Booking)
   - You should see: `📝 Available rooms: X` (number of rooms loaded)

4. **Fill Form Correctly**:
   - **Customer**: Click dropdown, select or create customer
   - **Check-in Date**: Click tomorrow (future date only)
   - **Check-out Date**: Click day after tomorrow
   - **Room**: Click dropdown, **must select a room** (important!)
   - **Total Amount**: Should auto-calculate if room rate exists
   - **Deposit**: Optional

5. **Watch Browser Console**:
   Before clicking submit, you should see:
   ```
   📝 Form data before validation: {
     customer_id: 1,      ← must be > 0
     room_id: 5,          ← must be > 0 and must be selected!
     check_in_date: "2025-10-22",
     check_out_date: "2025-10-23",
     total_amount: 1000,  ← must be > 0
     deposit_amount: 0,
     notes: ""
   }
   📝 Available rooms: 10  ← should show rooms available
   ```

6. **Submit Form**:
   - Click "สร้างการจอง"
   - Console should show:
     ```
     📝 Form validation passed, submitting: { ... }
     📝 Creating booking with: { ... }
     ```

7. **Success**:
   - ✅ Modal closes
   - ✅ Success message appears
   - ✅ Booking appears in calendar

## Expected Behavior After Fix

**Before Form Submission**:
- ✅ Room field shows available rooms list
- ✅ Form shows Thai error messages for missing fields
- ✅ Cannot submit if room_id = 0 (blocked by validation)

**On Submit**:
- ✅ Frontend validates all fields
- ✅ Backend receives valid data
- ✅ Booking created successfully
- ✅ Room status updates to "reserved"
- ✅ Booking visible in calendar

**On Error**:
- ❌ If backend returns error, shows Thai message
- ❌ Error shown in red toast notification

## Debugging Tips

### If Still Getting 400 Error

1. **Check Browser Console**:
   ```
   Look for: 📝 Form data before validation
   ```
   - If `room_id: 0` → User hasn't selected a room
   - If `customer_id: 0` → User hasn't selected a customer
   - If `total_amount: 0` → Room has no rate configured

2. **Check Backend Logs**:
   ```bash
   docker-compose logs backend | grep "POST /api/v1/bookings"
   ```
   Look for:
   - `❌ Error creating booking:` → Backend error message
   - `room_id = %s` with `(0,)` → Room not selected
   - `customer_id = %s` with `(0,)` → Customer not selected

3. **Check Room Data**:
   - In browser console, run:
   ```javascript
   // Check if rooms are loaded
   console.log(dashboardStore.rooms)

   // Check if rooms have rates
   dashboardStore.rooms.forEach(r => {
     console.log(`Room ${r.id}: overnight_rate=${r.overnight_rate}`)
   })
   ```

### If Form Validation Message Still Shows

- Check that all fields are filled
- Especially check:
  - "ห้อง" (Room) - must have a value > 0
  - "ลูกค้า" (Customer) - must have a value > 0
  - "ยอดรวม" (Total) - must have a value > 0

## Files Modified

```
frontend/src/components/BookingFormModal.vue
- Enhanced form validation rules
- Added console logging for debugging
- Improved error message display
- Better error handling in catch block

backend/app/api/v1/endpoints/bookings.py
- Added debug print statements to log request data
- Better error messages
```

## Next Steps

1. Test the fix with the steps above
2. Watch browser console for debug logs
3. If still errors, collect console output and backend logs
4. Fix any remaining issues based on logs

---

**Updated**: 2025-10-21
**Status**: Ready for testing

