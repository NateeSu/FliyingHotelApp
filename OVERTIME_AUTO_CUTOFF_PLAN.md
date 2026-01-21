# แผนการพัฒนา: Auto-Cutoff Temporary Stay เมื่อหมดเวลา 3 ชั่วโมง

## 📋 สรุป Requirement

สำหรับการพักแบบ **ชั่วคราว (TEMPORARY)** เมื่อครบ 3 ชั่วโมง:
1. ✅ แสดงข้อความเตือนว่า "หมดเวลาเข้าพัก"
2. ✅ ตัดไฟ Smart Breaker อัตโนมัติ
3. ✅ เปลี่ยนสถานะห้องเป็น "OCCUPIED_OVERTIME" (หมดเวลาเข้าพัก)

---

## 🔍 สถานะปัจจุบันของระบบ

### ✅ สิ่งที่มีอยู่แล้ว:

1. **Check-ins Table Structure:**
   - `stay_type` (OVERNIGHT/TEMPORARY)
   - `check_in_time`
   - `expected_check_out_time` (สำหรับ TEMPORARY = check_in_time + 3 ชั่วโมง)
   - `is_overtime` (0/1)
   - `overtime_minutes`
   - `overtime_charge`

2. **Overtime Detection (แบบ Reactive):**
   - Dashboard Service: `get_overtime_alerts()` - คำนวณเมื่อโหลด dashboard
   - WebSocket: `broadcast_overtime_alert()` - broadcast เมื่อมีการเรียก
   - Frontend: แสดง overtime badge บน RoomCard

3. **Room Status Enum:**
   ```python
   AVAILABLE = "AVAILABLE"
   OCCUPIED = "OCCUPIED"
   CLEANING = "CLEANING"
   RESERVED = "RESERVED"
   OUT_OF_SERVICE = "OUT_OF_SERVICE"
   ```

4. **Smart Breaker Automation:**
   - OCCUPIED/CLEANING → เปิดไฟ
   - AVAILABLE/RESERVED/OUT_OF_SERVICE → ปิดไฟ
   - Hook: `auto_control_on_room_status_change()` ทำงานเมื่อเปลี่ยนสถานะห้อง

### ❌ สิ่งที่ยังไม่มี:

1. **ไม่มี Celery Task สำหรับตรวจสอบ Overtime แบบอัตโนมัติ**
   - ปัจจุบันตรวจสอบแค่เมื่อโหลด dashboard เท่านั้น
   - ไม่มีการ monitor แบบ background job

2. **ไม่มี Room Status สำหรับ Overtime**
   - ห้องที่เกินเวลายังคงเป็น "OCCUPIED"
   - ไม่มี "OCCUPIED_OVERTIME" หรือสถานะอื่นที่บ่งบอกว่าหมดเวลา

3. **ไม่มีการ Auto-Cutoff Breaker เมื่อหมดเวลา**
   - Breaker ยังคงเปิดอยู่แม้เกินเวลาแล้ว
   - ต้องรอจนกว่าจะ check-out จึงจะเปลี่ยนเป็น CLEANING (และเปิดไฟต่อ)

4. **ไม่มี Telegram Notification สำหรับ Overtime**
   - PRD ระบุว่าควรมี แต่ยังไม่ได้ implement

---

## 🎯 แผนการพัฒนา

### Phase 1: เพิ่ม Room Status สำหรับ Overtime

**📁 ไฟล์ที่ต้องแก้ไข:**

1. **backend/app/models/room.py**
   - เพิ่ม `OCCUPIED_OVERTIME = "OCCUPIED_OVERTIME"` ใน RoomStatus enum
   - Comment: "มีผู้พัก (เกินเวลาแล้ว - ตัดไฟ)"

2. **Database Migration**
   - สร้าง migration สำหรับแก้ไข enum ใน rooms table
   - SQL: `ALTER TABLE rooms MODIFY COLUMN status ENUM('AVAILABLE','OCCUPIED','CLEANING','RESERVED','OUT_OF_SERVICE','OCCUPIED_OVERTIME')`

3. **backend/app/services/breaker_service.py**
   - แก้ไข `auto_control_on_room_status_change()`:
     ```python
     # OCCUPIED_OVERTIME should turn OFF breaker (cut power)
     elif new_status in [RoomStatus.OCCUPIED_OVERTIME]:
         if breaker.current_state != BreakerState.OFF:
             await self.turn_off(...)
     ```

