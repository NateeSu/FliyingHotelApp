"""
Booking Schemas (Phase 7)
Pydantic models for booking system
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal


# ==================== Base Schemas ====================

class BookingBase(BaseModel):
    """Base booking schema"""
    customer_id: int = Field(..., description="Customer ID")
    room_id: int = Field(..., description="Room ID")
    check_in_date: date = Field(..., description="Check-in date")
    check_out_date: date = Field(..., description="Check-out date")
    total_amount: Decimal = Field(..., ge=0, description="Total booking amount")
    deposit_amount: Decimal = Field(default=Decimal(0), ge=0, description="Deposit amount")
    notes: Optional[str] = Field(None, max_length=1000, description="Booking notes")

    @field_validator('check_out_date')
    @classmethod
    def validate_checkout_after_checkin(cls, v, info):
        """Validate check-out date is after check-in date"""
        if 'check_in_date' in info.data and v <= info.data['check_in_date']:
            raise ValueError('Check-out date must be after check-in date')
        return v

    @field_validator('deposit_amount')
    @classmethod
    def validate_deposit_not_exceed_total(cls, v, info):
        """Validate deposit does not exceed total amount"""
        if 'total_amount' in info.data and v > info.data['total_amount']:
            raise ValueError('Deposit amount cannot exceed total amount')
        return v


class BookingCreate(BookingBase):
    """Schema for creating a new booking"""
    pass


class BookingUpdate(BaseModel):
    """Schema for updating a booking"""
    check_in_date: Optional[date] = None
    check_out_date: Optional[date] = None
    total_amount: Optional[Decimal] = Field(None, ge=0)
    deposit_amount: Optional[Decimal] = Field(None, ge=0)
    notes: Optional[str] = Field(None, max_length=1000)

    @field_validator('check_out_date')
    @classmethod
    def validate_checkout_after_checkin(cls, v, info):
        """Validate check-out date is after check-in date"""
        if v and 'check_in_date' in info.data and info.data['check_in_date']:
            if v <= info.data['check_in_date']:
                raise ValueError('Check-out date must be after check-in date')
        return v


class BookingResponse(BookingBase):
    """Schema for booking response"""
    id: int
    number_of_nights: int
    status: str
    created_by: int
    created_at: datetime
    updated_at: datetime
    cancelled_at: Optional[datetime] = None

    # Related data
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    room_number: Optional[str] = None
    room_type_name: Optional[str] = None
    creator_name: Optional[str] = None

    class Config:
        from_attributes = True


class BookingListResponse(BaseModel):
    """Schema for booking list response"""
    data: List[BookingResponse]
    total: int
    skip: int
    limit: int


# ==================== Calendar Schemas ====================

class BookingCalendarEvent(BaseModel):
    """Schema for calendar event"""
    id: int
    title: str
    start: date
    end: date
    color: str
    status: str
    room_number: str
    customer_name: str
    deposit_amount: Decimal
    total_amount: Decimal

    class Config:
        from_attributes = True


class PublicHoliday(BaseModel):
    """Schema for Thai public holiday"""
    date: date
    name: str  # Thai name
    name_en: str  # English name

    class Config:
        from_attributes = True


# ==================== Special Schemas ====================

class RoomAvailabilityCheck(BaseModel):
    """Schema for room availability check request"""
    room_id: int
    check_in_date: date
    check_out_date: date
    exclude_booking_id: Optional[int] = None  # For editing existing booking


class RoomAvailabilityResponse(BaseModel):
    """Schema for room availability check response"""
    available: bool
    conflicting_bookings: List[BookingResponse] = []


class BookingConfirmRequest(BaseModel):
    """Schema for confirming a booking"""
    booking_id: int


class BookingStats(BaseModel):
    """Schema for booking statistics"""
    total_bookings: int
    pending: int
    confirmed: int
    checked_in: int
    completed: int
    cancelled: int
    total_revenue: Decimal
    total_deposits: Decimal


class BookingReminderData(BaseModel):
    """Schema for booking reminder notification"""
    booking_id: int
    room_number: str
    customer_name: str
    customer_phone: str
    check_in_date: date
    overdue_minutes: int
    deposit_amount: Decimal

    class Config:
        from_attributes = True
