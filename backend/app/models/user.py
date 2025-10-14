from sqlalchemy import Column, Integer, String, Boolean, Enum as SQLEnum, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum


class UserRole(str, enum.Enum):
    """User roles enum"""
    ADMIN = "admin"
    RECEPTION = "reception"
    HOUSEKEEPING = "housekeeping"
    MAINTENANCE = "maintenance"


class User(Base):
    """User model for authentication and user management"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(
        SQLEnum(UserRole),
        nullable=False,
        default=UserRole.RECEPTION
    )
    telegram_user_id = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships (Phase 3+)
    created_bookings = relationship("Booking", back_populates="creator", foreign_keys="[Booking.created_by]")
    created_check_ins = relationship("CheckIn", back_populates="creator", foreign_keys="[CheckIn.created_by]")
    checked_out_check_ins = relationship("CheckIn", back_populates="checkout_user", foreign_keys="[CheckIn.checked_out_by]")

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"
