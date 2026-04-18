from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from schemas.participant import FireParticipantEventIn, FireParticipantEventOut

class FireCreate(BaseModel):
    fire_date: datetime

    is_forest: bool
    land_type_id: int

    area: Optional[float] = None

    address: str
    address_comment: Optional[str] = None

    municipality_id: Optional[int] = None
    selsovet_id: Optional[int] = None

    latitude: Optional[float] = None
    longitude: Optional[float] = None

    forestry_id: Optional[int] = None

    right_of_way: Optional[bool] = None
    right_of_way_type: Optional[str] = None
    owner: Optional[str] = None

    source: Optional[str] = None
    extra: Optional[str] = None

    dispatcher_id: int

    external_card_number: Optional[str] = None

    # 🔥 НОВАЯ ЛОГИКА
    participants: Optional[list[FireParticipantEventIn]] = []



class FireResponse(BaseModel):
    id: int

    fire_date: datetime
    end_time: Optional[datetime] = None

    is_forest: bool
    land_type_id: int

    area: Optional[float] = None

    address: str
    address_comment: Optional[str] = None

    municipality_id: Optional[int] = None
    selsovet_id: Optional[int] = None

    latitude: Optional[float] = None
    longitude: Optional[float] = None

    forestry_id: Optional[int] = None

    right_of_way: Optional[bool] = None
    right_of_way_type: Optional[str] = None
    owner: Optional[str] = None

    source: Optional[str] = None
    extra: Optional[str] = None

    dispatcher_id: int
    inspector_id: Optional[int] = None

    external_card_number: Optional[str] = None

    status: str

    # 🔥 НОВАЯ СТРУКТУРА
    participants: list[FireParticipantEventOut] = []

    class Config:
        from_attributes = True