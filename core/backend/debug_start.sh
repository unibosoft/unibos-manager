#!/bin/bash
# Debug startup script for UNIBOS Backend

echo "Starting UNIBOS Backend in debug mode..."

# Navigate to backend directory
cd "$(dirname "$0")"

# Activate virtual environment if it exists
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
pip install django djangorestframework django-cors-headers python-dotenv

# Use emergency settings
export DJANGO_SETTINGS_MODULE=unibos_backend.settings.emergency

# Try to run the server with error output
echo "Starting server..."
python manage.py runserver 0.0.0.0:8000 2>&1