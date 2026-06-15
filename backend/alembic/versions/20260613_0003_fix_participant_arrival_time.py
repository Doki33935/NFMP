"""fix participant arrival time type

Revision ID: 20260613_0003
Revises: 20260613_0002
Create Date: 2026-06-13 00:00:00
"""

from typing import Sequence, Union

from alembic import op


revision: str = "20260613_0003"
down_revision: Union[str, None] = "20260613_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE fire_participant_events
        ALTER COLUMN arrival_time TYPE VARCHAR
        USING to_char(arrival_time, 'HH24:MI')
        """
    )


def downgrade() -> None:
    op.execute(
        """
        ALTER TABLE fire_participant_events
        ALTER COLUMN arrival_time TYPE TIMESTAMP WITHOUT TIME ZONE
        USING (
            CASE
                WHEN arrival_time ~ '^\\d{2}:\\d{2}$'
                THEN ('1970-01-01 ' || arrival_time)::timestamp
                ELSE arrival_time::timestamp
            END
        )
        """
    )
