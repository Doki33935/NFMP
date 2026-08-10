import os
import subprocess
from pathlib import Path

from db.session import engine


BACKUP_DIR = Path(os.getenv("BACKUP_DIR", "/backups"))


def quote_sql_literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def get_latest_backup() -> Path | None:
    backups = sorted(
        (path for path in BACKUP_DIR.glob("fire_db_*.dump") if path.stat().st_size > 0),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    return backups[0] if backups else None


def restore_latest_backup() -> Path:
    backup = get_latest_backup()
    if backup is None:
        raise FileNotFoundError(f"No backup files found in {BACKUP_DIR}")

    db_name = os.getenv("POSTGRES_DB", "fire_db")
    db_user = os.getenv("POSTGRES_USER", "fire_user")
    db_password = os.environ["POSTGRES_PASSWORD"]
    db_host = os.getenv("POSTGRES_HOST", "db")
    db_name_literal = quote_sql_literal(db_name)

    env = os.environ.copy()
    env["PGPASSWORD"] = db_password

    subprocess.run(["pg_restore", "--list", str(backup)], env=env, check=True)

    engine.dispose()

    subprocess.run(
        [
            "psql",
            "-h",
            db_host,
            "-U",
            db_user,
            "-d",
            "postgres",
            "-v",
            "ON_ERROR_STOP=1",
            "-c",
            (
                "SELECT pg_terminate_backend(pid) "
                "FROM pg_stat_activity "
                f"WHERE datname = {db_name_literal} AND pid <> pg_backend_pid();"
            ),
        ],
        env=env,
        check=True,
    )

    restore_result = subprocess.run(
        [
            "pg_restore",
            "-h",
            db_host,
            "-U",
            db_user,
            "-d",
            db_name,
            "--clean",
            "--if-exists",
            "--no-owner",
            "--no-privileges",
            str(backup),
        ],
        env=env,
        capture_output=True,
        text=True,
    )

    if restore_result.returncode != 0:
        stderr = restore_result.stderr or ""
        is_pg17_to_pg16_transaction_timeout_warning = (
            "unrecognized configuration parameter \"transaction_timeout\"" in stderr
            and "errors ignored on restore: 1" in stderr
        )
        if not is_pg17_to_pg16_transaction_timeout_warning:
            output = "\n".join(part for part in [restore_result.stdout, stderr] if part)
            raise RuntimeError(output.strip() or "pg_restore failed")

    subprocess.run(["alembic", "upgrade", "head"], env=env, check=True)

    engine.dispose()

    return backup
