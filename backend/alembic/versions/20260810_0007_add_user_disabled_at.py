"""add soft disable for users

Revision ID: 20260810_0007
Revises: 20260810_0006
Create Date: 2026-08-10 00:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260810_0007"
down_revision: Union[str, None] = "20260810_0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("disabled_at", sa.DateTime(), nullable=True))
    op.create_index("ix_users_disabled_at", "users", ["disabled_at"])


def downgrade() -> None:
    op.drop_index("ix_users_disabled_at", table_name="users")
    op.drop_column("users", "disabled_at")
