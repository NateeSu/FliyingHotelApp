from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from typing import List, Optional
from fastapi import HTTPException, status
import uuid

from app.models.room import Room, RoomStatus
from app.models.room_type import RoomType
from app.schemas.room import RoomCreate, RoomUpdate, RoomStatusUpdate


class RoomService:
    """Service layer for Room operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    def _generate_qr_code(self) -> str:
        """Generate unique QR code for room"""
        return f"ROOM-{str(uuid.uuid4())[:8].upper()}"

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        floor: Optional[int] = None,
        status: Optional[RoomStatus] = None,
        room_type_id: Optional[int] = None,
        is_active: Optional[bool] = None
    ) -> List[Room]:
        """Get all rooms with optional filtering"""
        query = select(Room).options(selectinload(Room.room_type))

        # Apply filters
        conditions = []
        if floor is not None:
            conditions.append(Room.floor == floor)
        if status is not None:
            conditions.append(Room.status == status)
        if room_type_id is not None:
            conditions.append(Room.room_type_id == room_type_id)
        if is_active is not None:
            conditions.append(Room.is_active == is_active)

        if conditions:
            query = query.where(and_(*conditions))

        query = query.offset(skip).limit(limit).order_by(Room.floor, Room.room_number)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, room_id: int) -> Optional[Room]:
        """Get room by ID with room type"""
        result = await self.db.execute(
            select(Room)
            .options(selectinload(Room.room_type))
            .where(Room.id == room_id)
        )
        return result.scalar_one_or_none()

    async def get_by_room_number(self, room_number: str) -> Optional[Room]:
        """Get room by room number"""
        result = await self.db.execute(
            select(Room).where(Room.room_number == room_number)
        )
        return result.scalar_one_or_none()

    async def create(self, data: RoomCreate) -> Room:
        """Create a new room"""
        # Check if room number already exists
        existing = await self.get_by_room_number(data.room_number)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="หมายเลขห้องนี้มีอยู่แล้ว"
            )

        # Verify room type exists
        room_type_result = await self.db.execute(
            select(RoomType).where(RoomType.id == data.room_type_id)
        )
        room_type = room_type_result.scalar_one_or_none()
        if not room_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="ไม่พบประเภทห้อง"
            )

        # Create room with auto-generated QR code
        room_data = data.model_dump()
        room_data["qr_code"] = self._generate_qr_code()
        room_data["status"] = RoomStatus.AVAILABLE  # Default status

        room = Room(**room_data)
        self.db.add(room)
        await self.db.commit()
        await self.db.refresh(room)

        # Load room type relationship
        await self.db.refresh(room, ["room_type"])

        return room

    async def update(self, room_id: int, data: RoomUpdate) -> Room:
        """
        Update an existing room
        Business Rule: Cannot change room_type if status is occupied or reserved
        """
        room = await self.get_by_id(room_id)
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="ไม่พบห้องพัก"
            )

        update_data = data.model_dump(exclude_unset=True)

        # Check if room number is being changed and if it conflicts
        if "room_number" in update_data and update_data["room_number"] != room.room_number:
            existing = await self.get_by_room_number(update_data["room_number"])
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="หมายเลขห้องนี้มีอยู่แล้ว"
                )

        # Business Rule: Cannot change room_type if room is occupied or reserved
        if "room_type_id" in update_data and update_data["room_type_id"] != room.room_type_id:
            if room.status in [RoomStatus.OCCUPIED, RoomStatus.RESERVED]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="ไม่สามารถเปลี่ยนประเภทห้องที่มีผู้พักหรือจองแล้วได้"
                )

            # Verify new room type exists
            room_type_result = await self.db.execute(
                select(RoomType).where(RoomType.id == update_data["room_type_id"])
            )
            if not room_type_result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="ไม่พบประเภทห้อง"
                )

        # Update fields
        for field, value in update_data.items():
            setattr(room, field, value)

        await self.db.commit()
        await self.db.refresh(room)
        await self.db.refresh(room, ["room_type"])

        return room

    async def update_status(self, room_id: int, new_status: RoomStatus) -> Room:
        """
        Update room status
        This will be used extensively by check-in/check-out/housekeeping systems
        """
        room = await self.get_by_id(room_id)
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="ไม่พบห้องพัก"
            )

        old_status = room.status
        room.status = new_status

        await self.db.commit()
        await self.db.refresh(room)

        # TODO: Broadcast WebSocket event for real-time dashboard update
        # await websocket_manager.broadcast({
        #     "event": "room_status_changed",
        #     "data": {
        #         "room_id": room.id,
        #         "room_number": room.room_number,
        #         "old_status": old_status.value,
        #         "new_status": new_status.value,
        #         "timestamp": datetime.now().isoformat()
        #     }
        # })

        # Auto control breaker based on room status change
        if old_status != new_status:
            try:
                from app.services.breaker_service import BreakerService
                breaker_service = BreakerService(self.db)
                await breaker_service.auto_control_on_room_status_change(
                    room_id=room.id,
                    old_status=old_status,
                    new_status=new_status
                )
            except Exception as e:
                # Log error but don't block room status update
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to auto-control breaker for room {room.id}: {str(e)}", exc_info=True)

        return room

    async def delete(self, room_id: int) -> None:
        """
        Delete a room
        Business Rule: Cannot delete if room is occupied or reserved
        """
        room = await self.get_by_id(room_id)
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="ไม่พบห้องพัก"
            )

        # Business Rule: Cannot delete occupied or reserved rooms
        if room.status in [RoomStatus.OCCUPIED, RoomStatus.RESERVED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ไม่สามารถลบห้องที่มีผู้พักหรือจองแล้วได้"
            )

        # TODO: Check if room has check-in/booking history
        # For now, we'll allow deletion

        await self.db.delete(room)
        await self.db.commit()

    async def get_available_rooms(self, room_type_id: Optional[int] = None) -> List[Room]:
        """Get all available rooms, optionally filtered by room type"""
        conditions = [
            Room.status == RoomStatus.AVAILABLE,
            Room.is_active == True
        ]

        if room_type_id:
            conditions.append(Room.room_type_id == room_type_id)

        result = await self.db.execute(
            select(Room)
            .options(selectinload(Room.room_type))
            .where(and_(*conditions))
            .order_by(Room.floor, Room.room_number)
        )
        return list(result.scalars().all())

    async def get_rooms_by_floor(self, floor: int) -> List[Room]:
        """Get all rooms on a specific floor"""
        result = await self.db.execute(
            select(Room)
            .options(selectinload(Room.room_type))
            .where(Room.floor == floor)
            .order_by(Room.room_number)
        )
        return list(result.scalars().all())
