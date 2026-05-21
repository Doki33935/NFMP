from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from datetime import datetime

from models.fire import Fire
from models.fire_participant_events import FireParticipantEvent
from models.fire_participants import FireParticipant
from models.tech_type import TechType
from models.user import User
from schemas.fire_create import FireCreate, FireResponse
from schemas.fire_update import FireUpdate
from core.security import get_db, get_current_user

router = APIRouter(prefix="/fires", tags=["fires"])


# =========================
# VALIDATION HELPERS
# =========================
def validate_participants(db: Session, participants):
    for p in participants:
        if not db.get(FireParticipant, p.participant_id):
            raise HTTPException(400, f"Participant {p.participant_id} not found")

        if p.tech_type_id and not db.get(TechType, p.tech_type_id):
            raise HTTPException(400, f"Tech {p.tech_type_id} not found")


def replace_events(db: Session, fire_id: int, participants):
    # удалить старые
    db.query(FireParticipantEvent).filter(
        FireParticipantEvent.fire_id == fire_id
    ).delete()

    # создать новые
    for p in participants:
        db.add(
            FireParticipantEvent(
                fire_id=fire_id,
                participant_id=p.participant_id,
                arrival_time=p.arrival_time,
                tech_type_id=p.tech_type_id,
                comment=p.comment,
            )
        )


# =========================
# CREATE
# =========================
@router.post("/", response_model=FireResponse, status_code=status.HTTP_201_CREATED)
def create_fire(data: FireCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    participants = data.participants or []
    validate_participants(db, participants)

    fire_data = data.model_dump(exclude={"participants"})
    fire_data["creator_id"] = current_user.id

    fire = Fire(
        **fire_data,
        time_msg=datetime.now(),
        status="OPEN"
    )

    db.add(fire)
    db.flush()

    replace_events(db, fire.id, participants)

    db.commit()

    fire = db.query(Fire).options(
        joinedload(Fire.participant_events),
        joinedload(Fire.creator),
        joinedload(Fire.reviewer),
    ).get(fire.id)

    return fire


# =========================
# GET ALL
# =========================
@router.get("/", response_model=list[FireResponse])
def get_fires(
    status: str | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Fire).options(
        joinedload(Fire.participant_events),
        joinedload(Fire.creator),
        joinedload(Fire.reviewer),
    )

    if status:
        query = query.filter(Fire.status == status)

    return query.order_by(Fire.id.desc()).all()


# =========================
# GET ONE
# =========================
@router.get("/{fire_id}", response_model=FireResponse)
def get_fire(fire_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    fire = db.query(Fire).options(
        joinedload(Fire.participant_events),
        joinedload(Fire.creator),
        joinedload(Fire.reviewer),
    ).filter(Fire.id == fire_id).first()

    if not fire:
        raise HTTPException(404, "Fire not found")

    return fire


# =========================
# UPDATE
# =========================
@router.put("/{fire_id}", response_model=FireResponse)
def update_fire(fire_id: int, data: FireUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    fire = db.get(Fire, fire_id)

    if not fire:
        raise HTTPException(404, "Fire not found")

    if fire.status == "COMPLETED":
        raise HTTPException(400, "Editing not allowed")

    update_data = data.model_dump(exclude_unset=True)
    participants = update_data.pop("participants", None)

    # Allow completing from IN_REVIEW
    requested_status = update_data.pop("status", None)
    if requested_status == "COMPLETED" and fire.status == "IN_REVIEW":
        fire.status = "COMPLETED"

    # 🔒 защита системных полей
    for field in ["id", "creator_id"]:
        update_data.pop(field, None)

    # обновление полей
    for field, value in update_data.items():
        setattr(fire, field, value)

    # обновление событий
    if participants is not None:
        from schemas.participant import FireParticipantEventIn as PSchema
        participant_objs = [PSchema(**p) if isinstance(p, dict) else p for p in participants]
        validate_participants(db, participant_objs)
        replace_events(db, fire.id, participant_objs)

    db.commit()

    fire = db.query(Fire).options(
        joinedload(Fire.participant_events),
        joinedload(Fire.creator),
        joinedload(Fire.reviewer),
    ).get(fire.id)

    return fire


# =========================
# TAKE (инспектор берёт пожар в работу)
# =========================
@router.post("/{fire_id}/take", response_model=FireResponse)
def take_fire(fire_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    fire = db.get(Fire, fire_id)

    if not fire:
        raise HTTPException(404, "Fire not found")

    if fire.status != "OPEN":
        raise HTTPException(400, "Fire is not open")

    fire.status = "IN_REVIEW"
    fire.reviewer_id = current_user.id

    db.commit()

    fire = db.query(Fire).options(
        joinedload(Fire.participant_events),
        joinedload(Fire.creator),
        joinedload(Fire.reviewer),
    ).get(fire.id)

    return fire


# =========================
# COMPLETE
# =========================
@router.post("/{fire_id}/complete", response_model=FireResponse)
def complete_fire(fire_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    fire = db.get(Fire, fire_id)

    if not fire:
        raise HTTPException(404, "Fire not found")

    if fire.status != "IN_REVIEW":
        raise HTTPException(400, "Cannot complete")

    fire.status = "COMPLETED"

    db.commit()
    db.refresh(fire)

    return fire


# =========================
# DELETE
# =========================
@router.delete("/{fire_id}", status_code=204)
def delete_fire(fire_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    fire = db.get(Fire, fire_id)

    if not fire:
        raise HTTPException(404, "Fire not found")

    if fire.status == "COMPLETED":
        raise HTTPException(400, "Completed fires cannot be deleted")

    db.delete(fire)
    db.commit()

    return None
