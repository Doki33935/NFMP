# NFMP

Веб-приложение для регистрации, оформления и мониторинга природных пожаров.

## Состав

- `backend` - FastAPI API, Alembic migrations, PostgreSQL access.
- `client-web` - React/Vite web interface.
- `db` - PostgreSQL 16.
- `db-restore` - одноразовая проверка и восстановление БД из последнего бекапа перед стартом backend.
- `db-backup` - периодические резервные копии PostgreSQL.

## Первый запуск

Требования:

- Docker
- Docker Compose plugin
- Git

Склонировать проект:

```powershell
git clone https://github.com/Doki33935/NFMP.git
cd NFMP
git checkout dev
```

Создать файл `.env` в корне проекта:

```env
POSTGRES_USER=fire_user
POSTGRES_PASSWORD=replace-with-a-strong-database-password
POSTGRES_DB=fire_db
POSTGRES_PORT=5432
SECRET_KEY=replace-with-a-random-secret-of-at-least-32-characters
INITIAL_ADMIN_USERNAME=admin
INITIAL_ADMIN_PASSWORD=replace-with-a-strong-initial-password
BACKUP_INTERVAL_SECONDS=86400
BACKUP_RETENTION_DAYS=7
BACKUP_RETENTION_COUNT=7
BACKUP_ON_START=true
TZ=Asia/Yekaterinburg
```

`SECRET_KEY`, пароль PostgreSQL и начальный пароль администратора должны быть уникальными случайными значениями. Начальный администратор создаётся только в пустой БД.

Запуск:

```powershell
docker compose up -d --build
```

Проверка:

```powershell
docker compose ps
docker compose logs --tail=100 backend
docker compose logs --tail=100 db-restore
docker compose logs --tail=100 db-backup
```

Адреса:

- Frontend: `http://localhost:3000`
- Backend Swagger: `http://localhost:8000/docs`
- PostgreSQL: `localhost:5432`

### Карта

Карта работает на Leaflet и OpenStreetMap без API-ключа. Поиск адресов выполняется
через Nominatim только по явному действию пользователя.

В `client-web/public/data/orenburg-municipalities.geojson` хранится локальный слой
42 муниципальных образований Оренбургской области. Исходный набор подготовлен
НИУ ВШЭ на основе геометрии OpenStreetMap и атрибутов Росстата (границы на
01.01.2021). Для повторной сборки слоя используется
`scripts/extract_orenburg_boundaries.py`.

## Production-запуск

Укажите в `.env` публичный адрес и разрешённый источник браузера:

```env
SITE_ADDRESS=fire.example.com
CORS_ORIGINS=https://fire.example.com
ENVIRONMENT=production
```

Запустите отдельный production-профиль:

```powershell
docker compose -f docker-compose.prod.yml up -d --build
```

В этом профиле наружу опубликованы только порты `80/443` Caddy. PostgreSQL и API доступны только во внутренней Docker-сети, Swagger отключён, а TLS-сертификат выпускается автоматически для корректно настроенного домена.

### Развёртывание на сервере Ubuntu

