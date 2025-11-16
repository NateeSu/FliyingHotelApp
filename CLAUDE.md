# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**FlyingHotelApp** is a comprehensive Property Management System (PMS) designed for small hotels (up to 50 rooms) in Thailand. The system's unique feature is supporting both **overnight stays** and **temporary stays** (3-hour sessions), which is uncommon in traditional hotel management systems.

**Language**: All UI/UX content is in Thai. Code comments and documentation should be in English.

**Target Users**: The system must be intuitive enough for someone with middle school education to use without reading manuals.

**Status**: Currently in planning phase. PRD.md contains the complete product requirements and development roadmap.

## Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: MySQL 8.0 with SQLAlchemy 2.0 (Async ORM)
- **Migrations**: Alembic
- **Auth**: JWT (JSON Web Tokens)
- **Background Tasks**: Celery + Redis
- **Validation**: Pydantic V2
- **PDF Generation**: ReportLab or WeasyPrint
- **Telegram Integration**: python-telegram-bot
- **WebSocket**: For real-time updates

### Frontend
- **Framework**: Vue 3 (Composition API + TypeScript)
- **State Management**: Pinia
- **UI Framework**: Naive UI (recommended) or Vuetify 3 or Element Plus
- **Real-time**: Socket.IO Client
- **HTTP Client**: Axios
- **Date/Time**: Day.js
- **Charts**: Chart.js + vue-chartjs
- **Calendar**: FullCalendar (for booking system)
- **PWA**: Vite PWA Plugin

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **Web Server**: Nginx (Reverse Proxy)
- **Cache & Queue**: Redis
- **Database Admin**: Adminer (lightweight alternative to phpMyAdmin)
- **Deployment**: Digital Ocean Droplet (2GB RAM)

## Core System Architecture

The system uses a **microservices-like architecture** within Docker:

```
Client (Vue 3) → Nginx → FastAPI Backend ↔ MySQL Database
                              ↓
                         Redis (Cache + Celery Queue)
                              ↓
                         Celery Workers → Telegram Bot
```

### Key Architectural Decisions

1. **Real-time Updates**: All room status changes broadcast via WebSocket to ensure dashboard updates instantly
2. **Mobile-First Design**: UI optimized for mobile/tablet first, then desktop
3. **Role-Based Access Control**: 4 user roles (admin, reception, housekeeping, maintenance)
4. **Telegram Integration**: Critical notifications sent to appropriate staff via Telegram
5. **QR Code System**: Static QR codes per room for guest orders (no authentication required)

## Development Workflow

### Phase-Based Development
Development is divided into **9 phases** (Phase 0-8), each must be **100% tested** before proceeding:

- **Phase 0**: Project Setup & Infrastructure (2-3 days)
- **Phase 1**: Authentication & User Management (3-4 days)
- **Phase 2**: Room Management (3-4 days)
- **Phase 3**: Room Control Dashboard - **CRITICAL** (5-6 days)
- **Phase 4**: Check-In & Check-Out - **CRITICAL** (5-6 days)
- **Phase 5**: Housekeeping System (4-5 days)
- **Phase 6**: Maintenance & Order System (4-5 days)
- **Phase 7**: Booking System (5-6 days)
- **Phase 8**: Reports & Settings (4-5 days)
- **Phase 9**: Final Polish & Testing (3-4 days)

**Total Timeline**: 5-6 weeks

### Commands

#### Development Setup
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f [service_name]

# Stop all services
docker-compose down
```

#### Database Management
```bash
# Create new migration
docker-compose exec backend alembic revision --autogenerate -m "description"

# Run migrations
docker-compose exec backend alembic upgrade head

# Rollback migration
docker-compose exec backend alembic downgrade -1

# Access database via Adminer
# Open browser: http://localhost:8080
```

#### Backend Development
```bash
# Run backend tests
docker-compose exec backend pytest

# Run tests with coverage
docker-compose exec backend pytest --cov=app --cov-report=html

# Format code
docker-compose exec backend black app/
docker-compose exec backend ruff check app/

