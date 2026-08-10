from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional
from datetime import datetime, date
from schemas.participant import FireParticipantEventIn


class FireUpdate(BaseModel):
    fire_date: Optional[date] = None
    time_msg: Optional[datetime] = None
    end_time: Optional[datetime] = None

    is_forest: Optional[bool] = None
    land_type_id: Optional[int] = None

    area: Optional[float] = Field(default=None, ge=0)

    address: Optional[str] = Field(default=None, min_length=1, max_length=500)
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

    participants: Optional[list[FireParticipantEventIn]] = None

    @field_validator("address")
    @classmethod
    def strip_address(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value:
            raise ValueError("Address is required")
        return value

    @model_validator(mode="after")
    def validate_coordinates(self):
        latitude_set = "latitude" in self.model_fields_set
        longitude_set = "longitude" in self.model_fields_set
        if latitude_set != longitude_set:
            raise ValueError("Latitude and longitude must be updated together")
        if latitude_set and (self.latitude is None) != (self.longitude is None):
            raise ValueError("Latitude and longitude must be provided together")
        return self
