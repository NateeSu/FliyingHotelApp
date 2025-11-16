# Home Assistant Smart Breaker Integration Plan
# แผนการพัฒนาระบบควบคุม Smart Breaker ผ่าน Home Assistant (Local)

**Created:** November 4, 2025
**Status:** Planning Phase
**Target Phase:** Phase 10 - IoT Integration
**Integration Method:** Home Assistant REST API (Local Network)

---

## Table of Contents

1. [ภาพรวมของระบบ](#ภาพรวมของระบบ)
2. [Business Requirements](#business-requirements)
3. [Technical Architecture](#technical-architecture)
4. [Database Design](#database-design)
5. [API Endpoints Design](#api-endpoints-design)
6. [Frontend UI Design](#frontend-ui-design)
7. [Automation Logic](#automation-logic)
8. [Home Assistant Integration](#home-assistant-integration)
9. [Security & Error Handling](#security--error-handling)
10. [Testing Strategy](#testing-strategy)
11. [Implementation Phases](#implementation-phases)
12. [Risks & Mitigation](#risks--mitigation)

---

## ภาพรวมของระบบ

### วัตถุประสงค์
พัฒนาระบบควบคุม Smart Breaker (เบรกเกอร์อัจฉริยะ) ผ่าน **Home Assistant** ที่ตั้งไว้ใน Local Network เพื่อ:
- **เปิดไฟฟ้าอัตโนมัติ** เมื่อห้องมีสถานะ "มีผู้พัก" (OCCUPIED) หรือ "กำลังทำความสะอาด" (CLEANING)
- **ปิดไฟฟ้าอัตโนมัติ** เมื่อห้องมีสถานะ "ว่าง" (AVAILABLE)
- **จัดการ Breaker ผ่านหน้า Web Interface** สำหรับแต่ละห้อง
- **บันทึกประวัติ** การเปิด-ปิด breaker เพื่อการตรวจสอบและประหยัดพลังงาน

### ข้อดีของการใช้ Home Assistant (Local)
1. **ไม่ต้องพึ่ง Cloud** - ทำงานใน Local Network เท่านั้น
2. **เร็วกว่า** - ไม่มี latency จาก internet
3. **ปลอดภัยกว่า** - ข้อมูลไม่ออกจาก network
4. **ไม่มีค่าใช้จ่าย** - ไม่ต้องจ่าย API subscription
5. **Reliable** - ไม่ขึ้นกับ internet connection
6. **ควบคุมได้เต็มที่** - จัดการ Home Assistant เอง

### ประโยชน์ที่ได้รับ
1. **ประหยัดพลังงาน** - ปิดไฟฟ้าห้องว่างอัตโนมัติ
2. **ความปลอดภัย** - ควบคุมไฟฟ้าจากระยะไกล
3. **สะดวกสบาย** - ไม่ต้องเดินไปเปิด-ปิดที่ห้อง
4. **รายงานการใช้ไฟ** - ติดตามข้อมูลการใช้งาน
5. **อัตโนมัติ** - ลดภาระงานของพนักงาน

---

## Business Requirements

### FR1: Auto Control Based on Room Status
**เปิด-ปิดอัตโนมัติตามสถานะห้อง**

| สถานะห้อง | การกระทำ Breaker | เหตุผล |
|-----------|------------------|--------|
| **AVAILABLE** (ว่าง) | 🔴 ปิด (OFF) | ประหยัดพลังงาน |
| **OCCUPIED** (มีผู้พัก) | 🟢 เปิด (ON) | ให้บริการแขก |
| **CLEANING** (ทำความสะอาด) | 🟢 เปิด (ON) | สำหรับพนักงาน |
| **RESERVED** (จอง) | 🔴 ปิด (OFF) | ยังไม่มีผู้เข้าพัก |
| **OUT_OF_SERVICE** (ซ่อม) | 🔴 ปิด (OFF) | ปิดซ่อมแซม |

**Business Rules:**
- ต้องมี delay 3 วินาที ก่อนส่งคำสั่งไปยัง Home Assistant (ป้องกันการสั่งงานซ้ำ)
- หากส่งคำสั่งไม่สำเร็จ ให้ retry 3 ครั้ง
- บันทึก log ทุกครั้งที่มีการเปิด-ปิด breaker
- แจ้งเตือน admin หาก breaker ตอบสนองผิดพลาด 3 ครั้งติด

---

### FR2: Manual Control from Web Interface
**ควบคุมด้วยตนเองผ่านหน้า Web**

**หน้าจัดการ Breaker (`/breakers`)**
- แสดงรายการ breaker ทั้งหมดพร้อมสถานะ (ON/OFF)
- แสดงห้องที่เชื่อมกับ breaker แต่ละตัว
- ปุ่มเปิด-ปิด breaker แบบ manual override
- แสดงสถานะการเชื่อมต่อกับ Home Assistant (Online/Offline)
- แสดงเวลาล่าสุดที่มีการเปิด-ปิด
- ปุ่ม Sync เพื่ออัปเดตสถานะจาก Home Assistant

**Permissions:**
- ADMIN: ดูและควบคุมได้ทั้งหมด
- RECEPTION: ดูและควบคุมได้ทั้งหมด
- HOUSEKEEPING: ดูได้อย่างเดียว (read-only)
- MAINTENANCE: ดูได้อย่างเดียว (read-only)

---

### FR3: Breaker Configuration
**ตั้งค่า Breaker แต่ละห้อง**

**หน้า Room Settings (`/rooms/:id/edit`)**
- เพิ่มส่วน "Smart Breaker Configuration"
- เลือก Home Assistant Entity ID ที่จะเชื่อมกับห้อง (เช่น `switch.room_101_breaker`)
- ตั้งค่า Auto Control (เปิด/ปิดใช้งาน)
- ทดสอบการทำงาน (Test Connection)

---

### FR4: Activity Logs & Reports
**บันทึกและรายงานการใช้งาน**

**Breaker Activity Log:**
- เวลาที่เปิด-ปิด
- ผู้ที่ทำการเปิด-ปิด (system/user)
- สถานะห้องในขณะนั้น
- สาเหตุ (auto/manual)
- ผลลัพธ์ (success/failed)

**Reports:**
- รายงานการประหยัดพลังงาน (คำนวณจากเวลาปิด)
- รายงานการใช้งาน breaker แต่ละห้อง
- รายงานข้อผิดพลาดของ breaker

---

## Technical Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                     Frontend (Vue 3)                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │  Breakers   │  │  Dashboard  │  │  Room Settings          │ │
│  │  Page       │  │  (Status)   │  │  (Configuration)        │ │
│  └──────┬──────┘  └──────┬──────┘  └───────────┬─────────────┘ │
└─────────┼────────────────┼─────────────────────┼───────────────┘
          │                │                     │
          │          WebSocket (Real-time)       │
          │                │                     │
┌─────────▼────────────────▼─────────────────────▼───────────────┐
│                  Backend (FastAPI)                              │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────────┐  │
│  │  Breaker     │  │  Room        │  │  Breaker Activity   │  │
│  │  API         │  │  Service     │  │  Log Service        │  │
│  └──────┬───────┘  └──────┬───────┘  └─────────────────────┘  │
│         │                 │                                     │
│  ┌──────▼─────────────────▼────────────────────────────────┐   │
│  │    Home Assistant Integration Service                   │   │
│  │  - REST API Client (Local)                              │   │
│  │  - Status Polling (every 30s)                           │   │
│  │  - Error Handling & Retry                               │   │
│  └──────┬──────────────────────────────────────────────────┘   │
└─────────┼──────────────────────────────────────────────────────┘
          │ HTTP REST API (Local Network)
          │ http://homeassistant.local:8123/api
          │
┌─────────▼─────────────────────────────────────────────────────┐
│              Home Assistant (Local Server)                     │
│  ┌───────────────────────────────────────────────────────┐    │
│  │  Tuya Local Integration                               │    │
│  │  - switch.room_101_breaker                            │    │
│  │  - switch.room_102_breaker                            │    │
│  │  - ... (all room breakers)                            │    │
│  └───────────────────────────────────────────────────────┘    │
└────────────┬──────────────────────────────────────────────────┘
             │ Local WiFi
             │
┌────────────▼──────────────────────────────────────────────────┐
│                Smart Breakers (Physical Devices)               │
│  - Room 101 Breaker (Tuya Device)                             │
│  - Room 102 Breaker (Tuya Device)                             │
│  - ... (all physical breakers)                                │
└────────────────────────────────────────────────────────────────┘
```

### Technology Stack

**Backend:**
- FastAPI for API endpoints
- `aiohttp` or `httpx` for HTTP client (async)
- Celery for scheduled status polling
- Redis for caching device status

**Frontend:**
- Vue 3 with Composition API
- New `/breakers` route
- Real-time status via WebSocket
- Toast notifications for actions

**Home Assistant:**
- Running on local server (Raspberry Pi / VM / Docker)
- Tuya Local integration installed
- Long-Lived Access Token for authentication
- REST API enabled

**Database:**
- New tables: `home_assistant_breakers`, `breaker_activity_logs`
- Update `rooms` table with breaker reference

---

## Database Design

### 1. New Table: `home_assistant_breakers`
Store Home Assistant entity information

```sql
CREATE TABLE home_assistant_breakers (
    id INT AUTO_INCREMENT PRIMARY KEY,

    -- Home Assistant Entity Information
    entity_id VARCHAR(255) NOT NULL UNIQUE COMMENT 'Home Assistant Entity ID เช่น "switch.room_101_breaker"',
    friendly_name VARCHAR(255) NOT NULL COMMENT 'ชื่อที่แสดง เช่น "เบรกเกอร์ห้อง 101"',

    -- Room Association
    room_id INT UNIQUE COMMENT 'ห้องที่เชื่อมกับ breaker นี้',

    -- Configuration
    auto_control_enabled BOOLEAN DEFAULT TRUE COMMENT 'เปิดใช้งานควบคุมอัตโนมัติ',

    -- Status Information
    is_available BOOLEAN DEFAULT FALSE COMMENT 'สถานะ entity ใน Home Assistant (available/unavailable)',
    current_state ENUM('on', 'off', 'unavailable') DEFAULT 'unavailable' COMMENT 'สถานะปัจจุบัน',
    last_state_update DATETIME COMMENT 'เวลาที่อัปเดตสถานะล่าสุด',
    last_control_at DATETIME COMMENT 'เวลาที่ส่งคำสั่งล่าสุด',

    -- Home Assistant Metadata
    ha_attributes JSON COMMENT 'Attributes จาก Home Assistant (JSON)',
    last_changed DATETIME COMMENT 'last_changed จาก Home Assistant',
    last_updated DATETIME COMMENT 'last_updated จาก Home Assistant',

    -- Error Tracking
    consecutive_errors INT DEFAULT 0 COMMENT 'จำนวนครั้งที่เกิด error ติดกัน',
    last_error_message TEXT COMMENT 'ข้อความ error ล่าสุด',
    last_error_at DATETIME COMMENT 'เวลาที่เกิด error ล่าสุด',

    -- Metadata
    is_active BOOLEAN DEFAULT TRUE COMMENT 'เปิดใช้งานหรือไม่',
    notes TEXT COMMENT 'หมายเหตุ',

    -- Timestamps
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    -- Foreign Keys
    FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE SET NULL,

    -- Indexes
    INDEX idx_entity_id (entity_id),
    INDEX idx_room_id (room_id),
    INDEX idx_is_active (is_active),
    INDEX idx_current_state (current_state)
);
```

### 2. New Table: `breaker_activity_logs`
Log all breaker actions

```sql
CREATE TABLE breaker_activity_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,

    -- Breaker & Room
    breaker_id INT NOT NULL COMMENT 'ID ของ breaker',
    room_id INT COMMENT 'ID ของห้อง',

    -- Action Details
    action ENUM('TURN_ON', 'TURN_OFF', 'STATUS_SYNC') NOT NULL COMMENT 'การกระทำ',
    trigger_type ENUM('AUTO', 'MANUAL', 'SYSTEM') NOT NULL COMMENT 'ประเภทการสั่งงาน',
    triggered_by INT COMMENT 'User ID ที่ทำการสั่งงาน (ถ้าเป็น manual)',

    -- Room Status Context
    room_status_before VARCHAR(50) COMMENT 'สถานะห้องก่อนหน้า',
    room_status_after VARCHAR(50) COMMENT 'สถานะห้องหลัง',

    -- Result
    status ENUM('SUCCESS', 'FAILED', 'TIMEOUT') NOT NULL COMMENT 'ผลลัพธ์',
    error_message TEXT COMMENT 'ข้อความ error (ถ้ามี)',
    response_time_ms INT COMMENT 'เวลาที่ Home Assistant ตอบกลับ (มิลลิวินาที)',

    -- Timestamps
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    -- Foreign Keys
    FOREIGN KEY (breaker_id) REFERENCES home_assistant_breakers(id) ON DELETE CASCADE,
    FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE SET NULL,
    FOREIGN KEY (triggered_by) REFERENCES users(id) ON DELETE SET NULL,

    -- Indexes
    INDEX idx_breaker_id (breaker_id),
    INDEX idx_room_id (room_id),
    INDEX idx_created_at (created_at),
    INDEX idx_action (action),
    INDEX idx_trigger_type (trigger_type)
);
```

### 3. Update Table: `rooms`
Add breaker reference

```sql
ALTER TABLE rooms
ADD COLUMN breaker_id INT DEFAULT NULL COMMENT 'Home Assistant Breaker ที่เชื่อมกับห้องนี้',
ADD FOREIGN KEY (breaker_id) REFERENCES home_assistant_breakers(id) ON DELETE SET NULL;

CREATE INDEX idx_breaker_id ON rooms(breaker_id);
```

### 4. New Table: `home_assistant_config`
Store Home Assistant connection settings

```sql
CREATE TABLE home_assistant_config (
    id INT AUTO_INCREMENT PRIMARY KEY,

    -- Connection Settings
    base_url VARCHAR(255) NOT NULL COMMENT 'Home Assistant URL เช่น http://homeassistant.local:8123',
    access_token TEXT NOT NULL COMMENT 'Long-Lived Access Token (encrypted)',

    -- Connection Status
    is_online BOOLEAN DEFAULT FALSE COMMENT 'สถานะการเชื่อมต่อ',
    last_ping_at DATETIME COMMENT 'เวลาที่ ping ล่าสุด',

    -- Configuration
    is_active BOOLEAN DEFAULT TRUE COMMENT 'ใช้งาน config นี้หรือไม่',

    -- Timestamps
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

---

## API Endpoints Design

### Breaker Management Endpoints

#### 1. GET `/api/v1/breakers/`
**List all breakers**

**Response:**
```json
{
  "data": [
    {
      "id": 1,
      "entity_id": "switch.room_101_breaker",
      "friendly_name": "เบรกเกอร์ห้อง 101",
      "room_id": 1,
      "room_number": "101",
      "auto_control_enabled": true,
      "is_available": true,
      "current_state": "on",
      "last_state_update": "2025-11-04T10:30:00",
      "last_control_at": "2025-11-04T08:15:00",
      "consecutive_errors": 0,
      "is_active": true
    }
  ],
  "total": 1
}
```

---

#### 2. GET `/api/v1/breakers/{breaker_id}`
**Get single breaker details**

**Response:**
```json
{
  "id": 1,
  "entity_id": "switch.room_101_breaker",
  "friendly_name": "เบรกเกอร์ห้อง 101",
  "room_id": 1,
  "room_number": "101",
  "room_status": "OCCUPIED",
  "auto_control_enabled": true,
  "is_available": true,
  "current_state": "on",
  "last_state_update": "2025-11-04T10:30:00",
  "last_control_at": "2025-11-04T08:15:00",
  "ha_attributes": {
    "friendly_name": "เบรกเกอร์ห้อง 101",
    "device_class": "switch"
  },
  "last_changed": "2025-11-04T08:15:00",
  "last_updated": "2025-11-04T10:30:00",
  "consecutive_errors": 0,
  "last_error_message": null,
  "is_active": true,
  "notes": null
}
```

---

#### 3. POST `/api/v1/breakers/`
**Create new breaker**

**Request:**
```json
{
  "entity_id": "switch.room_101_breaker",
  "friendly_name": "เบรกเกอร์ห้อง 101",
  "room_id": 1,
  "auto_control_enabled": true,
  "notes": "ติดตั้งเมื่อ 2025-11-01"
}
```

**Response:**
```json
{
  "id": 1,
  "entity_id": "switch.room_101_breaker",
  "friendly_name": "เบรกเกอร์ห้อง 101",
  "message": "สร้าง breaker สำเร็จ"
}
```

---

#### 4. PUT `/api/v1/breakers/{breaker_id}`
**Update breaker configuration**

**Request:**
```json
{
  "friendly_name": "เบรกเกอร์ห้อง 101 (ชั้น 1)",
  "room_id": 1,
  "auto_control_enabled": false,
  "notes": "ปิดการควบคุมอัตโนมัติชั่วคราว"
}
```

---

#### 5. DELETE `/api/v1/breakers/{breaker_id}`
**Delete breaker**

---

### Breaker Control Endpoints

#### 6. POST `/api/v1/breakers/{breaker_id}/turn-on`
**Turn on breaker (manual)**

**Response:**
```json
{
  "message": "เปิด breaker สำเร็จ",
  "breaker_id": 1,
  "entity_id": "switch.room_101_breaker",
  "current_state": "on",
  "response_time_ms": 120
}
```

---

#### 7. POST `/api/v1/breakers/{breaker_id}/turn-off`
**Turn off breaker (manual)**

---

#### 8. POST `/api/v1/breakers/{breaker_id}/sync-status`
**Sync status from Home Assistant**

**Response:**
```json
{
  "message": "อัปเดตสถานะสำเร็จ",
  "breaker_id": 1,
  "entity_id": "switch.room_101_breaker",
  "is_available": true,
  "current_state": "on",
  "last_state_update": "2025-11-04T10:35:00"
}
```

---

#### 9. POST `/api/v1/breakers/sync-all`
**Sync status for all breakers**

---

### Activity Log Endpoints

#### 10. GET `/api/v1/breakers/{breaker_id}/logs`
**Get breaker activity logs**

**Query Params:**
- `start_date` (optional)
- `end_date` (optional)
- `action` (optional): TURN_ON, TURN_OFF, STATUS_SYNC
- `trigger_type` (optional): AUTO, MANUAL, SYSTEM
- `limit` (default: 50)
- `offset` (default: 0)

---

#### 11. GET `/api/v1/breakers/logs`
**Get all breaker activity logs**

---

### Statistics & Reports

#### 12. GET `/api/v1/breakers/stats`
**Get breaker statistics**

**Response:**
```json
{
  "total_breakers": 10,
  "available_breakers": 9,
  "unavailable_breakers": 1,
  "breakers_on": 5,
  "breakers_off": 4,
  "auto_control_enabled": 8,
  "recent_errors": 2,
  "last_sync": "2025-11-04T10:30:00",
  "home_assistant_online": true
}
```

---

#### 13. GET `/api/v1/breakers/{breaker_id}/energy-report`
**Energy saving report**

---

### Home Assistant Configuration Endpoints

#### 14. GET `/api/v1/home-assistant/config`
**Get current Home Assistant configuration**

**Permissions:** ADMIN only

**Response:**
```json
{
  "id": 1,
  "base_url": "http://192.168.1.100:8123",
  "access_token": "eyJ0eXA...IiwibmJm..." (masked: "eyJ...f**"),
  "is_online": true,
  "last_ping_at": "2025-11-04T10:35:00",
  "is_active": true,
  "created_at": "2025-11-01T00:00:00",
  "updated_at": "2025-11-04T10:35:00"
}
```

**Note:** access_token จะถูก mask แสดงเฉพาะบางส่วน

---

#### 15. POST `/api/v1/home-assistant/config`
**Create or update Home Assistant configuration**

**Permissions:** ADMIN only

**Request:**
```json
{
  "base_url": "http://192.168.1.100:8123",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Validation:**
- `base_url` ต้องเป็น valid URL (http:// หรือ https://)
- `access_token` ต้องไม่ว่าง และมีความยาวอย่างน้อย 50 ตัวอักษร
- จะทำการ test connection อัตโนมัติก่อน save

**Response (Success):**
```json
{
  "success": true,
  "message": "บันทึกการตั้งค่า Home Assistant สำเร็จ",
  "config": {
    "id": 1,
    "base_url": "http://192.168.1.100:8123",
    "is_online": true,
    "version": "2024.11.0"
  }
}
```

**Response (Error - Connection Failed):**
```json
{
  "success": false,
  "error": "CONNECTION_FAILED",
  "message": "ไม่สามารถเชื่อมต่อ Home Assistant ได้",
  "details": "Connection timeout after 5 seconds"
}
```

**Response (Error - Invalid Token):**
```json
{
  "success": false,
  "error": "INVALID_TOKEN",
  "message": "Access Token ไม่ถูกต้อง",
  "details": "401 Unauthorized"
}
```

---

#### 16. PUT `/api/v1/home-assistant/config`
**Update existing Home Assistant configuration**

**Permissions:** ADMIN only

**Request:**
```json
{
  "base_url": "http://192.168.1.200:8123",
  "access_token": "new_token_here..."
}
```

**Note:** สามารถอัพเดตเฉพาะ field ที่ต้องการเปลี่ยน (partial update)

---

#### 17. DELETE `/api/v1/home-assistant/config`
**Delete Home Assistant configuration**

**Permissions:** ADMIN only

**Response:**
```json
{
  "success": true,
  "message": "ลบการตั้งค่า Home Assistant สำเร็จ"
}
```

**Warning:** การลบจะทำให้ระบบ breaker automation หยุดทำงาน

---

#### 18. POST `/api/v1/home-assistant/test-connection`
**Test Home Assistant connection**

**Permissions:** ADMIN only

**Request:**
```json
{
  "base_url": "http://192.168.1.100:8123",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Note:** สามารถทดสอบโดยไม่ต้อง save ก่อน

**Response (Success):**
```json
{
  "success": true,
  "message": "เชื่อมต่อ Home Assistant สำเร็จ",
  "connection_info": {
    "version": "2024.11.0",
    "entity_count": 150,
    "response_time_ms": 45,
    "base_url": "http://192.168.1.100:8123"
  }
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "CONNECTION_TIMEOUT",
  "message": "การเชื่อมต่อใช้เวลานานเกินไป",
  "details": "Timeout after 5 seconds"
}
```

---

#### 19. GET `/api/v1/home-assistant/status`
**Check current Home Assistant connection status**

**Permissions:** All authenticated users

**Response:**
```json
{
  "is_configured": true,
  "is_online": true,
  "base_url": "http://192.168.1.100:8123",
  "version": "2024.11.0",
  "last_ping_at": "2025-11-04T10:35:00",
  "response_time_ms": 45,
  "total_breakers": 10,
  "available_breakers": 9
}
```

**Response (Not Configured):**
```json
{
  "is_configured": false,
  "is_online": false,
  "message": "Home Assistant ยังไม่ได้ตั้งค่า"
}
```

---

#### 20. GET `/api/v1/home-assistant/entities`
**Get all entities from Home Assistant**

**Permissions:** ADMIN only

**Query Params:**
- `domain` (optional): filter by domain (e.g., "switch", "light", "sensor")
- `search` (optional): search in entity_id or friendly_name

**Response:**
```json
{
  "entities": [
    {
      "entity_id": "switch.room_101_breaker",
      "friendly_name": "เบรกเกอร์ห้อง 101",
      "state": "on",
      "domain": "switch",
      "attributes": {
        "device_class": "switch"
      },
      "last_changed": "2025-11-04T08:15:00",
      "last_updated": "2025-11-04T10:30:00"
    },
    {
      "entity_id": "switch.room_102_breaker",
      "friendly_name": "เบรกเกอร์ห้อง 102",
      "state": "off",
      "domain": "switch",
      "attributes": {
        "device_class": "switch"
      },
      "last_changed": "2025-11-03T22:00:00",
      "last_updated": "2025-11-04T10:30:00"
    }
  ],
  "total": 2
}
```

**Use Case:** ใช้สำหรับ dropdown เลือก entity เมื่อสร้าง breaker ใหม่

---

## Frontend UI Design

### 1. New Page: Breakers Management (`/breakers`)

**Layout:**
```
┌────────────────────────────────────────────────────────────────┐
│  Breakers Management - จัดการเบรกเกอร์อัจฉริยะ                  │
│  🟢 Home Assistant: Connected                                  │
├────────────────────────────────────────────────────────────────┤
│  [+ เพิ่ม Breaker]  [🔄 Sync ทั้งหมด]         🔍 [Search]     │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  เบรกเกอร์ห้อง 101                        🟢 Available    │ │
│  │  Entity: switch.room_101_breaker          ⚡ ON           │ │
│  │  Auto Control: ✅ เปิดใช้งาน                              │ │
│  │  Last Update: 10:30:00 (4 Nov 2025)                      │ │
│  │                                                            │ │
│  │  [🔴 ปิด] [⚙️ ตั้งค่า] [📊 ประวัติ]                       │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  เบรกเกอร์ห้อง 102                        🔴 Unavailable  │ │
│  │  Entity: switch.room_102_breaker          ⚫ unavailable  │ │
│  │  Auto Control: ❌ ปิดใช้งาน                               │ │
│  │  Last Update: 08:15:00 (4 Nov 2025)                      │ │
│  │  ⚠️ Error: Entity not found in Home Assistant            │ │
│  │                                                            │ │
│  │  [🔄 Sync] [⚙️ ตั้งค่า] [📊 ประวัติ]                       │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

**Features:**
- Home Assistant connection status indicator
- Card-based layout แสดง breaker แต่ละตัว
- Status indicator: 🟢 Available / 🔴 Unavailable
- Power status: ⚡ on / ⚫ off / ⚠️ unavailable
- Quick action buttons
- Real-time update via WebSocket
- Search/filter

---

### 2. Breaker Card Component

**Component:** `BreakerCard.vue`

**Props:**
```typescript
interface BreakerCardProps {
  breaker: {
    id: number
    entity_id: string
    friendly_name: string
    room_number: string | null
    auto_control_enabled: boolean
    is_available: boolean
    current_state: 'on' | 'off' | 'unavailable'
    last_state_update: string
    consecutive_errors: number
    last_error_message: string | null
  }
}
```

**Color Coding:**
- Available + on: 🟢 Green border
- Available + off: 🟡 Yellow border
- Unavailable: 🔴 Red border
- Error (>3): ⚠️ Orange border with warning icon

---

### 3. Breaker Configuration Modal

**Component:** `BreakerConfigModal.vue`

**Form Fields:**
- ชื่อที่แสดง (Friendly Name)
- Home Assistant Entity ID (เช่น `switch.room_101_breaker`)
- ห้องที่เชื่อม (Room Selection dropdown)
- เปิดใช้งานควบคุมอัตโนมัติ (Auto Control toggle)
- หมายเหตุ (Notes textarea)
- [ทดสอบการเชื่อมต่อ] button

---

### 4. Home Assistant Settings Page

**New Page:** `/settings/home-assistant`

**Access:** ADMIN only (เฉพาะผู้ดูแลระบบเท่านั้น)

**Form Fields:**
```
┌────────────────────────────────────────────────────────────────┐
│  🏠 Home Assistant Configuration                               │
│  ตั้งค่าการเชื่อมต่อ Home Assistant Server                     │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Base URL: *                                                   │
│  [http://192.168.1.100:8123                                 ]  │
│  💡 ใส่ URL ของ Home Assistant Server                          │
│     ตัวอย่าง: http://192.168.1.100:8123                       │
│               http://homeassistant.local:8123                  │
│                                                                 │
│  Long-Lived Access Token: *                                    │
│  [••••••••••••••••••••••••••••••••••                        ]  │
│  [👁️ แสดง/ซ่อน]                                               │
│  💡 สร้าง Token ได้ที่: Profile → Long-Lived Access Tokens    │
│                                                                 │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                                 │
│  Connection Status: 🟢 Connected                               │
│  Last Check: 10:35:00 (4 Nov 2025)                            │
│  Home Assistant Version: 2024.11.0                             │
│  Total Entities: 150                                           │
│                                                                 │
│  [🔄 Test Connection]  [💾 Save Configuration]                 │
│                                                                 │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                                 │
│  📖 คำแนะนำการตั้งค่า:                                        │
│                                                                 │
│  1. ไปที่ Home Assistant (http://your-ha-server:8123)         │
│  2. คลิกที่ Profile (มุมล่างซ้าย)                             │
│  3. Scroll ลงไปหา "Long-Lived Access Tokens"                  │
│  4. คลิก "Create Token"                                        │
│  5. ตั้งชื่อ: "FlyingHotelApp" และคลิก OK                     │
│  6. Copy token ที่ได้และนำมาใส่ที่นี่                          │
│  7. คลิก "Test Connection" เพื่อทดสอบการเชื่อมต่อ              │
│  8. ถ้าเชื่อมต่อสำเร็จให้คลิก "Save Configuration"            │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

**Features:**
- Validation URL format (ต้องเป็น http:// หรือ https://)
- Test connection ก่อน save (required)
- แสดง/ซ่อน token (toggle visibility)
- แสดง Home Assistant version เมื่อเชื่อมต่อสำเร็จ
- บันทึกประวัติการเชื่อมต่อ
- Error handling with clear messages

---

### 5. Dashboard Integration

**Add Breaker Status Widget:**

```
┌────────────────────────────────────────┐
│  ⚡ Smart Breakers (HA)                │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                        │
│  🟢 Available: 9 / 10                 │
│  ⚡ เปิดอยู่:   5                      │
│  ⚫ ปิดอยู่:    4                      │
│  ⚠️ Error:     1                      │
│                                        │
│  Home Assistant: 🟢 Connected         │
│                                        │
│  [ดูรายละเอียด →]                     │
└────────────────────────────────────────┘
```

---

## Automation Logic

### Auto Control Flow

```
Room Status Change (Event)
    ↓
Check if room has breaker assigned
    ↓ Yes
Check if auto_control_enabled = true
    ↓ Yes
Determine target breaker state:
    - AVAILABLE → off
    - OCCUPIED → on
    - CLEANING → on
    - RESERVED → off
    - OUT_OF_SERVICE → off
    ↓
Check if current state != target state
    ↓ Different
Add 3-second delay (debounce)
    ↓
Send command to Home Assistant REST API
    ↓
Retry up to 3 times if failed
    ↓
Update breaker status in database
    ↓
Create activity log entry
    ↓
Broadcast WebSocket event
    ↓
If failed 3+ times consecutively:
    - Send notification to admin
```

### Implementation

**1. Room Status Change Hook**
```python
# backend/app/services/room_service.py

async def update_room_status(
    room_id: int,
    new_status: RoomStatus,
    db: AsyncSession
):
    # Update room status
    room = await db.get(Room, room_id)
    old_status = room.status
    room.status = new_status
    await db.commit()

    # Trigger breaker automation
    await breaker_automation_service.handle_room_status_change(
        room_id=room_id,
        old_status=old_status,
        new_status=new_status
    )
```

**2. Breaker Automation Service**
```python
# backend/app/services/breaker_automation_service.py

class BreakerAutomationService:
    async def handle_room_status_change(
        self,
        room_id: int,
        old_status: RoomStatus,
        new_status: RoomStatus
    ):
        # Get breaker for this room
        breaker = await self.get_breaker_by_room(room_id)

        if not breaker:
            return  # No breaker assigned

        if not breaker.auto_control_enabled:
            return  # Auto control disabled

        # Determine target state
        target_state = self.get_target_state(new_status)

        if breaker.current_state == target_state:
            return  # Already in correct state

        # Add delay to prevent rapid switching
        await asyncio.sleep(3)

        # Send command with retry
        success = await self.send_command_with_retry(
            breaker=breaker,
            command='turn_on' if target_state == 'on' else 'turn_off',
            trigger_type='AUTO',
            room_status_before=old_status,
            room_status_after=new_status
        )

        if not success:
            await self.handle_command_failure(breaker)

    def get_target_state(self, room_status: RoomStatus) -> str:
        """Determine target breaker state based on room status"""
        if room_status in [RoomStatus.OCCUPIED, RoomStatus.CLEANING]:
            return 'on'
        else:
            return 'off'
```

---

## Home Assistant Integration

### Home Assistant Setup

**1. Install Tuya Local Integration**
```yaml
# configuration.yaml

# Enable REST API
api:

# Configure Tuya Local devices
tuya:
  username: !secret tuya_username
  password: !secret tuya_password
  country_code: 66
  platform: smart_life
```

**2. Add Breaker Devices**
- ติดตั้ง Tuya Local integration ผ่าน UI
- เพิ่มอุปกรณ์ breaker ทั้งหมด
- ตั้งชื่อ entity ให้ชัดเจน เช่น `switch.room_101_breaker`

**3. Generate Long-Lived Access Token**
```
1. เข้า Home Assistant
2. คลิกที่ Profile (ล่างซ้าย)
3. Scroll ลงไปหา "Long-Lived Access Tokens"
4. คลิก "Create Token"
5. ตั้งชื่อ: "FlyingHotelApp"
6. Copy token และเก็บไว้
```

---

### Python Integration

**Library:** `aiohttp` (async HTTP client)

**Installation:**
```bash
pip install aiohttp
```

**Home Assistant Service:**
```python
# backend/app/services/home_assistant_service.py

import aiohttp
import asyncio
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.home_assistant_config import HomeAssistantConfig
from app.core.security import decrypt_value

class HomeAssistantService:
    def __init__(self, db: AsyncSession = None):
        """
        Initialize Home Assistant Service

        Note: URL และ Token จะถูกดึงจาก database แทนที่จะใช้ environment variables
        """
        self.db = db
        self.base_url = None
        self.access_token = None
        self.headers = None

    async def _load_config(self):
        """Load Home Assistant configuration from database"""
        if not self.db:
            raise ValueError("Database session is required")

        # Get active config from database
        result = await self.db.execute(
            select(HomeAssistantConfig).where(
                HomeAssistantConfig.is_active == True
            ).limit(1)
        )
        config = result.scalar_one_or_none()

        if not config:
            raise HomeAssistantNotConfiguredError("Home Assistant has not been configured")

        # Decrypt token
        self.access_token = decrypt_value(config.access_token)
        self.base_url = config.base_url

        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        return config

    async def test_connection_with_config(
        self,
        base_url: str,
        access_token: str
    ) -> Dict[str, Any]:
        """
        Test connection with provided credentials (without saving to database)

        Args:
            base_url: Home Assistant URL (e.g., http://192.168.1.100:8123)
            access_token: Long-Lived Access Token

        Returns:
            Dict with connection info if successful

        Raises:
            HomeAssistantConnectionError: If connection fails
            HomeAssistantAuthError: If authentication fails
        """
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        url = f"{base_url}/api/"

        try:
            async with aiohttp.ClientSession() as session:
                start_time = time.time()
                async with session.get(
                    url,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    response_time_ms = int((time.time() - start_time) * 1000)

                    if response.status == 401:
                        raise HomeAssistantAuthError("Invalid access token")

                    if response.status != 200:
                        raise HomeAssistantConnectionError(
                            f"Unexpected status code: {response.status}"
                        )

                    data = await response.json()

                    # Get version and entity count
                    version_url = f"{base_url}/api/config"
                    async with session.get(
                        version_url,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=5)
                    ) as version_response:
                        if version_response.status == 200:
                            version_data = await version_response.json()
                            version = version_data.get("version", "unknown")
                        else:
                            version = "unknown"

                    # Get entity count
                    states_url = f"{base_url}/api/states"
                    async with session.get(
                        states_url,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=5)
                    ) as states_response:
                        if states_response.status == 200:
                            states_data = await states_response.json()
                            entity_count = len(states_data)
                        else:
                            entity_count = 0

                    return {
                        "success": True,
                        "version": version,
                        "entity_count": entity_count,
                        "response_time_ms": response_time_ms,
                        "message": data.get("message", "Connection successful")
                    }

        except aiohttp.ClientConnectorError as e:
            raise HomeAssistantConnectionError(f"Cannot connect to {base_url}: {str(e)}")
        except asyncio.TimeoutError:
            raise HomeAssistantConnectionError(f"Connection timeout to {base_url}")
        except Exception as e:
            raise HomeAssistantConnectionError(f"Connection error: {str(e)}")

    async def get_entity_state(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get entity state from Home Assistant"""
        url = f"{self.base_url}/api/states/{entity_id}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, timeout=5) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"Error getting entity state: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error connecting to Home Assistant: {str(e)}")
            return None

    async def turn_on(self, entity_id: str) -> bool:
        """Turn on entity"""
        url = f"{self.base_url}/api/services/switch/turn_on"
        data = {"entity_id": entity_id}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    headers=self.headers,
                    json=data,
                    timeout=5
                ) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Error turning on entity: {str(e)}")
            return False

    async def turn_off(self, entity_id: str) -> bool:
        """Turn off entity"""
        url = f"{self.base_url}/api/services/switch/turn_off"
        data = {"entity_id": entity_id}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    headers=self.headers,
                    json=data,
                    timeout=5
                ) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Error turning off entity: {str(e)}")
            return False

    async def send_command(self, entity_id: str, command: str) -> bool:
        """Generic command sender"""
        if command == "turn_on":
            return await self.turn_on(entity_id)
        elif command == "turn_off":
            return await self.turn_off(entity_id)
        else:
            raise ValueError(f"Unknown command: {command}")

    async def test_connection(self) -> bool:
        """Test connection to Home Assistant"""
        url = f"{self.base_url}/api/"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"Connected to Home Assistant: {data.get('message')}")
                        return True
                    return False
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return False

    async def get_all_entities(self) -> list:
        """Get all entities from Home Assistant"""
        url = f"{self.base_url}/api/states"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, timeout=10) as response:
                    if response.status == 200:
                        return await response.json()
                    return []
        except Exception as e:
            logger.error(f"Error getting entities: {str(e)}")
            return []
```

---

### Status Polling (Celery Task)

**Scheduled Task:**
```python
# backend/app/tasks/breaker_tasks.py

from celery import shared_task

@shared_task
def poll_breaker_status():
    """Poll breaker status from Home Assistant every 30 seconds"""

    # Get all active breakers
    breakers = db.query(HomeAssistantBreaker).filter(
        HomeAssistantBreaker.is_active == True
    ).all()

    for breaker in breakers:
        try:
            # Get status from Home Assistant
            state = await ha_service.get_entity_state(breaker.entity_id)

            if state:
                # Update database
                breaker.is_available = state.get("state") != "unavailable"
                breaker.current_state = state.get("state")
                breaker.last_state_update = datetime.now()
                breaker.ha_attributes = state.get("attributes", {})
                breaker.last_changed = state.get("last_changed")
                breaker.last_updated = state.get("last_updated")
                breaker.consecutive_errors = 0
            else:
                breaker.is_available = False
                breaker.consecutive_errors += 1

        except Exception as e:
            logger.error(f"Error polling breaker {breaker.id}: {str(e)}")
            breaker.consecutive_errors += 1
            breaker.last_error_message = str(e)
            breaker.last_error_at = datetime.now()

        db.commit()

    # Broadcast updates via WebSocket
    await websocket_manager.broadcast({
        "event": "breakers_status_updated",
        "data": {"breakers": [b.to_dict() for b in breakers]}
    })
```

**Celery Beat Configuration:**
```python
# backend/app/core/celery_config.py

beat_schedule = {
    'poll-breaker-status': {
        'task': 'app.tasks.breaker_tasks.poll_breaker_status',
        'schedule': 30.0,  # Every 30 seconds
    },
}
```

---

## Security & Error Handling

### Security

**1. Access Token Protection:**
```python
# Store token encrypted in database
from cryptography.fernet import Fernet

class ConfigService:
    def encrypt_token(self, token: str) -> str:
        key = os.getenv("ENCRYPTION_KEY").encode()
        fernet = Fernet(key)
        return fernet.encrypt(token.encode()).decode()

    def decrypt_token(self, encrypted_token: str) -> str:
        key = os.getenv("ENCRYPTION_KEY").encode()
        fernet = Fernet(key)
        return fernet.decrypt(encrypted_token.encode()).decode()
```

**2. Local Network Only:**
- Home Assistant ควรอยู่ใน Local Network เท่านั้น
- ไม่เปิด port ออก internet
- ใช้ firewall กั้น external access

**3. Access Control:**
```python
@router.post("/breakers/{breaker_id}/turn-on")
async def turn_on_breaker(
    breaker_id: int,
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in [UserRole.ADMIN, UserRole.RECEPTION]:
        raise HTTPException(status_code=403, detail="ไม่มีสิทธิ์ควบคุม breaker")
```

---

### Error Handling

**1. Connection Errors:**
```python
class HomeAssistantError(Exception):
    """Base class for Home Assistant errors"""
    pass

class HomeAssistantConnectionError(HomeAssistantError):
    """Cannot connect to Home Assistant"""
    pass

class HomeAssistantAuthError(HomeAssistantError):
    """Authentication failed"""
    pass

class HomeAssistantEntityNotFoundError(HomeAssistantError):
    """Entity not found"""
    pass
```

**2. Retry Logic:**
```python
async def send_command_with_retry(
    self,
    breaker: HomeAssistantBreaker,
    command: str,
    max_retries: int = 3
) -> bool:
    """Send command with retry logic"""

    for attempt in range(max_retries):
        try:
            result = await ha_service.send_command(
                entity_id=breaker.entity_id,
                command=command
            )

            if result:
                breaker.consecutive_errors = 0
                return True

        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed: {str(e)}")

            if attempt < max_retries - 1:
                await asyncio.sleep(1)  # 1 second delay
            else:
                breaker.consecutive_errors += 1
                breaker.last_error_message = str(e)
                breaker.last_error_at = datetime.now()
                return False
```

---

## Testing Strategy

### Unit Tests

**1. Home Assistant Service Tests:**
```python
# tests/test_ha_service.py

async def test_turn_on_entity():
    """Test turning on entity"""
    ha_service = HomeAssistantService()
    result = await ha_service.turn_on("switch.room_101_breaker")
    assert result == True

async def test_get_entity_state():
    """Test getting entity state"""
    ha_service = HomeAssistantService()
    state = await ha_service.get_entity_state("switch.room_101_breaker")
    assert state.get("state") in ["on", "off", "unavailable"]

async def test_connection():
    """Test Home Assistant connection"""
    ha_service = HomeAssistantService()
    result = await ha_service.test_connection()
    assert result == True
```

---

### Integration Tests

**Test with real Home Assistant instance**

---

### Manual Testing Checklist

- [ ] ตั้งค่า Home Assistant URL และ Token
- [ ] Test Connection สำเร็จ
- [ ] สร้าง breaker และ link กับห้อง
- [ ] Test manual turn on/off
- [ ] Check-in ห้องและตรวจสอบ breaker เปิดอัตโนมัติ
- [ ] Check-out ห้องและตรวจสอบ breaker ปิดอัตโนมัติ
- [ ] Start housekeeping และตรวจสอบ breaker เปิด
- [ ] Complete housekeeping และตรวจสอบ breaker ปิด
- [ ] ปิด Home Assistant และตรวจสอบ error handling
- [ ] Test sync status button
- [ ] ตรวจสอบ activity logs
- [ ] Test บน mobile

---

## Implementation Phases

### Phase 1: Database & Models (1 day)
- สร้างตาราง database
- SQLAlchemy models
- Alembic migration
- Pydantic schemas

### Phase 2: Home Assistant Integration (1-2 days)
- Install aiohttp
- สร้าง HomeAssistantService
- Test connection
- Test entity control

### Phase 3: Backend API (2 days)
- CRUD endpoints
- Control endpoints
- Activity log endpoints
- Permissions

### Phase 4: Automation Logic (2 days)
- BreakerAutomationService
- Room status change hooks
- Retry logic
- Error notifications

### Phase 5: Frontend UI (3 days)
- Breakers page
- Components (BreakerCard, Modals)
- Dashboard widget
- Settings page

### Phase 6: Status Polling (1 day)
- Celery task
- WebSocket updates

### Phase 7: Testing (2 days)
- Unit tests
- Integration tests
- Manual testing
- Bug fixes

### Phase 8: Documentation (1 day)
- API docs
- User guide
- Deployment guide

**Total: 13-14 days (2 weeks)**

---

## Risks & Mitigation

### Risk 1: Home Assistant Offline
**Mitigation:**
- Detect offline และแสดง warning
- ให้ manual control ผ่าน physical switch
- Send notification

### Risk 2: Network Latency
**Mitigation:**
- Set timeout 5 วินาที
- Retry mechanism
- Show loading state

### Risk 3: Entity Not Found
**Mitigation:**
- Validate entity_id ก่อน save
- Test connection button
- Clear error messages

### Risk 4: Token Expiry
**Mitigation:**
- Long-Lived Token ไม่หมดอายุ
- แต่ควรมี mechanism สำหรับ refresh

---

## Environment Variables

```bash
# .env

# Encryption Key (for storing Home Assistant token in database)
# Generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
ENCRYPTION_KEY=your_32_character_encryption_key_here

# Note: Home Assistant URL และ Access Token จะถูกตั้งค่าผ่านหน้า Settings
#       และเก็บใน database (encrypted) แทนที่จะใช้ environment variables
```

**สร้าง Encryption Key:**
```python
from cryptography.fernet import Fernet
key = Fernet.generate_key()
print(key.decode())
# ผลลัพธ์: kQdVx2VZL8h_example_key_here_32_chars==
```

---

## Next Steps

### Before Development

1. **ตั้งค่า Home Assistant (ฝั่ง Engineer)**
   - [ ] ติดตั้ง Home Assistant บน server แยก
   - [ ] ติดตั้ง Tuya Local integration
   - [ ] เพิ่ม breaker devices ทั้งหมด
   - [ ] ตั้งชื่อ entity ให้ชัดเจน (เช่น `switch.room_101_breaker`)
   - [ ] สร้าง Long-Lived Access Token สำหรับ FlyingHotelApp
   - [ ] จดบันทึก:
     - Home Assistant URL (เช่น `http://192.168.1.100:8123`)
     - Access Token
     - รายการ entity_id ของ breaker ทั้งหมด

2. **Test Home Assistant API (Manual)**
   ```bash
   # 1. Test connection
   curl -H "Authorization: Bearer YOUR_TOKEN" \
        http://192.168.1.100:8123/api/

   # 2. Get all entities
   curl -H "Authorization: Bearer YOUR_TOKEN" \
        http://192.168.1.100:8123/api/states

   # 3. Get specific breaker state
   curl -H "Authorization: Bearer YOUR_TOKEN" \
        http://192.168.1.100:8123/api/states/switch.room_101_breaker

   # 4. Turn on breaker
   curl -X POST \
        -H "Authorization: Bearer YOUR_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{"entity_id":"switch.room_101_breaker"}' \
        http://192.168.1.100:8123/api/services/switch/turn_on

   # 5. Turn off breaker
   curl -X POST \
        -H "Authorization: Bearer YOUR_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{"entity_id":"switch.room_101_breaker"}' \
        http://192.168.1.100:8123/api/services/switch/turn_off
   ```

3. **Prepare Development Environment**
   - [ ] Generate ENCRYPTION_KEY:
     ```python
     from cryptography.fernet import Fernet
     print(Fernet.generate_key().decode())
     ```
   - [ ] เพิ่ม ENCRYPTION_KEY ใน `.env` file
   - [ ] Install dependencies:
     ```bash
     pip install aiohttp cryptography
     ```

4. **Review Plan**
   - [ ] Review กับทีม
   - [ ] Approve timeline (13-14 วัน)
   - [ ] Assign tasks

### Development Start

**Phase 1: Database & Models (1 day)**
1. สร้าง migration file:
   ```bash
   docker-compose exec backend alembic revision -m "add_home_assistant_breaker_tables"
   ```
2. สร้างตาราง:
   - `home_assistant_config`
   - `home_assistant_breakers`
   - `breaker_activity_logs`
   - อัพเดต `rooms` table
3. สร้าง SQLAlchemy models
4. สร้าง Pydantic schemas
5. Run migration:
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

**Phase 2: Home Assistant Integration (1-2 days)**
1. สร้าง `HomeAssistantService` class
2. Implement test connection method
3. Implement turn on/off methods
4. Implement get entity state method
5. Implement error handling
6. Test with real Home Assistant

**Phase 3: Backend API (2 days)**
1. สร้าง Home Assistant config endpoints (CRUD)
2. สร้าง breaker management endpoints
3. สร้าง breaker control endpoints
4. สร้าง activity log endpoints
5. Implement permissions (ADMIN only for config)

**Phase 4: Automation Logic (2 days)**
1. สร้าง `BreakerAutomationService`
2. Add hook to room status change
3. Implement retry logic
4. Add error notifications

**Phase 5: Frontend UI (3 days)**
1. สร้างหน้า `/settings/home-assistant`
2. สร้างหน้า `/breakers`
3. สร้าง components (BreakerCard, Modals)
4. Add dashboard widget
5. Integrate with room settings

**Phase 6: Status Polling (1 day)**
1. สร้าง Celery task
2. Configure Celery Beat
3. Implement WebSocket broadcast

**Phase 7: Testing (2 days)**
1. Unit tests
2. Integration tests
3. Manual testing
4. Bug fixes

**Phase 8: Documentation (1 day)**
1. API documentation
2. User guide (Thai)
3. Update CLOUD_DEPLOYMENT_GUIDE.md

---

**Document Version:** 2.1 (Home Assistant Local - Configurable)
**Created:** November 4, 2025
**Updated:** November 11, 2025
**Status:** Planning - Ready for Development
**Estimated Timeline:** 13-14 days
**Integration Method:** Home Assistant REST API (Local Network)

---

## Summary

### ✅ Key Features

1. **Flexible Configuration**
   - กำหนด Home Assistant URL ได้ (รองรับ server แยก)
   - กำหนด Access Token ผ่านหน้า Settings
   - ไม่ต้องแก้ environment variables หรือ restart service

2. **Security**
   - Token encrypted ใน database
   - เฉพาะ ADMIN จัดการ config ได้
   - Audit trail ทุกการเปลี่ยนแปลง

3. **User-Friendly**
   - Test connection ก่อน save
   - แสดง Home Assistant version
   - Error messages ชัดเจน
   - คำแนะนำการตั้งค่าครบถ้วน

4. **Automation**
   - เปิด-ปิดอัตโนมัติตามสถานะห้อง
   - Retry mechanism
   - Real-time WebSocket updates
   - Activity logging

### 📋 API Endpoints Summary

**Home Assistant Configuration (7 endpoints):**
- GET/POST/PUT/DELETE `/api/v1/home-assistant/config`
- POST `/api/v1/home-assistant/test-connection`
- GET `/api/v1/home-assistant/status`
- GET `/api/v1/home-assistant/entities`

**Breaker Management (13 endpoints):**
- CRUD operations (5)
- Control operations (4)
- Activity logs (2)
- Statistics (2)

**Total: 20 API endpoints**

### 🎨 Frontend Pages

1. **`/settings/home-assistant`** (NEW)
   - ADMIN only
   - กำหนด URL และ Token
   - Test connection
   - แสดงสถานะการเชื่อมต่อ

2. **`/breakers`** (NEW)
   - รายการ breaker ทั้งหมด
   - Manual control
   - Real-time status
   - Activity logs

3. **Dashboard widget** (UPDATE)
   - แสดงสถานะ breaker
   - แสดงสถานะ Home Assistant

4. **Room Settings** (UPDATE)
   - เพิ่ม breaker configuration

### 🔒 Security Features

- ✅ Token encryption (Fernet)
- ✅ RBAC permissions
- ✅ Audit trail
- ✅ Token masking in API responses
- ✅ Connection validation before save
- ✅ Local network only (no internet required)

### 🚀 Development Timeline

| Phase | Duration | Tasks |
|-------|----------|-------|
| 1. Database & Models | 1 day | Tables, models, schemas |
| 2. HA Integration | 1-2 days | Service class, API client |
| 3. Backend API | 2 days | Endpoints, permissions |
| 4. Automation | 2 days | Room hooks, retry logic |
| 5. Frontend UI | 3 days | Pages, components |
| 6. Status Polling | 1 day | Celery tasks |
| 7. Testing | 2 days | Unit, integration tests |
| 8. Documentation | 1 day | Docs, user guide |

**Total: 13-14 days**

### 💡 Key Improvements vs. Original Plan

| Feature | Original | Updated |
|---------|----------|---------|
| **Configuration** | Environment variables | Database + Settings UI |
| **Flexibility** | Fixed URL | Configurable URL |
| **Setup** | Restart required | No restart needed |
| **Multi-server** | ❌ | ✅ Support |
| **Test before save** | ❌ | ✅ Required |
| **Entity browser** | ❌ | ✅ Available |
| **Error handling** | Basic | Comprehensive |

### 📝 Prerequisites Checklist

**ฝั่ง Engineer (Home Assistant):**
- [ ] ติดตั้ง Home Assistant บน server แยก
- [ ] ติดตั้ง Tuya Local integration
- [ ] เพิ่ม breaker devices ทั้งหมด
- [ ] สร้าง Long-Lived Access Token
- [ ] จดบันทึก URL และ Token

**ฝั่ง Development:**
- [ ] Generate ENCRYPTION_KEY
- [ ] Install dependencies (aiohttp, cryptography)
- [ ] Review และ approve แผน
- [ ] เตรียม test environment

### 🎯 Success Criteria

1. ✅ สามารถตั้งค่า Home Assistant URL ผ่าน UI ได้
2. ✅ สามารถ test connection และ validate token ได้
3. ✅ สามารถควบคุม breaker เปิด-ปิดได้
4. ✅ ระบบ auto control ทำงานตามสถานะห้อง
5. ✅ บันทึก activity log ครบถ้วน
6. ✅ Real-time update ผ่าน WebSocket
7. ✅ Error handling และ retry ทำงานถูกต้อง
8. ✅ Token encrypted ใน database
9. ✅ ADMIN เท่านั้นที่แก้ไข config ได้
10. ✅ User guide และ documentation ครบถ้วน

---

**Ready for Development** 🚀

ระบบพร้อมสำหรับการพัฒนา เมื่อ Engineer ติดตั้ง Home Assistant และเตรียม Token เรียบร้อยแล้ว
