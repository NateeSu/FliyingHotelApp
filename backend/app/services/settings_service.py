"""
Settings Service
Business logic for system settings management
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Optional
import json

from app.models.system_setting import SystemSetting, SettingDataTypeEnum
from app.schemas.settings import TelegramSettings, SystemSettingsResponse


class SettingsService:
    """Service for managing system settings"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_setting(self, key: str) -> Optional[str]:
        """Get a single setting value by key"""
        result = await self.db.execute(
            select(SystemSetting).where(SystemSetting.key == key)
        )
        setting = result.scalar_one_or_none()
        return setting.value if setting else None

    async def set_setting(self, key: str, value: str, data_type: SettingDataTypeEnum = SettingDataTypeEnum.STRING):
        """Set a setting value"""
        result = await self.db.execute(
            select(SystemSetting).where(SystemSetting.key == key)
        )
        setting = result.scalar_one_or_none()

        if setting:
            setting.value = value
            setting.data_type = data_type
        else:
            setting = SystemSetting(
                key=key,
                value=value,
                data_type=data_type
            )
            self.db.add(setting)

        await self.db.commit()
        await self.db.refresh(setting)
        return setting

    async def get_telegram_settings(self) -> TelegramSettings:
        """Get Telegram integration settings"""
        bot_token = await self.get_setting("telegram_bot_token") or ""
        admin_chat_id = await self.get_setting("telegram_admin_chat_id") or ""
        reception_chat_id = await self.get_setting("telegram_reception_chat_id") or ""
        housekeeping_chat_id = await self.get_setting("telegram_housekeeping_chat_id") or ""
        maintenance_chat_id = await self.get_setting("telegram_maintenance_chat_id") or ""
        enabled_str = await self.get_setting("telegram_enabled") or "false"
        enabled = enabled_str.lower() == "true"

        return TelegramSettings(
            bot_token=bot_token,
            admin_chat_id=admin_chat_id,
            reception_chat_id=reception_chat_id,
            housekeeping_chat_id=housekeeping_chat_id,
            maintenance_chat_id=maintenance_chat_id,
            enabled=enabled
        )

    async def update_telegram_settings(self, settings: TelegramSettings):
        """Update Telegram integration settings"""
        await self.set_setting("telegram_bot_token", settings.bot_token, SettingDataTypeEnum.STRING)
        await self.set_setting("telegram_admin_chat_id", settings.admin_chat_id, SettingDataTypeEnum.STRING)
        await self.set_setting("telegram_reception_chat_id", settings.reception_chat_id, SettingDataTypeEnum.STRING)
        await self.set_setting("telegram_housekeeping_chat_id", settings.housekeeping_chat_id, SettingDataTypeEnum.STRING)
        await self.set_setting("telegram_maintenance_chat_id", settings.maintenance_chat_id, SettingDataTypeEnum.STRING)
        await self.set_setting("telegram_enabled", "true" if settings.enabled else "false", SettingDataTypeEnum.BOOLEAN)

    async def get_all_settings(self) -> SystemSettingsResponse:
        """Get all system settings"""
        telegram = await self.get_telegram_settings()

        return SystemSettingsResponse(
            telegram=telegram
        )
