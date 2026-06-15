import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from api import admin, auth, users, fire, references
from db.init_db import (
    seed_admin,
    seed_fire_participants,
    seed_forestry,
    seed_land_types,
    seed_municipalities,
    seed_reasons,
    seed_selsovets,
    seed_tech_types,
)
from db.session import SessionLocal
from models.user import User


app = FastAPI()


def wait_for_database(retries: int = 30, delay: int = 2) -> None:
    for attempt in range(1, retries + 1):
        try:
            with SessionLocal() as db:
                db.execute(text("SELECT 1"))
            return
        except OperationalError:
            if attempt == retries:
                raise
            time.sleep(delay)


@app.on_event("startup")
def prepare_database() -> None:
    wait_for_database()

    with SessionLocal() as db:
        has_users = db.query(User.id).first() is not None

    if not has_users:
        seed_admin()

    seed_forestry()
    seed_land_types()
    seed_municipalities()
    seed_selsovets()
    seed_tech_types()
    seed_fire_participants()
    seed_reasons()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(fire.router)
app.include_router(references.router)
