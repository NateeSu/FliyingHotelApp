"""
System Settings Model
Stores system configuration and settings
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SQLEnum
from datetime import datetime
import enum

from app.db.base import Base


class SettingDataTypeEnum(str, enum.Enum):
    """Setting data type enumeration"""
    STRING = "string"
    NUMBER = "number"
    JSON = "json"
    BOOLEAN = "boolean"


class SystemSetting(Base):
    """
    SystemSetting Model
    Stores system-wide settings and configuration
    """
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(255), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=True)
    data_type = Column(
        SQLEnum(SettingDataTypeEnum, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=SettingDataTypeEnum.STRING
    )
    description = Column(Text, nullable=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<SystemSetting(key={self.key}, value={self.value})>"
