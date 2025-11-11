#!/bin/bash
# UNIBOS Backend startup script with automatic configuration detection

echo "🚀 Starting UNIBOS Backend..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a port is available
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 1
    fi
    return 0
}

# Check if virtual environment exists
if [ -d "venv" ]; then
    VENV_PATH="venv"
elif [ -d ".venv" ]; then
    VENV_PATH=".venv"
else
    echo -e "${RED}❌ No virtual environment found!${NC}"
    echo "Creating virtual environment..."
    python3 -m venv venv
    VENV_PATH="venv"
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source $VENV_PATH/bin/activate

# Install/update dependencies
echo "📦 Checking dependencies..."
pip install --quiet --upgrade pip

# Determine which settings to use based on available services
SETTINGS_MODULE=""
REQUIREMENTS_FILE=""

# Check for PostgreSQL (REQUIRED)
if command_exists psql && psql -U postgres -c '\l' >/dev/null 2>&1; then
    POSTGRES_AVAILABLE=true
    echo -e "${GREEN}✓ PostgreSQL detected${NC}"
else
    POSTGRES_AVAILABLE=false
    echo -e "${RED}❌ PostgreSQL not available${NC}"
    echo -e "${RED}PostgreSQL is required to run UNIBOS backend.${NC}"
    echo "Please install and start PostgreSQL before running this script."
    exit 1
fi

# Check for Redis
if command_exists redis-cli && redis-cli ping >/dev/null 2>&1; then
    REDIS_AVAILABLE=true
    echo -e "${GREEN}✓ Redis detected${NC}"
else
    REDIS_AVAILABLE=false
    echo -e "${YELLOW}⚠ Redis not available${NC}"
fi

# Select appropriate settings and requirements
if [ "$REDIS_AVAILABLE" = true ]; then
    SETTINGS_MODULE="unibos_backend.settings.development"
    REQUIREMENTS_FILE="requirements.txt"
    echo -e "${GREEN}✓ Using full development settings (PostgreSQL + Redis)${NC}"
else
    SETTINGS_MODULE="unibos_backend.settings.dev_no_redis"
    REQUIREMENTS_FILE="requirements-minimal.txt"
    echo -e "${YELLOW}⚠ Using settings without Redis (PostgreSQL only)${NC}"
fi

# Install appropriate requirements
echo "📦 Installing requirements from $REQUIREMENTS_FILE..."
pip install -q -r $REQUIREMENTS_FILE

# Export Django settings
export DJANGO_SETTINGS_MODULE=$SETTINGS_MODULE

# Check if port 8000 is available
if ! check_port 8000; then
    echo -e "${RED}❌ Port 8000 is already in use!${NC}"
    echo "Another server may be running. Please stop it first."
    echo ""
    echo "To find the process using port 8000:"
    echo "  lsof -i :8000"
    echo ""
    echo "To kill the process:"
    echo "  kill -9 \$(lsof -t -i:8000)"
    exit 1
fi

# Run migrations
echo "🔄 Running database migrations..."
python manage.py migrate --run-syncdb

# Create superuser if it doesn't exist
echo "👤 Checking for superuser..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@unibos.com', 'unibos123')
    print('✓ Created default superuser (admin/unibos123)')
else:
    print('✓ Superuser already exists')
"

# Collect static files (suppress output)
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput >/dev/null 2>&1 || true

# Start the server
echo ""
echo -e "${GREEN}✅ Starting Django development server${NC}"
echo "🌐 Server URL: http://localhost:8000"
echo "📝 API Documentation: http://localhost:8000/api/"
echo "👤 Admin Panel: http://localhost:8000/admin/"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run the server
python manage.py runserver 0.0.0.0:8000