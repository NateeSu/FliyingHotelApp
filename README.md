# FlyingHotelApp 🏨

ระบบบริหารจัดการโรงแรมขนาดเล็ก (Property Management System) ที่รองรับการพักแบบค้างคืนและชั่วคราว

## ✨ Features

- 🏢 รองรับโรงแรมขนาดเล็ก (ไม่เกิน 50 ห้อง)
- ⚡ Real-time updates ผ่าน WebSocket
- 📱 Mobile-first responsive design
- 🔔 แจ้งเตือนผ่าน Telegram
- 🌙 รองรับการพักค้างคืนและการพักชั่วคราว (3 ชั่วโมง)
- 📊 รายงานและ Analytics
- 🧹 ระบบแม่บ้านและซ่อมบำรุง
- 🛒 ระบบสั่งของผ่าน QR Code
- 📅 ระบบจองล่วงหน้า

## 🛠 Technology Stack

### Backend
- FastAPI (Python 3.11+)
- MySQL 8.0 + SQLAlchemy 2.0 (Async)
- Redis (Cache & Message Broker)
- Celery (Background Tasks)
- Telegram Bot Integration

### Frontend
- Vue 3 (Composition API + TypeScript)
- Naive UI
- Pinia (State Management)
- Socket.IO (Real-time)
- Vite + PWA

### Infrastructure
- Docker + Docker Compose
- Nginx (Reverse Proxy)
- Adminer (Database Management)

## 📋 Prerequisites

- Docker Desktop (Windows) หรือ Docker Engine (Linux)
- Git
- 2GB RAM ขึ้นไป

## 🚀 Quick Start

### 1. Clone Repository

```bash
git clone <repository-url>
cd FlyingHotelApp
```

### 2. Setup Environment Variables

```bash
cp .env.example .env
```

แก้ไขไฟล์ `.env` ตามต้องการ (สำหรับ development ใช้ค่า default ได้เลย)

### 3. Start All Services

```bash
docker-compose up -d
```

รอให้ services ทั้งหมดเริ่มทำงาน (ประมาณ 2-3 นาที)

### 4. Access Applications

- **Frontend**: http://localhost:5173
- **Backend API Docs**: http://localhost:8000/docs
- **Backend ReDoc**: http://localhost:8000/redoc
- **Adminer (Database)**: http://localhost:8080
- **Nginx**: http://localhost:80

### 5. Database Setup

```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# Create admin user (coming in Phase 1)
# docker-compose exec backend python scripts/create_admin.py
```

## 📚 Development

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Run Tests

```bash
# Backend tests
docker-compose exec backend pytest

# Backend tests with coverage
docker-compose exec backend pytest --cov=app --cov-report=html

# Frontend tests
docker-compose exec frontend npm run test
```

### Code Formatting

```bash
# Backend (Black + Ruff)
docker-compose exec backend black app/
docker-compose exec backend ruff check app/

# Frontend (ESLint + Prettier)
docker-compose exec frontend npm run lint
docker-compose exec frontend npm run format
```

### Database Migrations

```bash
# Create new migration
docker-compose exec backend alembic revision --autogenerate -m "description"

# Apply migrations
docker-compose exec backend alembic upgrade head

# Rollback one migration
docker-compose exec backend alembic downgrade -1

# Show current revision
docker-compose exec backend alembic current
```

### Access Adminer (Database Management)

1. เปิด http://localhost:8080
2. กรอกข้อมูล:
   - System: `MySQL`
   - Server: `mysql`
   - Username: `flyinghotel_user` (หรือตาม .env)
   - Password: `flyinghotel_pass` (หรือตาม .env)
   - Database: `flyinghotel` (หรือตาม .env)

## 🔧 Troubleshooting

### Services ไม่เริ่มทำงาน

```bash
# ดู logs
docker-compose logs

# Restart services
docker-compose restart

# Rebuild containers
docker-compose down
docker-compose up -d --build
```

### Database Connection Error

```bash
# ตรวจสอบว่า MySQL service ทำงานหรือไม่
docker-compose ps

# Restart MySQL
docker-compose restart mysql

# รอให้ MySQL พร้อม (health check)
docker-compose exec mysql mysqladmin ping -h localhost
```

### Port Already in Use

แก้ไข port ใน `docker-compose.yml`:
```yaml
ports:
  - "3307:3306"  # แทน 3306:3306
```

## 📖 Documentation

- [PRD.md](./PRD.md) - Product Requirements Document (ภาษาไทย)
- [CLAUDE.md](./CLAUDE.md) - Claude Code Development Guide
- [REQ.md](./REQ.md) - Initial Requirements

## 🗂 Project Structure

```
FlyingHotelApp/
├── backend/              # FastAPI Backend
│   ├── app/
│   │   ├── api/         # API endpoints
│   │   ├── core/        # Config & security
│   │   ├── models/      # SQLAlchemy models
│   │   ├── schemas/     # Pydantic schemas
│   │   ├── services/    # Business logic
│   │   ├── tasks/       # Celery tasks
│   │   └── db/          # Database session
│   ├── alembic/         # Database migrations
│   ├── tests/           # Backend tests
│   └── requirements.txt
├── frontend/            # Vue 3 Frontend
│   ├── src/
│   │   ├── api/        # API client
│   │   ├── components/ # Vue components
│   │   ├── views/      # Page views
│   │   ├── stores/     # Pinia stores
│   │   ├── router/     # Vue Router
│   │   └── types/      # TypeScript types
│   └── package.json
├── nginx/              # Nginx configuration
├── docker-compose.yml
└── .env.example
```

## 🎯 Development Phases

โปรเจ็คนี้พัฒนาเป็น 9 Phases:

- ✅ **Phase 0**: Project Setup & Infrastructure (ปัจจุบัน)
- ⏳ **Phase 1**: Authentication & User Management
- ⏳ **Phase 2**: Room Management
- ⏳ **Phase 3**: Room Control Dashboard (CRITICAL)
- ⏳ **Phase 4**: Check-In & Check-Out (CRITICAL)
- ⏳ **Phase 5**: Housekeeping System
- ⏳ **Phase 6**: Maintenance & Order System
- ⏳ **Phase 7**: Booking System
- ⏳ **Phase 8**: Reports & Settings

รายละเอียดแต่ละ phase ดูได้ที่ [PRD.md](./PRD.md)

## 🤝 Contributing

อ่าน [CLAUDE.md](./CLAUDE.md) สำหรับ development guidelines

## 📄 License

Proprietary - FlyToDream Development Team

## 📞 Support

สำหรับคำถามหรือปัญหา ติดต่อทีมพัฒนา

---

**Phase 0 Status**: ✅ Complete
**Last Updated**: 2025-10-12
