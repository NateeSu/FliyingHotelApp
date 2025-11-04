"""
Notification Model (Phase 3)
Handles system notifications and Telegram integration
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.db.base import Base


class NotificationTypeEnum(str, enum.Enum):
    """Notification type enumeration"""
    ROOM_STATUS_CHANGE = "ROOM_STATUS_CHANGE"
    OVERTIME_ALERT = "OVERTIME_ALERT"
    BOOKING_REMINDER = "BOOKING_REMINDER"
    HOUSEKEEPING_COMPLETE = "HOUSEKEEPING_COMPLETE"
    MAINTENANCE_REQUEST = "MAINTENANCE_REQUEST"
    CHECK_IN = "CHECK_IN"
    CHECK_OUT = "CHECK_OUT"
    ROOM_TRANSFER = "ROOM_TRANSFER"


class TargetRoleEnum(str, enum.Enum):
    """Target role enumeration"""
    ADMIN = "ADMIN"
    RECEPTION = "RECEPTION"
    HOUSEKEEPING = "HOUSEKEEPING"
    MAINTENANCE = "MAINTENANCE"


class Notification(Base):
    """
    Notification Model
    Stores system notifications for different user roles
    Supports Telegram integration
    """
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)

    # Notification details
    notification_type = Column(Enum(NotificationTypeEnum), nullable=False, index=True)
    target_role = Column(Enum(TargetRoleEnum), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)

    # Related room (optional)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=True, index=True)

    # Status tracking
    is_read = Column(Boolean, nullable=False, default=False, index=True)
    read_at = Column(DateTime, nullable=True)

    # Telegram integration
    telegram_sent = Column(Boolean, nullable=False, default=False, index=True)
    telegram_message_id = Column(String(100), nullable=True)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    # Relationships
    room = relationship("Room", back_populates="notifications")

    def __repr__(self):
        return f"<Notification(id={self.id}, type={self.notification_type}, target={self.target_role}, is_read={self.is_read})>"

    def mark_as_read(self):
        """Mark notification as read"""
        self.is_read = True
        self.read_at = datetime.utcnow()

    def mark_telegram_sent(self, message_id: str = None):
        """Mark notification as sent via Telegram"""
        self.telegram_sent = True
        if message_id:
            self.telegram_message_id = message_id
