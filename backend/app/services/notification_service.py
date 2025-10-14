"""
Notification Service (Phase 3)
Business logic for notification operations
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import joinedload
from typing import List, Optional
from datetime import datetime

from app.models import Notification, User, Room
from app.models.notification import NotificationTypeEnum, TargetRoleEnum
from app.schemas.notification import NotificationCreate, NotificationResponse, NotificationMarkAllReadResponse
from app.core.websocket import manager as websocket_manager
from app.core.datetime_utils import now_thailand
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for notification operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_notification(
        self,
        notification_data: NotificationCreate,
        broadcast_websocket: bool = True
    ) -> Notification:
        """
        Create a new notification

        Args:
            notification_data: Notification creation data
            broadcast_websocket: Whether to broadcast via WebSocket

        Returns:
            Created notification
        """
        notification = Notification(
            notification_type=notification_data.notification_type,
            target_role=notification_data.target_role,
            title=notification_data.title,
            message=notification_data.message,
            room_id=notification_data.room_id,
            related_booking_id=notification_data.related_booking_id,
            related_check_in_id=notification_data.related_check_in_id
        )

        self.db.add(notification)
        await self.db.commit()
        await self.db.refresh(notification)

        logger.info(f"Created notification: {notification.id} - {notification.title}")

        # Broadcast via WebSocket
        if broadcast_websocket:
            await websocket_manager.broadcast_notification(
                notification_type=notification.notification_type.value,
                target_role=notification.target_role.value,
                title=notification.title,
                message_text=notification.message,
                room_id=notification.room_id
            )

        return notification

    async def get_notifications_by_role(
        self,
        target_role: TargetRoleEnum,
        limit: int = 50,
        offset: int = 0,
        unread_only: bool = False
    ) -> tuple[List[Notification], int]:
        """
        Get notifications for a specific role

        Args:
            target_role: Target role for notifications
            limit: Maximum number of notifications to return
            offset: Number of notifications to skip
            unread_only: If True, return only unread notifications

        Returns:
            Tuple of (notifications list, total count)
        """
        # Build query
        conditions = [Notification.target_role == target_role]
        if unread_only:
            conditions.append(Notification.is_read == False)

        stmt = (
            select(Notification)
            .options(joinedload(Notification.room))
            .where(and_(*conditions))
            .order_by(Notification.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        result = await self.db.execute(stmt)
        notifications = result.unique().scalars().all()

        # Count total
        count_stmt = select(func.count(Notification.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar() or 0

        return list(notifications), total

    async def get_unread_count_by_role(self, target_role: TargetRoleEnum) -> int:
        """
        Get count of unread notifications for a role

        Args:
            target_role: Target role

        Returns:
            Count of unread notifications
        """
        stmt = select(func.count(Notification.id)).where(
            and_(
                Notification.target_role == target_role,
                Notification.is_read == False
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar() or 0

    async def mark_as_read(self, notification_id: int) -> Optional[Notification]:
        """
        Mark a notification as read

        Args:
            notification_id: Notification ID

        Returns:
            Updated notification or None if not found
        """
        stmt = select(Notification).where(Notification.id == notification_id)
        result = await self.db.execute(stmt)
        notification = result.scalar_one_or_none()

        if not notification:
            return None

        if not notification.is_read:
            notification.is_read = True
            notification.read_at = now_thailand()
            await self.db.commit()
            await self.db.refresh(notification)
            logger.info(f"Marked notification {notification_id} as read")

        return notification

    async def mark_all_as_read(self, target_role: TargetRoleEnum) -> int:
        """
        Mark all notifications for a role as read

        Args:
            target_role: Target role

        Returns:
            Number of notifications marked as read
        """
        stmt = select(Notification).where(
            and_(
                Notification.target_role == target_role,
                Notification.is_read == False
            )
        )
        result = await self.db.execute(stmt)
        notifications = result.scalars().all()

        count = 0
        now = now_thailand()
        for notification in notifications:
            notification.is_read = True
            notification.read_at = now
            count += 1

        if count > 0:
            await self.db.commit()
            logger.info(f"Marked {count} notifications as read for role {target_role.value}")

        return count

    async def create_overtime_notification(
        self,
        room_id: int,
        room_number: str,
        customer_name: str,
        stay_type: str,
        overtime_minutes: int
    ) -> Notification:
        """
        Create overtime alert notification

        Args:
            room_id: Room ID
            room_number: Room number
            customer_name: Customer name
            stay_type: Stay type (overnight/temporary)
            overtime_minutes: Minutes overtime

        Returns:
            Created notification
        """
        stay_type_thai = "ค้างคืน" if stay_type == "overnight" else "ชั่วคราว"
        title = f"เกินเวลา: ห้อง {room_number}"
        message = f"ผู้เข้าพัก {customer_name} ({stay_type_thai}) เกินเวลา {overtime_minutes} นาที"

        notification_data = NotificationCreate(
            notification_type=NotificationTypeEnum.OVERTIME_ALERT,
            target_role=TargetRoleEnum.RECEPTION,
            title=title,
            message=message,
            room_id=room_id
        )

        return await self.create_notification(notification_data)

    async def create_room_status_notification(
        self,
        room_id: int,
        room_number: str,
        old_status: str,
        new_status: str,
        target_role: TargetRoleEnum
    ) -> Notification:
        """
        Create room status change notification

        Args:
            room_id: Room ID
            room_number: Room number
            old_status: Old status
            new_status: New status
            target_role: Target role

        Returns:
            Created notification
        """
        status_thai_map = {
            "available": "ว่าง",
            "occupied": "มีผู้เข้าพัก",
            "cleaning": "กำลังทำความสะอาด",
            "reserved": "จอง",
            "out_of_service": "ไม่พร้อมใช้งาน"
        }

        old_status_thai = status_thai_map.get(old_status, old_status)
        new_status_thai = status_thai_map.get(new_status, new_status)

        title = f"เปลี่ยนสถานะ: ห้อง {room_number}"
        message = f"สถานะห้องเปลี่ยนจาก {old_status_thai} เป็น {new_status_thai}"

        notification_data = NotificationCreate(
            notification_type=NotificationTypeEnum.ROOM_STATUS_CHANGE,
            target_role=target_role,
            title=title,
            message=message,
            room_id=room_id
        )

        return await self.create_notification(notification_data)

    async def create_booking_reminder_notification(
        self,
        booking_id: int,
        room_number: str,
        customer_name: str,
        check_in_date: datetime
    ) -> Notification:
        """
        Create booking reminder notification

        Args:
            booking_id: Booking ID
            room_number: Room number
            customer_name: Customer name
            check_in_date: Check-in date

        Returns:
            Created notification
        """
        title = f"เตือนการจอง: ห้อง {room_number}"
        message = f"ผู้เข้าพัก {customer_name} มีการจองวันที่ {check_in_date.strftime('%d/%m/%Y %H:%M')}"

        notification_data = NotificationCreate(
            notification_type=NotificationTypeEnum.BOOKING_REMINDER,
            target_role=TargetRoleEnum.RECEPTION,
            title=title,
            message=message,
            related_booking_id=booking_id
        )

        return await self.create_notification(notification_data)

    async def get_notification_by_id(self, notification_id: int) -> Optional[Notification]:
        """
        Get notification by ID

        Args:
            notification_id: Notification ID

        Returns:
            Notification or None if not found
        """
        stmt = (
            select(Notification)
            .options(joinedload(Notification.room))
            .where(Notification.id == notification_id)
        )
        result = await self.db.execute(stmt)
        return result.unique().scalar_one_or_none()
