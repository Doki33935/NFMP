from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.security import get_db
from db.reference_values import OWNER_TYPES, ZOUIT_TYPES

from models.forestries import Forestry
from models.land_types import LandType
from models.municipalities import Municipality
from models.selsovets import Selsovet
from models.fire_participants import FireParticipant
from models.tech_type import TechType
from models.reasons import Reason, ReasonGroup

router = APIRouter(prefix="/references", tags=["references"])


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
# GET SELSOVETS BY MUNICIPALITY
# =========================
@router.get("/selsovets")
def get_selsovets(municipality_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(Selsovet)

    if municipality_id:
        query = query.filter(Selsovet.municipality_id == municipality_id)

    return query.order_by(Selsovet.name).all()


# =========================
# GET REASON GROUPS (краткие причины)
# =========================
@router.get("/reason-groups")
def get_reason_groups(db: Session = Depends(get_db)):
    return db.query(ReasonGroup).order_by(ReasonGroup.name).all()


# =========================
# GET REASONS BY GROUP (подпричины)
# =========================
@router.get("/reasons")
def get_reasons(group_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(Reason)

    if group_id:
        query = query.filter(Reason.group_id == group_id)

    return query.order_by(Reason.name).all()


@router.get("/zouit-types")
def get_zouit_types():
    return [{"id": name, "name": name} for name in ZOUIT_TYPES]


@router.get("/owners")
def get_owners():
    return [{"id": name, "name": name} for name in OWNER_TYPES]


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
