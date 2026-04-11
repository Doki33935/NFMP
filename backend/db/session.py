from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://fire_user:fire_pass@localhost:5432/fire_db"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)