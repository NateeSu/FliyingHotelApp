# FlyingHotelApp - Cloud Deployment Installation Guide

**Last Updated:** November 4, 2025
**Version:** 1.0
**Status:** Ready for Cloud Testing

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Server Setup](#server-setup)
3. [Environment Variables](#environment-variables)
4. [Database Setup & Migrations](#database-setup--migrations)
5. [Backend Setup](#backend-setup)
6. [Frontend Setup](#frontend-setup)
7. [Nginx Configuration](#nginx-configuration)
8. [Starting Services](#starting-services)
9. [Verification & Testing](#verification--testing)
10. [Troubleshooting](#troubleshooting)
11. [Backup & Recovery](#backup--recovery)

---

## Prerequisites

### System Requirements
- **OS:** Ubuntu 22.04 LTS or later (recommended for cloud)
- **CPU:** Minimum 2 cores
- **RAM:** Minimum 2GB (4GB recommended for production)
- **Storage:** Minimum 20GB (SSD recommended)
- **Docker & Docker Compose:** Latest versions installed

### Required Tools
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installations
docker --version
docker-compose --version
```

### Ports Required
- **3306:** MySQL Database
- **6379:** Redis Cache
- **8000:** FastAPI Backend
- **5173:** Vue Frontend (development)
- **80/443:** Nginx (production)
- **8080:** Adminer (optional, development only)

---

## Server Setup

### 1. Clone Repository
```bash
# SSH clone (recommended for servers)
git clone git@github.com:NateeSu/FliyingHotelApp.git
cd FlyingHotelApp

# Or HTTPS clone
git clone https://github.com/NateeSu/FliyingHotelApp.git
cd FlyingHotelApp
```

### 2. Set Directory Permissions
```bash
# Create upload directories for photos
sudo mkdir -p /app/uploads/maintenance
sudo mkdir -p /app/uploads/housekeeping
sudo mkdir -p /app/uploads/payments

# Ensure proper permissions
sudo chown -R 1000:1000 /app/uploads
sudo chmod -R 755 /app/uploads
```

### 3. Prepare Docker Volumes
```bash
# Docker volumes will be created automatically, but you can pre-create them
docker volume create flyinghotel_mysql_data
docker volume create flyinghotel_redis_data
docker volume create flyinghotel_backend_uploads
```

---

## Environment Variables

### Create `.env` File
```bash
cat > .env << 'EOF'
# ============================================================
# FlyingHotelApp Cloud Deployment Configuration
# ============================================================

# Database Configuration
MYSQL_ROOT_PASSWORD=your_secure_root_password_here_min_12_chars
MYSQL_DATABASE=flyinghotel_db
MYSQL_USER=flyinghotel_user
MYSQL_PASSWORD=your_secure_db_password_here_min_12_chars

# Backend Configuration
SECRET_KEY=your_very_secure_jwt_secret_key_min_32_chars_random
ENVIRONMENT=production
DATABASE_URL=mysql+aiomysql://flyinghotel_user:your_secure_db_password_here_min_12_chars@mysql:3306/flyinghotel_db?charset=utf8mb4
REDIS_URL=redis://redis:6379/0

# Telegram Configuration (optional)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_or_leave_empty

# Frontend Configuration
VITE_API_BASE_URL=https://your-domain.com/api/v1
VITE_WS_URL=wss://your-domain.com/ws

# Email Configuration (for notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_email_password_or_app_token
SMTP_FROM=noreply@your-domain.com

# Timezone
TZ=Asia/Bangkok
EOF
```

### Security Best Practices for Passwords
```bash
# Generate secure passwords
openssl rand -base64 32  # For SECRET_KEY
openssl rand -base64 16  # For database passwords

# IMPORTANT: Keep .env file secure
chmod 600 .env
# Add to .gitignore (already done, but verify)
echo ".env" >> .gitignore
echo ".env.local" >> .gitignore
```

---

## Database Setup & Migrations

### 1. Create Initial Database
```bash
# Start only MySQL service first
docker-compose up -d mysql

# Wait for MySQL to be ready (health check)
docker-compose ps
# Wait until mysql shows "healthy"
sleep 10
```

### 2. Apply Database Migrations
```bash
# Run all pending migrations
docker-compose run --rm backend alembic upgrade head

# Verify migrations applied
docker-compose exec backend alembic history

# Expected output: List of all migrations including:
# - cd860e3e92fd -> add_photos_maintenance, standardize all enum values to uppercase
# - 27091df09970 -> cd860e3e92fd, make customer name and phone optional
# - 86b5fe0f328b -> 27091df09970, fix room status enum case
# ... (and other previous migrations)
```

### 3. Create Initial Admin User
```bash
# Access backend container
docker-compose exec backend python -c "
from app.db.session import get_db_session
from app.models.user import User, UserRole
from app.core.security import get_password_hash
import asyncio

async def create_admin():
    db = get_db_session()
    try:
        # Check if admin exists
        admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
        if admin:
            print('Admin user already exists')
            return

        # Create admin user
        admin_user = User(
            username='admin',
            email='admin@flyinghotel.local',
            hashed_password=get_password_hash('admin123'),
            role=UserRole.ADMIN,
            is_active=True
        )
        db.add(admin_user)
        db.commit()
        print('Admin user created successfully')
        print('Username: admin')
        print('Password: admin123')
        print('⚠️  IMPORTANT: Change password after first login!')
    finally:
        db.close()

asyncio.run(create_admin())
"
```

### 4. Verify Database Connection
```bash
# Test database connection
docker-compose exec mysql mysql -h localhost -u root -p${MYSQL_ROOT_PASSWORD} -e "SHOW DATABASES;"

# Should output:
# | Database           |
# | flyinghotel_db     |
# | mysql              |
# | performance_schema |
# | information_schema |
```

---

## Backend Setup

### 1. Build Backend Image
```bash
# Build backend Docker image
docker-compose build backend

# This will:
# - Install all Python dependencies from requirements.txt
# - Create necessary directories
# - Set up environment for FastAPI
```

### 2. Start Backend Service
```bash
# Start backend (will run migrations on first start if not already done)
docker-compose up -d backend

# Check backend logs
docker-compose logs -f backend

# Wait for message: "Application startup complete"
# Press Ctrl+C to exit logs
```

### 3. Verify Backend API
```bash
# Check if API is responding
curl -s http://localhost:8000/docs | head -20

# Should return HTML with Swagger UI, confirming backend is running

# Or check specific endpoint
curl -s http://localhost:8000/api/v1/health

# Expected: Connection accepted (backend is running)
```

### 4. Important Backend Configuration

#### File Upload Directory
```bash
# Create persistent upload directory
docker exec flyinghotel_backend mkdir -p /app/uploads/maintenance
docker exec flyinghotel_backend mkdir -p /app/uploads/housekeeping

# Verify directory structure
docker exec flyinghotel_backend ls -la /app/uploads/
```

#### Static File Serving
```bash
# Backend automatically serves files from /app/uploads
# Verify in backend logs: "Mounting StaticFiles" message
```

---

## Frontend Setup

### 1. Build Frontend Image
```bash
# Build frontend Docker image
docker-compose build frontend

# This will:
# - Install Node.js dependencies
# - Compile TypeScript
# - Build Vue 3 application
# - Create optimized production bundle
```

### 2. Update Frontend Configuration
The frontend connects via the Nginx reverse proxy. No additional configuration needed if using the provided Nginx setup.

### 3. Start Frontend Service
```bash
# Start frontend
docker-compose up -d frontend

# Check frontend logs
docker-compose logs -f frontend

# Wait for message: "VITE v[version] ready in [time] ms"
```

### 4. Verify Frontend
```bash
# For development testing
curl -s http://localhost:5173 | head -30

# Should return HTML with Vue app root element
```

---

## Nginx Configuration

### 1. Install Nginx
```bash
# If not using Docker Nginx, install on host
sudo apt install -y nginx

# Start Nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

### 2. Create Nginx Configuration
```bash
# Create configuration directory
sudo mkdir -p /etc/nginx/sites-available
sudo mkdir -p /etc/nginx/sites-enabled

# Create configuration file
sudo tee /etc/nginx/sites-available/flyinghotel << 'EOF'
upstream backend {
    server localhost:8000;
}

upstream frontend {
    server localhost:5173;
}

server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # Redirect HTTP to HTTPS (production)
    # return 301 https://$server_name$request_uri;

    # Or for development, continue with HTTP

    # Frontend (main app)
    location / {
        proxy_pass http://frontend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket support
    location /ws {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 86400;
    }

    # Backend API
    location /api/ {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static files from backend (uploads)
    location /uploads/ {
        proxy_pass http://backend;
        proxy_cache_valid 200 1d;
    }

    # Swagger UI
    location /docs {
        proxy_pass http://backend;
        proxy_set_header Host $host;
    }

    location /redoc {
        proxy_pass http://backend;
        proxy_set_header Host $host;
    }
}

# HTTPS Configuration (Production Only)
# server {
#     listen 443 ssl http2;
#     server_name your-domain.com www.your-domain.com;
#
#     ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
#     ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
#     ssl_protocols TLSv1.2 TLSv1.3;
#     ssl_ciphers HIGH:!aNULL:!MD5;
#
#     # ... same configuration as above ...
# }
EOF
```

### 3. Enable Nginx Site
```bash
# Create symbolic link to enable site
sudo ln -s /etc/nginx/sites-available/flyinghotel /etc/nginx/sites-enabled/

# Test Nginx configuration
sudo nginx -t

# Should output: "syntax is ok" and "test is successful"

# Reload Nginx
sudo systemctl reload nginx
```

---

## Starting Services

### Complete Startup Sequence

```bash
# 1. Navigate to project directory
cd /path/to/FlyingHotelApp

# 2. Load environment variables
source .env

# 3. Start all services
docker-compose up -d

# 4. Wait for all services to be healthy
docker-compose ps

# Output should show all containers "Up" with proper health status

# 5. Check service logs (wait a moment between commands)
echo "=== Backend Logs ==="
docker-compose logs backend | tail -20

echo "=== Frontend Logs ==="
docker-compose logs frontend | tail -20

echo "=== MySQL Logs ==="
docker-compose logs mysql | tail -20
```

### Quick Start Commands
```bash
# Start specific services
docker-compose up -d mysql redis backend frontend

# Stop all services
docker-compose down

# Stop and remove volumes (⚠️  WARNING: Deletes all data!)
docker-compose down -v

# View all service logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f mysql
```

---

## Verification & Testing

### 1. Service Health Checks

```bash
# Check all services are running
docker-compose ps

# Expected output:
# NAME                  STATUS
# flyinghotel_mysql     Up (healthy)
# flyinghotel_redis     Up (healthy)
# flyinghotel_backend   Up
# flyinghotel_frontend  Up
# flyinghotel_adminer   Up (optional)
```

### 2. API Endpoints Testing

```bash
# Test backend health endpoint
curl -s http://localhost:8000/api/v1/health

# Get Swagger documentation
curl -s -H "Accept: application/json" http://localhost:8000/docs

# Test authentication (login endpoint)
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq

# Expected: JWT token response
```

### 3. Database Verification

```bash
# Connect to MySQL
docker-compose exec mysql mysql -u${MYSQL_USER} -p${MYSQL_PASSWORD} ${MYSQL_DATABASE}

# Run queries
mysql> SELECT COUNT(*) as user_count FROM users;
mysql> SELECT COUNT(*) as room_count FROM rooms;
mysql> EXIT;
```

### 4. Frontend Access

```bash
# In development (without SSL)
# Open browser: http://localhost:5173 (direct to Vite dev server)
# Or: http://localhost/  (through Nginx)

# Login credentials
# Username: admin
# Password: admin123
```

### 5. Upload Functionality Test

```bash
# Verify upload directory permissions
docker exec flyinghotel_backend ls -la /app/uploads/
docker exec flyinghotel_backend ls -la /app/uploads/maintenance/

# Test file upload (after admin login)
# 1. Go to Maintenance section: http://localhost:5173/maintenance
# 2. Create new maintenance task with photo upload
# 3. Verify files appear in /app/uploads/maintenance/
```

---

## Troubleshooting

### Common Issues & Solutions

#### 1. MySQL Connection Error
```bash
# Problem: "Can't connect to MySQL server"
# Solution:
docker-compose logs mysql
# Wait for "ready for connections" message
docker-compose restart mysql
docker-compose up -d backend
```

#### 2. Database Migration Failed
```bash
# Problem: "Alembic migration failed"
# Solution:
# Check migration history
docker-compose exec backend alembic history

# Rollback one migration if needed
docker-compose exec backend alembic downgrade -1

# Re-apply migrations
docker-compose exec backend alembic upgrade head

# Check for migration issues
docker-compose logs backend | grep -i alembic
```

#### 3. Frontend Not Loading
```bash
# Problem: Blank page or connection refused
# Solution:
docker-compose logs frontend

# Check if frontend is ready
curl -s http://localhost:5173/

# Rebuild frontend
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

#### 4. Port Already in Use
```bash
# Problem: "Address already in use"
# Solution:
# Find process using port
sudo lsof -i :8000
sudo lsof -i :5173
sudo lsof -i :3306

# Kill process (if safe)
sudo kill -9 <PID>

# Or change ports in docker-compose.yml and .env
```

#### 5. Permission Denied - Upload Directory
```bash
# Problem: "Permission denied" when uploading files
# Solution:
docker exec flyinghotel_backend chmod -R 777 /app/uploads
docker exec flyinghotel_backend chown -R 1000:1000 /app/uploads

# Or fix in docker-compose volumes section
```

#### 6. Enum Values Error
```bash
# Problem: "LookupError: 'pending' is not a valid..."
# Cause: Database has old lowercase enum values
# Solution:
docker-compose exec backend alembic upgrade head

# If still failing, check database directly
docker-compose exec mysql mysql -u${MYSQL_USER} -p${MYSQL_PASSWORD} ${MYSQL_DATABASE} \
  -e "SELECT DISTINCT status FROM bookings;"

# Should show UPPERCASE values (PENDING, CONFIRMED, CHECKED_IN, etc.)
```

#### 7. WebSocket Connection Timeout
```bash
# Problem: "WebSocket connection failed"
# Solution:
# Check Nginx proxy_read_timeout setting (should be 86400 or higher)
# Verify /ws endpoint is proxied correctly
# Check firewall allows WebSocket connections

sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

### Debug Mode

```bash
# Enable detailed logging
docker-compose down
export DEBUG=1
docker-compose up -d --log-level debug

# View real-time logs
docker-compose logs -f --tail=50 backend

# Check environment variables
docker exec flyinghotel_backend env | grep -E "DATABASE|SECRET|REDIS"
```

---

## Backup & Recovery

### 1. Database Backup

```bash
# Create database backup
BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec mysql mysqldump -u${MYSQL_USER} -p${MYSQL_PASSWORD} ${MYSQL_DATABASE} \
  > ./backups/flyinghotel_${BACKUP_DATE}.sql

# Or backup with compression
docker-compose exec mysql mysqldump -u${MYSQL_USER} -p${MYSQL_PASSWORD} ${MYSQL_DATABASE} \
  | gzip > ./backups/flyinghotel_${BACKUP_DATE}.sql.gz
```

### 2. Upload Files Backup

```bash
# Backup all uploaded files
BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
docker cp flyinghotel_backend:/app/uploads ./backups/uploads_${BACKUP_DATE}

# Or using tar
tar -czf ./backups/uploads_${BACKUP_DATE}.tar.gz backend/app/uploads/
```

### 3. Full Backup Script

```bash
#!/bin/bash
# Create backup directory
mkdir -p ./backups

# Backup database
BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
echo "Backing up database..."
docker-compose exec mysql mysqldump -u${MYSQL_USER} -p${MYSQL_PASSWORD} ${MYSQL_DATABASE} \
  | gzip > ./backups/db_${BACKUP_DATE}.sql.gz

# Backup files
echo "Backing up uploaded files..."
tar -czf ./backups/uploads_${BACKUP_DATE}.tar.gz backend/app/uploads/

# Backup .env file (SECURE THIS!)
cp .env ./backups/.env_${BACKUP_DATE}
chmod 600 ./backups/.env_${BACKUP_DATE}

echo "Backup completed: backups/"
ls -lh ./backups/
```

### 4. Database Recovery

```bash
# Restore from backup
docker-compose exec -T mysql mysql -u${MYSQL_USER} -p${MYSQL_PASSWORD} ${MYSQL_DATABASE} \
  < ./backups/flyinghotel_YYYYMMDD_HHMMSS.sql

# Or from gzip backup
gunzip < ./backups/flyinghotel_YYYYMMDD_HHMMSS.sql.gz \
  | docker-compose exec -T mysql mysql -u${MYSQL_USER} -p${MYSQL_PASSWORD} ${MYSQL_DATABASE}
```

---

## Important Notes for Testers

### Key Changes in This Version
- ✅ Enum standardization: All enum values are now **UPPERCASE** (PENDING, CONFIRMED, etc.)
- ✅ Optional customer info: Name and phone number are now optional during check-in
- ✅ Photo upload: Support for maintenance task photos
- ✅ Dashboard redesign: New room status metrics and stay type badges
- ✅ Proper null handling: Guest name fallback to "ไม่ระบุชื่อ" if empty

### Testing Checklist
- [ ] Login with admin account
- [ ] Create a room and configure room rates
- [ ] Test check-in (both overnight and temporary stays)
- [ ] Verify stay type displays correctly on dashboard
- [ ] Test maintenance task creation with photo upload
- [ ] Test housekeeping task completion
- [ ] Verify overtime alerts work
- [ ] Check WebSocket real-time updates
- [ ] Test booking creation and check-in flow
- [ ] Verify all enum values are UPPERCASE in API responses

### Support & Issues
- Check logs: `docker-compose logs -f service_name`
- Review database migrations: `docker-compose exec backend alembic history`
- Check environment variables: `docker-compose exec backend env | grep -i flying`

---

## Quick Reference Commands

```bash
# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f mysql

# Database
docker-compose exec backend alembic history
docker-compose exec backend alembic upgrade head

# Containers
docker-compose ps
docker-compose restart backend
docker-compose stop
docker-compose start

# Cleanup
docker-compose down
docker-compose down -v  # WARNING: Removes all data!

# Development
docker-compose up -d --build
docker-compose exec backend python -m pytest
```

---

## Contact & Support

For issues or questions:
1. Check the troubleshooting section above
2. Review Docker logs with detailed output
3. Verify all environment variables are set correctly
4. Ensure all ports are available and not blocked
5. Check database migration status

---

**Document Version:** 1.0
**Last Updated:** November 4, 2025
**Status:** Production Ready for Testing
