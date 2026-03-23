#!/bin/bash
set -e

echo "=== Co-Op API Container Starting ==="
echo "Starting supervisord (uvicorn + arq worker)..."

exec /usr/bin/supervisord -n -c /app/supervisord.conf
