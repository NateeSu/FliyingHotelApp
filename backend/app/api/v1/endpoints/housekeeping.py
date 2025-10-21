"""
Housekeeping API Endpoints (Phase 5)
Handles housekeeping task operations
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.dependencies import get_db, get_current_user
from app.models import User
from app.models.housekeeping_task import (
    HousekeepingTaskStatusEnum,
    HousekeepingTaskPriorityEnum
)
from app.services.housekeeping_service import HousekeepingService
from app.schemas.housekeeping import (
    HousekeepingTaskCreate,
    HousekeepingTaskUpdate,
    HousekeepingTaskResponse,
    HousekeepingTaskWithDetails,
    HousekeepingTaskListResponse,
    HousekeepingTaskStartRequest,
    HousekeepingTaskCompleteRequest,
    HousekeepingStats
)

router = APIRouter()


@router.post("/", response_model=HousekeepingTaskResponse)
async def create_housekeeping_task(
    task_data: HousekeepingTaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new housekeeping task

    Requires authentication (Reception or Admin role recommended)

    Request Body:
        - room_id: Room to clean
        - check_in_id: Related check-in (optional)
        - title: Task title
        - description: Task description (optional)
        - priority: Task priority (low, medium, high, urgent)
        - assigned_to: User ID to assign to (optional)
        - notes: Additional notes (optional)

    Returns:
        Created housekeeping task

    Business Logic:
        - Validates room exists
        - Updates room status to 'cleaning'
        - Broadcasts WebSocket event
        - Sends Telegram notification to housekeeping staff
    """
    try:
        service = HousekeepingService(db)
        task = await service.create_task(
            task_data=task_data,
            created_by_user_id=current_user.id
        )

        return HousekeepingTaskResponse.model_validate(task)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error creating housekeeping task: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")


