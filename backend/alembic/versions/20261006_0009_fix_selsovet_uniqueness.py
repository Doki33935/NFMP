"""allow equal selsovet names in different municipalities

Revision ID: 20261006_0009
Revises: 20260925_0008
Create Date: 2026-10-06 00:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20261006_0009"
down_revision: Union[str, None] = "20260925_0008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


SELSOVETS = (
    ("Преображенский сельсовет", "Бузулукский район"),
    ("Чапаевский сельсовет", "Тюльганский район"),
    ("Васильевский сельсовет", "Саракташский район"),
    ("Никольский сельсовет", "Сакмарский район"),
)


def upgrade() -> None:
    op.execute("ALTER TABLE selsovets DROP CONSTRAINT IF EXISTS selsovets_name_key")
    op.create_unique_constraint(
        "uq_selsovets_name_municipality",
        "selsovets",
        ["name", "municipality_id"],
    )

    connection = op.get_bind()
    for selsovet, municipality in SELSOVETS:
        connection.execute(
            sa.text(
                """
                INSERT INTO selsovets (name, municipality_id)
                SELECT :selsovet, id
                FROM municipalities
                WHERE name = :municipality
                ON CONFLICT (name, municipality_id) DO NOTHING
                """
            ),
            {"selsovet": selsovet, "municipality": municipality},
        )


def downgrade() -> None:
    connection = op.get_bind()
    for selsovet, municipality in SELSOVETS[1:]:
        connection.execute(
            sa.text(
                """
                DELETE FROM selsovets
                WHERE name = :selsovet
                  AND municipality_id = (
                      SELECT id FROM municipalities WHERE name = :municipality
                  )
                """
            ),
            {"selsovet": selsovet, "municipality": municipality},
        )

    op.drop_constraint(
        "uq_selsovets_name_municipality",
        "selsovets",
        type_="unique",
    )
    op.create_unique_constraint("selsovets_name_key", "selsovets", ["name"])
