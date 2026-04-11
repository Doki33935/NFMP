# backend/Dockerfile

FROM python:3.12-slim

WORKDIR /app

# системные зависимости (для psycopg2 / SQLAlchemy)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# зависимости Python
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt \
    -i https://pypi.org/simple

# копируем код
COPY . .

# запускаем FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]