from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class FireParticipantEventIn(BaseModel):
    participant_id: int
    arrival_time: datetime

    tech_type_id: Optional[int] = None
    comment: Optional[str] = None

class FireParticipantEventOut(BaseModel):
    participant_id: int
    arrival_time: datetime
    tech_type_id: Optional[int] = None
    comment: Optional[str] = None

    class Config:
        from_attributes = True
