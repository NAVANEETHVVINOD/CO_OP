#!/bin/bash
set -e

echo "=== Co-Op API Container Starting ==="
echo "Running database migrations..."
/opt/venv/bin/alembic upgrade head

echo "Starting supervisord (uvicorn + arq worker)..."
exec /usr/bin/supervisord -n -c /app/supervisord.conf
