import os
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from api import admin, auth, users, fire, references
from db.init_db import (
    seed_admin,
    hash_legacy_passwords,
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


IS_PRODUCTION = os.getenv("ENVIRONMENT", "development").lower() == "production"
app = FastAPI(
    docs_url=None if IS_PRODUCTION else "/docs",
    redoc_url=None if IS_PRODUCTION else "/redoc",
    openapi_url=None if IS_PRODUCTION else "/openapi.json",
)


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

    hash_legacy_passwords()

    seed_forestry()
    seed_land_types()
    seed_municipalities()
    seed_selsovets()
    seed_tech_types()
    seed_fire_participants()
    seed_reasons()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
        if origin.strip()
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", include_in_schema=False)
def health() -> dict[str, str]:
    with SessionLocal() as db:
        db.execute(text("SELECT 1"))
    return {"status": "ok"}

app.include_router(admin.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(fire.router)
app.include_router(references.router)
