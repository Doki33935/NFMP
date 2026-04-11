from fastapi import APIRouter
from db.reset_db import reset_database

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/resetdb")
def reset_db():
    reset_database()
    return {"status": "database reset complete"}