# Phase 7: Booking System - Implementation Plan

**Timeline**: 5-6 days
**Status**: Planning
**Date**: 2025-01-20

---

## 📋 Overview

Phase 7 implements a comprehensive booking system with calendar view, deposit management, automatic room status updates, and Telegram notifications for booking reminders.

### Current Status ✅
- ✅ `bookings` table already created (Phase 3 migration)
- ✅ `Booking` model exists in `backend/app/models/booking.py`
- ✅ Basic relationships defined (customer, room, creator, check_ins)
- ❌ No booking schemas created yet
- ❌ No booking service created yet
- ❌ No booking API endpoints created yet
- ❌ No booking frontend created yet

---

## 🎯 Objectives

1. **Calendar View** - FullCalendar integration showing bookings and Thai public holidays
2. **CRUD Operations** - Create, Read, Update, Delete bookings
3. **Deposit Management** - Record and track deposits (non-refundable)
4. **Auto Status Updates** - Room status → "reserved" on check-in date
5. **Telegram Reminders** - Notify if guest hasn't checked in 1 hour after check-in time
6. **Check-in Integration** - Pre-fill check-in form from booking data

---

## 📊 Database Schema (Already Exists)

### bookings table
```sql
- id (PK)
- customer_id (FK -> customers) [indexed]
- room_id (FK -> rooms) [indexed]
- check_in_date (Date) [indexed]
- check_out_date (Date) [indexed]
- number_of_nights (Integer)
- total_amount (Decimal 10,2)
- deposit_amount (Decimal 10,2) default 0
- status (Enum) [indexed]
  - pending
  - confirmed
  - checked_in
  - completed
  - cancelled
- notes (Text, nullable)
- created_by (FK -> users)
- created_at (DateTime)
- updated_at (DateTime)
- cancelled_at (DateTime, nullable)
```

### Additional Index Needed
```sql
CREATE INDEX idx_bookings_dates ON bookings(check_in_date, check_out_date);
```

---

## 🏗️ Implementation Breakdown

### Day 1-2: Backend Core

#### 1.1 Schemas (Pydantic)
**File**: `backend/app/schemas/booking.py`

```python
# Base schemas
- BookingBase
- BookingCreate
- BookingUpdate
- BookingInDB
- BookingResponse
- BookingListResponse
- BookingCalendarEvent
- BookingStats

# Special schemas
- PublicHoliday
- BookingReminderTask
```

#### 1.2 Service Layer
**File**: `backend/app/services/booking_service.py`

**Methods**:
```python
class BookingService:
    async def create_booking(data: BookingCreate, user_id: int) -> Booking
    async def get_booking_by_id(booking_id: int) -> Booking
    async def get_bookings(filters, skip, limit) -> List[Booking]
    async def update_booking(booking_id, data: BookingUpdate, user_id: int) -> Booking
    async def cancel_booking(booking_id: int, user_id: int) -> Booking
    async def get_calendar_events(start_date, end_date) -> List[BookingCalendarEvent]
    async def check_room_availability(room_id, check_in_date, check_out_date, exclude_booking_id=None) -> bool
    async def get_booking_by_room_and_date(room_id, date) -> Booking | None
    async def get_public_holidays(year: int) -> List[PublicHoliday]
```

**Business Logic**:
- ✅ Validate room availability (no overlapping bookings)
- ✅ Calculate number_of_nights automatically
- ✅ Calculate total_amount based on room_rate × nights
- ✅ Prevent booking temporary stay rooms
- ✅ Update room status when booking confirmed
- ✅ Revert room status when booking cancelled

#### 1.3 API Endpoints
**File**: `backend/app/api/v1/endpoints/bookings.py`

```python
GET    /api/v1/bookings              # List bookings with filters
POST   /api/v1/bookings              # Create new booking
GET    /api/v1/bookings/{id}         # Get booking details
PUT    /api/v1/bookings/{id}         # Update booking
DELETE /api/v1/bookings/{id}         # Cancel booking
GET    /api/v1/bookings/calendar     # Get calendar events
GET    /api/v1/bookings/public-holidays/{year}  # Get Thai public holidays
POST   /api/v1/bookings/{id}/confirm # Confirm pending booking
```

**Query Parameters** (GET /bookings):
- `status`: Filter by status
- `room_id`: Filter by room
- `customer_id`: Filter by customer
- `start_date`: Filter by date range start
- `end_date`: Filter by date range end
- `skip`: Pagination offset
- `limit`: Pagination limit

