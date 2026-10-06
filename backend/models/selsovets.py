from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from db.base import Base


class Selsovet(Base):
    __tablename__ = "selsovets"
    __table_args__ = (
        UniqueConstraint("name", "municipality_id", name="uq_selsovets_name_municipality"),
    )

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    municipality_id = Column(Integer, ForeignKey("municipalities.id"), nullable=False, index=True)

    municipality = relationship("Municipality", back_populates="selsovets")
