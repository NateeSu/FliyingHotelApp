from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import date, datetime
from app.models.room_rate import StayType


class RoomRateBase(BaseModel):
    """Base schema for RoomRate"""
    room_type_id: int = Field(..., gt=0, description="ID ประเภทห้อง")
    stay_type: StayType = Field(..., description="ประเภทการเข้าพัก (overnight/temporary)")
    rate: float = Field(..., ge=0, description="ราคา (บาท)")
    effective_from: date = Field(..., description="วันที่เริ่มใช้ราคา")
    effective_to: Optional[date] = Field(None, description="วันที่สิ้นสุดราคา (NULL = ไม่มีวันสิ้นสุด)")
    is_active: bool = Field(default=True, description="สถานะการใช้งาน")

    @field_validator('effective_to')
    @classmethod
    def validate_dates(cls, v: Optional[date], info) -> Optional[date]:
        """Validate that effective_to is after effective_from"""
        if v and 'effective_from' in info.data:
            effective_from = info.data['effective_from']
            if v < effective_from:
                raise ValueError('วันที่สิ้นสุดต้องมากกว่าวันที่เริ่มต้น')
        return v

    @field_validator('rate')
    @classmethod
    def validate_rate(cls, v: float) -> float:
        """Validate that rate is positive"""
        if v < 0:
            raise ValueError('ราคาต้องเป็นจำนวนบวก')
        if v > 999999.99:
            raise ValueError('ราคาสูงเกินไป')
        return v


class RoomRateCreate(RoomRateBase):
    """Schema for creating a new room rate"""
    pass


class RoomRateUpdate(BaseModel):
    """Schema for updating an existing room rate"""
    rate: Optional[float] = Field(None, ge=0, description="ราคา (บาท)")
    effective_to: Optional[date] = Field(None, description="วันที่สิ้นสุดราคา")
    is_active: Optional[bool] = Field(None, description="สถานะการใช้งาน")

    @field_validator('rate')
    @classmethod
    def validate_rate(cls, v: Optional[float]) -> Optional[float]:
        """Validate that rate is positive"""
        if v is not None:
            if v < 0:
                raise ValueError('ราคาต้องเป็นจำนวนบวก')
            if v > 999999.99:
                raise ValueError('ราคาสูงเกินไป')
        return v


class RoomRateResponse(RoomRateBase):
    """Schema for room rate response"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RoomRateWithRoomType(RoomRateResponse):
    """Schema for room rate response with room type details"""
    room_type: Optional[dict] = Field(None, description="ข้อมูลประเภทห้อง")


class RoomRateMatrix(BaseModel):
    """Schema for room rate matrix view (for UI)"""
    room_type_id: int
    room_type_name: str
    overnight_rate: Optional[float] = None
    temporary_rate: Optional[float] = None
    overnight_rate_id: Optional[int] = None
    temporary_rate_id: Optional[int] = None
