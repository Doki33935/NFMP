from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.user import UserCreate
from models.user import User
from core.security import get_db, hash_password, get_current_user, require_role
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["users"])


@router.get("/users")
def get_users(
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_role("admin")),
):
    users = db.query(User).all()
    return [
        {
            "id": u.id,
            "username": u.username,
            "role": u.role,
            "full_name": u.full_name,
        }
        for u in users
    ]


@router.post("/users")
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_role("admin")),
):
    existing = db.query(User).filter(User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    user_obj = User(
        username=user.username,
        password=hash_password(user.password),
        role=user.role,
        full_name=user.full_name,
    )

    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)

    logger.info(f"User created: id={user_obj.id}, username={user_obj.username}")

    return {
        "id": user_obj.id,
        "username": user_obj.username,
        "role": user_obj.role,
    }


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.error(f"Attempted to delete non-existent user id={user_id}")
        raise HTTPException(status_code=404, detail="User not found")

    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")

    try:
        db.delete(user)
        db.commit()
        logger.info(f"User deleted: id={user_id}, username={user.username}")
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete user id={user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete user")

    return {"status": "deleted"}


@router.put("/users/{user_id}/password")
def change_password(
    user_id: int,
    body: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_password = body.get("new_password")
    if not new_password or len(new_password) < 3:
        raise HTTPException(status_code=400, detail="Password too short")

    user.password = hash_password(new_password)
    db.commit()
    logger.info(f"Password changed for user id={user_id}")

    return {"status": "password changed"}
