from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
from threading import Lock

import os

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session

from core.security import ACCESS_TOKEN_EXPIRE_SECONDS, create_access_token, get_current_user, get_db, verify_password
from models.user import User
from schemas.auth import LoginRequest, LoginResponse


router = APIRouter(tags=["auth"])
MAX_FAILED_ATTEMPTS = 5
FAILED_ATTEMPT_WINDOW = timedelta(minutes=10)
failed_attempts: dict[str, deque[datetime]] = defaultdict(deque)
attempts_lock = Lock()


def login_key(request: Request, username: str) -> str:
    forwarded = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
    client_ip = forwarded or (request.client.host if request.client else "unknown")
    return f"{client_ip}:{username.casefold()}"


def enforce_login_limit(key: str) -> None:
    cutoff = datetime.now(timezone.utc) - FAILED_ATTEMPT_WINDOW
    with attempts_lock:
        attempts = failed_attempts[key]
        while attempts and attempts[0] < cutoff:
            attempts.popleft()
        if len(attempts) >= MAX_FAILED_ATTEMPTS:
            raise HTTPException(429, "Too many login attempts. Try again later.")


def record_failed_login(key: str) -> None:
    with attempts_lock:
        failed_attempts[key].append(datetime.now(timezone.utc))


@router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest, request: Request, response: Response, db: Session = Depends(get_db)):
    key = login_key(request, data.username)
    enforce_login_limit(key)
    user = db.query(User).filter(User.username == data.username).first()

    if not user or user.disabled_at is not None or not verify_password(data.password, user.password):
        record_failed_login(key)
        raise HTTPException(status_code=401, detail="Invalid credentials")

    with attempts_lock:
        failed_attempts.pop(key, None)
    access_token = create_access_token({"sub": str(user.id), "role": user.role})
    response.set_cookie(
        key="session",
        value=access_token,
        max_age=ACCESS_TOKEN_EXPIRE_SECONDS,
        httponly=True,
        secure=os.getenv("ENVIRONMENT", "development").lower() == "production",
        samesite="strict",
        path="/",
    )
    return LoginResponse(
        id=user.id,
        username=user.username,
        role=user.role,
        full_name=user.full_name,
    )


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("session", path="/", samesite="strict")
    return {"status": "ok"}


@router.get("/session", response_model=LoginResponse)
def session(current_user: User = Depends(get_current_user)):
    return LoginResponse(
        id=current_user.id,
        username=current_user.username,
        role=current_user.role,
        full_name=current_user.full_name,
    )
