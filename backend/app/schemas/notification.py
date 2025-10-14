"""
Notification Schemas (Phase 3)
Pydantic models for API request/response validation
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

from app.models.notification import NotificationTypeEnum, TargetRoleEnum


# Base schemas
class NotificationBase(BaseModel):
    """Base notification schema"""
    notification_type: NotificationTypeEnum
    target_role: TargetRoleEnum
    title: str = Field(..., max_length=255)
    message: str
    room_id: Optional[int] = None


class NotificationCreate(NotificationBase):
    """Schema for creating a notification"""
    pass


class NotificationUpdate(BaseModel):
    """Schema for updating a notification"""
    is_read: Optional[bool] = None


class NotificationResponse(NotificationBase):
    """Schema for notification response"""
    id: int
    is_read: bool
    read_at: Optional[datetime] = None
    telegram_sent: bool
    telegram_message_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    """Schema for notification list response"""
    data: list[NotificationResponse]
    total: int
    unread_count: int


class NotificationMarkAllReadResponse(BaseModel):
    """Schema for mark all as read response"""
    message: str
    marked_count: int
