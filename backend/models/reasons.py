# models/reason.py

from sqlalchemy import Column, Integer, String
from db.base import Base


class Reason(Base):
    __tablename__ = "reasons"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)