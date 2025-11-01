from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator
import enum


class MaintenanceTaskStatusEnum(str, enum.Enum):
    """Maintenance task status"""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class MaintenanceTaskPriorityEnum(str, enum.Enum):
    """Maintenance task priority"""
    URGENT = "URGENT"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class MaintenanceTaskCategoryEnum(str, enum.Enum):
    """Maintenance task category"""
    PLUMBING = "PLUMBING"
    ELECTRICAL = "ELECTRICAL"
    HVAC = "HVAC"
    FURNITURE = "FURNITURE"
    APPLIANCE = "APPLIANCE"
    BUILDING = "BUILDING"
    OTHER = "OTHER"


class MaintenanceTaskBase(BaseModel):
    """Base maintenance task schema"\n    room_id: int = Field(..., description="Room ID")
    category: MaintenanceTaskCategoryEnum = Field(..., description="Maintenance category")
    title: str = Field(..., min_length=1, max_length=255, description="Task title")
    description: Optional[str] = Field(None, max_length=1000, description="Task description")
    priority: MaintenanceTaskPriorityEnum = Field(
        default=MaintenanceTaskPriorityEnum.MEDIUM,
        description="Task priority"
    )
    assigned_to: Optional[int] = Field(None, description="Assigned user ID")
    notes: Optional[str] = Field(None, max_length=1000, description="Task notes")
    photos: Optional[list[str]] = Field(None, description="List of photo URLs")

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip()


class MaintenanceTaskCreate(MaintenanceTaskBase):
    """Create maintenance task schema"""
    pass


class MaintenanceTaskUpdate(BaseModel):
    """Update maintenance task schema"""
    category: Optional[MaintenanceTaskCategoryEnum] = None
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    priority: Optional[MaintenanceTaskPriorityEnum] = None
    assigned_to: Optional[int] = None
    notes: Optional[str] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not v.strip():
                raise ValueError("Title cannot be empty")
            return v.strip()
        return v


class MaintenanceTaskStartRequest(BaseModel):
    """Start maintenance task request"""
    started_at: Optional[datetime] = Field(
        default=None,
        description="Start time (defaults to now)"
    )


class MaintenanceTaskCompleteRequest(BaseModel):
    """Complete maintenance task request"""
    completed_at: Optional[datetime] = Field(
        default=None,
        description="Completion time (defaults to now)"
    )
    notes: Optional[str] = Field(
        None,
        max_length=1000,
        description="Completion notes"
    )


class MaintenanceTaskResponse(MaintenanceTaskBase):
    """Maintenance task response schema"""
    id: int
    status: MaintenanceTaskStatusEnum
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    completed_by: Optional[int] = None
    duration_minutes: Optional[int] = None

    model_config = {"from_attributes": True, "use_enum_values": True}


class MaintenanceTaskWithDetails(MaintenanceTaskResponse):
    """Maintenance task with detailed information"""
    room_number: str = Field(..., description="Room number")
    room_type_name: str = Field(..., description="Room type name")
    assigned_user_name: Optional[str] = Field(None, description="Assigned user name")
    creator_name: str = Field(..., description="Creator name")
    completer_name: Optional[str] = Field(None, description="Completer name")


class MaintenanceTaskListResponse(BaseModel):
    """List of maintenance tasks response"""
    tasks: list[MaintenanceTaskWithDetails]
    total: int
    skip: int
    limit: int


class MaintenanceTaskFilters(BaseModel):
    """Maintenance task filters"""
    status: Optional[MaintenanceTaskStatusEnum] = None
    priority: Optional[MaintenanceTaskPriorityEnum] = None
    category: Optional[MaintenanceTaskCategoryEnum] = None
    assigned_to: Optional[int] = None
    room_id: Optional[int] = None


class MaintenanceStats(BaseModel):
    """Maintenance statistics"""
    total_tasks: int = Field(..., description="Total tasks")
    pending_tasks: int = Field(..., description="Pending tasks")
    in_progress_tasks: int = Field(..., description="In-progress tasks")
    completed_today: int = Field(..., description="Tasks completed today")
    avg_duration_minutes: Optional[float] = Field(
        None,
        description="Average task duration in minutes"
    )
    by_category: dict[str, int] = Field(
        default_factory=dict,
        description="Task count by category"
    )
    by_priority: dict[str, int] = Field(
        default_factory=dict,
        description="Task count by priority"
    )
