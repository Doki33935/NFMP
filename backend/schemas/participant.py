from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ParticipantEquipmentIn(BaseModel):
    tech_type_id: int = Field(gt=0)
    quantity: int = Field(default=1, ge=1, le=9999)


class ParticipantEquipmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    tech_type_id: int
    quantity: int


class FireParticipantEventIn(BaseModel):
    participant_id: int = Field(gt=0)
    arrival_time: Optional[str] = Field(default=None, max_length=32)

    tech_type_id: Optional[int] = None
    equipment: list[ParticipantEquipmentIn] = Field(default_factory=list)
    comment: Optional[str] = Field(default=None, max_length=1000)

    @model_validator(mode="after")
    def normalize_legacy_equipment(self):
        if self.tech_type_id and not self.equipment:
            self.equipment = [ParticipantEquipmentIn(tech_type_id=self.tech_type_id)]
        if self.arrival_time is not None:
            self.arrival_time = self.arrival_time.strip() or None
        return self

class FireParticipantEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    fire_id: int
    participant_id: int
    arrival_time: str | datetime | None
    tech_type_id: Optional[int] = None
    equipment: list[ParticipantEquipmentOut] = Field(default_factory=list)
    comment: Optional[str] = None
