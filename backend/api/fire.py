from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from core.security import get_db, require_role
from db.reference_values import OWNER_TYPES, ZOUIT_TYPES
from models.fire import Fire
from models.fire_participant_events import FireParticipantEvent
from models.fire_participants import FireParticipant
from models.forestries import Forestry
from models.land_types import LandType
from models.municipalities import Municipality
from models.reasons import Reason
from models.selsovets import Selsovet
from models.tech_type import TechType
from models.user import User
from schemas.fire_create import FireCreate, FireResponse
from schemas.fire_update import FireUpdate


router = APIRouter(prefix="/fires", tags=["fires"])


def validate_participants(db: Session, participants) -> None:
    for participant in participants:
        if not db.get(FireParticipant, participant.participant_id):
            raise HTTPException(400, f"Participant {participant.participant_id} not found")
        if participant.tech_type_id and not db.get(TechType, participant.tech_type_id):
            raise HTTPException(400, f"Tech {participant.tech_type_id} not found")


def validate_zouit(has_zouit: bool | None, zouit_type: str | None) -> None:
    if has_zouit and zouit_type not in ZOUIT_TYPES:
        raise HTTPException(400, "Select a valid ZOUIT type")


def validate_owner(owner: str | None, existing_owner: str | None = None) -> None:
    if owner and owner not in OWNER_TYPES and owner != existing_owner:
        raise HTTPException(400, "Select a valid owner type")


def validate_fire_fields(db: Session, values: dict, *, fire_id: int | None = None) -> None:
    municipality_id = values.get("municipality_id")
    selsovet_id = values.get("selsovet_id")

    for field, model in (
        ("municipality_id", Municipality),
        ("land_type_id", LandType),
        ("forestry_id", Forestry),
        ("reason_id", Reason),
    ):
        reference_id = values.get(field)
        if reference_id is not None and not db.get(model, reference_id):
            raise HTTPException(400, f"Invalid reference: {field}")

    if selsovet_id is not None:
        selsovet = db.get(Selsovet, selsovet_id)
        if not selsovet:
            raise HTTPException(400, "Invalid reference: selsovet_id")
        if municipality_id is None or selsovet.municipality_id != municipality_id:
            raise HTTPException(400, "The selected settlement does not belong to the municipality")

    latitude = values.get("latitude")
    longitude = values.get("longitude")
    if (latitude is None) != (longitude is None):
        raise HTTPException(400, "Coordinates must be provided together")
    if latitude is not None and not (50.45 <= latitude <= 54.40 and 50.70 <= longitude <= 61.75):
        raise HTTPException(400, "Coordinates must be within the Orenburg region")

    fire_date = values.get("fire_date")
    time_msg = values.get("time_msg")
    end_time = values.get("end_time")
    if fire_date and time_msg and fire_date != time_msg.date():
        raise HTTPException(400, "Fire date must match the message date")
    if end_time and time_msg and end_time < time_msg:
        raise HTTPException(400, "End time cannot precede the message time")

    card_number = values.get("external_card_number")
    if card_number:
        duplicate = db.query(Fire.id).filter(Fire.external_card_number == card_number)
        if fire_id is not None:
            duplicate = duplicate.filter(Fire.id != fire_id)
        if duplicate.first():
            raise HTTPException(409, "External card number already exists")


def validate_completion(fire: Fire) -> None:
    missing = []
    for field, label in (
        ("land_type_id", "land type"),
        ("area", "area"),
        ("reason_id", "reason"),
        ("owner", "owner"),
        ("external_card_number", "external card number"),
        ("end_time", "end time"),
    ):
        if getattr(fire, field) is None or getattr(fire, field) == "":
            missing.append(label)
    if fire.is_forest and fire.forestry_id is None:
        missing.append("forestry")
    if missing:
        raise HTTPException(400, f"Cannot complete fire; missing: {', '.join(missing)}")


def replace_events(db: Session, fire_id: int, participants) -> None:
    db.query(FireParticipantEvent).filter(
        FireParticipantEvent.fire_id == fire_id
    ).delete(synchronize_session=False)

    for participant in participants:
        db.add(
            FireParticipantEvent(
                fire_id=fire_id,
                participant_id=participant.participant_id,
                arrival_time=participant.arrival_time,
                tech_type_id=participant.tech_type_id,
                comment=participant.comment,
            )
        )


def active_fire_query(db: Session):
    return db.query(Fire).filter(Fire.deleted_at.is_(None))


def get_active_fire(db: Session, fire_id: int, *, eager: bool = False) -> Fire | None:
    query = active_fire_query(db)
    if eager:
        query = query.options(
            joinedload(Fire.participant_events),
            joinedload(Fire.creator),
            joinedload(Fire.reviewer),
        )
    return query.filter(Fire.id == fire_id).first()