4. **frontend/src/types/room.ts**
   - เพิ่ม `'OCCUPIED_OVERTIME'` ใน RoomStatus type

5. **frontend/src/components/RoomCard.vue**
   - เพิ่ม color scheme สำหรับ OCCUPIED_OVERTIME (เช่น สีแดงเข้ม)
   - แสดงข้อความ "หมดเวลาเข้าพัก"
   - แสดง icon เตือน ⏰ หรือ ⚠️

**⚠️ คำเตือน:**
- ต้องตรวจสอบทุกจุดที่ใช้ RoomStatus enum
- ต้อง update frontend type definitions
- ต้อง test breaker automation ให้แน่ใจว่าปิดไฟจริง

---

### Phase 2: สร้าง Celery Task สำหรับตรวจสอบ Overtime อัตโนมัติ

**📁 ไฟล์ที่ต้องแก้ไข:**

1. **backend/app/tasks/overtime_tasks.py** (ไฟล์ใหม่)
   - สร้าง task: `check_temporary_stay_overtime()`
   - Logic:
     ```python
     @shared_task(name="overtime.check_temporary_stay_overtime")
     def check_temporary_stay_overtime():
         """
         Check all TEMPORARY stays that are CHECKED_IN
         If current_time >= expected_check_out_time:
         1. Update is_overtime = 1
         2. Calculate overtime_minutes
         3. Change room status to OCCUPIED_OVERTIME
         4. Turn OFF smart breaker
         5. Broadcast WebSocket overtime alert
         6. Send Telegram notification
         """
     ```

2. **backend/app/tasks/celery_app.py**
   - เพิ่ม periodic task ใน beat_schedule:
     ```python
     'check-temporary-stay-overtime': {
         'task': 'overtime.check_temporary_stay_overtime',
         'schedule': 60.0,  # Every 1 minute (or 30 seconds for faster response)
     }
     ```

3. **backend/app/services/overtime_service.py** (ไฟล์ใหม่)
   - สร้าง `OvertimeService` class
   - Methods:
     - `async def process_overtime_checkin(check_in_id: int)`
     - `async def send_overtime_notification(check_in: CheckIn)`
     - `async def auto_cutoff_room(room_id: int, check_in_id: int)`

**Logic Flow:**
```
1. Query: SELECT * FROM check_ins
   WHERE stay_type = 'TEMPORARY'
   AND status = 'CHECKED_IN'
   AND expected_check_out_time <= NOW()
   AND is_overtime = 0  -- ยังไม่ได้ประมวลผล

2. For each check_in:
   a. Update is_overtime = 1
   b. Calculate overtime_minutes
   c. Get room and update status to OCCUPIED_OVERTIME
   d. Trigger breaker automation (auto turn OFF)
   e. Broadcast WebSocket overtime alert
   f. Create notification record
   g. Send Telegram to reception/admin
   h. Commit transaction
```

**⚠️ คำเตือน:**
- ต้องใช้ transaction เพื่อความ consistent
- ต้อง handle error กรณี breaker ไม่ตอบสนอง
- ต้อง log ทุกขั้นตอนเพื่อ debug

---

### Phase 3: เพิ่ม Telegram Notification

**📁 ไฟล์ที่ต้องแก้ไข:**

1. **backend/app/services/telegram_service.py**
   - เพิ่ม method: `async def send_overtime_alert(check_in: CheckIn)`
   - Message template:
     ```
     ⚠️ แจ้งเตือน: หมดเวลาเข้าพัก

     ห้อง: {room_number}
     ลูกค้า: {customer_name}
     เบอร์โทร: {phone}

     เข้าพัก: {check_in_time}
     ครบกำหนด: {expected_check_out_time}
     เกินเวลามาแล้ว: {overtime_minutes} นาที

     ระบบได้ตัดไฟอัตโนมัติแล้ว
     กรุณาติดต่อลูกค้าเพื่อ check-out
     ```

2. **backend/app/models/notification.py**
   - เพิ่ม type ใน NotificationType enum (ถ้ายังไม่มี):
     ```python
     OVERTIME_ALERT = "OVERTIME_ALERT"
     ```