# Access backend shell
docker-compose exec backend python
```

#### Frontend Development
```bash
# Install dependencies
docker-compose exec frontend npm install

# Run frontend tests
docker-compose exec frontend npm run test

# Run tests in watch mode
docker-compose exec frontend npm run test:watch

# Lint and format
docker-compose exec frontend npm run lint
docker-compose exec frontend npm run format

# Build for production
docker-compose exec frontend npm run build
```

#### Celery Tasks
```bash
# View Celery worker logs
docker-compose logs -f celery-worker

# Access Celery shell
docker-compose exec backend celery -A app.tasks.celery_app shell
```

## Critical Business Logic

### Room Status Flow
```
available → reserved (booking) → occupied (check-in) → cleaning (check-out) → available
           ↘ out_of_service (manual toggle)
```

### Stay Types

**1. Overnight (ค้างคืน)**
- Check-in: from 13:00 on arrival day
- Check-out: before 12:00 on departure day
- Billing: per night
- Can be booked in advance

**2. Temporary (ชั่วคราว)**
- Check-in: anytime
- Check-out: within 3 hours (configurable)
- Billing: per session
- Cannot be booked in advance
- Auto-calculated expected check-out time

### Overtime Alerts
- **Overnight**: Alert if not checked out by 12:00
- **Temporary**: Alert if exceeds 3 hours from check-in
- Alerts shown on dashboard **real-time** with elapsed time
- Notifications sent via Telegram to reception/admin

### Housekeeping Task Auto-Creation
When a room is checked out or transferred:
1. Room status → "cleaning"
2. Housekeeping task created in database
3. Telegram notification sent with task detail URL
4. Housekeeping staff starts timer when beginning work
5. Upon completion, room status → "available"

## Database Architecture

### Key Tables & Relationships

**Core Entities**:
- `users` (4 roles: admin, reception, housekeeping, maintenance)
- `room_types`, `rooms`, `room_rates` (supports multi-type pricing)
- `customers` (mini CRM tracking visit history)
- `bookings` (overnight only, optional deposits)
- `check_ins` (both overnight and temporary)
- `orders` (guest orders via QR code or reception)
- `products` (room amenities + food/beverage)
- `housekeeping_tasks`, `maintenance_tasks`
- `payments`, `notifications`, `activity_logs`

**Important Indexes** (see PRD.md lines 447-459 for full list):
- `idx_rooms_status` on `rooms(status)`
- `idx_check_ins_status` on `check_ins(status)`
- `idx_bookings_dates` on `bookings(check_in_date, check_out_date)`

### Data Integrity Rules
1. **Room Transfer**: Only to same room type (VIP → VIP)
2. **Booking → Check-in**: If booking exists, pre-fill check-in form with booking data and deduct deposit from total
3. **Deposits**: Non-refundable if no-show (1 hour after check-in time)
4. **Customer Deduplication**: Auto-merge by phone number

## API Conventions

### Endpoint Structure
```
/api/v1/{resource}
```

All API endpoints use `/api/v1/` prefix for versioning.

### Response Format
**Success**:
```json
{
  "data": { ... },
  "message": "Success message in Thai" (optional)
}
```

**Error**:
```json
{
  "detail": "Error message in Thai",
  "error_code": "ROOM_NOT_FOUND"
}
```

### WebSocket Events
**Connection**: `/ws/dashboard`

**Message Format**:
```json
{
  "event": "room_status_changed",
  "data": {
    "room_id": 101,
    "old_status": "cleaning",
    "new_status": "available",
    "timestamp": "2024-01-15T10:30:00"
  }
}
```

**Event Types**:
- `room_status_changed`
- `overtime_alert`
- `new_booking`
- `housekeeping_completed`
- `maintenance_request`

## Enum Standards (CRITICAL)

### ⚠️ **ENUM CASE CONVENTION - MUST BE ALL UPPERCASE**

All enum values across the entire system **MUST** be **UPPERCASE ONLY**. This includes:
- Database enum columns
- Python model enums
- Pydantic schemas
- Frontend TypeScript enums
- API requests/responses

**WHY**: SQLAlchemy requires exact case matching between database and Python enums. Mismatched cases cause `LookupError` and break the entire application.

### Complete Enum Reference

#### Room Status (rooms.status)
```
Database: ENUM('AVAILABLE','OCCUPIED','CLEANING','RESERVED','OUT_OF_SERVICE')
Python:   AVAILABLE, OCCUPIED, CLEANING, RESERVED, OUT_OF_SERVICE
API:      'AVAILABLE', 'OCCUPIED', 'CLEANING', 'RESERVED', 'OUT_OF_SERVICE'
```

#### Stay Type (room_rates.stay_type, check_ins.stay_type, bookings.stay_type)
```
Database: ENUM('OVERNIGHT','TEMPORARY')
Python:   OVERNIGHT, TEMPORARY
API:      'OVERNIGHT', 'TEMPORARY'
```

#### Check-in Status (check_ins.status)
```
Database: ENUM('CHECKED_IN','CHECKED_OUT')
Python:   CHECKED_IN, CHECKED_OUT
API:      'CHECKED_IN', 'CHECKED_OUT'
```

#### Payment Method (check_ins.payment_method)
```
Database: ENUM('CASH','TRANSFER','CREDIT_CARD')
Python:   CASH, TRANSFER, CREDIT_CARD
API:      'CASH', 'TRANSFER', 'CREDIT_CARD'
```

#### Task Status (housekeeping_tasks.status, maintenance_tasks.status)
```
Database: ENUM('PENDING','IN_PROGRESS','COMPLETED','CANCELLED')
Python:   PENDING, IN_PROGRESS, COMPLETED, CANCELLED
API:      'PENDING', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED'
```

#### Task Priority (housekeeping_tasks.priority, maintenance_tasks.priority)
```
Database: ENUM('URGENT','HIGH','MEDIUM','LOW')
Python:   URGENT, HIGH, MEDIUM, LOW
API:      'URGENT', 'HIGH', 'MEDIUM', 'LOW'
```

#### Maintenance Category (maintenance_tasks.category)
```
Database: ENUM('PLUMBING','ELECTRICAL','HVAC','FURNITURE','APPLIANCE','BUILDING','OTHER')
Python:   PLUMBING, ELECTRICAL, HVAC, FURNITURE, APPLIANCE, BUILDING, OTHER
API:      'PLUMBING', 'ELECTRICAL', 'HVAC', 'FURNITURE', 'APPLIANCE', 'BUILDING', 'OTHER'
```

#### Booking Status (bookings.status)
```
Database: ENUM('PENDING','CONFIRMED','CHECKED_IN','COMPLETED','CANCELLED')
Python:   PENDING, CONFIRMED, CHECKED_IN, COMPLETED, CANCELLED
API:      'PENDING', 'CONFIRMED', 'CHECKED_IN', 'COMPLETED', 'CANCELLED'
```

#### User Role (users.role)
```
Database: ENUM('ADMIN','RECEPTION','HOUSEKEEPING','MAINTENANCE')
Python:   ADMIN, RECEPTION, HOUSEKEEPING, MAINTENANCE
API:      'ADMIN', 'RECEPTION', 'HOUSEKEEPING', 'MAINTENANCE'
```

#### Notification Type (notifications.notification_type)
```
Database: ENUM('ROOM_STATUS_CHANGE','OVERTIME_ALERT','BOOKING_REMINDER','HOUSEKEEPING_COMPLETE','MAINTENANCE_REQUEST','CHECK_IN','CHECK_OUT','ROOM_TRANSFER')
Python:   ROOM_STATUS_CHANGE, OVERTIME_ALERT, BOOKING_REMINDER, HOUSEKEEPING_COMPLETE, MAINTENANCE_REQUEST, CHECK_IN, CHECK_OUT, ROOM_TRANSFER
API:      'ROOM_STATUS_CHANGE', 'OVERTIME_ALERT', 'BOOKING_REMINDER', 'HOUSEKEEPING_COMPLETE', 'MAINTENANCE_REQUEST', 'CHECK_IN', 'CHECK_OUT', 'ROOM_TRANSFER'
```

#### Order Status (orders.status)
```
Database: ENUM('PENDING','DELIVERED','COMPLETED')
Python:   PENDING, DELIVERED, COMPLETED
API:      'PENDING', 'DELIVERED', 'COMPLETED'
```

#### Order Source (orders.order_source)
```
Database: ENUM('QR_CODE','RECEPTION')
Python:   QR_CODE, RECEPTION
API:      'QR_CODE', 'RECEPTION'
```

#### Product Category (products.category)
```
Database: ENUM('ROOM_AMENITY','FOOD_BEVERAGE')
Python:   ROOM_AMENITY, FOOD_BEVERAGE
API:      'ROOM_AMENITY', 'FOOD_BEVERAGE'
```

#### Settings Data Type (system_settings.data_type)
```
Database: ENUM('string','number','json','boolean')
Python:   STRING, NUMBER, JSON, BOOLEAN
API:      'STRING', 'NUMBER', 'JSON', 'BOOLEAN'
```

### How to Create New Enums
1. **Database Migration**: Define enum with ALL UPPERCASE values only
2. **Python Model**: Create class inheriting from `(str, enum.Enum)` with UPPERCASE keys and values
3. **Pydantic Schema**: Use `Literal` or `Enum` field with UPPERCASE values
4. **Frontend**: Match the exact UPPERCASE values in TypeScript/validation

### Verification Checklist
- [ ] Database enum uses UPPERCASE only
- [ ] Python enum values are UPPERCASE strings (e.g., `OVERNIGHT = "OVERNIGHT"`)
- [ ] Pydantic schemas match Python enum values
- [ ] Frontend components handle UPPERCASE values correctly
- [ ] API tests verify UPPERCASE in request/response bodies

## Testing Strategy

### Coverage Targets
- **Backend**: 80% code coverage (pytest)
- **Frontend**: 60% code coverage (vitest)

### Critical Test Scenarios
1. **Check-in/Check-out Flow**: Test both overnight and temporary stays
2. **Room Transfer**: Verify data migration and housekeeping task creation
3. **Overtime Calculation**: Ensure accurate time tracking and alerts
4. **WebSocket**: Test connection, disconnection, reconnection, and message broadcasting
5. **Booking Integration**: Test booking → check-in → check-out flow with deposit deduction
6. **QR Code Orders**: Test guest orders when room has active check-in

### Manual Testing Checklist (per phase)
- [ ] Feature works as designed
- [ ] UI responsive (mobile/tablet/desktop)
- [ ] Error handling works correctly
- [ ] Real-time updates work
- [ ] Telegram notifications sent successfully
- [ ] Performance acceptable

## UI/UX Guidelines

### Design Principles
1. **Mobile-First**: Design for mobile first, then scale to tablet/desktop
2. **Intuitive Navigation**: Users should find features within 3 clicks
3. **Thai Language First**: Use simple Thai, avoid technical jargon
4. **Immediate Feedback**: Every action has instant feedback (loading states, toasts)
5. **Color-Coded Status**: Rooms use consistent color scheme:
   - Green (เขียว): Available
   - Red (แดง): Occupied
   - Yellow (เหลือง): Cleaning
   - Blue (ฟ้า): Reserved
   - Gray (เทา): Out of Service

### Responsive Breakpoints
- Mobile: 320px - 767px
- Tablet: 768px - 1023px
- Desktop: 1024px+

### Typography
- Font Family: 'Prompt' or 'Sarabun' (Thai-friendly Google Fonts)
- Base font size: 16px

## Important Files & Locations

### Documentation
- `PRD.md` - Complete product requirements (in Thai, 2047 lines)
- `REQ.md` - Original requirements (in Thai)
- `CLAUDE.md` - This file

### Planned Structure (Not yet created)
```
backend/
  app/
    api/v1/endpoints/    # API route handlers
    core/                # Config, security, dependencies
    models/              # SQLAlchemy models
    schemas/             # Pydantic schemas
    services/            # Business logic
    tasks/               # Celery tasks
    db/                  # Database session management
  alembic/versions/      # Database migrations
  tests/

