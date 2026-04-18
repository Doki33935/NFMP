from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from db.base import Base


class Selsovet(Base):
    __tablename__ = "selsovets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    municipality_id = Column(Integer, ForeignKey("municipalities.id"), nullable=False, index=True)

    municipality = relationship("Municipality", back_populates="selsovets")