**Recipients:**
- Admin users
- Reception users
- (Optional) Specific users subscribed to overtime alerts

---

### Phase 4: Update Frontend UI

**📁 ไฟล์ที่ต้องแก้ไข:**

1. **frontend/src/components/RoomCard.vue**
   - เพิ่ม CSS class สำหรับ OCCUPIED_OVERTIME:
     ```css
     .room-card.occupied-overtime {
       background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%);
       border: 2px solid #dc2626;
       box-shadow: 0 0 20px rgba(220, 38, 38, 0.5);
       animation: pulse-red 2s infinite;
     }

     @keyframes pulse-red {
       0%, 100% { box-shadow: 0 0 20px rgba(220, 38, 38, 0.5); }
       50% { box-shadow: 0 0 30px rgba(220, 38, 38, 0.8); }
     }
     ```

   - แสดงข้อความ:
     ```vue
     <div v-if="room.status === 'OCCUPIED_OVERTIME'" class="overtime-banner">
       <span class="icon">⏰</span>
       <span class="text">หมดเวลาเข้าพัก - ตัดไฟแล้ว</span>
       <span class="overtime-duration">เกิน {{ room.overtime_minutes }} นาที</span>
     </div>
     ```

2. **frontend/src/stores/dashboard.ts**
   - Handle WebSocket event `overtime_auto_cutoff`:
     ```typescript
     socket.on('overtime_auto_cutoff', (data) => {
       // Refresh dashboard
       fetchDashboard()
       // Show notification
       notification.warning({
         title: 'หมดเวลาเข้าพัก',
         content: `ห้อง ${data.room_number} เกินเวลา - ระบบตัดไฟอัตโนมัติ`,
         duration: 5000
       })
     })
     ```

3. **frontend/src/views/DashboardView.vue**
   - เพิ่ม filter สำหรับแสดงห้อง OCCUPIED_OVERTIME แยกต่างหาก (optional)
   - เพิ่ม stats card แสดงจำนวนห้องที่เกินเวลา

---

### Phase 5: Update Check-Out Flow

**📁 ไฟล์ที่ต้องแก้ไข:**

1. **backend/app/services/check_out_service.py**
   - แก้ไข `process_checkout()` ให้รองรับ OCCUPIED_OVERTIME:
     ```python
     # Accept checkout from OCCUPIED_OVERTIME status
     if room.status not in [RoomStatus.OCCUPIED, RoomStatus.OCCUPIED_OVERTIME]:
         raise ValueError("ห้องไม่ได้อยู่ในสถานะมีผู้พัก")
     ```

2. **backend/app/services/check_out_service.py**
   - เมื่อ check-out จาก OCCUPIED_OVERTIME:
     - คำนวณ overtime_charge ตามปกติ
     - เปลี่ยนสถานะเป็น CLEANING
     - Breaker จะถูกเปิดอัตโนมัติ (เพราะ CLEANING → ON)

---

## 🧪 Test Cases

### Test Case 1: Temporary Stay - Normal (ภายใน 3 ชั่วโมง)
```
1. Check-in แบบ TEMPORARY เวลา 14:00
2. Expected check-out = 17:00
3. Check-out เวลา 16:45 (ยังไม่เกินเวลา)
4. ✅ ไม่มี overtime
5. ✅ Breaker เปิดตลอด (OCCUPIED → CLEANING)
6. ✅ ไม่มี notification
```

### Test Case 2: Temporary Stay - Overtime (เกิน 3 ชั่วโมง)
```
1. Check-in แบบ TEMPORARY เวลา 14:00
2. Expected check-out = 17:00
3. รอจนถึง 17:01 (Celery task ทำงาน)
4. ✅ Room status → OCCUPIED_OVERTIME
5. ✅ Breaker → OFF (ตัดไฟอัตโนมัติ)
6. ✅ is_overtime = 1, overtime_minutes = 1
7. ✅ WebSocket broadcast overtime_auto_cutoff
8. ✅ Telegram notification sent
9. ✅ Frontend แสดง "หมดเวลาเข้าพัก - ตัดไฟแล้ว"
10. Check-out เวลา 18:30 (เกิน 1.5 ชั่วโมง)
11. ✅ overtime_charge = base_amount * 2 (round up to 2 hours)
12. ✅ Room status → CLEANING
13. ✅ Breaker → ON (เพื่อทำความสะอาด)
```

