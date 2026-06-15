from fastapi import APIRouter, HTTPException, Request
from jose import JWTError, jwt

from core.security import ALGORITHM, SECRET_KEY
from db.backup_restore import restore_latest_backup
from db.session import SessionLocal
from models.user import User

router = APIRouter(prefix="/admin", tags=["admin"])


def require_admin_token(request: Request) -> User:
    auth_header = request.headers.get("authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = auth_header[7:]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    db = SessionLocal()
    try:
        try:
            user_id_int = int(user_id)
        except (TypeError, ValueError):
            raise HTTPException(status_code=401, detail="Invalid token")

        user = db.query(User).filter(User.id == user_id_int).first()
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        if user.role != "admin":
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    finally:
        db.close()


def restore_db_from_latest_backup():
    try:
        backup = restore_latest_backup()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Database restore failed: {exc}") from exc

    return {
        "status": "database restored from latest backup",
        "backup": backup.name,
    }


@router.post("/reset")
def reset_db(request: Request):
    require_admin_token(request)
    return restore_db_from_latest_backup()
