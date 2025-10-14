from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import List, Optional
from fastapi import HTTPException, status

from app.models.room_type import RoomType
from app.models.room import Room
from app.schemas.room_type import RoomTypeCreate, RoomTypeUpdate


class RoomTypeService:
    """Service layer for Room Type operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None
    ) -> List[RoomType]:
        """Get all room types with optional filtering"""
        query = select(RoomType)

        if is_active is not None:
            query = query.where(RoomType.is_active == is_active)

        query = query.offset(skip).limit(limit).order_by(RoomType.id)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, room_type_id: int) -> Optional[RoomType]:
        """Get room type by ID"""
        result = await self.db.execute(
            select(RoomType).where(RoomType.id == room_type_id)
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[RoomType]:
        """Get room type by name"""
        result = await self.db.execute(
            select(RoomType).where(RoomType.name == name)
        )
        return result.scalar_one_or_none()

    async def create(self, data: RoomTypeCreate) -> RoomType:
        """Create a new room type"""
        # Check if name already exists
        existing = await self.get_by_name(data.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ชื่อประเภทห้องนี้มีอยู่แล้ว"
            )

        room_type = RoomType(**data.model_dump())
        self.db.add(room_type)
        await self.db.commit()
        await self.db.refresh(room_type)
        return room_type

    async def update(self, room_type_id: int, data: RoomTypeUpdate) -> RoomType:
        """Update an existing room type"""
        room_type = await self.get_by_id(room_type_id)
        if not room_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="ไม่พบประเภทห้อง"
            )

        # Check if new name conflicts with existing room type
        update_data = data.model_dump(exclude_unset=True)
        if "name" in update_data and update_data["name"] != room_type.name:
            existing = await self.get_by_name(update_data["name"])
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="ชื่อประเภทห้องนี้มีอยู่แล้ว"
                )

        # Update fields
        for field, value in update_data.items():
            setattr(room_type, field, value)

        await self.db.commit()
        await self.db.refresh(room_type)
        return room_type

    async def delete(self, room_type_id: int) -> None:
        """
        Delete a room type
        Business Rule: Cannot delete if rooms are using this type
        """
        room_type = await self.get_by_id(room_type_id)
        if not room_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="ไม่พบประเภทห้อง"
            )

        # Check if any rooms are using this room type
        result = await self.db.execute(
            select(Room).where(Room.room_type_id == room_type_id).limit(1)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ไม่สามารถลบประเภทห้องที่มีห้องพักใช้งานอยู่ได้ กรุณาลบหรือเปลี่ยนประเภทห้องพักก่อน"
            )

        await self.db.delete(room_type)
        await self.db.commit()

    async def get_with_stats(self, room_type_id: int) -> dict:
        """Get room type with room statistics"""
        room_type = await self.get_by_id(room_type_id)
        if not room_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="ไม่พบประเภทห้อง"
            )

        # Count total rooms
        total_rooms_result = await self.db.execute(
            select(func.count(Room.id)).where(
                Room.room_type_id == room_type_id,
                Room.is_active == True
            )
        )
        total_rooms = total_rooms_result.scalar() or 0

        # Count available rooms
        available_rooms_result = await self.db.execute(
            select(func.count(Room.id)).where(
                Room.room_type_id == room_type_id,
                Room.status == "available",
                Room.is_active == True
            )
        )
        available_rooms = available_rooms_result.scalar() or 0

        return {
            **room_type.__dict__,
            "total_rooms": total_rooms,
            "available_rooms": available_rooms
        }
