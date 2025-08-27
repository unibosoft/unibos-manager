#!/bin/bash
# Rocksteady deployment configuration - single source of truth
# This file contains all configuration for rocksteady deployments

# Server configuration
export ROCKSTEADY_HOST="rocksteady"
export ROCKSTEADY_USER="ubuntu"
export ROCKSTEADY_DIR="~/unibos"

# Python configuration
export PYTHON_VERSION="python3"
export VENV_DIR="venv"

# Database configuration
export DB_NAME="unibos_db"
export DB_USER="unibos_user"
export DB_PASSWORD="unibos_password"
export DB_HOST="localhost"
export DB_PORT="5432"

# Redis configuration
export REDIS_HOST="localhost"
export REDIS_PORT="6379"
export REDIS_DB="0"

# Django configuration
export DJANGO_PORT="8000"
export DJANGO_SETTINGS_MODULE="unibos_backend.settings.production"
export SECRET_KEY="change-this-to-secure-random-key-in-production"

# Required Python packages (minimal)
export CORE_PACKAGES="Django==5.0.1 djangorestframework==3.14.0"
export DB_PACKAGES="psycopg2-binary==2.9.9 redis==5.0.1 django-redis==5.4.0"
export ESSENTIAL_PACKAGES="django-cors-headers==4.3.1 django-environ==0.11.2 django-filter==23.5"
export AUTH_PACKAGES="djangorestframework-simplejwt==5.3.1 PyJWT==2.8.0 pyotp==2.9.0"
export UTIL_PACKAGES="whitenoise==6.6.0 user-agents==2.2.0 python-json-logger==2.0.7 django-prometheus==2.3.1"

# All packages combined
export ALL_PACKAGES="$CORE_PACKAGES $DB_PACKAGES $ESSENTIAL_PACKAGES $AUTH_PACKAGES $UTIL_PACKAGES"

# Rsync exclusions - CRITICAL: Never sync archive folder!
export RSYNC_EXCLUDE=".git,venv,__pycache__,*.pyc,node_modules,*.log,db.sqlite3,.DS_Store,archive,archive/,archive/*,quarantine,*.sql,data_db,logs,staticfiles"

# Required directories
export REQUIRED_DIRS="logs staticfiles media"

# Connection test function
test_ssh_connection() {
    ssh -o ConnectTimeout=5 -o BatchMode=yes $ROCKSTEADY_HOST echo "connected" >/dev/null 2>&1
    return $?
}

# SSH command wrapper
run_on_rocksteady() {
    ssh $ROCKSTEADY_HOST "$@"
}

# Create .env content
generate_env_content() {
    cat << EOF
DEBUG=False
SECRET_KEY=$SECRET_KEY
ALLOWED_HOSTS=$ROCKSTEADY_HOST,localhost,127.0.0.1,0.0.0.0
DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME
REDIS_URL=redis://$REDIS_HOST:$REDIS_PORT/$REDIS_DB
CORS_ALLOWED_ORIGINS=http://localhost:$DJANGO_PORT,http://127.0.0.1:$DJANGO_PORT,http://$ROCKSTEADY_HOST:$DJANGO_PORT
ENVIRONMENT=production
DJANGO_LOG_LEVEL=INFO
EOF
}

# Color output helpers
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_step() {
    echo -e "${BLUE}▶️  $1${NC}"
}

# Export functions for use in other scripts
export -f test_ssh_connection
export -f run_on_rocksteady
export -f generate_env_content
export -f print_info
export -f print_success
export -f print_error
export -f print_warning
export -f print_step