#!/bin/sh
set -eu

BACKUP_INTERVAL_SECONDS="${BACKUP_INTERVAL_SECONDS:-2592000}"
BACKUP_RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-14}"
BACKUP_DIR="${BACKUP_DIR:-/backups}"

mkdir -p "$BACKUP_DIR"

while true; do
  timestamp="$(date +%Y-%m-%d_%H-%M-%S)"
  backup_file="$BACKUP_DIR/fire_db_${timestamp}.dump"

  echo "Creating backup: $backup_file"
  pg_dump \
    -h db \
    -U "$POSTGRES_USER" \
    -d "$POSTGRES_DB" \
    -F c \
    -f "$backup_file"

  find "$BACKUP_DIR" -name "fire_db_*.dump" -type f -mtime +"$BACKUP_RETENTION_DAYS" -delete
  echo "Backup complete: $backup_file"

  sleep "$BACKUP_INTERVAL_SECONDS"
done
