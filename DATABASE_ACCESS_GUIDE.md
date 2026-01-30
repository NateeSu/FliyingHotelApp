# วิธีดู Database ใน Docker - คู่มือฉบับสมบูรณ์

มีหลายวิธีในการเข้าถึงและดูข้อมูลใน MySQL Database ที่รันอยู่ใน Docker:

---

## 🌐 วิธีที่ 1: Adminer (Web-based GUI) - **แนะนำสำหรับมือใหม่**

Adminer เป็น Web UI สำหรับจัดการ Database แบบ GUI ใช้งานง่ายที่สุด

### ขั้นตอน:

1. **เปิดเบราว์เซอร์** ไปที่:
   ```
   http://localhost:8080
   ```

2. **Login ด้วยข้อมูล:**
   ```
   System:   MySQL
   Server:   mysql
   Username: flyinghotel_user
   Password: flyinghotel_pass
   Database: flyinghotel
   ```

3. **เริ่มใช้งาน:**
   - คลิกชื่อตารางด้านซ้ายเพื่อดูข้อมูล
   - ใช้ SQL command ได้ที่เมนู "SQL command"
   - Export/Import ข้อมูลได้ที่เมนู "Export" / "Import"

### ตัวอย่างการใช้งาน:

```sql
-- ดูข้อมูลผู้ใช้ทั้งหมด
SELECT * FROM users;

-- ดูห้องว่างทั้งหมด
SELECT * FROM rooms WHERE status = 'AVAILABLE';

-- ดูการ check-in ที่ยังไม่ check-out
SELECT * FROM check_ins WHERE status = 'CHECKED_IN';

-- นับจำนวนห้องแต่ละประเภท
SELECT room_type_id, COUNT(*) as count
FROM rooms
GROUP BY room_type_id;
```

---

## 💻 วิธีที่ 2: MySQL CLI ผ่าน Docker Exec - **แนะนำสำหรับผู้ใช้ขั้นสูง**

เข้าถึง MySQL command line ได้โดยตรงผ่าน Docker container

### ขั้นตอน:

```bash
# เข้าสู่ MySQL container
docker-compose exec mysql mysql -u flyinghotel_user -pflyinghotel_pass flyinghotel

# หรือใช้ root user (ถ้าต้องการสิทธิ์เต็ม)
docker-compose exec mysql mysql -u root -prootpassword
```

### คำสั่งพื้นฐาน MySQL:

```sql
-- แสดงฐานข้อมูลทั้งหมด
SHOW DATABASES;

-- เลือกใช้งานฐานข้อมูล
USE flyinghotel;

-- แสดงตารางทั้งหมด
SHOW TABLES;

-- ดูโครงสร้างตาราง
DESCRIBE users;
DESC rooms;

-- ดูข้อมูลในตาราง
SELECT * FROM users;
SELECT * FROM rooms LIMIT 10;

-- นับจำนวน records
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM rooms WHERE status = 'AVAILABLE';

-- ออกจาก MySQL
EXIT;
```

### ตัวอย่าง Query ที่มีประโยชน์:

```sql
-- ดูห้องทั้งหมดพร้อมประเภทห้อง
SELECT r.id, r.room_number, rt.name as room_type, r.status, r.floor
FROM rooms r
LEFT JOIN room_types rt ON r.room_type_id = rt.id
ORDER BY r.room_number;

-- ดู check-ins ที่กำลังพักอยู่
SELECT ci.id, r.room_number, c.full_name as customer, ci.check_in_time, ci.stay_type
FROM check_ins ci
LEFT JOIN rooms r ON ci.room_id = r.id
LEFT JOIN customers c ON ci.customer_id = c.id
WHERE ci.status = 'CHECKED_IN';

-- ดูอัตราห้องทั้งหมด
SELECT rt.name, rr.stay_type, rr.rate, rr.effective_from
FROM room_rates rr
LEFT JOIN room_types rt ON rr.room_type_id = rt.id
WHERE rr.is_active = 1
ORDER BY rt.name, rr.stay_type;

-- ดูผู้ใช้งานทั้งหมด
SELECT id, username, full_name, role, is_active
FROM users
ORDER BY role, username;
```

---

## 🔧 วิธีที่ 3: MySQL Workbench / DBeaver / TablePlus (External Tools)

