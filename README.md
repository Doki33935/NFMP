# NFMP

NFMP - веб-приложение для учета и мониторинга природных пожаров.

Состав проекта:

- `backend` - FastAPI API, PostgreSQL, Alembic migrations.
- `client-web` - React/Vite интерфейс.
- `db` - PostgreSQL 16.
- `db-backup` - автоматические резервные копии PostgreSQL.

## Быстрый запуск

Требования:

- Docker
- Docker Compose plugin
- Git

Клонировать проект:

```powershell
git clone https://github.com/Doki33935/NFMP.git
cd NFMP
git checkout dev
```

Создать `.env` из примера:

```powershell
copy .env.example .env
```

Минимальные значения по умолчанию:

```env
POSTGRES_USER=fire_user
POSTGRES_PASSWORD=fire_pass
POSTGRES_DB=fire_db
POSTGRES_PORT=5432
SECRET_KEY=change-me
BACKUP_INTERVAL_SECONDS=2592000
BACKUP_RETENTION_DAYS=14
TZ=Asia/Yekaterinburg
```

На рабочем сервере замените `SECRET_KEY` на длинную случайную строку.

Запуск:

```powershell
docker compose up -d --build
```

Проверка:

```powershell
docker compose ps
docker compose logs --tail=100 backend
```

Адреса:

- Frontend: `http://localhost:3000`
- Backend Swagger: `http://localhost:8000/docs`
- PostgreSQL: `localhost:5432`

Первый пользователь на пустой базе:

- логин: `111`
- пароль: `111`
- роль: `admin`

## Структура Docker-сервисов

```text
db          PostgreSQL 16
backend     FastAPI API, порт 8000
client-web  React/Vite, порт 3000
db-backup   периодические бекапы БД
```

Данные PostgreSQL хранятся в Docker volume `postgres_data`.

Папка `backups/` примонтирована в backend и backup-контейнер. Сами `.dump` файлы игнорируются git, в репозитории хранится только `backups/.gitkeep`.

## Миграции

Backend при запуске применяет миграции автоматически:

```text
alembic upgrade head
```

Ручные команды:

```powershell
docker compose exec backend alembic current
docker compose exec backend alembic history
docker compose exec backend alembic upgrade head
```

## Бекапы

Автоматический бекап выполняет сервис `db-backup`.

По умолчанию:

- период: `2592000` секунд, примерно 30 дней;
- хранение старых дампов: `14` дней;
- папка: `backups/`.

Настройки задаются в `.env`:

```env
BACKUP_INTERVAL_SECONDS=2592000
BACKUP_RETENTION_DAYS=14
```

Запустить backup-сервис:

```powershell
docker compose up -d db-backup
```

Сделать бекап вручную на Windows:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\backup-db.ps1
```

Восстановить конкретный бекап на Windows:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\restore-db.ps1 -BackupFile backups\fire_db_YYYY-MM-DD_HH-mm-ss.dump
```

Важно: восстановление заменяет содержимое базы. Перед восстановлением сделайте свежий бекап.

## Reset к последнему бекапу

В приложении оставлен один endpoint для отката БД:

```text
POST /admin/reset
```

Он требует Bearer token пользователя с ролью `admin` и восстанавливает самый свежий файл `backups/fire_db_*.dump`.

Пример:

```powershell
curl -X POST http://localhost:8000/admin/reset -H "Authorization: Bearer ADMIN_TOKEN"
```

## Полезные команды

Запустить сервисы:

```powershell
docker compose up -d
```

Остановить сервисы:

```powershell
docker compose down
```

Перезапустить все:

```powershell
docker compose restart
```

Перезапустить только backend:

```powershell
docker compose restart backend
```

Пересобрать без удаления данных БД:

```powershell
docker compose down
docker compose build --no-cache
docker compose up -d
```

Смотреть логи:

```powershell
docker compose logs -f
docker compose logs -f backend
docker compose logs -f client-web
docker compose logs -f db
docker compose logs -f db-backup
```

Последние строки логов backend:

```powershell
docker compose logs --tail=200 backend
```

Зайти в PostgreSQL:

```powershell
docker compose exec db psql -U fire_user -d fire_db
```

Проверить пользователей и пожары:

```powershell
docker compose exec db psql -U fire_user -d fire_db -c "select id, username, role, full_name from users order by id;"
docker compose exec db psql -U fire_user -d fire_db -c "select count(*) as fires from fires;"
```

## Проверки перед commit/push

Backend:

```powershell
docker compose exec -T backend python -m compileall api core db models schemas main.py
```

Frontend:

```powershell
docker compose exec -T client-web npm run build
```

Git whitespace check:

```powershell
git diff --check
```

## Обновление на сервере

```powershell
cd NFMP
git pull origin dev
docker compose up -d --build
docker compose ps
docker compose logs --tail=100 backend
```

## Что не хранится в git

Не коммитятся:

- `.env`
- `backups/*.dump`
- `node_modules`
- Python cache/build артефакты

Для передачи чистой стартовой БД используйте свежий `.dump` в `backups/` на сервере. Endpoint `/admin/reset` всегда берет самый новый dump из этой папки.
