from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class FireParticipantEventIn(BaseModel):
    participant_id: int
    arrival_time: str

    tech_type_id: Optional[int] = None
    comment: Optional[str] = None

class FireParticipantEventOut(BaseModel):
    participant_id: int
    arrival_time: str | datetime
    tech_type_id: Optional[int] = None
    comment: Optional[str] = None

    class Config:
        from_attributes = True
