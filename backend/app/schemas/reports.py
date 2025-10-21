"""
Reports Schemas (Phase 8)
Pydantic schemas for reports API responses
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import date, datetime
from decimal import Decimal


# ============================================================================
# Revenue Report Schemas
# ============================================================================

class RevenueByPeriod(BaseModel):
    """Revenue data point for chart"""
    period: str  # "2025-01-15" or "2025-01"
    revenue: float
    count: int  # number of transactions


class RevenueReportResponse(BaseModel):
    """Revenue report response"""
    total_revenue: float
    total_transactions: int
    average_transaction: float
    by_payment_method: Dict[str, float]  # {"cash": 5000, "transfer": 3000}
    by_stay_type: Dict[str, float]  # {"overnight": 8000, "temporary": 2000}
    by_period: List[RevenueByPeriod]  # Chart data
    start_date: date
    end_date: date


# ============================================================================
# Occupancy Report Schemas
# ============================================================================

class OccupancyByPeriod(BaseModel):
    """Occupancy data point for chart"""
    period: str  # "2025-01-15"
    occupancy_rate: float  # percentage
    occupied_rooms: int
    total_rooms: int


class RoomStatusDistribution(BaseModel):
    """Room status distribution"""
    available: int
    occupied: int
    cleaning: int
    reserved: int
    out_of_service: int


class OccupancyReportResponse(BaseModel):
    """Occupancy report response"""
    occupancy_rate: float  # Overall percentage
    total_rooms: int
    occupied_rooms: int
    available_rooms: int
    room_status_distribution: RoomStatusDistribution
    by_period: List[OccupancyByPeriod]  # Chart data
    start_date: date
    end_date: date


# ============================================================================
# Booking Report Schemas
# ============================================================================

class BookingByPeriod(BaseModel):
    """Booking data point for chart"""
    period: str  # "2025-01"
    total_bookings: int
    confirmed: int
    cancelled: int
    checked_in: int


class BookingReportResponse(BaseModel):
    """Booking report response"""
    total_bookings: int
    confirmed_bookings: int
    cancelled_bookings: int
    checked_in_bookings: int
    cancellation_rate: float  # percentage
    conversion_rate: float  # (checked_in / confirmed) * 100
    total_deposit: float
    by_period: List[BookingByPeriod]  # Chart data
    start_date: date
    end_date: date


# ============================================================================
# Customer Report Schemas
# ============================================================================

class TopCustomer(BaseModel):
    """Top customer data"""
    customer_id: int
    full_name: str
    phone_number: str
    total_spending: float
    visit_count: int
    last_visit: Optional[datetime]


class CustomerReportResponse(BaseModel):
    """Customer report response"""
    top_customers: List[TopCustomer]
    total_customers: int
    new_customers: int  # Customers with first visit in date range
    returning_customers: int  # Customers with > 1 visit


# ============================================================================
# Summary Report Schemas
# ============================================================================

class QuickStat(BaseModel):
    """Quick stat for dashboard"""
    label: str
    value: str
    change: Optional[float] = None  # percentage change vs previous period
    trend: Optional[str] = None  # "up" | "down" | "neutral"


class SummaryReportResponse(BaseModel):
    """Summary report for dashboard overview"""
    # Revenue
    total_revenue: float
    revenue_vs_previous: Optional[float] = None

    # Occupancy
    occupancy_rate: float
    occupancy_vs_previous: Optional[float] = None

    # Check-ins/outs
    total_checkins: int
    total_checkouts: int

    # Bookings
    total_bookings: int
    bookings_vs_previous: Optional[float] = None

    # Customers
    total_customers: int
    new_customers: int

    # Quick stats for cards
    quick_stats: List[QuickStat]

    # Date range
    start_date: date
    end_date: date
