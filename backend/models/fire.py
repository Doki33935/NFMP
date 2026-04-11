from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, ForeignKey
from db.base import Base

class Fire(Base):
    __tablename__ = "fires"

    id = Column(Integer, primary_key=True)

    fire_date = Column(DateTime)
    report_time = Column(DateTime)
    liquidation_datetime = Column(DateTime)

    address = Column(String)
    address_comment = Column(String)

    municipality_id = Column(Integer, ForeignKey("municipalities.id"))
    settlement_id = Column(Integer, ForeignKey("settlements.id"))

    latitude = Column(Float)
    longitude = Column(Float)

    land_type_id = Column(Integer, ForeignKey("land_types.id"))
    fire_type = Column(String)

    forestry_id = Column(Integer, ForeignKey("forestries.id"), nullable=True)

    is_right_of_way = Column(Boolean)
    right_of_way_type_id = Column(Integer, ForeignKey("right_of_way_types.id"), nullable=True)
    owner = Column(String, nullable=True)

    source = Column(String)
    area = Column(Float)

    dispatcher_name = Column(String)
    external_card_id = Column(String)
    investigator_name = Column(String)

    description = Column(String)

    status = Column(String, default="draft")

    locked_by = Column(Integer, ForeignKey("users.id"), nullable=True)