"""
Booking Model (Phase 3 - Basic, Full implementation in Phase 7)
Handles room reservations
"""
from sqlalchemy import Column, Integer, String, DateTime, Date, Numeric, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.db.base import Base


class BookingStatusEnum(str, enum.Enum):
    """Booking status enumeration"""
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CHECKED_IN = "CHECKED_IN"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class Booking(Base):
    """
    Booking Model
    Stores room reservations (overnight only)
    """
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)

    # Relationships
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id", ondelete="RESTRICT"), nullable=False, index=True)

    # Booking details
    check_in_date = Column(Date, nullable=False, index=True)
    check_out_date = Column(Date, nullable=False, index=True)
    number_of_nights = Column(Integer, nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    deposit_amount = Column(Numeric(10, 2), nullable=False, default=0)

    # Status and metadata
    status = Column(Enum(BookingStatusEnum), nullable=False, default=BookingStatusEnum.PENDING, index=True)
    notes = Column(Text, nullable=True)

    # Tracking
    created_by = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    cancelled_at = Column(DateTime, nullable=True)

    # Relationships
    customer = relationship("Customer", back_populates="bookings")
    room = relationship("Room", back_populates="bookings")
    creator = relationship("User", back_populates="created_bookings")
    check_ins = relationship("CheckIn", back_populates="booking")

    def __repr__(self):
        return f"<Booking(id={self.id}, room_id={self.room_id}, check_in={self.check_in_date}, status={self.status})>"
