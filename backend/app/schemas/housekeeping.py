"""
Housekeeping Schemas (Phase 5)
Pydantic models for housekeeping task API validation
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

from app.models.housekeeping_task import (
    HousekeepingTaskStatusEnum,
    HousekeepingTaskPriorityEnum
)


# Base schemas
class HousekeepingTaskCreate(BaseModel):
    """Schema for creating a housekeeping task"""
    room_id: int = Field(..., description="Room ID to clean")
    check_in_id: Optional[int] = Field(None, description="Related check-in ID (if from checkout)")
    title: str = Field(..., max_length=255, description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    priority: HousekeepingTaskPriorityEnum = Field(
        default=HousekeepingTaskPriorityEnum.MEDIUM,
        description="Task priority"
    )
    assigned_to: Optional[int] = Field(None, description="User ID to assign task to")
    notes: Optional[str] = Field(None, description="Additional notes")

    class Config:
        json_schema_extra = {
            "example": {
                "room_id": 101,
                "check_in_id": 50,
                "title": "ทำความสะอาดห้อง 101",
                "description": "ทำความสะอาดปกติหลังลูกค้าเช็คเอาท์",
                "priority": "MEDIUM",
                "assigned_to": None,
                "notes": None
            }
        }


class HousekeepingTaskUpdate(BaseModel):
    """Schema for updating a housekeeping task"""
    status: Optional[HousekeepingTaskStatusEnum] = None
    priority: Optional[HousekeepingTaskPriorityEnum] = None
    assigned_to: Optional[int] = None
    notes: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "status": "IN_PROGRESS",
                "assigned_to": 5
            }
        }


class HousekeepingTaskResponse(BaseModel):
    """Schema for housekeeping task response"""
    id: int
    room_id: int
    check_in_id: Optional[int] = None
    assigned_to: Optional[int] = None
    status: HousekeepingTaskStatusEnum
    priority: HousekeepingTaskPriorityEnum
    title: str
    description: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    created_by: int
    completed_by: Optional[int] = None
    updated_at: datetime

    class Config:
        from_attributes = True
        use_enum_values = True


class HousekeepingTaskWithDetails(HousekeepingTaskResponse):
    """Schema for housekeeping task with room and user details"""
    room_number: str
    room_type_name: str
    assigned_user_name: Optional[str] = None
    creator_name: str
    completer_name: Optional[str] = None

    class Config:
        from_attributes = True
        use_enum_values = True


class HousekeepingTaskListResponse(BaseModel):
    """Schema for housekeeping task list response"""
    data: list[HousekeepingTaskWithDetails]
    total: int


# Start/Complete Task Schemas
class HousekeepingTaskStartRequest(BaseModel):
    """Schema for starting a housekeeping task"""
    started_at: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "started_at": "2024-10-19T14:00:00"
            }
        }


class HousekeepingTaskCompleteRequest(BaseModel):
    """Schema for completing a housekeeping task"""
    completed_at: Optional[datetime] = None
    notes: Optional[str] = Field(None, max_length=500, description="Completion notes")

    class Config:
        json_schema_extra = {
            "example": {
                "completed_at": "2024-10-19T14:30:00",
                "notes": "ทำความสะอาดเสร็จแล้ว พร้อมให้บริการ"
            }
        }


# Statistics Schema
class HousekeepingStats(BaseModel):
    """Schema for housekeeping statistics"""
    total_tasks: int
    pending_tasks: int
    in_progress_tasks: int
    completed_today: int
    avg_duration_minutes: Optional[float] = None

    class Config:
        json_schema_extra = {
            "example": {
                "total_tasks": 50,
                "pending_tasks": 5,
                "in_progress_tasks": 2,
                "completed_today": 10,
                "avg_duration_minutes": 25.5
            }
        }
