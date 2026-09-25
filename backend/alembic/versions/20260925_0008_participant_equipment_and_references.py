"""add participant equipment quantities and requested reference values

Revision ID: 20260925_0008
Revises: 20260810_0007
Create Date: 2026-09-25 00:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260925_0008"
down_revision: Union[str, None] = "20260810_0007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


FORESTRY = "Лесничество в ведении Министерства обороны"
PARTICIPANT = "ГБУ «Центр пожаротушения и охраны лесов Оренбургской области»"
SELSOVETS = (
    ("Преображенский сельсовет", "Бузулукский район"),
    ("Чапаевский сельсовет", "Тюльганский район"),
    ("Васильевский сельсовет", "Саракташский район"),
    ("Никольский сельсовет", "Сакмарский район"),
)


def upgrade() -> None:
    op.alter_column(
        "fires",
        "area",
        existing_type=sa.Float(),
        type_=sa.Numeric(18, 4),
        postgresql_using="area::numeric(18, 4)",
        existing_nullable=True,
    )
    op.alter_column(
        "fire_participant_events",
        "arrival_time",
        existing_type=sa.String(),
        nullable=True,
    )
    op.create_table(
        "fire_participant_event_equipment",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "event_id",
            sa.Integer(),
            sa.ForeignKey("fire_participant_events.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "tech_type_id",
            sa.Integer(),
            sa.ForeignKey("tech_types.id"),
            nullable=False,
        ),
        sa.Column("quantity", sa.Integer(), nullable=False, server_default="1"),
        sa.CheckConstraint("quantity > 0", name="ck_event_equipment_quantity_positive"),
        sa.UniqueConstraint("event_id", "tech_type_id", name="uq_event_equipment_type"),
    )
    op.create_index(
        "ix_fire_participant_event_equipment_event_id",
        "fire_participant_event_equipment",
        ["event_id"],
    )
    op.create_index(
        "ix_fire_participant_event_equipment_tech_type_id",
        "fire_participant_event_equipment",
        ["tech_type_id"],
    )

    connection = op.get_bind()
    connection.execute(
        sa.text(
            """
            INSERT INTO fire_participant_event_equipment (event_id, tech_type_id, quantity)
            SELECT id, tech_type_id, 1
            FROM fire_participant_events
            WHERE tech_type_id IS NOT NULL
            ON CONFLICT (event_id, tech_type_id) DO NOTHING
            """
        )
    )
    connection.execute(
        sa.text("INSERT INTO forestries (name) VALUES (:name) ON CONFLICT (name) DO NOTHING"),
        {"name": FORESTRY},
    )
    connection.execute(
        sa.text("INSERT INTO fire_participants (name) VALUES (:name) ON CONFLICT (name) DO NOTHING"),
        {"name": PARTICIPANT},
    )
    for selsovet, municipality in SELSOVETS:
        connection.execute(
            sa.text(
                """
                INSERT INTO selsovets (name, municipality_id)
                SELECT :selsovet, id
                FROM municipalities
                WHERE name = :municipality
                ON CONFLICT (name) DO NOTHING
                """
            ),
            {"selsovet": selsovet, "municipality": municipality},
        )


def downgrade() -> None:
    op.drop_index(
        "ix_fire_participant_event_equipment_tech_type_id",
        table_name="fire_participant_event_equipment",
    )
    op.drop_index(
        "ix_fire_participant_event_equipment_event_id",
        table_name="fire_participant_event_equipment",
    )
    op.drop_table("fire_participant_event_equipment")
    op.alter_column(
        "fire_participant_events",
        "arrival_time",
        existing_type=sa.String(),
        nullable=False,
    )
    op.alter_column(
        "fires",
        "area",
        existing_type=sa.Numeric(18, 4),
        type_=sa.Float(),
        postgresql_using="area::double precision",
        existing_nullable=True,
    )
