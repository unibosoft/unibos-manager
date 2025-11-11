#\!/bin/bash
# UNIBOS Backend Emergency Start Script - PostgreSQL with minimal dependencies

echo "🚀 Starting UNIBOS Backend (Emergency Mode - PostgreSQL)..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if a port is available
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 1
    fi
    return 0
}

# Check if port 8000 is available
if \! check_port 8000; then
    echo -e "${RED}❌ Port 8000 is already in use\!${NC}"
    echo "Backend may already be running."
    # Get PID and check if it's Django
    PID=$(lsof -t -i:8000)
    PROCESS_INFO=$(ps -p $PID -o command= 2>/dev/null || echo "Unknown")
    if [[ $PROCESS_INFO == *"manage.py"* ]] || [[ $PROCESS_INFO == *"runserver"* ]]; then
        echo -e "${GREEN}✓ Django backend is already running (PID: $PID)${NC}"
        exit 0
    else
        echo "Another service is using port 8000: $PROCESS_INFO"
        echo "To stop it: kill -9 $PID"
        exit 1
    fi
fi

# Use emergency settings explicitly
export DJANGO_SETTINGS_MODULE=unibos_backend.settings.emergency

# Check if Django is installed
if \! python -c "import django" 2>/dev/null; then
    echo -e "${YELLOW}Installing minimal dependencies...${NC}"
    pip install django djangorestframework django-cors-headers --quiet
fi

# Run migrations silently
echo "🔄 Preparing database..."
python manage.py migrate --run-syncdb >/dev/null 2>&1

# Create superuser if it doesn't exist
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@unibos.com', 'unibos123')
    print('✓ Created default superuser (admin/unibos123)')
" 2>/dev/null

# Collect static files silently
python manage.py collectstatic --noinput >/dev/null 2>&1

# Start the server
echo -e "${GREEN}✅ Django backend started successfully${NC}"
echo "🌐 URL: http://localhost:8000"
echo "👤 Login: admin/unibos123"
echo ""

# Run the server
exec python manage.py runserver 0.0.0.0:8000