#### 1.4 Public Holidays API Integration
**External API**: https://date.nager.at/api/v3/PublicHolidays/{year}/TH

**Implementation**:
```python
import httpx

async def fetch_thai_holidays(year: int) -> List[PublicHoliday]:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://date.nager.at/api/v3/PublicHolidays/{year}/TH")
        holidays = response.json()
        return [
            PublicHoliday(
                date=h['date'],
                name=h['localName'],
                name_en=h['name']
            )
            for h in holidays
        ]
```

---

### Day 2-3: Celery Background Tasks

#### 2.1 Auto Update Room Status
**File**: `backend/app/tasks/booking_tasks.py`

**Task**: `check_bookings_for_today`
- **Schedule**: Every day at 00:01 (Thai time)
- **Action**:
  - Find all confirmed bookings where `check_in_date = TODAY`
  - Update room status from "available" → "reserved"
  - Broadcast WebSocket event

**Task**: `check_booking_check_in_times`
- **Schedule**: Every 30 minutes
- **Action**:
  - Find bookings with status = "confirmed" where:
    - `check_in_date = TODAY`
    - Expected check-in time passed by > 1 hour
    - No associated check_in record
  - Send Telegram reminder to admin/reception
  - Mark in system for follow-up

**Telegram Message Format**:
```
⚠️ การจองเลยเวลา Check-in

📅 Booking ID: #123
🏠 ห้อง: 101 (VIP)
👤 ลูกค้า: นายสมชาย ใจดี (081-234-5678)
📆 วันที่จอง: 20 ม.ค. 2025 (14:00)
⏰ เลยเวลามาแล้ว: 1 ชั่วโมง 30 นาที

💰 เงินมัดจำ: 500 บาท

🔗 ดูรายละเอียด: [URL]
```

#### 2.2 Celery Beat Configuration
**File**: `backend/app/tasks/celery_app.py`

```python
app.conf.beat_schedule = {
    'check-bookings-for-today': {
        'task': 'app.tasks.booking_tasks.check_bookings_for_today',
        'schedule': crontab(hour=0, minute=1),  # 00:01 daily
    },
    'check-booking-check-in-times': {
        'task': 'app.tasks.booking_tasks.check_booking_check_in_times',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
    },
}
```

---

### Day 3-4: Frontend - Calendar & Forms

#### 3.1 Install Dependencies
```bash
npm install @fullcalendar/core @fullcalendar/vue3 @fullcalendar/daygrid @fullcalendar/interaction
```

#### 3.2 Booking Store (Pinia)
**File**: `frontend/src/stores/booking.ts`

```typescript
export const useBookingStore = defineStore('booking', () => {
  const bookings = ref<Booking[]>([])
  const calendarEvents = ref<CalendarEvent[]>([])
  const publicHolidays = ref<PublicHoliday[]>([])
  const currentBooking = ref<Booking | null>(null)
  const loading = ref(false)

  async function fetchBookings(filters?)
  async function fetchCalendarEvents(start: Date, end: Date)
  async function fetchPublicHolidays(year: number)
  async function createBooking(data: BookingCreate)
  async function updateBooking(id: number, data: BookingUpdate)
  async function cancelBooking(id: number)
  async function confirmBooking(id: number)
  async function checkRoomAvailability(roomId: number, checkIn: Date, checkOut: Date)

  return {
    bookings,
    calendarEvents,
    publicHolidays,
    currentBooking,
    loading,
    fetchBookings,
    fetchCalendarEvents,
    fetchPublicHolidays,
    createBooking,
    updateBooking,
    cancelBooking,
    confirmBooking,
    checkRoomAvailability
  }
})
```

#### 3.3 Calendar View
**File**: `frontend/src/views/BookingCalendarView.vue`

**Features**:
- FullCalendar integration
- Month/Week/Day views
- Color-coded events:
  - 🟦 Blue: Pending bookings
  - 🟩 Green: Confirmed bookings
  - 🟨 Yellow: Checked-in
  - ⬜ Gray: Cancelled
  - 🟥 Red: Thai public holidays
- Click event → Show booking details modal
- Click empty date → Create new booking
- Drag & drop to reschedule (with validation)
- Responsive (mobile/tablet/desktop)

