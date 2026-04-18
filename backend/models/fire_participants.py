# models/fire_participant.py
from sqlalchemy import Column, Integer, String
from db.base import Base


class FireParticipant(Base):
    __tablename__ = "fire_participants"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)