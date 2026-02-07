"""add ondelete constraints to foreign keys

Revision ID: 20260207_0001
Revises: 20251126_1620
Create Date: 2026-02-07 00:01:00.000000

"""
from typing import Sequence, Union
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '20260207_0001'
down_revision: Union[str, None] = '20251126_1620'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Define all FK changes: (table, constraint_name, column, ref_table.ref_col, ondelete)
FK_CHANGES = [
    ("bookings", "bookings_ibfk_customer", "customer_id", "customers.id", "RESTRICT"),
    ("bookings", "bookings_ibfk_room", "room_id", "rooms.id", "RESTRICT"),
    ("bookings", "bookings_ibfk_creator", "created_by", "users.id", "RESTRICT"),
    ("check_ins", "check_ins_ibfk_booking", "booking_id", "bookings.id", "SET NULL"),
    ("check_ins", "check_ins_ibfk_customer", "customer_id", "customers.id", "RESTRICT"),
    ("check_ins", "check_ins_ibfk_room", "room_id", "rooms.id", "RESTRICT"),
    ("check_ins", "check_ins_ibfk_creator", "created_by", "users.id", "RESTRICT"),
    ("check_ins", "check_ins_ibfk_checkout_user", "checked_out_by", "users.id", "SET NULL"),
    ("orders", "orders_ibfk_checkin", "check_in_id", "check_ins.id", "CASCADE"),
    ("orders", "orders_ibfk_product", "product_id", "products.id", "RESTRICT"),
    ("notifications", "notifications_ibfk_room", "room_id", "rooms.id", "SET NULL"),
    ("payments", "payments_ibfk_creator", "created_by", "users.id", "RESTRICT"),
]


def _get_existing_fk_name(conn, table, column):
    """Get the existing FK constraint name from MySQL information_schema."""
    result = conn.execute(
        sa.text(
            "SELECT CONSTRAINT_NAME FROM information_schema.KEY_COLUMN_USAGE "
            "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = :table "
            "AND COLUMN_NAME = :column AND REFERENCED_TABLE_NAME IS NOT NULL"
        ),
        {"table": table, "column": column}
    )
    row = result.fetchone()
    return row[0] if row else None


import sqlalchemy as sa


def upgrade() -> None:
    conn = op.get_bind()

    for table, new_fk_name, column, ref, ondelete in FK_CHANGES:
        ref_table, ref_col = ref.split(".")

        # Find existing FK constraint name
        existing_name = _get_existing_fk_name(conn, table, column)

        if existing_name:
            # Drop old FK
            op.drop_constraint(existing_name, table, type_="foreignkey")

        # Create new FK with ondelete
        op.create_foreign_key(
            new_fk_name, table, ref_table,
            [column], [ref_col],
            ondelete=ondelete
        )


def downgrade() -> None:
    conn = op.get_bind()

    for table, new_fk_name, column, ref, _ondelete in FK_CHANGES:
        ref_table, ref_col = ref.split(".")

        # Drop the constrained FK
        try:
            op.drop_constraint(new_fk_name, table, type_="foreignkey")
        except Exception:
            pass

        # Re-create without ondelete
        op.create_foreign_key(
            None, table, ref_table,
            [column], [ref_col]
        )
