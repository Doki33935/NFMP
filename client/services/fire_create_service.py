from models.fire_create import FireCreateDTO
from models.participants import FireParticipantEventInDTO


class FireCreateService:
    def __init__(self, user):
        self.user = user

    def build_dto(self, ui) -> FireCreateDTO:
        participants = []

        for _, p, t, time in ui.participant_rows:
            participants.append(
                FireParticipantEventInDTO(
                    participant_id=p.currentData(),
                    tech_type_id=t.currentData(),
                    arrival_time=time.text()  # если надо → потом нормализуем
                )
            )

        return FireCreateDTO(
            fire_date=ui.fire_date.value(),

            is_forest=ui.is_forest.currentText() == "Лес",
            land_type_id=1,  # ⚠️ пока заглушка, если нет справочника

            area=float(ui.area.text()) if ui.area.text() else None,

            address=ui.address.text(),
            address_comment=ui.comment.text() or None,

            municipality_id=ui.municipality.currentData(),
            selsovet_id=None,  # если нет пока

            forestry_id=ui.forestry.currentData(),

            right_of_way=ui.right_of_way.currentText() == "Да",
            right_of_way_type=ui.right_of_way_type.text() or None,
            owner=ui.owner.text() or None,

            source=ui.source.text() or None,
            extra=ui.extra.text() or None,

            dispatcher_id=self.user.id,

            participants=participants
        )