"""
Check-Out Service (Phase 4)
Handles check-out business logic with overtime calculation and payment processing
"""
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.models import CheckIn, Room, Payment, RoomStatus
from app.models.check_in import CheckInStatusEnum
from app.models.notification import NotificationTypeEnum, TargetRoleEnum
from app.schemas.check_in import CheckOutRequest, CheckOutSummary
from app.schemas.notification import NotificationCreate
from app.core.websocket import manager as websocket_manager
from app.services.notification_service import NotificationService


class CheckOutService:
    """Service for managing check-outs"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.notification_service = NotificationService(db)

    async def get_checkout_summary(self, check_in_id: int) -> CheckOutSummary:
        """
        Get checkout summary with overtime calculation

        Returns summary of:
        - Check-in details
        - Base amount
        - Overtime status and charges
        - Extra charges
        - Discount
        - Total amount due
        """
        check_in = await self._get_check_in_with_details(check_in_id)

        if not check_in:
            raise ValueError(f"ไม่พบข้อมูลการเช็คอินหมายเลข {check_in_id}")

        if check_in.status != CheckInStatusEnum.CHECKED_IN:
            raise ValueError("การเช็คอินนี้ได้เช็คเอาท์แล้ว")

        # Calculate overtime
        now = datetime.utcnow()
        is_overtime = now > check_in.expected_check_out_time
        overtime_minutes = 0
        overtime_charge = Decimal(0)

        if is_overtime:
            overtime_delta = now - check_in.expected_check_out_time
            overtime_minutes = int(overtime_delta.total_seconds() / 60)
            overtime_charge = self._calculate_overtime_charge(
                check_in,
                overtime_minutes
            )

        # Calculate total
        total_amount = check_in.base_amount + overtime_charge

        return CheckOutSummary(
            check_in_id=check_in.id,
            room_number=check_in.room.room_number,
            customer_name=check_in.customer.full_name,
            stay_type=check_in.stay_type,
            check_in_time=check_in.check_in_time,
            expected_check_out_time=check_in.expected_check_out_time,
            actual_check_out_time=now,
            base_amount=check_in.base_amount,
            is_overtime=is_overtime,
            overtime_minutes=overtime_minutes if is_overtime else None,
            overtime_charge=overtime_charge,
            extra_charges=Decimal(0),
            discount_amount=Decimal(0),
            total_amount=total_amount
        )

    async def process_check_out(
        self,
        check_in_id: int,
        checkout_data: CheckOutRequest,
        processed_by_user_id: int
    ) -> CheckIn:
        """
        Process check-out with payment recording

        Steps:
        1. Validate check-in exists and is active
        2. Calculate overtime charges
        3. Apply extra charges and discounts
        4. Calculate final total
        5. Record payment
        6. Update check-in status to 'checked_out'
        7. Update room status to 'cleaning'
        8. Create housekeeping task (future phase)
        9. Broadcast WebSocket event
        10. Send Telegram notification (future phase)
        """
        check_in = await self._get_check_in_with_details(check_in_id)

        if not check_in:
            raise ValueError(f"ไม่พบข้อมูลการเช็คอินหมายเลข {check_in_id}")

        if check_in.status != CheckInStatusEnum.CHECKED_IN:
            raise ValueError("การเช็คอินนี้ได้เช็คเอาท์แล้ว")

        # Calculate actual checkout time
        actual_checkout_time = checkout_data.actual_check_out_time or datetime.utcnow()

        # Calculate overtime
        is_overtime = actual_checkout_time > check_in.expected_check_out_time
        overtime_minutes = 0
        overtime_charge = Decimal(0)

        if is_overtime:
            overtime_delta = actual_checkout_time - check_in.expected_check_out_time
            overtime_minutes = int(overtime_delta.total_seconds() / 60)
            overtime_charge = self._calculate_overtime_charge(
                check_in,
                overtime_minutes
            )

        # Calculate total
        extra_charges = checkout_data.extra_charges or Decimal(0)
        discount_amount = checkout_data.discount_amount or Decimal(0)

        total_amount = (
            check_in.base_amount +
            overtime_charge +
            extra_charges -
            discount_amount
        )

        if total_amount < 0:
            total_amount = Decimal(0)

        # Update check-in record
        check_in.actual_check_out_time = actual_checkout_time
        check_in.is_overtime = is_overtime
        check_in.overtime_minutes = overtime_minutes if is_overtime else None
        check_in.overtime_charge = overtime_charge
        check_in.extra_charges = extra_charges
        check_in.discount_amount = discount_amount
        check_in.discount_reason = checkout_data.discount_reason
        check_in.total_amount = total_amount
        check_in.status = CheckInStatusEnum.CHECKED_OUT
        check_in.checked_out_by = processed_by_user_id  # Set who processed the checkout

        # Create payment record
        payment = Payment(
            check_in_id=check_in.id,
            amount=total_amount,
            payment_method=checkout_data.payment_method,
            payment_time=actual_checkout_time,
            notes=checkout_data.payment_notes,
            created_by=processed_by_user_id
        )
        self.db.add(payment)

        # Update room status to cleaning
        room = check_in.room
        old_status = room.status
        room.status = RoomStatus.CLEANING

        # Create notification record for housekeeping (before commit)
        # Note: We'll broadcast via WebSocket after commit
        from app.models import Notification
        notification = Notification(
            notification_type=NotificationTypeEnum.CHECK_OUT,  # Fixed: Use CHECK_OUT instead of HOUSEKEEPING
            target_role=TargetRoleEnum.HOUSEKEEPING,
            title=f"ห้อง {room.room_number} ต้องการทำความสะอาด",
            message=f"แขกเช็คเอาท์แล้ว กรุณาทำความสะอาดห้อง {room.room_number}",
            room_id=room.id
        )
        self.db.add(notification)

        # Commit transaction (includes check-in, payment, room status, and notification)
        await self.db.commit()
        await self.db.refresh(check_in)

        # Broadcast WebSocket events (after commit)
        await self._broadcast_check_out_event(check_in, room)
        await websocket_manager.broadcast_room_status_change(
            room_id=room.id,
            old_status=old_status.value if isinstance(old_status, RoomStatus) else old_status,
            new_status="cleaning"
        )

        # Broadcast notification via WebSocket
        await websocket_manager.broadcast_notification(
            notification_type=NotificationTypeEnum.CHECK_OUT.value,  # Fixed: Use CHECK_OUT
            target_role=TargetRoleEnum.HOUSEKEEPING.value,
            title=notification.title,
            message_text=notification.message,
            room_id=notification.room_id
        )

        return check_in

    def _calculate_overtime_charge(
        self,
        check_in: CheckIn,
        overtime_minutes: int
    ) -> Decimal:
        """
        Calculate overtime charge

        Business Rules:
        - Overnight: 10% of base amount per hour (or fraction thereof)
        - Temporary: Full session rate per hour exceeded
        - Minimum charge: 1 hour
        """
        if overtime_minutes <= 0:
            return Decimal(0)

        # Round up to hours
        overtime_hours = (overtime_minutes + 59) // 60  # Ceiling division

        if check_in.stay_type == "overnight":
            # 10% of base amount per hour
            hourly_rate = check_in.base_amount * Decimal("0.10")
            return hourly_rate * overtime_hours
        else:
            # For temporary: charge full session rate per hour
            hourly_rate = check_in.base_amount
            return hourly_rate * overtime_hours

    async def _get_check_in_with_details(self, check_in_id: int) -> Optional[CheckIn]:
        """Get check-in with all related data"""
        stmt = select(CheckIn).where(CheckIn.id == check_in_id).options(
            joinedload(CheckIn.room).joinedload(Room.room_type),
            joinedload(CheckIn.customer),
            joinedload(CheckIn.booking)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def _broadcast_check_out_event(self, check_in: CheckIn, room: Room):
        """Broadcast check-out event via WebSocket"""
        await websocket_manager.broadcast({
            "event": "check_out_completed",
            "data": {
                "check_in_id": check_in.id,
                "room_id": room.id,
                "room_number": room.room_number,
                "customer_name": check_in.customer.full_name if check_in.customer else None,
                "check_out_time": check_in.actual_check_out_time.isoformat() if check_in.actual_check_out_time else None,
                "is_overtime": check_in.is_overtime,
                "total_amount": float(check_in.total_amount),
                "timestamp": datetime.utcnow().isoformat()
            }
        })
