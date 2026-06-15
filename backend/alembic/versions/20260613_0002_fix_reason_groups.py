"""fix reason groups

Revision ID: 20260613_0002
Revises: 20260611_0001
Create Date: 2026-06-13 00:00:00
"""

from typing import Sequence, Union

from alembic import op

revision: str = "20260613_0002"
down_revision: Union[str, None] = "20260611_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE IF EXISTS reasons ADD COLUMN IF NOT EXISTS group_id INTEGER")
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM pg_constraint
                WHERE conname = 'reasons_name_key'
            ) THEN
                ALTER TABLE reasons DROP CONSTRAINT reasons_name_key;
            END IF;
        END $$;
    """)
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint
                WHERE conname = 'reasons_group_id_fkey'
            ) THEN
                ALTER TABLE reasons
                ADD CONSTRAINT reasons_group_id_fkey
                FOREIGN KEY (group_id) REFERENCES reason_groups(id);
            END IF;
        END $$;
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_reasons_group_id ON reasons (group_id)")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_reasons_group_id")
    op.execute("ALTER TABLE IF EXISTS reasons DROP CONSTRAINT IF EXISTS reasons_group_id_fkey")
    op.execute("ALTER TABLE IF EXISTS reasons DROP COLUMN IF EXISTS group_id")
