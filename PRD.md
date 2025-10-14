# Product Requirements Document (PRD)
# FlyingHotelApp - ระบบบริหารจัดการโรงแรมสำหรับโรงแรมขนาดเล็ก

## 📋 สารบัญ
1. [ภาพรวมโครงการ](#ภาพรวมโครงการ)
2. [เป้าหมายและวัตถุประสงค์](#เป้าหมายและวัตถุประสงค์)
3. [กลุ่มผู้ใช้งาน](#กลุ่มผู้ใช้งาน)
4. [สถาปัตยกรรมระบบ](#สถาปัตยกรรมระบบ)
5. [โครงสร้างฐานข้อมูล](#โครงสร้างฐานข้อมูล)
6. [รายละเอียดฟีเจอร์](#รายละเอียดฟีเจอร์)
7. [UI/UX Design Principles](#uiux-design-principles)
8. [แผนการพัฒนา (Development Phases)](#แผนการพัฒนา)
9. [Testing Strategy](#testing-strategy)
10. [Deployment Strategy](#deployment-strategy)

---

## ภาพรวมโครงการ

FlyingHotelApp เป็นระบบบริหารจัดการโรงแรมแบบครบวงจร (Property Management System - PMS) ที่ออกแบบมาเฉพาะสำหรับโรงแรมขนาดเล็ก (ไม่เกิน 50 ห้อง) โดยมีจุดเด่นพิเศษในการรองรับการพักแบบ **ชั่วคราว** (Short-time stay) นอกเหนือจากการพักค้างคืนแบบปกติ

### คุณสมบัติหลัก
- รองรับการพักแบบค้างคืนและการพักชั่วคราว (3 ชั่วโมง)
- UI/UX ที่ออกแบบให้ใช้งานง่าย เหมาะสำหรับผู้ใช้ทุกระดับการศึกษา
- แสดงผลแบบ Real-time ไม่ต้อง refresh
- รองรับการแสดงผลบนมือถือและแท็บเล็ตได้อย่างสมบูรณ์ (Responsive Design)
- แจ้งเตือนผ่าน Telegram ไปยังเจ้าหน้าที่ที่เกี่ยวข้อง
- ใช้งานเป็นภาษาไทยทั้งหมด

---

## เป้าหมายและวัตถุประสงค์

### เป้าหมายหลัก
1. **ความง่ายในการใช้งาน**: ผู้ใช้ระดับมัธยมต้นสามารถใช้งานได้ทันทีโดยไม่ต้องอ่านคู่มือ
2. **UI ที่สวยงามและทันสมัย**: เพื่อใช้ในการ Pitching กับนักลงทุน
3. **Real-time Operation**: ข้อมูลอัปเดตแบบ Real-time ผ่าน WebSocket
4. **Mobile-First Design**: ออกแบบให้ใช้งานบนมือถือ/แท็บเล็ตได้อย่างสมบูรณ์
5. **ประสิทธิภาพสูง**: ทำงานได้ดีบน Droplet ขนาด RAM 2GB

### วัตถุประสงค์ทางธุรกิจ
- ลดความซับซ้อนในการบริหารโรงแรมขนาดเล็ก
- รองรับรูปแบบธุรกิจที่หลากหลาย (ค้างคืน + ชั่วคราว)
- เพิ่มประสิทธิภาพการทำงานของพนักงาน
- สร้างฐานข้อมูลลูกค้าสำหรับการทำการตลาด

---

## กลุ่มผู้ใช้งาน

### 1. Admin
- **สิทธิ์**: เข้าถึงได้ทุกระบบ
- **หน้าที่**: ตั้งค่าระบบ, ดูรายงานทั้งหมด, จัดการผู้ใช้

### 2. Reception (พนักงานต้อนรับ)
- **สิทธิ์**: เข้าได้ทุกระบบยกเว้นการตั้งค่าระบบและรายงาน
- **หน้าที่**: Check-in/out, จองห้อง, จัดการห้องพัก

### 3. แม่บ้าน (Housekeeping)
- **สิทธิ์**: เข้าได้เฉพาะระบบงานแม่บ้าน
- **หน้าที่**: รับและปิดงานทำความสะอาด

### 4. ช่างซ่อมบำรุง (Maintenance)
- **สิทธิ์**: เข้าได้เฉพาะการดูงานและปิดงานซ่อม
- **หน้าที่**: รับและปิดงานซ่อมบำรุง

### 5. ลูกค้า (Guest) - ไม่ต้อง Login
- **สิทธิ์**: สั่งของผ่าน QR Code เมื่ออยู่ในห้องพัก
- **หน้าที่**: สั่งของเพิ่มเติมขณะเข้าพัก

---

## สถาปัตยกรรมระบบ

### Technology Stack

#### Backend
- **Framework**: FastAPI (Python 3.11+)
- **API Style**: RESTful API + WebSocket (สำหรับ real-time updates)
- **Authentication**: JWT (JSON Web Token)
- **File Upload**: Multipart form data (สำหรับอัปโหลดสลิปโอนเงิน)
- **PDF Generation**: ReportLab หรือ WeasyPrint
- **Telegram Integration**: python-telegram-bot
- **Background Tasks**: Celery + Redis
- **Validation**: Pydantic V2

#### Frontend
- **Framework**: Vue 3 (Composition API + TypeScript)
- **State Management**: Pinia
- **UI Framework**:
  - Vuetify 3 (Material Design) หรือ
  - Element Plus หรือ
  - Naive UI (แนะนำ - modern และ performant)
- **Real-time**: Socket.IO Client
- **HTTP Client**: Axios
- **Date/Time**: Day.js
- **QR Code**: qrcode.vue3
- **Charts**: Chart.js + vue-chartjs (สำหรับรายงาน)
- **Calendar**: FullCalendar (สำหรับระบบจอง)
- **Mobile Detection**: @vueuse/core
- **PWA**: Vite PWA Plugin (เพื่อให้ติดตั้งเป็น App บนมือถือได้)

#### Database
- **RDBMS**: MySQL 8.0
- **ORM**: SQLAlchemy 2.0 (Async)
- **Migration**: Alembic
- **Database Admin**: Adminer (เบา น่าใช้กว่า phpMyAdmin) หรือ phpMyAdmin

#### Infrastructure
- **Containerization**: Docker + Docker Compose
- **Web Server**: Nginx (Reverse Proxy)
- **Cache**: Redis (สำหรับ session, cache, Celery broker)
- **SSL**: Let's Encrypt (ใน production)

#### Development Tools
- **Code Quality**:
  - Black (Python formatter)
  - Ruff (Python linter)
  - ESLint + Prettier (JavaScript/TypeScript)
- **Testing**:
  - Pytest (Backend)
  - Vitest (Frontend)
- **API Documentation**: OpenAPI (Swagger UI) + ReDoc

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         Client Layer                         │
├─────────────────────────────────────────────────────────────┤
│  Vue 3 App (Desktop/Tablet/Mobile)  │  Guest QR Code Page  │
└──────────────────┬──────────────────┴──────────────┬────────┘
                   │                                  │
                   │ HTTP/WebSocket                   │
                   │                                  │
┌──────────────────┴──────────────────────────────────┴────────┐
│                     Nginx (Reverse Proxy)                    │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────┴──────────────────────────────────────────┐
│                    FastAPI Application                       │
├──────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ REST API     │  │ WebSocket    │  │ Auth Module  │      │
│  │ Endpoints    │  │ Handler      │  │ (JWT)        │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Business     │  │ PDF          │  │ Telegram     │      │
│  │ Logic        │  │ Generator    │  │ Notification │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└───────────┬───────────────────┬──────────────────────────────┘
            │                   │
    ┌───────┴────────┐   ┌──────┴──────┐
    │ MySQL Database │   │ Redis Cache │
    │ (SQLAlchemy)   │   │ & Queue     │
    └────────────────┘   └──────┬──────┘
                                │
                         ┌──────┴──────┐
                         │   Celery    │
                         │   Workers   │
                         └─────────────┘
                                │
                         ┌──────┴──────┐
                         │  Telegram   │
                         │  Bot API    │
                         └─────────────┘
```

### Docker Services

```yaml
services:
  - frontend (Vue 3 App)
  - backend (FastAPI)
  - mysql (Database)
  - adminer (Database Management UI)
  - redis (Cache & Message Broker)
  - celery-worker (Background Tasks)
  - nginx (Reverse Proxy)
```

---

## โครงสร้างฐานข้อมูล

### ER Diagram Overview

```
┌──────────────┐
│    users     │
└──────┬───────┘
       │
       │ 1:N
       │
┌──────┴────────┐         ┌──────────────┐
│    bookings   │────────>│   payments   │
└──────┬────────┘   1:N   └──────────────┘
       │
       │ N:1
       │
┌──────┴────────┐
│     rooms     │<─────┬─────────────┐
└──────┬────────┘      │             │
       │               │             │
       │ 1:N           │ 1:N         │ 1:N
       │               │             │
┌──────┴────────┐  ┌───┴──────────┐ ┌┴──────────────┐
│  check_ins    │  │housekeeping  │ │  maintenance  │
└──────┬────────┘  └──────────────┘ └───────────────┘
       │
       │ 1:N
       │
┌──────┴────────┐
│   orders      │
└──────┬────────┘
       │
       │ N:1
       │
┌──────┴────────┐
│   products    │
└───────────────┘
```

### Database Tables

#### 1. users
```sql
- id (PK)
- username (unique)
- password_hash
- full_name
- role (enum: admin, reception, housekeeping, maintenance)
- telegram_user_id (optional)
- is_active
- created_at
- updated_at
```

#### 2. room_types
```sql
- id (PK)
- name (VIP, Standard, etc.)
- description
- is_active
- created_at
- updated_at
```

#### 3. rooms
```sql
- id (PK)
- room_number (unique)
- room_type_id (FK -> room_types)
- bed_type (enum: single, double, twin)
- status (enum: available, occupied, cleaning, reserved, out_of_service)
- is_active
- created_at
- updated_at
```

#### 4. room_rates
```sql
- id (PK)
- room_type_id (FK -> room_types)
- stay_type (enum: overnight, temporary)
- rate (decimal)
- created_at
- updated_at
- UNIQUE(room_type_id, stay_type)
```

#### 5. customers
```sql
- id (PK)
- full_name
- phone_number
- id_card_number (optional)
- email (optional)
- address (optional)
- notes (optional)
- first_visit_date
- last_visit_date
- total_visits
- created_at
- updated_at
```

#### 6. bookings
```sql
- id (PK)
- customer_id (FK -> customers)
- room_id (FK -> rooms)
- check_in_date
- check_out_date
- number_of_nights
- total_amount
- deposit_amount
- status (enum: pending, confirmed, checked_in, completed, cancelled)
- notes
- created_by (FK -> users)
- created_at
- updated_at
- cancelled_at
```

#### 7. check_ins
```sql
- id (PK)
- booking_id (FK -> bookings, nullable)
- customer_id (FK -> customers)
- room_id (FK -> rooms)
- stay_type (enum: overnight, temporary)
- check_in_time
- expected_check_out_time
- actual_check_out_time (nullable)
- number_of_nights (for overnight)
- base_amount
- extra_charges
- discount_amount
- discount_reason
- total_amount
- payment_method (enum: cash, transfer, credit_card)
- payment_slip_url (optional)
- status (enum: checked_in, checked_out)
- notes
- created_by (FK -> users)
- checked_out_by (FK -> users, nullable)
- created_at
- updated_at
```

#### 8. orders
```sql
- id (PK)
- check_in_id (FK -> check_ins)
- product_id (FK -> products)
- quantity
- unit_price
- total_price
- order_source (enum: qr_code, reception)
- status (enum: pending, delivered, completed)
- ordered_at
- delivered_at
- created_at
```

#### 9. products
```sql
- id (PK)
- name
- category (enum: room_amenity, food_beverage)
- price
- is_chargeable
- is_active
- description
- created_at
- updated_at
```

#### 10. housekeeping_tasks
```sql
- id (PK)
- room_id (FK -> rooms)
- task_type (enum: checkout_cleaning, move_room_cleaning, manual)
- assigned_to (FK -> users, nullable)
- status (enum: pending, in_progress, completed)
- started_at (nullable)
- completed_at (nullable)
- duration_minutes (calculated)
- notes
- created_at
- updated_at
```

#### 11. maintenance_tasks
```sql
- id (PK)
- room_id (FK -> rooms, nullable)
- reported_by (FK -> users)
- assigned_to (FK -> users, nullable)
- title
- description
- status (enum: pending, in_progress, completed)
- priority (enum: low, medium, high)
- cost
- cost_details (JSON)
- reported_at
- started_at (nullable)
- completed_at (nullable)
- created_at
- updated_at
```

#### 12. payments
```sql
- id (PK)
- check_in_id (FK -> check_ins, nullable)
- booking_id (FK -> bookings, nullable)
- amount
- payment_method (enum: cash, transfer, credit_card)
- payment_type (enum: deposit, full_payment, partial_payment)
- payment_slip_url (optional)
- receipt_url (optional)
- notes
- created_by (FK -> users)
- created_at
```

#### 13. notifications
```sql
- id (PK)
- notification_type (enum: room_status_change, overtime_alert, booking_reminder, etc.)
- target_role (enum: admin, reception, housekeeping, maintenance)
- title
- message
- room_id (FK -> rooms, nullable)
- is_read
- telegram_sent
- telegram_message_id
- created_at
- read_at
```

#### 14. system_settings
```sql
- id (PK)
- key (unique)
- value (text)
- data_type (enum: string, number, json)
- description
- updated_at
```

#### 15. activity_logs
```sql
- id (PK)
- user_id (FK -> users)
- action_type (enum: check_in, check_out, room_move, booking_create, etc.)
- entity_type (string)
- entity_id (integer)
- details (JSON)
- ip_address
- created_at
```

### Database Indexes

```sql
-- Performance indexes
CREATE INDEX idx_rooms_status ON rooms(status);
CREATE INDEX idx_check_ins_status ON check_ins(status);
CREATE INDEX idx_check_ins_room_id ON check_ins(room_id);
CREATE INDEX idx_bookings_dates ON bookings(check_in_date, check_out_date);
CREATE INDEX idx_bookings_status ON bookings(status);
CREATE INDEX idx_customers_phone ON customers(phone_number);
CREATE INDEX idx_notifications_target_role ON notifications(target_role, is_read);
CREATE INDEX idx_activity_logs_created_at ON activity_logs(created_at);
```

---

## รายละเอียดฟีเจอร์

### Module 1: ระบบจัดการผู้ใช้ (User Management)

#### Features
1. Login/Logout (JWT Authentication)
2. CRUD Users (admin only)
3. Role-based Access Control (RBAC)
4. User Profile Management

#### API Endpoints
```
POST   /api/v1/auth/login
POST   /api/v1/auth/logout
GET    /api/v1/auth/me
GET    /api/v1/users
POST   /api/v1/users
GET    /api/v1/users/{id}
PUT    /api/v1/users/{id}
DELETE /api/v1/users/{id}
```

#### UI Components
- Login Page
- User List Page
- User Form (Create/Edit)
- User Profile Page

---

### Module 2: ระบบจัดการห้องพัก (Room Management)

#### Features
1. CRUD Room Types
2. CRUD Rooms
3. Set Room Rates (by room type and stay type)
4. Enable/Disable Room Service Status

#### API Endpoints
```
GET    /api/v1/room-types
POST   /api/v1/room-types
PUT    /api/v1/room-types/{id}
DELETE /api/v1/room-types/{id}

GET    /api/v1/rooms
POST   /api/v1/rooms
PUT    /api/v1/rooms/{id}
DELETE /api/v1/rooms/{id}
PATCH  /api/v1/rooms/{id}/status

GET    /api/v1/room-rates
POST   /api/v1/room-rates
PUT    /api/v1/room-rates/{id}
```

#### UI Components
- Room Type List/Form
- Room List/Form
- Room Rate Matrix
- Room Status Toggle

---

### Module 3: แผงควบคุมห้องพัก (Room Control Dashboard) ⭐ CORE FEATURE

#### Features
1. **Real-time Room Status Display**
   - Display as Cards (responsive grid)
   - Color-coded status:
     - เขียว: ว่าง (Available)
     - แดง: มีการเข้าพัก (Occupied)
     - เหลือง: กำลังทำความสะอาด (Cleaning)
     - ฟ้า: จองแล้ว (Reserved)
     - เทา: ไม่เปิดบริการ (Out of Service)

2. **Room Card Information**
   - Room Number
   - Room Type
   - Bed Type
   - Current Status
   - Guest Name (if occupied)
   - Check-in Time
   - Expected Check-out Time
   - Overtime Alert (if applicable)

3. **Quick Actions on Card**
   - Check In
   - Check Out
   - Move Room
   - View Details
   - Order Items
   - Manual Status Change (cleaning -> available)

4. **Real-time Notifications**
   - Room status changes
   - Overtime alerts
   - New bookings
   - Housekeeping completed
   - Maintenance requests
   - Notification history panel

5. **Filtering & Search**
   - Filter by status
   - Filter by room type
   - Search by room number or guest name

#### API Endpoints
```
GET    /api/v1/dashboard/rooms (real-time room status)
WS     /ws/dashboard (WebSocket for real-time updates)
POST   /api/v1/dashboard/rooms/{id}/quick-check-in
POST   /api/v1/dashboard/rooms/{id}/quick-check-out
PATCH  /api/v1/dashboard/rooms/{id}/force-available
```

#### UI Components
- Dashboard Page (Main)
- Room Card Component
- Quick Action Modals
- Notification Panel
- Filter Sidebar

#### Real-time Events (WebSocket)
```javascript
{
  event: "room_status_changed",
  data: {
    room_id: 101,
    old_status: "cleaning",
    new_status: "available",
    timestamp: "2024-01-15T10:30:00"
  }
}

{
  event: "overtime_alert",
  data: {
    room_id: 102,
    guest_name: "นายสมชาย ใจดี",
    overtime_minutes: 45,
    stay_type: "temporary"
  }
}
```

---

### Module 4: ระบบ Check In

#### Features
1. Check In Form
2. Customer Information (auto-complete from existing customers)
3. Stay Type Selection (overnight/temporary)
4. Booking Integration (pre-fill from booking data)
5. Payment Recording
6. Show total amount and deposit deduction

#### Business Rules
- **Overnight**:
  - Check-in from 13:00
  - Check-out before 12:00 next day(s)
  - Specify number of nights
- **Temporary**:
  - Check-in anytime
  - Check-out within 3 hours (configurable)
  - Auto-calculate expected check-out time

#### API Endpoints
```
POST   /api/v1/check-ins
GET    /api/v1/check-ins/{id}
GET    /api/v1/bookings/{booking_id}/pre-fill
```

#### UI Components
- Check-In Form Modal
- Customer Search/Select
- Stay Type Selector
- Payment Calculator

---

### Module 5: ระบบ Check Out

#### Features
1. Check Out Form
2. Show overtime duration (if any)
3. Additional charges input
4. Discount input with reason
5. Total calculation (base + extras + orders - discount - deposit)
6. Payment method selection
7. Payment slip upload (for bank transfer)
8. PDF receipt generation
9. Auto-create housekeeping task
10. Telegram notification to housekeeping

#### API Endpoints
```
POST   /api/v1/check-outs
GET    /api/v1/check-ins/{id}/checkout-summary
POST   /api/v1/check-outs/{id}/generate-receipt
POST   /api/v1/check-outs/{id}/upload-slip
```

#### UI Components
- Check-Out Form Modal
- Payment Summary
- Slip Upload (with camera/file option)
- Receipt Preview/Download

---

### Module 6: การย้ายห้องพัก (Room Transfer)

#### Features
1. Move guest to another room (same room type only)
2. Transfer all data (customer, orders, charges, etc.)
3. Auto-create housekeeping task for old room
4. Telegram notification

#### API Endpoints
```
POST   /api/v1/room-transfers
```

#### UI Components
- Room Transfer Modal
- Available Room Selector

---

### Module 7: ระบบงานแม่บ้าน (Housekeeping)

#### Features
1. Task List View
2. Task Detail Page (accessible via Telegram link)
3. Start Cleaning (track time)
4. Complete Cleaning
5. Report Damage (create maintenance task)
6. Task History & Reports
7. Housekeeping Performance Report

#### API Endpoints
```
GET    /api/v1/housekeeping/tasks
GET    /api/v1/housekeeping/tasks/{id}
POST   /api/v1/housekeeping/tasks/{id}/start
POST   /api/v1/housekeeping/tasks/{id}/complete
POST   /api/v1/housekeeping/tasks/{id}/report-damage
GET    /api/v1/housekeeping/reports/performance
```

#### UI Components
- Housekeeping Task List
- Task Detail Page (mobile-optimized)
- Timer Component
- Damage Report Form

#### Telegram Integration
```
Message: "🧹 มีงานทำความสะอาดใหม่: ห้อง 101 (VIP)
🔗 คลิกเพื่อรับงาน: https://app.flyinghotel.com/housekeeping/tasks/123"
```

---

### Module 8: ระบบแจ้งซ่อม (Maintenance)

#### Features
1. Create Maintenance Request
2. Task List View
3. Task Detail Page (accessible via Telegram link)
4. Accept Task
5. Complete Task
6. Record Costs
7. Maintenance Reports

#### API Endpoints
```
GET    /api/v1/maintenance/tasks
POST   /api/v1/maintenance/tasks
GET    /api/v1/maintenance/tasks/{id}
POST   /api/v1/maintenance/tasks/{id}/accept
POST   /api/v1/maintenance/tasks/{id}/complete
GET    /api/v1/maintenance/reports
```

#### UI Components
- Maintenance Task List
- Create Task Form
- Task Detail Page (mobile-optimized)
- Cost Recording Form

#### Telegram Integration
```
Message: "🔧 มีงานซ่อมใหม่: แอร์เสีย - ห้อง 205
🔗 คลิกเพื่อรับงาน: https://app.flyinghotel.com/maintenance/tasks/456"
```

---

### Module 9: ระบบจองล่วงหน้า (Booking)

#### Features
1. Calendar View (FullCalendar)
2. Create Booking
3. Edit/Cancel Booking
4. Deposit Recording
5. Booking Reminders (Telegram notification 1 hour after check-in time)
6. Thai Public Holidays Integration (API)
7. Auto-update room status on check-in date
8. Booking Reports

#### Business Rules
- Only overnight stays can be booked
- Deposit is optional but non-refundable
- If guest doesn't check in within 1 hour after check-in time:
  - Send reminder via Telegram
  - Show alert on room card
  - If no-show: mark as cancelled, deposit is forfeited

#### API Endpoints
```
GET    /api/v1/bookings
POST   /api/v1/bookings
GET    /api/v1/bookings/{id}
PUT    /api/v1/bookings/{id}
DELETE /api/v1/bookings/{id}
GET    /api/v1/bookings/calendar
GET    /api/v1/bookings/public-holidays
```

#### UI Components
- Calendar View (FullCalendar)
- Booking Form Modal
- Booking List
- Booking Detail View

#### Thai Public Holiday API
```
https://github.com/peerapatch/thailand-public-holidays-api
หรือใช้ข้อมูลจาก Government Open Data
```

---

### Module 10: ระบบข้อมูลลูกค้า (Mini CRM)

#### Features
1. Customer Database
2. Customer Detail View
3. Visit History
4. Stay Preferences
5. Total Revenue per Customer
6. Customer Reports
7. Auto-merge duplicate customers (phone number)

#### API Endpoints
```
GET    /api/v1/customers
POST   /api/v1/customers
GET    /api/v1/customers/{id}
PUT    /api/v1/customers/{id}
GET    /api/v1/customers/{id}/history
GET    /api/v1/customers/reports
```

#### UI Components
- Customer List
- Customer Detail Page
- Visit History Timeline
- Customer Reports

---

### Module 11: ระบบให้ลูกค้าสั่งของเพิ่ม (Mini Store)

#### Features
1. **QR Code per Room** (static, unique per room)
2. Guest Order Page (no login required)
3. Product Catalog (room amenities + food & beverage)
4. Shopping Cart
5. Order History
6. Order Management (reception view)
7. Order Summary in Check-out

#### Business Rules
- Guest can only order when room has active check-in
- Orders are automatically added to check-out bill
- QR code is static and never changes (room-based)

#### QR Code URL Format
```
https://app.flyinghotel.com/guest/room/101/order?token=<unique_room_token>
```

#### API Endpoints
```
GET    /api/v1/guest/rooms/{room_id}/check-in-status
GET    /api/v1/guest/products
POST   /api/v1/guest/orders
GET    /api/v1/guest/orders/history

GET    /api/v1/products
POST   /api/v1/products
PUT    /api/v1/products/{id}

GET    /api/v1/orders
PATCH  /api/v1/orders/{id}/status
```

#### UI Components
- Guest Order Page (mobile-optimized, no login)
- Product Catalog
- Shopping Cart
- Order History
- Product Management (admin)
- Order Management (reception)

---

### Module 12: ระบบรายงาน (Reports)

#### Reports List
1. **Daily Summary Report**
   - Total bookings
   - Total check-ins
   - Total revenue
   - Occupancy rate
   - Auto-send via Telegram at 8:00 AM daily

2. **Revenue Report**
   - Filter by date range
   - Group by stay type
   - Group by room type
   - Charts & graphs

3. **Occupancy Report**
   - Occupancy rate over time
   - Peak hours/days analysis

4. **Booking Report**
   - Booking sources
   - Cancellation rate
   - Average booking lead time

5. **Housekeeping Performance Report**
   - Tasks completed per day
   - Average cleaning time
   - Staff performance

6. **Maintenance Report**
   - Tasks by status
   - Total maintenance costs
   - Average resolution time

7. **Customer Report**
   - New vs returning customers
   - Top customers by revenue
   - Customer demographics

8. **Product Sales Report**
   - Best-selling products
   - Revenue by product category

#### API Endpoints
```
GET    /api/v1/reports/daily-summary
GET    /api/v1/reports/revenue
GET    /api/v1/reports/occupancy
GET    /api/v1/reports/bookings
GET    /api/v1/reports/housekeeping
GET    /api/v1/reports/maintenance
GET    /api/v1/reports/customers
GET    /api/v1/reports/products
```

#### UI Components
- Reports Dashboard
- Date Range Picker
- Charts (Chart.js)
- Export to PDF/Excel

---

### Module 13: การตั้งค่าระบบ (System Settings)

#### Settings Sections
1. **Hotel Information**
   - Hotel name
   - Address
   - Phone number
   - Logo upload

2. **Room Settings**
   - Manage room types
   - Manage room rates
   - Temporary stay duration (default 3 hours)
   - Check-in/out times

3. **Telegram Integration**
   - Bot Token
   - Admin Group Chat ID
   - Reception Group Chat ID
   - Housekeeping Group Chat ID
   - Maintenance Group Chat ID
   - Test Connection

4. **Notification Settings**
   - Enable/disable notification types
   - Notification schedules

5. **Payment Settings**
   - Accepted payment methods
   - Tax rate (if any)

6. **System Settings**
   - Time zone
   - Date/time format
   - Currency

#### API Endpoints
```
GET    /api/v1/settings
PUT    /api/v1/settings
POST   /api/v1/settings/test-telegram
POST   /api/v1/settings/upload-logo
```

#### UI Components
- Settings Page (tabbed interface)
- Hotel Info Form
- Telegram Settings Form
- Test Connection Button

---

## UI/UX Design Principles

### Core Principles
1. **Mobile-First**: ออกแบบสำหรับมือถือก่อน แล้วขยายไป tablet และ desktop
2. **Intuitive Navigation**: ผู้ใช้สามารถหาฟีเจอร์ได้ภายใน 3 คลิก
3. **Visual Hierarchy**: ใช้สี ขนาด และการจัดวางเพื่อสื่อความสำคัญ
4. **Immediate Feedback**: ทุกการกระทำจะมี feedback ทันที (loading states, success/error messages)
5. **Consistent**: ใช้ design patterns เดียวกันทั่วทั้งระบบ
6. **Thai Language First**: ภาษาไทยที่อ่านง่าย ไม่ใช้คำศัพท์เทคนิค

### Color Scheme
```css
/* Primary Colors */
--primary: #1976D2 (น้ำเงิน - trustworthy, professional)
--secondary: #424242 (เทาเข้ม - modern)
--accent: #FF6F00 (ส้ม - call to action)

/* Status Colors */
--available: #4CAF50 (เขียว)
--occupied: #F44336 (แดง)
--cleaning: #FFC107 (เหลือง)
--reserved: #2196F3 (ฟ้า)
--out-of-service: #9E9E9E (เทา)

/* Alert Colors */
--success: #4CAF50
--warning: #FF9800
--error: #F44336
--info: #2196F3

/* Background */
--bg-primary: #FAFAFA
--bg-secondary: #FFFFFF
--bg-dark: #212121

/* Text */
--text-primary: #212121
--text-secondary: #757575
--text-disabled: #BDBDBD
```

### Typography
```css
/* Font Family */
--font-family: 'Prompt', 'Sarabun', sans-serif (Thai-friendly)

/* Font Sizes */
--text-xs: 0.75rem (12px)
--text-sm: 0.875rem (14px)
--text-base: 1rem (16px)
--text-lg: 1.125rem (18px)
--text-xl: 1.25rem (20px)
--text-2xl: 1.5rem (24px)
--text-3xl: 1.875rem (30px)
--text-4xl: 2.25rem (36px)

/* Font Weights */
--font-light: 300
--font-normal: 400
--font-medium: 500
--font-semibold: 600
--font-bold: 700
```

### Responsive Breakpoints
```css
--mobile: 320px - 767px
--tablet: 768px - 1023px
--desktop: 1024px+
```

### Component Guidelines

#### Room Card Design
```
┌─────────────────────────────┐
│ 101                    [VIP]│
│ เตียงคู่                     │
│                              │
│ ⚪ ว่าง                      │
│                              │
│ [Check In] [รายละเอียด]      │
└─────────────────────────────┘

(สีพื้นหลังเปลี่ยนตามสถานะ)
```

#### Dashboard Layout (Desktop)
```
┌─────────────────────────────────────────────────┐
│ Header: Logo | Dashboard | ... | User | Logout  │
├─────────────────────────────────────────────────┤
│                                                  │
│ [Filters] [Search: ค้นหาห้อง...]                │
│                                                  │
│ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐            │
│ │ 101  │ │ 102  │ │ 103  │ │ 104  │            │
│ │ ว่าง │ │ พัก  │ │ ทำส. │ │ จอง  │            │
│ └──────┘ └──────┘ └──────┘ └──────┘            │
│                                                  │
│ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐            │
│ │ 201  │ │ 202  │ │ 203  │ │ 204  │            │
│ └──────┘ └──────┘ └──────┘ └──────┘            │
│                                                  │
├─────────────────────────────────────────────────┤
│ Notification Panel (slide-in from right) 🔔     │
└─────────────────────────────────────────────────┘
```

#### Dashboard Layout (Mobile)
```
┌──────────────────┐
│ ☰  Dashboard  🔔 │
├──────────────────┤
│ [Search...]      │
├──────────────────┤
│ ┌──────┐         │
│ │ 101  │         │
│ │ ว่าง │         │
│ └──────┘         │
│                  │
│ ┌──────┐         │
│ │ 102  │         │
│ │ พัก  │         │
│ └──────┘         │
│                  │
│ ┌──────┐         │
│ │ 103  │         │
│ └──────┘         │
└──────────────────┘
```

### Interaction Patterns

#### Loading States
- Skeleton screens (ไม่ใช้ spinner เดี่ยวๆ)
- Progress indicators สำหรับ long operations
- Optimistic updates (อัปเดต UI ก่อนได้รับ response)

#### Form Validation
- Inline validation (real-time)
- Clear error messages ภาษาไทย
- Highlight required fields

#### Modals
- Mobile: Full-screen modal
- Desktop: Centered modal with backdrop
- Easy to close (ESC key, backdrop click, close button)

#### Toast Notifications
- Position: Top-right (desktop) / Top-center (mobile)
- Auto-dismiss after 5 seconds
- Manual dismiss option

---

## แผนการพัฒนา

### Development Phases

แผนการพัฒนาแบ่งเป็น **8 Phases** โดยแต่ละ phase จะต้องทดสอบให้ผ่าน 100% ก่อนไปต่อ

---

### Phase 0: Project Setup & Infrastructure (2-3 วัน)

#### Objectives
- ตั้งค่า Docker environment
- สร้าง project structure
- ตั้งค่า development tools

#### Tasks
1. **Docker Setup**
   - สร้าง `docker-compose.yml`
   - Services: MySQL, Redis, Adminer, FastAPI, Vue, Nginx
   - Volume mounting สำหรับ development

2. **Backend Setup**
   - สร้าง FastAPI project structure
   - ตั้งค่า SQLAlchemy + Alembic
   - ตั้งค่า Pydantic models
   - ตั้งค่า pytest

3. **Frontend Setup**
   - สร้าง Vue 3 + Vite project
   - ติดตั้ง UI framework (Naive UI recommended)
   - ตั้งค่า Vue Router + Pinia
   - ตั้งค่า Axios + API client
   - ตั้งค่า Vitest

4. **Code Quality Tools**
   - ESLint + Prettier (frontend)
   - Black + Ruff (backend)
   - Git hooks (pre-commit)

5. **Documentation**
   - สร้างไฟล์ `ARCHITECTURE.md`
   - สร้างไฟล์ `API_CONVENTIONS.md`
   - สร้างไฟล์ `DEVELOPMENT.md`

#### Deliverables
- โปรเจ็ค run ขึ้นด้วย `docker-compose up` ได้
- Backend ตอบ `/health` endpoint ได้
- Frontend แสดงหน้า Hello World ได้
- Database migration run ได้

#### Testing
- Docker compose up สำเร็จ
- เข้า Adminer ได้
- Backend Swagger UI ทำงานได้
- Frontend hot-reload ทำงานได้

---

### Phase 1: Authentication & User Management (3-4 วัน)

#### Objectives
- Login/Logout
- User CRUD (admin only)
- Role-based access control
- Basic UI layout

#### Tasks
1. **Database**
   - สร้าง migration สำหรับ `users` table
   - Seed data (1 admin user)

2. **Backend**
   - JWT authentication
   - `/api/v1/auth/login` endpoint
   - `/api/v1/auth/logout` endpoint
   - `/api/v1/auth/me` endpoint
   - `/api/v1/users/*` CRUD endpoints
   - Middleware สำหรับ authentication & authorization
   - Unit tests

3. **Frontend**
   - Login page
   - Auth store (Pinia)
   - HTTP interceptor (add JWT token)
   - Protected routes
   - Main layout (header, sidebar, content)
   - User management pages (admin only)

#### Deliverables
- Login ด้วย username/password ได้
- Token ถูกเก็บใน localStorage
- Protected routes redirect ไป login page
- Admin สามารถ CRUD users ได้
- Logout ทำงานได้

#### Testing
- Login successful → redirect to dashboard
- Login failed → show error message
- Protected route redirect ถ้าไม่ได้ login
- Admin สามารถเพิ่ม user ได้
- Non-admin ไม่เห็น user management menu

---

### Phase 2: Room Management (3-4 วัน)

#### Objectives
- จัดการประเภทห้อง
- จัดการห้องพัก
- กำหนดอัตราราคา

#### Tasks
1. **Database**
   - Migration: `room_types`, `rooms`, `room_rates`
   - Seed data: 2 room types, 10 rooms, room rates

2. **Backend**
   - `/api/v1/room-types/*` CRUD endpoints
   - `/api/v1/rooms/*` CRUD endpoints
   - `/api/v1/room-rates/*` CRUD endpoints
   - Unit tests

3. **Frontend**
   - Room Types management page
   - Rooms management page
   - Room Rates management page (matrix view)
   - Form validation

#### Deliverables
- Admin สามารถ CRUD room types ได้
- Admin สามารถ CRUD rooms ได้
- Admin สามารถตั้งราคาห้องได้ (per room type + stay type)
- UI responsive (mobile + desktop)

#### Testing
- สร้าง room type ได้
- สร้าง room ได้ และต้องเลือก room type
- ตั้งราคาห้อง VIP ค้างคืน 1000 บาท
- ตั้งราคาห้อง VIP ชั่วคราว 500 บาท
- Edit/Delete ทำงานได้

---

### Phase 3: Room Control Dashboard (5-6 วัน) ⭐ CRITICAL

#### Objectives
- แสดงสถานะห้องแบบ real-time
- Room cards with color-coded status
- Quick actions (check-in/out, view details)
- Real-time notifications
- WebSocket integration

#### Tasks
1. **Database**
   - Migration: `check_ins`, `notifications`

2. **Backend**
   - WebSocket server setup
   - `/api/v1/dashboard/rooms` endpoint (get all room status)
   - WebSocket endpoint `/ws/dashboard`
   - Room status update logic
   - Notification creation logic
   - Unit tests

3. **Frontend**
   - Dashboard page (main page after login)
   - Room card component
   - WebSocket client connection
   - Real-time room status updates
   - Notification panel (slide-in)
   - Filter sidebar (status, room type)
   - Search box (room number, guest name)

#### Deliverables
- Dashboard แสดง room cards ทั้งหมด
- Room cards เปลี่ยนสีตามสถานะ
- WebSocket connection ทำงานได้
- เมื่อสถานะห้องเปลี่ยน → card อัปเดตแบบ real-time
- Notification panel แสดงการแจ้งเตือน
- UI responsive (mobile: 1 column, tablet: 2 columns, desktop: 4-5 columns)

#### Testing
- Dashboard แสดงห้อง 10 ห้อง
- เปลี่ยนสถานะห้อง 101 เป็น "cleaning" ใน database → card อัปเดตทันที
- WebSocket disconnect → reconnect automatically
- Filter by status ทำงานได้
- Search room ทำงานได้
- Mobile/tablet/desktop responsive

---

### Phase 4: Check-In & Check-Out (5-6 วัน) ⭐ CRITICAL

#### Objectives
- Check-in form
- Check-out form
- Payment recording
- PDF receipt generation
- Customer data integration

#### Tasks
1. **Database**
   - Migration: `customers`, `payments`
   - Update `check_ins` table

2. **Backend**
   - Customer auto-complete search endpoint
   - `/api/v1/check-ins` POST endpoint
   - `/api/v1/check-ins/{id}` GET endpoint
   - `/api/v1/check-outs` POST endpoint
   - `/api/v1/check-outs/{id}/generate-receipt` endpoint
   - `/api/v1/check-outs/{id}/upload-slip` endpoint
   - PDF generation (WeasyPrint or ReportLab)
   - Calculate overtime logic
   - Room status update after check-in/out
   - WebSocket broadcast room status change
   - Unit tests

3. **Frontend**
   - Check-in modal (triggered from room card)
   - Customer search/select component
   - Stay type selector (overnight/temporary)
   - Check-out modal
   - Payment summary component
   - File upload (payment slip) with camera support
   - Receipt preview/download

#### Deliverables
- กดปุ่ม Check In ที่ room card → เปิด modal
- เลือกประเภทการพัก (ค้างคืน/ชั่วคราว)
- กรอกข้อมูลลูกค้า (auto-complete)
- Check-in สำเร็จ → room status เปลี่ยนเป็น "occupied"
- Check-out → คำนวณค่าใช้จ่ายทั้งหมด
- แสดง overtime alert ถ้ามี
- สามารถเพิ่มค่าใช้จ่าย/ส่วนลดได้
- Upload payment slip ได้
- Generate PDF receipt ได้

#### Testing
- Check-in ห้อง 101 แบบชั่วคราว → expected check-out = check-in + 3 hours
- Check-in ห้อง 102 แบบค้างคืน 2 คืน → expected check-out = check-in date + 2 days at 12:00
- Check-out ทันเวลา → ไม่มี overtime
- Check-out เกินเวลา 1 ชั่วโมง → แสดง overtime alert
- เพิ่มค่าใช้จ่าย 100 บาท → total amount เพิ่ม 100 บาท
- ใส่ส่วนลด 50 บาท → total amount ลด 50 บาท
- Generate PDF receipt → download ได้
- Upload slip → แสดง preview ได้

---

### Phase 5: Housekeeping System (4-5 วัน)

#### Objectives
- Housekeeping task creation (auto-create after check-out)
- Task list view
- Task detail page (mobile-optimized)
- Start/Complete task
- Report damage (create maintenance task)
- Telegram notification

#### Tasks
1. **Database**
   - Migration: `housekeeping_tasks`, `maintenance_tasks`

2. **Backend**
   - Auto-create housekeeping task after check-out
   - `/api/v1/housekeeping/tasks` endpoint
   - `/api/v1/housekeeping/tasks/{id}` GET endpoint
   - `/api/v1/housekeeping/tasks/{id}/start` POST endpoint
   - `/api/v1/housekeeping/tasks/{id}/complete` POST endpoint
   - `/api/v1/housekeeping/tasks/{id}/report-damage` POST endpoint
   - Telegram notification (python-telegram-bot)
   - Unit tests

3. **Frontend**
   - Housekeeping task list page
   - Task detail page (mobile-optimized)
   - Timer component (track cleaning time)
   - Damage report form

4. **Celery Setup**
   - Celery worker setup
   - Task: Send Telegram notification

#### Deliverables
- Check-out ห้อง 101 → auto-create housekeeping task
- Send Telegram notification with task link
- แม่บ้านกดรับงาน → status = "in_progress", start timer
- แม่บ้านกดทำเสร็จ → status = "completed", room status = "available"
- แม่บ้านรายงานความเสียหาย → create maintenance task

#### Testing
- Check-out ห้อง 101 → housekeeping task ถูกสร้าง
- Telegram message ถูกส่ง (ตรวจสอบใน Telegram group)
- คลิก link ใน Telegram → เปิด task detail page
- กดเริ่มทำความสะอาด → timer start
- กดทำเสร็จ → room status = "available"
- รายงานความเสียหาย → maintenance task ถูกสร้าง

---

### Phase 6: Maintenance & Order System (4-5 วัน)

#### Objectives
- Maintenance task management
- Telegram notification
- Product management
- Guest order page (QR code)
- Reception order management

#### Tasks
1. **Database**
   - Migration: `products`, `orders`

2. **Backend**
   - `/api/v1/maintenance/tasks/*` CRUD endpoints
   - `/api/v1/products/*` CRUD endpoints
   - `/api/v1/guest/rooms/{room_id}/check-in-status` endpoint
   - `/api/v1/guest/products` endpoint
   - `/api/v1/guest/orders` POST endpoint
   - `/api/v1/orders` GET endpoint (reception)
   - QR code generation (per room)
   - Telegram notification (maintenance)
   - Unit tests

3. **Frontend**
   - Maintenance task list page
   - Maintenance task detail page
   - Product management page
   - Guest order page (public, no auth, mobile-optimized)
   - Order management page (reception)
   - QR code display page (admin)

#### Deliverables
- Admin สามารถจัดการ maintenance tasks ได้
- ช่างรับ Telegram notification พร้อม link
- Admin สามารถจัดการสินค้าได้
- แต่ละห้องมี QR code เฉพาะ
- ลูกค้า scan QR → เปิดหน้าสั่งของ (ถ้ามีการ check-in)
- ลูกค้าสั่งของได้ → order ถูกบันทึก
- Reception เห็น order list และเปลี่ยนสถานะได้

#### Testing
- สร้าง maintenance task → ช่างได้รับ Telegram
- ช่างปิดงานพร้อมระบุค่าใช้จ่าย → บันทึกได้
- Admin สร้างสินค้า "น้ำเปล่า" ราคา 10 บาท
- Scan QR ห้อง 101 (ที่มี check-in) → เปิดหน้าสั่งของได้
- Scan QR ห้อง 102 (ที่ไม่มี check-in) → แสดง error
- ลูกค้าสั่งน้ำเปล่า 2 ขวด → order ถูกสร้าง
- Reception เห็น order และเปลี่ยนสถานะเป็น "delivered"

---

### Phase 7: Booking System (5-6 วัน)

#### Objectives
- Booking calendar (FullCalendar)
- Create/Edit/Cancel booking
- Deposit recording
- Thai public holidays integration
- Booking reminders (Telegram)
- Auto-update room status

#### Tasks
1. **Database**
   - Migration: `bookings` (already created in Phase 4)
   - Update indexes

2. **Backend**
   - `/api/v1/bookings/*` CRUD endpoints
   - `/api/v1/bookings/calendar` endpoint
   - `/api/v1/bookings/public-holidays` endpoint (fetch from external API)
   - Celery task: Check booking check-in time (run every 30 mins)
   - Celery task: Send reminder if 1 hour passed after check-in time
   - Auto-update room status on booking date
   - Unit tests

3. **Frontend**
   - Booking calendar page (FullCalendar)
   - Booking form modal
   - Booking list page
   - Booking detail page

4. **Celery Tasks**
   - Scheduled task: Update room status from "available" to "reserved" on booking date
   - Scheduled task: Check booking check-in time and send reminder

#### Deliverables
- สร้าง booking ได้ผ่าน calendar view
- Booking แสดงใน calendar
- Thai public holidays แสดงใน calendar
- สามารถระบุเงินมัดจำได้
- Edit/Cancel booking ได้
- เมื่อถึงวันเข้าพัก → room status = "reserved" automatically
- เมื่อเลยเวลา check-in ไป 1 ชั่วโมง → send Telegram reminder
- เมื่อ check-in จาก booking → ดึงข้อมูลจาก booking มาใช้

#### Testing
- สร้าง booking ห้อง 101 วันที่ 20 ม.ค. 2025 → แสดงใน calendar
- วันที่ 20 ม.ค. 2025 → room status = "reserved"
- Check-in time 14:00 → เวลา 15:00 ยังไม่ check-in → receive Telegram reminder
- Cancel booking → room status กลับเป็น "available"

---

### Phase 8: Reports & Settings (4-5 วัน)

#### Objectives
- Report pages (revenue, occupancy, etc.)
- Chart visualization
- System settings page
- Telegram settings
- Daily summary report (auto-send at 8 AM)

#### Tasks
1. **Database**
   - Migration: `system_settings`, `activity_logs`
   - Seed settings data

2. **Backend**
   - `/api/v1/reports/*` endpoints (all report types)
   - `/api/v1/settings` GET/PUT endpoints
   - `/api/v1/settings/test-telegram` POST endpoint
   - `/api/v1/settings/upload-logo` POST endpoint
   - Celery task: Daily summary report (send at 8:00 AM)
   - Unit tests

3. **Frontend**
   - Reports dashboard page
   - Individual report pages (revenue, occupancy, etc.)
   - Charts (Chart.js)
   - Settings page (tabbed)
   - Hotel info form
   - Telegram settings form
   - Test connection button

4. **Celery Tasks**
   - Scheduled task: Generate and send daily summary report at 8:00 AM

#### Deliverables
- Admin/Reception เห็น reports menu
- แต่ละรายงานแสดงข้อมูลได้ถูกต้อง
- Charts แสดงผลสวยงาม
- Admin สามารถตั้งค่าระบบได้
- Test Telegram connection ได้
- Daily summary report ถูกส่งไปยัง Admin group ทุกวันเวลา 8:00 AM

#### Testing
- ดูรายงานรายได้ → แสดง chart และ table
- Filter รายงานตามช่วงเวลา → ข้อมูลเปลี่ยน
- ตั้งค่าชื่อโรงแรม → บันทึกได้
- ตั้งค่า Telegram bot token → test connection สำเร็จ
- วันถัดไปเวลา 8:00 AM → receive daily summary report

---

### Phase 9: Final Polish & Testing (3-4 วัน)

#### Objectives
- UI/UX improvements
- Performance optimization
- End-to-end testing
- Bug fixes
- Documentation

#### Tasks
1. **UI/UX Polish**
   - Review all pages (mobile/tablet/desktop)
   - Improve animations/transitions
   - Ensure consistent styling
   - Add loading states
   - Improve error messages

2. **Performance**
   - Optimize SQL queries (add indexes)
   - Lazy load components
   - Image optimization
   - Bundle size optimization
   - WebSocket connection optimization

3. **Testing**
   - End-to-end tests (Playwright or Cypress)
   - Load testing (Locust)
   - Fix all bugs

4. **Documentation**
   - Update README.md
   - User manual (Thai language)
   - Deployment guide
   - API documentation

5. **Deployment Preparation**
   - Production docker-compose.yml
   - Environment variables template
   - Backup strategy
   - Monitoring setup (optional)

#### Deliverables
- แอพ run ได้สมบูรณ์ทุก feature
- UI responsive ทุกหน้า
- Performance ดี (load time < 3 seconds)
- Bug-free
- Documentation ครบถ้วน
- พร้อม deploy ไป production

#### Testing
- E2E test scenario:
  1. Login as reception
  2. Check-in guest to room 101
  3. Guest orders item via QR code
  4. Check-out guest
  5. Housekeeping receives notification
  6. Housekeeping completes task
  7. Room is available again
  8. Admin views reports

---

## Testing Strategy

### Unit Testing
- **Backend**: Pytest (target: 80% coverage)
- **Frontend**: Vitest (target: 60% coverage)

### Integration Testing
- API endpoint testing (Pytest)
- Database transaction testing

### End-to-End Testing
- Playwright or Cypress
- Critical user flows:
  - Login → Dashboard
  - Check-in → Order → Check-out → Housekeeping
  - Booking → Check-in from booking
  - Reports generation

### Manual Testing Checklist (per phase)
- [ ] Feature ทำงานได้ตามที่ออกแบบ
- [ ] UI responsive (mobile/tablet/desktop)
- [ ] Error handling ทำงานได้
- [ ] Real-time updates ทำงานได้
- [ ] Telegram notifications ส่งได้
- [ ] Performance ยอมรับได้

---

## Deployment Strategy

### Production Environment
- Platform: Digital Ocean Droplet (2GB RAM)
- OS: Ubuntu 22.04 LTS
- Docker + Docker Compose

### Deployment Steps
1. **Server Setup**
   ```bash
   # Install Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh

   # Install Docker Compose
   apt-get install docker-compose-plugin
   ```

2. **Clone Repository**
   ```bash
   git clone <repo_url>
   cd FlyingHotelApp
   ```

3. **Environment Configuration**
   ```bash
   cp .env.example .env.production
   # Edit .env.production with production values
   ```

4. **SSL Certificate (Let's Encrypt)**
   ```bash
   # Setup Nginx with Let's Encrypt
   # Use certbot Docker image or manual setup
   ```

5. **Run Application**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

6. **Database Migration**
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

7. **Create Admin User**
   ```bash
   docker-compose exec backend python scripts/create_admin.py
   ```

### Backup Strategy
- **Database Backup**: Daily at 2:00 AM (cron job)
- **File Backup**: Weekly (uploaded receipts, slips)
- **Retention**: 30 days

### Monitoring (Optional)
- **Application Logs**: Docker logs
- **Error Tracking**: Sentry (optional)
- **Uptime Monitoring**: UptimeRobot (optional)

---

## Additional Features & Improvements

### เพิ่มเติมจากความต้องการเดิม

1. **PWA (Progressive Web App)**
   - ติดตั้ง app บนหน้าจอโทรศัพท์ได้
   - ทำงาน offline ได้บางส่วน
   - รับ push notifications

2. **Activity Logs**
   - บันทึกทุก action ที่สำคัญ (check-in, check-out, etc.)
   - Audit trail สำหรับ admin

3. **Room Transfer History**
   - ประวัติการย้ายห้อง
   - เหตุผลในการย้าย

4. **Dashboard Analytics**
   - สรุปยอดวันนี้แบบรวดเร็ว
   - Occupancy rate real-time
   - Revenue today

5. **Multi-Hotel Support (Future)**
   - โครงสร้างฐานข้อมูลรองรับ multi-tenant
   - ตอนนี้ implement แบบ single hotel ก่อน

6. **Export Reports**
   - Export to Excel
   - Export to PDF

7. **Guest Feedback**
   - QR code สำหรับให้ feedback
   - Rating system

8. **Inventory Management (Future Phase)**
   - จัดการสต๊อกสินค้า
   - Alert เมื่อสินค้าใกล้หมด

---

## เอกสารประกอบการพัฒนา

### Files to Create

1. **ARCHITECTURE.md**
   - System architecture details
   - Technology choices explanation
   - Design patterns used

2. **API_CONVENTIONS.md**
   - API naming conventions
   - Response format standards
   - Error code definitions

3. **DEVELOPMENT.md**
   - Setup instructions
   - Development workflow
   - Coding standards
   - Git workflow

4. **DATABASE_SCHEMA.md**
   - Detailed table schemas
   - Relationships
   - Indexes
   - Migration strategy

5. **WEBSOCKET_PROTOCOL.md**
   - WebSocket events documentation
   - Message formats
   - Connection handling

6. **DEPLOYMENT.md**
   - Step-by-step deployment guide
   - Environment variables
   - Troubleshooting

7. **USER_MANUAL.md** (Thai)
   - คู่มือการใช้งานสำหรับผู้ใช้
   - Screenshot แต่ละฟีเจอร์

---

## Project File Structure

```
FlyingHotelApp/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── v1/
│   │   │   │   ├── endpoints/
│   │   │   │   │   ├── auth.py
│   │   │   │   │   ├── users.py
│   │   │   │   │   ├── rooms.py
│   │   │   │   │   ├── dashboard.py
│   │   │   │   │   ├── check_ins.py
│   │   │   │   │   ├── bookings.py
│   │   │   │   │   ├── housekeeping.py
│   │   │   │   │   ├── maintenance.py
│   │   │   │   │   ├── products.py
│   │   │   │   │   ├── orders.py
│   │   │   │   │   ├── customers.py
│   │   │   │   │   ├── reports.py
│   │   │   │   │   └── settings.py
│   │   │   │   ├── websocket.py
│   │   │   │   └── router.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── dependencies.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── room.py
│   │   │   ├── customer.py
│   │   │   ├── booking.py
│   │   │   ├── check_in.py
│   │   │   ├── order.py
│   │   │   ├── housekeeping.py
│   │   │   ├── maintenance.py
│   │   │   └── ...
│   │   ├── schemas/
│   │   │   ├── user.py
│   │   │   ├── room.py
│   │   │   └── ...
│   │   ├── services/
│   │   │   ├── auth_service.py
│   │   │   ├── room_service.py
│   │   │   ├── check_in_service.py
│   │   │   ├── booking_service.py
│   │   │   ├── telegram_service.py
│   │   │   ├── pdf_service.py
│   │   │   └── ...
│   │   ├── tasks/
│   │   │   ├── celery_app.py
│   │   │   ├── booking_tasks.py
│   │   │   ├── notification_tasks.py
│   │   │   └── report_tasks.py
│   │   ├── db/
│   │   │   ├── base.py
│   │   │   └── session.py
│   │   └── main.py
│   ├── alembic/
│   │   └── versions/
│   ├── tests/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── pytest.ini
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   └── client.ts
│   │   ├── components/
│   │   │   ├── common/
│   │   │   ├── room/
│   │   │   │   └── RoomCard.vue
│   │   │   ├── dashboard/
│   │   │   ├── check-in/
│   │   │   └── ...
│   │   ├── views/
│   │   │   ├── LoginView.vue
│   │   │   ├── DashboardView.vue
│   │   │   ├── RoomManagementView.vue
│   │   │   ├── BookingView.vue
│   │   │   ├── HousekeepingView.vue
│   │   │   ├── MaintenanceView.vue
│   │   │   ├── ReportsView.vue
│   │   │   ├── SettingsView.vue
│   │   │   └── GuestOrderView.vue
│   │   ├── stores/
│   │   │   ├── auth.ts
│   │   │   ├── dashboard.ts
│   │   │   ├── notification.ts
│   │   │   └── ...
│   │   ├── router/
│   │   │   └── index.ts
│   │   ├── composables/
│   │   │   ├── useWebSocket.ts
│   │   │   └── useNotification.ts
│   │   ├── utils/
│   │   ├── types/
│   │   ├── assets/
│   │   ├── App.vue
│   │   └── main.ts
│   ├── public/
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── Dockerfile
├── nginx/
│   ├── nginx.conf
│   └── Dockerfile
├── docs/
│   ├── PRD.md (this file)
│   ├── ARCHITECTURE.md
│   ├── API_CONVENTIONS.md
│   ├── DEVELOPMENT.md
│   ├── DATABASE_SCHEMA.md
│   ├── WEBSOCKET_PROTOCOL.md
│   ├── DEPLOYMENT.md
│   └── USER_MANUAL.md
├── scripts/
│   ├── create_admin.py
│   └── seed_data.py
├── docker-compose.yml
├── docker-compose.prod.yml
├── .env.example
├── .gitignore
├── README.md
└── REQ.md
```

---

## คำแนะนำในการพัฒนา

### Do's
1. ✅ ทดสอบทุก phase ให้ผ่าน 100% ก่อนไป phase ต่อไป
2. ✅ Commit บ่อยๆ (atomic commits)
3. ✅ เขียน docstring/comments ให้ชัดเจน
4. ✅ ใช้ TypeScript/Pydantic เพื่อ type safety
5. ✅ Handle errors อย่างสมบูรณ์
6. ✅ Test บน mobile/tablet จริงๆ ไม่ใช่แค่ browser responsive mode
7. ✅ ใช้ environment variables สำหรับ config ทั้งหมด

### Don'ts
1. ❌ อย่า hardcode ค่าใดๆ
2. ❌ อย่ารวม phase ต่างๆ เข้าด้วยกัน
3. ❌ อย่า skip การทดสอบ
4. ❌ อย่าใช้ SQL queries แบบ raw (ใช้ ORM)
5. ❌ อย่าเก็บ sensitive data ใน git (passwords, tokens, etc.)

### Best Practices
1. **Database Migrations**: Always use Alembic, never modify database manually
2. **API Versioning**: Always use `/api/v1/` prefix
3. **Error Responses**: Consistent error format
   ```json
   {
     "detail": "Error message in Thai",
     "error_code": "ROOM_NOT_FOUND"
   }
   ```
4. **WebSocket Messages**: Consistent message format
   ```json
   {
     "event": "room_status_changed",
     "data": {...},
     "timestamp": "2024-01-15T10:30:00"
   }
   ```
5. **Component Naming**: Use PascalCase for Vue components
6. **File Naming**: Use snake_case for Python, kebab-case for Vue files

---

## สรุป

โปรเจ็ค FlyingHotelApp เป็นระบบบริหารโรงแรมที่ออกแบบมาเพื่อความง่ายในการใช้งาน โดยมีจุดเด่นคือ:

1. **UI/UX ที่เข้าใจง่าย**: เด็กมัธยมต้นใช้ได้
2. **Real-time Updates**: ข้อมูลอัปเดตทันที
3. **Mobile-First**: ใช้งานบนมือถือ/แท็บเล็ตได้ดี
4. **Telegram Integration**: แจ้งเตือนผ่าน Telegram
5. **รองรับการพักแบบชั่วคราว**: ฟีเจอร์พิเศษที่คู่แข่งไม่มี

การพัฒนาแบ่งเป็น **9 phases** ใช้เวลาประมาณ **5-6 สัปดาห์** โดยแต่ละ phase จะทดสอบให้ผ่าน 100% ก่อนไปต่อ

Technology stack ที่เลือกใช้เป็น modern stack ที่ stable, performant และมี community support ดี:
- **Backend**: FastAPI (Python)
- **Frontend**: Vue 3 + TypeScript
- **Database**: MySQL
- **Infra**: Docker

ระบบนี้พร้อมสำหรับการใช้งานจริง (production-ready) และสามารถขยายฟีเจอร์เพิ่มเติมได้ในอนาคต

---

**หมายเหตุ**: เอกสารนี้เป็น living document ที่สามารถปรับปรุงเพิ่มเติมได้ตลอดระหว่างการพัฒนา

**เวอร์ชัน**: 1.0
**วันที่สร้าง**: 12 ตุลาคม 2567
**ผู้จัดทำ**: FlyToADream Development Team
