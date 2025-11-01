from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import select, func, and_, cast, Date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.models.maintenance_task import MaintenanceTask, MaintenanceTaskStatusEnum, MaintenanceTaskPriorityEnum, MaintenanceTaskCategoryEnum
from app.models.room import Room
from app.models.user import User
from app.schemas.maintenance import (
    MaintenanceTaskCreate,
    MaintenanceTaskUpdate,
    MaintenanceTaskFilters,
    MaintenanceStats
)
from app.core.websocket import manager as websocket_manager
from app.core.datetime_utils import now_thailand


class MaintenanceService:
    """Service for managing maintenance tasks"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_task(
        self,
        task_data: MaintenanceTaskCreate,
        created_by_user_id: int
    ) -> MaintenanceTask:
        """
        Create a new maintenance task

        Args:
            task_data: Task creation data
            created_by_user_id: ID of user creating the task

        Returns:
            Created maintenance task

        Raises:
            NotFoundException: If room not found
        """
        # Verify room exists
        room = await self.db.get(Room, task_data.room_id)
        if not room:
            raise ValueError(f"ไม่พบห้อง ID {task_data.room_id}")

        # Verify assigned user exists if provided
        if task_data.assigned_to:
            assigned_user = await self.db.get(User, task_data.assigned_to)
            if not assigned_user:
                raise ValueError(f"ไม่พบผู้ใช้ ID {task_data.assigned_to}")

        # Create task
        import json
        photos_json = None
        if task_data.photos:
            photos_json = json.dumps(task_data.photos)

        task = MaintenanceTask(
            room_id=task_data.room_id,
            category=task_data.category,
            title=task_data.title,
            description=task_data.description,
            priority=task_data.priority,
            assigned_to=task_data.assigned_to,
            notes=task_data.notes,
            photos=photos_json,
            status=MaintenanceTaskStatusEnum.PENDING,
            created_by=created_by_user_id
        )

        self.db.add(task)
        await self.db.commit()

        # Refresh with all needed relationships
        await self.db.refresh(
            task,
            ['room', 'assigned_user', 'creator', 'completer']
        )

        # Load nested room_type relationship
        if task.room:
            await self.db.refresh(task.room, ['room_type'])

        # TODO: Broadcast WebSocket event

        # Send Telegram notification (disabled for now - needs system_settings table)
        # try:
        #     from app.services.telegram_service import TelegramService
        #     telegram_service = TelegramService(self.db)
        #     await telegram_service.send_maintenance_notification(
        #         task_id=task.id,
        #         title=task.title,
        #         room_number=room.room_number,
        #         category=task.category.value,
        #         priority=task.priority.value
        #     )
        # except Exception as e:
        #     print(f"Failed to send Telegram notification: {e}")
        #     # Don't fail the task creation if notification fails

        return task

    async def get_tasks(
        self,
        filters: Optional[MaintenanceTaskFilters] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[list[MaintenanceTask], int]:
        """
        Get maintenance tasks with filters

        Args:
            filters: Optional filters
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Tuple of (tasks list, total count)
        """
        # Build query
        query = select(MaintenanceTask).options(
            joinedload(MaintenanceTask.room).joinedload(Room.room_type),
            joinedload(MaintenanceTask.assigned_user),
            joinedload(MaintenanceTask.creator),
            joinedload(MaintenanceTask.completer)
        )

        # Apply filters
        if filters:
            if filters.status:
                query = query.where(MaintenanceTask.status == filters.status)
            if filters.priority:
                query = query.where(MaintenanceTask.priority == filters.priority)
            if filters.category:
                query = query.where(MaintenanceTask.category == filters.category)
            if filters.assigned_to:
                query = query.where(MaintenanceTask.assigned_to == filters.assigned_to)
            if filters.room_id:
                query = query.where(MaintenanceTask.room_id == filters.room_id)

        # Get total count
        count_query = select(func.count()).select_from(MaintenanceTask)
        if filters:
            if filters.status:
                count_query = count_query.where(MaintenanceTask.status == filters.status)
            if filters.priority:
                count_query = count_query.where(MaintenanceTask.priority == filters.priority)
            if filters.category:
                count_query = count_query.where(MaintenanceTask.category == filters.category)
            if filters.assigned_to:
                count_query = count_query.where(MaintenanceTask.assigned_to == filters.assigned_to)
            if filters.room_id:
                count_query = count_query.where(MaintenanceTask.room_id == filters.room_id)

        result = await self.db.execute(count_query)
        total = result.scalar_one()

        # Apply pagination and ordering
        query = query.order_by(
            MaintenanceTask.priority.desc(),
            MaintenanceTask.created_at.desc()
        ).offset(skip).limit(limit)

        result = await self.db.execute(query)
        tasks = result.scalars().unique().all()

        return list(tasks), total

    async def get_task_by_id(self, task_id: int) -> MaintenanceTask:
        """
        Get maintenance task by ID

        Args:
            task_id: Task ID

        Returns:
            Maintenance task

        Raises:
            NotFoundException: If task not found
        """
        query = select(MaintenanceTask).where(
            MaintenanceTask.id == task_id
        ).options(
            joinedload(MaintenanceTask.room).joinedload(Room.room_type),
            joinedload(MaintenanceTask.assigned_user),
            joinedload(MaintenanceTask.creator),
            joinedload(MaintenanceTask.completer)
        )

        result = await self.db.execute(query)
        task = result.scalar_one_or_none()

        if not task:
            raise ValueError(f"ไม่พบงานซ่อมบำรุง ID {task_id}")

        return task

    async def update_task(
        self,
        task_id: int,
        task_data: MaintenanceTaskUpdate
    ) -> MaintenanceTask:
        """
        Update maintenance task

        Args:
            task_id: Task ID
            task_data: Task update data

        Returns:
            Updated maintenance task

        Raises:
            NotFoundException: If task not found
            BadRequestException: If trying to update completed/cancelled task
        """
        task = await self.get_task_by_id(task_id)

        # Cannot update completed or cancelled tasks
        if task.status in [MaintenanceTaskStatusEnum.COMPLETED, MaintenanceTaskStatusEnum.CANCELLED]:
            raise ValueError(f"ไม่สามารถแก้ไขงานที่มีสถานะ {task.status.value} ได้")

        # Update fields
        update_data = task_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)

        await self.db.commit()
        await self.db.refresh(task)

        return task

    async def start_task(
        self,
        task_id: int,
        user_id: int,
        started_at: Optional[datetime] = None
    ) -> MaintenanceTask:
        """
        Start a maintenance task

        Args:
            task_id: Task ID
            user_id: ID of user starting the task
            started_at: Optional start time (defaults to now)

        Returns:
            Updated maintenance task

        Raises:
            NotFoundException: If task not found
            BadRequestException: If task not in pending status
        """
        task = await self.get_task_by_id(task_id)

        # Can only start pending tasks
        if task.status != MaintenanceTaskStatusEnum.PENDING:
            raise ValueError(f"ไม่สามารถเริ่มงานที่มีสถานะ {task.status.value} ได้")

        # Update task
        task.status = MaintenanceTaskStatusEnum.IN_PROGRESS
        task.started_at = started_at or now_thailand()

        # Auto-assign to current user if not assigned
        if not task.assigned_to:
            task.assigned_to = user_id

        await self.db.commit()

        # Refresh with all needed relationships
        await self.db.refresh(
            task,
            ['room', 'assigned_user', 'creator', 'completer']
        )

        # Load nested room_type relationship
        if task.room:
            await self.db.refresh(task.room, ['room_type'])

        # TODO: Broadcast WebSocket event

        return task

    async def complete_task(
        self,
        task_id: int,
        user_id: int,
        completed_at: Optional[datetime] = None,
        notes: Optional[str] = None
    ) -> MaintenanceTask:
        """
        Complete a maintenance task

        Args:
            task_id: Task ID
            user_id: ID of user completing the task
            completed_at: Optional completion time (defaults to now)
            notes: Optional completion notes

        Returns:
            Updated maintenance task

        Raises:
            NotFoundException: If task not found
            BadRequestException: If task not in progress
        """
        task = await self.get_task_by_id(task_id)

        # Can only complete in-progress tasks
        if task.status != MaintenanceTaskStatusEnum.IN_PROGRESS:
            raise ValueError(f"ไม่สามารถทำงานให้เสร็จที่มีสถานะ {task.status.value} ได้")

        # Update task
        task.completed_at = completed_at or now_thailand()
        task.completed_by = user_id
        task.status = MaintenanceTaskStatusEnum.COMPLETED

        if notes:
            task.notes = (task.notes or "") + f"\n[เสร็จสิ้น] {notes}"

        # Calculate duration
        if task.started_at and task.completed_at:
            duration = task.completed_at - task.started_at
            task.duration_minutes = int(duration.total_seconds() / 60)

        await self.db.commit()

        # Refresh with all needed relationships
        await self.db.refresh(
            task,
            ['room', 'assigned_user', 'creator', 'completer']
        )

        # Load nested room_type relationship
        if task.room:
            await self.db.refresh(task.room, ['room_type'])

        # TODO: Broadcast WebSocket event

        return task

    async def cancel_task(self, task_id: int) -> MaintenanceTask:
        """
        Cancel a maintenance task

        Args:
            task_id: Task ID

        Returns:
            Cancelled maintenance task

        Raises:
            NotFoundException: If task not found
            BadRequestException: If task already completed
        """
        task = await self.get_task_by_id(task_id)

        # Cannot cancel completed tasks
        if task.status == MaintenanceTaskStatusEnum.COMPLETED:
            raise ValueError("ไม่สามารถยกเลิกงานที่เสร็จแล้วได้")

        task.status = MaintenanceTaskStatusEnum.CANCELLED

        await self.db.commit()
        await self.db.refresh(task)

        return task

    async def get_stats(self) -> MaintenanceStats:
        """
        Get maintenance statistics

        Returns:
            Maintenance statistics
        """
        # Total tasks
        total_result = await self.db.execute(
            select(func.count()).select_from(MaintenanceTask)
        )
        total_tasks = total_result.scalar_one()

        # Pending tasks
        pending_result = await self.db.execute(
            select(func.count()).select_from(MaintenanceTask).where(
                MaintenanceTask.status == MaintenanceTaskStatusEnum.PENDING
            )
        )
        pending_tasks = pending_result.scalar_one()

        # In-progress tasks
        in_progress_result = await self.db.execute(
            select(func.count()).select_from(MaintenanceTask).where(
                MaintenanceTask.status == MaintenanceTaskStatusEnum.IN_PROGRESS
            )
        )
        in_progress_tasks = in_progress_result.scalar_one()

        # Completed today
        today_start = now_thailand().replace(hour=0, minute=0, second=0, microsecond=0)
        completed_today_result = await self.db.execute(
            select(func.count()).select_from(MaintenanceTask).where(
                and_(
                    MaintenanceTask.status == MaintenanceTaskStatusEnum.COMPLETED,
                    MaintenanceTask.completed_at >= today_start
                )
            )
        )
        completed_today = completed_today_result.scalar_one()

        # Average duration
        avg_duration_result = await self.db.execute(
            select(func.avg(MaintenanceTask.duration_minutes)).where(
                MaintenanceTask.status == MaintenanceTaskStatusEnum.COMPLETED
            )
        )
        avg_duration = avg_duration_result.scalar_one()

        # By category
        category_result = await self.db.execute(
            select(
                MaintenanceTask.category,
                func.count(MaintenanceTask.id)
            ).where(
                MaintenanceTask.status != MaintenanceTaskStatusEnum.CANCELLED
            ).group_by(MaintenanceTask.category)
        )
        by_category = {str(cat): count for cat, count in category_result.all()}

        # By priority
        priority_result = await self.db.execute(
            select(
                MaintenanceTask.priority,
                func.count(MaintenanceTask.id)
            ).where(
                MaintenanceTask.status.in_([
                    MaintenanceTaskStatusEnum.PENDING,
                    MaintenanceTaskStatusEnum.IN_PROGRESS
                ])
            ).group_by(MaintenanceTask.priority)
        )
        by_priority = {str(pri): count for pri, count in priority_result.all()}

        return MaintenanceStats(
            total_tasks=total_tasks,
            pending_tasks=pending_tasks,
            in_progress_tasks=in_progress_tasks,
            completed_today=completed_today,
            avg_duration_minutes=float(avg_duration) if avg_duration else None,
            by_category=by_category,
            by_priority=by_priority
        )
