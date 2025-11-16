from sqlalchemy import Column, Integer, String, Text, Enum, Boolean, ForeignKey, TIMESTAMP, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
import enum


class BreakerState(str, enum.Enum):
    """
    Breaker State Enum
    - ON: เปิด (breaker is on)
    - OFF: ปิด (breaker is off)
    - UNAVAILABLE: ไม่สามารถเชื่อมต่อได้ (unavailable in Home Assistant)
    """
    ON = "ON"
    OFF = "OFF"
    UNAVAILABLE = "UNAVAILABLE"


class BreakerAction(str, enum.Enum):
    """
    Breaker Action Enum
    - TURN_ON: สั่งเปิด
    - TURN_OFF: สั่งปิด
    - STATUS_SYNC: ตรวจสอบสถานะ
    """
    TURN_ON = "TURN_ON"
    TURN_OFF = "TURN_OFF"
    STATUS_SYNC = "STATUS_SYNC"


class TriggerType(str, enum.Enum):
    """
    Trigger Type Enum
    - AUTO: ระบบเปิด/ปิดอัตโนมัติ (based on room status)
    - MANUAL: ผู้ใช้กดเปิด/ปิดเอง
    - SYSTEM: ระบบภายใน (sync, maintenance, etc.)
    """
    AUTO = "AUTO"
    MANUAL = "MANUAL"
    SYSTEM = "SYSTEM"


class ActionStatus(str, enum.Enum):
    """
    Action Status Enum
    - SUCCESS: สำเร็จ
    - FAILED: ล้มเหลว
    - TIMEOUT: หมดเวลา
    """
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"


class QueueStatus(str, enum.Enum):
    """
    Queue Status Enum
    - PENDING: รอดำเนินการ
    - PROCESSING: กำลังดำเนินการ
    - COMPLETED: เสร็จสิ้น
    - FAILED: ล้มเหลว
    """
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class TargetState(str, enum.Enum):
    """
    Target State Enum (for queue)
    - ON: เป้าหมายคือเปิด
    - OFF: เป้าหมายคือปิด
    """
    ON = "ON"
    OFF = "OFF"


class HomeAssistantConfig(Base):
    """
    Home Assistant Configuration Model

    Stores the Home Assistant server connection details.
    Only one active configuration at a time.

    Security:
    - access_token is encrypted using Fernet encryption
    - Only ADMIN role can view/modify configuration
    """
    __tablename__ = "home_assistant_config"

    id = Column(Integer, primary_key=True, index=True)
    base_url = Column(String(255), nullable=False, comment="Home Assistant URL (e.g., http://192.168.1.100:8123)")
    access_token = Column(Text, nullable=False, comment="Long-Lived Access Token (encrypted with Fernet)")
    is_online = Column(Boolean, default=False, nullable=False, comment="Current connection status")
    last_ping_at = Column(TIMESTAMP, nullable=True, comment="Last successful ping timestamp")
    ha_version = Column(String(50), nullable=True, comment="Home Assistant version")
    is_active = Column(Boolean, default=True, nullable=False, comment="Configuration active status")
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<HomeAssistantConfig(id={self.id}, url='{self.base_url}', online={self.is_online})>"


