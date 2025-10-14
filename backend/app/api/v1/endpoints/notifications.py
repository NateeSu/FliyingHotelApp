"""
Notification API Endpoints (Phase 3)
Manages notifications for different user roles
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.dependencies import get_db, get_current_user
from app.models import User
from app.services import NotificationService
from app.schemas.notification import (
    NotificationCreate,
    NotificationResponse,
    NotificationListResponse,
    NotificationMarkAllReadResponse
)
from app.schemas.user import UserRole

router = APIRouter()


@router.get("/", response_model=NotificationListResponse)
async def get_notifications(
    limit: int = Query(50, ge=1, le=100, description="Maximum number of notifications to return"),
    offset: int = Query(0, ge=0, description="Number of notifications to skip"),
    unread_only: bool = Query(False, description="Return only unread notifications"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get notifications for current user's role

    Requires authentication.

    Query Parameters:
        - limit: Maximum number of notifications (1-100, default: 50)
        - offset: Number to skip for pagination (default: 0)
        - unread_only: If true, return only unread notifications (default: false)

    Returns:
        List of notifications with total count and unread count
    """
    service = NotificationService(db)

    # Get notifications for user's role
    notifications, total = await service.get_notifications_by_role(
        target_role=current_user.role,
        limit=limit,
        offset=offset,
        unread_only=unread_only
    )

    # Get unread count
    unread_count = await service.get_unread_count_by_role(current_user.role)

    # Convert to response models
    notification_responses = [
        NotificationResponse.model_validate(n) for n in notifications
    ]

    return NotificationListResponse(
        data=notification_responses,
        total=total,
        unread_count=unread_count
    )


@router.get("/unread-count", response_model=dict)
async def get_unread_count(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get count of unread notifications for current user

    Requires authentication.

    Returns:
        {"unread_count": int}
    """
    service = NotificationService(db)
    count = await service.get_unread_count_by_role(current_user.role)
    return {"unread_count": count}


@router.patch("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_as_read(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mark a notification as read

    Requires authentication.

    Returns:
        Updated notification
    """
    service = NotificationService(db)

    # Get notification and verify ownership
    notification = await service.get_notification_by_id(notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="ไม่พบการแจ้งเตือน")

    # Check if notification belongs to user's role
    if notification.target_role != current_user.role:
        raise HTTPException(status_code=403, detail="ไม่มีสิทธิ์เข้าถึงการแจ้งเตือนนี้")

    # Mark as read
    notification = await service.mark_as_read(notification_id)

    return NotificationResponse.model_validate(notification)


@router.post("/mark-all-read", response_model=NotificationMarkAllReadResponse)
async def mark_all_notifications_as_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mark all notifications as read for current user's role

    Requires authentication.

    Returns:
        Number of notifications marked as read
    """
    service = NotificationService(db)
    count = await service.mark_all_as_read(current_user.role)

    return NotificationMarkAllReadResponse(
        marked_count=count,
        message=f"ทำเครื่องหมายการแจ้งเตือน {count} รายการว่าอ่านแล้ว"
    )


@router.post("/", response_model=NotificationResponse)
async def create_notification(
    notification_data: NotificationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new notification (Admin only)

    Requires authentication and admin role.

    Returns:
        Created notification
    """
    # Only admin can manually create notifications
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="เฉพาะผู้ดูแลระบบเท่านั้นที่สามารถสร้างการแจ้งเตือนได้")

    service = NotificationService(db)
    notification = await service.create_notification(notification_data)

    return NotificationResponse.model_validate(notification)
