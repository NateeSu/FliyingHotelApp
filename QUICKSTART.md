# FlyingHotelApp - Quick Start Guide

## วิธีติดตั้งแบบรวดเร็ว (สำหรับ Digital Ocean)

### 1. เชื่อมต่อ Server
```bash
ssh root@YOUR_SERVER_IP
```

### 2. Clone และติดตั้งอัตโนมัติ
```bash
cd /opt
git clone https://github.com/YOUR_USERNAME/FlyingHotelApp.git
cd FlyingHotelApp
chmod +x setup_production.sh
./setup_production.sh
```

สคริปต์จะทำทุกอย่างอัตโนมัติ:
- ติดตั้ง Docker
- Build containers
- Setup database
- สร้าง admin user
- เพิ่มข้อมูลเริ่มต้น

### 3. ตั้งค่า Nginx (ทำเองครั้งเดียว)

```bash
# สร้าง config
nano /etc/nginx/sites-available/flyinghotel
```

วาง config นี้:
```nginx
server {
    listen 80;
    server_name YOUR_SERVER_IP;
    client_max_body_size 100M;
    
    location / {
        proxy_pass http://localhost:5173;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
    
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /ws/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
    }
}
```

Enable และ reload:
```bash
ln -s /etc/nginx/sites-available/flyinghotel /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

### 4. เข้าใช้งาน

เปิดเบราว์เซอร์:
```
http://YOUR_SERVER_IP
```

Login:
- Username: `admin`
- Password: `admin123`

**⚠️ เปลี่ยนรหัสผ่านทันที!**

---

## การอัพเดท (ครั้งที่ 2 เป็นต้นไป)

### ถ้าต้องการเริ่มใหม่ทั้งหมด:
```bash
cd /opt/FlyingHotelApp
docker compose down
docker volume rm flyinghotel_mysql_data
git pull
./setup_production.sh
```

### ถ้าต้องการเก็บข้อมูลเดิม:
```bash
cd /opt/FlyingHotelApp

# Backup ก่อน
docker compose exec mysql mysqldump -u flyinghotel_user -pflyinghotel_pass flyinghotel > backup.sql

# Pull code ใหม่
git pull

# Rebuild
docker compose build
docker compose up -d

# Migrate database
docker compose exec backend alembic upgrade head
```

---

## คำสั่งที่ใช้บ่อย

```bash
# ดู status
docker compose ps

# ดู logs
docker compose logs -f

# Restart
docker compose restart

# Stop
docker compose down

# Start
docker compose up -d
```

---

## Troubleshooting

### Services ไม่ทำงาน
```bash
docker compose down
docker compose up -d
docker compose logs
```

### ลืมรหัสผ่าน admin
```bash
cd /opt/FlyingHotelApp
docker compose exec -T backend python3 << 'PYTHON'
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, update
from app.models.user import User
from app.core.security import get_password_hash

async def reset_admin():
    engine = create_async_engine('mysql+aiomysql://flyinghotel_user:flyinghotel_pass@mysql:3306/flyinghotel')
    async_session = sessionmaker(engine, class_=AsyncSession)
    
    async with async_session() as db:
        await db.execute(
            update(User).where(User.username == 'admin').values(
                hashed_password=get_password_hash('admin123')
            )
        )
        await db.commit()
        print('Password reset to: admin123')
    await engine.dispose()

asyncio.run(reset_admin())
PYTHON
```

---

## ข้อมูลเพิ่มเติม

ดูรายละเอียดเพิ่มเติมใน:
- `DEPLOYMENT.md` - คู่มือการติดตั้งแบบละเอียด
- `README.md` - ข้อมูลโครงการ
- `PRD.md` - เอกสารความต้องการระบบ

