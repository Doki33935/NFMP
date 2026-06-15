param(
    [string]$OutputDir = "backups"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir | Out-Null
}

$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$backupFile = Join-Path $OutputDir "fire_db_$timestamp.dump"

docker compose exec -T db pg_dump `
    -U fire_user `
    -d fire_db `
    -F c `
    -f "/tmp/fire_db_$timestamp.dump"

docker compose cp "db:/tmp/fire_db_$timestamp.dump" $backupFile
docker compose exec -T db rm "/tmp/fire_db_$timestamp.dump"

Write-Host "Backup created: $backupFile"
