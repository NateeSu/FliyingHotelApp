"""
Dashboard Schemas (Phase 3)
Pydantic models for dashboard API responses
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from decimal import Decimal

from app.models.room import RoomStatus
from app.models.check_in import StayTypeEnum


class DashboardRoomCard(BaseModel):
    """Schema for room card display on dashboard"""
    # Room information
    id: int
    room_number: str
    floor: int
    status: RoomStatus

    # Room type information
    room_type_id: int
    room_type_name: str
    room_type_description: Optional[str] = None

    # Check-in information (if occupied)
    check_in_id: Optional[int] = None
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    stay_type: Optional[StayTypeEnum] = None
    check_in_time: Optional[datetime] = None
    expected_check_out_time: Optional[datetime] = None

    # Overtime information
    is_overtime: bool = False
    overtime_minutes: Optional[int] = None

    # Additional info
    qr_code: Optional[str] = None
    notes: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    """Schema for dashboard statistics"""
    total_rooms: int
    available_rooms: int
    occupied_rooms: int
    cleaning_rooms: int
    reserved_rooms: int
    out_of_service_rooms: int
    occupancy_rate: float  # Percentage

    # Check-in statistics
    total_check_ins_today: int
    overnight_stays: int
    temporary_stays: int

    # Revenue statistics (today)
    revenue_today: Decimal


class DashboardResponse(BaseModel):
    """Schema for complete dashboard response"""
    rooms: list[DashboardRoomCard]
    stats: DashboardStats
    last_updated: datetime


class OvertimeAlert(BaseModel):
    """Schema for overtime alert"""
    room_id: int
    room_number: str
    check_in_id: int
    customer_name: str
    stay_type: StayTypeEnum
    expected_check_out_time: datetime
    overtime_minutes: int
    created_at: datetime

    class Config:
        from_attributes = True


class OvertimeAlertsResponse(BaseModel):
    """Schema for overtime alerts response"""
    data: list[OvertimeAlert]
    total: int
