from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class FireParticipantEventInDTO:
    participant_id: int
    arrival_time: datetime

    tech_type_id: Optional[int] = None
    role: Optional[str] = None
    people_count: Optional[int] = None
    comment: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "participant_id": self.participant_id,
            "arrival_time": self.arrival_time.isoformat(),
            "tech_type_id": self.tech_type_id,
            "role": self.role,
            "people_count": self.people_count,
            "comment": self.comment,
        }
    

@dataclass
class FireParticipantEventOutDTO:
    participant_id: int
    arrival_time: datetime

    tech_type_id: Optional[int]
    role: Optional[str]
    people_count: Optional[int]

    @staticmethod
    def from_dict(data: dict):
        return FireParticipantEventOutDTO(
            participant_id=data["participant_id"],
            arrival_time=datetime.fromisoformat(data["arrival_time"]),
            tech_type_id=data.get("tech_type_id"),
            role=data.get("role"),
            people_count=data.get("people_count"),
        )