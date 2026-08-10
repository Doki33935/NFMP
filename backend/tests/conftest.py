import os
import sys
from pathlib import Path

os.environ.setdefault("SECRET_KEY", "test-secret-key-with-at-least-32-characters")
os.environ.setdefault("DATABASE_URL", "sqlite://")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from api import auth, fire, users
from core.security import get_current_user, get_db, hash_password
from db.base import Base
from models.fire import Fire  # noqa: F401
from models.fire_participant_events import FireParticipantEvent  # noqa: F401
from models.fire_participants import FireParticipant  # noqa: F401
from models.forestries import Forestry  # noqa: F401
from models.land_types import LandType  # noqa: F401
from models.municipalities import Municipality  # noqa: F401
from models.reasons import Reason, ReasonGroup
from models.selsovets import Selsovet
from models.tech_type import TechType  # noqa: F401
from models.user import User


@pytest.fixture()
def api_context():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSession = sessionmaker(bind=engine, expire_on_commit=False)
    Base.metadata.create_all(engine)
    db = TestingSession()

    roles = {}
    for role in ("dispatcher", "inspector", "admin", "chief"):
        user = User(
            username=role,
            password=hash_password(f"Strong-{role}-password-2026"),
            full_name=role.title(),
            role=role,
        )
        db.add(user)
        roles[role] = user
    second_inspector = User(
        username="inspector2",
        password=hash_password("Strong-inspector2-password-2026"),
        full_name="Second Inspector",
        role="inspector",
    )
    db.add(second_inspector)

    municipality = Municipality(name="Test municipality")
    land_type = LandType(name="Test land")
    forestry = Forestry(name="Test forestry")
    reason_group = ReasonGroup(name="Test reason group")
    db.add_all([municipality, land_type, forestry, reason_group])
    db.flush()
    selsovet = Selsovet(name="Test settlement", municipality_id=municipality.id)
    reason = Reason(name="Test reason", group_id=reason_group.id)
    db.add_all([selsovet, reason])
    db.commit()

    current = {"user": roles["admin"]}
    app = FastAPI()
    app.include_router(auth.router)
    app.include_router(fire.router)
    app.include_router(users.router)

    def override_db():
        yield db

    def override_user():
        return current["user"]

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_current_user] = override_user

    with TestClient(app) as client:
        yield {
            "client": client,
            "db": db,
            "roles": roles,
            "second_inspector": second_inspector,
            "current": current,
            "municipality": municipality,
            "selsovet": selsovet,
            "land_type": land_type,
            "forestry": forestry,
            "reason": reason,
        }

    db.close()
    Base.metadata.drop_all(engine)
