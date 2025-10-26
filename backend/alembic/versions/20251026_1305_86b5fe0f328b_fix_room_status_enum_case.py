"""fix_room_status_enum_case

Revision ID: 86b5fe0f328b
Revises: 20251025_0944
Create Date: 2025-10-26 13:05:58.735205+07:00

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '86b5fe0f328b'
down_revision: Union[str, None] = '20251025_0944'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Fix RoomStatus enum to use lowercase values
    op.execute("""
        ALTER TABLE rooms
        MODIFY COLUMN status ENUM('available', 'occupied', 'cleaning', 'reserved', 'out_of_service')
        NOT NULL DEFAULT 'available'
    """)

    # Fix StayType enum to use lowercase values
    op.execute("""
        ALTER TABLE room_rates
        MODIFY COLUMN stay_type ENUM('overnight', 'temporary')
        NOT NULL
    """)

    # Update existing data from uppercase to lowercase (if any)
    op.execute("""
        UPDATE rooms SET status = LOWER(status)
    """)

    op.execute("""
        UPDATE room_rates SET stay_type = LOWER(stay_type)
    """)


def downgrade() -> None:
    # Revert to uppercase
    op.execute("""
        ALTER TABLE rooms
        MODIFY COLUMN status ENUM('AVAILABLE', 'OCCUPIED', 'CLEANING', 'RESERVED', 'OUT_OF_SERVICE')
        NOT NULL DEFAULT 'AVAILABLE'
    """)

    op.execute("""
        ALTER TABLE room_rates
        MODIFY COLUMN stay_type ENUM('OVERNIGHT', 'TEMPORARY')
        NOT NULL
    """)

    op.execute("""
        UPDATE rooms SET status = UPPER(status)
    """)

    op.execute("""
        UPDATE room_rates SET stay_type = UPPER(stay_type)
    """)

