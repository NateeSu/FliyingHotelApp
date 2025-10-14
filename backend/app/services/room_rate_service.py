from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload
from typing import List, Optional
from fastapi import HTTPException, status
from datetime import date

from app.models.room_rate import RoomRate, StayType
from app.models.room_type import RoomType
from app.schemas.room_rate import RoomRateCreate, RoomRateUpdate


class RoomRateService:
    """Service layer for Room Rate operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        room_type_id: Optional[int] = None,
        stay_type: Optional[StayType] = None,
        is_active: Optional[bool] = None
    ) -> List[RoomRate]:
        """Get all room rates with optional filtering"""
        query = select(RoomRate).options(selectinload(RoomRate.room_type))

        # Apply filters
        conditions = []
        if room_type_id is not None:
            conditions.append(RoomRate.room_type_id == room_type_id)
        if stay_type is not None:
            conditions.append(RoomRate.stay_type == stay_type)
        if is_active is not None:
            conditions.append(RoomRate.is_active == is_active)

        if conditions:
            query = query.where(and_(*conditions))

        query = query.offset(skip).limit(limit).order_by(
            RoomRate.room_type_id,
            RoomRate.stay_type,
            RoomRate.effective_from.desc()
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, room_rate_id: int) -> Optional[RoomRate]:
        """Get room rate by ID"""
        result = await self.db.execute(
            select(RoomRate)
            .options(selectinload(RoomRate.room_type))
            .where(RoomRate.id == room_rate_id)
        )
        return result.scalar_one_or_none()

    async def get_current_rate(
        self,
        room_type_id: int,
        stay_type: StayType,
        check_date: date = None
    ) -> Optional[RoomRate]:
        """
        Get current active rate for a room type and stay type
        If check_date is provided, get the rate effective for that date
        """
        if check_date is None:
            check_date = date.today()

        result = await self.db.execute(
            select(RoomRate).where(
                and_(
                    RoomRate.room_type_id == room_type_id,
                    RoomRate.stay_type == stay_type,
                    RoomRate.effective_from <= check_date,
                    or_(
                        RoomRate.effective_to.is_(None),
                        RoomRate.effective_to >= check_date
                    ),
                    RoomRate.is_active == True
                )
            ).order_by(RoomRate.effective_from.desc())
        )
        return result.scalars().first()

    async def check_date_overlap(
        self,
        room_type_id: int,
        stay_type: StayType,
        effective_from: date,
        effective_to: Optional[date],
        exclude_rate_id: Optional[int] = None
    ) -> bool:
        """
        Check if the date range overlaps with existing rates
        Business Rule: Dates must not overlap for same room_type + stay_type
        """
        conditions = [
            RoomRate.room_type_id == room_type_id,
            RoomRate.stay_type == stay_type
        ]

        # Exclude current rate when updating
        if exclude_rate_id:
            conditions.append(RoomRate.id != exclude_rate_id)

        # Check for overlap
        # Case 1: New rate has no end date (effective_to = NULL)
        if effective_to is None:
            # Overlaps if existing rate has no end date OR end date >= new start date
            overlap_condition = or_(
                RoomRate.effective_to.is_(None),
                RoomRate.effective_to >= effective_from
            )
        # Case 2: New rate has end date
        else:
            # Overlaps if:
            # - Existing rate has no end date AND start date <= new end date
            # - OR date ranges overlap
            overlap_condition = or_(
                and_(
                    RoomRate.effective_to.is_(None),
                    RoomRate.effective_from <= effective_to
                ),
                and_(
                    RoomRate.effective_from <= effective_to,
                    or_(
                        RoomRate.effective_to.is_(None),
                        RoomRate.effective_to >= effective_from
                    )
                )
            )

        conditions.append(overlap_condition)

        result = await self.db.execute(
            select(RoomRate).where(and_(*conditions)).limit(1)
        )
        return result.scalar_one_or_none() is not None

    async def create(self, data: RoomRateCreate) -> RoomRate:
        """Create a new room rate"""
        # Verify room type exists
        room_type_result = await self.db.execute(
            select(RoomType).where(RoomType.id == data.room_type_id)
        )
        if not room_type_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="ไม่พบประเภทห้อง"
            )

        # Check for date overlap
        has_overlap = await self.check_date_overlap(
            room_type_id=data.room_type_id,
            stay_type=data.stay_type,
            effective_from=data.effective_from,
            effective_to=data.effective_to
        )

        if has_overlap:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ช่วงวันที่ซ้อนทับกับราคาที่มีอยู่แล้ว"
            )

        room_rate = RoomRate(**data.model_dump())
        self.db.add(room_rate)
        await self.db.commit()
        await self.db.refresh(room_rate)
        await self.db.refresh(room_rate, ["room_type"])

        return room_rate

    async def update(self, room_rate_id: int, data: RoomRateUpdate) -> RoomRate:
        """Update an existing room rate"""
        room_rate = await self.get_by_id(room_rate_id)
        if not room_rate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="ไม่พบอัตราค่าห้อง"
            )

        update_data = data.model_dump(exclude_unset=True)

        # If effective_to is being updated, check for overlap
        if "effective_to" in update_data:
            has_overlap = await self.check_date_overlap(
                room_type_id=room_rate.room_type_id,
                stay_type=room_rate.stay_type,
                effective_from=room_rate.effective_from,
                effective_to=update_data["effective_to"],
                exclude_rate_id=room_rate_id
            )

            if has_overlap:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="ช่วงวันที่ซ้อนทับกับราคาที่มีอยู่แล้ว"
                )

        # Update fields
        for field, value in update_data.items():
            setattr(room_rate, field, value)

        await self.db.commit()
        await self.db.refresh(room_rate)
        await self.db.refresh(room_rate, ["room_type"])

        return room_rate

    async def delete(self, room_rate_id: int) -> None:
        """
        Delete a room rate
        Business Rule: Cannot delete if referenced by bookings/check-ins (TODO in Phase 3/4)
        """
        room_rate = await self.get_by_id(room_rate_id)
        if not room_rate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="ไม่พบอัตราค่าห้อง"
            )

        # TODO: Check if rate is referenced by bookings or check-ins
        # For now, we'll allow deletion

        await self.db.delete(room_rate)
        await self.db.commit()

    async def get_rate_matrix(self) -> List[dict]:
        """
        Get room rate matrix for UI display
        Returns a list of room types with their overnight and temporary rates
        """
        # Get all active room types
        room_types_result = await self.db.execute(
            select(RoomType).where(RoomType.is_active == True).order_by(RoomType.id)
        )
        room_types = room_types_result.scalars().all()

        matrix = []
        for room_type in room_types:
            # Get current overnight rate
            overnight_rate = await self.get_current_rate(room_type.id, StayType.OVERNIGHT)

            # Get current temporary rate
            temporary_rate = await self.get_current_rate(room_type.id, StayType.TEMPORARY)

            matrix.append({
                "room_type_id": room_type.id,
                "room_type_name": room_type.name,
                "overnight_rate": float(overnight_rate.rate) if overnight_rate else None,
                "temporary_rate": float(temporary_rate.rate) if temporary_rate else None,
                "overnight_rate_id": overnight_rate.id if overnight_rate else None,
                "temporary_rate_id": temporary_rate.id if temporary_rate else None
            })

        return matrix

    async def update_matrix_rate(
        self,
        room_type_id: int,
        stay_type: StayType,
        new_rate: float
    ) -> RoomRate:
        """
        Update current rate for a room type and stay type
        If rate exists, updates it. If not, creates a new one.
        """
        # Get current rate
        current_rate = await self.get_current_rate(room_type_id, stay_type)

        if current_rate:
            # Update existing rate
            return await self.update(current_rate.id, RoomRateUpdate(rate=new_rate))
        else:
            # Create new rate
            return await self.create(
                RoomRateCreate(
                    room_type_id=room_type_id,
                    stay_type=stay_type,
                    rate=new_rate,
                    effective_from=date.today(),
                    effective_to=None,
                    is_active=True
                )
            )
