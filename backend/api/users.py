from datetime import datetime, timezone
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.user import PasswordChange, UserCreate, UserUpdate
from models.user import User
from core.security import get_db, hash_password, verify_password, get_current_user, require_role

logger = logging.getLogger(__name__)

router = APIRouter(tags=["users"])

ALLOWED_ROLES = {"dispatcher", "inspector", "admin", "chief"}


def serialize_user(user: User) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "role": user.role,
        "full_name": user.full_name,
        "is_active": user.disabled_at is None,
    }


@router.get("/users")
def get_users(
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_role("admin")),
):
    users = db.query(User).all()
    return [serialize_user(u) for u in users]


@router.post("/users")
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_role("admin")),
):
    existing = db.query(User).filter(User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    if user.role not in ALLOWED_ROLES:
        raise HTTPException(status_code=400, detail="Invalid role")

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

    return serialize_user(user_obj)


@router.put("/users/{user_id}")
def update_user(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = data.model_dump(exclude_unset=True)

    if current_user.role != "admin":
        update_data.pop("role", None)
        update_data.pop("password", None)
        update_data.pop("password_confirmation", None)

    username = update_data.get("username")
    if username is not None:
        username = username.strip()
        if not username:
            raise HTTPException(status_code=400, detail="Username is required")
        existing = db.query(User).filter(User.username == username, User.id != user_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="User already exists")
        user.username = username

    full_name = update_data.get("full_name")
    if full_name is not None:
        full_name = full_name.strip()
        if not full_name:
            raise HTTPException(status_code=400, detail="Full name is required")
        user.full_name = full_name

    role = update_data.get("role")
    if role is not None:
        if role not in ALLOWED_ROLES:
            raise HTTPException(status_code=400, detail="Invalid role")
        if user.id == current_user.id and role != "admin":
            raise HTTPException(status_code=400, detail="Cannot remove your own admin role")
        user.role = role

    password = update_data.get("password")
    password_confirmation = update_data.get("password_confirmation")
    if password:
        if password_confirmation is None or password != password_confirmation:
            raise HTTPException(status_code=400, detail="Passwords do not match")
        user.password = hash_password(password)

    db.commit()
    db.refresh(user)
    logger.info(f"User updated: id={user.id}, username={user.username}")

    return serialize_user(user)


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

    user.disabled_at = datetime.now(timezone.utc)
    db.commit()
    logger.info(f"User disabled: id={user_id}, username={user.username}")

    return {"status": "disabled"}


@router.post("/users/{user_id}/restore")
def restore_user(
    user_id: int,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_role("admin")),
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.disabled_at = None
    db.commit()
    return serialize_user(user)


@router.put("/users/{user_id}/password")
def change_password(
    user_id: int,
    body: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if current_user.id == user_id:
        if not body.current_password or not verify_password(body.current_password, user.password):
            raise HTTPException(status_code=400, detail="Current password is incorrect")

    user.password = hash_password(body.new_password)
    db.commit()
    logger.info(f"Password changed for user id={user_id}")

    return {"status": "password changed"}
