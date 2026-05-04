from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


@dataclass
class FireUpdateDTO:
    fire_date: Optional[datetime] = None
    end_time: Optional[datetime] = None

    is_forest: Optional[bool] = None
    land_type_id: Optional[int] = None

    area: Optional[float] = None

    address: Optional[str] = None
    address_comment: Optional[str] = None

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

    inspector_id: Optional[int] = None

    external_card_number: Optional[str] = None

    participants_ids: Optional[List[int]] = None
    tech_types_ids: Optional[List[int]] = None

    def to_dict(self) -> dict:
        return {
            k: (v.isoformat() if isinstance(v, datetime) else v)
            for k, v in self.__dict__.items()
            if v is not None
        }
