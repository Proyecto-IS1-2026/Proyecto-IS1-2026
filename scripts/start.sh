#!/usr/bin/env bash

set -e

export APP_ENV=production
export PYTHONPATH=src

uv run --locked --no-dev python - <<'PY'
from sqlalchemy import create_engine, text
from qanda.config import obtener_configuracion

engine = create_engine(
    obtener_configuracion().DATABASE_URL
)

with engine.begin() as connection:
    connection.execute(
        text("CREATE SCHEMA IF NOT EXISTS is1")
    )

engine.dispose()
PY

uv run --locked --no-dev alembic \
    -c migrations/alembic.ini upgrade head

exec uv run --locked --no-dev gunicorn \
    --bind "0.0.0.0:${PORT:-8000}" \
    --workers 1 \
    --timeout 120 \
    "qanda:create_app()"