def require_fire_editor(fire: Fire, current_user: User) -> None:
    if current_user.role == "admin":
        return
    if fire.reviewer_id != current_user.id:
        raise HTTPException(403, "Fire is assigned to another investigator")


@router.post("/", response_model=FireResponse, status_code=status.HTTP_201_CREATED)
def create_fire(
    data: FireCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("dispatcher", "inspector", "admin")),
):
    participants = data.participants or []
    validate_participants(db, participants)
    validate_zouit(data.right_of_way, data.right_of_way_type)
    validate_owner(data.owner)

    fire_data = data.model_dump(exclude={"participants"})
    validate_fire_fields(db, fire_data)
    fire_data["creator_id"] = current_user.id
    fire = Fire(**fire_data, status="OPEN")

    db.add(fire)
    db.flush()
    replace_events(db, fire.id, participants)
    db.commit()

    return get_active_fire(db, fire.id, eager=True)


@router.get("/", response_model=list[FireResponse])
def get_fires(
    status_value: str | None = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("inspector", "admin", "chief")),
):
    query = active_fire_query(db).options(
        joinedload(Fire.participant_events),
        joinedload(Fire.creator),
        joinedload(Fire.reviewer),
    )
    if status_value:
        query = query.filter(Fire.status == status_value)
    return query.order_by(Fire.id.desc()).all()


@router.get("/{fire_id}", response_model=FireResponse)
def get_fire(
    fire_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("inspector", "admin")),
):
    fire = get_active_fire(db, fire_id, eager=True)
    if not fire:
        raise HTTPException(404, "Fire not found")
    return fire


@router.get("/{fire_id}/view", response_model=FireResponse)
def view_fire(
    fire_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "chief")),
):
    fire = get_active_fire(db, fire_id, eager=True)
    if not fire:
        raise HTTPException(404, "Fire not found")
    return fire


@router.put("/{fire_id}", response_model=FireResponse)
def update_fire(
    fire_id: int,
    data: FireUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("inspector", "admin")),
):
    fire = get_active_fire(db, fire_id)
    if not fire:
        raise HTTPException(404, "Fire not found")
    if fire.status == "COMPLETED":
        raise HTTPException(400, "Editing not allowed")
    if fire.status != "IN_REVIEW":
        raise HTTPException(400, "Take the fire before editing")
    require_fire_editor(fire, current_user)

    update_data = data.model_dump(exclude_unset=True)
    participants = update_data.pop("participants", None)

    has_zouit = update_data.get("right_of_way", fire.right_of_way)
    zouit_type = update_data.get("right_of_way_type", fire.right_of_way_type)
    if not has_zouit:
        update_data["right_of_way_type"] = None
        zouit_type = None
    validate_zouit(has_zouit, zouit_type)
    if "owner" in update_data:
        validate_owner(update_data["owner"], fire.owner)

    merged_data = {
        column.name: getattr(fire, column.name)
        for column in Fire.__table__.columns
    }
    merged_data.update(update_data)
    validate_fire_fields(db, merged_data, fire_id=fire.id)

    for field in ["id", "creator_id", "reviewer_id", "status", "deleted_at"]:
        update_data.pop(field, None)
    for field, value in update_data.items():
        setattr(fire, field, value)

    if participants is not None:
        validate_participants(db, participants)
        replace_events(db, fire.id, participants)

    db.commit()
    return get_active_fire(db, fire.id, eager=True)


@router.post("/{fire_id}/take", response_model=FireResponse)
def take_fire(
    fire_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("inspector", "admin")),
):
    updated = db.query(Fire).filter(
        Fire.id == fire_id,
        Fire.deleted_at.is_(None),
        Fire.status == "OPEN",
    ).update(
        {Fire.status: "IN_REVIEW", Fire.reviewer_id: current_user.id},
        synchronize_session=False,
    )

    if updated != 1:
        if not get_active_fire(db, fire_id):
            raise HTTPException(404, "Fire not found")
        raise HTTPException(409, "Fire has already been taken")

    db.commit()
    return get_active_fire(db, fire_id, eager=True)


@router.post("/{fire_id}/complete", response_model=FireResponse)
def complete_fire(
    fire_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("inspector", "admin")),
):
    fire = get_active_fire(db, fire_id)
    if not fire:
        raise HTTPException(404, "Fire not found")
    if fire.status != "IN_REVIEW":
        raise HTTPException(400, "Cannot complete")
    require_fire_editor(fire, current_user)
    validate_completion(fire)

    fire.status = "COMPLETED"
    db.commit()
    return get_active_fire(db, fire_id, eager=True)


@router.delete("/{fire_id}", status_code=204)
def delete_fire(
    fire_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    fire = db.get(Fire, fire_id)
    if not fire:
        raise HTTPException(404, "Fire not found")
    if fire.deleted_at is None:
        fire.deleted_at = datetime.now(timezone.utc)
    db.commit()
    return None
