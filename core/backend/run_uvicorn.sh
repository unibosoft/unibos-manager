#!/bin/bash
# Development server with Uvicorn directly (fast reload, debug mode)
# Use this for local development

cd "$(dirname "$0")"

export DJANGO_SETTINGS_MODULE=unibos_backend.settings.development

echo "Starting UNIBOS Backend with Uvicorn (Development Mode)"
echo "=========================================="
echo "Server: http://localhost:8000"
echo "WebSocket Support: Enabled"
echo "Auto-reload: Enabled"
echo "=========================================="

./venv/bin/uvicorn unibos_backend.asgi:application \
    --host 0.0.0.0 \
    --port 8000 \
    --reload \
    --reload-dir apps \
    --reload-dir unibos_backend \
    --log-level info \
    --access-log
