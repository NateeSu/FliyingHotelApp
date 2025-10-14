from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, room_types, rooms, room_rates, dashboard, notifications, websocket, check_ins, customers

api_router = APIRouter()

# Authentication endpoints
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

# User management endpoints
api_router.include_router(
    users.router,
    prefix="/users",
    tags=["User Management"]
)

# Phase 2: Room Management endpoints
api_router.include_router(
    room_types.router,
    prefix="/room-types",
    tags=["Room Types"]
)

api_router.include_router(
    rooms.router,
    prefix="/rooms",
    tags=["Rooms"]
)

api_router.include_router(
    room_rates.router,
    prefix="/room-rates",
    tags=["Room Rates"]
)

# Phase 3: Dashboard and Real-time endpoints
api_router.include_router(
    dashboard.router,
    prefix="/dashboard",
    tags=["Dashboard"]
)

api_router.include_router(
    notifications.router,
    prefix="/notifications",
    tags=["Notifications"]
)

# WebSocket endpoint (no /api/v1 prefix, registered separately in main.py)
# Included here for Swagger documentation
api_router.include_router(
    websocket.router,
    prefix="/ws",
    tags=["WebSocket"]
)

# Phase 4: Check-In/Check-Out endpoints
api_router.include_router(
    check_ins.router,
    prefix="/check-ins",
    tags=["Check-Ins"]
)

api_router.include_router(
    customers.router,
    prefix="/customers",
    tags=["Customers"]
)
