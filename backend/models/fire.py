from sqlalchemy import Column, Integer, DateTime, Float, ForeignKey, Boolean, String
from sqlalchemy.orm import relationship
from db.base import Base


class Fire(Base):
    __tablename__ = "fires"

    # =========================
    # 🔥 PRIMARY
    # =========================
    id = Column(Integer, primary_key=True, index=True)

    # =========================
    # 🔥 EVENT
    # =========================
    fire_date = Column(DateTime, nullable=False)
    time_msg = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)

    is_forest = Column(Boolean, nullable=False)

    land_type_id = Column(Integer, ForeignKey("land_types.id"), nullable=False, index=True)

    area = Column(Float, nullable=True)

    # =========================
    # 📍 LOCATION
    # =========================
    address = Column(String, nullable=False)
    address_comment = Column(String, nullable=True)

    municipality_id = Column(Integer, ForeignKey("municipalities.id"), nullable=False, index=True)
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
    dispatcher_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    inspector_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    # =========================
    # 📄 EXTERNAL
    # =========================
    external_card_number = Column(String, nullable=True)

    # =========================
    # 📊 STATUS
    # =========================
    status = Column(String, default="OPEN", nullable=False)

    # =========================
    # 🔗 RELATIONS (ТОЛЬКО FK-объекты)
    # =========================
    municipality = relationship("Municipality")
    selsovet = relationship("Selsovet")
    land_type = relationship("LandType")
    forestry = relationship("Forestry")
    reason = relationship("Reason")