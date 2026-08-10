from sqlalchemy import Column, Integer, DateTime, Float, ForeignKey, Boolean, String, Date, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from db.base import Base


class Fire(Base):
    __tablename__ = "fires"
    __table_args__ = (
        CheckConstraint("status IN ('OPEN', 'IN_REVIEW', 'COMPLETED')", name="ck_fires_status"),
        CheckConstraint("area IS NULL OR area >= 0", name="ck_fires_area_nonnegative"),
        CheckConstraint(
            "(latitude IS NULL AND longitude IS NULL) OR "
            "(latitude BETWEEN 50.45 AND 54.40 AND longitude BETWEEN 50.70 AND 61.75)",
            name="ck_fires_orenburg_coordinates",
        ),
        UniqueConstraint("external_card_number", name="uq_fires_external_card_number"),
    )

    # =========================
    # 🔥 PRIMARY
    # =========================
    id = Column(Integer, primary_key=True, index=True)

    # =========================
    # 🔥 EVENT
    # =========================
    fire_date = Column(Date, nullable=False)
    time_msg = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)

    is_forest = Column(Boolean, nullable=False)

    land_type_id = Column(Integer, ForeignKey("land_types.id"), nullable=True, index=True)

    area = Column(Float, nullable=True)

    # =========================
    # 📍 LOCATION
    # =========================
    address = Column(String, nullable=False)

    municipality_id = Column(Integer, ForeignKey("municipalities.id"), nullable=True, index=True)
    selsovet_id = Column(Integer, ForeignKey("selsovets.id"), nullable=True, index=True)

    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    # =========================
    # 🧭 CONTEXT
    # =========================
    forestry_id = Column(Integer, ForeignKey("forestries.id"), nullable=True, index=True)
    reason_id = Column(Integer, ForeignKey("reasons.id"), nullable=True, index=True)
    right_of_way = Column(Boolean, nullable=True)
    right_of_way_type = Column(String, nullable=True)
    owner = Column(String, nullable=True)

    source = Column(String, nullable=True)
    extra = Column(String, nullable=True)

    # =========================
    # 👤 USERS
    # =========================
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    # =========================
    # 📄 EXTERNAL
    # =========================
    external_card_number = Column(String, nullable=True)

    # =========================
    # 📊 STATUS
    # =========================
    status = Column(String, default="OPEN", nullable=False)
    deleted_at = Column(DateTime, nullable=True, index=True)

    # =========================
    # 🔗 RELATIONS
    # =========================
    creator = relationship("User", foreign_keys=[creator_id])
    reviewer = relationship("User", foreign_keys=[reviewer_id])
    municipality = relationship("Municipality")
    selsovet = relationship("Selsovet")
    land_type = relationship("LandType")
    forestry = relationship("Forestry")
    reason = relationship("Reason")
    participant_events = relationship(
        "FireParticipantEvent",
        backref="fire",
        cascade="all, delete-orphan"
    )

    @property
    def creator_name(self):
        return self.creator.full_name if self.creator else None

    @property
    def reviewer_name(self):
        return self.reviewer.full_name if self.reviewer else None
