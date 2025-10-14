"""
Check-In Schemas (Phase 4)
Pydantic models for API request/response validation
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from decimal import Decimal

from app.models.check_in import StayTypeEnum, PaymentMethodEnum, CheckInStatusEnum


# Base schemas
class CheckInCreate(BaseModel):
    """Schema for creating a check-in"""
    room_id: int
    stay_type: StayTypeEnum
    number_of_nights: Optional[int] = None
    number_of_guests: int = Field(default=1, ge=1)
    check_in_time: Optional[datetime] = None
    booking_id: Optional[int] = None
    deposit_amount: Optional[Decimal] = None
    payment_method: PaymentMethodEnum
    notes: Optional[str] = None


class CheckInCreateWithCustomer(BaseModel):
    """Schema for creating a check-in with customer data"""
    # Check-in fields
    room_id: int
    stay_type: StayTypeEnum
    number_of_nights: Optional[int] = None
    number_of_guests: int = Field(default=1, ge=1)
    check_in_time: Optional[datetime] = None
    booking_id: Optional[int] = None
    deposit_amount: Optional[Decimal] = None
    payment_method: PaymentMethodEnum
    notes: Optional[str] = None

    # Nested customer data
    customer_data: dict  # Will be validated as CustomerCreate


class CheckInUpdate(BaseModel):
    """Schema for updating a check-in (Phase 4)"""
    extra_charges: Optional[Decimal] = None
    discount_amount: Optional[Decimal] = None
    discount_reason: Optional[str] = None
    payment_method: Optional[PaymentMethodEnum] = None
    payment_slip_url: Optional[str] = None
    notes: Optional[str] = None


class CheckInResponse(BaseModel):
    """Schema for check-in response"""
    id: int
    room_id: int
    customer_id: int
    booking_id: Optional[int] = None
    stay_type: StayTypeEnum
    number_of_nights: Optional[int] = None
    number_of_guests: int
    check_in_time: datetime
    expected_check_out_time: datetime
    actual_check_out_time: Optional[datetime] = None
    is_overtime: bool
    overtime_minutes: Optional[int] = None
    overtime_charge: Decimal
    base_amount: Decimal
    extra_charges: Decimal
    discount_amount: Decimal
    discount_reason: Optional[str] = None
    total_amount: Decimal
    payment_method: Optional[PaymentMethodEnum] = None
    payment_slip_url: Optional[str] = None
    status: CheckInStatusEnum
    notes: Optional[str] = None
    created_by: int
    checked_out_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CheckInWithDetails(CheckInResponse):
    """Schema for check-in with customer and room details"""
    customer_name: str
    customer_phone: str
    room_number: str
    room_type_name: str

    class Config:
        from_attributes = True


class CheckInListResponse(BaseModel):
    """Schema for check-in list response"""
    data: list[CheckInResponse]
    total: int


# Check-Out Schemas
class CheckOutRequest(BaseModel):
    """Schema for check-out request"""
    actual_check_out_time: Optional[datetime] = None
    extra_charges: Optional[Decimal] = Field(default=0, ge=0)
    discount_amount: Optional[Decimal] = Field(default=0, ge=0)
    discount_reason: Optional[str] = None
    payment_method: PaymentMethodEnum
    payment_notes: Optional[str] = None


class CheckOutSummary(BaseModel):
    """Schema for checkout summary calculation"""
    check_in_id: int
    room_number: str
    customer_name: str
    stay_type: StayTypeEnum
    check_in_time: datetime
    expected_check_out_time: datetime
    actual_check_out_time: datetime
    base_amount: Decimal
    is_overtime: bool
    overtime_minutes: Optional[int] = None
    overtime_charge: Decimal
    extra_charges: Decimal
    discount_amount: Decimal
    total_amount: Decimal

    class Config:
        from_attributes = True
