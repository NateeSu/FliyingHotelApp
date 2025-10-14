# Phase 2: Room Management - Implementation Plan

## สถานะ: 🚧 กำลังดำเนินการ
## วันที่เริ่มต้น: 2025-10-13
## เป้าหมาย: 3-4 วัน

---

## 📋 Overview

Phase 2 มุ่งเน้นการสร้างระบบจัดการห้องพัก ซึ่งเป็นหัวใจหลักของระบบ PMS โดยจะครอบคลุม:
- **Room Types** (ประเภทห้อง): เช่น Standard, Deluxe, VIP
- **Rooms** (ห้องพัก): ห้องจริงที่มีหมายเลขห้อง พร้อมสถานะห้อง
- **Room Rates** (อัตราราคา): ราคาห้องตามประเภทและประเภทการเข้าพัก (ค้างคืน/ชั่วคราว)

---

## 🎯 Objectives

1. ✅ Admin สามารถ CRUD room types ได้
2. ✅ Admin สามารถ CRUD rooms ได้ (โดยระบุประเภทห้อง)
3. ✅ Admin สามารถตั้งราคาห้องได้ (per room type + stay type)
4. ✅ ระบบแสดงสถานะห้องแบบ real-time (available, occupied, cleaning, reserved, out_of_service)
5. ✅ UI responsive (mobile + tablet + desktop)
6. ✅ Material Design UI สอดคล้องกับ Phase 1

---

## 📊 Database Schema

### 1. Table: `room_types`

