"""add_frontend_domain_setting

Revision ID: 20251025_0944
Revises: 20251025_0933
Create Date: 2025-10-25 09:44:00.000000+07:00

This migration adds the frontend_domain system setting which is used by
the Telegram service to generate correct URLs in notification messages.
The setting is stored in the system_settings table as a key-value pair.
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20251025_0944'
down_revision: Union[str, None] = '20251025_0933'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # This migration is for documentation purposes.
    # The frontend_domain setting will be stored in system_settings table
    # using the SettingsService.set_setting() method.
    # No database schema changes are needed.
    pass


def downgrade() -> None:
    # No changes to revert - this was a documentation migration
    pass
