"""Add photos field to maintenance tasks

Revision ID: add_photos_maintenance
Revises: cd860e3e92fd
Create Date: 2025-11-01 15:35:00

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'add_photos_maintenance'
down_revision: Union[str, None] = 'cd860e3e92fd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('maintenance_tasks', sa.Column('photos', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('maintenance_tasks', 'photos')
