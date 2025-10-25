# FlyingHotelApp - Digital Ocean Deployment Guide

คู่มือการติดตั้งระบบ FlyingHotelApp บน Digital Ocean Droplet

---

## 📋 ข้อกำหนดเบื้องต้น

### Server Requirements
- **Droplet**: Digital Ocean Droplet 2GB RAM ขึ้นไป
- **OS**: Ubuntu 22.04 LTS
- **Storage**: อย่างน้อย 25GB
- **Network**: Static IP address

### Software Requirements
- Docker Engine
- Docker Compose v2+
- Git
- Nginx

---

## 🚀 ขั้นตอนการติดตั้ง

### STEP 1: เตรียม Droplet

1. สร้าง Droplet: Ubuntu 22.04 LTS, 2GB RAM, Singapore region
2. เชื่อมต่อ SSH: `ssh root@YOUR_SERVER_IP`

### STEP 2: ติดตั้ง Docker

```bash
# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Verify
docker --version
docker compose version
```

### STEP 3: Clone Repository

```bash
cd /opt
git clone https://github.com/YOUR_USERNAME/FlyingHotelApp.git
cd FlyingHotelApp
```

### STEP 4: ตั้งค่า Environment

```bash
cp .env.example .env
nano .env
```

แก้ไข:
```env
MYSQL_ROOT_PASSWORD=YOUR_STRONG_PASSWORD
MYSQL_PASSWORD=YOUR_DB_PASSWORD
SECRET_KEY=YOUR_SECRET_KEY
ENVIRONMENT=production
```

สร้าง SECRET_KEY:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### STEP 5: ติดตั้ง Nginx

```bash
apt install -y nginx

# Create config
cat > /etc/nginx/sites-available/flyinghotel << 'NGINX'
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
NGINX

# Enable site
ln -s /etc/nginx/sites-available/flyinghotel /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

### STEP 6: Start Services

```bash
cd /opt/FlyingHotelApp
docker compose up -d
sleep 30  # Wait for MySQL
```

### STEP 7: Database Setup

```bash
# Run migrations
docker compose exec backend alembic upgrade head

# Create admin user
docker compose exec backend python3 << 'PYTHON'
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.user import User
from app.core.security import get_password_hash
import os

async def create_admin():
    db_url = os.getenv('DATABASE_URL', 'mysql+aiomysql://flyinghotel_user:flyinghotel_pass@mysql:3306/flyinghotel')
    engine = create_async_engine(db_url)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as db:
        admin = User(
            username='admin',
            full_name='System Admin',
            email='admin@flyinghotel.com',
            hashed_password=get_password_hash('admin123'),
            role='ADMIN',
            is_active=True
        )
        db.add(admin)
        await db.commit()
        print('Admin user created!')
        await engine.dispose()

asyncio.run(create_admin())
PYTHON
```

### STEP 8: Seed Data

```bash
docker compose exec mysql mysql -u flyinghotel_user -pflyinghotel_pass flyinghotel << 'SQL'
-- Room Types
INSERT INTO room_types (name, description, base_price_per_night, base_price_per_3hours, max_guests, amenities, created_at, updated_at) VALUES
('Standard', 'ห้องพักมาตรฐาน', 800.00, 300.00, 2, 'เตียง, แอร์, TV, WiFi', NOW(), NOW()),
('Deluxe', 'ห้องพักดีลักซ์', 1200.00, 400.00, 2, 'เตียงใหญ่, แอร์, Smart TV, WiFi, ตู้เย็น', NOW(), NOW()),
('VIP', 'ห้องพัก VIP', 2000.00, 600.00, 4, 'เตียงคิงไซซ์, แอร์, Smart TV 55", WiFi, ตู้เย็น, อ่างอาบน้ำ', NOW(), NOW());

-- Rooms
INSERT INTO rooms (room_number, room_type_id, floor, status, created_at, updated_at) VALUES
('101', 1, 1, 'available', NOW(), NOW()),
('102', 1, 1, 'available', NOW(), NOW()),
('103', 1, 1, 'available', NOW(), NOW()),
('104', 1, 1, 'available', NOW(), NOW()),
('105', 1, 1, 'available', NOW(), NOW()),
('201', 2, 2, 'available', NOW(), NOW()),
('202', 2, 2, 'available', NOW(), NOW()),
('203', 2, 2, 'available', NOW(), NOW()),
('204', 2, 2, 'available', NOW(), NOW()),
('205', 2, 2, 'available', NOW(), NOW()),
('301', 3, 3, 'available', NOW(), NOW()),
('302', 3, 3, 'available', NOW(), NOW()),
('303', 3, 3, 'available', NOW(), NOW());
SQL
```

### STEP 9: Firewall

```bash
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 22/tcp
ufw enable
```

---

## 🔄 Database Migration (การอัพเดทครั้งที่ 2)

### ถ้ามี Database เก่า:

**Option 1: เริ่มใหม่ทั้งหมด**
```bash
docker compose down
docker volume rm flyinghotel_mysql_data
docker compose up -d
sleep 30
docker compose exec backend alembic upgrade head
# ทำ STEP 7-8 ใหม่
```

**Option 2: Migrate Database เดิม**
```bash
# Backup ก่อน
docker compose exec mysql mysqldump -u flyinghotel_user -p flyinghotel > backup.sql

# Run migration
docker compose exec backend alembic upgrade head
```

---

## 📊 การตรวจสอบ

```bash
# Check services
docker compose ps

# Check logs
docker compose logs -f

# Test
curl http://localhost:8000/api/docs
```

---

## 🔧 Maintenance

### Update Code
```bash
cd /opt/FlyingHotelApp
git pull
docker compose build
docker compose up -d
```

### Backup
```bash
docker compose exec mysql mysqldump -u flyinghotel_user -p flyinghotel > backup.sql
```

### Restart
```bash
docker compose restart
```

---

## ⚠️ Troubleshooting

### Services ไม่ทำงาน
```bash
docker compose down
docker compose up -d
docker compose logs
```

### MySQL Error
```bash
docker compose logs mysql
# Check .env passwords
```

---

## 📝 Default Login

- Username: `admin`
- Password: `admin123`
- **⚠️ เปลี่ยนรหัสผ่านทันที!**

---

## ✅ Checklist

- [ ] Docker installed
- [ ] Services running
- [ ] Database migrated
- [ ] Admin user created
- [ ] Seed data loaded
- [ ] Nginx configured
- [ ] Firewall enabled
- [ ] Can login to system
- [ ] Changed admin password

