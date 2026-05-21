from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date
from schemas.participant import FireParticipantEventIn, FireParticipantEventOut

class FireCreate(BaseModel):
    fire_date: date

    is_forest: bool
    land_type_id: Optional[int] = None

    area: Optional[float] = None

    address: str
    address_comment: Optional[str] = None

    municipality_id: Optional[int] = None
    selsovet_id: Optional[int] = None

    forestry_id: Optional[int] = None
    reason_id: Optional[int] = None

    right_of_way: Optional[bool] = None
    right_of_way_type: Optional[str] = None
    owner: Optional[str] = None

    source: Optional[str] = None
    extra: Optional[str] = None

    external_card_number: Optional[str] = None

    participants: Optional[list[FireParticipantEventIn]] = []


class FireResponse(BaseModel):
    id: int

    fire_date: date
    time_msg: datetime
    end_time: Optional[datetime] = None

    is_forest: bool
    land_type_id: int

    area: Optional[float] = None

    address: str
    address_comment: Optional[str] = None

    municipality_id: Optional[int] = None
    selsovet_id: Optional[int] = None

    forestry_id: Optional[int] = None
    reason_id: Optional[int] = None

    right_of_way: Optional[bool] = None
    right_of_way_type: Optional[str] = None
    owner: Optional[str] = None

    source: Optional[str] = None
    extra: Optional[str] = None

    creator_id: int
    creator_name: Optional[str] = None
    reviewer_id: Optional[int] = None
    reviewer_name: Optional[str] = None

    external_card_number: Optional[str] = None

    status: str

    participant_events: list[FireParticipantEventOut] = []

    class Config:
        from_attributes = True
