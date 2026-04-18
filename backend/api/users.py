from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.user import UserCreate
from db.session import SessionLocal
from models.user import User

router = APIRouter(tags=["users"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/users")
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    existing = db.query(User).filter(User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    user_obj = User(
        username=user.username,
        password_hash=user.password,
        role=user.role,
        full_name=user.full_name
    )

    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)

    return {
        "id": user_obj.id,
        "username": user_obj.username,
        "role": user_obj.role
    }