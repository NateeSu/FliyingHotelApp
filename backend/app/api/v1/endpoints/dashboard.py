"""
Dashboard API Endpoints (Phase 3)
Provides room status and statistics for the dashboard
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import List

from app.core.dependencies import get_db, get_current_user
from app.models import User
from app.services import DashboardService
from app.schemas.dashboard import DashboardResponse, DashboardRoomCard, DashboardStats, OvertimeAlertsResponse

router = APIRouter()


@router.get("/", response_model=DashboardResponse)
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get complete dashboard data (rooms + stats)

    Requires authentication.

    Returns:
        - rooms: List of all rooms with current status and check-in details
        - stats: Dashboard statistics (occupancy, revenue, etc.)
        - last_updated: Timestamp of when data was fetched
    """
    service = DashboardService(db)

    # Get rooms and stats in parallel
    rooms = await service.get_all_rooms_with_details()
    stats = await service.get_dashboard_stats()

    return DashboardResponse(
        rooms=rooms,
        stats=stats,
        last_updated=datetime.utcnow()
    )


@router.get("/rooms", response_model=List[DashboardRoomCard])
async def get_dashboard_rooms(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all rooms with check-in details for dashboard

    Requires authentication.

    Returns:
        List of room cards with full information
    """
    service = DashboardService(db)
    rooms = await service.get_all_rooms_with_details()
    return rooms


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get dashboard statistics

    Requires authentication.

    Returns:
        Dashboard statistics (occupancy rate, revenue, check-in counts, etc.)
    """
    service = DashboardService(db)
    stats = await service.get_dashboard_stats()
    return stats


@router.get("/overtime-alerts", response_model=OvertimeAlertsResponse)
async def get_overtime_alerts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all rooms with overtime check-ins

    Requires authentication.

    Returns:
        List of overtime alerts with room and guest information
    """
    service = DashboardService(db)
    alerts = await service.get_overtime_alerts()

    return OvertimeAlertsResponse(
        data=alerts,
        total=len(alerts)
    )
