# Phase 5: Housekeeping Workflow Enhancement

**Date**: 2025-01-20
**Status**: Completed

## Overview

Enhanced the housekeeping workflow to streamline operations by:
1. Auto-starting housekeeping tasks immediately upon checkout (no manual start needed)
2. Adding damage/maintenance reporting capability directly from the cleaning completion form

## Changes Made

### 1. Backend Changes

#### `backend/app/services/check_out_service.py` (Lines 170-186)
**Modified**: Housekeeping task creation to start immediately in `IN_PROGRESS` status

```python
# Phase 5: Create housekeeping task
# Start task immediately (IN_PROGRESS) - housekeeping staff only needs to confirm completion
current_time = now_thailand()
housekeeping_task = HousekeepingTask(
    room_id=room.id,
    check_in_id=check_in.id,
    title=f"ทำความสะอาดห้อง {room.room_number}",
    description=f"ทำความสะอาดหลังลูกค้าเช็คเอาท์ ({check_in.customer.full_name if check_in.customer else 'N/A'})",
    priority=HousekeepingTaskPriorityEnum.HIGH if is_overtime else HousekeepingTaskPriorityEnum.MEDIUM,
    status=HousekeepingTaskStatusEnum.IN_PROGRESS,  # Auto-start immediately
    started_at=current_time,  # Set start time to now
    created_by=processed_by_user_id
)
```

**Impact**:
- Tasks are now created with `status=IN_PROGRESS` instead of `PENDING`
- `started_at` timestamp is set immediately
- Housekeeping staff only need to confirm completion, not manually start tasks

#### `backend/app/api/v1/endpoints/public.py` (Lines 336-380)
**Added**: New public endpoint for maintenance reporting

```python
@router.post("/maintenance/report")
async def report_public_maintenance(
    report_data: MaintenanceTaskCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create maintenance task report (PUBLIC - no authentication required)
    Used by housekeeping staff to report damage discovered while cleaning.
    """
```

**Features**:
- No authentication required (for housekeeping staff access via Telegram links)
- Creates maintenance task with provided room_id, category, title, description, priority
- Returns success confirmation with task_id

### 2. Frontend Changes

#### `frontend/src/views/PublicHousekeepingTaskView.vue`

**Changed (Lines 118-130)**: Removed "Start Task" button, added auto-start info box

**Before**:
```vue
<!-- Start Task Button -->
<button v-if="task.status === 'pending'" @click="handleStartTask">
  เริ่มทำงาน
</button>
```

**After**:
```vue
<!-- Auto-started Info (No manual start needed) -->
<div v-if="task.status === 'in_progress' && task.started_at" class="mb-4 p-4 bg-blue-50 border-2 border-blue-200 rounded-xl">
  <div class="flex items-start space-x-3">
    <svg class="w-6 h-6 text-blue-600">...</svg>
    <div class="flex-1">
      <p class="text-sm font-bold text-blue-900">งานเริ่มอัตโนมัติแล้ว</p>
      <p class="text-xs text-blue-700 mt-1">เริ่มเมื่อ: {{ formatThaiDateTime(task.started_at) }}</p>
      <p class="text-xs text-blue-600 mt-1">กรุณาทำความสะอาดห้องให้เสร็จสิ้น แล้วกดปุ่มยืนยันด้านล่าง</p>
    </div>
  </div>
</div>
```

**Added (Lines 189-199)**: "Report Damage" button in completion modal

```vue
<!-- Report Damage Button (Separate row for emphasis) -->
<div class="mb-3">
  <button @click="handleReportDamage" class="w-full px-6 py-3 bg-gradient-to-r from-orange-500 to-red-500 text-white rounded-xl">
    <svg>...</svg>
    <span>พบความชำรุด - แจ้งซ่อม</span>
  </button>
</div>
```

**Added (Lines 324-337)**: `handleReportDamage` function

