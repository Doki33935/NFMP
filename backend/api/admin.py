import os

from fastapi import APIRouter, Depends, HTTPException

from core.security import require_role
from db.backup_restore import restore_latest_backup
from models.user import User

router = APIRouter(prefix="/admin", tags=["admin"])


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
def reset_db(_current_user: User = Depends(require_role("admin"))):
    if os.getenv("ENABLE_REMOTE_RESTORE", "false").lower() != "true":
        raise HTTPException(status_code=404, detail="Not found")
    return restore_db_from_latest_backup()
