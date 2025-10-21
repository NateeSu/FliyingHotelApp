"""
Housekeeping Task Model (Phase 5)
Manages room cleaning tasks
"""
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.db.base import Base


class HousekeepingTaskStatusEnum(str, enum.Enum):
    """Housekeeping task status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class HousekeepingTaskPriorityEnum(str, enum.Enum):
    """Housekeeping task priority enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class HousekeepingTask(Base):
    """
    HousekeepingTask Model
    Represents a cleaning task for a room
    Created automatically after checkout or room transfer
    """
    __tablename__ = "housekeeping_tasks"

    id = Column(Integer, primary_key=True, index=True)

    # Relationships
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False, index=True)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    check_in_id = Column(Integer, ForeignKey("check_ins.id"), nullable=True, index=True)

    # Task information
    status = Column(
        Enum(HousekeepingTaskStatusEnum, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=HousekeepingTaskStatusEnum.PENDING,
        index=True
    )
    priority = Column(
        Enum(HousekeepingTaskPriorityEnum, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=HousekeepingTaskPriorityEnum.MEDIUM
    )
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

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
    room = relationship("Room", back_populates="housekeeping_tasks")
    assigned_user = relationship("User", foreign_keys=[assigned_to], back_populates="assigned_housekeeping_tasks")
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_housekeeping_tasks")
    completer = relationship("User", foreign_keys=[completed_by], back_populates="completed_housekeeping_tasks")
    check_in = relationship("CheckIn", back_populates="housekeeping_tasks")

    def __repr__(self):
        return f"<HousekeepingTask(id={self.id}, room_id={self.room_id}, status={self.status})>"
