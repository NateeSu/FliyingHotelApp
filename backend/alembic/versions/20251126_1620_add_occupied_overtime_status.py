"""add occupied_overtime status to rooms

Revision ID: 20251126_1620
Revises: 6bdc7fb2217d
Create Date: 2025-11-26 16:20:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '20251126_1620'
down_revision: Union[str, None] = '6bdc7fb2217d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Add OCCUPIED_OVERTIME status to rooms.status enum

    This status is used for temporary stays that have exceeded their 3-hour limit.
    When a room enters this status:
    - The smart breaker is automatically turned OFF
    - Frontend displays "หมดเวลาเข้าพัก" warning
    - Telegram notification is sent to reception/admin
    """
    # Modify the enum to include OCCUPIED_OVERTIME
    op.execute("""
        ALTER TABLE rooms
        MODIFY COLUMN status
        ENUM('AVAILABLE', 'OCCUPIED', 'CLEANING', 'RESERVED', 'OUT_OF_SERVICE', 'OCCUPIED_OVERTIME')
        NOT NULL
    """)


def downgrade() -> None:
    """
    Remove OCCUPIED_OVERTIME status from rooms.status enum

    WARNING: This will fail if any rooms currently have status = OCCUPIED_OVERTIME
    You should manually update those rooms to OCCUPIED before running downgrade.
    """
    # First, update any OCCUPIED_OVERTIME rooms to OCCUPIED
    op.execute("""
        UPDATE rooms
        SET status = 'OCCUPIED'
        WHERE status = 'OCCUPIED_OVERTIME'
    """)

    # Then remove the enum value
    op.execute("""
        ALTER TABLE rooms
        MODIFY COLUMN status
        ENUM('AVAILABLE', 'OCCUPIED', 'CLEANING', 'RESERVED', 'OUT_OF_SERVICE')
        NOT NULL
    """)
