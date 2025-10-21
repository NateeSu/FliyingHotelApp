"""
System Settings Schemas
Pydantic models for system settings API validation
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict


class TelegramSettings(BaseModel):
    """Telegram integration settings"""
    bot_token: str = Field(default="", description="Telegram Bot API Token")
    admin_chat_id: str = Field(default="", description="Admin Group Chat ID")
    reception_chat_id: str = Field(default="", description="Reception Group Chat ID")
    housekeeping_chat_id: str = Field(default="", description="Housekeeping Group Chat ID")
    maintenance_chat_id: str = Field(default="", description="Maintenance Group Chat ID")
    enabled: bool = Field(default=False, description="Enable/Disable Telegram notifications")


class SystemSettingsResponse(BaseModel):
    """System settings response"""
    telegram: TelegramSettings


class SystemSettingsUpdate(BaseModel):
    """System settings update request"""
    telegram: Optional[TelegramSettings] = None


class TelegramTestResponse(BaseModel):
    """Telegram test connection response"""
    success: bool
    message: str
    bot_info: Optional[Dict] = None
