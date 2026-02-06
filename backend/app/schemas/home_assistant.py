"""
Home Assistant Integration Schemas
Pydantic models for Home Assistant breaker control API validation
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime

from app.models.home_assistant import (
    BreakerState,
    BreakerAction,
    TriggerType,
    ActionStatus,
    QueueStatus,
    TargetState
)

# Type aliases for backward compatibility (schema previously used *Enum suffix)
BreakerStateEnum = BreakerState
BreakerActionEnum = BreakerAction
TriggerTypeEnum = TriggerType
ActionStatusEnum = ActionStatus
QueueStatusEnum = QueueStatus
TargetStateEnum = TargetState


# ============================================================================
# Home Assistant Configuration Schemas
# ============================================================================

class HomeAssistantConfigCreate(BaseModel):
    """Create Home Assistant configuration"""
    base_url: str = Field(..., description="Home Assistant URL (e.g., http://192.168.1.100:8123)")
    access_token: str = Field(..., description="Long-Lived Access Token")

    @validator('base_url')
    def validate_base_url(cls, v):
        """Validate base URL format"""
        if not v.startswith(('http://', 'https://')):
            raise ValueError('base_url must start with http:// or https://')
        if v.endswith('/'):
            v = v[:-1]  # Remove trailing slash
        return v

    @validator('access_token')
    def validate_access_token(cls, v):
        """Validate token is not empty"""
        if not v or len(v.strip()) < 10:
            raise ValueError('access_token must be at least 10 characters')
        return v.strip()


class HomeAssistantConfigUpdate(BaseModel):
    """Update Home Assistant configuration"""
    base_url: Optional[str] = Field(None, description="Home Assistant URL")
    access_token: Optional[str] = Field(None, description="Long-Lived Access Token")

    @validator('base_url')
    def validate_base_url(cls, v):
        if v is not None:
            if not v.startswith(('http://', 'https://')):
                raise ValueError('base_url must start with http:// or https://')
            if v.endswith('/'):
                v = v[:-1]
        return v

    @validator('access_token')
    def validate_access_token(cls, v):
        if v is not None and (not v or len(v.strip()) < 10):
            raise ValueError('access_token must be at least 10 characters')
        return v.strip() if v else None


class HomeAssistantConfigResponse(BaseModel):
    """Home Assistant configuration response"""
    id: int
    base_url: str
    access_token_masked: str = Field(..., description="Masked token (e.g., ey...abc)")
    is_online: bool
    last_ping_at: Optional[datetime]
    ha_version: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class HomeAssistantTestConnectionRequest(BaseModel):
    """Test Home Assistant connection without saving"""
    base_url: str = Field(..., description="Home Assistant URL to test")
    access_token: str = Field(..., description="Access token to test")

    @validator('base_url')
    def validate_base_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('base_url must start with http:// or https://')
        if v.endswith('/'):
            v = v[:-1]
        return v


class HomeAssistantTestConnectionResponse(BaseModel):
    """Test connection response"""
    success: bool
    message: str
    ha_version: Optional[str] = None
    entity_count: Optional[int] = None
    response_time_ms: Optional[int] = None


class HomeAssistantStatusResponse(BaseModel):
    """Home Assistant connection status"""
    is_configured: bool
    is_online: bool
    last_ping_at: Optional[datetime]
    ha_version: Optional[str]
    base_url: Optional[str]


class HomeAssistantEntityResponse(BaseModel):
    """Home Assistant entity information"""
    entity_id: str
    friendly_name: Optional[str]
    state: str
    attributes: Optional[Dict[str, Any]]


class HomeAssistantEntitiesResponse(BaseModel):
    """List of Home Assistant entities"""
    entities: List[HomeAssistantEntityResponse]
    total: int


# ============================================================================
# Breaker Management Schemas
# ============================================================================

class BreakerCreate(BaseModel):
    """Create breaker"""
    entity_id: str = Field(..., description="Home Assistant Entity ID (e.g., switch.room_101_breaker)")
    friendly_name: str = Field(..., description="Human-readable name")
    room_id: Optional[int] = Field(None, description="Linked room ID")
    auto_control_enabled: bool = Field(True, description="Enable automatic control")

    @validator('entity_id')
    def validate_entity_id(cls, v):
        """Validate entity_id format"""
        if not v or '.' not in v:
            raise ValueError('entity_id must be in format: domain.entity_name (e.g., switch.room_101)')
        return v.strip()

    @validator('friendly_name')
    def validate_friendly_name(cls, v):
        """Validate friendly_name is not empty"""
        if not v or len(v.strip()) < 3:
            raise ValueError('friendly_name must be at least 3 characters')
        return v.strip()


class BreakerUpdate(BaseModel):
    """Update breaker"""
    entity_id: Optional[str] = Field(None, description="Home Assistant Entity ID")
    friendly_name: Optional[str] = Field(None, description="Human-readable name")
    room_id: Optional[int] = Field(None, description="Linked room ID")
    auto_control_enabled: Optional[bool] = Field(None, description="Enable automatic control")

    @validator('entity_id')
    def validate_entity_id(cls, v):
        if v is not None:
            if not v or '.' not in v:
                raise ValueError('entity_id must be in format: domain.entity_name')
        return v.strip() if v else None

    @validator('friendly_name')
    def validate_friendly_name(cls, v):
        if v is not None and (not v or len(v.strip()) < 3):
            raise ValueError('friendly_name must be at least 3 characters')
        return v.strip() if v else None


class BreakerResponse(BaseModel):
    """Breaker response"""
    id: int
    entity_id: str
    friendly_name: str
    room_id: Optional[int]
    room_number: Optional[str] = None
    room_status: Optional[str] = None
    auto_control_enabled: bool
    is_available: bool
    current_state: BreakerStateEnum
    last_state_update: Optional[datetime]
    consecutive_errors: int
    last_error_message: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BreakerListResponse(BaseModel):
    """List of breakers"""
    breakers: List[BreakerResponse]
    total: int


class BreakerControlRequest(BaseModel):
    """Manual control breaker"""
    reason: Optional[str] = Field(None, description="Reason for manual control (optional)")


class BreakerControlResponse(BaseModel):
    """Breaker control response"""
    success: bool
    message: str
    breaker_id: int
    new_state: BreakerStateEnum
    response_time_ms: Optional[int]


class BreakerSyncResponse(BaseModel):
    """Breaker sync response"""
    success: bool
    message: str
    breaker_id: int
    current_state: BreakerStateEnum
    is_available: bool
    synced_at: datetime
    consecutive_errors: int = 0
    last_error_message: Optional[str] = None


# ============================================================================
# Activity Log Schemas
# ============================================================================

class BreakerActivityLogResponse(BaseModel):
    """Breaker activity log response"""
    id: int
    breaker_id: int
    entity_id: str
    friendly_name: str
    action: BreakerActionEnum
    trigger_type: TriggerTypeEnum
    triggered_by: Optional[int]
    triggered_by_name: Optional[str] = None
    room_status_before: Optional[str]
    room_status_after: Optional[str]
    status: ActionStatusEnum
    error_message: Optional[str]
    response_time_ms: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class BreakerActivityLogListResponse(BaseModel):
    """List of activity logs"""
    logs: List[BreakerActivityLogResponse]
    total: int


class BreakerActivityLogFilter(BaseModel):
    """Activity log filter parameters"""
    breaker_id: Optional[int] = None
    action: Optional[BreakerActionEnum] = None
    trigger_type: Optional[TriggerTypeEnum] = None
    status: Optional[ActionStatusEnum] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = Field(50, ge=1, le=500)
    offset: int = Field(0, ge=0)


# ============================================================================
# Statistics & Reports Schemas
# ============================================================================

class BreakerStatistics(BaseModel):
    """Breaker statistics"""
    total_breakers: int
    online_breakers: int
    offline_breakers: int
    breakers_on: int
    breakers_off: int
    auto_control_enabled: int
    breakers_with_errors: int
    total_actions_today: int
    success_rate_today: float
    avg_response_time_ms: Optional[float]


class BreakerEnergyReport(BaseModel):
    """Breaker energy usage report"""
    breaker_id: int
    entity_id: str
    friendly_name: str
    room_number: Optional[str]
    total_on_time_hours: float
    total_actions: int
    auto_actions: int
    manual_actions: int
    success_rate: float
    last_7_days: List[Dict[str, Any]]  # Daily breakdown


class BreakerEnergyReportResponse(BaseModel):
    """Energy report response"""
    report: BreakerEnergyReport
    generated_at: datetime


# ============================================================================
# Control Queue Schemas
# ============================================================================

class BreakerControlQueueResponse(BaseModel):
    """Control queue item response"""
    id: int
    breaker_id: int
    entity_id: str
    target_state: TargetStateEnum
    trigger_type: TriggerTypeEnum
    triggered_by: Optional[int]
    priority: int
    retry_count: int
    max_retries: int
    scheduled_at: datetime
    status: QueueStatusEnum
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BreakerControlQueueListResponse(BaseModel):
    """List of queue items"""
    queue_items: List[BreakerControlQueueResponse]
    total: int
