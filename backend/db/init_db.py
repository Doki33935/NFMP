from db.base import Base
from db.session import engine
from db.session import SessionLocal
from models.user import User


def init_db():
    Base.metadata.create_all(bind=engine)

def seed_admin():
    db = SessionLocal()

    admin = User(
        username="111",
        password_hash="111",  # потом заменим на хеш
        full_name="Admin",
        role="admin"
    )

    db.add(admin)
    db.commit()
    db.close()