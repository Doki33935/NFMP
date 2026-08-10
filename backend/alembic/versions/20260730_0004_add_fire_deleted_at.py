"""add soft delete marker for fires

Revision ID: 20260730_0004
Revises: 20260613_0003
Create Date: 2026-07-30 00:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260730_0004"
down_revision: Union[str, None] = "20260613_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("fires", sa.Column("deleted_at", sa.DateTime(), nullable=True))
    op.create_index("ix_fires_deleted_at", "fires", ["deleted_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_fires_deleted_at", table_name="fires")
    op.drop_column("fires", "deleted_at")
