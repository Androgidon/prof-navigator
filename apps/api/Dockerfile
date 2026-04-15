FROM python:3.13-slim

WORKDIR /usr/src/app

COPY pyproject.toml .
COPY alembic.ini .
COPY alembic ./alembic
COPY src ./src

RUN pip install --no-cache-dir "./"

CMD ["sh", "-c", "uvicorn app.main:create_app --factory --host 0.0.0.0 --port ${PORT:-8000}"]
