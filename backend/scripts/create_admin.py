"""
Script to create admin user
Usage: python scripts/create_admin.py
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from sqlalchemy import select


async def create_admin_user():
    """Create admin user if not exists"""

    # Create async engine
    engine = create_async_engine(settings.DATABASE_URL, echo=True)

    # Create session factory
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        # Check if admin already exists
        result = await session.execute(
            select(User).where(User.username == "admin")
        )
        existing_admin = result.scalar_one_or_none()

        if existing_admin:
            print("❌ Admin user already exists!")
            return

        # Create admin user
        admin = User(
            username="admin",
            password_hash=get_password_hash("admin123"),  # Default password
            full_name="ผู้ดูแลระบบ",
            role=UserRole.ADMIN,
            is_active=True,
        )

        session.add(admin)
        await session.commit()

        print("✅ Admin user created successfully!")
        print(f"   Username: admin")
        print(f"   Password: admin123")
        print(f"   ⚠️  Please change the password after first login!")


if __name__ == "__main__":
    asyncio.run(create_admin_user())
