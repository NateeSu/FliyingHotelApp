"""
Customer Schemas (Phase 4)
Pydantic models for customer API request/response validation
"""
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional
from decimal import Decimal


class CustomerCreate(BaseModel):
    """Schema for creating a customer"""
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    phone_number: Optional[str] = Field(None, min_length=9, max_length=20)
    email: Optional[EmailStr] = None
    id_card_number: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    notes: Optional[str] = None


class CustomerUpdate(BaseModel):
    """Schema for updating a customer"""
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    phone_number: Optional[str] = Field(None, min_length=10, max_length=20)
    email: Optional[EmailStr] = None
    id_card_number: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    notes: Optional[str] = None


class CustomerResponse(BaseModel):
    """Schema for customer response"""
    id: int
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    id_card_number: Optional[str] = None
    address: Optional[str] = None
    total_visits: int
    total_spent: Decimal = Decimal('0.00')  # Default to 0, will be calculated from check_ins/bookings
    last_visit_date: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CustomerSearchResult(BaseModel):
    """Schema for customer search result (autocomplete)"""
    id: int
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    total_visits: int
    last_visit_date: Optional[datetime] = None

    class Config:
        from_attributes = True


class CustomerListResponse(BaseModel):
    """Schema for customer list response"""
    data: list[CustomerResponse]
    total: int
