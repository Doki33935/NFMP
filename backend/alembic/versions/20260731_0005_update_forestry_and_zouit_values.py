"""update forestry and ZOUIT reference values

Revision ID: 20260731_0005
Revises: 20260730_0004
Create Date: 2026-07-31 00:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260731_0005"
down_revision: Union[str, None] = "20260730_0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


FORESTRY_NAMES = [
    "ГКУ «Абдулинское лесничество»",
    "ГКУ «Адамовское лесничество»",
    "ГКУ «Асекеевское лесничество»",
    "ГКУ «Беляевское лесничество»",
    "ГКУ «Бугурусланское лесничество»",
    "ГКУ «Бузулукское лесничество»",
    "ГКУ «Грачевское лесничество»",
    "ГКУ «Домбаровское лесничество»",
    "ГКУ «Илекское лесничество»",
    "ГКУ «Кваркенское лесничество»",
    "ГКУ «Краснохолмское лесничество»",
    "ГКУ «Кувандыкское лесничество»",
    "ГКУ «Новосергиевское лесничество»",
    "ГКУ «Оренбургское лесничество»",
    "ГКУ «Орское лесничество»",
    "ГКУ «Первомайское лесничество»",
    "ГКУ «Пономаревское лесничество»",
    "ГКУ «Сакмарское лесничество»",
    "ГКУ «Саракташское лесничество»",
    "ГКУ «Северное лесничество»",
    "ГКУ «Соль-Илецкое лесничество»",
    "ГКУ «Сорочинское лесничество»",
    "ГКУ «Ташлинское лесничество»",
    "ГКУ «Тюльганское лесничество»",
    "ГКУ «Чернореченское лесничество»",
    "ГКУ «Шарлыкское лесничество»",
]

LEGACY_ZOUIT_VALUES = {
    "railway": "охранная зона железных дорог",
    "road": "придорожные полосы автомобильных дорог",
    "powerline": "охранная зона объектов электроэнергетики (объектов электросетевого хозяйства и объектов по производству электрической энергии)",
}


def upgrade() -> None:
    connection = op.get_bind()

    connection.execute(
        sa.text(
            """
            UPDATE forestries
            SET name = :corrected
            WHERE name = :misspelled
              AND NOT EXISTS (
                  SELECT 1 FROM forestries WHERE name = :corrected
              )
            """
        ),
        {
            "misspelled": "ГКУ «Шарлыкское лесничество »",
            "corrected": "ГКУ «Шарлыкское лесничество»",
        },
    )
    connection.execute(
        sa.text(
            """
            UPDATE fires
            SET forestry_id = corrected.id
            FROM forestries AS misspelled, forestries AS corrected
            WHERE fires.forestry_id = misspelled.id
              AND misspelled.name = :misspelled
              AND corrected.name = :corrected
            """
        ),
        {
            "misspelled": "ГКУ «Шарлыкское лесничество »",
            "corrected": "ГКУ «Шарлыкское лесничество»",
        },
    )
    connection.execute(
        sa.text("DELETE FROM forestries WHERE name = :misspelled"),
        {"misspelled": "ГКУ «Шарлыкское лесничество »"},
    )

    for name in FORESTRY_NAMES:
        connection.execute(
            sa.text(
                """
                INSERT INTO forestries (name)
                VALUES (:name)
                ON CONFLICT (name) DO NOTHING
                """
            ),
            {"name": name},
        )

    for legacy_value, zouit_type in LEGACY_ZOUIT_VALUES.items():
        connection.execute(
            sa.text(
                """
                UPDATE fires
                SET right_of_way_type = :zouit_type
                WHERE right_of_way_type = :legacy_value
                """
            ),
            {"legacy_value": legacy_value, "zouit_type": zouit_type},
        )


def downgrade() -> None:
    connection = op.get_bind()
    for legacy_value, zouit_type in LEGACY_ZOUIT_VALUES.items():
        connection.execute(
            sa.text(
                """
                UPDATE fires
                SET right_of_way_type = :legacy_value
                WHERE right_of_way_type = :zouit_type
                """
            ),
            {"legacy_value": legacy_value, "zouit_type": zouit_type},
        )
