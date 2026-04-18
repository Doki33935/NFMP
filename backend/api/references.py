from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.session import SessionLocal

from models.forestries import Forestry
from models.land_types import LandType
from models.municipalities import Municipality
from models.selsovets import Selsovet
from models.fire_participants import FireParticipant
from models.tech_type import TechType

router = APIRouter(prefix="/references", tags=["references"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# MAP
# =========================
REFERENCE_MAP = {
    "forestry": Forestry,
    "land-types": LandType,
    "municipalities": Municipality,
    "fire-participants": FireParticipant,
    "tech-types": TechType,
}


# =========================
# GET ALL ITEMS BY TYPE
# =========================
@router.get("/{ref_type}")
def get_reference(ref_type: str, db: Session = Depends(get_db)):
    model = REFERENCE_MAP.get(ref_type)

    if not model:
        raise HTTPException(
            status_code=404,
            detail=f"Reference '{ref_type}' not found"
        )

    return db.query(model).order_by(model.name).all()


# =========================
# GET SELSOVETS BY MUNICIPALITY
# =========================
@router.get("/selsovets")
def get_selsovets(municipality_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(Selsovet)

    if municipality_id:
        query = query.filter(Selsovet.municipality_id == municipality_id)

    return query.order_by(Selsovet.name).all()