เชื่อมต่อด้วย Database GUI Tools ภายนอก

### ข้อมูลการเชื่อมต่อ:

```
Host:     localhost  (หรือ 127.0.0.1)
Port:     3306
Database: flyinghotel
Username: flyinghotel_user
Password: flyinghotel_pass
```

### Tools ที่แนะนำ:

1. **MySQL Workbench** (Official MySQL GUI)
   - Download: https://dev.mysql.com/downloads/workbench/

2. **DBeaver** (Universal Database Tool)
   - Download: https://dbeaver.io/download/

3. **TablePlus** (Modern, Lightweight)
   - Download: https://tableplus.com/

4. **HeidiSQL** (Windows)
   - Download: https://www.heidisql.com/

### ขั้นตอนการเชื่อมต่อ (MySQL Workbench):

1. เปิด MySQL Workbench
2. คลิก "+" เพื่อสร้าง New Connection
3. ใส่ข้อมูล:
   - Connection Name: Flying Hotel (localhost)
   - Hostname: localhost
   - Port: 3306
   - Username: flyinghotel_user
4. คลิก "Test Connection" แล้วใส่รหัสผ่าน: `flyinghotel_pass`
5. คลิก "OK" เพื่อบันทึก
6. Double-click connection เพื่อเชื่อมต่อ

---

## 🚀 วิธีที่ 4: FastAPI Swagger UI (ผ่าน API)

ดูข้อมูลผ่าน API endpoints พร้อมทดสอบ

### ขั้นตอน:

1. **เปิดเบราว์เซอร์** ไปที่:
   ```
   http://localhost:8000/docs
   ```

2. **Login เพื่อรับ Token:**
   - เลื่อนหา `POST /api/v1/auth/login`
   - คลิก "Try it out"
   - ใส่ข้อมูล:
     ```json
     {
       "username": "admin",
       "password": "admin123"
     }
     ```
   - คลิก "Execute"
   - Copy `access_token` จาก response

3. **Authorize:**
   - คลิกปุ่ม "Authorize" 🔓 ด้านบนขวา
   - ใส่ token ในช่อง "Value"
   - คลิก "Authorize"

4. **ทดสอบ API endpoints:**
   - `GET /api/v1/users` - ดูผู้ใช้ทั้งหมด
   - `GET /api/v1/rooms` - ดูห้องทั้งหมด
   - `GET /api/v1/room-types` - ดูประเภทห้อง
   - `GET /api/v1/products` - ดูสินค้า
   - `GET /api/v1/dashboard/rooms` - ดูสถานะห้องบน Dashboard

---

## 📊 วิธีที่ 5: ใช้ Python Script เข้าถึง Database โดยตรง

สร้าง script เพื่อดูข้อมูลแบบ custom

### สร้างไฟล์: `backend/scripts/query_database.py`

```python
"""
Quick database query script
Usage: docker-compose exec backend python scripts/query_database.py
"""
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, func
from app.db.session import AsyncSessionLocal
from app.models import User, Room, RoomType, CheckIn, Customer

async def main():
    async with AsyncSessionLocal() as db:
        print("=" * 60)
        print("FlyingHotelApp - Database Quick View")
        print("=" * 60)

        # Count users by role
        print("\n👥 Users by Role:")
        stmt = select(User.role, func.count(User.id)).group_by(User.role)
        result = await db.execute(stmt)
        for role, count in result:
            print(f"   {role.value}: {count}")

        # Count rooms by status
        print("\n🏠 Rooms by Status:")
        stmt = select(Room.status, func.count(Room.id)).group_by(Room.status)
        result = await db.execute(stmt)
        for status, count in result:
            print(f"   {status.value}: {count}")

        # Show room types
        print("\n🏨 Room Types:")
        stmt = select(RoomType)
        result = await db.execute(stmt)
        room_types = result.scalars().all()
        for rt in room_types:
            print(f"   {rt.name}: {rt.max_guests} guests, {rt.room_size_sqm}㎡")

        # Current check-ins
        print("\n✅ Active Check-ins:")
        stmt = select(func.count(CheckIn.id)).where(CheckIn.status == 'CHECKED_IN')
        result = await db.execute(stmt)
        count = result.scalar()
        print(f"   Total: {count}")

        # Total customers
        print("\n👤 Total Customers:")
        stmt = select(func.count(Customer.id))
        result = await db.execute(stmt)
        count = result.scalar()
        print(f"   Total: {count}")

        print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
```

