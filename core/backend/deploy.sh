#!/bin/bash

# UNIBOS Backend Deployment Script
# This script handles the deployment of UNIBOS backend to production

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting UNIBOS Backend Deployment...${NC}"

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo -e "${RED}This script should not be run as root!${NC}"
   exit 1
fi

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo -e "${RED}Error: .env file not found!${NC}"
    exit 1
fi

# Function to check command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check required commands
REQUIRED_COMMANDS=("python3" "pip3" "postgresql" "redis-cli" "nginx" "systemctl")
for cmd in "${REQUIRED_COMMANDS[@]}"; do
    if ! command_exists "$cmd"; then
        echo -e "${RED}Error: $cmd is not installed!${NC}"
        exit 1
    fi
done

echo -e "${GREEN}1. Creating virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate

echo -e "${GREEN}2. Installing Python dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

echo -e "${GREEN}3. Running database migrations...${NC}"
python manage.py migrate --noinput

echo -e "${GREEN}4. Creating superuser (if not exists)...${NC}"
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@unibos.com', 'changeme')"

echo -e "${GREEN}5. Collecting static files...${NC}"
python manage.py collectstatic --noinput

echo -e "${GREEN}6. Running tests...${NC}"
python manage.py test --parallel --keepdb

echo -e "${GREEN}7. Checking deployment readiness...${NC}"
python manage.py check --deploy

echo -e "${GREEN}8. Setting up log directories...${NC}"
sudo mkdir -p /var/log/unibos
sudo chown $USER:$USER /var/log/unibos

echo -e "${GREEN}9. Configuring systemd service...${NC}"
sudo cp unibos.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable unibos.service

echo -e "${GREEN}10. Configuring Nginx...${NC}"
sudo cp nginx.conf /etc/nginx/sites-available/unibos
sudo ln -sf /etc/nginx/sites-available/unibos /etc/nginx/sites-enabled/
sudo nginx -t

echo -e "${GREEN}11. Starting services...${NC}"
sudo systemctl restart unibos.service
sudo systemctl restart nginx

echo -e "${GREEN}12. Setting up Celery services...${NC}"
sudo cp unibos-celery.service /etc/systemd/system/
sudo cp unibos-celery-beat.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable unibos-celery.service
sudo systemctl enable unibos-celery-beat.service
sudo systemctl restart unibos-celery.service
sudo systemctl restart unibos-celery-beat.service

echo -e "${GREEN}13. Checking service status...${NC}"
sudo systemctl status unibos.service --no-pager
sudo systemctl status unibos-celery.service --no-pager
sudo systemctl status unibos-celery-beat.service --no-pager

echo -e "${GREEN}14. Running health check...${NC}"
curl -f http://localhost/health/ || echo -e "${RED}Health check failed!${NC}"

echo -e "${GREEN}Deployment completed successfully!${NC}"
echo -e "${YELLOW}Don't forget to:${NC}"
echo -e "${YELLOW}- Update your DNS records${NC}"
echo -e "${YELLOW}- Configure SSL certificates (certbot)${NC}"
echo -e "${YELLOW}- Set up monitoring alerts${NC}"
echo -e "${YELLOW}- Configure backup scripts${NC}"
echo -e "${YELLOW}- Change the default admin password${NC}"