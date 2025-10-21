"""
Check-In Service (Phase 4)
Handles check-in business logic for both overnight and temporary stays
"""
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import joinedload

from app.models import CheckIn, Room, RoomRate, Customer, Booking, RoomStatus
from app.models.check_in import StayTypeEnum, CheckInStatusEnum
from app.schemas.check_in import CheckInCreate, CheckInResponse
from app.core.websocket import manager as websocket_manager
from app.core.datetime_utils import now_thailand


class CheckInService:
    """Service for managing check-ins"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_check_in(
        self,
        check_in_data: CheckInCreate,
        customer_id: int,
        created_by_user_id: int
    ) -> CheckIn:
        """
        Create a new check-in

        Business Logic:
        - For overnight: expected_check_out = next day at 12:00
        - For temporary: expected_check_out = check_in_time + 3 hours
        - Look up room rate based on stay type
        - Update room status to 'occupied'
        - Broadcast WebSocket event
        - If booking_id provided, link to booking and deduct deposit
        """
        # Validate room exists and is available
        room = await self._get_and_validate_room(check_in_data.room_id)

        # Get room rate for this room type and stay type
        room_rate = await self._get_room_rate(
            room.room_type_id,
            check_in_data.stay_type
        )

        if not room_rate:
            raise ValueError(
                f"ไม่พบอัตราค่าห้องสำหรับประเภทห้อง {room.room_type.name} "
                f"และประเภทการเข้าพัก {check_in_data.stay_type}"
            )

        # Calculate expected check-out time
        # Use Thailand timezone for check-in time
        check_in_time = check_in_data.check_in_time or now_thailand()
        expected_check_out_time = self._calculate_expected_checkout(
            check_in_time,
            check_in_data.stay_type,
            check_in_data.number_of_nights
        )

        # Calculate amounts
        base_amount, total_amount = self._calculate_amounts(
            room_rate.rate,  # Fixed: field name is 'rate', not 'rate_per_unit'
            check_in_data.stay_type,
            check_in_data.number_of_nights,
            check_in_data.booking_id,
            check_in_data.deposit_amount
        )

        # Create check-in record
        check_in = CheckIn(
            room_id=check_in_data.room_id,
            customer_id=customer_id,
            booking_id=check_in_data.booking_id,
            stay_type=check_in_data.stay_type,
            number_of_nights=check_in_data.number_of_nights,
            number_of_guests=check_in_data.number_of_guests,
            check_in_time=check_in_time,
            expected_check_out_time=expected_check_out_time,
            status=CheckInStatusEnum.CHECKED_IN,
            base_amount=base_amount,
            total_amount=total_amount,
            payment_method=check_in_data.payment_method,
            notes=check_in_data.notes,
            created_by=created_by_user_id
        )

        self.db.add(check_in)

        # Update room status to occupied
        room.status = RoomStatus.OCCUPIED

        # If booking exists, mark as checked in
        if check_in_data.booking_id:
            booking = await self._get_booking(check_in_data.booking_id)
            if booking:
                booking.status = "checked_in"

        # Commit transaction
        await self.db.commit()
        await self.db.refresh(check_in)

        # Load relationships for response
        await self.db.refresh(check_in, ['room', 'customer', 'booking'])

        # Broadcast WebSocket event
        await self._broadcast_check_in_event(check_in, room)

        return check_in

    async def get_check_in_by_id(
        self,
        check_in_id: int,
        include_relations: bool = True
    ) -> Optional[CheckIn]:
        """Get check-in by ID with optional relationship loading"""
        stmt = select(CheckIn).where(CheckIn.id == check_in_id)

        if include_relations:
            stmt = stmt.options(
                joinedload(CheckIn.room).joinedload(Room.room_type),
                joinedload(CheckIn.customer),
                joinedload(CheckIn.booking)
            )

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active_check_in_by_room(
        self,
        room_id: int
    ) -> Optional[CheckIn]:
        """Get active check-in for a room (if any)"""
        stmt = select(CheckIn).where(
            and_(
                CheckIn.room_id == room_id,
                CheckIn.status == CheckInStatusEnum.CHECKED_IN
            )
        ).options(
            joinedload(CheckIn.customer),
            joinedload(CheckIn.room)
        )

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    def _calculate_expected_checkout(
        self,
        check_in_time: datetime,
        stay_type: StayTypeEnum,
        number_of_nights: Optional[int] = None
    ) -> datetime:
        """
        Calculate expected check-out time based on stay type

        Overnight: check_in_date + number_of_nights days at 12:00
        Temporary: check_in_time + 3 hours
        """
        if stay_type == StayTypeEnum.OVERNIGHT:
            if not number_of_nights or number_of_nights < 1:
                raise ValueError("จำนวนคืนต้องมากกว่า 0 สำหรับการเข้าพักแบบค้างคืน")

            # Add number_of_nights days and set time to 12:00
            checkout_date = check_in_time.date() + timedelta(days=number_of_nights)
            return datetime.combine(checkout_date, datetime.min.time().replace(hour=12))

        else:  # TEMPORARY
            # Add 3 hours to check-in time
            return check_in_time + timedelta(hours=3)

    def _calculate_amounts(
        self,
        rate_per_unit: Decimal,
        stay_type: StayTypeEnum,
        number_of_nights: Optional[int],
        booking_id: Optional[int],
        deposit_amount: Optional[Decimal]
    ) -> Tuple[Decimal, Decimal]:
        """
        Calculate base amount and total amount

        Base amount = rate_per_unit * units (nights or sessions)
        Total amount = base_amount - deposit (if from booking)
        """
        if stay_type == StayTypeEnum.OVERNIGHT:
            units = number_of_nights or 1
        else:
            units = 1  # Temporary is always 1 session

        base_amount = rate_per_unit * Decimal(units)

        # Deduct deposit if booking exists
        total_amount = base_amount
        if booking_id and deposit_amount:
            total_amount = base_amount - deposit_amount
            if total_amount < 0:
                total_amount = Decimal(0)

        return base_amount, total_amount

    async def _get_and_validate_room(self, room_id: int) -> Room:
        """Get room and validate it's available for check-in"""
        stmt = select(Room).where(Room.id == room_id).options(
            joinedload(Room.room_type)
        )
        result = await self.db.execute(stmt)
        room = result.scalar_one_or_none()

        if not room:
            raise ValueError(f"ไม่พบห้องหมายเลข {room_id}")

        if room.status not in [RoomStatus.AVAILABLE, RoomStatus.RESERVED]:
            raise ValueError(
                f"ห้อง {room.room_number} ไม่สามารถเช็คอินได้ "
                f"(สถานะปัจจุบัน: {room.status})"
            )

        return room

    async def _get_room_rate(
        self,
        room_type_id: int,
        stay_type: StayTypeEnum
    ) -> Optional[RoomRate]:
        """Get room rate for room type and stay type"""
        stmt = select(RoomRate).where(
            and_(
                RoomRate.room_type_id == room_type_id,
                RoomRate.stay_type == stay_type,
                RoomRate.is_active == True
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def _get_booking(self, booking_id: int) -> Optional[Booking]:
        """Get booking by ID"""
        stmt = select(Booking).where(Booking.id == booking_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def _broadcast_check_in_event(self, check_in: CheckIn, room: Room):
        """Broadcast check-in event via WebSocket"""
        await websocket_manager.broadcast({
            "event": "check_in_created",
            "data": {
                "check_in_id": check_in.id,
                "room_id": room.id,
                "room_number": room.room_number,
                "customer_name": check_in.customer.full_name if check_in.customer else None,
                "stay_type": check_in.stay_type,
                "check_in_time": check_in.check_in_time.isoformat(),
                "expected_check_out_time": check_in.expected_check_out_time.isoformat(),
                "timestamp": now_thailand().isoformat()
            }
        })

        # Also broadcast room status change
        await websocket_manager.broadcast_room_status_change(
            room_id=room.id,
            old_status="available",
            new_status="occupied"
        )

    async def transfer_room(
        self,
        check_in_id: int,
        new_room_id: int,
        reason: Optional[str],
        transferred_by_user_id: int
    ) -> Tuple[CheckIn, Room, Room]:
        """
        Transfer a guest from current room to a new room

        Business Logic:
        1. Validate check-in exists and is active
        2. Validate new room is available
        3. Validate new room is same room type as old room
        4. Update check_in.room_id to new room
        5. Update old room status to 'cleaning'
        6. Update new room status to 'occupied'
        7. TODO Phase 5: Create housekeeping task for old room
        8. TODO Phase 5: Send Telegram notification to housekeeping
        9. Broadcast WebSocket events

        Returns:
            Tuple of (check_in, old_room, new_room)
        """
        # Get check-in with relationships
        check_in = await self.get_check_in_by_id(check_in_id, include_relations=True)
        if not check_in:
            raise ValueError(f"ไม่พบการเช็คอิน ID {check_in_id}")

        if check_in.status != CheckInStatusEnum.CHECKED_IN:
            raise ValueError(
                f"ไม่สามารถย้ายห้องได้ เนื่องจากสถานะการเช็คอินไม่ถูกต้อง "
                f"(สถานะปัจจุบัน: {check_in.status})"
            )

        # Get old room
        old_room = check_in.room
        if not old_room:
            raise ValueError("ไม่พบข้อมูลห้องเดิม")

        # Validate new room exists and is available
        new_room = await self._get_and_validate_room(new_room_id)

        # Validate same room type
        if old_room.room_type_id != new_room.room_type_id:
            raise ValueError(
                f"ไม่สามารถย้ายห้องได้ เนื่องจากประเภทห้องไม่ตรงกัน\n"
                f"ห้องเดิม: {old_room.room_type.name} → ห้องใหม่: {new_room.room_type.name}\n"
                f"สามารถย้ายได้เฉพาะห้องประเภทเดียวกันเท่านั้น"
            )

        # Prevent transfer to same room
        if old_room.id == new_room.id:
            raise ValueError("ไม่สามารถย้ายไปห้องเดิมได้")

        # Update check-in to new room
        check_in.room_id = new_room_id
        if reason:
            # Append transfer reason to notes
            transfer_note = f"\n[ย้ายห้อง {now_thailand().strftime('%Y-%m-%d %H:%M')}] {old_room.room_number} → {new_room.room_number}: {reason}"
            check_in.notes = (check_in.notes or "") + transfer_note

        # Update room statuses
        old_room.status = RoomStatus.CLEANING
        new_room.status = RoomStatus.OCCUPIED

        # Phase 5: Create housekeeping task for old room
        from app.models import HousekeepingTask
        from app.models.housekeeping_task import HousekeepingTaskStatusEnum, HousekeepingTaskPriorityEnum

        housekeeping_task = HousekeepingTask(
            room_id=old_room.id,
            check_in_id=check_in_id,
            title=f"ทำความสะอาดห้อง {old_room.room_number}",
            description=f"ทำความสะอาดหลังย้ายห้อง (ลูกค้าย้ายไปห้อง {new_room.room_number})",
            priority=HousekeepingTaskPriorityEnum.HIGH,
            status=HousekeepingTaskStatusEnum.PENDING,
            created_by=transferred_by_user_id,
            notes=reason
        )
        self.db.add(housekeeping_task)

        # Commit changes
        await self.db.commit()
        await self.db.refresh(check_in)
        await self.db.refresh(old_room)
        await self.db.refresh(new_room)
        await self.db.refresh(housekeeping_task)

        # Phase 5: Send Telegram notification (optional - can be implemented later)
        # from app.services.telegram_service import TelegramService
        # telegram_service = TelegramService()
        # await telegram_service.send_housekeeping_task_notification(housekeeping_task)

        # Broadcast WebSocket events
        await self._broadcast_room_transfer_event(
            check_in=check_in,
            old_room=old_room,
            new_room=new_room,
            transferred_by_user_id=transferred_by_user_id,
            reason=reason
        )

        return check_in, old_room, new_room

    async def _broadcast_room_transfer_event(
        self,
        check_in: CheckIn,
        old_room: Room,
        new_room: Room,
        transferred_by_user_id: int,
        reason: Optional[str]
    ):
        """Broadcast room transfer event via WebSocket"""
        # Room transfer event
        await websocket_manager.broadcast({
            "event": "room_transferred",
            "data": {
                "check_in_id": check_in.id,
                "customer_name": check_in.customer.full_name if check_in.customer else None,
                "old_room_id": old_room.id,
                "old_room_number": old_room.room_number,
                "new_room_id": new_room.id,
                "new_room_number": new_room.room_number,
                "transferred_by": transferred_by_user_id,
                "reason": reason,
                "timestamp": now_thailand().isoformat()
            }
        })

        # Broadcast old room status change (occupied → cleaning)
        await websocket_manager.broadcast_room_status_change(
            room_id=old_room.id,
            old_status="occupied",
            new_status="cleaning"
        )

        # Broadcast new room status change (available → occupied)
        await websocket_manager.broadcast_room_status_change(
            room_id=new_room.id,
            old_status="available",
            new_status="occupied"
        )
