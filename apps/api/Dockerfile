FROM python:3.13-slim

WORKDIR /usr/src/app

COPY pyproject.toml .
COPY alembic.ini .
COPY alembic ./alembic
COPY src ./src

RUN pip install --no-cache-dir "./"

CMD ["uvicorn", "app.main:create_app", "--host", "0.0.0.0", "--port", "8000"]
