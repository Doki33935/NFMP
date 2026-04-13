from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from db.base import Base


class Fire(Base):
    __tablename__ = "fires"

    id = Column(Integer, primary_key=True)

    # 🔥 основные
    date = Column(String)
    time_msg = Column(String)
    fire_type = Column(String)
    land_type = Column(String)
    area = Column(Float)

    # 📍 локация
    address = Column(String)
    comment = Column(String)
    municipality = Column(String)
    settlement = Column(String)

    # 🧑‍🚒 контекст
    forestry = Column(String)
    right_of_way = Column(String)
    owner = Column(String)
    source = Column(String)
    extra = Column(String)

    # 👤 пользователи
    dispatcher_id = Column(Integer, ForeignKey("users.id"))
    inspector_id = Column(Integer, nullable=True)

    dispatcher_fio = Column(String)
    inspector_fio = Column(String)

    # 📊 статус
    status = Column(String, default="OPEN")