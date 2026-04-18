from sqlalchemy import Column, Integer, String
from db.base import Base


class Forestry(Base):
    __tablename__ = "forestries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)