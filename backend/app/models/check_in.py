"""
Check-In Model (Phase 3)
Handles both overnight and temporary stays
"""
from sqlalchemy import Column, Integer, String, DateTime, Numeric, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.db.base import Base


class StayTypeEnum(str, enum.Enum):
    """Stay type enumeration"""
    OVERNIGHT = "overnight"
    TEMPORARY = "temporary"


class PaymentMethodEnum(str, enum.Enum):
    """Payment method enumeration"""
    CASH = "cash"
    TRANSFER = "transfer"
    CREDIT_CARD = "credit_card"


class CheckInStatusEnum(str, enum.Enum):
    """Check-in status enumeration"""
    CHECKED_IN = "checked_in"
    CHECKED_OUT = "checked_out"


class CheckIn(Base):
    """
    CheckIn Model
    Represents a guest check-in to a room
    Supports both overnight and temporary stays
    """
    __tablename__ = "check_ins"

    id = Column(Integer, primary_key=True, index=True)

    # Relationships
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False, index=True)

    # Stay information
    stay_type = Column(Enum(StayTypeEnum), nullable=False, index=True)
    check_in_time = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    expected_check_out_time = Column(DateTime, nullable=False)
    actual_check_out_time = Column(DateTime, nullable=True)
    number_of_nights = Column(Integer, nullable=True)  # For overnight stays
    number_of_guests = Column(Integer, nullable=False, default=1)

    # Overtime tracking
    is_overtime = Column(Integer, nullable=False, default=0)  # Boolean as int (0 or 1)
    overtime_minutes = Column(Integer, nullable=True)
    overtime_charge = Column(Numeric(10, 2), nullable=False, default=0)

    # Financial information
    base_amount = Column(Numeric(10, 2), nullable=False, default=0)
    extra_charges = Column(Numeric(10, 2), nullable=False, default=0)
    discount_amount = Column(Numeric(10, 2), nullable=False, default=0)
    discount_reason = Column(String(255), nullable=True)
    total_amount = Column(Numeric(10, 2), nullable=False, default=0)

    # Payment information
    payment_method = Column(Enum(PaymentMethodEnum), nullable=True)
    payment_slip_url = Column(String(500), nullable=True)

    # Status and metadata
    status = Column(Enum(CheckInStatusEnum), nullable=False, default=CheckInStatusEnum.CHECKED_IN, index=True)
    notes = Column(Text, nullable=True)

    # Tracking
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    checked_out_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    booking = relationship("Booking", back_populates="check_ins")
    customer = relationship("Customer", back_populates="check_ins")
    room = relationship("Room", back_populates="check_ins")
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_check_ins")
    checkout_user = relationship("User", foreign_keys=[checked_out_by], back_populates="checked_out_check_ins")
    orders = relationship("Order", back_populates="check_in", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="check_in", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<CheckIn(id={self.id}, room_id={self.room_id}, stay_type={self.stay_type}, status={self.status})>"
