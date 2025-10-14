from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.core.dependencies import get_db, require_role, get_current_user_id
from app.services.room_service import RoomService
from app.schemas.room import RoomCreate, RoomUpdate, RoomResponse, RoomWithRoomType, RoomStatusUpdate
from app.models.room import RoomStatus, Room

router = APIRouter()


def _serialize_room_with_type(room: Room) -> dict:
    """Helper to serialize Room with RoomType to dict"""
    room_dict = {
        "id": room.id,
        "room_number": room.room_number,
        "room_type_id": room.room_type_id,
        "floor": room.floor,
        "status": room.status,
        "qr_code": room.qr_code,
        "notes": room.notes,
        "is_active": room.is_active,
        "created_at": room.created_at,
        "updated_at": room.updated_at,
        "room_type": None
    }

    if room.room_type:
        room_dict["room_type"] = {
            "id": room.room_type.id,
            "name": room.room_type.name,
            "description": room.room_type.description,
            "amenities": room.room_type.amenities,
            "max_guests": room.room_type.max_guests,
            "bed_type": room.room_type.bed_type,
            "room_size_sqm": room.room_type.room_size_sqm,
            "is_active": room.room_type.is_active,
            "created_at": room.room_type.created_at,
            "updated_at": room.room_type.updated_at,
        }

    return room_dict


@router.get("/", response_model=List[RoomWithRoomType])
async def get_rooms(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    floor: Optional[int] = Query(None, ge=1),
    status: Optional[RoomStatus] = None,
    room_type_id: Optional[int] = Query(None, gt=0),
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    _current_user_id: int = Depends(get_current_user_id)
):
    """
    รายการห้องพักทั้งหมด พร้อมข้อมูลประเภทห้อง

    - **skip**: จำนวนแถวที่ข้าม (สำหรับ pagination)
    - **limit**: จำนวนแถวสูงสุดที่ต้องการ
    - **floor**: กรองตามชั้น
    - **status**: กรองตามสถานะห้อง (available, occupied, cleaning, reserved, out_of_service)
    - **room_type_id**: กรองตามประเภทห้อง
    - **is_active**: กรองตามสถานะการใช้งาน

    **สิทธิ์**: ทุก role ที่ login แล้วสามารถดูได้
    """
    service = RoomService(db)
    rooms = await service.get_all(
        skip=skip,
        limit=limit,
        floor=floor,
        status=status,
        room_type_id=room_type_id,
        is_active=is_active
    )

    # Convert to RoomWithRoomType response
    return [RoomWithRoomType(**_serialize_room_with_type(room)) for room in rooms]


@router.get("/available", response_model=List[RoomWithRoomType])
async def get_available_rooms(
    room_type_id: Optional[int] = Query(None, gt=0),
    db: AsyncSession = Depends(get_db),
    _current_user_id: int = Depends(get_current_user_id)
):
    """
    รายการห้องว่าง (status = available)

    - **room_type_id**: กรองตามประเภทห้อง (optional)

    **สิทธิ์**: ทุก role ที่ login แล้วสามารถดูได้
    """
    service = RoomService(db)
    rooms = await service.get_available_rooms(room_type_id=room_type_id)

    return [RoomWithRoomType(**_serialize_room_with_type(room)) for room in rooms]


@router.get("/floor/{floor}", response_model=List[RoomWithRoomType])
async def get_rooms_by_floor(
    floor: int,
    db: AsyncSession = Depends(get_db),
    _current_user_id: int = Depends(get_current_user_id)
):
    """
    รายการห้องพักตามชั้น

    **สิทธิ์**: ทุก role ที่ login แล้วสามารถดูได้
    """
    service = RoomService(db)
    rooms = await service.get_rooms_by_floor(floor)

    return [RoomWithRoomType(**_serialize_room_with_type(room)) for room in rooms]


@router.get("/{room_id}", response_model=RoomWithRoomType)
async def get_room(
    room_id: int,
    db: AsyncSession = Depends(get_db),
    _current_user_id: int = Depends(get_current_user_id)
):
    """
    ดึงข้อมูลห้องพักตาม ID พร้อมข้อมูลประเภทห้อง

    **สิทธิ์**: ทุก role ที่ login แล้วสามารถดูได้
    """
    service = RoomService(db)
    room = await service.get_by_id(room_id)

    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ไม่พบห้องพัก"
        )

    return RoomWithRoomType(**_serialize_room_with_type(room))


@router.post("/", response_model=RoomWithRoomType, status_code=status.HTTP_201_CREATED)
async def create_room(
    room_data: RoomCreate,
    db: AsyncSession = Depends(get_db),
    _role: str = Depends(require_role(["admin"]))
):
    """
    สร้างห้องพักใหม่

    - QR Code จะถูกสร้างอัตโนมัติ
    - สถานะเริ่มต้นเป็น "available"

    **สิทธิ์**: Admin เท่านั้น
    """
    service = RoomService(db)
    room = await service.create(room_data)

    return RoomWithRoomType(**_serialize_room_with_type(room))


@router.patch("/{room_id}", response_model=RoomWithRoomType)
async def update_room(
    room_id: int,
    room_data: RoomUpdate,
    db: AsyncSession = Depends(get_db),
    _role: str = Depends(require_role(["admin"]))
):
    """
    แก้ไขข้อมูลห้องพัก

    **Business Rule**: ไม่สามารถเปลี่ยนประเภทห้องได้ถ้าห้องมีผู้พักหรือจองแล้ว

    **สิทธิ์**: Admin เท่านั้น
    """
    service = RoomService(db)
    room = await service.update(room_id, room_data)

    return RoomWithRoomType(**_serialize_room_with_type(room))


@router.patch("/{room_id}/status", response_model=RoomWithRoomType)
async def update_room_status(
    room_id: int,
    status_data: RoomStatusUpdate,
    db: AsyncSession = Depends(get_db),
    _role: str = Depends(require_role(["admin", "reception", "housekeeping"]))
):
    """
    อัปเดตสถานะห้องพัก

    Endpoint นี้จะถูกใช้งานบ่อยโดย:
    - Reception: เปลี่ยนสถานะเมื่อ check-in/check-out
    - Housekeeping: เปลี่ยนสถานะเมื่อเริ่ม/เสร็จการทำความสะอาด
    - Admin: เปลี่ยนสถานะใดก็ได้

    **สิทธิ์**: Admin, Reception, Housekeeping
    """
    service = RoomService(db)
    room = await service.update_status(room_id, status_data.status)

    return RoomWithRoomType(**_serialize_room_with_type(room))


@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_room(
    room_id: int,
    db: AsyncSession = Depends(get_db),
    _role: str = Depends(require_role(["admin"]))
):
    """
    ลบห้องพัก

    **Business Rule**: ไม่สามารถลบได้ถ้าห้องมีผู้พักหรือจองแล้ว

    **สิทธิ์**: Admin เท่านั้น
    """
    service = RoomService(db)
    await service.delete(room_id)
    return None
