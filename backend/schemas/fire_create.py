from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from typing import Optional
from datetime import datetime, date
from schemas.participant import FireParticipantEventIn, FireParticipantEventOut

class FireCreate(BaseModel):
    fire_date: date
    time_msg: datetime

    is_forest: bool
    land_type_id: Optional[int] = None

    area: Optional[float] = Field(default=None, ge=0)

    address: str = Field(min_length=1, max_length=500)
    municipality_id: Optional[int] = None
    selsovet_id: Optional[int] = None
    latitude: Optional[float] = Field(default=None, ge=50.45, le=54.40)
    longitude: Optional[float] = Field(default=None, ge=50.70, le=61.75)

    forestry_id: Optional[int] = None
    reason_id: Optional[int] = None

    right_of_way: Optional[bool] = None
    right_of_way_type: Optional[str] = Field(default=None, max_length=500)
    owner: Optional[str] = Field(default=None, max_length=500)

    source: Optional[str] = Field(default=None, max_length=2000)
    extra: Optional[str] = Field(default=None, max_length=4000)

    external_card_number: Optional[str] = Field(default=None, max_length=100)

    participants: list[FireParticipantEventIn] = Field(default_factory=list)

    @field_validator("address")
    @classmethod
    def strip_address(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Address is required")
        return value

    @model_validator(mode="after")
    def validate_coordinates(self):
        if (self.latitude is None) != (self.longitude is None):
            raise ValueError("Latitude and longitude must be provided together")
        return self


class FireResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int

    fire_date: date
    time_msg: datetime
    end_time: Optional[datetime] = None

    is_forest: bool
    land_type_id: Optional[int] = None

    area: Optional[float] = None

    address: str
    municipality_id: Optional[int] = None
    selsovet_id: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

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
    deleted_at: Optional[datetime] = None

    participant_events: list[FireParticipantEventOut] = Field(default_factory=list)
