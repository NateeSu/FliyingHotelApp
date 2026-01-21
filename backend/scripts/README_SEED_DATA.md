# Database Seed Data - คู่มือการใช้งาน

## ภาพรวม

ไฟล์นี้ใช้สำหรับเพิ่มข้อมูลเริ่มต้นเข้าสู่ฐานข้อมูล เหมาะสำหรับ:
- การพัฒนาระบบ (Development)
- การทดสอบระบบ (Testing)
- การสาธิตระบบ (Demo)

## ข้อมูลที่จะถูกเพิ่มเข้าระบบ

### 1. Users (ผู้ใช้งานระบบ) - 6 บัญชี

| Username | Password | Role | ชื่อ-นามสกุล |
|----------|----------|------|--------------|
| admin | admin123 | ADMIN | ผู้ดูแลระบบ |
| reception1 | reception123 | RECEPTION | พนักงานต้อนรับ 1 |
| reception2 | reception123 | RECEPTION | พนักงานต้อนรับ 2 |
| housekeeping1 | house123 | HOUSEKEEPING | พนักงานทำความสะอาด 1 |
| housekeeping2 | house123 | HOUSEKEEPING | พนักงานทำความสะอาด 2 |
| maintenance1 | maint123 | MAINTENANCE | พนักงานซ่อมบำรุง |

⚠️ **IMPORTANT**: เปลี่ยนรหัสผ่านเหล่านี้ก่อนใช้งานจริง (Production)!

### 2. Room Types (ประเภทห้อง) - 4 ประเภท

| ประเภท | ขนาด (ตร.ม.) | จำนวนผู้พักสูงสุด | ประเภทเตียง |
|--------|--------------|-------------------|-------------|
| Standard | 25 | 2 | เตียงคู่ |
| Deluxe | 35 | 2 | เตียงควีนไซส์ |
| VIP | 45 | 3 | เตียงคิงไซส์ |
| Suite | 60 | 4 | เตียงคิงไซส์ + โซฟาเบด |

### 3. Rooms (ห้องพัก) - 30 ห้อง

**ชั้น 1 (101-110)**:
- 6 ห้อง Standard (101-106)
- 4 ห้อง Deluxe (107-110)

**ชั้น 2 (201-210)**:
- 4 ห้อง Standard (201-204)
- 4 ห้อง Deluxe (205-208)
- 2 ห้อง VIP (209-210)

**ชั้น 3 (301-310)**:
- 2 ห้อง Deluxe (301-302)
- 6 ห้อง VIP (303-308)
- 2 ห้อง Suite (309-310)

### 4. Room Rates (ราคาห้อง)

| ประเภทห้อง | ค้างคืน (OVERNIGHT) | ชั่วคราว (TEMPORARY) |
|------------|---------------------|----------------------|
| Standard | ฿800 | ฿300 |
| Deluxe | ฿1,200 | ฿450 |
| VIP | ฿1,800 | ฿650 |
| Suite | ฿2,500 | ฿900 |

### 5. Products (สินค้าและบริการ) - 14 รายการ

**Room Amenities (สิ่งอำนวยความสะดวก)**:
- ผ้าเช็ดตัวเพิ่ม (฿50)
- ผ้าห่มเพิ่ม (฿100)
- หมอนเพิ่ม (฿80)
- ชุดอาบน้ำ (฿150)

**Food & Beverages (อาหารและเครื่องดื่ม)**:
- น้ำดื่ม (฿15-25)
- กาแฟสำเร็จรูป (฿30)
- ชาเขียว (฿25)
- ขนมขบเคี้ยว (฿35)
- มาม่า (฿20)
- ไข่ต้มกึ่งสุก (฿25)
- โค้ก/เป๊ปซี่/สไปรท์ (฿20)

### 6. System Settings (การตั้งค่าระบบ) - 11 รายการ

| Key | Value | Description |
|-----|-------|-------------|
| temporary_stay_duration_hours | 3 | ระยะเวลาการพักชั่วคราว (ชั่วโมง) |
| overnight_checkin_time | 14:00 | เวลาเช็คอินมาตรฐานสำหรับค้างคืน |
| overnight_checkout_time | 12:00 | เวลาเช็คเอาท์มาตรฐานสำหรับค้างคืน |
| overtime_charge_rate | 100 | อัตราค่าเกินเวลาต่อชั่วโมง (บาท) |
| booking_deposit_percentage | 30 | เปอร์เซ็นต์เงินมัดจำการจอง (%) |
| hotel_name | Flying Hotel | ชื่อโรงแรม |
| hotel_address | ... | ที่อยู่โรงแรม |
| hotel_phone | 02-123-4567 | เบอร์โทรโรงแรม |
| hotel_email | info@flyinghotel.com | อีเมลโรงแรม |

## วิธีการใช้งาน

### วิธีที่ 1: รันผ่าน Docker (แนะนำ)

```bash
# 1. ตรวจสอบว่า Docker containers กำลังทำงาน
docker-compose ps

# 2. รัน seed script
docker-compose exec backend python scripts/seed_data.py

# 3. ตรวจสอบผลลัพธ์
# Script จะแสดงสรุปข้อมูลที่ถูกเพิ่มเข้าระบบ
```

### วิธีที่ 2: รันโดยตรง (สำหรับ Local Development)

