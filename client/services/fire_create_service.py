from datetime import datetime, time
import re

from models.fire_create import FireCreateDTO
from models.participants import FireParticipantEventInDTO


class FireCreateService:
    def __init__(self, user):
        self.user = user

    def build_dto(self, ui) -> FireCreateDTO:
        participants = []
        fire_date = ui.fire_date.value()
        area = self._parse_area(ui.area.text())

        for _, participant, tech_type, arrival in ui.participant_rows:
            participant_id = participant.currentData()
            if not participant_id:
                continue

            participants.append(
                FireParticipantEventInDTO(
                    participant_id=participant_id,
                    tech_type_id=tech_type.currentData(),
                    arrival_time=self._parse_arrival_time(fire_date, arrival.text()),
                )
            )

        return FireCreateDTO(
            fire_date=fire_date,
            is_forest=ui.is_forest.currentData() is True,
            land_type_id=ui.land_type.currentData(),
            area=area,
            address=ui.address.text(),
            address_comment=ui.comment.text() or None,
            municipality_id=ui.municipality.currentData(),
            selsovet_id=ui.settlement.currentData(),
            forestry_id=ui.forestry.currentData(),
            reason_id=ui.reason.currentData(),
            right_of_way=ui.right_of_way.currentData() is True,
            right_of_way_type=ui.right_of_way_type.currentData() or None,
            owner=ui.owner.text() or None,
            source=ui.source.text() or None,
            extra=ui.extra.toPlainText() or None,
            dispatcher_id=self.user.id,
            participants=participants,
        )

    def _parse_arrival_time(self, fire_date, value: str) -> datetime:
        value = (value or "").strip()
        if not value:
            return datetime.combine(fire_date, time(0, 0))

        if not re.fullmatch(r"\d{1,2}:\d{2}", value):
            raise ValueError("Время прибытия участника укажите в формате HH:MM")

        hour, minute = value.split(":", 1)
        try:
            return datetime.combine(fire_date, time(int(hour), int(minute)))
        except ValueError as exc:
            raise ValueError("Время прибытия участника должно быть от 00:00 до 23:59") from exc

    def _parse_area(self, value: str) -> float | None:
        value = (value or "").strip().replace(",", ".")
        if not value:
            return None

        try:
            area = float(value)
        except ValueError as exc:
            raise ValueError("Площадь должна быть числом") from exc

        if area < 0:
            raise ValueError("Площадь не может быть отрицательной")

        return area