### Test Case 3: Multiple Overtime Rooms
```
1. มีห้อง TEMPORARY 3 ห้องเกินเวลาพร้อมกัน
2. Celery task ประมวลผลทีละห้อง
3. ✅ แต่ละห้องได้รับ notification แยกกัน
4. ✅ Breaker ทุกห้องถูกปิด
5. ✅ Dashboard แสดง overtime alerts ทั้งหมด
```

### Test Case 4: Breaker Failure Handling
```
1. Temporary stay เกินเวลา
2. Breaker ไม่ตอบสนอง (Home Assistant offline)
3. ✅ Room status ยังคงเปลี่ยนเป็น OCCUPIED_OVERTIME
4. ✅ is_overtime ยังคง = 1
5. ✅ Notification ยังคงส่ง
6. ✅ Log error แต่ไม่ block process
7. ✅ Retry turn_off breaker ใน next cycle
```

---

## ⚙️ Configuration

### System Settings (Optional Enhancement)

เพิ่มการ config ระยะเวลาแบบ TEMPORARY (ตอนนี้ hard-code 3 ชั่วโมง):

**backend/app/models/system_settings.py:**
```python
# Key: temporary_stay_duration_hours
# Value: 3
# Data Type: number
# Description: จำนวนชั่วโมงสำหรับการพักแบบชั่วคราว
```

**backend/app/services/check_in_service.py:**
```python
def _calculate_expected_checkout(self, ...):
    if stay_type == StayTypeEnum.TEMPORARY:
        # Read from settings instead of hard-code
        duration_hours = await self._get_temporary_duration_hours()
        return check_in_time + timedelta(hours=duration_hours)
```

---

## 📊 Database Changes Summary

### 1. Migration: Add OCCUPIED_OVERTIME status
```sql
ALTER TABLE rooms
MODIFY COLUMN status ENUM(
    'AVAILABLE',
    'OCCUPIED',
    'CLEANING',
    'RESERVED',
    'OUT_OF_SERVICE',
    'OCCUPIED_OVERTIME'
) NOT NULL;
```

### 2. No Changes to check_ins table
- ใช้ field ที่มีอยู่แล้ว: `is_overtime`, `overtime_minutes`
- ไม่ต้องเพิ่ม column ใหม่

### 3. notifications table
- เพิ่ม type ใหม่: `OVERTIME_ALERT` (ถ้ายังไม่มี)

---

## 🔄 Implementation Order

### Priority 1 (Core Functionality):
1. ✅ Phase 1: เพิ่ม OCCUPIED_OVERTIME status + breaker automation
2. ✅ Phase 2: สร้าง Celery task สำหรับ auto-detect overtime
3. ✅ Phase 4: Update Frontend UI

### Priority 2 (Notifications):
4. ✅ Phase 3: Telegram notifications

### Priority 3 (Enhancement):
5. ✅ Phase 5: Update check-out flow
6. ⚪ Configuration: ทำให้ระยะเวลา 3 ชั่วโมง configurable ได้

---

## 🚨 Risks & Considerations

### Risk 1: Breaker ไม่ตอบสนอง
**Impact:** ไม่สามารถตัดไฟได้
**Mitigation:**
- Log error และ retry
- ส่ง notification ให้พนักงานรู้ว่าต้อง manual cutoff
- ไม่ block การเปลี่ยนสถานะห้อง

### Risk 2: Celery task ล่าช้า
**Impact:** ตัดไฟช้ากว่ากำหนด
**Mitigation:**
- Run task ทุก 1 นาที (หรือ 30 วินาที)
- Monitor Celery worker performance
- Alert ถ้า task queue สูงเกินไป

### Risk 3: Race Condition
**Impact:** Check-out ขณะที่ Celery task กำลังประมวลผล overtime
**Mitigation:**
- ใช้ database transaction
- ตรวจสอบ status ก่อน update
- Lock row ระหว่าง process

### Risk 4: Multiple Notifications
**Impact:** ส่ง Telegram ซ้ำ
**Mitigation:**
- ตรวจสอบ is_overtime ก่อนประมวลผล
- บันทึก notification_sent flag
- Idempotent task design

