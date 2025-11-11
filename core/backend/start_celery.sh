#!/bin/bash
# Start Celery Worker and Beat for UNIBOS Backend

DJANGO_SETTINGS_MODULE=unibos_backend.settings.development

# Check if already running
if pgrep -f "celery.*worker" > /dev/null; then
    echo "Celery worker already running"
else
    echo "Starting Celery worker..."
    nohup ./venv/bin/celery -A unibos_backend worker --loglevel=info > logs/celery_worker.log 2>&1 &
    echo "Celery worker started (PID: $!)"
fi

if pgrep -f "celery.*beat" > /dev/null; then
    echo "Celery beat already running"
else
    echo "Starting Celery beat..."
    nohup ./venv/bin/celery -A unibos_backend beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler > logs/celery_beat.log 2>&1 &
    echo "Celery beat started (PID: $!)"
fi

echo "✅ Celery services started"
echo "   Worker log: logs/celery_worker.log"
echo "   Beat log: logs/celery_beat.log"
