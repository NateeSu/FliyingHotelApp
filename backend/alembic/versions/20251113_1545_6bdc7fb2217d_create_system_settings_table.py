"""create_system_settings_table

Revision ID: 6bdc7fb2217d
Revises: create_home_assistant_tables
Create Date: 2025-11-13 15:45:51.906307+07:00

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision: str = '6bdc7fb2217d'
down_revision: Union[str, None] = 'create_home_assistant_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create system_settings table
    op.create_table(
        'system_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(length=255), nullable=False),
        sa.Column('value', sa.Text(), nullable=True),
        sa.Column('data_type', mysql.ENUM('STRING', 'NUMBER', 'JSON', 'BOOLEAN', name='settingdatatypeenum'), nullable=False, server_default='STRING'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index('ix_system_settings_id', 'system_settings', ['id'], unique=False)
    op.create_index('ix_system_settings_key', 'system_settings', ['key'], unique=True)


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_system_settings_key', table_name='system_settings')
    op.drop_index('ix_system_settings_id', table_name='system_settings')

    # Drop table
    op.drop_table('system_settings')
