from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash
from typing import List, Optional


class UserService:
    """Service for user management operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination"""
        result = await self.db.execute(
            select(User).offset(skip).limit(limit).order_by(User.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def create_user(self, user_data: UserCreate) -> User:
        """Create new user"""
        # Check if username already exists
        existing_user = await self.get_user_by_username(user_data.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ชื่อผู้ใช้นี้มีอยู่ในระบบแล้ว"
            )

        # Create new user
        user = User(
            username=user_data.username,
            password_hash=get_password_hash(user_data.password),
            full_name=user_data.full_name,
            role=user_data.role,
            telegram_user_id=user_data.telegram_user_id,
        )

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        """Update existing user"""
        user = await self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="ไม่พบผู้ใช้นี้ในระบบ"
            )

        # Update fields if provided
        if user_data.full_name is not None:
            user.full_name = user_data.full_name

        if user_data.role is not None:
            user.role = user_data.role

        if user_data.telegram_user_id is not None:
            user.telegram_user_id = user_data.telegram_user_id

        if user_data.is_active is not None:
            user.is_active = user_data.is_active

        if user_data.password is not None:
            user.password_hash = get_password_hash(user_data.password)

        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def delete_user(self, user_id: int) -> bool:
        """Delete user (soft delete by setting is_active=False)"""
        user = await self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="ไม่พบผู้ใช้นี้ในระบบ"
            )

        # Soft delete
        user.is_active = False
        await self.db.commit()

        return True
