from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from app.models.user import UserRole


# Base schema with common fields
class UserBase(BaseModel):
    """Base user schema"""
    username: str = Field(..., min_length=3, max_length=50, description="ชื่อผู้ใช้")
    full_name: str = Field(..., min_length=1, max_length=100, description="ชื่อ-นามสกุล")
    role: UserRole = Field(..., description="บทบาท")
    telegram_user_id: Optional[str] = Field(None, max_length=50, description="Telegram User ID")


# Schema for creating new user
class UserCreate(UserBase):
    """Schema for creating new user"""
    password: str = Field(..., min_length=6, max_length=100, description="รหัสผ่าน")


# Schema for updating user
class UserUpdate(BaseModel):
    """Schema for updating user"""
    full_name: Optional[str] = Field(None, min_length=1, max_length=100, description="ชื่อ-นามสกุล")
    role: Optional[UserRole] = Field(None, description="บทบาท")
    telegram_user_id: Optional[str] = Field(None, max_length=50, description="Telegram User ID")
    is_active: Optional[bool] = Field(None, description="สถานะการใช้งาน")
    password: Optional[str] = Field(None, min_length=6, max_length=100, description="รหัสผ่าน (ถ้าต้องการเปลี่ยน)")


# Schema for user response
class UserResponse(UserBase):
    """Schema for user response"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Schema for login request
class LoginRequest(BaseModel):
    """Schema for login request"""
    username: str = Field(..., description="ชื่อผู้ใช้")
    password: str = Field(..., description="รหัสผ่าน")


# Schema for login response
class LoginResponse(BaseModel):
    """Schema for login response"""
    access_token: str = Field(..., description="Access Token")
    token_type: str = Field(default="bearer", description="Token Type")
    user: UserResponse = Field(..., description="ข้อมูลผู้ใช้")


# Schema for token payload
class TokenPayload(BaseModel):
    """Schema for JWT token payload"""
    sub: int = Field(..., description="User ID")
    role: str = Field(..., description="User Role")
    exp: Optional[datetime] = Field(None, description="Expiration time")


# Schema for profile update
class ProfileUpdate(BaseModel):
    """Schema for updating user profile"""
    full_name: str = Field(..., min_length=1, max_length=100, description="ชื่อ-นามสกุล")


# Schema for password change
class PasswordChange(BaseModel):
    """Schema for changing password"""
    current_password: str = Field(..., description="รหัสผ่านปัจจุบัน")
    new_password: str = Field(..., min_length=6, max_length=100, description="รหัสผ่านใหม่")