```sql
CREATE TABLE room_types (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,          -- เช่น "Standard", "Deluxe", "VIP"
    description TEXT,                           -- คำอธิบายประเภทห้อง
    amenities JSON,                             -- สิ่งอำนวยความสะดวก ["TV", "แอร์", "ตู้เย็น"]
    max_guests INT NOT NULL DEFAULT 2,         -- จำนวนผู้พักสูงสุด
    bed_type VARCHAR(50),                       -- เช่น "เตียงคิงไซส์", "เตียงเดี่ยว 2 เตียง"
    room_size_sqm DECIMAL(5,2),                -- ขนาดห้อง (ตารางเมตร)
    is_active BOOLEAN DEFAULT TRUE,            -- สามารถใช้งานได้หรือไม่
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_room_types_name (name),
    INDEX idx_room_types_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Business Rules**:
- `name` ต้องไม่ซ้ำกัน (UNIQUE)
- ไม่สามารถลบ room_type ได้ถ้ามี rooms ที่ใช้งานอยู่
- การ deactivate จะทำให้ห้องในประเภทนั้นไม่สามารถรับจองใหม่ได้

### 2. Table: `rooms`

```sql
CREATE TABLE rooms (
    id INT AUTO_INCREMENT PRIMARY KEY,
    room_number VARCHAR(10) NOT NULL UNIQUE,   -- เช่น "101", "201", "VIP-01"
    room_type_id INT NOT NULL,                 -- FK to room_types
    floor INT NOT NULL,                        -- ชั้น (1, 2, 3, ...)
    status ENUM('available', 'occupied', 'cleaning', 'reserved', 'out_of_service')
           DEFAULT 'available',
    qr_code VARCHAR(255) UNIQUE,               -- QR Code สำหรับสั่งของ
    notes TEXT,                                -- หมายเหตุเพิ่มเติม (เช่น "แอร์เสีย")
    is_active BOOLEAN DEFAULT TRUE,            -- สามารถใช้งานได้หรือไม่
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (room_type_id) REFERENCES room_types(id) ON DELETE RESTRICT,
    INDEX idx_rooms_number (room_number),
    INDEX idx_rooms_status (status),
    INDEX idx_rooms_type (room_type_id),
    INDEX idx_rooms_floor (floor),
    INDEX idx_rooms_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Business Rules**:
- `room_number` ต้องไม่ซ้ำกัน (UNIQUE)
- ไม่สามารถเปลี่ยน room_type ได้ถ้าห้องมี status = occupied หรือ reserved
- `qr_code` จะถูกสร้างอัตโนมัติเมื่อสร้างห้องใหม่ (UUID format)
- Room status flow: `available → reserved → occupied → cleaning → available`
- ห้องสามารถ toggle เป็น `out_of_service` ได้ทุกเวลา

### 3. Table: `room_rates`

```sql
CREATE TABLE room_rates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    room_type_id INT NOT NULL,                 -- FK to room_types
    stay_type ENUM('overnight', 'temporary') NOT NULL,  -- ประเภทการเข้าพัก
    rate DECIMAL(10,2) NOT NULL,               -- ราคา (บาท)
    effective_from DATE NOT NULL,              -- วันที่เริ่มใช้ราคา
    effective_to DATE,                         -- วันที่สิ้นสุดราคา (NULL = ไม่มีวันสิ้นสุด)
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (room_type_id) REFERENCES room_types(id) ON DELETE RESTRICT,
    INDEX idx_room_rates_type_stay (room_type_id, stay_type),
    INDEX idx_room_rates_dates (effective_from, effective_to),
    INDEX idx_room_rates_active (is_active),

    UNIQUE KEY uk_room_rates (room_type_id, stay_type, effective_from)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Business Rules**:
- แต่ละ room_type + stay_type ต้องมีราคาที่ active อยู่เสมอ
- `effective_from` + `effective_to` ต้องไม่ทับซ้อนกันสำหรับ room_type + stay_type เดียวกัน
- ราคาที่มี `effective_to = NULL` คือราคาปัจจุบัน
- ไม่สามารถลบราคาได้ถ้ามี bookings/check-ins ที่อ้างอิงถึง

### Database Relationships

```
room_types (1) ──< (N) rooms
room_types (1) ──< (N) room_rates
```

---

## 🔧 Backend Implementation

### 1. SQLAlchemy Models

**File**: `backend/app/models/room_type.py`

```python
from sqlalchemy import Column, Integer, String, Text, JSON, Boolean, DECIMAL, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class RoomType(Base):
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
    rooms = relationship("Room", back_populates="room_type")
    room_rates = relationship("RoomRate", back_populates="room_type")
```

**File**: `backend/app/models/room.py`

```python
from sqlalchemy import Column, Integer, String, Text, Enum, Boolean, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
import enum

class RoomStatus(str, enum.Enum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    CLEANING = "cleaning"
    RESERVED = "reserved"
    OUT_OF_SERVICE = "out_of_service"

class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    room_number = Column(String(10), unique=True, nullable=False, index=True)
    room_type_id = Column(Integer, ForeignKey("room_types.id"), nullable=False, index=True)
    floor = Column(Integer, nullable=False, index=True)
    status = Column(Enum(RoomStatus), default=RoomStatus.AVAILABLE, index=True)
    qr_code = Column(String(255), unique=True, nullable=True)
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    room_type = relationship("RoomType", back_populates="rooms")
```

**File**: `backend/app/models/room_rate.py`

```python
from sqlalchemy import Column, Integer, Enum, DECIMAL, Date, Boolean, ForeignKey, TIMESTAMP, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
import enum

class StayType(str, enum.Enum):
    OVERNIGHT = "overnight"
    TEMPORARY = "temporary"

class RoomRate(Base):
    __tablename__ = "room_rates"

    id = Column(Integer, primary_key=True, index=True)
    room_type_id = Column(Integer, ForeignKey("room_types.id"), nullable=False, index=True)
    stay_type = Column(Enum(StayType), nullable=False)
    rate = Column(DECIMAL(10, 2), nullable=False)
    effective_from = Column(Date, nullable=False, index=True)
    effective_to = Column(Date, nullable=True, index=True)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    room_type = relationship("RoomType", back_populates="room_rates")

    # Unique constraint
    __table_args__ = (
        UniqueConstraint('room_type_id', 'stay_type', 'effective_from', name='uk_room_rates'),
    )
```

### 2. Pydantic Schemas

**File**: `backend/app/schemas/room_type.py`

```python
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class RoomTypeBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None
    amenities: Optional[List[str]] = None
    max_guests: int = Field(default=2, ge=1, le=10)
    bed_type: Optional[str] = Field(None, max_length=50)
    room_size_sqm: Optional[float] = Field(None, ge=0)
    is_active: bool = True

class RoomTypeCreate(RoomTypeBase):
    pass

class RoomTypeUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = None
    amenities: Optional[List[str]] = None
    max_guests: Optional[int] = Field(None, ge=1, le=10)
    bed_type: Optional[str] = Field(None, max_length=50)
    room_size_sqm: Optional[float] = Field(None, ge=0)
    is_active: Optional[bool] = None

class RoomTypeResponse(RoomTypeBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

**File**: `backend/app/schemas/room.py`

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.room import RoomStatus

class RoomBase(BaseModel):
    room_number: str = Field(..., min_length=1, max_length=10)
    room_type_id: int = Field(..., gt=0)
    floor: int = Field(..., ge=1)
    notes: Optional[str] = None
    is_active: bool = True

class RoomCreate(RoomBase):
    pass

class RoomUpdate(BaseModel):
    room_number: Optional[str] = Field(None, min_length=1, max_length=10)
    room_type_id: Optional[int] = Field(None, gt=0)
    floor: Optional[int] = Field(None, ge=1)
    status: Optional[RoomStatus] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None

class RoomResponse(RoomBase):
    id: int
    status: RoomStatus
    qr_code: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    room_type: Optional[dict] = None  # Nested room type info

    class Config:
        from_attributes = True
```

**File**: `backend/app/schemas/room_rate.py`

```python
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import date, datetime
from app.models.room_rate import StayType

class RoomRateBase(BaseModel):
    room_type_id: int = Field(..., gt=0)
    stay_type: StayType
    rate: float = Field(..., ge=0)
    effective_from: date
    effective_to: Optional[date] = None
    is_active: bool = True

    @validator('effective_to')
    def validate_dates(cls, v, values):
        if v and 'effective_from' in values:
            if v < values['effective_from']:
                raise ValueError('effective_to must be after effective_from')
        return v

class RoomRateCreate(RoomRateBase):
    pass

class RoomRateUpdate(BaseModel):
    rate: Optional[float] = Field(None, ge=0)
    effective_to: Optional[date] = None
    is_active: Optional[bool] = None

class RoomRateResponse(RoomRateBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

### 3. API Endpoints

**File**: `backend/app/api/v1/endpoints/room_types.py`

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.db.base import get_db
from app.schemas.room_type import RoomTypeCreate, RoomTypeUpdate, RoomTypeResponse
from app.services.room_type_service import RoomTypeService
from app.core.deps import get_current_active_user, require_role
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[RoomTypeResponse])
async def get_room_types(
    skip: int = 0,
    limit: int = 100,
    is_active: bool = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    รายการประเภทห้องทั้งหมด
    - สามารถกรองตาม is_active
    """
    service = RoomTypeService(db)
    return await service.get_all(skip=skip, limit=limit, is_active=is_active)

@router.get("/{room_type_id}", response_model=RoomTypeResponse)
async def get_room_type(
    room_type_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """ดึงข้อมูลประเภทห้องตาม ID"""
    service = RoomTypeService(db)
    room_type = await service.get_by_id(room_type_id)
    if not room_type:
        raise HTTPException(status_code=404, detail="ไม่พบประเภทห้อง")
    return room_type

@router.post("/", response_model=RoomTypeResponse, status_code=status.HTTP_201_CREATED)
async def create_room_type(
    room_type_data: RoomTypeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    """สร้างประเภทห้องใหม่ (Admin only)"""
    service = RoomTypeService(db)
    return await service.create(room_type_data)

@router.patch("/{room_type_id}", response_model=RoomTypeResponse)
async def update_room_type(
    room_type_id: int,
    room_type_data: RoomTypeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    """แก้ไขข้อมูลประเภทห้อง (Admin only)"""
    service = RoomTypeService(db)
    room_type = await service.update(room_type_id, room_type_data)
    if not room_type:
        raise HTTPException(status_code=404, detail="ไม่พบประเภทห้อง")
    return room_type

@router.delete("/{room_type_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_room_type(
    room_type_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    """ลบประเภทห้อง (Admin only) - จะลบไม่ได้ถ้ามีห้องที่ใช้งานอยู่"""
    service = RoomTypeService(db)
    await service.delete(room_type_id)
```

**File**: `backend/app/api/v1/endpoints/rooms.py` (similar structure)

**File**: `backend/app/api/v1/endpoints/room_rates.py` (similar structure)

### 4. Service Layer

**File**: `backend/app/services/room_type_service.py`

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from app.models.room_type import RoomType
from app.schemas.room_type import RoomTypeCreate, RoomTypeUpdate
from fastapi import HTTPException

class RoomTypeService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None
    ) -> List[RoomType]:
        query = select(RoomType)
        if is_active is not None:
            query = query.where(RoomType.is_active == is_active)
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_id(self, room_type_id: int) -> Optional[RoomType]:
        result = await self.db.execute(
            select(RoomType).where(RoomType.id == room_type_id)
        )
        return result.scalar_one_or_none()

    async def create(self, data: RoomTypeCreate) -> RoomType:
        # Check if name already exists
        existing = await self.db.execute(
            select(RoomType).where(RoomType.name == data.name)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="ชื่อประเภทห้องนี้มีอยู่แล้ว")

        room_type = RoomType(**data.model_dump())
        self.db.add(room_type)
        await self.db.commit()
        await self.db.refresh(room_type)
        return room_type

    async def update(self, room_type_id: int, data: RoomTypeUpdate) -> Optional[RoomType]:
        room_type = await self.get_by_id(room_type_id)
        if not room_type:
            return None

        # Check if new name conflicts
        if data.name and data.name != room_type.name:
            existing = await self.db.execute(
                select(RoomType).where(RoomType.name == data.name)
            )
            if existing.scalar_one_or_none():
                raise HTTPException(status_code=400, detail="ชื่อประเภทห้องนี้มีอยู่แล้ว")

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(room_type, field, value)

        await self.db.commit()
        await self.db.refresh(room_type)
        return room_type

    async def delete(self, room_type_id: int) -> None:
        room_type = await self.get_by_id(room_type_id)
        if not room_type:
            raise HTTPException(status_code=404, detail="ไม่พบประเภทห้อง")

        # Check if any rooms are using this room type
        from app.models.room import Room
        result = await self.db.execute(
            select(Room).where(Room.room_type_id == room_type_id).limit(1)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=400,
                detail="ไม่สามารถลบประเภทห้องที่มีห้องพักใช้งานอยู่ได้"
            )

        await self.db.delete(room_type)
        await self.db.commit()
```

### 5. Alembic Migration

**File**: `backend/alembic/versions/002_create_room_management_tables.py`

```python
"""create room management tables

Revision ID: 002
Revises: 001
Create Date: 2025-10-13

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create room_types table
    op.create_table(
        'room_types',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('amenities', sa.JSON(), nullable=True),
        sa.Column('max_guests', sa.Integer(), nullable=False, server_default='2'),
        sa.Column('bed_type', sa.String(length=50), nullable=True),
        sa.Column('room_size_sqm', sa.DECIMAL(5, 2), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='1'),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index('idx_room_types_name', 'room_types', ['name'])
    op.create_index('idx_room_types_active', 'room_types', ['is_active'])

    # Create rooms table
    op.create_table(
        'rooms',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('room_number', sa.String(length=10), nullable=False),
        sa.Column('room_type_id', sa.Integer(), nullable=False),
        sa.Column('floor', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('available', 'occupied', 'cleaning', 'reserved', 'out_of_service', name='roomstatus'), nullable=True, server_default='available'),
        sa.Column('qr_code', sa.String(length=255), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='1'),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['room_type_id'], ['room_types.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('room_number'),
        sa.UniqueConstraint('qr_code')
    )
    op.create_index('idx_rooms_number', 'rooms', ['room_number'])
    op.create_index('idx_rooms_status', 'rooms', ['status'])
    op.create_index('idx_rooms_type', 'rooms', ['room_type_id'])
    op.create_index('idx_rooms_floor', 'rooms', ['floor'])
    op.create_index('idx_rooms_active', 'rooms', ['is_active'])

    # Create room_rates table
    op.create_table(
        'room_rates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('room_type_id', sa.Integer(), nullable=False),
        sa.Column('stay_type', sa.Enum('overnight', 'temporary', name='staytype'), nullable=False),
        sa.Column('rate', sa.DECIMAL(10, 2), nullable=False),
        sa.Column('effective_from', sa.Date(), nullable=False),
        sa.Column('effective_to', sa.Date(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='1'),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['room_type_id'], ['room_types.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('room_type_id', 'stay_type', 'effective_from', name='uk_room_rates')
    )
    op.create_index('idx_room_rates_type_stay', 'room_rates', ['room_type_id', 'stay_type'])
    op.create_index('idx_room_rates_dates', 'room_rates', ['effective_from', 'effective_to'])
    op.create_index('idx_room_rates_active', 'room_rates', ['is_active'])

def downgrade() -> None:
    op.drop_table('room_rates')
    op.drop_table('rooms')
    op.drop_table('room_types')

    # Drop enums
    op.execute('DROP TYPE IF EXISTS roomstatus')
    op.execute('DROP TYPE IF EXISTS staytype')
```

### 6. Seed Data Script

**File**: `backend/scripts/seed_phase2.py`

```python
import asyncio
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import get_db, engine
from app.models.room_type import RoomType
from app.models.room import Room, RoomStatus
from app.models.room_rate import RoomRate, StayType
from datetime import date
import uuid

async def seed_phase2():
    async with engine.begin() as conn:
        async with AsyncSession(conn, expire_on_commit=False) as db:
            print("🌱 Starting Phase 2 seed data...")

            # 1. Create Room Types
            room_types_data = [
                {
                    "name": "Standard",
                    "description": "ห้องพักมาตรฐาน สะดวกสบาย เหมาะสำหรับนักท่องเที่ยว",
                    "amenities": ["ทีวี", "แอร์", "ตู้เย็น", "ห้องน้ำในตัว", "Wi-Fi ฟรี"],
                    "max_guests": 2,
                    "bed_type": "เตียงคู่",
                    "room_size_sqm": 25.00,
                    "is_active": True
                },
                {
                    "name": "Deluxe",
                    "description": "ห้องพักระดับดีลักซ์ พื้นที่กว้างขวาง สิ่งอำนวยความสะดวกครบครัน",
                    "amenities": ["ทีวี LED 42\"", "แอร์", "ตู้เย็น", "ห้องน้ำในตัว", "Wi-Fi ฟรี", "โต๊ะทำงาน", "โซฟานั่งเล่น"],
                    "max_guests": 3,
                    "bed_type": "เตียงคิงไซส์",
                    "room_size_sqm": 35.00,
                    "is_active": True
                },
                {
                    "name": "VIP",
                    "description": "ห้องพักระดับวีไอพี หรูหรา พิเศษสุด มีจากุซซี่",
                    "amenities": ["ทีวี LED 55\"", "แอร์", "ตู้เย็น", "ห้องน้ำในตัว", "Wi-Fi ฟรี", "โต๊ะทำงาน", "โซฟานั่งเล่น", "จากุซซี่", "ระเบียงส่วนตัว"],
                    "max_guests": 4,
                    "bed_type": "เตียงคิงไซส์ + โซฟาเบด",
                    "room_size_sqm": 50.00,
                    "is_active": True
                }
            ]

            created_room_types = []
            for data in room_types_data:
                room_type = RoomType(**data)
                db.add(room_type)
                await db.flush()
                created_room_types.append(room_type)
                print(f"✅ Created room type: {room_type.name}")

            await db.commit()

            # 2. Create Rooms (10 rooms total)
            rooms_data = [
                # Floor 1 - Standard (5 rooms)
                {"room_number": "101", "room_type": "Standard", "floor": 1},
                {"room_number": "102", "room_type": "Standard", "floor": 1},
                {"room_number": "103", "room_type": "Standard", "floor": 1},
                {"room_number": "104", "room_type": "Deluxe", "floor": 1},
                {"room_number": "105", "room_type": "Deluxe", "floor": 1},

                # Floor 2 - Mixed (5 rooms)
                {"room_number": "201", "room_type": "Standard", "floor": 2},
                {"room_number": "202", "room_type": "Deluxe", "floor": 2},
                {"room_number": "203", "room_type": "Deluxe", "floor": 2},
                {"room_number": "204", "room_type": "VIP", "floor": 2},
                {"room_number": "205", "room_type": "VIP", "floor": 2},
            ]

            room_type_map = {rt.name: rt for rt in created_room_types}

            for data in rooms_data:
                room_type_name = data.pop("room_type")
                room_type = room_type_map[room_type_name]

                room = Room(
                    **data,
                    room_type_id=room_type.id,
                    status=RoomStatus.AVAILABLE,
                    qr_code=f"ROOM-{str(uuid.uuid4())[:8].upper()}",
                    is_active=True
                )
                db.add(room)
                print(f"✅ Created room: {room.room_number} ({room_type_name})")

            await db.commit()

            # 3. Create Room Rates (current rates)
            room_rates_data = [
                # Standard
                {"room_type": "Standard", "stay_type": StayType.OVERNIGHT, "rate": 600.00},
                {"room_type": "Standard", "stay_type": StayType.TEMPORARY, "rate": 300.00},

                # Deluxe
                {"room_type": "Deluxe", "stay_type": StayType.OVERNIGHT, "rate": 900.00},
                {"room_type": "Deluxe", "stay_type": StayType.TEMPORARY, "rate": 450.00},

                # VIP
                {"room_type": "VIP", "stay_type": StayType.OVERNIGHT, "rate": 1500.00},
                {"room_type": "VIP", "stay_type": StayType.TEMPORARY, "rate": 750.00},
            ]

            for data in room_rates_data:
                room_type_name = data.pop("room_type")
                room_type = room_type_map[room_type_name]

                room_rate = RoomRate(
                    room_type_id=room_type.id,
                    stay_type=data["stay_type"],
                    rate=data["rate"],
                    effective_from=date.today(),
                    effective_to=None,  # No end date = current rate
                    is_active=True
                )
                db.add(room_rate)
                print(f"✅ Created rate: {room_type_name} - {data['stay_type'].value} = {data['rate']} บาท")

            await db.commit()

            print("\n🎉 Phase 2 seed data completed successfully!")
            print(f"📊 Summary:")
            print(f"   - Room Types: {len(created_room_types)}")
            print(f"   - Rooms: {len(rooms_data)}")
            print(f"   - Room Rates: {len(room_rates_data)}")

if __name__ == "__main__":
    asyncio.run(seed_phase2())
```

---

## 🎨 Frontend Implementation

### 1. TypeScript Types

**File**: `frontend/src/types/room.ts`

```typescript
export enum RoomStatus {
  AVAILABLE = 'available',
  OCCUPIED = 'occupied',
  CLEANING = 'cleaning',
  RESERVED = 'reserved',
  OUT_OF_SERVICE = 'out_of_service'
}

export enum StayType {
  OVERNIGHT = 'overnight',
  TEMPORARY = 'temporary'
}

export interface RoomType {
  id: number
  name: string
  description?: string
  amenities?: string[]
  max_guests: number
  bed_type?: string
  room_size_sqm?: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Room {
  id: number
  room_number: string
  room_type_id: number
  room_type?: RoomType
  floor: number
  status: RoomStatus
  qr_code?: string
  notes?: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface RoomRate {
  id: number
  room_type_id: number
  stay_type: StayType
  rate: number
  effective_from: string
  effective_to?: string
  is_active: boolean
  created_at: string
  updated_at: string
}

// Form types
export interface RoomTypeFormData {
  name: string
  description?: string
  amenities?: string[]
  max_guests: number
  bed_type?: string
  room_size_sqm?: number
  is_active: boolean
}

export interface RoomFormData {
  room_number: string
  room_type_id: number
  floor: number
  notes?: string
  is_active: boolean
}

export interface RoomRateFormData {
  room_type_id: number
  stay_type: StayType
  rate: number
  effective_from: string
  effective_to?: string
}
```

### 2. API Client

**File**: `frontend/src/api/rooms.ts`

```typescript
import axios from './axios'
import type { RoomType, Room, RoomRate, RoomTypeFormData, RoomFormData, RoomRateFormData } from '@/types/room'

// Room Types API
export const roomTypesApi = {
  getAll: (params?: { skip?: number; limit?: number; is_active?: boolean }) =>
    axios.get<RoomType[]>('/api/v1/room-types/', { params }),

  getById: (id: number) =>
    axios.get<RoomType>(`/api/v1/room-types/${id}`),

  create: (data: RoomTypeFormData) =>
    axios.post<RoomType>('/api/v1/room-types/', data),

  update: (id: number, data: Partial<RoomTypeFormData>) =>
    axios.patch<RoomType>(`/api/v1/room-types/${id}`, data),

  delete: (id: number) =>
    axios.delete(`/api/v1/room-types/${id}`)
}

// Rooms API
export const roomsApi = {
  getAll: (params?: { skip?: number; limit?: number; is_active?: boolean; floor?: number; status?: string }) =>
    axios.get<Room[]>('/api/v1/rooms/', { params }),

  getById: (id: number) =>
    axios.get<Room>(`/api/v1/rooms/${id}`),

  create: (data: RoomFormData) =>
    axios.post<Room>('/api/v1/rooms/', data),

  update: (id: number, data: Partial<RoomFormData>) =>
    axios.patch<Room>(`/api/v1/rooms/${id}`, data),

  delete: (id: number) =>
    axios.delete(`/api/v1/rooms/${id}`),

  updateStatus: (id: number, status: string) =>
    axios.patch<Room>(`/api/v1/rooms/${id}/status`, { status })
}

// Room Rates API
export const roomRatesApi = {
  getAll: (params?: { room_type_id?: number; stay_type?: string }) =>
    axios.get<RoomRate[]>('/api/v1/room-rates/', { params }),

  getById: (id: number) =>
    axios.get<RoomRate>(`/api/v1/room-rates/${id}`),

  create: (data: RoomRateFormData) =>
    axios.post<RoomRate>('/api/v1/room-rates/', data),

  update: (id: number, data: Partial<RoomRateFormData>) =>
    axios.patch<RoomRate>(`/api/v1/room-rates/${id}`, data),

  delete: (id: number) =>
    axios.delete(`/api/v1/room-rates/${id}`)
}
```

### 3. Pinia Stores

**File**: `frontend/src/stores/room.ts`

```typescript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { RoomType, Room, RoomRate } from '@/types/room'
import { roomTypesApi, roomsApi, roomRatesApi } from '@/api/rooms'

export const useRoomStore = defineStore('room', () => {
  // State
  const roomTypes = ref<RoomType[]>([])
  const rooms = ref<Room[]>([])
  const roomRates = ref<RoomRate[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const activeRoomTypes = computed(() =>
    roomTypes.value.filter(rt => rt.is_active)
  )

  const availableRooms = computed(() =>
    rooms.value.filter(r => r.status === 'available' && r.is_active)
  )

  const roomsByFloor = computed(() => {
    const grouped = new Map<number, Room[]>()
    rooms.value.forEach(room => {
      if (!grouped.has(room.floor)) {
        grouped.set(room.floor, [])
      }
      grouped.get(room.floor)!.push(room)
    })
    return grouped
  })

  // Actions - Room Types
  async function fetchRoomTypes(params?: any) {
    isLoading.value = true
    error.value = null
    try {
      const response = await roomTypesApi.getAll(params)
      roomTypes.value = response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'เกิดข้อผิดพลาดในการดึงข้อมูลประเภทห้อง'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function createRoomType(data: any) {
    isLoading.value = true
    error.value = null
    try {
      const response = await roomTypesApi.create(data)
      roomTypes.value.push(response.data)
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'เกิดข้อผิดพลาดในการสร้างประเภทห้อง'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function updateRoomType(id: number, data: any) {
    isLoading.value = true
    error.value = null
    try {
      const response = await roomTypesApi.update(id, data)
      const index = roomTypes.value.findIndex(rt => rt.id === id)
      if (index !== -1) {
        roomTypes.value[index] = response.data
      }
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'เกิดข้อผิดพลาดในการแก้ไขประเภทห้อง'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function deleteRoomType(id: number) {
    isLoading.value = true
    error.value = null
    try {
      await roomTypesApi.delete(id)
      roomTypes.value = roomTypes.value.filter(rt => rt.id !== id)
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'เกิดข้อผิดพลาดในการลบประเภทห้อง'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // Actions - Rooms
  async function fetchRooms(params?: any) {
    isLoading.value = true
    error.value = null
    try {
      const response = await roomsApi.getAll(params)
      rooms.value = response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'เกิดข้อผิดพลาดในการดึงข้อมูลห้องพัก'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function createRoom(data: any) {
    isLoading.value = true
    error.value = null
    try {
      const response = await roomsApi.create(data)
      rooms.value.push(response.data)
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'เกิดข้อผิดพลาดในการสร้างห้องพัก'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function updateRoom(id: number, data: any) {
    isLoading.value = true
    error.value = null
    try {
      const response = await roomsApi.update(id, data)
      const index = rooms.value.findIndex(r => r.id === id)
      if (index !== -1) {
        rooms.value[index] = response.data
      }
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'เกิดข้อผิดพลาดในการแก้ไขห้องพัก'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function deleteRoom(id: number) {
    isLoading.value = true
    error.value = null
    try {
      await roomsApi.delete(id)
      rooms.value = rooms.value.filter(r => r.id !== id)
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'เกิดข้อผิดพลาดในการลบห้องพัก'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // Actions - Room Rates
  async function fetchRoomRates(params?: any) {
    isLoading.value = true
    error.value = null
    try {
      const response = await roomRatesApi.getAll(params)
      roomRates.value = response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'เกิดข้อผิดพลาดในการดึงข้อมูลราคาห้อง'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function createRoomRate(data: any) {
    isLoading.value = true
    error.value = null
    try {
      const response = await roomRatesApi.create(data)
      roomRates.value.push(response.data)
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'เกิดข้อผิดพลาดในการสร้างราคาห้อง'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function updateRoomRate(id: number, data: any) {
    isLoading.value = true
    error.value = null
    try {
      const response = await roomRatesApi.update(id, data)
      const index = roomRates.value.findIndex(rr => rr.id === id)
      if (index !== -1) {
        roomRates.value[index] = response.data
      }
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'เกิดข้อผิดพลาดในการแก้ไขราคาห้อง'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function deleteRoomRate(id: number) {
    isLoading.value = true
    error.value = null
    try {
      await roomRatesApi.delete(id)
      roomRates.value = roomRates.value.filter(rr => rr.id !== id)
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'เกิดข้อผิดพลาดในการลบราคาห้อง'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  function clearError() {
    error.value = null
  }

  return {
    // State
    roomTypes,
    rooms,
    roomRates,
    isLoading,
    error,
    // Getters
    activeRoomTypes,
    availableRooms,
    roomsByFloor,
    // Actions
    fetchRoomTypes,
    createRoomType,
    updateRoomType,
    deleteRoomType,
    fetchRooms,
    createRoom,
    updateRoom,
    deleteRoom,
    fetchRoomRates,
    createRoomRate,
    updateRoomRate,
    deleteRoomRate,
    clearError
  }
})
```

### 4. Material Design Views

Phase 2 will have **3 main views**:

1. **RoomTypesView.vue** - จัดการประเภทห้อง (CRUD)
2. **RoomsView.vue** - จัดการห้องพัก (CRUD)
3. **RoomRatesView.vue** - จัดการราคาห้อง (Matrix view)

**Design Pattern**:
- Material Design cards with elevation
- Gradient headers (Indigo → Purple → Pink)
- Floating action button for "เพิ่มใหม่"
- Data tables with sort/filter/pagination
- Modal dialogs for forms
- Success/Error toast notifications
- Loading skeletons
- Responsive grid layouts

**Color Scheme** (Status Colors):
```css
/* Room Status Colors */
.status-available { @apply bg-green-100 text-green-800 border-green-300; }
.status-occupied { @apply bg-red-100 text-red-800 border-red-300; }
.status-cleaning { @apply bg-yellow-100 text-yellow-800 border-yellow-300; }
.status-reserved { @apply bg-blue-100 text-blue-800 border-blue-300; }
.status-out_of_service { @apply bg-gray-100 text-gray-800 border-gray-300; }
```

### 5. Router Updates

**File**: `frontend/src/router/index.ts`

Add routes:
```typescript
{
  path: '/room-types',
  name: 'RoomTypes',
  component: () => import('@/views/RoomTypesView.vue'),
  meta: { requiresAuth: true, roles: ['admin'] }
},
{
  path: '/rooms',
  name: 'Rooms',
  component: () => import('@/views/RoomsView.vue'),
  meta: { requiresAuth: true, roles: ['admin', 'reception'] }
},
{
  path: '/room-rates',
  name: 'RoomRates',
  component: () => import('@/views/RoomRatesView.vue'),
  meta: { requiresAuth: true, roles: ['admin'] }
}
```

---

## ✅ Testing Strategy

### Backend Tests

**File**: `backend/tests/api/test_room_types.py`

```python
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.asyncio
async def test_create_room_type(client: AsyncClient, admin_token: str):
    response = await client.post(
        "/api/v1/room-types/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "Test Room Type",
            "description": "Test Description",
            "max_guests": 2,
            "is_active": True
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Room Type"
    assert data["max_guests"] == 2

@pytest.mark.asyncio
async def test_create_duplicate_room_type(client: AsyncClient, admin_token: str):
    # Create first room type
    await client.post(
        "/api/v1/room-types/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"name": "Duplicate", "max_guests": 2}
    )

    # Try to create duplicate
    response = await client.post(
        "/api/v1/room-types/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"name": "Duplicate", "max_guests": 2}
    )
    assert response.status_code == 400
    assert "มีอยู่แล้ว" in response.json()["detail"]

@pytest.mark.asyncio
async def test_update_room_type(client: AsyncClient, admin_token: str, db: AsyncSession):
    # Create room type
    create_response = await client.post(
        "/api/v1/room-types/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"name": "Original", "max_guests": 2}
    )
    room_type_id = create_response.json()["id"]

    # Update room type
    response = await client.patch(
        f"/api/v1/room-types/{room_type_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"name": "Updated", "max_guests": 3}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated"
    assert data["max_guests"] == 3

@pytest.mark.asyncio
async def test_delete_room_type_with_rooms(client: AsyncClient, admin_token: str):
    # Create room type
    rt_response = await client.post(
        "/api/v1/room-types/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"name": "CannotDelete", "max_guests": 2}
    )
    room_type_id = rt_response.json()["id"]

    # Create room using this room type
    await client.post(
        "/api/v1/rooms/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "room_number": "999",
            "room_type_id": room_type_id,
            "floor": 1
        }
    )

    # Try to delete room type (should fail)
    response = await client.delete(
        f"/api/v1/room-types/{room_type_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 400
    assert "ไม่สามารถลบ" in response.json()["detail"]
```

### Frontend Tests

**File**: `frontend/src/views/__tests__/RoomTypesView.spec.ts`

```typescript
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import RoomTypesView from '../RoomTypesView.vue'

describe('RoomTypesView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('renders room types list', () => {
    const wrapper = mount(RoomTypesView)
    expect(wrapper.find('h1').text()).toContain('จัดการประเภทห้อง')
  })

  it('opens create modal when clicking add button', async () => {
    const wrapper = mount(RoomTypesView)
    const addButton = wrapper.find('[data-testid="add-room-type-btn"]')
    await addButton.trigger('click')
    expect(wrapper.find('[data-testid="room-type-modal"]').exists()).toBe(true)
  })

  // Add more tests...
})
```

---

## 📅 Implementation Timeline

### Day 1: Database & Backend Core (8 hours)
- ✅ Create SQLAlchemy models
- ✅ Create Pydantic schemas
- ✅ Create Alembic migration
- ✅ Run migration
- ✅ Create seed data script
- ✅ Run seed script

### Day 2: Backend APIs & Services (8 hours)
- ✅ Implement RoomTypeService
- ✅ Implement RoomService (with QR code generation)
- ✅ Implement RoomRateService
- ✅ Create API endpoints for all three entities
- ✅ Write unit tests
- ✅ Test all endpoints via Swagger UI

### Day 3: Frontend - Room Types & Rooms (8 hours)
- ✅ Create TypeScript types
- ✅ Create API client functions
- ✅ Create Pinia store
- ✅ Build RoomTypesView with Material Design
- ✅ Build RoomsView with Material Design
- ✅ Add router routes
- ✅ Test CRUD operations

### Day 4: Frontend - Room Rates & Polish (8 hours)
- ✅ Build RoomRatesView (Matrix layout)
- ✅ Add form validation
- ✅ Add loading states
- ✅ Add error handling
- ✅ Responsive testing (mobile/tablet/desktop)
- ✅ Write frontend tests
- ✅ Final testing & bug fixes
- ✅ Update documentation

---

## 🎯 Success Criteria

Phase 2 จะถือว่าสำเร็จเมื่อ:

1. ✅ **Database**: 3 ตารางถูกสร้างพร้อม indexes และ relationships ที่ถูกต้อง
2. ✅ **Backend**: CRUD endpoints ทั้งหมดทำงานได้และ pass unit tests
3. ✅ **Seed Data**: มีข้อมูลตัวอย่าง (3 room types, 10 rooms, 6 room rates)
4. ✅ **Frontend**: 3 หน้าจอทำงานได้ครบถ้วน:
   - Admin สามารถ CRUD room types ได้
   - Admin/Reception สามารถ CRUD rooms ได้
   - Admin สามารถตั้งราคาห้องได้ (matrix view)
5. ✅ **UI/UX**: Material Design สวยงาม responsive ทุกขนาดหน้าจอ
6. ✅ **Validation**: Form validation ทำงานถูกต้อง (ชื่อซ้ำ, ราคาติดลบ, วันที่ผิด)
7. ✅ **Error Handling**: แสดง error messages เป็นภาษาไทยที่เข้าใจง่าย
8. ✅ **Testing**: Backend tests pass ≥80%, Frontend tests pass ≥60%
9. ✅ **Documentation**: อัปเดต PHASE2_COMPLETE.md เมื่อเสร็จสิ้น

---

## 🚀 Next Steps

หลังจาก Phase 2 เสร็จสิ้น จะเข้าสู่ **Phase 3: Room Control Dashboard** ซึ่งเป็น Phase ที่สำคัญที่สุด:

- แดชบอร์ดแสดงสถานะห้องแบบ real-time
- WebSocket integration
- Drag-and-drop room status changes
- Overtime alerts
- Telegram notifications

---

**Phase 2 Start Date**: 2025-10-13
**Estimated Completion**: 2025-10-16
**Status**: 🟡 Ready to Begin
