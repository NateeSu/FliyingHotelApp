from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.dependencies import get_db, require_role
from app.services.user_service import UserService
from app.schemas.user import UserCreate, UserUpdate, UserResponse

router = APIRouter()


@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    _role: str = Depends(require_role(["admin"])),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all users (Admin only)

    - **skip**: จำนวนแถวที่ข้าม (สำหรับ pagination)
    - **limit**: จำนวนแถวสูงสุดที่ต้องการ
    """
    user_service = UserService(db)
    users = await user_service.get_all_users(skip=skip, limit=limit)
    return [UserResponse.model_validate(user) for user in users]


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    _role: str = Depends(require_role(["admin"])),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user by ID (Admin only)
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ไม่พบผู้ใช้นี้ในระบบ"
        )

    return UserResponse.model_validate(user)


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    _role: str = Depends(require_role(["admin"])),
    db: AsyncSession = Depends(get_db)
):
    """
    Create new user (Admin only)
    """
    user_service = UserService(db)
    user = await user_service.create_user(user_data)
    return UserResponse.model_validate(user)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    _role: str = Depends(require_role(["admin"])),
    db: AsyncSession = Depends(get_db)
):
    """
    Update user (Admin only)
    """
    user_service = UserService(db)
    user = await user_service.update_user(user_id, user_data)
    return UserResponse.model_validate(user)


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    _role: str = Depends(require_role(["admin"])),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete user (Admin only) - Soft delete
    """
    user_service = UserService(db)
    await user_service.delete_user(user_id)
    return {"message": "ลบผู้ใช้สำเร็จ"}
