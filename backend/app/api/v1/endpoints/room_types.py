from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.core.dependencies import get_db, require_role, get_current_user_id
from app.services.room_type_service import RoomTypeService
from app.schemas.room_type import RoomTypeCreate, RoomTypeUpdate, RoomTypeResponse, RoomTypeWithStats

router = APIRouter()


@router.get("/", response_model=List[RoomTypeResponse])
async def get_room_types(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    _current_user_id: int = Depends(get_current_user_id)
):
    """
    รายการประเภทห้องทั้งหมด

    - **skip**: จำนวนแถวที่ข้าม (สำหรับ pagination)
    - **limit**: จำนวนแถวสูงสุดที่ต้องการ
    - **is_active**: กรองตามสถานะการใช้งาน (True/False/None)

    **สิทธิ์**: ทุก role ที่ login แล้วสามารถดูได้
    """
    service = RoomTypeService(db)
    room_types = await service.get_all(skip=skip, limit=limit, is_active=is_active)
    return room_types


@router.get("/{room_type_id}", response_model=RoomTypeResponse)
async def get_room_type(
    room_type_id: int,
    db: AsyncSession = Depends(get_db),
    _current_user_id: int = Depends(get_current_user_id)
):
    """
    ดึงข้อมูลประเภทห้องตาม ID

    **สิทธิ์**: ทุก role ที่ login แล้วสามารถดูได้
    """
    service = RoomTypeService(db)
    room_type = await service.get_by_id(room_type_id)

    if not room_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ไม่พบประเภทห้อง"
        )

    return room_type


@router.get("/{room_type_id}/stats", response_model=RoomTypeWithStats)
async def get_room_type_with_stats(
    room_type_id: int,
    db: AsyncSession = Depends(get_db),
    _current_user_id: int = Depends(get_current_user_id)
):
    """
    ดึงข้อมูลประเภทห้องพร้อมสถิติ (จำนวนห้องทั้งหมด, ห้องว่าง)

    **สิทธิ์**: ทุก role ที่ login แล้วสามารถดูได้
    """
    service = RoomTypeService(db)
    room_type_stats = await service.get_with_stats(room_type_id)
    return room_type_stats


@router.post("/", response_model=RoomTypeResponse, status_code=status.HTTP_201_CREATED)
async def create_room_type(
    room_type_data: RoomTypeCreate,
    db: AsyncSession = Depends(get_db),
    _role: str = Depends(require_role(["admin"]))
):
    """
    สร้างประเภทห้องใหม่

    **สิทธิ์**: Admin เท่านั้น
    """
    service = RoomTypeService(db)
    room_type = await service.create(room_type_data)
    return room_type


@router.patch("/{room_type_id}", response_model=RoomTypeResponse)
async def update_room_type(
    room_type_id: int,
    room_type_data: RoomTypeUpdate,
    db: AsyncSession = Depends(get_db),
    _role: str = Depends(require_role(["admin"]))
):
    """
    แก้ไขข้อมูลประเภทห้อง

    **สิทธิ์**: Admin เท่านั้น
    """
    service = RoomTypeService(db)
    room_type = await service.update(room_type_id, room_type_data)
    return room_type


@router.delete("/{room_type_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_room_type(
    room_type_id: int,
    db: AsyncSession = Depends(get_db),
    _role: str = Depends(require_role(["admin"]))
):
    """
    ลบประเภทห้อง

    **Business Rule**: ไม่สามารถลบได้ถ้ามีห้องพักที่ใช้ประเภทนี้อยู่

    **สิทธิ์**: Admin เท่านั้น
    """
    service = RoomTypeService(db)
    await service.delete(room_type_id)
    return None
