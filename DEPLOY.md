# 🚀 คู่มือการติดตั้ง FlyingHotelApp บน Digital Ocean

คู่มือนี้จะแนะนำวิธีการติดตั้งและรันระบบ FlyingHotelApp บน Digital Ocean Droplet ด้วย Docker อย่างสมบูรณ์

---

## 📋 สิ่งที่ต้องเตรียม

### 1. Digital Ocean Droplet
- **ขนาดที่แนะนำ:** 2GB RAM, 1 CPU, 50GB SSD (Basic Plan $12/mo)
- **OS:** Ubuntu 22.04 LTS (64-bit)
- **Location:** เลือก datacenter ใกล้ประเทศไทยที่สุด (เช่น Singapore)

### 2. Domain Name (ถ้ามี)
- ตั้งค่า DNS A record ชี้ไปที่ IP ของ Droplet
- ถ้าไม่มี สามารถใช้ IP Address โดยตรงได้

### 3. SSH Key หรือ Password
- สำหรับเข้าถึง Droplet

---

## 🔧 ขั้นตอนที่ 1: สร้าง Droplet และเข้าสู่ระบบ

### 1.1 สร้าง Droplet บน Digital Ocean

1. เข้า [Digital Ocean Dashboard](https://cloud.digitalocean.com)
2. คลิก "Create" → "Droplets"
3. เลือก:
   - **Image:** Ubuntu 22.04 LTS x64
   - **Plan:** Basic ($12/mo - 2GB RAM / 1 CPU / 50GB SSD)
   - **Datacenter:** Singapore
   - **Authentication:** SSH Key (แนะนำ) หรือ Password
   - **Hostname:** flyinghotel-prod
4. คลิก "Create Droplet"

### 1.2 เชื่อมต่อกับ Droplet

```bash
# เปลี่ยน YOUR_DROPLET_IP เป็น IP ของ Droplet
ssh root@YOUR_DROPLET_IP
```

---

## 🛠️ ขั้นตอนที่ 2: ติดตั้ง Docker และ Docker Compose

### 2.1 อัปเดตระบบ

```bash
apt update && apt upgrade -y
```

### 2.2 ติดตั้ง Docker

```bash
# ติดตั้ง dependencies
apt install -y apt-transport-https ca-certificates curl software-properties-common

# เพิ่ม Docker GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# เพิ่ม Docker repository
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# ติดตั้ง Docker
apt update
apt install -y docker-ce docker-ce-cli containerd.io

# เปิดใช้งาน Docker
systemctl start docker
systemctl enable docker

# ตรวจสอบการติดตั้ง
docker --version
```

### 2.3 ติดตั้ง Docker Compose

```bash
# ติดตั้ง Docker Compose
curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# ให้สิทธิ์ execute
chmod +x /usr/local/bin/docker-compose

# ตรวจสอบการติดตั้ง
docker-compose --version
```

---

## 📦 ขั้นตอนที่ 3: Clone โปรเจกต์จาก GitHub

### 3.1 ติดตั้ง Git (ถ้ายังไม่มี)

```bash
apt install -y git
```

### 3.2 Clone Repository

```bash
# ไปที่ home directory
cd /root

# Clone โปรเจกต์ (เปลี่ยน URL เป็น repository ของคุณ)
git clone https://github.com/YOUR_USERNAME/FlyingHotelApp.git

# เข้าไปในโฟลเดอร์โปรเจกต์
cd FlyingHotelApp
```

---

## ⚙️ ขั้นตอนที่ 4: ตั้งค่า Environment Variables

### 4.1 สร้างไฟล์ .env

```bash
# Copy จากไฟล์ตัวอย่าง
cp .env.example .env

# แก้ไขไฟล์ .env
nano .env
```

### 4.2 แก้ไขค่าใน .env สำหรับ Production

```bash
# Database Configuration
MYSQL_ROOT_PASSWORD=<STRONG_PASSWORD_HERE>
MYSQL_DATABASE=flyinghotel
MYSQL_USER=flyinghotel_user
MYSQL_PASSWORD=<STRONG_PASSWORD_HERE>

# Backend Configuration
SECRET_KEY=<GENERATE_RANDOM_64_CHAR_STRING>
ENVIRONMENT=production
DATABASE_URL=mysql+aiomysql://flyinghotel_user:<MYSQL_PASSWORD>@mysql:3306/flyinghotel

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# Telegram Configuration (Optional)
TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN_IF_NEEDED
TELEGRAM_ADMIN_GROUP_ID=
TELEGRAM_RECEPTION_GROUP_ID=
TELEGRAM_HOUSEKEEPING_GROUP_ID=
TELEGRAM_MAINTENANCE_GROUP_ID=

# Frontend Configuration (เปลี่ยนเป็น IP หรือ Domain ของคุณ)
VITE_API_URL=http://YOUR_DROPLET_IP:8000
VITE_WS_URL=ws://YOUR_DROPLET_IP:8000

# JWT Configuration
JWT_SECRET_KEY=<GENERATE_RANDOM_64_CHAR_STRING>
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Upload Configuration
MAX_UPLOAD_SIZE=5242880
UPLOAD_DIR=/app/uploads

# Thai Timezone
TZ=Asia/Bangkok
```

**สำคัญ:** สร้าง SECRET_KEY และ JWT_SECRET_KEY ที่แข็งแกร่ง:

```bash
# วิธีสร้าง random string
openssl rand -hex 32
```

### 4.3 บันทึกและออกจาก nano
- กด `Ctrl + X`
- กด `Y` เพื่อยืนยัน
- กด `Enter`

---

## 🐳 ขั้นตอนที่ 5: แก้ไข Docker Compose สำหรับ Production

### 5.1 สร้างไฟล์ docker-compose.prod.yml

```bash
nano docker-compose.prod.yml
```

วางโค้ดนี้:

```yaml
services:
  # MySQL Database
  mysql:
    image: mysql:8.0
    container_name: flyinghotel_mysql
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: ${MYSQL_DATABASE}
      MYSQL_USER: ${MYSQL_USER}
      MYSQL_PASSWORD: ${MYSQL_PASSWORD}
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
    networks:
      - flyinghotel_network
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      timeout: 20s
      retries: 10

  # Redis Cache & Message Broker
  redis:
    image: redis:7-alpine
    container_name: flyinghotel_redis
    restart: always
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - flyinghotel_network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  # Adminer - Database Management UI
  adminer:
    image: adminer:latest
    container_name: flyinghotel_adminer
    restart: always
    ports:
      - "8080:8080"
    networks:
      - flyinghotel_network
    depends_on:
      - mysql
    environment:
      ADMINER_DEFAULT_SERVER: mysql

  # FastAPI Backend
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: flyinghotel_backend
    restart: always
    ports:
      - "8000:8000"
    volumes:
      - backend_uploads:/app/uploads
    environment:
      DATABASE_URL: ${DATABASE_URL}
      REDIS_URL: ${REDIS_URL}
      SECRET_KEY: ${SECRET_KEY}
      JWT_SECRET_KEY: ${JWT_SECRET_KEY}
      TELEGRAM_BOT_TOKEN: ${TELEGRAM_BOT_TOKEN}
      ENVIRONMENT: production
      TZ: Asia/Bangkok
    networks:
      - flyinghotel_network
    depends_on:
      mysql:
        condition: service_healthy
      redis:
        condition: service_healthy
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2

  # Celery Worker
  celery-worker:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: flyinghotel_celery_worker
    restart: always
    environment:
      DATABASE_URL: ${DATABASE_URL}
      REDIS_URL: ${REDIS_URL}
      SECRET_KEY: ${SECRET_KEY}
      TELEGRAM_BOT_TOKEN: ${TELEGRAM_BOT_TOKEN}
      ENVIRONMENT: production
      TZ: Asia/Bangkok
    networks:
      - flyinghotel_network
    depends_on:
      mysql:
        condition: service_healthy
      redis:
        condition: service_healthy
    command: celery -A app.tasks.celery_app worker --loglevel=info

  # Vue 3 Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
      args:
        VITE_API_URL: ${VITE_API_URL}
        VITE_WS_URL: ${VITE_WS_URL}
    container_name: flyinghotel_frontend
    restart: always
    ports:
      - "5173:80"
    networks:
      - flyinghotel_network
    depends_on:
      - backend

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    container_name: flyinghotel_nginx
    restart: always
    ports:
      - "80:80"
    volumes:
      - ./nginx/nginx.prod.conf:/etc/nginx/nginx.conf:ro
    networks:
      - flyinghotel_network
    depends_on:
      - backend
      - frontend

networks:
  flyinghotel_network:
    driver: bridge

volumes:
  mysql_data:
  redis_data:
  backend_uploads:
```

### 5.2 สร้าง Dockerfile.prod สำหรับ Frontend

```bash
nano frontend/Dockerfile.prod
```

วางโค้ดนี้:

```dockerfile
# Build stage
FROM node:20-alpine AS build

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build arguments for environment variables
ARG VITE_API_URL
ARG VITE_WS_URL

# Set environment variables
ENV VITE_API_URL=$VITE_API_URL
ENV VITE_WS_URL=$VITE_WS_URL

# Build the app
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### 5.3 สร้าง nginx.conf สำหรับ Frontend

```bash
nano frontend/nginx.conf
```

วางโค้ดนี้:

```nginx
server {
    listen 80;
    server_name _;

    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/javascript application/json;
}
```

### 5.4 สร้าง nginx.prod.conf สำหรับ Reverse Proxy

```bash
mkdir -p nginx
nano nginx/nginx.prod.conf
```

วางโค้ดนี้:

```nginx
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;

    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/javascript application/json;

    # Main application
    server {
        listen 80;
        server_name _;

        client_max_body_size 10M;

        # Frontend
        location / {
            proxy_pass http://frontend:80;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Backend API
        location /api/ {
            proxy_pass http://backend:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # WebSocket
        location /ws {
            proxy_pass http://backend:8000;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }

        # Backend docs (disable in production if needed)
        location /docs {
            proxy_pass http://backend:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        location /redoc {
            proxy_pass http://backend:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
```

---

## 🚀 ขั้นตอนที่ 6: Build และรัน Docker Containers

### 6.1 Build Docker Images

```bash
# Build images (ใช้เวลาประมาณ 5-10 นาที)
docker-compose -f docker-compose.prod.yml build
```

### 6.2 Start Services

```bash
# Start all services
docker-compose -f docker-compose.prod.yml up -d

# ดูสถานะ containers
docker-compose -f docker-compose.prod.yml ps
```

### 6.3 ตรวจสอบ Logs

```bash
# ดู logs ทั้งหมด
docker-compose -f docker-compose.prod.yml logs

# ดู logs แบบ realtime
docker-compose -f docker-compose.prod.yml logs -f

# ดู logs ของ service เฉพาะ
docker-compose -f docker-compose.prod.yml logs backend
docker-compose -f docker-compose.prod.yml logs frontend
```

---

## 🗄️ ขั้นตอนที่ 7: ตั้งค่า Database

### 7.1 รัน Database Migrations

```bash
# เข้าไปใน backend container
docker-compose -f docker-compose.prod.yml exec backend bash

# รัน migrations
alembic upgrade head

# ออกจาก container
exit
```

### 7.2 สร้าง Admin User

```bash
# เข้าไปใน backend container
docker-compose -f docker-compose.prod.yml exec backend bash

# เปิด Python shell
python

# รันคำสั่งนี้ใน Python shell
```

```python
import asyncio
from app.db.session import get_db
from app.models import User
from app.core.security import get_password_hash
from sqlalchemy import select

async def create_admin():
    async for db in get_db():
        # ตรวจสอบว่ามี admin อยู่แล้วหรือไม่
        result = await db.execute(select(User).where(User.username == "admin"))
        existing_user = result.scalar_one_or_none()

        if existing_user:
            print("Admin user already exists!")
            return

        # สร้าง admin user
        admin_user = User(
            username="admin",
            password_hash=get_password_hash("admin123"),  # เปลี่ยน password นี้
            full_name="Administrator",
            role="admin",
            is_active=True
        )

        db.add(admin_user)
        await db.commit()
        print("Admin user created successfully!")
        print("Username: admin")
        print("Password: admin123")
        print("⚠️  Please change password after first login!")

# รัน
asyncio.run(create_admin())
```

กด `Ctrl+D` เพื่อออกจาก Python shell และพิมพ์ `exit` เพื่อออกจาก container

---

## 🔐 ขั้นตอนที่ 8: ตั้งค่า Firewall (UFW)

```bash
# เปิดใช้งาน UFW
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 8080/tcp  # Adminer (ปิดถ้าไม่ต้องการให้เข้าถึงจากภายนอก)
ufw enable

# ตรวจสอบสถานะ
ufw status
```

---

## ✅ ขั้นตอนที่ 9: ทดสอบระบบ

### 9.1 เข้าใช้งานระบบ

เปิดเว็บเบราว์เซอร์และเข้าที่:

- **Frontend:** `http://YOUR_DROPLET_IP`
- **Backend API Docs:** `http://YOUR_DROPLET_IP/docs`
- **Adminer (Database):** `http://YOUR_DROPLET_IP:8080`

### 9.2 Login ครั้งแรก

- **Username:** admin
- **Password:** admin123 (หรือที่คุณตั้งไว้)

**⚠️ สำคัญ:** เปลี่ยน password ทันทีหลัง login ครั้งแรก!

### 9.3 ตรวจสอบ Services

```bash
# ตรวจสอบว่า services ทั้งหมดรันอยู่
docker-compose -f docker-compose.prod.yml ps

# ควรเห็น status เป็น "Up" ทั้งหมด:
# - mysql (healthy)
# - redis (healthy)
# - backend (Up)
# - celery-worker (Up)
# - frontend (Up)
# - nginx (Up)
# - adminer (Up)
```

---

## 🔄 การจัดการระบบ

### Start/Stop/Restart Services

```bash
# Stop all services
docker-compose -f docker-compose.prod.yml down

# Start all services
docker-compose -f docker-compose.prod.yml up -d

# Restart specific service
docker-compose -f docker-compose.prod.yml restart backend

# Rebuild and restart
docker-compose -f docker-compose.prod.yml up -d --build
```

### ดู Logs

```bash
# All logs
docker-compose -f docker-compose.prod.yml logs

# Follow logs (realtime)
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs backend
docker-compose -f docker-compose.prod.yml logs -f frontend
```

### อัปเดตโค้ด

```bash
# Pull latest code
cd /root/FlyingHotelApp
git pull origin main

# Rebuild and restart
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Run new migrations (if any)
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

---

## 💾 การสำรองข้อมูล (Backup)

### Backup Database

```bash
# สร้างโฟลเดอร์ backup
mkdir -p /root/backups

# Backup database
docker-compose -f docker-compose.prod.yml exec mysql mysqldump \
  -u flyinghotel_user \
  -p<MYSQL_PASSWORD> \
  flyinghotel > /root/backups/flyinghotel_$(date +%Y%m%d_%H%M%S).sql

# Backup แบบอัตโนมัติด้วย cron (ทุกวัน เวลา 3:00 น.)
crontab -e

# เพิ่มบรรทัดนี้:
0 3 * * * cd /root/FlyingHotelApp && docker-compose -f docker-compose.prod.yml exec mysql mysqldump -u flyinghotel_user -p<MYSQL_PASSWORD> flyinghotel > /root/backups/flyinghotel_$(date +\%Y\%m\%d_\%H\%M\%S).sql
```

### Restore Database

```bash
# Restore จาก backup file
docker-compose -f docker-compose.prod.yml exec -T mysql mysql \
  -u flyinghotel_user \
  -p<MYSQL_PASSWORD> \
  flyinghotel < /root/backups/flyinghotel_20250101_030000.sql
```

### Backup Uploaded Files

```bash
# Backup uploads folder
docker cp flyinghotel_backend:/app/uploads /root/backups/uploads_$(date +%Y%m%d_%H%M%S)

# หรือใช้ volume backup
docker run --rm \
  -v flyinghotelapp_backend_uploads:/data \
  -v /root/backups:/backup \
  alpine tar czf /backup/uploads_$(date +%Y%m%d_%H%M%S).tar.gz -C /data .
```

---

## 🔒 การปรับแต่งความปลอดภัย

### 1. เปลี่ยน Default Passwords

แก้ไขในไฟล์ `.env`:
- `MYSQL_ROOT_PASSWORD`
- `MYSQL_PASSWORD`
- `SECRET_KEY`
- `JWT_SECRET_KEY`

### 2. ปิด Adminer ใน Production (ถ้าไม่ใช้)

แก้ไข `docker-compose.prod.yml` ลบหรือ comment service adminer ออก

### 3. เพิ่ม SSL/TLS (HTTPS)

#### ติดตั้ง Certbot

```bash
apt install -y certbot python3-certbot-nginx

# ขอ SSL certificate (เปลี่ยน your-domain.com)
certbot --nginx -d your-domain.com
```

#### อัปเดต nginx config สำหรับ HTTPS

แก้ไข `nginx/nginx.prod.conf` เพิ่ม redirect HTTP → HTTPS

### 4. จำกัดการเข้าถึง Adminer

ใน UFW ปิด port 8080 จากภายนอก:

```bash
ufw delete allow 8080/tcp
```

เข้า Adminer ผ่าน SSH tunnel:

```bash
ssh -L 8080:localhost:8080 root@YOUR_DROPLET_IP
# จากนั้นเปิด http://localhost:8080 บนเครื่องตัวเอง
```

---

## 🐛 Troubleshooting

### ปัญหา: Container ไม่ start

```bash
# ดู logs
docker-compose -f docker-compose.prod.yml logs

# ลบ containers และ volumes แล้ว start ใหม่
docker-compose -f docker-compose.prod.yml down -v
docker-compose -f docker-compose.prod.yml up -d
```

### ปัญหา: Database connection error

```bash
# ตรวจสอบว่า MySQL container healthy
docker-compose -f docker-compose.prod.yml ps mysql

# ตรวจสอบ MySQL logs
docker-compose -f docker-compose.prod.yml logs mysql

# Restart MySQL
docker-compose -f docker-compose.prod.yml restart mysql
```

### ปัญหา: Frontend ไม่โหลด

```bash
# ตรวจสอบ environment variables
docker-compose -f docker-compose.prod.yml exec frontend env | grep VITE

# Rebuild frontend
docker-compose -f docker-compose.prod.yml build frontend
docker-compose -f docker-compose.prod.yml up -d frontend
```

### ปัญหา: Migrations ล้มเหลว

```bash
# ตรวจสอบ alembic version ปัจจุบัน
docker-compose -f docker-compose.prod.yml exec backend alembic current

# ดู migration history
docker-compose -f docker-compose.prod.yml exec backend alembic history

# Downgrade แล้ว upgrade ใหม่
docker-compose -f docker-compose.prod.yml exec backend alembic downgrade -1
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

### ปัญหา: Disk เต็ม

```bash
# ดูพื้นที่ disk
df -h

# ลบ Docker images และ containers ที่ไม่ใช้
docker system prune -a

# ลบ volumes ที่ไม่ใช้ (ระวัง!)
docker volume prune
```

---

## 📊 Monitoring

### ดูการใช้ทรัพยากร

```bash
# CPU, Memory, Network ของแต่ละ container
docker stats

# เฉพาะ containers ที่รัน
docker stats $(docker ps --format '{{.Names}}')
```

### ตรวจสอบสุขภาพระบบ

```bash
# Health check
docker-compose -f docker-compose.prod.yml ps

# Check disk usage
du -sh /var/lib/docker

# Check logs size
du -sh /var/lib/docker/containers/*/
```

---

## 🎉 เสร็จสิ้น!

ตอนนี้ระบบ FlyingHotelApp ของคุณพร้อมใช้งานบน Digital Ocean แล้ว!

### Next Steps:

1. ✅ เปลี่ยน admin password
2. ✅ ตั้งค่า backup อัตโนมัติ
3. ✅ ติดตั้ง SSL/TLS (ถ้ามี domain)
4. ✅ ตั้งค่า Telegram Bot (ถ้าต้องการ)
5. ✅ ทดสอบระบบให้ครบทุก feature
6. ✅ สร้าง user accounts สำหรับพนักงาน

### Links ที่สำคัญ:

- **Frontend:** `http://YOUR_IP`
- **API Docs:** `http://YOUR_IP/docs`
- **Adminer:** `http://YOUR_IP:8080` (เฉพาะผู้ดูแลระบบ)

---

## 📞 ติดต่อสอบถาม

หากมีปัญหาหรือข้อสงสัย:
1. ตรวจสอบ logs: `docker-compose -f docker-compose.prod.yml logs`
2. อ่าน Troubleshooting section ด้านบน
3. ตรวจสอบ GitHub Issues

---

**หมายเหตุ:** คู่มือนี้อ้างอิงจาก Phase 0-4 ที่พัฒนาเสร็จแล้ว หากมีการพัฒนาเพิ่มเติม (Phase 5-8) อาจต้องอัปเดตคู่มือนี้ตามด้วย