frontend/
  src/
    api/                 # API client
    components/          # Vue components
    views/               # Page views
    stores/              # Pinia stores
    router/              # Vue Router
    composables/         # Composition API utilities
    types/               # TypeScript types

nginx/                   # Nginx configuration
docs/                    # Additional documentation
scripts/                 # Utility scripts
```

## Common Patterns

### Backend Service Pattern
```python
# services/room_service.py
class RoomService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def update_room_status(self, room_id: int, status: RoomStatus):
        # Update database
        room = await self.db.get(Room, room_id)
        room.status = status
        await self.db.commit()

        # Broadcast via WebSocket
        await websocket_manager.broadcast({
            "event": "room_status_changed",
            "data": {...}
        })
```

### Frontend Composable Pattern
```typescript
// composables/useWebSocket.ts
export function useWebSocket() {
  const socket = io(WS_URL)

  onMounted(() => {
    socket.connect()
    socket.on('room_status_changed', handleRoomStatusChange)
  })

  onUnmounted(() => {
    socket.disconnect()
  })

  return { socket }
}
```

## Debugging

### Backend Debugging
- FastAPI auto-generates Swagger UI: `http://localhost:8000/docs`
- ReDoc documentation: `http://localhost:8000/redoc`
- Check logs: `docker-compose logs -f backend`
- Database inspection: Use Adminer at `http://localhost:8080`

