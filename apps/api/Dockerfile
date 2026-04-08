FROM python:3.13-slim

WORKDIR /usr/src/app

COPY pyproject.toml .
COPY src ./src

RUN pip install --no-cache-dir "./"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
