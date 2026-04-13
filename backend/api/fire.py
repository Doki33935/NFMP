from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from db.session import SessionLocal
from models.fire import Fire

router = APIRouter(prefix="/fires", tags=["fires"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# CREATE (диспетчер)
# =========================
@router.post("/")
def create_fire(data: dict, db: Session = Depends(get_db)):
    fire = Fire(
        date=data.get("date"),
        time_msg=data.get("time_msg"),
        fire_type=data.get("fire_type"),
        land_type=data.get("land_type"),
        area=data.get("area"),

        address=data.get("address"),
        comment=data.get("comment"),
        municipality=data.get("mo"),
        settlement=data.get("selsovet"),

        forestry=data.get("forestry"),
        right_of_way=data.get("right_of_way"),
        owner=data.get("owner"),
        source=data.get("source"),
        extra=data.get("extra"),

        dispatcher_fio=data.get("dispatcher_fio"),

        status="OPEN"
    )

    db.add(fire)
    db.commit()
    db.refresh(fire)

    return {"id": fire.id}


# =========================
# READ ALL (список)
# =========================
# =========================
# GET FIRES (FILTERED)
# =========================
@router.get("/")
def get_fires(
    status: str | None = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Fire)

    if status:
        query = query.filter(Fire.status == status)

    fires = query.all()

    return [
        {
            "id": f.id,
            "date": f.date,
            "time_msg": f.time_msg,
            "address": f.address,
            "status": f.status
        }
        for f in fires
    ]


# =========================
# READ ONE
# =========================
@router.get("/{fire_id}")
def get_fire(fire_id: int, db: Session = Depends(get_db)):
    fire = db.get(Fire, fire_id)

    if not fire:
        raise HTTPException(404, "Fire not found")

    return {
        "id": fire.id,
        "date": fire.date,
        "time_msg": fire.time_msg,
        "fire_type": fire.fire_type,
        "land_type": fire.land_type,
        "area": fire.area,

        "address": fire.address,
        "comment": fire.comment,
        "municipality": fire.municipality,
        "settlement": fire.settlement,

        "forestry": fire.forestry,
        "right_of_way": fire.right_of_way,
        "owner": fire.owner,
        "source": fire.source,
        "extra": fire.extra,

        "status": fire.status,
        "dispatcher_fio": fire.dispatcher_fio,
        "inspector_fio": fire.inspector_fio
    }


# =========================
# UPDATE (инспектор начинает/ведёт проверку)
# =========================
@router.put("/{fire_id}")
def update_fire(fire_id: int, data: dict, db: Session = Depends(get_db)):
    fire = db.get(Fire, fire_id)

    if not fire:
        raise HTTPException(404, "Fire not found")

    # 🔥 разрешаем только OPEN или IN_REVIEW
    if fire.status not in ["OPEN", "IN_REVIEW"]:
        raise HTTPException(400, "Editing not allowed")

    # 🔥 первый вход инспектора переводит в IN_REVIEW
    if fire.status == "OPEN":
        fire.status = "IN_REVIEW"

    # 🔥 разрешённые поля редактирования
    fields = [
        "date", "time_msg", "fire_type", "land_type", "area",
        "address", "comment", "municipality", "settlement",
        "forestry", "right_of_way", "owner", "source", "extra"
    ]

    for field in fields:
        if field in data:
            setattr(fire, field, data[field])

    fire.inspector_fio = data.get("inspector_fio")

    db.commit()

    return {"status": fire.status}


# =========================
# COMPLETE (финал инспектора)
# =========================
@router.post("/{fire_id}/complete")
def complete_fire(fire_id: int, db: Session = Depends(get_db)):
    fire = db.get(Fire, fire_id)

    if not fire:
        raise HTTPException(404, "Fire not found")

    # 🔥 завершить можно только после проверки
    if fire.status != "IN_REVIEW":
        raise HTTPException(400, "Cannot complete")

    fire.status = "COMPLETED"
    db.commit()

    return {"status": "COMPLETED"}