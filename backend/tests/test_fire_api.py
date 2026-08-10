from models.fire import Fire
from db.reference_values import OWNER_TYPES


def base_fire_payload(context):
    return {
        "fire_date": "2026-08-10",
        "time_msg": "2026-08-10T10:00:00",
        "is_forest": True,
        "address": "Оренбургская область, тестовый адрес",
        "municipality_id": context["municipality"].id,
        "selsovet_id": context["selsovet"].id,
        "latitude": 51.77,
        "longitude": 55.10,
        "participants": [],
    }


def test_fire_lifecycle_and_roles(api_context):
    context = api_context
    client = context["client"]
    current = context["current"]

    current["user"] = context["roles"]["dispatcher"]
    created = client.post("/fires/", json=base_fire_payload(context))
    assert created.status_code == 201, created.text
    fire_id = created.json()["id"]
    assert client.get("/fires/").status_code == 403

    current["user"] = context["roles"]["inspector"]
    assert client.get("/fires/").status_code == 200
    taken = client.post(f"/fires/{fire_id}/take")
    assert taken.status_code == 200, taken.text
    assert taken.json()["status"] == "IN_REVIEW"

    current["user"] = context["second_inspector"]
    assert client.post(f"/fires/{fire_id}/take").status_code == 409
    assert client.put(f"/fires/{fire_id}", json={"area": 1.5}).status_code == 403

    current["user"] = context["roles"]["inspector"]
    completed_fields = {
        "land_type_id": context["land_type"].id,
        "area": 1.5,
        "forestry_id": context["forestry"].id,
        "reason_id": context["reason"].id,
        "owner": OWNER_TYPES[0],
        "external_card_number": "TEST-CARD-1",
        "end_time": "2026-08-10T12:00:00",
    }
    updated = client.put(f"/fires/{fire_id}", json=completed_fields)
    assert updated.status_code == 200, updated.text
    completed = client.post(f"/fires/{fire_id}/complete")
    assert completed.status_code == 200, completed.text
    assert completed.json()["status"] == "COMPLETED"
    assert client.delete(f"/fires/{fire_id}").status_code == 403

    current["user"] = context["roles"]["admin"]
    assert client.delete(f"/fires/{fire_id}").status_code == 204
    assert client.get(f"/fires/{fire_id}").status_code == 404
    assert context["db"].get(Fire, fire_id).deleted_at is not None

    current["user"] = context["roles"]["chief"]
    assert client.get("/fires/").status_code == 200
    assert client.post("/fires/", json=base_fire_payload(context)).status_code == 403


def test_fire_input_validation(api_context):
    context = api_context
    client = context["client"]
    context["current"]["user"] = context["roles"]["dispatcher"]

    payload = base_fire_payload(context)
    payload["longitude"] = 70
    assert client.post("/fires/", json=payload).status_code == 422

    payload = base_fire_payload(context)
    payload["longitude"] = None
    assert client.post("/fires/", json=payload).status_code == 422

    payload = base_fire_payload(context)
    payload["fire_date"] = "2026-08-09"
    response = client.post("/fires/", json=payload)
    assert response.status_code == 400
