"""
Reports API Endpoints (Phase 8)
Admin/Reception endpoints for viewing reports and analytics
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, timedelta

from app.core.dependencies import get_db, require_role
from app.models.user import User
from app.services.reports_service import ReportsService
from app.schemas.reports import (
    RevenueReportResponse,
    OccupancyReportResponse,
    BookingReportResponse,
    CustomerReportResponse,
    SummaryReportResponse,
    CheckInsListResponse
)

router = APIRouter()


@router.get("/revenue", response_model=RevenueReportResponse)
async def get_revenue_report(
    start_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: date = Query(..., description="End date (YYYY-MM-DD)"),
    group_by: str = Query("day", description="Group by: day or month"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN", "RECEPTION"]))
):
    """
    Get revenue report

    **Permissions**: Admin, Reception

    **Query Parameters**:
    - start_date: Start date for report (YYYY-MM-DD)
    - end_date: End date for report (YYYY-MM-DD)
    - group_by: Group data by "day" or "month"

    **Returns**:
    - Total revenue
    - Revenue by payment method
    - Revenue by stay type
    - Revenue trend over time (chart data)
    """
    service = ReportsService(db)
    return await service.get_revenue_report(start_date, end_date, group_by)


@router.get("/occupancy", response_model=OccupancyReportResponse)
async def get_occupancy_report(
    start_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: date = Query(..., description="End date (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN", "RECEPTION"]))
):
    """
    Get occupancy report

    **Permissions**: Admin, Reception

    **Query Parameters**:
    - start_date: Start date for report (YYYY-MM-DD)
    - end_date: End date for report (YYYY-MM-DD)

    **Returns**:
    - Overall occupancy rate (%)
    - Room status distribution
    - Occupancy trend over time (chart data)
    """
    service = ReportsService(db)
    return await service.get_occupancy_report(start_date, end_date)


@router.get("/bookings", response_model=BookingReportResponse)
async def get_booking_report(
    start_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: date = Query(..., description="End date (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN", "RECEPTION"]))
):
    """
    Get booking report

    **Permissions**: Admin, Reception

    **Query Parameters**:
    - start_date: Start date for report (YYYY-MM-DD)
    - end_date: End date for report (YYYY-MM-DD)

    **Returns**:
    - Total bookings
    - Booking status breakdown
    - Cancellation rate
    - Conversion rate (booking → check-in)
    - Booking trend over time (chart data)
    """
    service = ReportsService(db)
    return await service.get_booking_report(start_date, end_date)


@router.get("/customers", response_model=CustomerReportResponse)
async def get_customer_report(
    limit: int = Query(10, ge=1, le=100, description="Number of top customers"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN", "RECEPTION"]))
):
    """
    Get customer report (top customers)

    **Permissions**: Admin, Reception

    **Query Parameters**:
    - limit: Number of top customers to return (default: 10, max: 100)

    **Returns**:
    - Top customers by total spending
    - Total customers
    - New customers (last 30 days)
    - Returning customers
    """
    service = ReportsService(db)
    return await service.get_customer_report(limit)


@router.get("/summary", response_model=SummaryReportResponse)
async def get_summary_report(
    start_date: date = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: date = Query(None, description="End date (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN", "RECEPTION"]))
):
    """
    Get summary report (dashboard overview)

    **Permissions**: Admin, Reception

    **Query Parameters**:
    - start_date: Start date (default: 7 days ago)
    - end_date: End date (default: today)

    **Returns**:
    - Key metrics summary:
      - Total revenue
      - Occupancy rate
      - Check-ins/Check-outs
      - Bookings
      - Customers
    - Quick stats for dashboard cards
    """
    # Default to last 7 days if not specified
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=7)

    service = ReportsService(db)
    return await service.get_summary_report(start_date, end_date)


@router.get("/check-ins", response_model=CheckInsListResponse)
async def get_checkins_list(
    start_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: date = Query(..., description="End date (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN", "RECEPTION"]))
):
    """
    Get list of all check-ins within date range

    **Permissions**: Admin, Reception

    **Query Parameters**:
    - start_date: Start date for report (YYYY-MM-DD)
    - end_date: End date for report (YYYY-MM-DD)

    **Returns**:
    - List of check-ins with customer and room details
    - Total count and revenue
    - Sortable and filterable table data
    """
    service = ReportsService(db)
    return await service.get_checkins_list(start_date, end_date)
