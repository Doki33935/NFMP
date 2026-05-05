from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, List
from models.participants import FireParticipantEventOutDTO

@dataclass
class FireResponseDTO:
    id: int

    fire_date: date
    time_msg: Optional[datetime]
    end_time: Optional[datetime]

    is_forest: bool
    land_type_id: int

    area: Optional[float]

    address: str
    address_comment: Optional[str]

    municipality_id: Optional[int]
    selsovet_id: Optional[int]

    latitude: Optional[float]
    longitude: Optional[float]

    forestry_id: Optional[int]
    reason_id: Optional[int]

    right_of_way: Optional[bool]
    right_of_way_type: Optional[str]
    owner: Optional[str]

    source: Optional[str]
    extra: Optional[str]

    dispatcher_id: int
    dispatcher_name: Optional[str]
    inspector_id: Optional[int]
    inspector_name: Optional[str]

    external_card_number: Optional[str]

    status: str

    participants: List[FireParticipantEventOutDTO] = field(default_factory=list)

    @staticmethod
    def from_dict(data: dict):
        return FireResponseDTO(
            id=data["id"],
            fire_date=date.fromisoformat(data["fire_date"]),
            time_msg=datetime.fromisoformat(data["time_msg"]) if data.get("time_msg") else None,
            end_time=datetime.fromisoformat(data["end_time"]) if data.get("end_time") else None,
            is_forest=data["is_forest"],
            land_type_id=data["land_type_id"],
            area=data.get("area"),
            address=data["address"],
            address_comment=data.get("address_comment"),
            municipality_id=data.get("municipality_id"),
            selsovet_id=data.get("selsovet_id"),
            latitude=data.get("latitude"),
            longitude=data.get("longitude"),
            forestry_id=data.get("forestry_id"),
            reason_id=data.get("reason_id"),
            right_of_way=data.get("right_of_way"),
            right_of_way_type=data.get("right_of_way_type"),
            owner=data.get("owner"),
            source=data.get("source"),
            extra=data.get("extra"),
            dispatcher_id=data["dispatcher_id"],
            dispatcher_name=data.get("dispatcher_name"),
            inspector_id=data.get("inspector_id"),
            inspector_name=data.get("inspector_name"),
            external_card_number=data.get("external_card_number"),
            status=data["status"],
            participants=[
                FireParticipantEventOutDTO.from_dict(p)
                for p in data.get("participants", [])
            ],
        )
