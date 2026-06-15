from logging.config import fileConfig
import os

from alembic import context
from sqlalchemy import engine_from_config, pool

from db.base import Base

from models.user import User
from models.fire import Fire
from models.fire_participant_events import FireParticipantEvent
from models.fire_participants import FireParticipant
from models.forestries import Forestry
from models.land_types import LandType
from models.municipalities import Municipality
from models.reasons import Reason, ReasonGroup
from models.selsovets import Selsovet
from models.tech_type import TechType

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_url() -> str:
    return os.getenv("DATABASE_URL") or config.get_main_option("sqlalchemy.url")


def run_migrations_offline() -> None:
    context.configure(
        url=get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = get_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
