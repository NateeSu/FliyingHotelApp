"""
Breaker Management API Endpoints

Manages smart breaker devices and control operations.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime

from app.core.dependencies import get_db, require_role, get_current_user_id
from app.services.breaker_service import BreakerService
from app.models.home_assistant import (
    BreakerState,
    BreakerAction,
    TriggerType,
    ActionStatus
)
from app.schemas.home_assistant import (
    BreakerCreate,
    BreakerUpdate,
    BreakerResponse,
    BreakerListResponse,
    BreakerControlRequest,
    BreakerControlResponse,
    BreakerSyncResponse,
    BreakerActivityLogResponse,
    BreakerActivityLogListResponse,
    BreakerActivityLogFilter,
    BreakerStatistics
)
from app.core.exceptions import (
    BreakerNotFoundError,
    BreakerAlreadyExistsError,
    BreakerRoomConflictError
)

router = APIRouter()


@router.get("/", response_model=BreakerListResponse)
async def get_breakers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    room_id: Optional[int] = None,
    auto_control_enabled: Optional[bool] = None,
    current_state: Optional[BreakerState] = None,
    is_active: Optional[bool] = True,
    db: AsyncSession = Depends(get_db),
    _current_user_id: int = Depends(get_current_user_id)
):
    """
    รายการ breaker ทั้งหมด

    **สิทธิ์**: ทุก role ที่ login แล้ว

    **Query Parameters**:
    - **skip**: ข้ามแถว (pagination)
    - **limit**: จำนวนแถวสูงสุด
    - **room_id**: กรองตามห้อง
    - **auto_control_enabled**: กรองตาม auto control
    - **current_state**: กรองตามสถานะ (ON, OFF, UNAVAILABLE)
    - **is_active**: กรองตามสถานะการใช้งาน

    **Returns**: รายการ breakers พร้อมข้อมูลห้อง
    """
    service = BreakerService(db)
    breakers = await service.get_all(
        skip=skip,
        limit=limit,
        room_id=room_id,
        auto_control_enabled=auto_control_enabled,
        current_state=current_state,
        is_active=is_active
    )

    # Build response with room info
    breaker_responses = []
    for breaker in breakers:
        breaker_dict = {
            "id": breaker.id,
            "entity_id": breaker.entity_id,
            "friendly_name": breaker.friendly_name,
            "room_id": breaker.room_id,
            "room_number": breaker.room.room_number if breaker.room else None,
            "room_status": breaker.room.status.value if breaker.room else None,
            "auto_control_enabled": breaker.auto_control_enabled,
            "is_available": breaker.is_available,
            "current_state": breaker.current_state,
            "last_state_update": breaker.last_state_update,
            "consecutive_errors": breaker.consecutive_errors,
            "last_error_message": breaker.last_error_message,
            "is_active": breaker.is_active,
            "created_at": breaker.created_at,
            "updated_at": breaker.updated_at
        }
        breaker_responses.append(BreakerResponse(**breaker_dict))

    return BreakerListResponse(
        breakers=breaker_responses,
        total=len(breaker_responses)
    )


@router.get("/{breaker_id}", response_model=BreakerResponse)
async def get_breaker(
    breaker_id: int,
    db: AsyncSession = Depends(get_db),
    _current_user_id: int = Depends(get_current_user_id)
):
    """
    ดึงข้อมูล breaker ตาม ID

    **สิทธิ์**: ทุก role ที่ login แล้ว

    **Returns**: ข้อมูล breaker พร้อมข้อมูลห้อง
    """
    service = BreakerService(db)
    breaker = await service.get_by_id(breaker_id)

    if not breaker:
        raise BreakerNotFoundError(f"ไม่พบ breaker ID {breaker_id}")

    return BreakerResponse(
        id=breaker.id,
        entity_id=breaker.entity_id,
        friendly_name=breaker.friendly_name,
        room_id=breaker.room_id,
        room_number=breaker.room.room_number if breaker.room else None,
        room_status=breaker.room.status.value if breaker.room else None,
        auto_control_enabled=breaker.auto_control_enabled,
        is_available=breaker.is_available,
        current_state=breaker.current_state,
        last_state_update=breaker.last_state_update,
        consecutive_errors=breaker.consecutive_errors,
        last_error_message=breaker.last_error_message,
        is_active=breaker.is_active,
        created_at=breaker.created_at,
        updated_at=breaker.updated_at
    )


@router.post("/", response_model=BreakerResponse, status_code=status.HTTP_201_CREATED)
async def create_breaker(
    data: BreakerCreate,
    db: AsyncSession = Depends(get_db),
    _current_user_id: int = Depends(require_role(["ADMIN"]))
):
    """
    สร้าง breaker ใหม่

    **สิทธิ์**: ADMIN เท่านั้น

    **Body Parameters**:
    - **entity_id**: Home Assistant Entity ID (เช่น switch.room_101_breaker)
    - **friendly_name**: ชื่อที่แสดงผล (เช่น Breaker ห้อง 101)
    - **room_id**: ID ห้องที่เชื่อมโยง (optional)
    - **auto_control_enabled**: เปิด/ปิดควบคุมอัตโนมัติ (default: true)

    **Returns**: Breaker ที่สร้าง
    """
    service = BreakerService(db)

    try:
        breaker = await service.create(
            entity_id=data.entity_id,
            friendly_name=data.friendly_name,
            room_id=data.room_id,
            auto_control_enabled=data.auto_control_enabled
        )

        return BreakerResponse(
            id=breaker.id,
            entity_id=breaker.entity_id,
            friendly_name=breaker.friendly_name,
            room_id=breaker.room_id,
            room_number=breaker.room.room_number if breaker.room else None,
            room_status=breaker.room.status.value if breaker.room else None,
            auto_control_enabled=breaker.auto_control_enabled,
            is_available=breaker.is_available,
            current_state=breaker.current_state,
            last_state_update=breaker.last_state_update,
            consecutive_errors=breaker.consecutive_errors,
            last_error_message=breaker.last_error_message,
            is_active=breaker.is_active,
            created_at=breaker.created_at,
            updated_at=breaker.updated_at
        )
    except BreakerAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except BreakerRoomConflictError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/{breaker_id}", response_model=BreakerResponse)
async def update_breaker(
    breaker_id: int,
    data: BreakerUpdate,
    db: AsyncSession = Depends(get_db),
    _current_user_id: int = Depends(require_role(["ADMIN"]))
):
    """
    อัปเดตข้อมูล breaker

    **สิทธิ์**: ADMIN เท่านั้น

    **Body Parameters**:
    - **entity_id**: Entity ID ใหม่
    - **friendly_name**: ชื่อใหม่
    - **room_id**: เปลี่ยนห้องที่เชื่อมโยง
    - **auto_control_enabled**: เปลี่ยนสถานะควบคุมอัตโนมัติ

    **Returns**: Breaker ที่อัปเดต
    """
    service = BreakerService(db)

    try:
        breaker = await service.update(
            breaker_id=breaker_id,
            entity_id=data.entity_id,
            friendly_name=data.friendly_name,
            room_id=data.room_id,
            auto_control_enabled=data.auto_control_enabled
        )

        return BreakerResponse(
            id=breaker.id,
            entity_id=breaker.entity_id,
            friendly_name=breaker.friendly_name,
            room_id=breaker.room_id,
            room_number=breaker.room.room_number if breaker.room else None,
            room_status=breaker.room.status.value if breaker.room else None,
            auto_control_enabled=breaker.auto_control_enabled,
            is_available=breaker.is_available,
            current_state=breaker.current_state,
            last_state_update=breaker.last_state_update,
            consecutive_errors=breaker.consecutive_errors,
            last_error_message=breaker.last_error_message,
            is_active=breaker.is_active,
            created_at=breaker.created_at,
            updated_at=breaker.updated_at
        )
    except BreakerNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (BreakerAlreadyExistsError, BreakerRoomConflictError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{breaker_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_breaker(
    breaker_id: int,
    db: AsyncSession = Depends(get_db),
    _current_user_id: int = Depends(require_role(["ADMIN"]))
):
    """
    ลบ breaker (soft delete)

    **สิทธิ์**: ADMIN เท่านั้น

    **Returns**: HTTP 204 No Content
    """
    service = BreakerService(db)

    try:
        await service.delete(breaker_id)
        return None
    except BreakerNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{breaker_id}/turn-on", response_model=BreakerControlResponse)
async def turn_on_breaker(
    breaker_id: int,
    request: BreakerControlRequest = BreakerControlRequest(),
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
    _role: str = Depends(require_role(["ADMIN", "RECEPTION"]))
):
    """
    เปิด breaker แบบ manual

    **สิทธิ์**: ADMIN, RECEPTION

    **Body Parameters**:
    - **reason**: เหตุผลในการเปิด (optional)

    **Returns**: ผลลัพธ์การเปิด breaker
    """
    service = BreakerService(db)

    try:
        result = await service.turn_on(
            breaker_id=breaker_id,
            trigger_type=TriggerType.MANUAL,
            triggered_by=current_user_id
        )

        return BreakerControlResponse(
            success=result["success"],
            message=result["message"],
            breaker_id=result["breaker_id"],
            new_state=result["new_state"],
            response_time_ms=result.get("response_time_ms")
        )
    except BreakerNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{breaker_id}/turn-off", response_model=BreakerControlResponse)
async def turn_off_breaker(
    breaker_id: int,
    request: BreakerControlRequest = BreakerControlRequest(),
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
    _role: str = Depends(require_role(["ADMIN", "RECEPTION"]))
):
    """
    ปิด breaker แบบ manual

    **สิทธิ์**: ADMIN, RECEPTION

    **Body Parameters**:
    - **reason**: เหตุผลในการปิด (optional)

    **Returns**: ผลลัพธ์การปิด breaker
    """
    service = BreakerService(db)

    try:
        result = await service.turn_off(
            breaker_id=breaker_id,
            trigger_type=TriggerType.MANUAL,
            triggered_by=current_user_id
        )

        return BreakerControlResponse(
            success=result["success"],
            message=result["message"],
            breaker_id=result["breaker_id"],
            new_state=result["new_state"],
            response_time_ms=result.get("response_time_ms")
        )
    except BreakerNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{breaker_id}/sync-status", response_model=BreakerSyncResponse)
async def sync_breaker_status(
    breaker_id: int,
    db: AsyncSession = Depends(get_db),
    _current_user_id: int = Depends(get_current_user_id)
):
    """
    ซิงค์สถานะ breaker จาก Home Assistant

    **สิทธิ์**: ทุก role ที่ login แล้ว

    **Returns**: สถานะปัจจุบันของ breaker
    """
    service = BreakerService(db)

    try:
        result = await service.sync_breaker_state(breaker_id)

        # Return result (can be success or failure)
        return BreakerSyncResponse(
            success=result["success"],
            message=result["message"],
            breaker_id=result["breaker_id"],
            current_state=result["current_state"],
            is_available=result["is_available"],
            synced_at=result["synced_at"]
        )
    except BreakerNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/sync-all", response_model=dict)
async def sync_all_breakers(
    db: AsyncSession = Depends(get_db),
    _current_user_id: int = Depends(require_role(["ADMIN"]))
):
    """
    ซิงค์สถานะ breaker ทั้งหมดจาก Home Assistant

    **สิทธิ์**: ADMIN เท่านั้น

    **Returns**: สรุปผลการซิงค์
    """
    service = BreakerService(db)

    try:
        result = await service.sync_all_breakers()
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{breaker_id}/logs", response_model=BreakerActivityLogListResponse)
async def get_breaker_activity_logs(
    breaker_id: int,
    action: Optional[BreakerAction] = None,
    trigger_type: Optional[TriggerType] = None,
    status: Optional[ActionStatus] = None,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    _current_user_id: int = Depends(get_current_user_id)
):
    """
    ดึง activity logs ของ breaker

    **สิทธิ์**: ทุก role ที่ login แล้ว

    **Query Parameters**:
    - **action**: กรองตามการกระทำ (TURN_ON, TURN_OFF, STATUS_SYNC)
    - **trigger_type**: กรองตาม trigger (AUTO, MANUAL, SYSTEM)
    - **status**: กรองตามผลลัพธ์ (SUCCESS, FAILED, TIMEOUT)
    - **limit**: จำนวนแถวสูงสุด
    - **offset**: ข้ามแถว

    **Returns**: รายการ activity logs
    """
    service = BreakerService(db)

    logs = await service.get_activity_logs(
        breaker_id=breaker_id,
        action=action,
        trigger_type=trigger_type,
        status=status,
        limit=limit,
        offset=offset
    )

    log_responses = []
    for log in logs:
        log_dict = {
            "id": log.id,
            "breaker_id": log.breaker_id,
            "entity_id": log.breaker.entity_id if log.breaker else None,
            "friendly_name": log.breaker.friendly_name if log.breaker else None,
            "action": log.action,
            "trigger_type": log.trigger_type,
            "triggered_by": log.triggered_by,
            "triggered_by_name": log.triggered_by_user.username if log.triggered_by_user else None,
            "room_status_before": log.room_status_before,
            "room_status_after": log.room_status_after,
            "status": log.status,
            "error_message": log.error_message,
            "response_time_ms": log.response_time_ms,
            "created_at": log.created_at
        }
        log_responses.append(BreakerActivityLogResponse(**log_dict))

    return BreakerActivityLogListResponse(
        logs=log_responses,
        total=len(log_responses)
    )


@router.get("/logs/all", response_model=BreakerActivityLogListResponse)
async def get_all_activity_logs(
    breaker_id: Optional[int] = None,
    action: Optional[BreakerAction] = None,
    trigger_type: Optional[TriggerType] = None,
    status: Optional[ActionStatus] = None,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    _current_user_id: int = Depends(get_current_user_id)
):
    """
    ดึง activity logs ทั้งหมด (จากทุก breaker)

    **สิทธิ์**: ทุก role ที่ login แล้ว

    **Returns**: รายการ activity logs ทั้งหมด
    """
    service = BreakerService(db)

    logs = await service.get_activity_logs(
        breaker_id=breaker_id,
        action=action,
        trigger_type=trigger_type,
        status=status,
        limit=limit,
        offset=offset
    )

    log_responses = []
    for log in logs:
        log_dict = {
            "id": log.id,
            "breaker_id": log.breaker_id,
            "entity_id": log.breaker.entity_id if log.breaker else None,
            "friendly_name": log.breaker.friendly_name if log.breaker else None,
            "action": log.action,
            "trigger_type": log.trigger_type,
            "triggered_by": log.triggered_by,
            "triggered_by_name": log.triggered_by_user.username if log.triggered_by_user else None,
            "room_status_before": log.room_status_before,
            "room_status_after": log.room_status_after,
            "status": log.status,
            "error_message": log.error_message,
            "response_time_ms": log.response_time_ms,
            "created_at": log.created_at
        }
        log_responses.append(BreakerActivityLogResponse(**log_dict))

    return BreakerActivityLogListResponse(
        logs=log_responses,
        total=len(log_responses)
    )


@router.get("/stats/overview", response_model=BreakerStatistics)
async def get_breaker_statistics(
    db: AsyncSession = Depends(get_db),
    _current_user_id: int = Depends(get_current_user_id)
):
    """
    ดึงสถิติ breaker

    **สิทธิ์**: ทุก role ที่ login แล้ว

    **Returns**: สถิติ breaker ทั้งหมด
    """
    service = BreakerService(db)

    try:
        stats = await service.get_statistics()
        return BreakerStatistics(**stats)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
