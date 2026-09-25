from sqlalchemy import CheckConstraint, Column, Integer, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import relationship
from db.base import Base


class FireParticipantEvent(Base):
    __tablename__ = "fire_participant_events"

    id = Column(Integer, primary_key=True, index=True)

    fire_id = Column(Integer, ForeignKey("fires.id", ondelete="CASCADE"), nullable=False, index=True)

    participant_id = Column(Integer, ForeignKey("fire_participants.id"), nullable=False, index=True)

    arrival_time = Column(String, nullable=True)

    tech_type_id = Column(Integer, ForeignKey("tech_types.id"), nullable=True)

    comment = Column(String, nullable=True)

    equipment = relationship(
        "FireParticipantEventEquipment",
        back_populates="event",
        cascade="all, delete-orphan",
        order_by="FireParticipantEventEquipment.id",
    )


class FireParticipantEventEquipment(Base):
    __tablename__ = "fire_participant_event_equipment"
    __table_args__ = (
        UniqueConstraint("event_id", "tech_type_id", name="uq_event_equipment_type"),
        CheckConstraint("quantity > 0", name="ck_event_equipment_quantity_positive"),
    )

    id = Column(Integer, primary_key=True)
    event_id = Column(
        Integer,
        ForeignKey("fire_participant_events.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    tech_type_id = Column(Integer, ForeignKey("tech_types.id"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False, default=1)

    event = relationship("FireParticipantEvent", back_populates="equipment")