### Frontend Debugging
- Vue DevTools: Install browser extension
- Check logs: `docker-compose logs -f frontend`
- Network tab: Monitor API calls and WebSocket messages

### WebSocket Debugging
- Use browser console to inspect WebSocket frames
- Backend logs show connection/disconnection events

## Performance Considerations

### Target Environment
- Production: Digital Ocean Droplet (2GB RAM)
- Expected load: Small hotel (≤50 rooms), ~10 concurrent users

### Optimization Guidelines
1. **Database**: Use indexes on frequently queried columns (status, dates)
2. **WebSocket**: Limit broadcast frequency to prevent overhead
3. **Frontend**: Lazy load components, optimize bundle size
4. **Images**: Compress payment slips and receipts
5. **Caching**: Use Redis for session management and frequently accessed data

## Security Notes

1. **JWT Tokens**: Store in localStorage (acceptable for this use case)
2. **File Uploads**: Validate payment slip files (size, type)
3. **SQL Injection**: Always use SQLAlchemy ORM, never raw SQL
4. **CORS**: Configure Nginx to allow only frontend origin
5. **Environment Variables**: Never commit `.env` files with secrets

## Common Gotchas

1. **Timezone**: All timestamps should use Thai timezone (Asia/Bangkok)
2. **Booking Time Check**: Celery task runs every 30 minutes to check booking no-shows
3. **Room Transfer**: Must validate same room type before allowing transfer
4. **QR Code Access**: Guest can only order if room has active check-in
5. **Daily Report**: Telegram notification sent at 8:00 AM Thai time
6. **WebSocket Reconnection**: Frontend must handle reconnection after network issues

## Next Steps for Development

1. **Phase 0**: Set up Docker environment and project structure
2. Review PRD.md thoroughly before starting each phase
3. Create database schema and migrations for each phase
4. Implement backend API endpoints with tests
5. Build frontend components with responsive design
6. Integrate WebSocket for real-time updates
7. Add Telegram notifications
8. Test thoroughly before moving to next phase

## Additional Resources

- PRD.md contains full system architecture diagrams (lines 126-168)
- Database ER diagram (lines 187-223)
- All database table schemas (lines 225-445)
- Complete feature specifications (lines 463-998)
- UI/UX design guidelines (lines 1001-1154)
- Development phase breakdown (lines 1157-1673)

---

**Key Success Factors**:
1. Maintain phase discipline - test 100% before proceeding
2. Prioritize mobile/tablet UX - this is critical for end users
3. Ensure real-time updates work flawlessly - it's a core differentiator
4. Keep UI simple - target audience has basic education level
5. Test Telegram integration thoroughly - it's essential for operations
