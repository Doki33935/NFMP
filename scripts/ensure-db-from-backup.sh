#!/bin/sh
set -eu

BACKUP_DIR="${BACKUP_DIR:-/backups}"
DB_HOST="${POSTGRES_HOST:-db}"

sql_literal() {
  escaped="$(printf "%s" "$1" | sed "s/'/''/g")"
  printf "'%s'" "$escaped"
}

latest_backup() {
  if [ ! -d "$BACKUP_DIR" ]; then
    return 0
  fi

  find "$BACKUP_DIR" -maxdepth 1 -type f -name 'fire_db_*.dump' -size +0c | sort | tail -n 1
}

restore_backup() {
  backup_file="$1"

  if [ -z "$backup_file" ]; then
    echo "No non-empty fire_db_*.dump backups found in $BACKUP_DIR"
    echo "Database will be initialized by migrations."
    return 0
  fi

  echo "Restoring database '$POSTGRES_DB' from latest backup: $backup_file"

  restore_log="$(mktemp)"
  if pg_restore \
    -h "$DB_HOST" \
    -U "$POSTGRES_USER" \
    -d "$POSTGRES_DB" \
    --no-owner \
    --no-privileges \
    "$backup_file" \
    2>"$restore_log"; then
    rm -f "$restore_log"
    echo "Database restore complete: $backup_file"
    return 0
  fi

  if grep -q 'unrecognized configuration parameter "transaction_timeout"' "$restore_log" \
    && grep -q "errors ignored on restore: 1" "$restore_log"; then
    cat "$restore_log"
    rm -f "$restore_log"
    echo "Restore completed with PostgreSQL version compatibility warning."
    return 0
  fi

  cat "$restore_log"
  rm -f "$restore_log"
  echo "Database restore failed."
  return 1
}

until pg_isready -h "$DB_HOST" -U "$POSTGRES_USER" -d postgres; do
  echo "Waiting for PostgreSQL before restore check..."
  sleep 5
done

db_name_literal="$(sql_literal "$POSTGRES_DB")"
db_exists="$(psql -h "$DB_HOST" -U "$POSTGRES_USER" -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname = $db_name_literal;")"

if [ "$db_exists" != "1" ]; then
  echo "Database '$POSTGRES_DB' does not exist. Creating it before restore."
  createdb -h "$DB_HOST" -U "$POSTGRES_USER" "$POSTGRES_DB"
  restore_backup "$(latest_backup)"
  exit 0
fi

table_count="$(
  psql -h "$DB_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -tAc \
    "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE';"
)"

if [ "${table_count:-0}" = "0" ]; then
  echo "Database '$POSTGRES_DB' exists but has no public tables."
  restore_backup "$(latest_backup)"
  exit 0
fi

echo "Database '$POSTGRES_DB' already contains tables. Restore on startup is skipped."
