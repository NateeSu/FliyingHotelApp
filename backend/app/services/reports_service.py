"""
Reports Service (Phase 8)
Business logic for generating reports
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, cast, Date
from sqlalchemy.orm import selectinload
from datetime import date, datetime, timedelta
from typing import Optional
from decimal import Decimal

from app.models.payment import Payment
from app.models.check_in import CheckIn, PaymentMethodEnum, StayTypeEnum, CheckInStatusEnum
from app.models.booking import Booking, BookingStatusEnum
from app.models.customer import Customer
from app.models.room import Room, RoomStatus
from app.schemas.reports import (
    RevenueReportResponse,
    RevenueByPeriod,
    OccupancyReportResponse,
    OccupancyByPeriod,
    RoomStatusDistribution,
    BookingReportResponse,
    BookingByPeriod,
    CustomerReportResponse,
    TopCustomer,
    SummaryReportResponse,
    QuickStat,
    CheckInsListResponse,
    CheckInListItem,
    CheckInStatsResponse,
    DailyCheckInStats
)


class ReportsService:
    """Service for generating various reports"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_revenue_report(
        self,
        start_date: date,
        end_date: date,
        group_by: str = "day"  # "day" or "month"
    ) -> RevenueReportResponse:
        """
        Generate revenue report

        Args:
            start_date: Start date for report
            end_date: End date for report
            group_by: Group data by "day" or "month"

        Returns:
            RevenueReportResponse with revenue breakdown
        """
        # Get all payments in date range
        stmt = select(Payment).join(CheckIn).where(
            and_(
                cast(Payment.payment_time, Date) >= start_date,
                cast(Payment.payment_time, Date) <= end_date
            )
        ).options(selectinload(Payment.check_in))
        result = await self.db.execute(stmt)
        payments = result.scalars().all()

        # Calculate totals
        total_revenue = sum(float(p.amount) for p in payments)
        total_transactions = len(payments)
        average_transaction = total_revenue / total_transactions if total_transactions > 0 else 0

        # By payment method
        by_payment_method = {}
        for payment in payments:
            method = payment.payment_method.value if hasattr(payment.payment_method, 'value') else payment.payment_method
            by_payment_method[method] = by_payment_method.get(method, 0) + float(payment.amount)

        # By stay type (from check-in)
        by_stay_type = {}
        for payment in payments:
            if payment.check_in:
                stay_type = payment.check_in.stay_type.value if hasattr(payment.check_in.stay_type, 'value') else payment.check_in.stay_type
                by_stay_type[stay_type] = by_stay_type.get(stay_type, 0) + float(payment.amount)

        # By period (for chart)
        by_period_dict = {}
        for payment in payments:
            if group_by == "day":
                period_key = payment.payment_time.strftime("%Y-%m-%d")
            else:  # month
                period_key = payment.payment_time.strftime("%Y-%m")

            if period_key not in by_period_dict:
                by_period_dict[period_key] = {"revenue": 0, "count": 0}

            by_period_dict[period_key]["revenue"] += float(payment.amount)
            by_period_dict[period_key]["count"] += 1

        by_period = [
            RevenueByPeriod(
                period=period,
                revenue=data["revenue"],
                count=data["count"]
            )
            for period, data in sorted(by_period_dict.items())
        ]

        return RevenueReportResponse(
            total_revenue=total_revenue,
            total_transactions=total_transactions,
            average_transaction=average_transaction,
            by_payment_method=by_payment_method,
            by_stay_type=by_stay_type,
            by_period=by_period,
            start_date=start_date,
            end_date=end_date
        )

    async def get_occupancy_report(
        self,
        start_date: date,
        end_date: date
    ) -> OccupancyReportResponse:
        """
        Generate occupancy report

        Args:
            start_date: Start date for report
            end_date: End date for report

        Returns:
            OccupancyReportResponse with occupancy statistics
        """
        # Get total rooms
        stmt = select(func.count(Room.id)).where(Room.status != RoomStatus.OUT_OF_SERVICE)
        result = await self.db.execute(stmt)
        total_rooms = result.scalar() or 0

        # Get current room status distribution
        stmt = select(Room.status, func.count(Room.id)).group_by(Room.status)
        result = await self.db.execute(stmt)
        status_counts = dict(result.all())

        room_status_distribution = RoomStatusDistribution(
            available=status_counts.get(RoomStatus.AVAILABLE, 0),
            occupied=status_counts.get(RoomStatus.OCCUPIED, 0),
            cleaning=status_counts.get(RoomStatus.CLEANING, 0),
            reserved=status_counts.get(RoomStatus.RESERVED, 0),
            out_of_service=status_counts.get(RoomStatus.OUT_OF_SERVICE, 0)
        )

        # Current occupancy
        occupied_rooms = status_counts.get(RoomStatus.OCCUPIED, 0)
        available_rooms = status_counts.get(RoomStatus.AVAILABLE, 0)
        occupancy_rate = (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0

        # By period (daily occupancy for chart)
        by_period = []
        current_date = start_date
        while current_date <= end_date:
            # Count occupied rooms on this date
            # (rooms with check-in on or before this date, and check-out after this date)
            stmt = select(func.count(CheckIn.id)).where(
                and_(
                    cast(CheckIn.check_in_time, Date) <= current_date,
                    or_(
                        CheckIn.status == CheckInStatusEnum.CHECKED_IN,
                        and_(
                            CheckIn.status == CheckInStatusEnum.CHECKED_OUT,
                            cast(CheckIn.actual_check_out_time, Date) >= current_date
                        )
                    )
                )
            )
            result = await self.db.execute(stmt)
            occupied_on_date = result.scalar() or 0

            period_occupancy = (occupied_on_date / total_rooms * 100) if total_rooms > 0 else 0

            by_period.append(OccupancyByPeriod(
                period=current_date.strftime("%Y-%m-%d"),
                occupancy_rate=round(period_occupancy, 2),
                occupied_rooms=occupied_on_date,
                total_rooms=total_rooms
            ))

            current_date += timedelta(days=1)

        return OccupancyReportResponse(
            occupancy_rate=round(occupancy_rate, 2),
            total_rooms=total_rooms,
            occupied_rooms=occupied_rooms,
            available_rooms=available_rooms,
            room_status_distribution=room_status_distribution,
            by_period=by_period,
            start_date=start_date,
            end_date=end_date
        )

    async def get_booking_report(
        self,
        start_date: date,
        end_date: date
    ) -> BookingReportResponse:
        """
        Generate booking report

        Args:
            start_date: Start date for report
            end_date: End date for report

        Returns:
            BookingReportResponse with booking statistics
        """
        # Get all bookings in date range
        stmt = select(Booking).where(
            and_(
                Booking.check_in_date >= start_date,
                Booking.check_in_date <= end_date
            )
        )
        result = await self.db.execute(stmt)
        bookings = result.scalars().all()

        total_bookings = len(bookings)
        confirmed_bookings = sum(1 for b in bookings if b.status == BookingStatusEnum.CONFIRMED)
        cancelled_bookings = sum(1 for b in bookings if b.status == BookingStatusEnum.CANCELLED)
        checked_in_bookings = sum(1 for b in bookings if b.status == BookingStatusEnum.CHECKED_IN)

        cancellation_rate = (cancelled_bookings / total_bookings * 100) if total_bookings > 0 else 0
        conversion_rate = (checked_in_bookings / confirmed_bookings * 100) if confirmed_bookings > 0 else 0

        total_deposit = sum(float(b.deposit_amount) for b in bookings if b.deposit_amount)

        # By period (monthly)
        by_period_dict = {}
        for booking in bookings:
            period_key = booking.check_in_date.strftime("%Y-%m")

            if period_key not in by_period_dict:
                by_period_dict[period_key] = {
                    "total": 0,
                    "confirmed": 0,
                    "cancelled": 0,
                    "checked_in": 0
                }

            by_period_dict[period_key]["total"] += 1
            if booking.status == BookingStatusEnum.CONFIRMED:
                by_period_dict[period_key]["confirmed"] += 1
            elif booking.status == BookingStatusEnum.CANCELLED:
                by_period_dict[period_key]["cancelled"] += 1
            elif booking.status == BookingStatusEnum.CHECKED_IN:
                by_period_dict[period_key]["checked_in"] += 1

        by_period = [
            BookingByPeriod(
                period=period,
                total_bookings=data["total"],
                confirmed=data["confirmed"],
                cancelled=data["cancelled"],
                checked_in=data["checked_in"]
            )
            for period, data in sorted(by_period_dict.items())
        ]

        return BookingReportResponse(
            total_bookings=total_bookings,
            confirmed_bookings=confirmed_bookings,
            cancelled_bookings=cancelled_bookings,
            checked_in_bookings=checked_in_bookings,
            cancellation_rate=round(cancellation_rate, 2),
            conversion_rate=round(conversion_rate, 2),
            total_deposit=total_deposit,
            by_period=by_period,
            start_date=start_date,
            end_date=end_date
        )

    async def get_customer_report(
        self,
        limit: int = 10
    ) -> CustomerReportResponse:
        """
        Generate customer report (top customers)

        Args:
            limit: Number of top customers to return

        Returns:
            CustomerReportResponse with customer statistics
        """
        # Get all customers with their spending
        stmt = select(
            Customer,
            func.count(CheckIn.id).label('visit_count'),
            func.sum(Payment.amount).label('total_spending'),
            func.max(CheckIn.check_in_time).label('last_visit')
        ).outerjoin(
            CheckIn, CheckIn.customer_id == Customer.id
        ).outerjoin(
            Payment, Payment.check_in_id == CheckIn.id
        ).group_by(
            Customer.id
        ).order_by(
            func.sum(Payment.amount).desc()
        ).limit(limit)

        result = await self.db.execute(stmt)
        rows = result.all()

        top_customers = []
        for row in rows:
            customer = row[0]
            visit_count = row[1] or 0
            total_spending = float(row[2]) if row[2] else 0.0
            last_visit = row[3]

            top_customers.append(TopCustomer(
                customer_id=customer.id,
                full_name=customer.full_name,
                phone_number=customer.phone_number,
                total_spending=total_spending,
                visit_count=visit_count,
                last_visit=last_visit
            ))

        # Total customers
        stmt = select(func.count(Customer.id))
        result = await self.db.execute(stmt)
        total_customers = result.scalar() or 0

        # New customers (first visit in last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        stmt = select(func.count(Customer.id)).where(
            Customer.created_at >= thirty_days_ago
        )
        result = await self.db.execute(stmt)
        new_customers = result.scalar() or 0

        # Returning customers (> 1 visit)
        stmt = select(func.count(func.distinct(CheckIn.customer_id))).where(
            CheckIn.customer_id.in_(
                select(CheckIn.customer_id).group_by(CheckIn.customer_id).having(func.count(CheckIn.id) > 1)
            )
        )
        result = await self.db.execute(stmt)
        returning_customers = result.scalar() or 0

        return CustomerReportResponse(
            top_customers=top_customers,
            total_customers=total_customers,
            new_customers=new_customers,
            returning_customers=returning_customers
        )

    async def get_summary_report(
        self,
        start_date: date,
        end_date: date
    ) -> SummaryReportResponse:
        """
        Generate summary report for dashboard

        Args:
            start_date: Start date for report
            end_date: End date for report

        Returns:
            SummaryReportResponse with all key metrics
        """
        # Revenue
        revenue_report = await self.get_revenue_report(start_date, end_date, "day")
        total_revenue = revenue_report.total_revenue

        # Occupancy
        occupancy_report = await self.get_occupancy_report(start_date, end_date)
        occupancy_rate = occupancy_report.occupancy_rate

        # Check-ins/outs
        stmt = select(func.count(CheckIn.id)).where(
            and_(
                cast(CheckIn.check_in_time, Date) >= start_date,
                cast(CheckIn.check_in_time, Date) <= end_date
            )
        )
        result = await self.db.execute(stmt)
        total_checkins = result.scalar() or 0

        stmt = select(func.count(CheckIn.id)).where(
            and_(
                CheckIn.status == CheckInStatusEnum.CHECKED_OUT,
                cast(CheckIn.actual_check_out_time, Date) >= start_date,
                cast(CheckIn.actual_check_out_time, Date) <= end_date
            )
        )
        result = await self.db.execute(stmt)
        total_checkouts = result.scalar() or 0

        # Bookings
        booking_report = await self.get_booking_report(start_date, end_date)
        total_bookings = booking_report.total_bookings

        # Customers
        customer_report = await self.get_customer_report(limit=10)
        total_customers = customer_report.total_customers
        new_customers = customer_report.new_customers

        # Quick stats
        quick_stats = [
            QuickStat(
                label="รายได้รวม",
                value=f"฿{total_revenue:,.2f}",
                trend="up" if total_revenue > 0 else "neutral"
            ),
            QuickStat(
                label="อัตราเข้าพัก",
                value=f"{occupancy_rate:.1f}%",
                trend="up" if occupancy_rate > 50 else "down"
            ),
            QuickStat(
                label="จำนวนเช็คอิน",
                value=str(total_checkins),
                trend="neutral"
            ),
            QuickStat(
                label="การจองทั้งหมด",
                value=str(total_bookings),
                trend="neutral"
            )
        ]

        return SummaryReportResponse(
            total_revenue=total_revenue,
            occupancy_rate=occupancy_rate,
            total_checkins=total_checkins,
            total_checkouts=total_checkouts,
            total_bookings=total_bookings,
            total_customers=total_customers,
            new_customers=new_customers,
            quick_stats=quick_stats,
            start_date=start_date,
            end_date=end_date
        )

    async def get_checkins_list(
        self,
        start_date: date,
        end_date: date
    ) -> CheckInsListResponse:
        """
        Get list of all check-ins within date range for reports table

        For "last night" reports (yesterday to today):
        - Filters check-ins from 12:00 (noon) of start_date to 12:00 (noon) of end_date

        For other reports:
        - Filters check-ins within the full day range

        Args:
            start_date: Start date for report
            end_date: End date for report

        Returns:
            CheckInsListResponse with list of check-ins and summary
        """
        from app.models.room_type import RoomType
        from app.core.datetime_utils import now_thailand

        # Check if this is a "last night" query (1 day difference)
        is_last_night = (end_date - start_date).days == 1

        if is_last_night:
            # Last night: from 12:00 of start_date to 12:00 of end_date
            start_datetime = datetime.combine(start_date, datetime.min.time()).replace(hour=12, minute=0, second=0)
            end_datetime = datetime.combine(end_date, datetime.min.time()).replace(hour=12, minute=0, second=0)

            stmt = (
                select(CheckIn)
                .options(
                    selectinload(CheckIn.customer),
                    selectinload(CheckIn.room).selectinload(Room.room_type)
                )
                .where(
                    and_(
                        CheckIn.check_in_time >= start_datetime,
                        CheckIn.check_in_time < end_datetime
                    )
                )
                .order_by(CheckIn.check_in_time.desc())
            )
        else:
            # Other periods: full day range
            stmt = (
                select(CheckIn)
                .options(
                    selectinload(CheckIn.customer),
                    selectinload(CheckIn.room).selectinload(Room.room_type)
                )
                .where(
                    and_(
                        cast(CheckIn.check_in_time, Date) >= start_date,
                        cast(CheckIn.check_in_time, Date) <= end_date
                    )
                )
                .order_by(CheckIn.check_in_time.desc())
            )

        result = await self.db.execute(stmt)
        check_ins = result.unique().scalars().all()

        # Build check-in list items
        check_in_items = []
        total_revenue = Decimal("0.00")

        for check_in in check_ins:
            # Calculate total amount
            total_amount = Decimal(str(check_in.total_amount or 0))
            total_revenue += total_amount

            check_in_items.append(
                CheckInListItem(
                    id=check_in.id,
                    room_number=check_in.room.room_number,
                    room_type_name=check_in.room.room_type.name,
                    customer_name=check_in.customer.full_name,
                    customer_phone=check_in.customer.phone_number,
                    stay_type=check_in.stay_type.value,
                    check_in_time=check_in.check_in_time,
                    expected_check_out_time=check_in.expected_check_out_time,
                    check_out_time=check_in.actual_check_out_time,
                    total_amount=total_amount,
                    payment_method=check_in.payment_method.value,
                    status=check_in.status.value,
                    number_of_nights=check_in.number_of_nights,
                    number_of_guests=check_in.number_of_guests
                )
            )

        return CheckInsListResponse(
            check_ins=check_in_items,
            total_count=len(check_in_items),
            total_revenue=total_revenue,
            start_date=start_date,
            end_date=end_date
        )

    async def get_checkin_stats(
        self,
        start_date: date,
        end_date: date
    ) -> CheckInStatsResponse:
        """
        Get daily check-in statistics by stay type

        Args:
            start_date: Start date for report
            end_date: End date for report

        Returns:
            CheckInStatsResponse with daily stats
        """
        # Query check-ins grouped by date and stay type
        stmt = (
            select(
                cast(CheckIn.check_in_time, Date).label("date"),
                CheckIn.stay_type,
                func.count(CheckIn.id).label("count")
            )
            .where(
                and_(
                    cast(CheckIn.check_in_time, Date) >= start_date,
                    cast(CheckIn.check_in_time, Date) <= end_date
                )
            )
            .group_by(cast(CheckIn.check_in_time, Date), CheckIn.stay_type)
            .order_by(cast(CheckIn.check_in_time, Date))
        )

        result = await self.db.execute(stmt)
        rows = result.all()

        # Process results into daily stats
        daily_stats_dict = {}
        total_overnight = 0
        total_temporary = 0

        for row in rows:
            day = row[0]
            stay_type = row[1]
            count = row[2]

            day_str = day.isoformat()

            if day_str not in daily_stats_dict:
                daily_stats_dict[day_str] = {
                    "overnight": 0,
                    "temporary": 0
                }

            if stay_type == StayTypeEnum.OVERNIGHT:
                daily_stats_dict[day_str]["overnight"] = count
                total_overnight += count
            elif stay_type == StayTypeEnum.TEMPORARY:
                daily_stats_dict[day_str]["temporary"] = count
                total_temporary += count

        # Build daily stats list
        daily_stats = []
        current_date = start_date
        while current_date <= end_date:
            day_str = current_date.isoformat()
            if day_str in daily_stats_dict:
                stats = daily_stats_dict[day_str]
                daily_stats.append(
                    DailyCheckInStats(
                        date=day_str,
                        overnight=stats["overnight"],
                        temporary=stats["temporary"],
                        total=stats["overnight"] + stats["temporary"]
                    )
                )
            else:
                # Add empty stats for days with no check-ins
                daily_stats.append(
                    DailyCheckInStats(
                        date=day_str,
                        overnight=0,
                        temporary=0,
                        total=0
                    )
                )
            current_date += timedelta(days=1)

        total_checkins = total_overnight + total_temporary

        return CheckInStatsResponse(
            daily_stats=daily_stats,
            total_overnight=total_overnight,
            total_temporary=total_temporary,
            total_checkins=total_checkins,
            start_date=start_date,
            end_date=end_date
        )
