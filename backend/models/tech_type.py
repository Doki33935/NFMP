from sqlalchemy import Column, Integer, String
from db.base import Base


class TechType(Base):
    __tablename__ = "tech_types"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)