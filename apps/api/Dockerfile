FROM python:3.13-slim

WORKDIR /usr/src/app

COPY pyproject.toml .
COPY alembic.ini .
COPY alembic ./alembic
COPY src ./src

RUN pip install --no-cache-dir "./"

CMD ["sh", "-c", "python -m alembic -c alembic.ini upgrade head && if [ \"${RUN_ASSESSMENT_SEEDS:-0}\" = \"1\" ]; then python -m app.scripts.import_assessment_seeds_from_github --repo ${SEED_REPO:-Androgidon/prof-navigator} --ref ${SEED_REF:-main} --base-path ${SEED_BASE_PATH:-docs/ai-context/forTest}; fi && uvicorn app.main:create_app --factory --host 0.0.0.0 --port ${PORT:-8000}"]
