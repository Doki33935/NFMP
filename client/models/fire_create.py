from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, List

from models.participants import FireParticipantEventInDTO


@dataclass
class FireCreateDTO:
    fire_date: date

    is_forest: bool
    land_type_id: int

    area: Optional[float] = None

    address: str = ""
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

    dispatcher_id: int = 0

    external_card_number: Optional[str] = None

    participants: List[FireParticipantEventInDTO] = field(default_factory=list)

    # =========================
    # SERIALIZE
    # =========================
    def to_dict(self) -> dict:
        data = {
            "fire_date": self.fire_date.isoformat(),
            "is_forest": self.is_forest,
            "land_type_id": self.land_type_id,
            "area": self.area,
            "address": self.address,
            "address_comment": self.address_comment,
            "municipality_id": self.municipality_id,
            "selsovet_id": self.selsovet_id,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "forestry_id": self.forestry_id,
            "reason_id": self.reason_id,
            "right_of_way": self.right_of_way,
            "right_of_way_type": self.right_of_way_type,
            "owner": self.owner,
            "source": self.source,
            "extra": self.extra,
            "dispatcher_id": self.dispatcher_id,
            "external_card_number": self.external_card_number,
            "participants": [p.to_dict() for p in self.participants],
        }

        # ✅ УБИРАЕМ None (очень важно)
        return {k: v for k, v in data.items() if v is not None}