Поддерживаемый вариант: 64-битный Ubuntu 22.04 LTS или 24.04 LTS, минимум 2 CPU, 4 ГБ RAM и 20 ГБ свободного места. Установите Docker Engine и Compose plugin по [официальной инструкции Docker](https://docs.docker.com/engine/install/ubuntu/). Не используйте convenience script для production.

До запуска:

1. Создайте DNS-запись `A` домена на публичный IPv4 сервера. Если используется IPv6, также настройте корректную запись `AAAA`.
2. Разрешите входящие TCP-порты `80` и `443`, а также UDP `443`. PostgreSQL `5432` и backend `8000` наружу открывать не нужно.
3. Клонируйте ветку `dev` и подготовьте окружение:

```bash
git clone --branch dev --single-branch https://github.com/Doki33935/NFMP.git
cd NFMP
cp .env.example .env
mkdir -p backups
chmod 700 backups
chmod 600 .env
```

4. Сгенерируйте отдельные секреты и внесите их в `.env`:

```bash
openssl rand -hex 32
openssl rand -base64 24
```

Обязательные production-параметры:

```env
POSTGRES_USER=fire_user
POSTGRES_PASSWORD=<уникальный пароль БД>
POSTGRES_DB=fire_db
SECRET_KEY=<случайная строка не короче 32 символов>
INITIAL_ADMIN_USERNAME=admin
INITIAL_ADMIN_PASSWORD=<уникальный пароль не короче 12 символов>
ENVIRONMENT=production
SITE_ADDRESS=fire.example.com
CORS_ORIGINS=https://fire.example.com
BACKUP_INTERVAL_SECONDS=86400
BACKUP_RETENTION_DAYS=7
BACKUP_RETENTION_COUNT=7
BACKUP_ON_START=true
TZ=Asia/Yekaterinburg
```

5. Запустите production-профиль:

```bash
sudo docker compose -f docker-compose.prod.yml pull
sudo docker compose -f docker-compose.prod.yml up -d --build
sudo docker compose -f docker-compose.prod.yml ps
sudo docker compose -f docker-compose.prod.yml logs --tail=100 db-restore backend caddy db-backup
```

После запуска откройте `https://<SITE_ADDRESS>` и войдите под начальным администратором. При корректном DNS Caddy автоматически получает и продлевает HTTPS-сертификат; для этого сервер должен быть доступен из интернета по портам `80/443`. Сразу смените временный пароль администратора через профиль.

Проверка API из внутренней сети Compose:

```bash
sudo docker compose -f docker-compose.prod.yml exec -T backend \
  python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8000/health').read().decode())"
```

Обновление приложения:

```bash
git pull --ff-only origin dev
sudo docker compose -f docker-compose.prod.yml up -d --build
sudo docker compose -f docker-compose.prod.yml ps
```

Перед обновлением убедитесь, что в `backups/` есть свежий проверенный dump. Никогда не выполняйте `docker compose down -v`: ключ `-v` удалит volume PostgreSQL.

## Данные и восстановление

Данные PostgreSQL хранятся в Docker volume `postgres_data`.

Бекапы хранятся в папке `backups/` в формате `fire_db_YYYY-MM-DD_HH-MM-SS.dump`. Сами `.dump` файлы не коммитятся в git.

При запуске сервисов порядок такой:

1. `db` запускает PostgreSQL.
2. `db-restore` проверяет целевую БД.
3. Если БД отсутствует или в ней нет таблиц, `db-restore` восстанавливает последний непустой dump из `backups/`.
4. Если БД уже содержит таблицы, восстановление пропускается.
5. После успешного `db-restore` запускаются `backend` и `db-backup`.

Это закрывает сценарии:

- сервер перезапущен, volume БД на месте - данные остаются как есть;
- БД была удалена или volume пустой - сервис поднимет ее из последнего бекапа;
- бекапов нет - backend создаст чистую БД миграциями и seed-данными.

## Автоматические бекапы

`db-backup` делает резервную копию раз в 24 часа:

```env
BACKUP_INTERVAL_SECONDS=86400
```

При старте backup-сервиса сразу создаётся свежая копия:

```env
BACKUP_ON_START=true
```

Копии старше 7 дней удаляются; дополнительно хранится не более 7 последних файлов:

```env
BACKUP_RETENTION_DAYS=7
BACKUP_RETENTION_COUNT=7
```

Каждый dump проверяется через `pg_restore --list` до публикации готового файла.

Проверить backup-сервис:

```powershell
docker compose logs -f db-backup
```

## Ручной бекап и восстановление

Создать бекап вручную на Windows:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\backup-db.ps1
```

Восстановить конкретный dump вручную:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\restore-db.ps1 -BackupFile backups\fire_db_YYYY-MM-DD_HH-mm-ss.dump
```

Endpoint отката к последнему dump по умолчанию отключён. Для временного включения задайте `ENABLE_REMOTE_RESTORE=true`; после операции параметр следует убрать:

```text
POST /admin/reset
```

Endpoint требует активную сессию администратора. На рабочем сервере предпочтительно выполнять восстановление вручную в окне обслуживания.

## Полезные команды

Запустить сервисы:

```powershell
docker compose up -d
```

Остановить сервисы без удаления данных:

```powershell
docker compose down
```

Пересобрать и запустить:

```powershell
docker compose up -d --build
```

Смотреть логи:

```powershell
docker compose logs -f
docker compose logs -f backend
docker compose logs -f client-web
docker compose logs -f db
docker compose logs -f db-restore
docker compose logs -f db-backup
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

Compose:

```powershell
docker compose config --quiet
```

Git whitespace check:

```powershell
git diff --check
```

## Важно

Не используйте `docker compose down -v` на рабочем сервере без свежего бекапа. Эта команда удаляет Docker volumes, включая PostgreSQL data.

Если сломался только frontend `node_modules`, можно удалить только его volume:

```powershell
docker compose down
docker volume rm nfmp_client_web_node_modules
docker compose up -d --build
```

Не удаляйте `nfmp_postgres_data`, если не хотите восстановление БД из backup.