**Components**:
```vue
<template>
  <div class="booking-calendar-page">
    <div class="header">
      <h1>ปฏิทินการจอง</h1>
      <n-button @click="showCreateModal = true">+ สร้างการจอง</n-button>
    </div>

    <FullCalendar
      :options="calendarOptions"
      ref="calendar"
    />

    <!-- Create/Edit Booking Modal -->
    <BookingFormModal
      v-model:show="showFormModal"
      :booking="selectedBooking"
      :preselected-date="preselectedDate"
      @saved="handleBookingSaved"
    />

    <!-- Booking Detail Modal -->
    <BookingDetailModal
      v-model:show="showDetailModal"
      :booking="selectedBooking"
      @edit="handleEdit"
      @cancel="handleCancel"
    />
  </div>
</template>
```

#### 3.4 Booking Form Modal
**File**: `frontend/src/components/BookingFormModal.vue`

**Form Fields**:
1. **Customer Selection** (autocomplete with create new)
   - Name, Phone, ID Card
2. **Room Selection** (dropdown with availability indicator)
   - Show only available rooms for selected dates
3. **Date Range** (date picker)
   - Check-in date
   - Check-out date
   - Auto-calculate nights
4. **Rate Display**
   - Show room rate per night
   - Show total amount (auto-calculated)
5. **Deposit** (optional)
   - Amount
   - Warning: Non-refundable
6. **Notes** (optional)

**Validation**:
- ✅ All required fields filled
- ✅ Check-out date > Check-in date
- ✅ Room available for selected dates
- ✅ Deposit ≤ Total amount
- ✅ Customer phone number valid format

#### 3.5 Booking List View
**File**: `frontend/src/views/BookingListView.vue`

**Features**:
- Table view with filters
- Status badges (color-coded)
- Search by customer name/phone
- Filter by status, room, date range
- Quick actions: View, Edit, Cancel, Check-in
- Pagination
- Export to Excel

**Columns**:
- Booking ID
- Customer Name
- Phone
- Room
- Check-in Date
- Check-out Date
- Nights
- Total Amount
- Deposit
- Status
- Actions

#### 3.6 Booking Detail Modal
**File**: `frontend/src/components/BookingDetailModal.vue`

**Sections**:
1. Customer Information
2. Room & Dates
3. Financial Details (Total, Deposit, Balance)
4. Status & Timeline
5. Notes
6. Actions (Edit, Cancel, Check-in, Print)

---

### Day 4-5: Integration & Features

#### 4.1 Check-in Integration
**File**: `frontend/src/views/DashboardView.vue`

When clicking "Check-in" from dashboard:
1. Check if room has booking for today
2. If yes, pre-fill check-in form:
   - Customer info from booking
   - Room from booking
   - Stay type: overnight
   - Expected check-out date from booking
   - Total amount = booking.total_amount - booking.deposit_amount
3. After check-in success:
   - Update booking status → "checked_in"
   - Link check_in.booking_id → booking.id

**Implementation**:
```typescript
async function handleCheckIn(room: Room) {
  // Check for active booking
  const booking = await bookingApi.getBookingByRoomAndDate(room.id, new Date())

  if (booking) {
    // Pre-fill from booking
    checkInForm.value = {
      customer_id: booking.customer_id,
      room_id: booking.room_id,
      stay_type: 'overnight',
      booking_id: booking.id,
      number_of_nights: booking.number_of_nights,
      base_amount: booking.total_amount - booking.deposit_amount,
      // ... other fields
    }
    showCheckInModal.value = true
  } else {
    // Normal check-in flow
    showCheckInModal.value = true
  }
}
```

#### 4.2 Room Availability Checker
**Component**: `frontend/src/components/RoomAvailabilityChecker.vue`

**Use Case**: When selecting room in booking form
- Real-time availability check
- Show conflicting bookings if any
- Visual indicator (✅ Available / ❌ Not Available)

#### 4.3 Booking Reminder UI
**File**: `frontend/src/views/DashboardView.vue`

**Feature**: Show alert for overdue bookings
```vue
<div v-if="overdueBookings.length > 0" class="alert alert-warning">
  <h4>⚠️ การจองที่เลยเวลา Check-in ({{ overdueBookings.length }})</h4>
  <div v-for="booking in overdueBookings" :key="booking.id" class="overdue-item">
    <span>ห้อง {{ booking.room_number }} - {{ booking.customer_name }}</span>
    <span>เลยมา {{ formatDuration(booking.overdue_minutes) }}</span>
    <n-button size="small" @click="handleCheckInFromBooking(booking)">Check-in</n-button>
    <n-button size="small" @click="handleCancelBooking(booking.id)">ยกเลิก</n-button>
  </div>
</div>
```