### รันคำสั่ง:

```bash
docker-compose exec backend python scripts/query_database.py
```

---

## 🔍 คำสั่งที่มีประโยชน์

### ตรวจสอบสถานะ Containers:

```bash
# ดู containers ที่กำลังรัน
docker-compose ps

# ดู logs ของ MySQL
docker-compose logs mysql

# ดู logs แบบ real-time
docker-compose logs -f mysql
```

### Backup & Restore Database:

```bash
# Backup database
docker-compose exec mysql mysqldump -u flyinghotel_user -pflyinghotel_pass flyinghotel > backup_$(date +%Y%m%d).sql

# Restore database
docker-compose exec -T mysql mysql -u flyinghotel_user -pflyinghotel_pass flyinghotel < backup_20260121.sql
```

### เข้าไปใน MySQL Container:

```bash
# เข้าสู่ shell ของ container
docker-compose exec mysql bash

# จากนั้นสามารถรันคำสั่ง mysql
mysql -u root -p
# ใส่รหัสผ่าน: rootpassword
```

---

## 📋 ตารางสำคัญในระบบ

| ตาราง | คำอธิบาย | จำนวน Records (หลัง seed) |
|-------|----------|---------------------------|
| `users` | ผู้ใช้งานระบบ | 6 |
| `room_types` | ประเภทห้อง | 4 |
| `rooms` | ห้องพัก | 30 |
| `room_rates` | อัตราค่าห้อง | 8 |
| `products` | สินค้าและบริการ | 14 |
| `system_settings` | การตั้งค่าระบบ | 11 |
| `customers` | ข้อมูลลูกค้า | 0 (เริ่มต้น) |
| `check_ins` | การเช็คอิน | 0 (เริ่มต้น) |
| `bookings` | การจอง | 0 (เริ่มต้น) |
| `housekeeping_tasks` | งานแม่บ้าน | 0 (เริ่มต้น) |
| `maintenance_tasks` | งานซ่อมบำรุง | 0 (เริ่มต้น) |
| `orders` | คำสั่งซื้อ | 0 (เริ่มต้น) |
| `payments` | การชำระเงิน | 0 (เริ่มต้น) |
| `notifications` | การแจ้งเตือน | 0 (เริ่มต้น) |

---

## ⚠️ Troubleshooting

### Problem: ไม่สามารถเข้า Adminer ที่ localhost:8080

**Solution:**
```bash
# ตรวจสอบว่า Adminer ทำงาน
docker-compose ps adminer

# ถ้าไม่ทำงาน ให้ start
docker-compose up -d adminer

# ดู logs เพื่อหาสาเหตุ
docker-compose logs adminer
```

### Problem: Connection refused เมื่อเชื่อมต่อ MySQL

**Solution:**
```bash
# ตรวจสอบว่า MySQL ทำงาน
docker-compose ps mysql

# รอให้ MySQL start เสร็จ (อาจใช้เวลา 10-30 วินาที)
docker-compose logs -f mysql

# ดูว่า healthcheck ผ่านหรือยัง
docker inspect flyinghotel_mysql | grep -A 10 Health
```

### Problem: Access denied for user

**Solution:**
```bash
# ตรวจสอบ environment variables
docker-compose exec mysql env | grep MYSQL

# ถ้าต้องการ reset password
docker-compose down
docker volume rm flyinghotel_mysql_data  # ⚠️ จะลบข้อมูลทั้งหมด!
docker-compose up -d mysql
```

---

## 🎯 Best Practices

1. **Development**: ใช้ Adminer สำหรับดูข้อมูลและทดสอบ query
2. **Production**: ห้ามเปิด Adminer บน production server
3. **Backup**: สำรองข้อมูลก่อนทำการแก้ไขที่สำคัญ
4. **Security**: เปลี่ยนรหัสผ่าน default ก่อนใช้งานจริง
5. **Performance**: ใช้ indexes บนคอลัมน์ที่ query บ่อยๆ

---

**สร้างโดย**: Claude Code
**วันที่**: 2026-01-21
**เวอร์ชัน**: 1.0
