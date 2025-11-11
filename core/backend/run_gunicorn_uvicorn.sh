#!/bin/bash
# Production-like server with Gunicorn + Uvicorn workers
# Use this to test production setup locally

cd "$(dirname "$0")"

export DJANGO_SETTINGS_MODULE=unibos_backend.settings.development

echo "Starting UNIBOS Backend with Gunicorn + Uvicorn Workers"
echo "=========================================="
echo "Server: http://localhost:8000"
echo "WebSocket Support: Enabled"
echo "Workers: $(python3 -c 'import multiprocessing; print(multiprocessing.cpu_count() * 2 + 1)')"
echo "Worker Class: uvicorn.workers.UvicornWorker"
echo "=========================================="

./venv/bin/gunicorn unibos_backend.asgi:application \
    --config gunicorn.conf.py \
    --log-level info \
    --access-logfile - \
    --error-logfile -
