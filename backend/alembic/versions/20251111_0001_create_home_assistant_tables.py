"""Create Home Assistant integration tables

Revision ID: create_home_assistant_tables
Revises: maintenance_desc_optional
Create Date: 2025-11-11 00:01:00.000000+07:00

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'create_home_assistant_tables'
down_revision: Union[str, None] = 'maintenance_desc_optional'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create home_assistant_config table
    op.create_table(
        'home_assistant_config',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('base_url', sa.String(255), nullable=False, comment='Home Assistant URL (e.g., http://192.168.1.100:8123)'),
        sa.Column('access_token', sa.Text(), nullable=False, comment='Long-Lived Access Token (encrypted with Fernet)'),
        sa.Column('is_online', sa.Boolean(), nullable=False, server_default='0', comment='Current connection status'),
        sa.Column('last_ping_at', sa.DateTime(), nullable=True, comment='Last successful ping timestamp'),
        sa.Column('ha_version', sa.String(50), nullable=True, comment='Home Assistant version'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1', comment='Configuration active status'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )

    # Create home_assistant_breakers table
    op.create_table(
        'home_assistant_breakers',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('entity_id', sa.String(255), nullable=False, unique=True, comment='Home Assistant Entity ID (e.g., switch.room_101_breaker)'),
        sa.Column('friendly_name', sa.String(255), nullable=False, comment='Human-readable name (e.g., Breaker ห้อง 101)'),
        sa.Column('room_id', sa.Integer(), nullable=True, unique=True, comment='Linked room (one breaker per room)'),
        sa.Column('auto_control_enabled', sa.Boolean(), nullable=False, server_default='1', comment='Enable automatic control based on room status'),
        sa.Column('is_available', sa.Boolean(), nullable=False, server_default='0', comment='Breaker available in Home Assistant'),
        sa.Column('current_state', sa.Enum('ON', 'OFF', 'UNAVAILABLE', name='breaker_state'), nullable=False, server_default='UNAVAILABLE', comment='Current breaker state'),
        sa.Column('last_state_update', sa.DateTime(), nullable=True, comment='Last state sync timestamp'),
        sa.Column('ha_attributes', sa.JSON(), nullable=True, comment='Additional attributes from Home Assistant'),
        sa.Column('consecutive_errors', sa.Integer(), nullable=False, server_default='0', comment='Number of consecutive command failures'),
        sa.Column('last_error_message', sa.Text(), nullable=True, comment='Last error message'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1', comment='Breaker active status'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['room_id'], ['rooms.id'], ondelete='SET NULL'),
        sa.Index('idx_breaker_entity_id', 'entity_id'),
        sa.Index('idx_breaker_room_id', 'room_id'),
        sa.Index('idx_breaker_state', 'current_state'),
        sa.Index('idx_breaker_auto_control', 'auto_control_enabled'),
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )

    # Create breaker_activity_logs table
    op.create_table(
        'breaker_activity_logs',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('breaker_id', sa.Integer(), nullable=False, comment='Reference to home_assistant_breakers'),
        sa.Column('action', sa.Enum('TURN_ON', 'TURN_OFF', 'STATUS_SYNC', name='breaker_action'), nullable=False, comment='Action performed'),
        sa.Column('trigger_type', sa.Enum('AUTO', 'MANUAL', 'SYSTEM', name='trigger_type'), nullable=False, comment='How action was triggered'),
        sa.Column('triggered_by', sa.Integer(), nullable=True, comment='User ID who triggered (for MANUAL)'),
        sa.Column('room_status_before', sa.String(50), nullable=True, comment='Room status before action'),
        sa.Column('room_status_after', sa.String(50), nullable=True, comment='Room status after action'),
        sa.Column('status', sa.Enum('SUCCESS', 'FAILED', 'TIMEOUT', name='action_status'), nullable=False, comment='Action result'),
        sa.Column('error_message', sa.Text(), nullable=True, comment='Error details if failed'),
        sa.Column('response_time_ms', sa.Integer(), nullable=True, comment='API response time in milliseconds'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['breaker_id'], ['home_assistant_breakers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['triggered_by'], ['users.id'], ondelete='SET NULL'),
        sa.Index('idx_activity_breaker_id', 'breaker_id'),
        sa.Index('idx_activity_created_at', 'created_at'),
        sa.Index('idx_activity_trigger_type', 'trigger_type'),
        sa.Index('idx_activity_status', 'status'),
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )

    # Create breaker_control_queue table
    op.create_table(
        'breaker_control_queue',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('breaker_id', sa.Integer(), nullable=False, comment='Reference to home_assistant_breakers'),
        sa.Column('target_state', sa.Enum('ON', 'OFF', name='target_state'), nullable=False, comment='Desired state'),
        sa.Column('trigger_type', sa.Enum('AUTO', 'MANUAL', 'SYSTEM', name='queue_trigger_type'), nullable=False, comment='How command was triggered'),
        sa.Column('triggered_by', sa.Integer(), nullable=True, comment='User ID who triggered'),
        sa.Column('priority', sa.Integer(), nullable=False, server_default='5', comment='Command priority (1=highest, 10=lowest)'),
        sa.Column('retry_count', sa.Integer(), nullable=False, server_default='0', comment='Number of retry attempts'),
        sa.Column('max_retries', sa.Integer(), nullable=False, server_default='3', comment='Maximum retry attempts'),
        sa.Column('scheduled_at', sa.DateTime(), nullable=False, comment='When to execute command'),
        sa.Column('status', sa.Enum('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED', name='queue_status'), nullable=False, server_default='PENDING', comment='Queue item status'),
        sa.Column('error_message', sa.Text(), nullable=True, comment='Error details if failed'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['breaker_id'], ['home_assistant_breakers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['triggered_by'], ['users.id'], ondelete='SET NULL'),
        sa.Index('idx_queue_breaker_id', 'breaker_id'),
        sa.Index('idx_queue_status', 'status'),
        sa.Index('idx_queue_scheduled_at', 'scheduled_at'),
        sa.Index('idx_queue_priority', 'priority'),
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )


def downgrade() -> None:
    # Drop tables in reverse order (due to foreign keys)
    op.drop_table('breaker_control_queue')
    op.drop_table('breaker_activity_logs')
    op.drop_table('home_assistant_breakers')
    op.drop_table('home_assistant_config')
