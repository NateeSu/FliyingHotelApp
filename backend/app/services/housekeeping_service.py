"""
Housekeeping Service (Phase 5)
Handles housekeeping task business logic
"""
from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, or_
from sqlalchemy.orm import joinedload

from app.models import HousekeepingTask, Room, User, CheckIn
from app.models.housekeeping_task import (
    HousekeepingTaskStatusEnum,
    HousekeepingTaskPriorityEnum
)
from app.models.room import RoomStatus
from app.schemas.housekeeping import (
    HousekeepingTaskCreate,
    HousekeepingTaskUpdate,
    HousekeepingStats
)
from app.core.websocket import manager as websocket_manager
from app.core.datetime_utils import now_thailand


class HousekeepingService:
    """Service for managing housekeeping tasks"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_task(
        self,
        task_data: HousekeepingTaskCreate,
        created_by_user_id: int
    ) -> HousekeepingTask:
        """
        Create a new housekeeping task

        Business Logic:
        1. Validate room exists
        2. Create housekeeping task
        3. Update room status to 'cleaning' (if not already)
        4. Broadcast WebSocket event
        5. TODO: Send Telegram notification to housekeeping staff
        """
        # Validate room exists
        room = await self._get_room(task_data.room_id)
        if not room:
            raise ValueError(f"ไม่พบห้องหมายเลข {task_data.room_id}")

        # Validate assigned user exists (if provided)
        if task_data.assigned_to:
            assigned_user = await self._get_user(task_data.assigned_to)
            if not assigned_user:
                raise ValueError(f"ไม่พบผู้ใช้ ID {task_data.assigned_to}")
            if assigned_user.role not in ["housekeeping", "admin"]:
                raise ValueError(
                    f"ไม่สามารถมอบหมายงานให้ผู้ใช้ที่ไม่ใช่แผนกแม่บ้านได้ "
                    f"(บทบาทปัจจุบัน: {assigned_user.role})"
                )

        # Create task
        task = HousekeepingTask(
            room_id=task_data.room_id,
            check_in_id=task_data.check_in_id,
            title=task_data.title,
            description=task_data.description,
            priority=task_data.priority,
            assigned_to=task_data.assigned_to,
            notes=task_data.notes,
            status=HousekeepingTaskStatusEnum.PENDING,
            created_by=created_by_user_id
        )

        self.db.add(task)

        # Update room status to cleaning (if not already) using RoomService (triggers breaker automation)
        if room.status != RoomStatus.CLEANING:
            from app.services.room_service import RoomService
            room_service = RoomService(self.db)
            await room_service.update_status(room.id, RoomStatus.CLEANING)
            # Refresh room to get updated status
            await self.db.refresh(room)

        await self.db.commit()
        await self.db.refresh(task)

        # Load relationships for response
        await self.db.refresh(task, ['room', 'assigned_user', 'creator'])

        # Broadcast task creation event
        await self._broadcast_task_event("housekeeping_task_created", task)

        # Send Telegram notification
        try:
            from app.services.telegram_service import TelegramService
            telegram_service = TelegramService(self.db)
            await telegram_service.send_housekeeping_notification(
                task_id=task.id,
                room_number=room.room_number,
                room_type=room.room_type.name if room.room_type else "ไม่ระบุ"
            )
        except Exception as e:
            print(f"Failed to send Telegram notification: {e}")
            # Don't fail the task creation if notification fails

        return task

    async def get_task_by_id(
        self,
        task_id: int,
        include_relations: bool = True
    ) -> Optional[HousekeepingTask]:
        """Get task by ID with optional relationship loading"""
        stmt = select(HousekeepingTask).where(HousekeepingTask.id == task_id)

        if include_relations:
            stmt = stmt.options(
                joinedload(HousekeepingTask.room).joinedload(Room.room_type),
                joinedload(HousekeepingTask.assigned_user),
                joinedload(HousekeepingTask.creator),
                joinedload(HousekeepingTask.completer),
                joinedload(HousekeepingTask.check_in)
            )

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_tasks(
        self,
        status: Optional[HousekeepingTaskStatusEnum] = None,
        priority: Optional[HousekeepingTaskPriorityEnum] = None,
        assigned_to: Optional[int] = None,
        room_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[HousekeepingTask], int]:
        """
        Get list of housekeeping tasks with filters
        Returns (tasks, total_count)
        """
        # Build filters
        filters = []
        if status:
            filters.append(HousekeepingTask.status == status)
        if priority:
            filters.append(HousekeepingTask.priority == priority)
        if assigned_to:
            filters.append(HousekeepingTask.assigned_to == assigned_to)
        if room_id:
            filters.append(HousekeepingTask.room_id == room_id)

        # Count query
        count_stmt = select(func.count(HousekeepingTask.id))
        if filters:
            count_stmt = count_stmt.where(and_(*filters))

        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar_one()

        # Data query with relationships
        stmt = select(HousekeepingTask)
        if filters:
            stmt = stmt.where(and_(*filters))

        stmt = stmt.options(
            joinedload(HousekeepingTask.room).joinedload(Room.room_type),
            joinedload(HousekeepingTask.assigned_user),
            joinedload(HousekeepingTask.creator),
            joinedload(HousekeepingTask.completer)
        ).order_by(
            HousekeepingTask.priority.desc(),
            HousekeepingTask.created_at.desc()
        ).offset(skip).limit(limit)

        result = await self.db.execute(stmt)
        tasks = result.scalars().unique().all()

        return list(tasks), total

    async def update_task(
        self,
        task_id: int,
        update_data: HousekeepingTaskUpdate
    ) -> HousekeepingTask:
        """Update housekeeping task"""
        task = await self.get_task_by_id(task_id, include_relations=True)
        if not task:
            raise ValueError(f"ไม่พบงาน ID {task_id}")

        # Validate assigned user if provided
        if update_data.assigned_to is not None:
            assigned_user = await self._get_user(update_data.assigned_to)
            if not assigned_user:
                raise ValueError(f"ไม่พบผู้ใช้ ID {update_data.assigned_to}")
            if assigned_user.role not in ["housekeeping", "admin"]:
                raise ValueError("ไม่สามารถมอบหมายงานให้ผู้ใช้ที่ไม่ใช่แผนกแม่บ้านได้")

        # Update fields
        if update_data.status is not None:
            task.status = update_data.status
        if update_data.priority is not None:
            task.priority = update_data.priority
        if update_data.assigned_to is not None:
            task.assigned_to = update_data.assigned_to
        if update_data.notes is not None:
            task.notes = update_data.notes

        await self.db.commit()
        await self.db.refresh(task)

        # Broadcast update event
        await self._broadcast_task_event("housekeeping_task_updated", task)

        return task

    async def start_task(
        self,
        task_id: int,
        user_id: int,
        started_at: Optional[datetime] = None
    ) -> HousekeepingTask:
        """
        Start a housekeeping task

        Business Logic:
        1. Validate task exists and is pending
        2. Update status to in_progress
        3. Set started_at time
        4. Auto-assign to user if not assigned
        5. Broadcast event
        """
        task = await self.get_task_by_id(task_id, include_relations=True)
        if not task:
            raise ValueError(f"ไม่พบงาน ID {task_id}")

        if task.status != HousekeepingTaskStatusEnum.PENDING:
            raise ValueError(
                f"ไม่สามารถเริ่มงานได้ เนื่องจากสถานะไม่ถูกต้อง "
                f"(สถานะปัจจุบัน: {task.status})"
            )

        # Update task
        task.status = HousekeepingTaskStatusEnum.IN_PROGRESS
        task.started_at = started_at or now_thailand()

        # Auto-assign to current user if not assigned
        if not task.assigned_to:
            task.assigned_to = user_id

        await self.db.commit()

        # Re-fetch task with relationships for broadcasting
        task = await self.get_task_by_id(task_id, include_relations=True)

        # Broadcast event
        await self._broadcast_task_event("housekeeping_task_started", task)

        return task

    async def complete_task(
        self,
        task_id: int,
        user_id: int,
        completed_at: Optional[datetime] = None,
        notes: Optional[str] = None
    ) -> HousekeepingTask:
        """
        Complete a housekeeping task

        Business Logic:
        1. Validate task exists and is in_progress
        2. Update status to completed
        3. Set completed_at time and calculate duration
        4. Update room status to available
        5. Broadcast event
        6. TODO: Send Telegram notification
        """
        task = await self.get_task_by_id(task_id, include_relations=True)
        if not task:
            raise ValueError(f"ไม่พบงาน ID {task_id}")

        if task.status != HousekeepingTaskStatusEnum.IN_PROGRESS:
            raise ValueError(
                f"ไม่สามารถทำงานให้เสร็จได้ เนื่องจากสถานะไม่ถูกต้อง "
                f"(สถานะปัจจุบัน: {task.status})"
            )

        # Calculate duration
        complete_time = completed_at or now_thailand()
        if task.started_at:
            duration = complete_time - task.started_at
            task.duration_minutes = int(duration.total_seconds() / 60)

        # Update task
        task.status = HousekeepingTaskStatusEnum.COMPLETED
        task.completed_at = complete_time
        task.completed_by = user_id
        if notes:
            task.notes = (task.notes or "") + f"\n[เสร็จสิ้น] {notes}"

        # Update room status to available
        room = task.room
        if room and room.status == RoomStatus.CLEANING:
            # Update room status to available using RoomService (triggers breaker automation)
            from app.services.room_service import RoomService
            room_service = RoomService(self.db)
            await room_service.update_status(room.id, RoomStatus.AVAILABLE)
            # Refresh room to get updated status
            await self.db.refresh(room)

        await self.db.commit()

        # Re-fetch task with relationships for broadcasting
        task = await self.get_task_by_id(task_id, include_relations=True)

        # Broadcast task completion event
        await self._broadcast_task_event("housekeeping_task_completed", task)

        # TODO: Send Telegram notification
        # from app.services.telegram_service import TelegramService
        # telegram_service = TelegramService()
        # await telegram_service.send_task_completed_notification(task)

        return task

    async def get_stats(self) -> HousekeepingStats:
        """Get housekeeping statistics"""
        # Total tasks
        total_stmt = select(func.count(HousekeepingTask.id))
        total_result = await self.db.execute(total_stmt)
        total_tasks = total_result.scalar_one()

        # Pending tasks
        pending_stmt = select(func.count(HousekeepingTask.id)).where(
            HousekeepingTask.status == HousekeepingTaskStatusEnum.PENDING
        )
        pending_result = await self.db.execute(pending_stmt)
        pending_tasks = pending_result.scalar_one()

        # In progress tasks
        in_progress_stmt = select(func.count(HousekeepingTask.id)).where(
            HousekeepingTask.status == HousekeepingTaskStatusEnum.IN_PROGRESS
        )
        in_progress_result = await self.db.execute(in_progress_stmt)
        in_progress_tasks = in_progress_result.scalar_one()

        # Completed today
        today_start = now_thailand().replace(hour=0, minute=0, second=0, microsecond=0)
        completed_today_stmt = select(func.count(HousekeepingTask.id)).where(
            and_(
                HousekeepingTask.status == HousekeepingTaskStatusEnum.COMPLETED,
                HousekeepingTask.completed_at >= today_start
            )
        )
        completed_today_result = await self.db.execute(completed_today_stmt)
        completed_today = completed_today_result.scalar_one()

        # Average duration
        avg_duration_stmt = select(func.avg(HousekeepingTask.duration_minutes)).where(
            HousekeepingTask.duration_minutes.is_not(None)
        )
        avg_duration_result = await self.db.execute(avg_duration_stmt)
        avg_duration = avg_duration_result.scalar_one()

        return HousekeepingStats(
            total_tasks=total_tasks,
            pending_tasks=pending_tasks,
            in_progress_tasks=in_progress_tasks,
            completed_today=completed_today,
            avg_duration_minutes=float(avg_duration) if avg_duration else None
        )

    async def _get_room(self, room_id: int) -> Optional[Room]:
        """Get room by ID"""
        stmt = select(Room).where(Room.id == room_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def _get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def _broadcast_task_event(
        self,
        event_name: str,
        task: HousekeepingTask
    ):
        """Broadcast housekeeping task event via WebSocket"""
        await websocket_manager.broadcast({
            "event": event_name,
            "data": {
                "task_id": task.id,
                "room_id": task.room_id,
                "room_number": task.room.room_number if task.room else None,
                "status": task.status,
                "priority": task.priority,
                "assigned_to": task.assigned_to,
                "assigned_user_name": task.assigned_user.full_name if task.assigned_user else None,
                "timestamp": now_thailand().isoformat()
            }
        })
