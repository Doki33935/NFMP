from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from db.base import Base


class ReasonGroup(Base):
    __tablename__ = "reason_groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    reasons = relationship("Reason", back_populates="group")


class Reason(Base):
    __tablename__ = "reasons"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    group_id = Column(Integer, ForeignKey("reason_groups.id"), nullable=False)

    group = relationship("ReasonGroup", back_populates="reasons")