---

### Day 5-6: Testing & Polish

#### 5.1 Backend Tests
**File**: `backend/tests/test_booking_service.py`

**Test Cases**:
```python
def test_create_booking_success()
def test_create_booking_room_not_available()
def test_create_booking_invalid_dates()
def test_update_booking_success()
def test_cancel_booking_success()
def test_check_room_availability()
def test_get_calendar_events()
def test_fetch_public_holidays()
def test_auto_update_room_status_on_booking_date()
def test_send_reminder_for_overdue_booking()
```

#### 5.2 Frontend Tests
**File**: `frontend/src/views/__tests__/BookingCalendarView.spec.ts`

**Test Cases**:
```typescript
test('Calendar displays bookings correctly')
test('Create booking from empty date click')
test('Edit booking from event click')
test('Drag and drop reschedules booking')
test('Public holidays displayed in red')
test('Room availability check works')
test('Form validation works')
```

#### 5.3 End-to-End Testing

**Scenario 1**: Create Booking
1. Go to calendar page
2. Click empty date (tomorrow)
3. Select customer (create new if needed)
4. Select available room
5. Select check-out date (+2 nights)
6. Enter deposit (500 baht)
7. Save → Booking appears in calendar

**Scenario 2**: Auto Update Room Status
1. Create booking for today
2. Wait for midnight (or trigger Celery task manually)
3. Room status should change to "reserved"
4. Dashboard shows room as reserved

**Scenario 3**: Check-in from Booking
1. Create booking for today
2. Go to dashboard
3. Click check-in on reserved room
4. Form pre-filled with booking data
5. Complete check-in
6. Booking status → "checked_in"
7. Room status → "occupied"

**Scenario 4**: Overdue Booking Reminder
1. Create booking for today (check-in time 14:00)
2. Wait until 15:00 (or trigger Celery task)
3. Telegram notification sent
4. Dashboard shows overdue alert

**Scenario 5**: Cancel Booking
1. Create future booking
2. Room status → "reserved"
3. Cancel booking
4. Room status → "available"
5. Booking status → "cancelled"

---

## 🎨 UI/UX Design

### Color Scheme (Booking Status)
- 🟦 **Pending**: `#3B82F6` (Blue) - Waiting for confirmation
- 🟩 **Confirmed**: `#10B981` (Green) - Ready for check-in
- 🟨 **Checked-in**: `#F59E0B` (Amber) - Guest checked in
- ⬜ **Completed**: `#6B7280` (Gray) - Past booking
- 🟥 **Cancelled**: `#EF4444` (Red) - Cancelled booking
- 🔴 **Public Holiday**: `#DC2626` (Dark Red)

### Calendar View Icons
- 📅 Booking event
- 🎉 Public holiday
- ⚠️ Overdue booking (pulsing animation)

### Mobile Optimization
- Calendar switches to list view on mobile
- Swipe gestures for month navigation
- Bottom sheet for booking details

---

## 🔌 API Integration Points

### External APIs
1. **Thai Public Holidays**: https://date.nager.at/api/v3/PublicHolidays/{year}/TH
   - Cache holidays per year in Redis (TTL: 365 days)
   - Fallback to local data if API unavailable

### Internal APIs
1. **Room Service**: Check room availability
2. **Customer Service**: Search/Create customers
3. **Check-in Service**: Create check-in from booking
4. **Telegram Service**: Send notifications
5. **WebSocket**: Broadcast room status changes

---

## 📦 Dependencies

### Backend
```txt
# Already installed
fastapi
sqlalchemy
pydantic
celery
redis
python-telegram-bot

# New
httpx  # For public holidays API
```

### Frontend
```json
{
  "@fullcalendar/core": "^6.1.10",
  "@fullcalendar/vue3": "^6.1.10",
  "@fullcalendar/daygrid": "^6.1.10",
  "@fullcalendar/interaction": "^6.1.10"
}
```

---

## 🚨 Edge Cases & Validations

### Business Rules
1. ✅ Only overnight stays can be booked (no temporary)
2. ✅ Cannot book same room for overlapping dates
3. ✅ Check-out date must be after check-in date
4. ✅ Deposit cannot exceed total amount
5. ✅ Cannot edit booking after check-in
6. ✅ Cannot cancel booking after check-in (must check-out first)
7. ✅ Deposit is non-refundable on cancellation
8. ✅ Room must be available (not out_of_service)

