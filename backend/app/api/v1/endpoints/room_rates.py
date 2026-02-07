from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import date
from app.core.dependencies import get_db, require_role, get_current_user_id
from app.services.room_rate_service import RoomRateService
from app.schemas.room_rate import RoomRateCreate, RoomRateUpdate, RoomRateResponse, RoomRateWithRoomType, RoomRateMatrix
from app.models.room_rate import RoomRate, StayType

router = APIRouter()


def _serialize_rate(rate: RoomRate) -> RoomRateWithRoomType:
    """Convert SQLAlchemy RoomRate to Pydantic response, avoiding __dict__ conflicts."""
    rate_data = {c.key: getattr(rate, c.key) for c in RoomRate.__table__.columns}
    if rate.room_type:
        from app.models.room_type import RoomType
        rate_data["room_type"] = {c.key: getattr(rate.room_type, c.key) for c in RoomType.__table__.columns}
    else:
        rate_data["room_type"] = None
    return RoomRateWithRoomType(**rate_data)


@router.get("/", response_model=List[RoomRateWithRoomType])
async def get_room_rates(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    room_type_id: Optional[int] = Query(None, gt=0),
    stay_type: Optional[StayType] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    _current_user_id: int = Depends(get_current_user_id)
):
    """
    รายการอัตราค่าห้องทั้งหมด พร้อมข้อมูลประเภทห้อง

    - **skip**: จำนวนแถวที่ข้าม (สำหรับ pagination)
    - **limit**: จำนวนแถวสูงสุดที่ต้องการ
    - **room_type_id**: กรองตามประเภทห้อง
    - **stay_type**: กรองตามประเภทการเข้าพัก (overnight, temporary)
    - **is_active**: กรองตามสถานะการใช้งาน

    **สิทธิ์**: ทุก role ที่ login แล้วสามารถดูได้
    """
    service = RoomRateService(db)
    rates = await service.get_all(
        skip=skip,
        limit=limit,
        room_type_id=room_type_id,
        stay_type=stay_type,
        is_active=is_active
    )

    return [_serialize_rate(rate) for rate in rates]


@router.get("/matrix", response_model=List[RoomRateMatrix])
async def get_rate_matrix(
    db: AsyncSession = Depends(get_db),
    _current_user_id: int = Depends(get_current_user_id)
):
    """
    ดึงราคาห้องในรูปแบบ Matrix สำหรับแสดงผลบน UI

    Returns:
    ```json
    [
      {
        "room_type_id": 1,
        "room_type_name": "Standard",
        "overnight_rate": 600.00,
        "temporary_rate": 300.00,
        "overnight_rate_id": 1,
        "temporary_rate_id": 2
      },
      ...
    ]
    ```

    **สิทธิ์**: ทุก role ที่ login แล้วสามารถดูได้
    """
    service = RoomRateService(db)
    matrix = await service.get_rate_matrix()
    return matrix


@router.get("/current", response_model=RoomRateResponse)
async def get_current_rate(
    room_type_id: int = Query(..., gt=0),
    stay_type: StayType = Query(...),
    check_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    _current_user_id: int = Depends(get_current_user_id)
):
    """
    ดึงราคาปัจจุบันสำหรับประเภทห้องและประเภทการเข้าพัก

    - **room_type_id**: ID ประเภทห้อง
    - **stay_type**: ประเภทการเข้าพัก (overnight, temporary)
    - **check_date**: วันที่ต้องการเช็คราคา (default: วันนี้)

    **สิทธิ์**: ทุก role ที่ login แล้วสามารถดูได้
    """
    service = RoomRateService(db)
    rate = await service.get_current_rate(room_type_id, stay_type, check_date)

    if not rate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ไม่พบอัตราค่าห้องสำหรับประเภทห้องและประเภทการเข้าพักนี้"
        )

    return rate


@router.get("/{room_rate_id}", response_model=RoomRateWithRoomType)
async def get_room_rate(
    room_rate_id: int,
    db: AsyncSession = Depends(get_db),
    _current_user_id: int = Depends(get_current_user_id)
):
    """
    ดึงข้อมูลอัตราค่าห้องตาม ID พร้อมข้อมูลประเภทห้อง

    **สิทธิ์**: ทุก role ที่ login แล้วสามารถดูได้
    """
    service = RoomRateService(db)
    rate = await service.get_by_id(room_rate_id)

    if not rate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ไม่พบอัตราค่าห้อง"
        )

    return _serialize_rate(rate)


@router.post("/", response_model=RoomRateWithRoomType, status_code=status.HTTP_201_CREATED)
async def create_room_rate(
    rate_data: RoomRateCreate,
    db: AsyncSession = Depends(get_db),
    _role: str = Depends(require_role(["admin"]))
):
    """
    สร้างอัตราค่าห้องใหม่

    **Business Rule**:
    - ช่วงวันที่ต้องไม่ซ้อนทับกับราคาที่มีอยู่แล้ว (สำหรับ room_type + stay_type เดียวกัน)
    - effective_to = NULL หมายถึงราคาปัจจุบันที่ไม่มีวันสิ้นสุด

    **สิทธิ์**: Admin เท่านั้น
    """
    service = RoomRateService(db)
    rate = await service.create(rate_data)

    return _serialize_rate(rate)


@router.patch("/{room_rate_id}", response_model=RoomRateWithRoomType)
async def update_room_rate(
    room_rate_id: int,
    rate_data: RoomRateUpdate,
    db: AsyncSession = Depends(get_db),
    _role: str = Depends(require_role(["admin"]))
):
    """
    แก้ไขอัตราค่าห้อง

    **Business Rule**:
    - ถ้าแก้ไข effective_to จะตรวจสอบว่าวันที่ไม่ซ้อนทับกับราคาอื่น

    **สิทธิ์**: Admin เท่านั้น
    """
    service = RoomRateService(db)
    rate = await service.update(room_rate_id, rate_data)

    return _serialize_rate(rate)


@router.delete("/{room_rate_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_room_rate(
    room_rate_id: int,
    db: AsyncSession = Depends(get_db),
    _role: str = Depends(require_role(["admin"]))
):
    """
    ลบอัตราค่าห้อง

    **Business Rule**: ไม่สามารถลบได้ถ้ามี bookings หรือ check-ins ที่อ้างอิง (TODO: Phase 3/4)

    **สิทธิ์**: Admin เท่านั้น
    """
    service = RoomRateService(db)
    await service.delete(room_rate_id)
    return None
