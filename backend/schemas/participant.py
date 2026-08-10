from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class FireParticipantEventIn(BaseModel):
    participant_id: int = Field(gt=0)
    arrival_time: str = Field(min_length=1, max_length=32)

    tech_type_id: Optional[int] = None
    comment: Optional[str] = Field(default=None, max_length=1000)

class FireParticipantEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    participant_id: int
    arrival_time: str | datetime
    tech_type_id: Optional[int] = None
    comment: Optional[str] = None
