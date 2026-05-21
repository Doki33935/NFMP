from fastapi import APIRouter, Depends
from db.reset_db import reset_database
from core.security import require_role
from models.user import User

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/resetdb")
def reset_db(_current_user: User = Depends(require_role("admin"))):
    reset_database()
    return {"status": "database reset complete"}
