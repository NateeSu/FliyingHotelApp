# คู่มือการทดสอบระบบ Home Assistant Breaker Control

## ภาพรวม
เอกสารนี้เป็นคู่มือการทดสอบระบบควบคุมเบรกเกอร์ไฟฟ้าผ่าน Home Assistant ที่ผสานเข้ากับ FlyingHotelApp PMS

**สร้างเมื่อ**: 2025-01-11
**ครอบคลุม**: Phase 1-4 (Database, Services, API, Frontend)

---

## สารบัญ
1. [การเตรียมสภาพแวดล้อม](#1-การเตรียมสภาพแวดล้อม)
2. [Phase 1: ทดสอบ Database & Models](#phase-1-ทดสอบ-database--models)
3. [Phase 2: ทดสอบ Service Layer](#phase-2-ทดสอบ-service-layer)
4. [Phase 3: ทดสอบ API Endpoints](#phase-3-ทดสอบ-api-endpoints)
5. [Phase 4: ทดสอบ Frontend](#phase-4-ทดสอบ-frontend)
6. [การทดสอบแบบ End-to-End](#การทดสอบแบบ-end-to-end)
7. [การแก้ไขปัญหาที่พบบ่อย](#การแก้ไขปัญหาที่พบบ่อย)

---

## 1. การเตรียมสภาพแวดล้อม

### 1.1 ข้อกำหนดเบื้องต้น

**Home Assistant Setup:**
- Home Assistant ติดตั้งและทำงานบนเครือข่ายท้องถิ่น (Local Network)
- URL ตัวอย่าง: `http://192.168.1.100:8123`
- มี Switch entity อย่างน้อย 1 อันสำหรับทดสอบ (เช่น `switch.test_breaker`)
- สร้าง Long-Lived Access Token แล้ว

**วิธีสร้าง Access Token:**
1. เข้า Home Assistant → คลิกที่ชื่อผู้ใช้มุมล่างซ้าย
2. เลื่อนลงไปที่ "Long-Lived Access Tokens"
3. คลิก "Create Token" → ตั้งชื่อ "FlyingHotel"
4. คัดลอก Token (ขึ้นต้นด้วย `eyJ...`)

**Docker Containers:**
```bash
# ตรวจสอบว่า containers ทำงานปกติ
docker-compose ps

# ควรเห็น containers เหล่านี้ในสถานะ Up:
# - backend
# - frontend
# - mysql
# - redis
# - celery-worker
# - adminer
```

### 1.2 การ Start ระบบ

```bash
# Start all services
docker-compose up -d

# ตรวจสอบ logs
docker-compose logs -f backend
docker-compose logs -f celery-worker
docker-compose logs -f frontend
```

### 1.3 การเข้าถึงระบบ

- **Frontend**: http://localhost:5173
- **Backend API Docs**: http://localhost:8000/docs
- **Adminer (Database)**: http://localhost:8080
  - Server: `mysql`
  - Username: `root`
  - Password: `rootpassword`
  - Database: `flyinghotel`

---

## Phase 1: ทดสอบ Database & Models

### 1.1 ตรวจสอบว่า Migration ทำงานสำเร็จ

```bash
# เข้า backend container
docker-compose exec backend bash

# ตรวจสอบ migration history
alembic history

# ควรเห็น migration:
# 20251111_0001_create_home_assistant_tables (head)
```

### 1.2 ตรวจสอบ Tables ใน Database

**ผ่าน Adminer** (http://localhost:8080):

1. Login เข้าสู่ database `flyinghotel`
2. ตรวจสอบว่ามี tables ใหม่ 4 ตัว:
   - `home_assistant_config`
   - `home_assistant_breakers`
   - `breaker_activity_logs`
   - `breaker_control_queue`

**ผ่าน MySQL CLI:**
```bash
docker-compose exec mysql mysql -u root -prootpassword flyinghotel

SHOW TABLES LIKE 'home_assistant%';
SHOW TABLES LIKE 'breaker%';

# ตรวจสอบ schema
DESCRIBE home_assistant_config;
DESCRIBE home_assistant_breakers;
DESCRIBE breaker_activity_logs;
DESCRIBE breaker_control_queue;
```

### 1.3 ตรวจสอบ Indexes และ Foreign Keys

```sql
-- ตรวจสอบ indexes
SHOW INDEX FROM home_assistant_breakers;
SHOW INDEX FROM breaker_activity_logs;
SHOW INDEX FROM breaker_control_queue;

-- ควรเห็น indexes:
-- idx_breakers_room_id
-- idx_breakers_state
-- idx_breakers_auto_control
-- idx_activity_logs_breaker_id
-- idx_activity_logs_created_at
-- idx_control_queue_breaker_id
-- idx_control_queue_status
-- idx_control_queue_scheduled_at

-- ตรวจสอบ foreign keys
SELECT
  CONSTRAINT_NAME,
  TABLE_NAME,
  COLUMN_NAME,
  REFERENCED_TABLE_NAME,
  REFERENCED_COLUMN_NAME
FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
WHERE TABLE_SCHEMA = 'flyinghotel'
  AND TABLE_NAME IN ('home_assistant_breakers', 'breaker_activity_logs', 'breaker_control_queue')
  AND REFERENCED_TABLE_NAME IS NOT NULL;
```

### 1.4 ทดสอบ Enum Values

```sql
-- ตรวจสอบว่า enum values ถูกต้อง (ต้องเป็น UPPERCASE ทั้งหมด)
SHOW COLUMNS FROM home_assistant_breakers LIKE 'current_state';
-- Type: enum('ON','OFF','UNAVAILABLE')

SHOW COLUMNS FROM breaker_activity_logs LIKE 'action';
-- Type: enum('TURN_ON','TURN_OFF','STATUS_SYNC')

SHOW COLUMNS FROM breaker_activity_logs LIKE 'trigger_type';
-- Type: enum('AUTO','MANUAL','SYSTEM')

SHOW COLUMNS FROM breaker_activity_logs LIKE 'status';
-- Type: enum('SUCCESS','FAILED','TIMEOUT')

SHOW COLUMNS FROM breaker_control_queue LIKE 'status';
-- Type: enum('PENDING','PROCESSING','COMPLETED','FAILED','CANCELLED')
```

**✅ Expected Results:**
- ✅ ทั้ง 4 tables ถูกสร้างสำเร็จ
- ✅ Indexes ครบถ้วน
- ✅ Foreign keys เชื่อมโยงถูกต้อง
- ✅ Enum values เป็น UPPERCASE

---

## Phase 2: ทดสอบ Service Layer

### 2.1 ตรวจสอบ Encryption Key

```bash
# ตรวจสอบว่า encryption key ถูกสร้างแล้ว
docker-compose exec backend cat /app/.encryption_key

# ควรเห็น key ขนาด 44 characters (base64)
# ตัวอย่าง: 7CcKurV_QcLo0IaxWf7s0PCXZzbjKmf7EFXgoiOvqmc=
```

### 2.2 ทดสอบ Encryption Service

**สร้างไฟล์ทดสอบ** `test_encryption.py`:
```python
import sys
sys.path.append('/app')

from app.core.encryption import encrypt_value, decrypt_value

# Test token
test_token = "test_secret_token_12345"

# Encrypt
encrypted = encrypt_value(test_token)
print(f"Encrypted: {encrypted}")

# Decrypt
decrypted = decrypt_value(encrypted)
print(f"Decrypted: {decrypted}")

# Verify
assert decrypted == test_token, "Encryption/Decryption failed!"
print("✅ Encryption test passed!")
```

```bash
# Run test
docker-compose exec backend python test_encryption.py
```

**✅ Expected Result:**
```
Encrypted: gAAAABm5x...
Decrypted: test_secret_token_12345
✅ Encryption test passed!
```

### 2.3 ตรวจสอบ Celery Tasks

```bash
# ดู logs ของ celery worker
docker-compose logs -f celery-worker

# ควรเห็น tasks ถูก register:
# [tasks]
#   . breaker.sync_all_breaker_states
#   . breaker.process_control_queue
#   . breaker.health_check
#   . breaker.cleanup_old_queue_items
#   . breaker.cleanup_old_activity_logs
#   . booking.check_no_show_bookings
```

### 2.4 ทดสอบ Celery Beat Schedule

```bash
# ดู celerybeat schedule
docker-compose exec backend python -c "
from app.tasks.celery_app import celery_app
for name, schedule in celery_app.conf.beat_schedule.items():
    print(f'{name}: {schedule}')
"
```

**✅ Expected Output:**
```
breaker.sync_all_breaker_states: {'task': 'breaker.sync_all_breaker_states', 'schedule': 30.0}
breaker.process_control_queue: {'task': 'breaker.process_control_queue', 'schedule': 5.0}
breaker.health_check: {'task': 'breaker.health_check', 'schedule': 300.0}
...
```

### 2.5 ทดสอบ Helper Functions

**สร้างไฟล์ทดสอบ** `test_helpers.py`:
```python
import sys
sys.path.append('/app')

from app.services.breaker_helpers import (
    room_status_requires_breaker_on,
    ha_state_to_breaker_state,
    breaker_state_to_ha_service
)
from app.models.room import RoomStatus
from app.models.home_assistant import BreakerState

# Test 1: Room status logic
print("Testing room_status_requires_breaker_on:")
assert room_status_requires_breaker_on(RoomStatus.OCCUPIED) == True
assert room_status_requires_breaker_on(RoomStatus.CLEANING) == True
assert room_status_requires_breaker_on(RoomStatus.AVAILABLE) == False
print("✅ Room status logic correct")

# Test 2: HA state conversion
print("\nTesting ha_state_to_breaker_state:")
assert ha_state_to_breaker_state("on") == BreakerState.ON
assert ha_state_to_breaker_state("off") == BreakerState.OFF
assert ha_state_to_breaker_state("unavailable") == BreakerState.UNAVAILABLE
print("✅ State conversion correct")

# Test 3: Service mapping
print("\nTesting breaker_state_to_ha_service:")
assert breaker_state_to_ha_service(BreakerState.ON) == "turn_on"
assert breaker_state_to_ha_service(BreakerState.OFF) == "turn_off"
print("✅ Service mapping correct")

print("\n✅ All helper function tests passed!")
```

```bash
docker-compose exec backend python test_helpers.py
```

**✅ Expected Results:**
- ✅ Encryption key exists
- ✅ Encryption/Decryption works
- ✅ 5 breaker tasks registered in Celery
- ✅ Beat schedule configured correctly
- ✅ Helper functions work as expected

---

## Phase 3: ทดสอบ API Endpoints

### 3.1 การเตรียมตัว

**สร้าง Test User (ADMIN role):**
```bash
# เข้า backend container
docker-compose exec backend python

# ใน Python shell:
from app.db.session import SessionLocal
from app.models.user import User, UserRole
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
db = SessionLocal()

# สร้าง test admin user
admin = User(
    username="testadmin",
    full_name="Test Admin",
    hashed_password=pwd_context.hash("testpass123"),
    role=UserRole.ADMIN,
    is_active=True
)
db.add(admin)
db.commit()
print(f"Created admin user: {admin.username}")
db.close()
exit()
```

**Login และรับ Token:**

ไปที่ http://localhost:8000/docs

1. คลิก "Authorize" ปุ่มสีเขียว
2. Username: `testadmin`
3. Password: `testpass123`
4. คลิก "Authorize"

หรือใช้ curl:
```bash
TOKEN=$(curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testadmin&password=testpass123" | jq -r '.access_token')

echo "Token: $TOKEN"
```

### 3.2 ทดสอบ Home Assistant Configuration API

**Test 1: Get Status (ก่อนตั้งค่า)**
```bash
curl -X GET "http://localhost:8000/api/v1/home-assistant/status" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response:**
```json
{
  "is_configured": false,
  "is_online": false,
  "last_ping_at": null,
  "ha_version": null,
  "base_url": null
}
```

**Test 2: Test Connection**
```bash
curl -X POST "http://localhost:8000/api/v1/home-assistant/test-connection" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "base_url": "http://192.168.1.100:8123",
    "access_token": "YOUR_HA_TOKEN_HERE"
  }'
```

**Expected Response (Success):**
```json
{
  "success": true,
  "message": "เชื่อมต่อ Home Assistant สำเร็จ",
  "ha_version": "2024.1.0",
  "entity_count": 150,
  "response_time_ms": 250
}
```

**Expected Response (Failure - Wrong URL):**
```json
{
  "success": false,
  "message": "ไม่สามารถเชื่อมต่อได้: Connection refused"
}
```

**Test 3: Save Configuration**
```bash
curl -X POST "http://localhost:8000/api/v1/home-assistant/config" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "base_url": "http://192.168.1.100:8123",
    "access_token": "YOUR_HA_TOKEN_HERE"
  }'
```

**Expected Response:**
```json
{
  "id": 1,
  "base_url": "http://192.168.1.100:8123",
  "access_token_masked": "ey***abc",
  "is_online": true,
  "last_ping_at": "2025-01-11T10:30:00",
  "ha_version": "2024.1.0",
  "is_active": true,
  "created_at": "2025-01-11T10:30:00",
  "updated_at": "2025-01-11T10:30:00"
}
```

**Test 4: Get Configuration**
```bash
curl -X GET "http://localhost:8000/api/v1/home-assistant/config" \
  -H "Authorization: Bearer $TOKEN"
```

**Test 5: Get Entities**
```bash
# Get all entities
curl -X GET "http://localhost:8000/api/v1/home-assistant/entities" \
  -H "Authorization: Bearer $TOKEN"

# Filter by domain (switches only)
curl -X GET "http://localhost:8000/api/v1/home-assistant/entities?domain_filter=switch" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response:**
```json
{
  "entities": [
    {
      "entity_id": "switch.test_breaker",
      "friendly_name": "Test Breaker",
      "state": "off",
      "attributes": {}
    }
  ],
  "total": 1
}
```

**Test 6: Delete Configuration**
```bash
curl -X DELETE "http://localhost:8000/api/v1/home-assistant/config" \
  -H "Authorization: Bearer $TOKEN"
```

### 3.3 ทดสอบ Breakers API

**Prerequisite: ต้องมี Home Assistant config และ room อย่างน้อย 1 ห้อง**

**Test 1: Create Breaker**
```bash
curl -X POST "http://localhost:8000/api/v1/breakers/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": "switch.test_breaker",
    "friendly_name": "เบรกเกอร์ห้อง 101",
    "room_id": 1,
    "auto_control_enabled": true
  }'
```

**Expected Response:**
```json
{
  "id": 1,
  "entity_id": "switch.test_breaker",
  "friendly_name": "เบรกเกอร์ห้อง 101",
  "room_id": 1,
  "room_number": "101",
  "room_status": "AVAILABLE",
  "auto_control_enabled": true,
  "is_available": true,
  "current_state": "OFF",
  "last_state_update": "2025-01-11T10:35:00",
  "consecutive_errors": 0,
  "last_error_message": null,
  "is_active": true,
  "created_at": "2025-01-11T10:35:00",
  "updated_at": "2025-01-11T10:35:00"
}
```

**Test 2: Get All Breakers**
```bash
# Get all
curl -X GET "http://localhost:8000/api/v1/breakers/" \
  -H "Authorization: Bearer $TOKEN"

# Filter by room
curl -X GET "http://localhost:8000/api/v1/breakers/?room_id=1" \
  -H "Authorization: Bearer $TOKEN"

# Filter by state
curl -X GET "http://localhost:8000/api/v1/breakers/?current_state=OFF" \
  -H "Authorization: Bearer $TOKEN"

# Filter by auto_control
curl -X GET "http://localhost:8000/api/v1/breakers/?auto_control_enabled=true" \
  -H "Authorization: Bearer $TOKEN"
```

**Test 3: Get Breaker by ID**
```bash
curl -X GET "http://localhost:8000/api/v1/breakers/1" \
  -H "Authorization: Bearer $TOKEN"
```

**Test 4: Update Breaker**
```bash
curl -X PUT "http://localhost:8000/api/v1/breakers/1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "friendly_name": "เบรกเกอร์ห้อง 101 (Updated)",
    "auto_control_enabled": false
  }'
```

**Test 5: Turn On Breaker (Manual)**
```bash
curl -X POST "http://localhost:8000/api/v1/breakers/1/turn-on" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "reason": "ทดสอบเปิดด้วยตนเอง"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "เปิด Breaker สำเร็จ",
  "breaker_id": 1,
  "new_state": "ON",
  "response_time_ms": 300
}
```

**ตรวจสอบใน Home Assistant:**
- Switch ควรเปลี่ยนเป็น "on"
- ตรวจสอบผ่าน Home Assistant UI หรือ Developer Tools → States

**Test 6: Turn Off Breaker (Manual)**
```bash
curl -X POST "http://localhost:8000/api/v1/breakers/1/turn-off" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "reason": "ทดสอบปิดด้วยตนเอง"
  }'
```

**Test 7: Sync Status**
```bash
curl -X POST "http://localhost:8000/api/v1/breakers/1/sync-status" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response:**
```json
{
  "success": true,
  "message": "ซิงค์สถานะสำเร็จ",
  "breaker_id": 1,
  "current_state": "OFF",
  "is_available": true,
  "synced_at": "2025-01-11T10:40:00"
}
```

**Test 8: Sync All Breakers**
```bash
curl -X POST "http://localhost:8000/api/v1/breakers/sync-all" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response:**
```json
{
  "success": true,
  "message": "ซิงค์ breakers ทั้งหมดสำเร็จ",
  "total": 1,
  "success_count": 1,
  "failed_count": 0
}
```

**Test 9: Get Activity Logs**
```bash
# Get logs for specific breaker
curl -X GET "http://localhost:8000/api/v1/breakers/1/logs" \
  -H "Authorization: Bearer $TOKEN"

# Get all logs
curl -X GET "http://localhost:8000/api/v1/breakers/logs/all" \
  -H "Authorization: Bearer $TOKEN"

# Filter by action
curl -X GET "http://localhost:8000/api/v1/breakers/logs/all?action=TURN_ON" \
  -H "Authorization: Bearer $TOKEN"

# Filter by trigger_type
curl -X GET "http://localhost:8000/api/v1/breakers/logs/all?trigger_type=MANUAL" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response:**
```json
{
  "logs": [
    {
      "id": 1,
      "breaker_id": 1,
      "entity_id": "switch.test_breaker",
      "friendly_name": "เบรกเกอร์ห้อง 101",
      "action": "TURN_ON",
      "trigger_type": "MANUAL",
      "triggered_by": 1,
      "triggered_by_name": "Test Admin",
      "room_status_before": null,
      "room_status_after": null,
      "status": "SUCCESS",
      "error_message": null,
      "response_time_ms": 300,
      "created_at": "2025-01-11T10:38:00"
    }
  ],
  "total": 1
}
```

**Test 10: Get Statistics**
```bash
curl -X GET "http://localhost:8000/api/v1/breakers/stats/overview" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response:**
```json
{
  "total_breakers": 1,
  "online_breakers": 1,
  "offline_breakers": 0,
  "breakers_on": 0,
  "breakers_off": 1,
  "auto_control_enabled": 1,
  "breakers_with_errors": 0,
  "total_actions_today": 2,
  "success_rate_today": 100.0,
  "avg_response_time_ms": 300
}
```

**Test 11: Delete Breaker**
```bash
curl -X DELETE "http://localhost:8000/api/v1/breakers/1" \
  -H "Authorization: Bearer $TOKEN"
```

### 3.4 ทดสอบ Auto Control Logic

**Test Scenario: Room Status Change → Auto Control**

```bash
# 1. สร้าง breaker ผูกกับห้อง 101 และเปิด auto_control
curl -X POST "http://localhost:8000/api/v1/breakers/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": "switch.test_breaker",
    "friendly_name": "เบรกเกอร์ห้อง 101",
    "room_id": 1,
    "auto_control_enabled": true
  }'

# 2. เปลี่ยนสถานะห้องเป็น OCCUPIED (ควรเปิด breaker อัตโนมัติ)
curl -X PATCH "http://localhost:8000/api/v1/rooms/1/status" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "OCCUPIED"
  }'

# 3. รอ 5 วินาที (ให้ celery queue ประมวลผล)
sleep 5

# 4. ตรวจสอบสถานะ breaker
curl -X GET "http://localhost:8000/api/v1/breakers/1" \
  -H "Authorization: Bearer $TOKEN"

# Expected: current_state = "ON"

# 5. เปลี่ยนสถานะห้องเป็น AVAILABLE (ควรปิด breaker อัตโนมัติ)
curl -X PATCH "http://localhost:8000/api/v1/rooms/1/status" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "AVAILABLE"
  }'

# 6. รอ 5 วินาที
sleep 5

# 7. ตรวจสอบสถานะ breaker อีกครั้ง
curl -X GET "http://localhost:8000/api/v1/breakers/1" \
  -H "Authorization: Bearer $TOKEN"

# Expected: current_state = "OFF"

# 8. ดู activity logs เพื่อยืนยันว่ามี AUTO actions
curl -X GET "http://localhost:8000/api/v1/breakers/1/logs?trigger_type=AUTO" \
  -H "Authorization: Bearer $TOKEN"
```

**✅ Expected Results:**
- ✅ All Home Assistant config endpoints work
- ✅ All Breaker CRUD endpoints work
- ✅ Manual control (turn on/off) works with real HA
- ✅ Sync status works
- ✅ Activity logs are created
- ✅ Statistics are calculated correctly
- ✅ Auto control triggers when room status changes

---

## Phase 4: ทดสอบ Frontend

### 4.1 การเข้าสู่ระบบ

1. เปิดเบราว์เซอร์ไปที่ http://localhost:5173
2. Login ด้วย:
   - Username: `testadmin`
   - Password: `testpass123`
3. ควรเข้าสู่หน้า Home Dashboard

### 4.2 ทดสอบ Home Assistant Settings

**Test 1: เข้าหน้า Settings**
1. คลิกปุ่ม "ตั้งค่าระบบ" จาก Home page
2. หรือไปที่ http://localhost:5173/settings
3. คลิกแท็บ "Home Assistant"

**Test 2: ตรวจสอบ Status Banner**
- กรณียังไม่ได้ตั้งค่า: ควรแสดง "ไม่ได้เชื่อมต่อ" สีแดง
- กรณีตั้งค่าแล้ว: ควรแสดง "เชื่อมต่อแล้ว" สีเขียว พร้อม version และ URL

**Test 3: กรอกข้อมูล Configuration**
1. Base URL: `http://192.168.1.100:8123`
2. Access Token: วาง token จาก Home Assistant
3. คลิกไอคอน "ตา" เพื่อแสดง/ซ่อน token → ควรทำงาน
4. อ่านคำแนะนำใต้ช่องกรอก → ควรมีคำอธิบายชัดเจน

**Test 4: ทดสอบการเชื่อมต่อ**
1. คลิกปุ่ม "ทดสอบการเชื่อมต่อ"
2. ระหว่างทดสอบ: ปุ่มควรแสดง "กำลังทดสอบ..." และ disabled
3. สำเร็จ: แสดงกล่องสีเขียว พร้อม version, entity count, response time
4. ล้มเหลว: แสดงกล่องสีแดง พร้อมข้อความ error

**Test 5: บันทึกการตั้งค่า**
1. คลิกปุ่ม "บันทึกการตั้งค่า"
2. ควรเห็น Toast notification "บันทึกการตั้งค่า Home Assistant สำเร็จ" สีเขียว
3. Status Banner ควรเปลี่ยนเป็น "เชื่อมต่อแล้ว"
4. URL และ Version ควรแสดงข้อมูลถูกต้อง

**Test 6: รีเซ็ตฟอร์ม**
1. แก้ไขข้อมูลในฟอร์ม
2. คลิกปุ่ม "รีเซ็ต"
3. ข้อมูลควรกลับไปเป็นค่าเดิมที่บันทึกไว้

**Test 7: ลบการตั้งค่า**
1. คลิกปุ่ม "ลบการตั้งค่า" (สีแดง)
2. ควรมี confirmation dialog
3. ยืนยันการลบ
4. Toast notification "ลบการตั้งค่า Home Assistant สำเร็จ"
5. Status Banner กลับเป็น "ไม่ได้เชื่อมต่อ"
6. ฟอร์มเคลียร์เป็นค่าว่าง

### 4.3 ทดสอบ Breakers Management Page

**Test 1: เข้าหน้า Breakers**
1. จาก Home page คลิก "เบรกเกอร์ไฟฟ้า"
2. หรือไปที่ http://localhost:5173/breakers

**Test 2: ตรวจสอบ Statistics Cards**
- ควรเห็น 8 การ์ด:
  1. ทั้งหมด
  2. ออนไลน์ (สีเขียว)
  3. ออฟไลน์ (สีแดง)
  4. เปิด
  5. ปิด
  6. ควบคุมอัตโนมัติ
  7. มีข้อผิดพลาด
  8. Response Time
- ตัวเลขควรถูกต้องตามข้อมูลจริง

**Test 3: สร้าง Breaker ใหม่**
1. คลิกปุ่ม "+ เพิ่ม Breaker"
2. กรอกข้อมูล:
   - Entity ID: `switch.test_breaker` (ต้องมีใน Home Assistant)
   - ชื่อเรียก: `เบรกเกอร์ห้อง 101`
   - ผูกกับห้อง: เลือกห้อง 101
   - เปิดใช้งานควบคุมอัตโนมัติ: ✓
3. คลิก "บันทึก"
4. ควรเห็น Toast "เพิ่ม Breaker สำเร็จ"
5. Breaker card ใหม่ปรากฏในหน้า

**Test 4: ตรวจสอบ Breaker Card**
- Header แสดง friendly name และ entity_id
- มีจุดสีเขียว (online) หรือแดง (offline) กระพริบ
- แสดง badge ห้องที่ผูก (ถ้ามี)
- แสดง State badge (เปิด/ปิด/ไม่พร้อมใช้งาน) สีถูกต้อง
- แสดงโหมดควบคุม (🤖 อัตโนมัติ / 🎮 ด้วยตนเอง)
- แสดงเวลาอัปเดตล่าสุด

**Test 5: Manual Control - Turn On**
1. คลิกปุ่ม "เปิด"
2. ปุ่มควร disabled ระหว่างประมวลผล
3. Toast "กำลังเปิด Breaker"
4. Breaker card อัปเดตเป็นสีเขียว
5. State badge เปลี่ยนเป็น "เปิด"
6. **ตรวจสอบใน Home Assistant**: Switch ควรเปิดจริง

**Test 6: Manual Control - Turn Off**
1. คลิกปุ่ม "ปิด"
2. Toast "กำลังปิด Breaker"
3. Breaker card อัปเดตเป็นสีขาว/เทา
4. State badge เปลี่ยนเป็น "ปิด"
5. **ตรวจสอบใน Home Assistant**: Switch ควรปิดจริง

**Test 7: Sync Status**
1. **เปลี่ยนสถานะ switch ใน Home Assistant** ด้วยตนเอง
2. กลับมาที่หน้า Breakers
3. คลิกปุ่ม "↻" (Sync) บน Breaker card
4. Toast "ซิงค์สถานะสำเร็จ"
5. Breaker card อัปเดตตามสถานะจริงใน HA

**Test 8: Sync All**
1. คลิกปุ่ม "ซิงค์ทั้งหมด" ด้านบน
2. ปุ่มแสดง "กำลังซิงค์..."
3. Toast "ซิงค์ทั้งหมดสำเร็จ"
4. ทุก breaker card อัปเดตสถานะ

**Test 9: Edit Breaker**
1. คลิกปุ่ม "แก้ไข" บน Breaker card
2. Dialog เปิดขึ้น พร้อมข้อมูลเดิม
3. แก้ไข:
   - ชื่อเรียก: เพิ่ม "(Updated)"
   - เปลี่ยนโหมดควบคุม
4. คลิก "บันทึก"
5. Toast "อัปเดต Breaker สำเร็จ"
6. Breaker card แสดงข้อมูลใหม่

**Test 10: View Activity Logs**
1. คลิกปุ่ม "ประวัติ" บน Breaker card
2. Dialog เปิดแสดงรายการ logs
3. ตรวจสอบแต่ละ log:
   - มี badge: Action (เปิด/ปิด/ซิงค์)
   - มี badge: Trigger (อัตโนมัติ/กดเอง/ระบบ)
   - มี badge: Status (สำเร็จ/ล้มเหลว/หมดเวลา)
   - แสดงผู้ทำ (ถ้ามี)
   - แสดงสถานะห้อง before/after (ถ้าเป็น AUTO)
   - แสดง response time
   - แสดงเวลา

**Test 11: Filter Breakers**
1. **Filter by Room**: เลือกห้อง → แสดงเฉพาะ breaker ของห้องนั้น
2. **Filter by State**: เลือก "เปิด" → แสดงเฉพาะ breaker ที่เปิดอยู่
3. **Filter by Auto Control**: เลือก "ควบคุมอัตโนมัติ" → แสดงเฉพาะ breaker ที่เปิด auto

**Test 12: Delete Breaker**
1. คลิกปุ่ม "แก้ไข" บน Breaker card
2. ใน Edit dialog คลิกปุ่ม "ลบ Breaker" (สีแดง)
3. Confirmation dialog "คุณต้องการลบ Breaker..."
4. ยืนยัน
5. Toast "ลบ Breaker สำเร็จ"
6. Breaker card หายจากหน้า

**Test 13: Error Display**
1. ปิด Home Assistant (หรือใส่ entity_id ที่ไม่มีจริง)
2. สร้าง breaker ใหม่
3. ลองเปิด/ปิด breaker
4. Breaker card ควรแสดง:
   - `consecutive_errors` เพิ่มขึ้น
   - แสดงกล่องสีแดง "⚠️ ข้อผิดพลาด: X ครั้ง"
   - แสดง error message

**Test 14: Empty State**
1. ลบ breaker ทั้งหมด
2. ควรเห็น:
   - ไอคอน ⚡ ขนาดใหญ่
   - "ยังไม่มี Breaker"
   - "คลิกปุ่ม 'เพิ่ม Breaker' เพื่อเริ่มต้น"

### 4.4 ทดสอบ Responsive Design

**Mobile (< 768px):**
1. เปิด DevTools → Toggle Device Toolbar
2. เลือก iPhone 12 Pro
3. ทดสอบ:
   - Statistics cards จัดเรียงเป็น 2 คอลัมน์
   - Breaker cards จัดเรียงเป็น 1 คอลัมน์
   - Dialogs เต็มหน้าจอ
   - ปุ่มกดง่าย (ขนาดเหมาะสม)
   - ฟอร์มใช้งานได้สะดวก

**Tablet (768px - 1023px):**
1. เลือก iPad
2. ทดสอบ:
   - Statistics cards จัดเรียงเป็น 4 คอลัมน์
   - Breaker cards จัดเรียงเป็น 2 คอลัมน์
   - Navigation ใช้งานได้ดี

**Desktop (> 1024px):**
1. Full width browser
2. ทดสอบ:
   - Statistics cards จัดเรียงเป็น 8 คอลัมน์
   - Breaker cards จัดเรียงเป็น 3 คอลัมน์
   - Content ไม่กระจายเกินไป (max-width: 7xl)

### 4.5 ทดสอบ Error Handling

**Test 1: Network Error**
1. ปิด backend: `docker-compose stop backend`
2. ลองใช้ฟีเจอร์ต่างๆ
3. ควรเห็น Toast error พร้อมข้อความเหมาะสม
4. เปิด backend กลับมา: `docker-compose start backend`

**Test 2: Validation Error**
1. สร้าง breaker โดยไม่กรอก Entity ID
2. ควรไม่สามารถ submit ได้ (HTML5 validation)
3. กรอก Entity ID ผิดรูปแบบ (ไม่มี dot)
4. ควรได้รับ error จาก API

**Test 3: Unauthorized Access**
1. Logout
2. พยายามเข้า http://localhost:5173/breakers
3. ควร redirect ไป login page

**Test 4: Permission Error**
1. สร้าง user ที่ role เป็น HOUSEKEEPING
2. Login ด้วย user นี้
3. พยายามเข้า /breakers
4. ควร redirect ไป Home (ไม่มีสิทธิ์)

**✅ Expected Results:**
- ✅ Settings page ทำงานครบทุกฟังก์ชัน
- ✅ Breakers page แสดงข้อมูลถูกต้อง
- ✅ Statistics อัปเดตตามเวลาจริง
- ✅ Manual control สั่งงาน HA ได้จริง
- ✅ Sync status ดึงข้อมูลจาก HA ถูกต้อง
- ✅ Activity logs แสดงประวัติครบถ้วน
- ✅ Filters ทำงานถูกต้อง
- ✅ Responsive design ใช้งานได้ทุก device
- ✅ Error handling ครอบคลุม
- ✅ Toast notifications แสดงเหมาะสม

---

## การทดสอบแบบ End-to-End

### Scenario 1: เช็คอินห้อง → เบรกเกอร์เปิดอัตโนมัติ

**Prerequisite:**
- มี breaker ผูกกับห้อง 101
- `auto_control_enabled = true`
- ห้อง 101 สถานะ AVAILABLE

**Steps:**
1. เข้าหน้า Dashboard (http://localhost:5173/dashboard)
2. คลิกห้อง 101
3. คลิกปุ่ม "เช็คอิน"
4. กรอกข้อมูลลูกค้า → บันทึก
5. สถานะห้องเปลี่ยนเป็น OCCUPIED
6. **รอ 5-10 วินาที**
7. เข้าหน้า Breakers
8. ✅ Breaker ห้อง 101 ควรเปิดอัตโนมัติ (สีเขียว, State = "เปิด")
9. คลิก "ประวัติ"
10. ✅ ควรเห็น log:
    - Action: เปิด
    - Trigger: อัตโนมัติ
    - สถานะห้อง: AVAILABLE → OCCUPIED
    - Status: สำเร็จ

**ตรวจสอบใน Home Assistant:**
- Switch ควรเป็น "on"

**ตรวจสอบใน Database:**
```sql
SELECT * FROM breaker_activity_logs
WHERE breaker_id = 1
ORDER BY created_at DESC
LIMIT 1;

-- Expected:
-- action = 'TURN_ON'
-- trigger_type = 'AUTO'
-- room_status_before = 'AVAILABLE'
-- room_status_after = 'OCCUPIED'
-- status = 'SUCCESS'
```

### Scenario 2: เช็คเอาท์ห้อง → เบรกเกอร์ปิดอัตโนมัติ

**Steps:**
1. จาก Scenario 1 ต่อเนื่อง (ห้อง 101 มีผู้พัก)
2. เข้าหน้า Dashboard
3. คลิกห้อง 101
4. คลิกปุ่ม "เช็คเอาท์"
5. ยืนยันการเช็คเอาท์
6. สถานะห้องเปลี่ยนเป็น CLEANING
7. **รอ 5-10 วินาที**
8. เข้าหน้า Breakers
9. ✅ Breaker ยังคงเปิดอยู่ (เพราะห้องสถานะ CLEANING ต้องเปิดไฟ)
10. กลับไป Dashboard → คลิกห้อง 101
11. คลิกปุ่ม "เสร็จสิ้น" (Housekeeping เสร็จ)
12. สถานะห้องเปลี่ยนเป็น AVAILABLE
13. **รอ 5-10 วินาที**
14. เข้าหน้า Breakers
15. ✅ Breaker ควรปิดอัตโนมัติ (สีขาว/เทา, State = "ปิด")

**ตรวจสอบใน Home Assistant:**
- Switch ควรเป็น "off"

### Scenario 3: ปิด Auto Control → ควบคุมด้วยตนเอง

**Steps:**
1. เข้าหน้า Breakers
2. คลิก "แก้ไข" บน breaker ห้อง 101
3. ✓ ยกเลิก "เปิดใช้งานระบบควบคุมอัตโนมัติ"
4. บันทึก
5. กลับไป Dashboard
6. เช็คอินห้อง 101 อีกครั้ง
7. **รอ 5-10 วินาที**
8. เข้าหน้า Breakers
9. ✅ Breaker ควรยังปิดอยู่ (ไม่เปิดอัตโนมัติ)
10. คลิกปุ่ม "เปิด" ด้วยตนเอง
11. ✅ Breaker เปิดสำเร็จ
12. ดู "ประวัติ"
13. ✅ Log ล่าสุดควรเป็น Trigger: กดเอง

### Scenario 4: Home Assistant Offline → Error Handling

**Steps:**
1. ปิด Home Assistant หรือตัดการเชื่อมต่อ
2. เข้าหน้า Breakers
3. **รอ 30 วินาที** (sync task ทำงาน)
4. ✅ Breaker cards ควรแสดง:
   - จุดสีแดง (offline)
   - State badge = "ไม่พร้อมใช้งาน"
   - Background สีแดง/ส้ม
5. ลองคลิกปุ่ม "เปิด"
6. ✅ ควรได้รับ error toast
7. ✅ Breaker card แสดง error message
8. เปิด Home Assistant กลับมา
9. คลิกปุ่ม "ซิงค์ทั้งหมด"
10. ✅ Breaker กลับมา online (จุดสีเขียว)

### Scenario 5: Multiple Rooms Auto Control

**Setup:**
- สร้าง breaker 3 อัน ผูกกับห้อง 101, 102, 103
- เปิด auto_control ทั้งหมด

**Steps:**
1. เช็คอินห้อง 101, 102, 103 พร้อมกัน
2. **รอ 10 วินาที**
3. เข้าหน้า Breakers
4. ✅ Breaker ทั้ง 3 ควรเปิดอัตโนมัติ
5. Statistics card "เปิด" ควรแสดง 3
6. เช็คเอาท์ห้อง 102
7. เสร็จสิ้นการทำความสะอาด (AVAILABLE)
8. **รอ 10 วินาที**
9. ✅ Breaker ห้อง 102 ปิด
10. ✅ Breaker ห้อง 101 และ 103 ยังเปิดอยู่
11. Statistics card "เปิด" ควรแสดง 2

### Scenario 6: Activity Logs Filtering

**Steps:**
1. มี activity logs หลากหลาย (AUTO, MANUAL, SUCCESS, FAILED)
2. เข้า Breakers page → คลิก "ประวัติ" บน breaker
3. ทดสอบ filter:
   - Filter by Action: TURN_ON → แสดงเฉพาะการเปิด
   - Filter by Trigger: AUTO → แสดงเฉพาะอัตโนมัติ
   - Filter by Status: SUCCESS → แสดงเฉพาะสำเร็จ
   - Filter by Date range → แสดงตาม period

**✅ Expected Results:**
- ✅ Auto control ทำงานถูกต้องตาม room status
- ✅ Manual control override auto control
- ✅ Error handling ครอบคลุม
- ✅ Multiple breakers ทำงานพร้อมกันได้
- ✅ Activity logs บันทึกครบถ้วน
- ✅ Statistics อัปเดตแบบ real-time

---

## การแก้ไขปัญหาที่พบบ่อย

### ปัญหา 1: Celery Tasks ไม่ทำงาน

**อาการ:**
- Auto control ไม่ทำงาน
- Breaker ไม่ sync สถานะ

**วิธีแก้:**
```bash
# 1. ตรวจสอบว่า celery worker ทำงานอยู่
docker-compose ps celery-worker

# 2. ดู logs
docker-compose logs -f celery-worker

# 3. Restart celery worker
docker-compose restart celery-worker

# 4. ตรวจสอบว่า tasks ถูก register
docker-compose logs celery-worker | grep "breaker."
```

### ปัญหา 2: Encryption Error

**อาการ:**
- Error: "Encryption key not found"
- Error: "Invalid token"

**วิธีแก้:**
```bash
# 1. ตรวจสอบว่ามี encryption key
docker-compose exec backend ls -la /app/.encryption_key

# 2. ถ้าไม่มี ให้สร้างใหม่
docker-compose exec backend python -c "
from app.core.encryption import generate_and_save_encryption_key
generate_and_save_encryption_key()
print('Key generated')
"

# 3. Restart backend
docker-compose restart backend
```

### ปัญหา 3: Home Assistant Connection Failed

**อาการ:**
- Test connection ล้มเหลว
- "Connection refused" error

**วิธีแก้:**
1. ตรวจสอบว่า Home Assistant ทำงานอยู่
2. ตรวจสอบ URL ถูกต้อง (http:// หรือ https://)
3. ตรวจสอบว่า backend container สามารถเข้าถึง HA network ได้:
```bash
docker-compose exec backend curl http://192.168.1.100:8123/api/
```
4. ตรวจสอบ Access Token ยังใช้ได้อยู่:
   - ไปที่ Home Assistant → Profile → Long-Lived Access Tokens
   - ตรวจสอบว่า token ยังไม่ถูกลบหรือหมดอายุ
5. ตรวจสอบ Firewall ไม่บล็อก

### ปัญหา 4: Breaker State ไม่ตรงกับ Home Assistant

**อาการ:**
- Frontend แสดงสถานะต่างจากใน HA

**วิธีแก้:**
1. คลิกปุ่ม "Sync" บน breaker card
2. หรือคลิก "ซิงค์ทั้งหมด"
3. ตรวจสอบว่า Entity ID ถูกต้อง:
```bash
# ใน Home Assistant Developer Tools → States
# หา entity_id ที่ตรงกัน
```
4. ตรวจสอบ logs:
```bash
docker-compose logs backend | grep "sync_breaker_status"
```

### ปัญหา 5: Auto Control ไม่ทำงาน

**อาการ:**
- เปลี่ยนสถานะห้อง แต่ breaker ไม่เปลี่ยน

**Checklist:**
1. ✓ Breaker ผูกกับห้อง (`room_id` ไม่เป็น null)
2. ✓ `auto_control_enabled = true`
3. ✓ Celery worker ทำงานอยู่
4. ✓ Control queue ถูกประมวลผล

**วิธีแก้:**
```bash
# 1. ตรวจสอบ control queue
docker-compose exec mysql mysql -u root -prootpassword flyinghotel -e "
SELECT * FROM breaker_control_queue
WHERE status = 'PENDING'
ORDER BY scheduled_at DESC;
"

# 2. ตรวจสอบ celery logs
docker-compose logs celery-worker | grep "process_control_queue"

# 3. ตรวจสอบว่า room status change trigger auto control
docker-compose logs backend | grep "auto_control_on_room_status_change"

# 4. Manual trigger queue processing
docker-compose exec backend python -c "
from app.tasks.breaker_tasks import process_control_queue
process_control_queue.delay()
print('Queue processing triggered')
"
```

### ปัญหา 6: Frontend ไม่เชื่อมต่อ Backend

**อาการ:**
- API calls ล้มเหลว
- Network errors

**วิธีแก้:**
1. ตรวจสอบ frontend env:
```bash
cat frontend/.env
# VITE_API_BASE_URL=http://localhost:8000
```
2. ตรวจสอบ CORS:
```bash
docker-compose logs backend | grep CORS
```
3. ตรวจสอบ backend health:
```bash
curl http://localhost:8000/health
```

### ปัญหา 7: Database Migration Failed

**อาการ:**
- Migration error เมื่อ start backend
- Tables ไม่ถูกสร้าง

**วิธีแก้:**
```bash
# 1. ตรวจสอบ migration status
docker-compose exec backend alembic current

# 2. ถ้า migration pending, run manual
docker-compose exec backend alembic upgrade head

# 3. ถ้ามี error, ดู logs
docker-compose logs backend | grep alembic

# 4. Nuclear option: Reset database (ข้อมูลจะหาย!)
docker-compose down -v
docker-compose up -d
docker-compose exec backend alembic upgrade head
```

### ปัญหา 8: Token Expired

**อาการ:**
- "Token expired" error
- Auto logout

**วิธีแก้:**
1. Login ใหม่
2. Token มี expiry time (ดูที่ `app/core/security.py`)
3. ปรับ `ACCESS_TOKEN_EXPIRE_MINUTES` ใน `.env` ถ้าต้องการ

### ปัญหา 9: Enum Case Mismatch

**อาการ:**
- "LookupError: 'on' is not among the defined enum values"
- "ValueError: 'available' is not a valid RoomStatus"

**วิธีแก้:**
1. ตรวจสอบว่า enum values ใน database เป็น UPPERCASE:
```sql
SHOW COLUMNS FROM home_assistant_breakers LIKE 'current_state';
```
2. ตรวจสอบว่า Python models ใช้ UPPERCASE:
```python
# ใน models ต้องเป็น:
current_state = Column(Enum(BreakerState), default=BreakerState.OFF)

# NOT:
current_state = Column(Enum('on', 'off'), ...)
```
3. ตรวจสอบว่า API requests ส่ง UPPERCASE:
```json
{
  "status": "OCCUPIED",  // ✅ ถูกต้อง
  "status": "occupied"   // ❌ ผิด
}
```

### ปัญหา 10: High Response Time

**อาการ:**
- Breaker control ช้า
- Avg response time > 2000ms

**สาเหตุที่เป็นไปได้:**
1. Home Assistant ตอบสนองช้า
2. Network latency สูง
3. Too many breakers

**วิธีแก้:**
1. ตรวจสอบ HA performance
2. ตรวจสอบ network ping:
```bash
docker-compose exec backend ping 192.168.1.100
```
3. ปรับ timeout settings ใน `home_assistant_service.py`:
```python
timeout = aiohttp.ClientTimeout(total=5)  # เพิ่มเป็น 10
```
4. ลด polling frequency (ปรับ celery beat schedule)

---

## สรุปการทดสอบ

### Checklist การทดสอบทั้งหมด

**Phase 1: Database**
- [ ] Tables สร้างสำเร็จ
- [ ] Indexes ครบถ้วน
- [ ] Foreign keys ถูกต้อง
- [ ] Enum values เป็น UPPERCASE

**Phase 2: Services**
- [ ] Encryption key ถูกสร้าง
- [ ] Encryption/Decryption ทำงานได้
- [ ] Celery tasks ถูก register
- [ ] Beat schedule ถูกต้อง
- [ ] Helper functions ทำงานถูกต้อง

**Phase 3: API**
- [ ] Home Assistant config endpoints ทำงาน
- [ ] Breaker CRUD endpoints ทำงาน
- [ ] Manual control (turn on/off) ทำงานกับ HA จริง
- [ ] Sync status ดึงข้อมูลถูกต้อง
- [ ] Activity logs ถูกบันทึก
- [ ] Statistics คำนวณถูกต้อง
- [ ] Auto control trigger เมื่อเปลี่ยนสถานะห้อง

**Phase 4: Frontend**
- [ ] Settings page ทำงานครบทุกฟังก์ชัน
- [ ] Breakers page แสดงข้อมูลถูกต้อง
- [ ] Manual control สั่งงานได้
- [ ] Activity logs แสดงครบถ้วน
- [ ] Filters ทำงานถูกต้อง
- [ ] Responsive design ใช้งานได้ทุก device
- [ ] Error handling ครอบคลุม

**End-to-End**
- [ ] เช็คอิน → Breaker เปิดอัตโนมัติ
- [ ] เช็คเอาท์ → Breaker ปิดอัตโนมัติ
- [ ] Manual control override auto control
- [ ] Multiple breakers ทำงานพร้อมกัน
- [ ] Error handling เมื่อ HA offline
- [ ] Activity logs บันทึกครบถ้วน

---

## บันทึกการทดสอบ (Test Log Template)

```
วันที่ทดสอบ: _____________
ผู้ทดสอบ: _____________
เวอร์ชัน: _____________

Phase 1: Database
- Tables: ✅ / ❌
- Indexes: ✅ / ❌
- Foreign Keys: ✅ / ❌
- Enum Values: ✅ / ❌
หมายเหตุ: _______________________

Phase 2: Services
- Encryption: ✅ / ❌
- Celery Tasks: ✅ / ❌
- Beat Schedule: ✅ / ❌
- Helper Functions: ✅ / ❌
หมายเหตุ: _______________________

Phase 3: API
- HA Config API: ✅ / ❌
- Breaker CRUD: ✅ / ❌
- Manual Control: ✅ / ❌
- Auto Control: ✅ / ❌
- Activity Logs: ✅ / ❌
- Statistics: ✅ / ❌
หมายเหตุ: _______________________

Phase 4: Frontend
- Settings Page: ✅ / ❌
- Breakers Page: ✅ / ❌
- Manual Control UI: ✅ / ❌
- Activity Logs UI: ✅ / ❌
- Filters: ✅ / ❌
- Responsive: ✅ / ❌
หมายเหตุ: _______________________

End-to-End
- Scenario 1 (Check-in): ✅ / ❌
- Scenario 2 (Check-out): ✅ / ❌
- Scenario 3 (Manual Override): ✅ / ❌
- Scenario 4 (HA Offline): ✅ / ❌
- Scenario 5 (Multiple Rooms): ✅ / ❌
หมายเหตุ: _______________________

ปัญหาที่พบ:
1. _______________________
2. _______________________
3. _______________________

ข้อเสนอแนะ:
_______________________
_______________________
```

---

**สร้างโดย**: Claude Code
**วันที่**: 2025-01-11
**Version**: 1.0
