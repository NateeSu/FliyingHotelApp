from sqlalchemy import Column, Integer, Enum, DECIMAL, Date, Boolean, ForeignKey, TIMESTAMP, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
import enum


class StayType(str, enum.Enum):
    """
    Stay Type Enum
    - overnight: ค้างคืน (13:00 check-in, 12:00 check-out)
    - temporary: ชั่วคราว (3 hours session)
    """
    OVERNIGHT = "OVERNIGHT"
    TEMPORARY = "TEMPORARY"


class RoomRate(Base):
    """
    RoomRate Model - อัตราค่าห้องพัก

    Relationships:
    - room_type: Many-to-One with RoomType

    Business Rules:
    - Each room_type + stay_type combination must have an active rate
    - effective_from and effective_to dates must not overlap for same room_type + stay_type
    - effective_to = NULL means current active rate
    - Cannot delete rate if referenced by bookings/check-ins
    """
    __tablename__ = "room_rates"

    id = Column(Integer, primary_key=True, index=True)
    room_type_id = Column(Integer, ForeignKey("room_types.id", ondelete="RESTRICT"), nullable=False, index=True)
    stay_type = Column(Enum(StayType), nullable=False)
    rate = Column(DECIMAL(10, 2), nullable=False)
    effective_from = Column(Date, nullable=False, index=True)
    effective_to = Column(Date, nullable=True, index=True)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    room_type = relationship("RoomType", back_populates="room_rates")

    # Unique constraint: room_type + stay_type + effective_from must be unique
    __table_args__ = (
        UniqueConstraint('room_type_id', 'stay_type', 'effective_from', name='uk_room_rates'),
    )

    def __repr__(self):
        return f"<RoomRate(id={self.id}, room_type_id={self.room_type_id}, stay_type='{self.stay_type.value}', rate={self.rate})>"
