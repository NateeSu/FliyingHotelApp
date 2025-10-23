"""
Dashboard Service (Phase 3)
Business logic for dashboard operations
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import joinedload
from typing import List, Optional
from datetime import datetime, timedelta
from decimal import Decimal

from app.models import Room, RoomType, CheckIn, Customer, RoomRate, Booking
from app.models.room import RoomStatus
from app.models.check_in import CheckInStatusEnum, StayTypeEnum
from app.models.room_rate import StayType
from app.models.booking import BookingStatusEnum
from app.schemas.dashboard import DashboardRoomCard, DashboardStats, OvertimeAlert
from app.core.datetime_utils import now_thailand, today_thailand


class DashboardService:
    """Service for dashboard operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def _get_current_rates_for_room_type(self, room_type_id: int) -> tuple[Optional[Decimal], Optional[Decimal]]:
        """
        Get current active rates for a room type

        Returns:
            Tuple of (overnight_rate, temporary_rate)
        """
        today = now_thailand().date()

        # Query rates that are active and effective today
        stmt = (
            select(RoomRate.stay_type, RoomRate.rate)
            .where(
                RoomRate.room_type_id == room_type_id,
                RoomRate.is_active == True,
                RoomRate.effective_from <= today,
                or_(RoomRate.effective_to == None, RoomRate.effective_to >= today)
            )
        )

        result = await self.db.execute(stmt)
        rates = dict(result.all())

        overnight_rate = rates.get(StayType.OVERNIGHT)
        temporary_rate = rates.get(StayType.TEMPORARY)

        return overnight_rate, temporary_rate

    async def get_all_rooms_with_details(self) -> List[DashboardRoomCard]:
        """
        Get all rooms with check-in details and booking information for dashboard display

        Returns:
            List of DashboardRoomCard with full information including bookings
        """
        # Query rooms with room_type and current check_in
        stmt = (
            select(Room)
            .options(
                joinedload(Room.room_type),
                joinedload(Room.check_ins).joinedload(CheckIn.customer)
            )
            .where(Room.is_active == True)
            .order_by(Room.floor, Room.room_number)
        )

        result = await self.db.execute(stmt)
        rooms = result.unique().scalars().all()

        # Get today's date in Thailand timezone
        today = today_thailand()

        room_cards = []
        for room in rooms:
            # Get current check-in (status = checked_in)
            current_check_in = next(
                (ci for ci in room.check_ins if ci.status == CheckInStatusEnum.CHECKED_IN),
                None
            )

            # Get active booking for this room (if reserved)
            current_booking = None
            if room.status == RoomStatus.RESERVED:
                booking_stmt = (
                    select(Booking)
                    .options(joinedload(Booking.customer))
                    .where(
                        and_(
                            Booking.room_id == room.id,
                            Booking.status == BookingStatusEnum.CONFIRMED,
                            Booking.check_in_date == today
                        )
                    )
                )
                booking_result = await self.db.execute(booking_stmt)
                current_booking = booking_result.unique().scalar_one_or_none()

            # Calculate overtime if applicable using Thailand timezone
            is_overtime = False
            overtime_minutes = None
            if current_check_in and current_check_in.expected_check_out_time:
                now = now_thailand()
                if now > current_check_in.expected_check_out_time:
                    is_overtime = True
                    overtime_delta = now - current_check_in.expected_check_out_time
                    overtime_minutes = int(overtime_delta.total_seconds() / 60)

            # Get current rates for this room type
            overnight_rate, temporary_rate = await self._get_current_rates_for_room_type(room.room_type_id)

            room_card = DashboardRoomCard(
                id=room.id,
                room_number=room.room_number,
                floor=room.floor,
                status=room.status,
                room_type_id=room.room_type_id,
                room_type_name=room.room_type.name,
                room_type_description=room.room_type.description,
                overnight_rate=overnight_rate,
                temporary_rate=temporary_rate,
                check_in_id=current_check_in.id if current_check_in else None,
                customer_name=current_check_in.customer.full_name if current_check_in else None,
                customer_phone=current_check_in.customer.phone_number if current_check_in else None,
                stay_type=current_check_in.stay_type if current_check_in else None,
                check_in_time=current_check_in.check_in_time if current_check_in else None,
                expected_check_out_time=current_check_in.expected_check_out_time if current_check_in else None,
                # Booking information (Phase 7)
                booking_id=current_booking.id if current_booking else None,
                booking_customer_name=current_booking.customer.full_name if current_booking else None,
                booking_customer_phone=current_booking.customer.phone_number if current_booking else None,
                booking_check_in_date=current_booking.check_in_date.isoformat() if current_booking else None,
                booking_check_out_date=current_booking.check_out_date.isoformat() if current_booking else None,
                booking_deposit_amount=current_booking.deposit_amount if current_booking else None,
                is_overtime=is_overtime,
                overtime_minutes=overtime_minutes,
                qr_code=room.qr_code,
                notes=room.notes,
                is_active=room.is_active
            )
            room_cards.append(room_card)

        return room_cards

    async def get_dashboard_stats(self) -> DashboardStats:
        """
        Get dashboard statistics

        Returns:
            DashboardStats with counts and metrics
        """
        # Count rooms by status
        stmt = select(Room.status, func.count(Room.id)).where(Room.is_active == True).group_by(Room.status)
        result = await self.db.execute(stmt)
        status_counts = dict(result.all())

        total_rooms = sum(status_counts.values())
        available_rooms = status_counts.get(RoomStatus.AVAILABLE, 0)
        occupied_rooms = status_counts.get(RoomStatus.OCCUPIED, 0)
        cleaning_rooms = status_counts.get(RoomStatus.CLEANING, 0)
        reserved_rooms = status_counts.get(RoomStatus.RESERVED, 0)
        out_of_service_rooms = status_counts.get(RoomStatus.OUT_OF_SERVICE, 0)

        # Calculate occupancy rate
        occupancy_rate = (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0.0

        # Count check-ins today using Thailand timezone
        today_start = now_thailand().replace(hour=0, minute=0, second=0, microsecond=0)
        stmt = select(func.count(CheckIn.id)).where(CheckIn.check_in_time >= today_start)
        result = await self.db.execute(stmt)
        total_check_ins_today = result.scalar() or 0

        # Count by stay type
        stmt = (
            select(CheckIn.stay_type, func.count(CheckIn.id))
            .where(
                CheckIn.check_in_time >= today_start,
                CheckIn.status == CheckInStatusEnum.CHECKED_IN
            )
            .group_by(CheckIn.stay_type)
        )
        result = await self.db.execute(stmt)
        stay_type_counts = dict(result.all())

        overnight_stays = stay_type_counts.get(StayTypeEnum.OVERNIGHT, 0)
        temporary_stays = stay_type_counts.get(StayTypeEnum.TEMPORARY, 0)

        # Calculate revenue today (completed check-ins)
        stmt = (
            select(func.sum(CheckIn.total_amount))
            .where(
                CheckIn.check_in_time >= today_start,
                CheckIn.status == CheckInStatusEnum.CHECKED_OUT
            )
        )
        result = await self.db.execute(stmt)
        revenue_today = result.scalar() or Decimal(0)

        return DashboardStats(
            total_rooms=total_rooms,
            available_rooms=available_rooms,
            occupied_rooms=occupied_rooms,
            cleaning_rooms=cleaning_rooms,
            reserved_rooms=reserved_rooms,
            out_of_service_rooms=out_of_service_rooms,
            occupancy_rate=round(occupancy_rate, 2),
            total_check_ins_today=total_check_ins_today,
            overnight_stays=overnight_stays,
            temporary_stays=temporary_stays,
            revenue_today=revenue_today
        )

    async def get_overtime_alerts(self) -> List[OvertimeAlert]:
        """
        Get all check-ins that are currently overtime

        Returns:
            List of OvertimeAlert
        """
        now = now_thailand()

        stmt = (
            select(CheckIn)
            .options(
                joinedload(CheckIn.customer),
                joinedload(CheckIn.room)
            )
            .where(
                CheckIn.status == CheckInStatusEnum.CHECKED_IN,
                CheckIn.expected_check_out_time < now
            )
            .order_by(CheckIn.expected_check_out_time)
        )

        result = await self.db.execute(stmt)
        check_ins = result.unique().scalars().all()

        alerts = []
        for check_in in check_ins:
            overtime_delta = now - check_in.expected_check_out_time
            overtime_minutes = int(overtime_delta.total_seconds() / 60)

            alert = OvertimeAlert(
                room_id=check_in.room_id,
                room_number=check_in.room.room_number,
                check_in_id=check_in.id,
                customer_name=check_in.customer.full_name,
                stay_type=check_in.stay_type,
                expected_check_out_time=check_in.expected_check_out_time,
                overtime_minutes=overtime_minutes,
                created_at=check_in.created_at
            )
            alerts.append(alert)

        return alerts

    async def get_room_by_id(self, room_id: int) -> Optional[Room]:
        """Get room by ID with relationships"""
        stmt = (
            select(Room)
            .options(
                joinedload(Room.room_type),
                joinedload(Room.check_ins).joinedload(CheckIn.customer)
            )
            .where(Room.id == room_id)
        )
        result = await self.db.execute(stmt)
        return result.unique().scalar_one_or_none()
