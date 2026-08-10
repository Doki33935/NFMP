# backend/Dockerfile

FROM python:3.12-slim

WORKDIR /app

# системные зависимости (для psycopg2 / SQLAlchemy)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# зависимости Python
COPY requirements.txt .

RUN python -m pip install --no-cache-dir --upgrade pip==26.1.2 \
    -i https://pypi.org/simple \
    && python -m pip install --no-cache-dir -r requirements.txt \
    -i https://pypi.org/simple

# копируем код
COPY . .

# запускаем FastAPI
CMD ["sh", "-c", "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000 --workers ${UVICORN_WORKERS:-2}"]
