"""standardize all enum values to uppercase

Revision ID: cd860e3e92fd
Revises: 27091df09970
Create Date: 2025-11-01 11:52:39.798250+07:00

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'cd860e3e92fd'
down_revision: Union[str, None] = '27091df09970'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Update all enum columns to UPPERCASE
    tables_and_columns = [
        ('rooms', 'status', ['AVAILABLE', 'OCCUPIED', 'CLEANING', 'RESERVED', 'OUT_OF_SERVICE']),
        ('room_rates', 'stay_type', ['OVERNIGHT', 'TEMPORARY']),
        ('check_ins', 'stay_type', ['OVERNIGHT', 'TEMPORARY']),
        ('check_ins', 'payment_method', ['CASH', 'TRANSFER', 'CREDIT_CARD']),
        ('check_ins', 'status', ['CHECKED_IN', 'CHECKED_OUT']),
        ('bookings', 'status', ['PENDING', 'CONFIRMED', 'CHECKED_IN', 'COMPLETED', 'CANCELLED']),
        ('users', 'role', ['ADMIN', 'RECEPTION', 'HOUSEKEEPING', 'MAINTENANCE']),
        ('products', 'category', ['ROOM_AMENITY', 'FOOD_BEVERAGE']),
        ('orders', 'order_source', ['QR_CODE', 'RECEPTION']),
        ('orders', 'status', ['PENDING', 'DELIVERED', 'COMPLETED']),
        ('notifications', 'notification_type', ['ROOM_STATUS_CHANGE', 'OVERTIME_ALERT', 'BOOKING_REMINDER', 'HOUSEKEEPING_COMPLETE', 'MAINTENANCE_REQUEST', 'CHECK_IN', 'CHECK_OUT', 'ROOM_TRANSFER']),
        ('notifications', 'target_role', ['ADMIN', 'RECEPTION', 'HOUSEKEEPING', 'MAINTENANCE']),
        ('housekeeping_tasks', 'status', ['PENDING', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED']),
        ('housekeeping_tasks', 'priority', ['URGENT', 'HIGH', 'MEDIUM', 'LOW']),
        ('maintenance_tasks', 'status', ['PENDING', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED']),
        ('maintenance_tasks', 'priority', ['URGENT', 'HIGH', 'MEDIUM', 'LOW']),
        ('maintenance_tasks', 'category', ['PLUMBING', 'ELECTRICAL', 'HVAC', 'FURNITURE', 'APPLIANCE', 'BUILDING', 'OTHER']),
        ('system_settings', 'data_type', ['STRING', 'NUMBER', 'JSON', 'BOOLEAN']),
    ]
    
    for table, col, enums in tables_and_columns:
        enum_str = ', '.join([f"'{e}'" for e in enums])
        op.execute(f"ALTER TABLE {table} MODIFY COLUMN {col} ENUM({enum_str}) DEFAULT NULL" if col != 'category' else f"ALTER TABLE {table} MODIFY COLUMN {col} ENUM({enum_str})")
        op.execute(f"UPDATE {table} SET {col} = UPPER({col}) WHERE {col} IS NOT NULL")


def downgrade() -> None:
    pass
