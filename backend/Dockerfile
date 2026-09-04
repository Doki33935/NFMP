# backend/Dockerfile

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN python -m pip install --no-cache-dir --upgrade pip==26.1.2 \
    -i https://pypi.org/simple \
    && python -m pip install --no-cache-dir -r requirements.txt \
    -i https://pypi.org/simple \
    && addgroup --system app \
    && adduser --system --ingroup app app

COPY --chown=app:app . .

USER app

CMD ["sh", "-c", "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000 --workers ${UVICORN_WORKERS:-2}"]
