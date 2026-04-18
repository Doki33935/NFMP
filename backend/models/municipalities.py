from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from db.base import Base


class Municipality(Base):
    __tablename__ = "municipalities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    selsovets = relationship(
        "Selsovet",
        back_populates="municipality",
        cascade="all, delete-orphan"
    )