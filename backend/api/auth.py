from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models.user import User
from schemas.auth import LoginRequest, LoginResponse
from core.security import verify_password, create_access_token, get_db

router = APIRouter(tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token({"sub": str(user.id), "role": user.role})

    return LoginResponse(
        id=user.id,
        username=user.username,
        role=user.role,
        full_name=user.full_name,
        access_token=access_token,
    )