### Error Handling
- Room not available → Show conflicting booking details
- API failure → Use cached data / show error message
- Telegram send failure → Log error, retry later
- Invalid dates → Clear validation messages

---

## 📊 Database Queries (Performance)

### Critical Queries
```sql
-- Check room availability
SELECT COUNT(*) FROM bookings
WHERE room_id = ?
  AND status NOT IN ('cancelled', 'completed')
  AND (
    (check_in_date <= ? AND check_out_date > ?) OR
    (check_in_date < ? AND check_out_date >= ?) OR
    (check_in_date >= ? AND check_out_date <= ?)
  )

-- Get today's bookings for auto-update
SELECT * FROM bookings
WHERE check_in_date = CURDATE()
  AND status = 'confirmed'

-- Get overdue bookings (for reminder)
SELECT * FROM bookings
WHERE check_in_date = CURDATE()
  AND status = 'confirmed'
  AND created_at < NOW() - INTERVAL 1 HOUR
  AND id NOT IN (SELECT booking_id FROM check_ins WHERE booking_id IS NOT NULL)
```

**Indexes** (already exist):
- `idx_bookings_dates` on (check_in_date, check_out_date)
- `idx_bookings_room_id` on (room_id)
- `idx_bookings_status` on (status)

---

## 🎯 Success Criteria

### Functional
- ✅ Create booking with customer and room selection
- ✅ Calendar displays all bookings and holidays
- ✅ Edit/Cancel booking works correctly
- ✅ Room status auto-updates on booking date
- ✅ Telegram reminder sent for overdue bookings
- ✅ Check-in pre-fills from booking data
- ✅ Deposit correctly deducted from total at check-in

### Non-Functional
- ✅ Calendar loads within 2 seconds
- ✅ Room availability check < 500ms
- ✅ Mobile-responsive (320px+)
- ✅ No data loss on cancellation
- ✅ Proper error messages in Thai

---

## 📝 File Structure

```
backend/
  app/
    api/v1/endpoints/
      bookings.py                 # NEW
    models/
      booking.py                  # EXISTS (enhance)
    schemas/
      booking.py                  # NEW
    services/
      booking_service.py          # NEW
    tasks/
      booking_tasks.py            # NEW
    tests/
      test_booking_service.py     # NEW

frontend/
  src/
    api/
      bookings.ts                 # NEW
    components/
      BookingFormModal.vue        # NEW
      BookingDetailModal.vue      # NEW
      RoomAvailabilityChecker.vue # NEW
    stores/
      booking.ts                  # NEW
    views/
      BookingCalendarView.vue     # NEW
      BookingListView.vue         # NEW
    types/
      booking.ts                  # NEW
```

---

## ⚡ Quick Start Checklist

### Phase 7 - Day 1
- [ ] Create `schemas/booking.py` with all Pydantic models
- [ ] Create `services/booking_service.py` with business logic
- [ ] Create `api/v1/endpoints/bookings.py` with all endpoints
- [ ] Test endpoints with Swagger UI

### Phase 7 - Day 2
- [ ] Create Celery tasks in `tasks/booking_tasks.py`
- [ ] Configure Celery beat schedule
- [ ] Test auto room status update
- [ ] Test Telegram reminder

### Phase 7 - Day 3
- [ ] Install FullCalendar dependencies
- [ ] Create `stores/booking.ts` Pinia store
- [ ] Create `api/bookings.ts` API client
- [ ] Create `types/booking.ts` TypeScript types

### Phase 7 - Day 4
- [ ] Create `BookingCalendarView.vue` with FullCalendar
- [ ] Create `BookingFormModal.vue` with validation
- [ ] Create `BookingDetailModal.vue`
- [ ] Test calendar interactions

### Phase 7 - Day 5
- [ ] Create `BookingListView.vue` with filters
- [ ] Integrate check-in pre-fill from booking
- [ ] Add overdue booking alerts to dashboard
- [ ] Create room availability checker

### Phase 7 - Day 6
- [ ] Write backend tests
- [ ] Write frontend tests
- [ ] End-to-end testing
- [ ] Bug fixes and polish
- [ ] Update documentation

---

## 🎓 Learning Resources

- FullCalendar Vue 3 Docs: https://fullcalendar.io/docs/vue
- Thai Public Holidays API: https://date.nager.at/
- Celery Beat Scheduling: https://docs.celeryproject.org/en/stable/userguide/periodic-tasks.html

---

**Ready to start implementation? Let's begin with Day 1! 🚀**
