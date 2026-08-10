"""harden fire and user constraints

Revision ID: 20260810_0006
Revises: 20260731_0005
Create Date: 2026-08-10 00:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260810_0006"
down_revision: Union[str, None] = "20260731_0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("users", "full_name", existing_type=sa.String(), nullable=False)
    op.alter_column("users", "username", existing_type=sa.String(), nullable=False)
    op.alter_column("users", "password", existing_type=sa.String(), nullable=False)
    op.alter_column("users", "role", existing_type=sa.String(), nullable=False)
    op.create_check_constraint(
        "ck_users_role",
        "users",
        "role IN ('dispatcher', 'inspector', 'admin', 'chief')",
    )
    op.create_check_constraint(
        "ck_fires_status",
        "fires",
        "status IN ('OPEN', 'IN_REVIEW', 'COMPLETED')",
    )
    op.create_check_constraint(
        "ck_fires_area_nonnegative",
        "fires",
        "area IS NULL OR area >= 0",
    )
    op.create_check_constraint(
        "ck_fires_orenburg_coordinates",
        "fires",
        "(latitude IS NULL AND longitude IS NULL) OR "
        "(latitude BETWEEN 50.45 AND 54.40 AND longitude BETWEEN 50.70 AND 61.75)",
    )
    op.create_unique_constraint(
        "uq_fires_external_card_number",
        "fires",
        ["external_card_number"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_fires_external_card_number", "fires", type_="unique")
    op.drop_constraint("ck_fires_orenburg_coordinates", "fires", type_="check")
    op.drop_constraint("ck_fires_area_nonnegative", "fires", type_="check")
    op.drop_constraint("ck_fires_status", "fires", type_="check")
    op.drop_constraint("ck_users_role", "users", type_="check")
    op.alter_column("users", "role", existing_type=sa.String(), nullable=True)
    op.alter_column("users", "password", existing_type=sa.String(), nullable=True)
    op.alter_column("users", "username", existing_type=sa.String(), nullable=True)
    op.alter_column("users", "full_name", existing_type=sa.String(), nullable=True)
