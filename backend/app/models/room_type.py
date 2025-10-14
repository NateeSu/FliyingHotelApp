from sqlalchemy import Column, Integer, String, Text, JSON, Boolean, DECIMAL, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class RoomType(Base):
    """
    RoomType Model - ประเภทห้องพัก (Standard, Deluxe, VIP)

    Relationships:
    - rooms: One-to-Many with Room
    - room_rates: One-to-Many with RoomRate
    """
    __tablename__ = "room_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    amenities = Column(JSON, nullable=True)  # ["TV", "แอร์", "ตู้เย็น"]
    max_guests = Column(Integer, nullable=False, default=2)
    bed_type = Column(String(50), nullable=True)
    room_size_sqm = Column(DECIMAL(5, 2), nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    rooms = relationship("Room", back_populates="room_type", cascade="all, delete-orphan")
    room_rates = relationship("RoomRate", back_populates="room_type", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<RoomType(id={self.id}, name='{self.name}', max_guests={self.max_guests})>"
