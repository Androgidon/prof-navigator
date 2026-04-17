#!/bin/sh
set -eu

echo "[startup] Applying migrations"
python -m alembic -c alembic.ini upgrade head

if [ "${RUN_ASSESSMENT_SEEDS:-0}" = "1" ]; then
  echo "SEED STARTED"
  python -m src.app.scripts.import_assessment_seeds_from_github \
    --repo "${SEED_REPO:-Androgidon/prof-navigator}" \
    --ref "${SEED_REF:-main}" \
    --base-path "${SEED_BASE_PATH:-docs/ai-context/forTest}"
  echo "SEED COMPLETED"
else
  echo "[startup] Seed skipped (RUN_ASSESSMENT_SEEDS=${RUN_ASSESSMENT_SEEDS:-0})"
fi

exec uvicorn src.app.main:create_app --factory --host 0.0.0.0 --port "${PORT:-8000}"
