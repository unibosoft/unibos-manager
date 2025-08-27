#!/bin/bash
set -e

echo "Starting UNIBOS container setup..."

# Wait for database
echo "Waiting for PostgreSQL..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 1
done
echo "PostgreSQL is ready!"

# Wait for Redis
echo "Waiting for Redis..."
while ! nc -z ${REDIS_HOST:-redis} ${REDIS_PORT:-6379}; do
  sleep 1
done
echo "Redis is ready!"

# Change to backend directory
cd /app/backend

# Run migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if not exists
echo "Checking for superuser..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@unibos.local', 'admin123')
    print('Superuser created')
else:
    print('Superuser already exists')
"

# Start the application
echo "Starting UNIBOS application..."
exec "$@"