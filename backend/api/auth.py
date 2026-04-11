from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from fastapi import Depends
from db.session import SessionLocal
from models.user import User
from schemas.auth import LoginRequest, LoginResponse

router = APIRouter(tags=["auth"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # пока без хешей (dev режим)
    if user.password_hash != data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return LoginResponse(
        id=user.id,
        username=user.username,
        role=user.role,
        full_name=user.full_name
    )