from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import os

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    user = os.getenv("POSTGRES_USER", "fire_user")
    password = os.getenv("POSTGRES_PASSWORD")
    if not password:
        raise RuntimeError("DATABASE_URL or POSTGRES_PASSWORD is required")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "fire_db")
    DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{db}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
