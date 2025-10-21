"""
Settings API Endpoints (Phase 5.1)
System settings management including Telegram integration
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, require_admin, get_db
from app.schemas.settings import (
    SystemSettingsResponse,
    SystemSettingsUpdate,
    TelegramTestResponse
)
from app.services.settings_service import SettingsService
from app.services.telegram_service import TelegramService
from app.models.user import User

router = APIRouter()


@router.get("", response_model=SystemSettingsResponse)
async def get_settings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Get all system settings (Admin only)
    """
    service = SettingsService(db)
    settings = await service.get_all_settings()
    return settings


@router.put("", response_model=SystemSettingsResponse)
async def update_settings(
    settings_update: SystemSettingsUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Update system settings (Admin only)
    """
    service = SettingsService(db)

    # Update Telegram settings if provided
    if settings_update.telegram:
        await service.update_telegram_settings(settings_update.telegram)

    # Return updated settings
    settings = await service.get_all_settings()
    return settings


@router.post("/test-telegram", response_model=TelegramTestResponse)
async def test_telegram_connection(
    bot_token: str,
    chat_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Test Telegram bot connection (Admin only)

    Args:
        bot_token: Telegram Bot API Token
        chat_id: Chat ID to send test message to

    Returns:
        Test result with bot information
    """
    telegram_service = TelegramService(db)

    success, message, bot_info = await telegram_service.test_connection(bot_token, chat_id)

    return TelegramTestResponse(
        success=success,
        message=message,
        bot_info=bot_info
    )
