"""initial schema

Revision ID: 20260611_0001
Revises: None
Create Date: 2026-06-11 19:50:00
"""

from typing import Sequence, Union

from alembic import op

revision: str = "20260611_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            full_name VARCHAR,
            username VARCHAR UNIQUE,
            password VARCHAR,
            role VARCHAR
        )
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS municipalities (
            id SERIAL PRIMARY KEY,
            name VARCHAR UNIQUE NOT NULL
        )
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS selsovets (
            id SERIAL PRIMARY KEY,
            name VARCHAR UNIQUE NOT NULL,
            municipality_id INTEGER NOT NULL REFERENCES municipalities(id)
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_selsovets_municipality_id ON selsovets (municipality_id)")
    op.execute("""
        CREATE TABLE IF NOT EXISTS land_types (
            id SERIAL PRIMARY KEY,
            name VARCHAR UNIQUE NOT NULL
        )
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS forestries (
            id SERIAL PRIMARY KEY,
            name VARCHAR UNIQUE NOT NULL
        )
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS fire_participants (
            id SERIAL PRIMARY KEY,
            name VARCHAR UNIQUE NOT NULL
        )
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS tech_types (
            id SERIAL PRIMARY KEY,
            name VARCHAR UNIQUE NOT NULL
        )
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS reason_groups (
            id SERIAL PRIMARY KEY,
            name VARCHAR UNIQUE NOT NULL
        )
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS reasons (
            id SERIAL PRIMARY KEY,
            name VARCHAR NOT NULL,
            group_id INTEGER NOT NULL REFERENCES reason_groups(id)
        )
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS fires (
            id SERIAL PRIMARY KEY,
            fire_date DATE NOT NULL,
            time_msg TIMESTAMP WITHOUT TIME ZONE NOT NULL,
            end_time TIMESTAMP WITHOUT TIME ZONE,
            is_forest BOOLEAN NOT NULL,
            land_type_id INTEGER REFERENCES land_types(id),
            area DOUBLE PRECISION,
            address VARCHAR NOT NULL,
            address_comment VARCHAR,
            municipality_id INTEGER REFERENCES municipalities(id),
            selsovet_id INTEGER REFERENCES selsovets(id),
            latitude DOUBLE PRECISION,
            longitude DOUBLE PRECISION,
            forestry_id INTEGER REFERENCES forestries(id),
            reason_id INTEGER REFERENCES reasons(id),
            right_of_way BOOLEAN,
            right_of_way_type VARCHAR,
            owner VARCHAR,
            source VARCHAR,
            extra VARCHAR,
            creator_id INTEGER NOT NULL REFERENCES users(id),
            reviewer_id INTEGER REFERENCES users(id),
            external_card_number VARCHAR,
            status VARCHAR NOT NULL
        )
    """)
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'fires' AND column_name = 'dispatcher_id'
            ) AND NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'fires' AND column_name = 'creator_id'
            ) THEN
                ALTER TABLE fires RENAME COLUMN dispatcher_id TO creator_id;
            END IF;

            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'fires' AND column_name = 'inspector_id'
            ) AND NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'fires' AND column_name = 'reviewer_id'
            ) THEN
                ALTER TABLE fires RENAME COLUMN inspector_id TO reviewer_id;
            END IF;
        END $$;
    """)
    op.execute("ALTER TABLE IF EXISTS fires ADD COLUMN IF NOT EXISTS creator_id INTEGER")
    op.execute("ALTER TABLE IF EXISTS fires ADD COLUMN IF NOT EXISTS reviewer_id INTEGER")
    op.execute("ALTER TABLE IF EXISTS fires ALTER COLUMN land_type_id DROP NOT NULL")
    op.execute("ALTER TABLE IF EXISTS fires ALTER COLUMN municipality_id DROP NOT NULL")
    op.execute("CREATE INDEX IF NOT EXISTS ix_fires_id ON fires (id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_fires_land_type_id ON fires (land_type_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_fires_municipality_id ON fires (municipality_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_fires_selsovet_id ON fires (selsovet_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_fires_forestry_id ON fires (forestry_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_fires_reason_id ON fires (reason_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_fires_creator_id ON fires (creator_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_fires_reviewer_id ON fires (reviewer_id)")
    op.execute("""
        CREATE TABLE IF NOT EXISTS fire_participant_events (
            id SERIAL PRIMARY KEY,
            fire_id INTEGER NOT NULL REFERENCES fires(id) ON DELETE CASCADE,
            participant_id INTEGER NOT NULL REFERENCES fire_participants(id),
            arrival_time VARCHAR NOT NULL,
            tech_type_id INTEGER REFERENCES tech_types(id),
            comment VARCHAR
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_fire_participant_events_id ON fire_participant_events (id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_fire_participant_events_fire_id ON fire_participant_events (fire_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_fire_participant_events_participant_id ON fire_participant_events (participant_id)")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS fire_participant_events")
    op.execute("DROP TABLE IF EXISTS fires")
    op.execute("DROP TABLE IF EXISTS reasons")
    op.execute("DROP TABLE IF EXISTS reason_groups")
    op.execute("DROP TABLE IF EXISTS tech_types")
    op.execute("DROP TABLE IF EXISTS fire_participants")
    op.execute("DROP TABLE IF EXISTS forestries")
    op.execute("DROP TABLE IF EXISTS land_types")
    op.execute("DROP TABLE IF EXISTS selsovets")
    op.execute("DROP TABLE IF EXISTS municipalities")
    op.execute("DROP TABLE IF EXISTS users")