class HomeAssistantBreaker(Base):
    """
    Home Assistant Breaker Model

    Represents a smart breaker device controlled through Home Assistant.
    Each breaker can be linked to one room for automatic control.

    Business Rules:
    - entity_id must be unique (e.g., switch.room_101_breaker)
    - One breaker per room (room_id is unique)
    - auto_control_enabled determines if room status changes trigger breaker control
    - consecutive_errors >= 3 triggers admin notification

    Relationships:
    - room: One-to-One with Room
    - activity_logs: One-to-Many with BreakerActivityLog
    - control_queue: One-to-Many with BreakerControlQueue
    """
    __tablename__ = "home_assistant_breakers"

    id = Column(Integer, primary_key=True, index=True)
    entity_id = Column(String(255), unique=True, nullable=False, index=True, comment="Home Assistant Entity ID (e.g., switch.room_101_breaker)")
    friendly_name = Column(String(255), nullable=False, comment="Human-readable name (e.g., Breaker ห้อง 101)")
    room_id = Column(Integer, ForeignKey("rooms.id", ondelete="SET NULL"), unique=True, nullable=True, index=True, comment="Linked room (one breaker per room)")
    auto_control_enabled = Column(Boolean, default=True, nullable=False, index=True, comment="Enable automatic control based on room status")
    is_available = Column(Boolean, default=False, nullable=False, comment="Breaker available in Home Assistant")
    current_state = Column(Enum(BreakerState), default=BreakerState.UNAVAILABLE, nullable=False, index=True, comment="Current breaker state")
    last_state_update = Column(TIMESTAMP, nullable=True, comment="Last state sync timestamp")
    ha_attributes = Column(JSON, nullable=True, comment="Additional attributes from Home Assistant")
    consecutive_errors = Column(Integer, default=0, nullable=False, comment="Number of consecutive command failures")
    last_error_message = Column(Text, nullable=True, comment="Last error message")
    is_active = Column(Boolean, default=True, nullable=False, comment="Breaker active status")
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    room = relationship("Room", foreign_keys=[room_id], backref="breaker")
    activity_logs = relationship("BreakerActivityLog", back_populates="breaker", cascade="all, delete-orphan")
    control_queue = relationship("BreakerControlQueue", back_populates="breaker", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<HomeAssistantBreaker(id={self.id}, entity='{self.entity_id}', room_id={self.room_id}, state='{self.current_state.value}')>"


class BreakerActivityLog(Base):
    """
    Breaker Activity Log Model

    Records all breaker actions for audit trail and analytics.
    Includes action details, trigger source, room status context, and performance metrics.

    Relationships:
    - breaker: Many-to-One with HomeAssistantBreaker
    - triggered_by_user: Many-to-One with User (optional)
    """
    __tablename__ = "breaker_activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    breaker_id = Column(Integer, ForeignKey("home_assistant_breakers.id", ondelete="CASCADE"), nullable=False, index=True, comment="Reference to home_assistant_breakers")
    action = Column(Enum(BreakerAction), nullable=False, comment="Action performed")
    trigger_type = Column(Enum(TriggerType), nullable=False, index=True, comment="How action was triggered")
    triggered_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="User ID who triggered (for MANUAL)")
    room_status_before = Column(String(50), nullable=True, comment="Room status before action")
    room_status_after = Column(String(50), nullable=True, comment="Room status after action")
    status = Column(Enum(ActionStatus), nullable=False, index=True, comment="Action result")
    error_message = Column(Text, nullable=True, comment="Error details if failed")
    response_time_ms = Column(Integer, nullable=True, comment="API response time in milliseconds")
    created_at = Column(TIMESTAMP, server_default=func.now(), index=True)

    # Relationships
    breaker = relationship("HomeAssistantBreaker", back_populates="activity_logs")
    triggered_by_user = relationship("User", foreign_keys=[triggered_by])

    def __repr__(self):
        return f"<BreakerActivityLog(id={self.id}, breaker_id={self.breaker_id}, action='{self.action.value}', status='{self.status.value}')>"


class BreakerControlQueue(Base):
    """
    Breaker Control Queue Model

    Queue for breaker control commands with retry logic and debouncing.
    Commands are scheduled for execution with priority and retry handling.

    Business Rules:
    - priority: 1=highest, 10=lowest (default=5)
    - max_retries: default 3 attempts
    - scheduled_at: supports debouncing (e.g., 3-second delay)
    - status transitions: PENDING → PROCESSING → COMPLETED/FAILED

    Relationships:
    - breaker: Many-to-One with HomeAssistantBreaker
    - triggered_by_user: Many-to-One with User (optional)
    """
    __tablename__ = "breaker_control_queue"

    id = Column(Integer, primary_key=True, index=True)
    breaker_id = Column(Integer, ForeignKey("home_assistant_breakers.id", ondelete="CASCADE"), nullable=False, index=True, comment="Reference to home_assistant_breakers")
    target_state = Column(Enum(TargetState), nullable=False, comment="Desired state")
    trigger_type = Column(Enum(TriggerType), nullable=False, comment="How command was triggered")
    triggered_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="User ID who triggered")
    priority = Column(Integer, default=5, nullable=False, index=True, comment="Command priority (1=highest, 10=lowest)")
    retry_count = Column(Integer, default=0, nullable=False, comment="Number of retry attempts")
    max_retries = Column(Integer, default=3, nullable=False, comment="Maximum retry attempts")
    scheduled_at = Column(TIMESTAMP, nullable=False, index=True, comment="When to execute command")
    status = Column(Enum(QueueStatus), default=QueueStatus.PENDING, nullable=False, index=True, comment="Queue item status")
    error_message = Column(Text, nullable=True, comment="Error details if failed")
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    breaker = relationship("HomeAssistantBreaker", back_populates="control_queue")
    triggered_by_user = relationship("User", foreign_keys=[triggered_by])

    def __repr__(self):
        return f"<BreakerControlQueue(id={self.id}, breaker_id={self.breaker_id}, target='{self.target_state.value}', status='{self.status.value}')>"
