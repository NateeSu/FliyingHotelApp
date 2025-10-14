from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class RoomTypeBase(BaseModel):
    """Base schema for RoomType"""
    name: str = Field(..., min_length=1, max_length=50, description="ชื่อประเภทห้อง")
    description: Optional[str] = Field(None, description="คำอธิบายประเภทห้อง")
    amenities: Optional[List[str]] = Field(None, description="สิ่งอำนวยความสะดวก")
    max_guests: int = Field(default=2, ge=1, le=10, description="จำนวนผู้พักสูงสุด")
    bed_type: Optional[str] = Field(None, max_length=50, description="ประเภทเตียง")
    room_size_sqm: Optional[float] = Field(None, ge=0, description="ขนาดห้อง (ตารางเมตร)")
    is_active: bool = Field(default=True, description="สถานะการใช้งาน")


class RoomTypeCreate(RoomTypeBase):
    """Schema for creating a new room type"""
    pass


class RoomTypeUpdate(BaseModel):
    """Schema for updating an existing room type"""
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="ชื่อประเภทห้อง")
    description: Optional[str] = Field(None, description="คำอธิบายประเภทห้อง")
    amenities: Optional[List[str]] = Field(None, description="สิ่งอำนวยความสะดวก")
    max_guests: Optional[int] = Field(None, ge=1, le=10, description="จำนวนผู้พักสูงสุด")
    bed_type: Optional[str] = Field(None, max_length=50, description="ประเภทเตียง")
    room_size_sqm: Optional[float] = Field(None, ge=0, description="ขนาดห้อง (ตารางเมตร)")
    is_active: Optional[bool] = Field(None, description="สถานะการใช้งาน")


class RoomTypeResponse(RoomTypeBase):
    """Schema for room type response"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RoomTypeWithStats(RoomTypeResponse):
    """Schema for room type with statistics"""
    total_rooms: int = Field(default=0, description="จำนวนห้องทั้งหมด")
    available_rooms: int = Field(default=0, description="จำนวนห้องว่าง")
