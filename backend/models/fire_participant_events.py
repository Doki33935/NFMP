from sqlalchemy import Column, Integer, ForeignKey, DateTime, String
from db.base import Base


class FireParticipantEvent(Base):
    __tablename__ = "fire_participant_events"

    id = Column(Integer, primary_key=True, index=True)

    fire_id = Column(Integer, ForeignKey("fires.id", ondelete="CASCADE"), nullable=False, index=True)

    participant_id = Column(Integer, ForeignKey("fire_participants.id"), nullable=False, index=True)

    arrival_time = Column(DateTime, nullable=False)

    tech_type_id = Column(Integer, ForeignKey("tech_types.id"), nullable=True)

    comment = Column(String, nullable=True)