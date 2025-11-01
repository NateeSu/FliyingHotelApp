"""
Maintenance Task Model (Phase 6)
Manages maintenance and repair tasks
"""
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.db.base import Base


class MaintenanceTaskStatusEnum(str, enum.Enum):
    """Maintenance task status enumeration"""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class MaintenanceTaskPriorityEnum(str, enum.Enum):
    """Maintenance task priority enumeration"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


class MaintenanceTaskCategoryEnum(str, enum.Enum):
    """Maintenance task category enumeration"""
    PLUMBING = "PLUMBING"
    ELECTRICAL = "ELECTRICAL"
    HVAC = "HVAC"
    FURNITURE = "FURNITURE"
    APPLIANCE = "APPLIANCE"
    BUILDING = "BUILDING"
    OTHER = "OTHER"


class MaintenanceTask(Base):
    """
    MaintenanceTask Model
    Represents a maintenance or repair task for a room or facility
    Can be created by reception/housekeeping when issues are found
    """
    __tablename__ = "maintenance_tasks"

    id = Column(Integer, primary_key=True, index=True)

    # Relationships
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=True, index=True)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    # Task information
    status = Column(
        Enum(MaintenanceTaskStatusEnum, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=MaintenanceTaskStatusEnum.PENDING,
        index=True
    )
    priority = Column(
        Enum(MaintenanceTaskPriorityEnum, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=MaintenanceTaskPriorityEnum.MEDIUM
    )
    category = Column(
        Enum(MaintenanceTaskCategoryEnum, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=MaintenanceTaskCategoryEnum.OTHER
    )
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    resolution_notes = Column(Text, nullable=True)
    photos = Column(Text, nullable=True)  # JSON array of photo URLs

    # Time tracking
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    duration_minutes = Column(Integer, nullable=True)  # Auto-calculated duration

    # Tracking
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    completed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    room = relationship("Room", back_populates="maintenance_tasks")
    assigned_user = relationship("User", foreign_keys=[assigned_to], back_populates="assigned_maintenance_tasks")
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_maintenance_tasks")
    completer = relationship("User", foreign_keys=[completed_by], back_populates="completed_maintenance_tasks")

    def __repr__(self):
        return f"<MaintenanceTask(id={self.id}, room_id={self.room_id}, status={self.status}, category={self.category})>"
