from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db, get_current_user_id
from app.services.auth_service import AuthService
from app.schemas.user import LoginRequest, LoginResponse, UserResponse, ProfileUpdate, PasswordChange

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Login endpoint

    - **username**: ชื่อผู้ใช้
    - **password**: รหัสผ่าน

    Returns access token and user data
    """
    auth_service = AuthService(db)
    access_token, user = await auth_service.login(login_data)

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )


@router.post("/logout")
async def logout():
    """
    Logout endpoint (client should remove token)
    """
    return {"message": "ออกจากระบบสำเร็จ"}


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current logged-in user information
    """
    auth_service = AuthService(db)
    user = await auth_service.get_user_by_id(current_user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ไม่พบข้อมูลผู้ใช้"
        )

    return UserResponse.model_validate(user)


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    profile_data: ProfileUpdate,
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Update current user's profile (full_name)

    - **full_name**: ชื่อ-นามสกุล
    """
    auth_service = AuthService(db)
    user = await auth_service.update_profile(current_user_id, profile_data.full_name)
    return UserResponse.model_validate(user)


@router.post("/change-password", response_model=UserResponse)
async def change_password(
    password_data: PasswordChange,
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Change current user's password

    - **current_password**: รหัสผ่านปัจจุบัน
    - **new_password**: รหัสผ่านใหม่
    """
    auth_service = AuthService(db)
    user = await auth_service.change_password(
        current_user_id,
        password_data.current_password,
        password_data.new_password
    )
    return UserResponse.model_validate(user)
