from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date
from schemas.participant import FireParticipantEventIn


class FireUpdate(BaseModel):
    fire_date: Optional[date] = None
    end_time: Optional[datetime] = None

    is_forest: Optional[bool] = None
    land_type_id: Optional[int] = None

    area: Optional[float] = None

    address: Optional[str] = None
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

    reviewer_id: Optional[int] = None

    external_card_number: Optional[str] = None

    status: Optional[str] = None

    participants: Optional[list[FireParticipantEventIn]] = None
