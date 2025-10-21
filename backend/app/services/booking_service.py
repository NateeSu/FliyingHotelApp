"""
Booking Service (Phase 7)
Business logic for booking management
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, Date, cast
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import date, datetime, timedelta
import httpx

from app.models.booking import Booking, BookingStatusEnum
from app.models.room import Room, RoomStatus
from app.models.customer import Customer
from app.models.user import User
from app.models.room_rate import RoomRate
from app.schemas.booking import (
    BookingCreate,
    BookingUpdate,
    BookingResponse,
    BookingCalendarEvent,
    PublicHoliday,
    RoomAvailabilityResponse
)
from app.core.websocket import websocket_manager
from app.core.datetime_utils import now_thailand


class BookingService:
    """Service for booking management"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_booking(
        self,
        booking_data: BookingCreate,
        created_by_user_id: int
    ) -> Booking:
        """
        Create a new booking

        Args:
            booking_data: Booking creation data
            created_by_user_id: User ID creating the booking

        Returns:
            Created booking

        Raises:
            ValueError: If room not available or validation fails
        """
        # 1. Validate room exists and is not out of service
        room = await self.db.get(Room, booking_data.room_id)
        if not room:
            raise ValueError("ไม่พบห้องที่ระบุ")

        if room.status == RoomStatus.OUT_OF_SERVICE:
            raise ValueError("ห้องนี้ไม่พร้อมให้บริการ")

        # 2. Check room availability
        is_available = await self.check_room_availability(
            room_id=booking_data.room_id,
            check_in_date=booking_data.check_in_date,
            check_out_date=booking_data.check_out_date
        )

        if not is_available:
            raise ValueError("ห้องนี้ไม่ว่างในช่วงเวลาที่เลือก")

        # 3. Validate customer exists
        customer = await self.db.get(Customer, booking_data.customer_id)
        if not customer:
            raise ValueError("ไม่พบข้อมูลลูกค้า")

        # 4. Calculate number of nights
        number_of_nights = (booking_data.check_out_date - booking_data.check_in_date).days

        if number_of_nights <= 0:
            raise ValueError("จำนวนคืนต้องมากกว่า 0")

        # 5. Create booking
        booking = Booking(
            customer_id=booking_data.customer_id,
            room_id=booking_data.room_id,
            check_in_date=booking_data.check_in_date,
            check_out_date=booking_data.check_out_date,
            number_of_nights=number_of_nights,
            total_amount=booking_data.total_amount,
            deposit_amount=booking_data.deposit_amount,
            notes=booking_data.notes,
            status=BookingStatusEnum.CONFIRMED,  # Default to confirmed
            created_by=created_by_user_id,
            created_at=now_thailand(),
            updated_at=now_thailand()
        )

        self.db.add(booking)
        await self.db.commit()
        await self.db.refresh(booking)

        # 6. If booking is for today, update room status to reserved
        today = date.today()
        if booking.check_in_date == today:
            room.status = RoomStatus.RESERVED
            await self.db.commit()

            # Broadcast room status change
            await self._broadcast_room_status_change(room.id, RoomStatus.AVAILABLE, RoomStatus.RESERVED)

        # 7. Reload booking with eager-loaded relationships
        booking = await self.get_booking_by_id(booking.id, include_relations=True)
        return booking

    async def get_booking_by_id(
        self,
        booking_id: int,
        include_relations: bool = True
    ) -> Optional[Booking]:
        """Get booking by ID with optional relations"""
        if include_relations:
            stmt = (
                select(Booking)
                .options(
                    selectinload(Booking.customer),
                    selectinload(Booking.room).selectinload(Room.room_type),
                    selectinload(Booking.creator)
                )
                .where(Booking.id == booking_id)
            )
            result = await self.db.execute(stmt)
            return result.scalar_one_or_none()
        else:
            return await self.db.get(Booking, booking_id)


    async def get_bookings(
        self,
        status: Optional[BookingStatusEnum] = None,
        room_id: Optional[int] = None,
        customer_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[Booking], int]:
        """
        Get bookings with filters

        Returns:
            Tuple of (bookings list, total count)
        """
        # Base query
        stmt = select(Booking).options(
            selectinload(Booking.customer),
            selectinload(Booking.room).selectinload(Room.room_type),
            selectinload(Booking.creator)
        )

        # Apply filters
        conditions = []

        if status:
            conditions.append(Booking.status == status)

        if room_id:
            conditions.append(Booking.room_id == room_id)

        if customer_id:
            conditions.append(Booking.customer_id == customer_id)

        if start_date:
            conditions.append(Booking.check_in_date >= start_date)

        if end_date:
            conditions.append(Booking.check_out_date <= end_date)

        if conditions:
            stmt = stmt.where(and_(*conditions))

        # Order by check_in_date desc
        stmt = stmt.order_by(Booking.check_in_date.desc())

        # Count total
        count_stmt = select(func.count()).select_from(Booking)
        if conditions:
            count_stmt = count_stmt.where(and_(*conditions))

        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar()

        # Apply pagination
        stmt = stmt.offset(skip).limit(limit)

        result = await self.db.execute(stmt)
        bookings = result.scalars().all()

        return list(bookings), total

    async def update_booking(
        self,
        booking_id: int,
        booking_data: BookingUpdate,
        user_id: int
    ) -> Booking:
        """
        Update booking

        Args:
            booking_id: Booking ID
            booking_data: Update data
            user_id: User performing update

        Returns:
            Updated booking

        Raises:
            ValueError: If booking not found or validation fails
        """
        booking = await self.get_booking_by_id(booking_id, include_relations=False)
        if not booking:
            raise ValueError("ไม่พบการจองที่ระบุ")

        # Cannot update checked-in, completed, or cancelled bookings
        if booking.status in [BookingStatusEnum.CHECKED_IN, BookingStatusEnum.COMPLETED, BookingStatusEnum.CANCELLED]:
            raise ValueError(f"ไม่สามารถแก้ไขการจองที่มีสถานะ {booking.status.value} ได้")

        # If changing dates, check availability
        if booking_data.check_in_date or booking_data.check_out_date:
            new_check_in = booking_data.check_in_date or booking.check_in_date
            new_check_out = booking_data.check_out_date or booking.check_out_date

            # Validate dates
            if new_check_out <= new_check_in:
                raise ValueError("วันเช็คเอาท์ต้องหลังวันเช็คอิน")

            # Check availability (exclude current booking)
            is_available = await self.check_room_availability(
                room_id=booking.room_id,
                check_in_date=new_check_in,
                check_out_date=new_check_out,
                exclude_booking_id=booking_id
            )

            if not is_available:
                raise ValueError("ห้องนี้ไม่ว่างในช่วงเวลาที่เลือก")

            # Update fields
            booking.check_in_date = new_check_in
            booking.check_out_date = new_check_out
            booking.number_of_nights = (new_check_out - new_check_in).days

        # Update other fields
        if booking_data.total_amount is not None:
            booking.total_amount = booking_data.total_amount

        if booking_data.deposit_amount is not None:
            if booking_data.deposit_amount > booking.total_amount:
                raise ValueError("เงินมัดจำต้องไม่เกินยอดรวม")
            booking.deposit_amount = booking_data.deposit_amount

        if booking_data.notes is not None:
            booking.notes = booking_data.notes

        booking.updated_at = now_thailand()

        await self.db.commit()
        await self.db.refresh(booking)

        return booking

    async def cancel_booking(
        self,
        booking_id: int,
        user_id: int
    ) -> Booking:
        """
        Cancel booking

        Args:
            booking_id: Booking ID
            user_id: User cancelling the booking

        Returns:
            Cancelled booking

        Raises:
            ValueError: If booking not found or already cancelled/completed
        """
        booking = await self.get_booking_by_id(booking_id, include_relations=True)
        if not booking:
            raise ValueError("ไม่พบการจองที่ระบุ")

        # Cannot cancel checked-in or completed bookings
        if booking.status == BookingStatusEnum.CHECKED_IN:
            raise ValueError("ไม่สามารถยกเลิกการจองที่เช็คอินแล้ว")

        if booking.status == BookingStatusEnum.COMPLETED:
            raise ValueError("ไม่สามารถยกเลิกการจองที่เสร็จสมบูรณ์แล้ว")

        if booking.status == BookingStatusEnum.CANCELLED:
            raise ValueError("การจองนี้ถูกยกเลิกไปแล้ว")

        # Update status
        old_status = booking.status
        booking.status = BookingStatusEnum.CANCELLED
        booking.cancelled_at = now_thailand()
        booking.updated_at = now_thailand()

        # If room was reserved for this booking, revert to available
        room = booking.room
        if room.status == RoomStatus.RESERVED:
            # Check if there are other bookings for this room today
            today = date.today()
            other_booking_exists = await self._has_other_booking_for_date(
                room_id=room.id,
                check_date=today,
                exclude_booking_id=booking_id
            )

            if not other_booking_exists:
                old_room_status = room.status
                room.status = RoomStatus.AVAILABLE
                await self._broadcast_room_status_change(room.id, old_room_status, RoomStatus.AVAILABLE)

        await self.db.commit()
        await self.db.refresh(booking)

        return booking

    async def check_room_availability(
        self,
        room_id: int,
        check_in_date: date,
        check_out_date: date,
        exclude_booking_id: Optional[int] = None
    ) -> bool:
        """
        Check if room is available for given date range

        Returns:
            True if available, False otherwise
        """
        # Query for conflicting bookings
        stmt = select(Booking).where(
            and_(
                Booking.room_id == room_id,
                Booking.status.in_([
                    BookingStatusEnum.PENDING,
                    BookingStatusEnum.CONFIRMED,
                    BookingStatusEnum.CHECKED_IN
                ]),
                or_(
                    # New booking starts during existing booking
                    and_(
                        Booking.check_in_date <= check_in_date,
                        Booking.check_out_date > check_in_date
                    ),
                    # New booking ends during existing booking
                    and_(
                        Booking.check_in_date < check_out_date,
                        Booking.check_out_date >= check_out_date
                    ),
                    # New booking completely contains existing booking
                    and_(
                        Booking.check_in_date >= check_in_date,
                        Booking.check_out_date <= check_out_date
                    )
                )
            )
        )

        # Exclude specific booking (for updates)
        if exclude_booking_id:
            stmt = stmt.where(Booking.id != exclude_booking_id)

        result = await self.db.execute(stmt)
        conflicting_bookings = result.scalars().all()

        return len(conflicting_bookings) == 0

    async def get_conflicting_bookings(
        self,
        room_id: int,
        check_in_date: date,
        check_out_date: date,
        exclude_booking_id: Optional[int] = None
    ) -> List[Booking]:
        """Get list of conflicting bookings for a date range"""
        from sqlalchemy.orm import selectinload

        stmt = select(Booking).options(
            selectinload(Booking.customer),
            selectinload(Booking.room).selectinload(Room.room_type)
        ).where(
            and_(
                Booking.room_id == room_id,
                Booking.status.in_([
                    BookingStatusEnum.PENDING,
                    BookingStatusEnum.CONFIRMED,
                    BookingStatusEnum.CHECKED_IN
                ]),
                or_(
                    and_(
                        Booking.check_in_date <= check_in_date,
                        Booking.check_out_date > check_in_date
                    ),
                    and_(
                        Booking.check_in_date < check_out_date,
                        Booking.check_out_date >= check_out_date
                    ),
                    and_(
                        Booking.check_in_date >= check_in_date,
                        Booking.check_out_date <= check_out_date
                    )
                )
            )
        )

        if exclude_booking_id:
            stmt = stmt.where(Booking.id != exclude_booking_id)

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_calendar_events(
        self,
        start_date: date,
        end_date: date
    ) -> List[BookingCalendarEvent]:
        """
        Get bookings as calendar events for given date range

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            List of calendar events
        """
        from sqlalchemy.orm import selectinload

        stmt = select(Booking).options(
            selectinload(Booking.customer),
            selectinload(Booking.room).selectinload(Room.room_type)
        ).where(
            and_(
                Booking.status != BookingStatusEnum.CANCELLED,
                or_(
                    and_(
                        Booking.check_in_date <= end_date,
                        Booking.check_out_date >= start_date
                    )
                )
            )
        ).order_by(Booking.check_in_date)

        result = await self.db.execute(stmt)
        bookings = result.scalars().all()

        # Convert to calendar events
        events = []
        for booking in bookings:
            # Determine color based on status
            color = self._get_status_color(booking.status)

            event = BookingCalendarEvent(
                id=booking.id,
                title=f"ห้อง {booking.room.room_number} - {booking.customer.full_name}",
                start=booking.check_in_date,
                end=booking.check_out_date,
                color=color,
                status=booking.status.value,
                room_number=booking.room.room_number,
                customer_name=booking.customer.full_name,
                deposit_amount=booking.deposit_amount,
                total_amount=booking.total_amount
            )
            events.append(event)

        return events

    async def get_booking_by_room_and_date(
        self,
        room_id: int,
        check_date: date
    ) -> Optional[Booking]:
        """
        Get active booking for a room on a specific date

        Args:
            room_id: Room ID
            check_date: Date to check

        Returns:
            Booking if exists, None otherwise
        """
        from sqlalchemy.orm import selectinload

        stmt = select(Booking).options(
            selectinload(Booking.customer),
            selectinload(Booking.room).selectinload(Room.room_type)
        ).where(
            and_(
                Booking.room_id == room_id,
                Booking.check_in_date <= check_date,
                Booking.check_out_date > check_date,
                Booking.status.in_([
                    BookingStatusEnum.CONFIRMED,
                    BookingStatusEnum.CHECKED_IN
                ])
            )
        )

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_public_holidays(self, year: int) -> List[PublicHoliday]:
        """
        Fetch Thai public holidays from external API

        Args:
            year: Year to fetch holidays for

        Returns:
            List of public holidays
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"https://date.nager.at/api/v3/PublicHolidays/{year}/TH"
                )
                response.raise_for_status()
                holidays_data = response.json()

                holidays = []
                for h in holidays_data:
                    holiday = PublicHoliday(
                        date=datetime.strptime(h['date'], '%Y-%m-%d').date(),
                        name=h.get('localName', h['name']),
                        name_en=h['name']
                    )
                    holidays.append(holiday)

                return holidays

        except Exception as e:
            print(f"Error fetching public holidays: {str(e)}")
            # Return empty list if API fails
            return []

    # ==================== Helper Methods ====================

    def _get_status_color(self, status: BookingStatusEnum) -> str:
        """Get calendar event color based on booking status"""
        color_map = {
            BookingStatusEnum.PENDING: "#3B82F6",      # Blue
            BookingStatusEnum.CONFIRMED: "#10B981",    # Green
            BookingStatusEnum.CHECKED_IN: "#F59E0B",   # Amber
            BookingStatusEnum.COMPLETED: "#6B7280",    # Gray
            BookingStatusEnum.CANCELLED: "#EF4444"     # Red
        }
        return color_map.get(status, "#6B7280")

    async def _has_other_booking_for_date(
        self,
        room_id: int,
        check_date: date,
        exclude_booking_id: int
    ) -> bool:
        """Check if there are other bookings for a room on a specific date"""
        stmt = select(func.count()).select_from(Booking).where(
            and_(
                Booking.room_id == room_id,
                Booking.id != exclude_booking_id,
                Booking.check_in_date <= check_date,
                Booking.check_out_date > check_date,
                Booking.status.in_([
                    BookingStatusEnum.CONFIRMED,
                    BookingStatusEnum.CHECKED_IN
                ])
            )
        )

        result = await self.db.execute(stmt)
        count = result.scalar()
        return count > 0

    async def _broadcast_room_status_change(
        self,
        room_id: int,
        old_status: RoomStatus,
        new_status: RoomStatus
    ):
        """Broadcast room status change via WebSocket"""
        await websocket_manager.broadcast({
            "event": "room_status_changed",
            "data": {
                "room_id": room_id,
                "old_status": old_status.value if isinstance(old_status, RoomStatus) else old_status,
                "new_status": new_status.value if isinstance(new_status, RoomStatus) else new_status,
                "timestamp": now_thailand().isoformat()
            }
        })
