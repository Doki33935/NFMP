#!/bin/sh
set -eu

BACKUP_INTERVAL_SECONDS="${BACKUP_INTERVAL_SECONDS:-86400}"
BACKUP_RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-7}"
BACKUP_RETENTION_COUNT="${BACKUP_RETENTION_COUNT:-7}"
BACKUP_DIR="${BACKUP_DIR:-/backups}"
BACKUP_ON_START="${BACKUP_ON_START:-true}"
DB_HOST="${POSTGRES_HOST:-db}"

mkdir -p "$BACKUP_DIR"

until pg_isready -h "$DB_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB"; do
  echo "Waiting for PostgreSQL before backup..."
  sleep 5
done

until [ "$(psql -h "$DB_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -tAc "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE';")" != "0" ]; do
  echo "Waiting for database schema before backup..."
  sleep 5
done

if [ "$BACKUP_ON_START" != "true" ]; then
  echo "Initial automatic backup is disabled. Next backup in $BACKUP_INTERVAL_SECONDS seconds."
  sleep "$BACKUP_INTERVAL_SECONDS"
fi

while true; do
  timestamp="$(date +%Y-%m-%d_%H-%M-%S)"
  backup_file="$BACKUP_DIR/fire_db_${timestamp}.dump"
  backup_tmp="$backup_file.tmp"

  echo "Creating backup: $backup_file"
  rm -f "$backup_tmp"
  pg_dump \
    -h "$DB_HOST" \
    -U "$POSTGRES_USER" \
    -d "$POSTGRES_DB" \
    -F c \
    -f "$backup_tmp"
  pg_restore --list "$backup_tmp" >/dev/null
  mv "$backup_tmp" "$backup_file"

  find "$BACKUP_DIR" -name "fire_db_*.dump" -type f -size 0 -delete
  find "$BACKUP_DIR" -name "fire_db_*.dump" -type f -mtime +"$BACKUP_RETENTION_DAYS" -delete
  ls -1t "$BACKUP_DIR"/fire_db_*.dump 2>/dev/null \
    | awk "NR > $BACKUP_RETENTION_COUNT" \
    | xargs -r rm -f
  echo "Backup complete: $backup_file"

  sleep "$BACKUP_INTERVAL_SECONDS"
done
