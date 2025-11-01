from typing import Optional
from fastapi import APIRouter, Depends, Query, Form, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
import json
import os
from datetime import datetime

from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.room import Room
from app.services.maintenance_service import MaintenanceService
from app.schemas.maintenance import (
    MaintenanceTaskCreate,
    MaintenanceTaskUpdate,
    MaintenanceTaskResponse,
    MaintenanceTaskWithDetails,
    MaintenanceTaskListResponse,
    MaintenanceTaskFilters,
    MaintenanceTaskStartRequest,
    MaintenanceTaskCompleteRequest,
    MaintenanceStats,
    MaintenanceTaskStatusEnum,
    MaintenanceTaskPriorityEnum,
    MaintenanceTaskCategoryEnum
)

router = APIRouter()


def _map_task_to_details(task) -> MaintenanceTaskWithDetails:
    """Map MaintenanceTask model to MaintenanceTaskWithDetails schema"""
    # Parse photos from JSON if stored
    import json
    photos = []
    if task.photos:
        try:
            photos = json.loads(task.photos)
        except (json.JSONDecodeError, TypeError):
            photos = []

    return MaintenanceTaskWithDetails(
        id=task.id,
        room_id=task.room_id,
        room_number=task.room.room_number if task.room else "",
        room_type_name=task.room.room_type.name if task.room and task.room.room_type else "",
        category=task.category,
        title=task.title,
        description=task.description,
        priority=task.priority,
        status=task.status,
        assigned_to=task.assigned_to,
        assigned_user_name=task.assigned_user.full_name if task.assigned_user else None,
        created_by=task.created_by,
        creator_name=task.creator.full_name if task.creator else "",
        completed_by=task.completed_by,
        completer_name=task.completer.full_name if task.completer else None,
        notes=task.notes,
        photos=photos if photos else None,
        created_at=task.created_at,
        updated_at=task.updated_at,
        started_at=task.started_at,
        completed_at=task.completed_at,
        duration_minutes=task.duration_minutes
    )


@router.post("/", response_model=MaintenanceTaskWithDetails)
async def create_maintenance_task(
    room_id: int = Form(...),
    category: str = Form(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    priority: Optional[str] = Form("MEDIUM"),
    assigned_to: Optional[int] = Form(None),
    notes: Optional[str] = Form(None),
    photos: list[UploadFile] = File(default=[]),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new maintenance task with optional photo uploads

    Required role: ADMIN, RECEPTION, MAINTENANCE
    """
    # Create uploads directory if it doesn't exist
    uploads_dir = "uploads/maintenance"
    os.makedirs(uploads_dir, exist_ok=True)

    # Handle photo uploads
    photo_urls = []
    if photos:
        for photo in photos:
            if photo.filename:
                # Generate unique filename
                timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
                filename = f"maintenance_{timestamp}_{photo.filename}"
                file_path = os.path.join(uploads_dir, filename)

                # Save file
                with open(file_path, 'wb') as f:
                    content_data = await photo.read()
                    f.write(content_data)

                # Store relative URL
                photo_urls.append(f"/uploads/maintenance/{filename}")

    # Create task data
    task_data = MaintenanceTaskCreate(
        room_id=room_id,
        category=category,
        title=title,
        description=description,
        priority=priority,
        assigned_to=assigned_to,
        notes=notes,
        photos=photo_urls
    )

    service = MaintenanceService(db)
    task = await service.create_task(task_data, current_user.id)
    return _map_task_to_details(task)


@router.get("/", response_model=MaintenanceTaskListResponse)
async def get_maintenance_tasks(
    status: Optional[MaintenanceTaskStatusEnum] = Query(None, description="Filter by status"),
    priority: Optional[MaintenanceTaskPriorityEnum] = Query(None, description="Filter by priority"),
    category: Optional[MaintenanceTaskCategoryEnum] = Query(None, description="Filter by category"),
    assigned_to: Optional[int] = Query(None, description="Filter by assigned user ID"),
    room_id: Optional[int] = Query(None, description="Filter by room ID"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of records to return"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of maintenance tasks with filters

    Required role: ADMIN, RECEPTION, MAINTENANCE
    """
    filters = MaintenanceTaskFilters(
        status=status,
        priority=priority,
        category=category,
        assigned_to=assigned_to,
        room_id=room_id
    )

    service = MaintenanceService(db)
    tasks, total = await service.get_tasks(filters, skip, limit)

    # Map to detailed response
    tasks_with_details = [_map_task_to_details(task) for task in tasks]

    return MaintenanceTaskListResponse(
        tasks=tasks_with_details,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/{task_id}", response_model=MaintenanceTaskWithDetails)
async def get_maintenance_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get maintenance task by ID

    Required role: ADMIN, RECEPTION, MAINTENANCE
    """
    service = MaintenanceService(db)
    task = await service.get_task_by_id(task_id)
    return _map_task_to_details(task)


@router.put("/{task_id}", response_model=MaintenanceTaskResponse)
async def update_maintenance_task(
    task_id: int,
    task_data: MaintenanceTaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update maintenance task

    Required role: ADMIN, RECEPTION, MAINTENANCE
    """
    service = MaintenanceService(db)
    task = await service.update_task(task_id, task_data)
    return MaintenanceTaskResponse.model_validate(task)


@router.post("/{task_id}/start", response_model=MaintenanceTaskWithDetails)
async def start_maintenance_task(
    task_id: int,
    request: MaintenanceTaskStartRequest = MaintenanceTaskStartRequest(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Start a maintenance task

    Required role: ADMIN, MAINTENANCE
    """
    service = MaintenanceService(db)
    task = await service.start_task(task_id, current_user.id, request.started_at)
    return _map_task_to_details(task)


@router.post("/{task_id}/complete", response_model=MaintenanceTaskWithDetails)
async def complete_maintenance_task(
    task_id: int,
    request: MaintenanceTaskCompleteRequest = MaintenanceTaskCompleteRequest(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Complete a maintenance task

    Required role: ADMIN, MAINTENANCE
    """
    service = MaintenanceService(db)
    task = await service.complete_task(
        task_id,
        current_user.id,
        request.completed_at,
        request.notes
    )
    return _map_task_to_details(task)


@router.post("/{task_id}/cancel", response_model=MaintenanceTaskResponse)
async def cancel_maintenance_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cancel a maintenance task

    Required role: ADMIN
    """
    service = MaintenanceService(db)
    task = await service.cancel_task(task_id)
    return MaintenanceTaskResponse.model_validate(task)


@router.get("/stats/summary", response_model=MaintenanceStats)
async def get_maintenance_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get maintenance statistics

    Required role: ADMIN, RECEPTION, MAINTENANCE
    """
    service = MaintenanceService(db)
    stats = await service.get_stats()
    return stats
