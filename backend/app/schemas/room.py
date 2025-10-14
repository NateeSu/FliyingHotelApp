from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.room import RoomStatus


class RoomBase(BaseModel):
    """Base schema for Room"""
    room_number: str = Field(..., min_length=1, max_length=10, description="หมายเลขห้อง")
    room_type_id: int = Field(..., gt=0, description="ID ประเภทห้อง")
    floor: int = Field(..., ge=1, description="ชั้น")
    notes: Optional[str] = Field(None, description="หมายเหตุ")
    is_active: bool = Field(default=True, description="สถานะการใช้งาน")


class RoomCreate(RoomBase):
    """Schema for creating a new room"""
    pass


class RoomUpdate(BaseModel):
    """Schema for updating an existing room"""
    room_number: Optional[str] = Field(None, min_length=1, max_length=10, description="หมายเลขห้อง")
    room_type_id: Optional[int] = Field(None, gt=0, description="ID ประเภทห้อง")
    floor: Optional[int] = Field(None, ge=1, description="ชั้น")
    status: Optional[RoomStatus] = Field(None, description="สถานะห้อง")
    notes: Optional[str] = Field(None, description="หมายเหตุ")
    is_active: Optional[bool] = Field(None, description="สถานะการใช้งาน")


class RoomStatusUpdate(BaseModel):
    """Schema for updating room status only"""
    status: RoomStatus = Field(..., description="สถานะห้องใหม่")


class RoomResponse(RoomBase):
    """Schema for room response"""
    id: int
    status: RoomStatus
    qr_code: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RoomWithRoomType(RoomResponse):
    """Schema for room response with room type details"""
    room_type: Optional[dict] = Field(None, description="ข้อมูลประเภทห้อง")

    class Config:
        from_attributes = True


class RoomListResponse(BaseModel):
    """Schema for paginated room list"""
    total: int
    skip: int
    limit: int
    items: list[RoomResponse]
