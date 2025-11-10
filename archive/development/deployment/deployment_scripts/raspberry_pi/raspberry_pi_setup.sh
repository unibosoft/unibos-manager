#!/bin/bash
#
# UNIBOS Raspberry Pi Optimized Setup
# Tested on: Raspberry Pi 3B+, 4, Zero 2 W
#

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   UNIBOS Raspberry Pi Setup${NC}"
echo -e "${GREEN}========================================${NC}"

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo && ! grep -q "BCM" /proc/cpuinfo; then
    echo -e "${YELLOW}Warning: This doesn't appear to be a Raspberry Pi${NC}"
    read -p "Continue anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Get Pi model
PI_MODEL=$(cat /proc/device-tree/model 2>/dev/null || echo "Unknown")
echo -e "${BLUE}Detected: $PI_MODEL${NC}"

# Update system
echo -e "${BLUE}Updating system packages...${NC}"
sudo apt-get update
sudo apt-get upgrade -y

# Install dependencies
echo -e "${BLUE}Installing dependencies...${NC}"
sudo apt-get install -y \
    python3-pip \
    python3-venv \
    python3-dev \
    postgresql \
    postgresql-contrib \
    redis-server \
    nginx \
    git \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    libatlas-base-dev \
    libopenblas-dev \
    liblapack-dev \
    libhdf5-dev \
    supervisor

# Optimize for Raspberry Pi
echo -e "${BLUE}Applying Raspberry Pi optimizations...${NC}"

# Increase swap (important for compilation on low-memory Pis)
if [ $(free -m | awk '/^Swap:/ {print $2}') -lt 1024 ]; then
    echo -e "${YELLOW}Increasing swap size...${NC}"
    sudo dphys-swapfile swapoff
    sudo sed -i 's/CONF_SWAPSIZE=.*/CONF_SWAPSIZE=1024/' /etc/dphys-swapfile
    sudo dphys-swapfile setup
    sudo dphys-swapfile swapon
fi

