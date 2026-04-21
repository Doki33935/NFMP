class FireCreateService:
    def __init__(self, user):
        self.user = user

    def build_payload(self, ui):
        participants = []

        for _, p, t, time in ui.participant_rows:
            participants.append({
                "participant_id": p.currentData(),
                "tech_type_id": t.currentData(),
                "arrival_time": time.text()
            })

        return {
            "fire_date": ui.fire_date.value(),
            "is_forest": ui.is_forest.currentText() == "Лес",
            "land_type": ui.land_type.text(),
            "area": float(ui.area.text()) if ui.area.text() else None,

            "address": ui.address.text(),
            "address_comment": ui.comment.text(),

            "municipality": ui.municipality.currentData(),
            "settlement": ui.settlement.text(),

            "forestry": ui.forestry.currentData(),

            "right_of_way": ui.right_of_way.currentText() == "Да",
            "right_of_way_type": ui.right_of_way_type.text(),
            "owner": ui.owner.text(),

            "source": ui.source.text(),
            "extra": ui.extra.text(),

            "dispatcher_id": self.user.id,
            "status": "OPEN",
            "participants": participants
        }