---

## 📈 Performance Considerations

### Database Query Optimization:
```sql
-- Index for faster query
CREATE INDEX idx_check_ins_overtime_monitor
ON check_ins(stay_type, status, expected_check_out_time, is_overtime);
```

### Celery Task Frequency:
- **Recommended:** ทุก 1 นาที (60 วินาที)
- **Maximum:** ทุก 30 วินาที (real-time กว่า)
- **Minimum:** ทุก 5 นาที (ประหยัด resource แต่ช้ากว่า)

### WebSocket Broadcasting:
- ใช้ room-based channel แทน broadcast ทั้งหมด
- Send เฉพาะ dashboard clients ที่ active

---

## 🎨 UI/UX Design Notes

### Color Scheme:
- **OCCUPIED_OVERTIME:** สีแดงเข้ม (#dc2626) + pulse animation
- **Icon:** ⏰ (alarm clock) หรือ ⚠️ (warning)
- **Badge:** "หมดเวลา" + จำนวนนาทีที่เกิน

### Dashboard Layout:
- แยก section "ห้องเกินเวลา" ไว้ด้านบน (priority high)
- แสดง countdown แบบ real-time
- ปุ่ม "Check-out ทันที" สำหรับ quick action

### Mobile Responsive:
- ใช้ icon แทนข้อความยาวๆ
- Show critical info only
- Touch-friendly button size

---

## 📝 Documentation Updates Needed

1. **README.md:** อธิบาย overtime auto-cutoff feature
2. **API Documentation:** Endpoint changes (if any)
3. **User Manual:** วิธีจัดการห้องที่เกินเวลา
4. **Admin Guide:** การ config Telegram notifications

---

## ✅ Acceptance Criteria

### Must Have:
- [ ] Temporary stay ครบ 3 ชั่วโมง → auto change status to OCCUPIED_OVERTIME
- [ ] Smart breaker ปิดอัตโนมัติเมื่อเปลี่ยนเป็น OCCUPIED_OVERTIME
- [ ] WebSocket broadcast overtime event
- [ ] Frontend แสดง "หมดเวลาเข้าพัก" พร้อม styling ที่ eye-catching
- [ ] Telegram notification ส่งถึง reception/admin
- [ ] Check-out จาก OCCUPIED_OVERTIME ได้ปกติ + คำนวณ overtime_charge
- [ ] Celery task ทำงานทุก 1 นาที
- [ ] Error handling สำหรับ breaker failure

### Nice to Have:
- [ ] Configuration สำหรับปรับระยะเวลา 3 ชั่วโมง
- [ ] Dashboard stats สำหรับ overtime rooms
- [ ] Filter/sort ห้องที่เกินเวลา
- [ ] Export overtime report

---

## 🔗 Related Files

### Backend:
- `backend/app/models/room.py`
- `backend/app/models/check_in.py`
- `backend/app/services/overtime_service.py` (new)
- `backend/app/services/breaker_service.py`
- `backend/app/services/room_service.py`
- `backend/app/tasks/overtime_tasks.py` (new)
- `backend/app/tasks/celery_app.py`
- `backend/alembic/versions/YYYYMMDD_add_occupied_overtime_status.py` (new)

### Frontend:
- `frontend/src/types/room.ts`
- `frontend/src/components/RoomCard.vue`
- `frontend/src/stores/dashboard.ts`
- `frontend/src/views/DashboardView.vue`

### Documentation:
- `PRD.md`
- `CLAUDE.md`
- `HOME_ASSISTANT_BREAKER_INTEGRATION_PLAN.md`

---

## 🎯 Success Metrics

- ⏱️ Overtime detection time: < 1 minute after expected_check_out_time
- 🔌 Breaker cutoff success rate: > 99%
- 📱 Notification delivery rate: > 99%
- 🐛 Error rate: < 0.1%
- 💰 Overtime charge accuracy: 100%

---

**สรุป:** แผนนี้ครอบคลุมทุกด้านของการพัฒนา Auto-Cutoff feature ตั้งแต่ database, backend logic, Celery tasks, breaker automation, frontend UI, notifications และ error handling พร้อม test cases และ risk mitigation
