"""
Public API Endpoints (Phase 5.1)
Public endpoints that don't require authentication
Used for Telegram bot links to allow staff to view and complete tasks
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.services.housekeeping_service import HousekeepingService
from app.services.maintenance_service import MaintenanceService
from app.schemas.housekeeping import (
    HousekeepingTaskWithDetails,
    HousekeepingTaskStartRequest,
    HousekeepingTaskCompleteRequest
)
from app.schemas.maintenance import (
    MaintenanceTaskResponse,
    MaintenanceTaskStartRequest,
    MaintenanceTaskCompleteRequest,
    MaintenanceTaskCreate
)

router = APIRouter()


# ==================== Housekeeping Public Endpoints ====================

@router.get("/housekeeping/tasks/{task_id}", response_model=HousekeepingTaskWithDetails)
async def get_public_housekeeping_task(
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get housekeeping task details (PUBLIC - no authentication required)

    This endpoint is used by Telegram bot links to allow housekeeping staff
    to view task details without logging in.

    Path Parameters:
        - task_id: Task ID

    Returns:
        Housekeeping task with full details
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
        print(f"Error getting public housekeeping task: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")


@router.post("/housekeeping/tasks/{task_id}/start")
async def start_public_housekeeping_task(
    task_id: int,
    start_data: HousekeepingTaskStartRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Start housekeeping task (PUBLIC - no authentication required)

    This endpoint is used by Telegram bot links to allow housekeeping staff
    to start tasks without logging in.

    Path Parameters:
        - task_id: Task ID

    Request Body:
        - started_at: Optional start time (defaults to now)

    Note: Since there's no authentication, the task will be started without
    assigning to a specific user (unless already assigned).
    """
    try:
        service = HousekeepingService(db)

        # Get task to check if it's already assigned
        task = await service.get_task_by_id(task_id, include_relations=False)
        if not task:
            raise HTTPException(status_code=404, detail="ไม่พบงานทำความสะอาด")

        # Use assigned user if exists, otherwise use a default user_id
        # In production, you might want to create a special "telegram_bot" user
        user_id = task.assigned_to if task.assigned_to else 1  # Default to admin user

        task = await service.start_task(
            task_id=task_id,
            user_id=user_id,
            started_at=start_data.started_at
        )

        return {
            "success": True,
            "message": "เริ่มงานทำความสะอาดเรียบร้อย",
            "task_id": task.id,
            "status": task.status
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error starting public housekeeping task: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")


@router.post("/housekeeping/tasks/{task_id}/complete")
async def complete_public_housekeeping_task(
    task_id: int,
    complete_data: HousekeepingTaskCompleteRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Complete housekeeping task (PUBLIC - no authentication required)

    This endpoint is used by Telegram bot links to allow housekeeping staff
    to complete tasks without logging in.

    Path Parameters:
        - task_id: Task ID

    Request Body:
        - completed_at: Optional completion time (defaults to now)
        - notes: Completion notes (optional)
    """
    try:
        service = HousekeepingService(db)

        # Get task to check if it's already assigned
        task = await service.get_task_by_id(task_id, include_relations=False)
        if not task:
            raise HTTPException(status_code=404, detail="ไม่พบงานทำความสะอาด")

        # Use assigned user if exists, otherwise use a default user_id
        user_id = task.assigned_to if task.assigned_to else 1  # Default to admin user

        task = await service.complete_task(
            task_id=task_id,
            user_id=user_id,
            completed_at=complete_data.completed_at,
            notes=complete_data.notes
        )

        return {
            "success": True,
            "message": "ทำความสะอาดเสร็จสิ้นเรียบร้อย",
            "task_id": task.id,
            "status": task.status,
            "duration_minutes": task.duration_minutes
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error completing public housekeeping task: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")


# ==================== Maintenance Public Endpoints ====================

@router.get("/maintenance/tasks/{task_id}", response_model=MaintenanceTaskResponse)
async def get_public_maintenance_task(
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get maintenance task details (PUBLIC - no authentication required)

    This endpoint is used by Telegram bot links to allow maintenance staff
    to view task details without logging in.

    Path Parameters:
        - task_id: Task ID

    Returns:
        Maintenance task with full details
    """
    try:
        service = MaintenanceService(db)
        task = await service.get_task_by_id(task_id)

        return MaintenanceTaskResponse.model_validate(task)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print(f"Error getting public maintenance task: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")


@router.post("/maintenance/tasks/{task_id}/start")
async def start_public_maintenance_task(
    task_id: int,
    start_data: MaintenanceTaskStartRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Start maintenance task (PUBLIC - no authentication required)

    This endpoint is used by Telegram bot links to allow maintenance staff
    to start tasks without logging in.

    Path Parameters:
        - task_id: Task ID

    Request Body:
        - started_at: Optional start time (defaults to now)
    """
    try:
        service = MaintenanceService(db)

        # Get task to check if it's already assigned
        task = await service.get_task_by_id(task_id)

        # Use assigned user if exists, otherwise use a default user_id
        user_id = task.assigned_to if task.assigned_to else 1  # Default to admin user

        task = await service.start_task(
            task_id=task_id,
            user_id=user_id,
            started_at=start_data.started_at
        )

        return {
            "success": True,
            "message": "เริ่มงานซ่อมบำรุงเรียบร้อย",
            "task_id": task.id,
            "status": task.status
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error starting public maintenance task: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")


@router.post("/maintenance/tasks/{task_id}/complete")
async def complete_public_maintenance_task(
    task_id: int,
    complete_data: MaintenanceTaskCompleteRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Complete maintenance task (PUBLIC - no authentication required)

    This endpoint is used by Telegram bot links to allow maintenance staff
    to complete tasks without logging in.

    Path Parameters:
        - task_id: Task ID

    Request Body:
        - completed_at: Optional completion time (defaults to now)
        - notes: Completion notes (optional)
    """
    try:
        service = MaintenanceService(db)

        # Get task to check if it's already assigned
        task = await service.get_task_by_id(task_id)

        # Use assigned user if exists, otherwise use a default user_id
        user_id = task.assigned_to if task.assigned_to else 1  # Default to admin user

        task = await service.complete_task(
            task_id=task_id,
            user_id=user_id,
            completed_at=complete_data.completed_at,
            notes=complete_data.notes
        )

        return {
            "success": True,
            "message": "งานซ่อมบำรุงเสร็จสิ้นเรียบร้อย",
            "task_id": task.id,
            "status": task.status,
            "duration_minutes": task.duration_minutes
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error completing public maintenance task: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")


@router.post("/maintenance/report")
async def report_public_maintenance(
    report_data: MaintenanceTaskCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create maintenance task report (PUBLIC - no authentication required)

    This endpoint is used by housekeeping staff (via public links) to report
    damage or maintenance needs they discover while cleaning.

    Request Body:
        - room_id: Room ID
        - title: Task title
        - description: Task description (optional)
        - category: Task category (plumbing, electrical, hvac, furniture, appliance, building, other)
        - priority: Priority level (urgent, high, medium, low)
        - assigned_to: Assigned user ID (optional)

    Returns:
        Created maintenance task
    """
    try:
        service = MaintenanceService(db)

        # Create task using default user (admin) as creator since no auth
        # In production, you might want to create a special "housekeeping_report" user
        creator_user_id = 1  # Default to admin user

        task = await service.create_task(report_data, creator_user_id)

        return {
            "success": True,
            "message": "แจ้งซ่อมบำรุงเรียบร้อย",
            "task_id": task.id,
            "room_id": task.room_id
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error creating public maintenance report: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")
