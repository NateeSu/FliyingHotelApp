import logging
from typing import AsyncGenerator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.core.security import decode_access_token
from app.models import User

logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> int:
    """
    Get current user ID from JWT token
    """
    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ไม่สามารถยืนยันตัวตนได้",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id: Optional[int] = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ไม่พบข้อมูลผู้ใช้",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return int(user_id)


async def get_current_user_role(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    Get current user role from JWT token
    """
    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ไม่สามารถยืนยันตัวตนได้",
            headers={"WWW-Authenticate": "Bearer"},
        )

    role: Optional[str] = payload.get("role")
    if role is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ไม่พบข้อมูลสิทธิ์",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return role


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get current user from JWT token
    """
    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ไม่สามารถยืนยันตัวตนได้",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id: Optional[int] = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ไม่พบข้อมูลผู้ใช้",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user from database
    stmt = select(User).where(User.id == int(user_id))
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ไม่พบผู้ใช้ในระบบ",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        logger.warning("User %s is not active", user.username)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="บัญชีถูกระงับการใช้งาน",
        )

    logger.debug("Authenticated user=%s role=%s", user.username, user.role)
    return user


def require_role(allowed_roles: list[str]):
    """
    Dependency to check if user has required role
    Case-insensitive role comparison to handle both uppercase and lowercase roles
    """
    async def role_checker(role: str = Depends(get_current_user_role)) -> str:
        # Normalize both role and allowed_roles to lowercase for comparison
        normalized_role = role.lower()
        normalized_allowed = [r.lower() for r in allowed_roles]

        if normalized_role not in normalized_allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="คุณไม่มีสิทธิ์เข้าถึงส่วนนี้",
            )
        return role

    return role_checker


async def require_admin(
    user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to require admin role
    """
    from app.models.user import UserRole

    # Check if user role is ADMIN (case-insensitive comparison)
    # Handle both enum value and string from database
    user_role_str = user.role.value if hasattr(user.role, 'value') else str(user.role)

    if user_role_str.upper() != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="ต้องมีสิทธิ์ ADMIN เท่านั้น",
        )
    return user


async def require_admin_or_reception(
    user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to require admin or reception role
    """
    try:
        from app.models.user import UserRole

        # Check if user role is ADMIN or RECEPTION (case-insensitive comparison)
        # Handle both enum value and string from database
        user_role_str = user.role.value if hasattr(user.role, 'value') else str(user.role)

        if user_role_str.upper() not in ["ADMIN", "RECEPTION"]:
            logger.warning("Access denied for user=%s role=%s", user.username, user_role_str)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="ต้องมีสิทธิ์ ADMIN หรือ RECEPTION เท่านั้น",
            )

        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error in require_admin_or_reception")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="เกิดข้อผิดพลาดในการตรวจสอบสิทธิ์",
        )