```typescript
function handleReportDamage() {
  if (!task.value?.room_id) {
    showToast('error', 'ไม่พบข้อมูลห้อง')
    return
  }
  showCompleteModal.value = false
  window.location.href = `http://localhost:5173/public/maintenance/report?room_id=${task.value.room_id}&from_housekeeping=true&task_id=${taskId}`
}
```

#### `frontend/src/views/PublicMaintenanceReportView.vue`
**Created**: New public page for damage/maintenance reporting

**Features**:
- Beautiful gradient UI matching housekeeping task pages
- Form fields:
  - Category selection (plumbing, electrical, hvac, furniture, appliance, building, other)
  - Title (required, 3-200 chars)
  - Description (optional, up to 500 chars)
  - Priority selection (urgent, high, medium, low) - defaults to HIGH
- Displays room info (room number and type)
- Shows "Back" button when coming from housekeeping (returns to task)
- Auto-redirects back to housekeeping task after successful submission
- No authentication required

**Query Parameters**:
- `room_id`: Room ID to report maintenance for
- `from_housekeeping`: Boolean flag indicating origin
- `task_id`: Housekeeping task ID to return to after reporting

#### `frontend/src/router/index.ts` (Lines 84-89)
**Added**: Route for public maintenance report page

```typescript
{
  path: '/public/maintenance/report',
  name: 'PublicMaintenanceReport',
  component: () => import('@/views/PublicMaintenanceReportView.vue'),
  meta: { requiresAuth: false }
}
```

## User Workflow

### Old Workflow:
1. Guest checks out
2. Telegram notification sent to housekeeping
3. Housekeeping clicks link → Public task page
4. **Manual click "เริ่มทำงาน" button**
5. Clean room
6. Click "ทำความสะอาดเสร็จสิ้น"
7. **If damage found, must separately navigate to maintenance page (authenticated)**

### New Workflow:
1. Guest checks out
2. Telegram notification sent to housekeeping
3. Housekeeping clicks link → Public task page
4. **Task already started (shows start time info)**
5. Clean room
6. Click "ทำความสะอาดเสร็จสิ้น"
7. **If damage found:**
   - Click "พบความชำรุด - แจ้งซ่อม" button
   - Fill maintenance report form (no login needed)
   - Submit → Auto-redirect back to housekeeping task
   - Complete housekeeping task

## Benefits

1. **Faster Operations**: One less click for housekeeping staff (no manual start)
2. **Better UX**: Clear visual indication that task is auto-started
3. **Integrated Damage Reporting**:
   - No need to switch apps or login
   - Seamless flow from cleaning to damage reporting
   - Maintains context (room info carried over)
4. **Audit Trail**: Still tracks start time and completion time for analytics
5. **Mobile-Friendly**: All interactions optimized for mobile devices

## Technical Notes

### Auto-Start Implementation
- Tasks created in `IN_PROGRESS` status with `started_at` timestamp
- Frontend shows info box instead of start button for in_progress tasks
- Backend `start_task` endpoint still functional for edge cases

### Public Maintenance Reporting
- Uses same `MaintenanceTaskCreate` schema as authenticated endpoint
- Creator defaults to user_id=1 (admin) since no authentication
- Telegram notification sent when maintenance task created
- Room status remains "cleaning" until housekeeping confirms completion

### Database Impact
- No schema changes required
- Existing fields used: `status`, `started_at`
- Compatible with existing analytics/reporting queries

## Testing Checklist

- [x] Checkout creates task in IN_PROGRESS status
- [x] Public housekeeping page shows auto-start info instead of start button
- [x] Complete button still works
- [x] Report damage button appears in completion modal
- [x] Clicking damage button navigates to maintenance report page
- [x] Maintenance report form displays room info
- [x] Form validation works (required fields)
- [x] Successful submission creates maintenance task
- [x] Telegram notification sent for maintenance task
- [x] After submission, redirects back to housekeeping task
- [x] Back button works correctly
- [x] Can complete housekeeping task after reporting damage

## Files Modified

1. `backend/app/services/check_out_service.py` - Auto-start housekeeping tasks
2. `backend/app/api/v1/endpoints/public.py` - Add maintenance report endpoint
3. `frontend/src/views/PublicHousekeepingTaskView.vue` - UI changes
4. `frontend/src/views/PublicMaintenanceReportView.vue` - New file
5. `frontend/src/router/index.ts` - Add route

## Related Documentation

- Phase 5 Telegram Integration: `PHASE5_TELEGRAM_COMPLETE.md`
- Housekeeping Service: `backend/app/services/housekeeping_service.py`
- Maintenance Service: `backend/app/services/maintenance_service.py`

## Future Enhancements

1. Create dedicated "housekeeping_bot" user instead of using admin (user_id=1)
2. Add photo upload capability for damage documentation
3. Add predefined damage templates (e.g., "แอร์ไม่เย็น", "ก๊อกน้ำรั่ว")
4. Show history of previously reported issues for the room
5. Add estimated repair time field
6. Add auto-assignment based on maintenance category
