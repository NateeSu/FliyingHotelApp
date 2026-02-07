"""create housekeeping and maintenance task tables

Revision ID: 20251015_0001
Revises: b4a03c2e07c7
Create Date: 2025-10-15 00:01:00.000000+07:00

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20251015_0001'
down_revision: Union[str, None] = 'b4a03c2e07c7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create housekeeping_tasks table
    op.create_table('housekeeping_tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('room_id', sa.Integer(), nullable=False),
        sa.Column('assigned_to', sa.Integer(), nullable=True),
        sa.Column('check_in_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.Enum('PENDING', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED', name='housekeepingtaskstatusenum'), nullable=False),
        sa.Column('priority', sa.Enum('LOW', 'MEDIUM', 'HIGH', 'URGENT', name='housekeepingtaskpriorityenum'), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('duration_minutes', sa.Integer(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('completed_by', sa.Integer(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['room_id'], ['rooms.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['assigned_to'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['check_in_id'], ['check_ins.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['completed_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_housekeeping_tasks_id'), 'housekeeping_tasks', ['id'], unique=False)
    op.create_index(op.f('ix_housekeeping_tasks_room_id'), 'housekeeping_tasks', ['room_id'], unique=False)
    op.create_index(op.f('ix_housekeeping_tasks_assigned_to'), 'housekeeping_tasks', ['assigned_to'], unique=False)
    op.create_index(op.f('ix_housekeeping_tasks_check_in_id'), 'housekeeping_tasks', ['check_in_id'], unique=False)
    op.create_index(op.f('ix_housekeeping_tasks_status'), 'housekeeping_tasks', ['status'], unique=False)

    # Create maintenance_tasks table
    op.create_table('maintenance_tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('room_id', sa.Integer(), nullable=True),
        sa.Column('assigned_to', sa.Integer(), nullable=True),
        sa.Column('status', sa.Enum('PENDING', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED', name='maintenancetaskstatusenum'), nullable=False),
        sa.Column('priority', sa.Enum('LOW', 'MEDIUM', 'HIGH', 'URGENT', name='maintenancetaskpriorityenum'), nullable=False),
        sa.Column('category', sa.Enum('PLUMBING', 'ELECTRICAL', 'HVAC', 'FURNITURE', 'APPLIANCE', 'BUILDING', 'OTHER', name='maintenancetaskcategoryenum'), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('resolution_notes', sa.Text(), nullable=True),
        sa.Column('photos', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('duration_minutes', sa.Integer(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('completed_by', sa.Integer(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['room_id'], ['rooms.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['assigned_to'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['completed_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_maintenance_tasks_id'), 'maintenance_tasks', ['id'], unique=False)
    op.create_index(op.f('ix_maintenance_tasks_room_id'), 'maintenance_tasks', ['room_id'], unique=False)
    op.create_index(op.f('ix_maintenance_tasks_assigned_to'), 'maintenance_tasks', ['assigned_to'], unique=False)
    op.create_index(op.f('ix_maintenance_tasks_status'), 'maintenance_tasks', ['status'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_maintenance_tasks_status'), table_name='maintenance_tasks')
    op.drop_index(op.f('ix_maintenance_tasks_assigned_to'), table_name='maintenance_tasks')
    op.drop_index(op.f('ix_maintenance_tasks_room_id'), table_name='maintenance_tasks')
    op.drop_index(op.f('ix_maintenance_tasks_id'), table_name='maintenance_tasks')
    op.drop_table('maintenance_tasks')

    op.drop_index(op.f('ix_housekeeping_tasks_status'), table_name='housekeeping_tasks')
    op.drop_index(op.f('ix_housekeeping_tasks_check_in_id'), table_name='housekeeping_tasks')
    op.drop_index(op.f('ix_housekeeping_tasks_assigned_to'), table_name='housekeeping_tasks')
    op.drop_index(op.f('ix_housekeeping_tasks_room_id'), table_name='housekeeping_tasks')
    op.drop_index(op.f('ix_housekeeping_tasks_id'), table_name='housekeeping_tasks')
    op.drop_table('housekeeping_tasks')