@router.get("/", response_model=HousekeepingTaskListResponse)
async def get_housekeeping_tasks(
    status: Optional[HousekeepingTaskStatusEnum] = None,
    priority: Optional[HousekeepingTaskPriorityEnum] = None,
    assigned_to: Optional[int] = None,
    room_id: Optional[int] = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of housekeeping tasks with filters

    Requires authentication

    Query Parameters:
        - status: Filter by status (pending, in_progress, completed, cancelled)
        - priority: Filter by priority (low, medium, high, urgent)
        - assigned_to: Filter by assigned user ID
        - room_id: Filter by room ID
        - skip: Number of records to skip (pagination)
        - limit: Maximum number of records to return

    Returns:
        List of housekeeping tasks with details
    """
    try:
        service = HousekeepingService(db)
        tasks, total = await service.get_tasks(
            status=status,
            priority=priority,
            assigned_to=assigned_to,
            room_id=room_id,
            skip=skip,
            limit=limit
        )

        # Convert to response models with details
        tasks_with_details = []
        for task in tasks:
            task_dict = {
                "id": task.id,
                "room_id": task.room_id,
                "check_in_id": task.check_in_id,
                "assigned_to": task.assigned_to,
                "status": task.status,
                "priority": task.priority,
                "title": task.title,
                "description": task.description,
                "notes": task.notes,
                "created_at": task.created_at,
                "started_at": task.started_at,
                "completed_at": task.completed_at,
                "duration_minutes": task.duration_minutes,
                "created_by": task.created_by,
                "completed_by": task.completed_by,
                "updated_at": task.updated_at,
                "room_number": task.room.room_number if task.room else None,
                "room_type_name": task.room.room_type.name if task.room and task.room.room_type else None,
                "assigned_user_name": task.assigned_user.full_name if task.assigned_user else None,
                "creator_name": task.creator.full_name if task.creator else None,
                "completer_name": task.completer.full_name if task.completer else None
            }
            tasks_with_details.append(HousekeepingTaskWithDetails(**task_dict))

        return HousekeepingTaskListResponse(
            data=tasks_with_details,
            total=total
        )

    except Exception as e:
        print(f"Error getting housekeeping tasks: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")


@router.get("/{task_id}", response_model=HousekeepingTaskWithDetails)
async def get_housekeeping_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get housekeeping task by ID with details

    Requires authentication

    Returns:
        Housekeeping task with room and user details
    """
    try:
        service = HousekeepingService(db)
        task = await service.get_task_by_id(task_id, include_relations=True)

        if not task:
            raise HTTPException(status_code=404, detail="ไม่พบงานทำความสะอาด")

        task_dict = {
            "id": task.id,
            "room_id": task.room_id,
            "check_in_id": task.check_in_id,
            "assigned_to": task.assigned_to,
            "status": task.status,
            "priority": task.priority,
            "title": task.title,
            "description": task.description,
            "notes": task.notes,
            "created_at": task.created_at,
            "started_at": task.started_at,
            "completed_at": task.completed_at,
            "duration_minutes": task.duration_minutes,
            "created_by": task.created_by,
            "completed_by": task.completed_by,
            "updated_at": task.updated_at,
            "room_number": task.room.room_number if task.room else None,
            "room_type_name": task.room.room_type.name if task.room and task.room.room_type else None,
            "assigned_user_name": task.assigned_user.full_name if task.assigned_user else None,
            "creator_name": task.creator.full_name if task.creator else None,
            "completer_name": task.completer.full_name if task.completer else None
        }

        return HousekeepingTaskWithDetails(**task_dict)

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting housekeeping task: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")


@router.put("/{task_id}", response_model=HousekeepingTaskResponse)
async def update_housekeeping_task(
    task_id: int,
    update_data: HousekeepingTaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update housekeeping task

    Requires authentication

    Request Body:
        - status: Task status (optional)
        - priority: Task priority (optional)
        - assigned_to: User ID to assign to (optional)
        - notes: Additional notes (optional)

    Returns:
        Updated housekeeping task
    """
    try:
        service = HousekeepingService(db)
        task = await service.update_task(task_id, update_data)

        return HousekeepingTaskResponse.model_validate(task)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error updating housekeeping task: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")


@router.post("/{task_id}/start", response_model=HousekeepingTaskResponse)
async def start_housekeeping_task(
    task_id: int,
    start_data: HousekeepingTaskStartRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Start a housekeeping task

    Requires authentication (Housekeeping role recommended)

    Request Body:
        - started_at: Optional start time (defaults to now)

    Returns:
        Updated task with status 'in_progress'

    Business Logic:
        - Updates status to 'in_progress'
        - Sets started_at time
        - Auto-assigns to current user if not assigned
        - Broadcasts WebSocket event
    """
    try:
        service = HousekeepingService(db)
        task = await service.start_task(
            task_id=task_id,
            user_id=current_user.id,
            started_at=start_data.started_at
        )

        return HousekeepingTaskResponse.model_validate(task)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error starting housekeeping task: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")


@router.post("/{task_id}/complete", response_model=HousekeepingTaskResponse)
async def complete_housekeeping_task(
    task_id: int,
    complete_data: HousekeepingTaskCompleteRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Complete a housekeeping task

    Requires authentication (Housekeeping role recommended)

    Request Body:
        - completed_at: Optional completion time (defaults to now)
        - notes: Completion notes (optional)

    Returns:
        Updated task with status 'completed'

    Business Logic:
        - Updates status to 'completed'
        - Sets completed_at time
        - Calculates duration
        - Updates room status to 'available'
        - Broadcasts WebSocket event
        - Sends Telegram notification to reception
    """
    try:
        service = HousekeepingService(db)
        task = await service.complete_task(
            task_id=task_id,
            user_id=current_user.id,
            completed_at=complete_data.completed_at,
            notes=complete_data.notes
        )

        return HousekeepingTaskResponse.model_validate(task)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error completing housekeeping task: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")


@router.get("/stats/summary", response_model=HousekeepingStats)
async def get_housekeeping_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get housekeeping statistics

    Requires authentication

    Returns:
        Statistics including:
        - Total tasks
        - Pending tasks
        - In progress tasks
        - Completed today
        - Average duration (minutes)
    """
    try:
        service = HousekeepingService(db)
        stats = await service.get_stats()

        return stats

    except Exception as e:
        print(f"Error getting housekeeping stats: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")
