param(
    [Parameter(Mandatory = $true)]
    [string]$BackupFile,

    [string]$Database = "fire_db"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $BackupFile)) {
    throw "Backup file not found: $BackupFile"
}

$containerFile = "/tmp/restore_fire_db.dump"

docker compose cp $BackupFile "db:$containerFile"

docker compose exec -T db pg_restore `
    -U fire_user `
    -d $Database `
    --clean `
    --if-exists `
    --no-owner `
    --no-privileges `
    $containerFile

docker compose exec -T db rm $containerFile

Write-Host "Database '$Database' restored from: $BackupFile"
