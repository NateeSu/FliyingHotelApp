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


class GeneralSettings(BaseModel):
    """General system settings"""
    frontend_domain: str = Field(default="http://localhost:5173", description="Frontend domain URL for Telegram links")
    hotel_name: str = Field(default="", description="Hotel name for receipts and documents")
    hotel_address: str = Field(default="", description="Hotel address for receipts and documents")
    hotel_phone: str = Field(default="", description="Hotel phone number for receipts and documents")
    temporary_stay_duration_hours: int = Field(default=3, ge=1, le=24, description="Temporary stay duration in hours")


class SystemSettingsResponse(BaseModel):
    """System settings response"""
    telegram: TelegramSettings
    general: GeneralSettings


class SystemSettingsUpdate(BaseModel):
    """System settings update request"""
    telegram: Optional[TelegramSettings] = None
    general: Optional[GeneralSettings] = None


class TelegramTestResponse(BaseModel):
    """Telegram test connection response"""
    success: bool
    message: str
    bot_info: Optional[Dict] = None
