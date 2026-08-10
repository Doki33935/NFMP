from sqlalchemy import CheckConstraint, Column, DateTime, Integer, String
from db.base import Base

class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(
            "role IN ('dispatcher', 'inspector', 'admin', 'chief')",
            name="ck_users_role",
        ),
    )

    id = Column(Integer, primary_key=True)
    full_name = Column(String, nullable=False)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)
    disabled_at = Column(DateTime, nullable=True, index=True)
