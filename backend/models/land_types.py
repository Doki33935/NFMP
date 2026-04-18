from sqlalchemy import Column, Integer, String
from db.base import Base


class LandType(Base):
    __tablename__ = "land_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)