#!/bin/bash
cd "$(dirname "$0")"

# Check for virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
fi

# Install minimal requirements
echo "Installing requirements..."
pip install -q django djangorestframework django-cors-headers python-dotenv

# Set Django settings
export DJANGO_SETTINGS_MODULE=unibos_backend.settings.emergency

# Run migrations
python manage.py migrate --run-syncdb >/dev/null 2>&1

# Create superuser if needed
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@unibos.com', 'unibos123')
    print('Created default superuser (admin/unibos123)')
" 2>/dev/null

# Start server
echo "Backend server starting on http://localhost:8000"
exec python manage.py runserver 0.0.0.0:8000
