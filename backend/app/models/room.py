from sqlalchemy import Column, Integer, String, Text, Enum, Boolean, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
import enum


class RoomStatus(str, enum.Enum):
    """
    Room Status Enum
    - available: ว่าง พร้อมให้บริการ
    - occupied: มีผู้พัก
    - cleaning: กำลังทำความสะอาด
    - reserved: จองแล้ว
    - out_of_service: ปิดปรับปรุง/ซ่อมแซม
    """
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    CLEANING = "cleaning"
    RESERVED = "reserved"
    OUT_OF_SERVICE = "out_of_service"


class Room(Base):
    """
    Room Model - ห้องพักจริง

    Relationships:
    - room_type: Many-to-One with RoomType

    Business Rules:
    - room_number must be unique
    - qr_code is auto-generated on creation (UUID)
    - Cannot change room_type if status is occupied or reserved
    """
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    room_number = Column(String(10), unique=True, nullable=False, index=True)
    room_type_id = Column(Integer, ForeignKey("room_types.id", ondelete="RESTRICT"), nullable=False, index=True)
    floor = Column(Integer, nullable=False, index=True)
    status = Column(Enum(RoomStatus), default=RoomStatus.AVAILABLE, nullable=False, index=True)
    qr_code = Column(String(255), unique=True, nullable=True)
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    room_type = relationship("RoomType", back_populates="rooms")
    bookings = relationship("Booking", back_populates="room")
    check_ins = relationship("CheckIn", back_populates="room")
    notifications = relationship("Notification", back_populates="room")

    def __repr__(self):
        return f"<Room(id={self.id}, number='{self.room_number}', status='{self.status.value}')>"