```bash
# 1. เข้าสู่ backend directory
cd backend

# 2. Activate virtual environment (ถ้ามี)
source venv/bin/activate  # Linux/Mac
# หรือ
venv\Scripts\activate  # Windows

# 3. รัน seed script
python scripts/seed_data.py
```

### วิธีที่ 3: ลบข้อมูลเดิมและเพิ่มใหม่ทั้งหมด

⚠️ **WARNING**: วิธีนี้จะลบข้อมูลทั้งหมดในฐานข้อมูล!

```python
# แก้ไขในไฟล์ seed_data.py (บรรทัด 638)
clear_data = True  # เปลี่ยนจาก False เป็น True

# จากนั้นรัน script
docker-compose exec backend python scripts/seed_data.py
```

## การตรวจสอบว่าข้อมูลถูก Import สำเร็จ

### 1. ผ่าน Adminer (Database GUI)

```bash
# เปิดเบราว์เซอร์ไปที่
http://localhost:8080

# Login ด้วยข้อมูล:
Server: mysql
Username: flyinghotel_user
Password: flyinghotel_password
Database: flyinghotel_db

# จากนั้นตรวจสอบตาราง:
- users (ควรมี 6 records)
- room_types (ควรมี 4 records)
- rooms (ควรมี 30 records)
- room_rates (ควรมี 8 records)
- products (ควรมี 14 records)
- system_settings (ควรมี 11 records)
```

### 2. ผ่าน API (Swagger UI)

```bash
# เปิดเบราว์เซอร์ไปที่
http://localhost:8000/docs

# 1. Login ด้วยบัญชี admin
POST /api/v1/auth/login
{
  "username": "admin",
  "password": "admin123"
}

# 2. Copy access_token จาก response

# 3. คลิก "Authorize" ด้านบนขวา และใส่ token

# 4. ทดสอบ API endpoints:
GET /api/v1/room-types  # ควรได้ 4 room types
GET /api/v1/rooms       # ควรได้ 30 rooms
GET /api/v1/products    # ควรได้ 14 products
```

### 3. ผ่าน MySQL CLI

```bash
# เข้าสู่ MySQL container
docker-compose exec mysql mysql -u flyinghotel_user -pflyinghotel_password flyinghotel_db

# รัน SQL queries
SELECT COUNT(*) FROM users;          -- ควรได้ 6
SELECT COUNT(*) FROM room_types;     -- ควรได้ 4
SELECT COUNT(*) FROM rooms;          -- ควรได้ 30
SELECT COUNT(*) FROM room_rates;     -- ควรได้ 8
SELECT COUNT(*) FROM products;       -- ควรได้ 14
SELECT COUNT(*) FROM system_settings; -- ควรได้ 11

# ออกจาก MySQL
exit;
```

## Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'app'"

**Solution**:
```bash
# ตรวจสอบว่ารันจาก directory ที่ถูกต้อง
cd backend
python scripts/seed_data.py
```

### Problem: "sqlalchemy.exc.IntegrityError: Duplicate entry"

**สาเหตุ**: ข้อมูลบางส่วนมีอยู่ในฐานข้อมูลแล้ว

**Solution**:
- Script จะ skip ข้อมูลที่มีอยู่แล้วโดยอัตโนมัติ
- ถ้าต้องการเริ่มต้นใหม่ทั้งหมด ให้ตั้งค่า `clear_data = True`

### Problem: "Connection refused" หรือ "Can't connect to MySQL server"

**Solution**:
```bash
# 1. ตรวจสอบว่า MySQL container ทำงาน
docker-compose ps

# 2. ถ้า MySQL ไม่ทำงาน ให้ start
docker-compose up -d mysql

# 3. รอสักครู่ให้ MySQL เริ่มต้นเสร็จ (ประมาณ 10-30 วินาที)
docker-compose logs -f mysql

# 4. ลองรัน seed script อีกครั้ง
```

## หมายเหตุสำคัญ

1. **Production Environment**:
   - เปลี่ยนรหัสผ่าน default ทั้งหมด
   - แก้ไขข้อมูล System Settings ให้ตรงกับข้อมูลจริง
   - ไม่ควรใช้ `clear_data = True` ใน production

2. **Development Environment**:
   - สามารถรัน script ซ้ำได้เรื่อยๆ
   - ข้อมูลที่มีอยู่แล้วจะถูก skip
   - ข้อมูลใหม่จะถูกเพิ่มเข้าไป

3. **Testing Environment**:
   - ควรใช้ `clear_data = True` เพื่อเริ่มต้นใหม่ทุกครั้ง
   - ทำให้การทดสอบมีความสม่ำเสมอ

## การปรับแต่งข้อมูล

หากต้องการเพิ่มหรือแก้ไขข้อมูล สามารถแก้ไขได้ที่:

- **Users**: บรรทัด 47-90 ในฟังก์ชัน `seed_users()`
- **Room Types**: บรรทัด 104-163 ในฟังก์ชัน `seed_room_types()`
- **Rooms**: บรรทัด 179-272 ในฟังก์ชัน `seed_rooms()`
- **Room Rates**: บรรทัด 278-332 ในฟังก์ชัน `seed_room_rates()`
- **Products**: บรรทัด 338-488 ในฟังก์ชัน `seed_products()`
- **System Settings**: บรรทัด 494-609 ในฟังก์ชัน `seed_system_settings()`

---

**Created by**: Claude Code
**Last Updated**: 2025-01-21
**Version**: 1.0