# PostgreSQL optimization for Pi
sudo tee -a /etc/postgresql/*/main/postgresql.conf > /dev/null <<EOF

# Raspberry Pi Optimizations
shared_buffers = 128MB
work_mem = 2MB
maintenance_work_mem = 32MB
effective_cache_size = 256MB
checkpoint_segments = 16
checkpoint_completion_target = 0.9
wal_buffers = 4MB
max_connections = 50
EOF

# Redis optimization for Pi
sudo tee -a /etc/redis/redis.conf > /dev/null <<EOF

# Raspberry Pi Optimizations
maxmemory 256mb
maxmemory-policy allkeys-lru
save ""
EOF

# Setup PostgreSQL
echo -e "${BLUE}Setting up PostgreSQL...${NC}"
sudo systemctl enable postgresql
sudo systemctl start postgresql

sudo -u postgres psql <<EOF 2>/dev/null || true
CREATE USER unibos_user WITH PASSWORD 'unibos_password';
CREATE DATABASE unibos_db OWNER unibos_user;
GRANT ALL PRIVILEGES ON DATABASE unibos_db TO unibos_user;
EOF

# Setup project
echo -e "${BLUE}Setting up UNIBOS project...${NC}"
cd /home/pi

if [ ! -d "unibos" ]; then
    git clone https://github.com/unibosoft/unibos_dev.git unibos
fi

cd unibos/backend

# Create virtual environment
echo -e "${BLUE}Creating Python virtual environment...${NC}"
python3 -m venv venv --system-site-packages  # Use system packages to save space

source venv/bin/activate

# Install Python packages with Pi-specific options
echo -e "${BLUE}Installing Python packages (this may take a while on Pi)...${NC}"

# Install numpy and scipy from apt (pre-compiled for ARM)
sudo apt-get install -y python3-numpy python3-scipy

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install requirements with specific versions for Pi
cat > requirements_pi.txt <<EOF
# Core - minimal versions for Pi
Django==5.0.1
djangorestframework==3.14.0
psycopg2-binary==2.9.9
django-redis==5.4.0
redis==5.0.1
django-cors-headers==4.3.1
django-environ==0.11.2
PyJWT==2.8.0
whitenoise==6.6.0

# Lightweight server for Pi
gunicorn==23.0.0
EOF

pip install --no-cache-dir -r requirements_pi.txt

# Create .env file
cat > .env <<EOF
SECRET_KEY='django-insecure-pi-$(date +%s | sha256sum | base64 | head -c 32)'
DEBUG=False
DB_NAME=unibos_db
DB_USER=unibos_user
DB_PASSWORD=unibos_password
DB_HOST=localhost
DB_PORT=5432
ALLOWED_HOSTS=localhost,127.0.0.1,raspberrypi.local,$(hostname -I | awk '{print $1}')
EOF

# Run migrations
echo -e "${BLUE}Setting up database...${NC}"
python manage.py migrate
python manage.py collectstatic --noinput

# Setup Gunicorn service for Pi
echo -e "${BLUE}Setting up Gunicorn service...${NC}"
sudo tee /etc/systemd/system/gunicorn.service > /dev/null <<EOF
[Unit]
Description=UNIBOS Gunicorn daemon
After=network.target

[Service]
User=pi
Group=pi
WorkingDirectory=/home/pi/unibos/backend
ExecStart=/home/pi/unibos/backend/venv/bin/gunicorn \\
          --workers 2 \\
          --worker-class sync \\
          --worker-connections 50 \\
          --max-requests 100 \\
          --max-requests-jitter 10 \\
          --bind 0.0.0.0:8000 \\
          --timeout 60 \\
          unibos_backend.wsgi:application

EnvironmentFile=/home/pi/unibos/backend/.env
Environment="DJANGO_SETTINGS_MODULE=unibos_backend.settings.production"

Restart=on-failure
RestartSec=5

# CPU and Memory limits for Pi
CPUQuota=80%
MemoryLimit=512M

[Install]
WantedBy=multi-user.target
EOF

# Setup Nginx
echo -e "${BLUE}Configuring Nginx...${NC}"
sudo tee /etc/nginx/sites-available/unibos > /dev/null <<EOF
server {
    listen 80;
    server_name _;
    
    client_max_body_size 10M;  # Smaller limit for Pi
    
    location /static/ {
        alias /home/pi/unibos/backend/staticfiles/;
        expires 30d;
    }
    
    location /media/ {
        alias /home/pi/unibos/backend/media/;
        expires 7d;
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/unibos /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Enable and start services
echo -e "${BLUE}Starting services...${NC}"
sudo systemctl daemon-reload
sudo systemctl enable redis-server postgresql nginx gunicorn
sudo systemctl restart redis-server postgresql nginx gunicorn

# Setup auto-start on boot
echo -e "${BLUE}Setting up auto-start...${NC}"
sudo tee /etc/rc.local > /dev/null <<EOF
#!/bin/sh -e
# Start UNIBOS services
systemctl start postgresql
systemctl start redis-server
systemctl start gunicorn
systemctl start nginx
exit 0
EOF

sudo chmod +x /etc/rc.local

# Create monitoring script
echo -e "${BLUE}Creating monitoring script...${NC}"
cat > /home/pi/monitor_unibos.sh <<'EOF'
#!/bin/bash
# UNIBOS Pi Monitor

echo "=== UNIBOS Raspberry Pi Status ==="
echo
echo "CPU Temperature: $(vcgencmd measure_temp | cut -d= -f2)"
echo "Memory Usage: $(free -h | grep Mem | awk '{print $3 "/" $2}')"
echo "Disk Usage: $(df -h / | tail -1 | awk '{print $3 "/" $2 " (" $5 ")"}')"
echo
echo "Services:"
systemctl is-active postgresql && echo "✓ PostgreSQL" || echo "✗ PostgreSQL"
systemctl is-active redis-server && echo "✓ Redis" || echo "✗ Redis"
systemctl is-active gunicorn && echo "✓ Gunicorn" || echo "✗ Gunicorn"
systemctl is-active nginx && echo "✓ Nginx" || echo "✗ Nginx"
echo
echo "UNIBOS URL: http://$(hostname -I | awk '{print $1}')"
EOF

chmod +x /home/pi/monitor_unibos.sh

# Final message
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   Installation Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo
echo -e "UNIBOS is now running on your Raspberry Pi!"
echo
echo -e "Access URL: ${BLUE}http://$(hostname -I | awk '{print $1}')${NC}"
echo -e "           ${BLUE}http://raspberrypi.local${NC}"
echo
echo -e "Monitor status: ${YELLOW}./monitor_unibos.sh${NC}"
echo
echo -e "${YELLOW}Note: First load may be slow on Pi. Consider enabling browser caching.${NC}"
echo
echo -e "${GREEN}Enjoy UNIBOS on Raspberry Pi!${NC}"