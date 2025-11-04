"""make customer name and phone optional

Revision ID: 27091df09970
Revises: 86b5fe0f328b
Create Date: 2025-11-01 11:17:05.311449+07:00

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '27091df09970'
down_revision: Union[str, None] = '86b5fe0f328b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Make full_name and phone_number nullable
    op.alter_column('customers', 'full_name',
                    existing_type=sa.String(255),
                    nullable=True)
    op.alter_column('customers', 'phone_number',
                    existing_type=sa.String(20),
                    nullable=True)


def downgrade() -> None:
    # Revert to non-nullable (with data migration to handle existing NULL values)
    # Set default value for any NULL records before making columns non-nullable
    op.execute("UPDATE customers SET full_name = 'Unknown Guest' WHERE full_name IS NULL")
    op.execute("UPDATE customers SET phone_number = '0000000000' WHERE phone_number IS NULL")

    op.alter_column('customers', 'full_name',
                    existing_type=sa.String(255),
                    nullable=False)
    op.alter_column('customers', 'phone_number',
                    existing_type=sa.String(20),
                    nullable=False)
