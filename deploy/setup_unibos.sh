#!/bin/bash
#
# UNIBOS Cross-Platform Setup Script
# Works on: macOS, Ubuntu/Debian, Raspberry Pi OS
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        echo -e "${BLUE}Detected OS: macOS${NC}"
    elif [[ -f /etc/os-release ]]; then
        . /etc/os-release
        if [[ "$ID" == "raspbian" ]]; then
            OS="raspberrypi"
            echo -e "${BLUE}Detected OS: Raspberry Pi OS${NC}"
        elif [[ "$ID" == "ubuntu" || "$ID" == "debian" ]]; then
            OS="linux"
            echo -e "${BLUE}Detected OS: $NAME${NC}"
        else
            OS="linux"
            echo -e "${YELLOW}Unknown Linux distribution, treating as generic Linux${NC}"
        fi
    else
        echo -e "${RED}Unsupported OS${NC}"
        exit 1
    fi
}

# Check Python version
check_python() {
    echo -e "${BLUE}Checking Python...${NC}"
    
    # Try different Python commands
    if command -v python3.12 &> /dev/null; then
        PYTHON_CMD="python3.12"
    elif command -v python3.11 &> /dev/null; then
        PYTHON_CMD="python3.11"
    elif command -v python3.10 &> /dev/null; then
        PYTHON_CMD="python3.10"
    elif command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    else
        echo -e "${RED}Python 3 not found. Please install Python 3.10 or higher${NC}"
        exit 1
    fi
    
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
    echo -e "${GREEN}Found Python: $PYTHON_VERSION${NC}"
}

# Install system dependencies
install_dependencies() {
    echo -e "${BLUE}Installing system dependencies...${NC}"
    
    case $OS in
        "macos")
            # Check if Homebrew is installed
            if ! command -v brew &> /dev/null; then
                echo -e "${YELLOW}Homebrew not found. Please install from https://brew.sh/${NC}"
                exit 1
            fi
            brew install postgresql redis nginx
            ;;
        "linux"|"raspberrypi")
            sudo apt-get update
            sudo apt-get install -y \
                postgresql postgresql-contrib \
                redis-server \
                nginx \
                python3-pip python3-venv python3-dev \
                build-essential \
                libpq-dev \
                libjpeg-dev zlib1g-dev \
                git curl
            
            # Start services
            sudo systemctl enable postgresql redis-server nginx
            sudo systemctl start postgresql redis-server nginx
            ;;
    esac
}

# Setup PostgreSQL
setup_postgresql() {
    echo -e "${BLUE}Setting up PostgreSQL...${NC}"
    
    case $OS in
        "macos")
            # Start PostgreSQL if not running
            brew services start postgresql
            ;;
        "linux"|"raspberrypi")
            sudo systemctl start postgresql
            ;;
    esac
    
    # Create database and user
    echo -e "${YELLOW}Creating database and user...${NC}"
    
    sudo -u postgres psql <<EOF 2>/dev/null || true
CREATE USER unibos_user WITH PASSWORD 'unibos_password';
CREATE DATABASE unibos_db OWNER unibos_user;
GRANT ALL PRIVILEGES ON DATABASE unibos_db TO unibos_user;
ALTER USER unibos_user CREATEDB;
EOF
    
    echo -e "${GREEN}PostgreSQL setup complete${NC}"
}

# Setup Python virtual environment
setup_venv() {
    echo -e "${BLUE}Setting up Python virtual environment...${NC}"
    
    cd backend
    
    # Create venv if not exists
    if [ ! -d "venv" ]; then
        $PYTHON_CMD -m venv venv
    fi
    
    # Activate venv
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    echo -e "${GREEN}Virtual environment ready${NC}"
}

# Install Python dependencies
install_python_deps() {
    echo -e "${BLUE}Installing Python dependencies...${NC}"
    
    # Create requirements file if not exists
    if [ ! -f "requirements.txt" ]; then
        cat > requirements.txt <<EOF
# Core
Django==5.0.1
djangorestframework==3.14.0
psycopg2-binary==2.9.9

# Redis & Cache
django-redis==5.4.0
redis==5.0.1

# CORS & Security
django-cors-headers==4.3.1
django-environ==0.11.2
django-filter==23.5
djangorestframework-simplejwt==5.3.1

# Authentication
PyJWT==2.8.0
pyotp==2.9.0

# Monitoring
django-prometheus==2.3.1
python-json-logger==2.0.7

# Static files
whitenoise==6.6.0

# User agents
user-agents==2.2.0

# Web server
gunicorn==23.0.0
uvicorn==0.30.6

# WebSockets
channels==4.3.1
channels-redis==4.3.0
daphne==4.2.1

# API Documentation
drf-spectacular==0.28.0

# Additional
aiohttp==3.12.15
Pillow==11.3.0
requests==2.32.5
beautifulsoup4==4.13.5
lxml==6.0.1
python-dotenv==1.1.1
django-extensions==4.1
EOF
    fi
    
    pip install -r requirements.txt
    
    echo -e "${GREEN}Python dependencies installed${NC}"
}

# Setup Django
setup_django() {
    echo -e "${BLUE}Setting up Django...${NC}"
    
    # Create .env file
    cat > .env <<EOF
SECRET_KEY='django-insecure-dev-key-$(openssl rand -hex 32)'
DEBUG=False
DB_NAME=unibos_db
DB_USER=unibos_user
DB_PASSWORD=unibos_password
DB_HOST=localhost
DB_PORT=5432
EOF
    
    # Run migrations
    python manage.py migrate
    
    # Collect static files
    python manage.py collectstatic --noinput
    
    echo -e "${GREEN}Django setup complete${NC}"
}

# Setup systemd service (Linux only)
setup_systemd() {
    if [[ "$OS" == "linux" || "$OS" == "raspberrypi" ]]; then
        echo -e "${BLUE}Setting up systemd service...${NC}"
        
        CURRENT_DIR=$(pwd)
        USER=$(whoami)
        
        sudo tee /etc/systemd/system/gunicorn.service > /dev/null <<EOF
[Unit]
Description=gunicorn daemon for UNIBOS
After=network.target

[Service]
User=$USER
Group=$USER
WorkingDirectory=$CURRENT_DIR
ExecStart=$CURRENT_DIR/venv/bin/gunicorn \\
          --access-logfile $CURRENT_DIR/../logs/gunicorn-access.log \\
          --error-logfile $CURRENT_DIR/../logs/gunicorn-error.log \\
          --workers 3 \\
          --bind 0.0.0.0:8000 \\
          --timeout 120 \\
          --reload \\
          unibos_backend.wsgi:application

EnvironmentFile=$CURRENT_DIR/.env
Environment="DJANGO_SETTINGS_MODULE=unibos_backend.settings.production"

Restart=always

[Install]
WantedBy=multi-user.target
EOF
        
        sudo systemctl daemon-reload
        sudo systemctl enable gunicorn
        sudo systemctl restart gunicorn
        
        echo -e "${GREEN}Systemd service configured${NC}"
    fi
}

# Setup Nginx
setup_nginx() {
    echo -e "${BLUE}Setting up Nginx...${NC}"
    
    case $OS in
        "macos")
            NGINX_CONF="/usr/local/etc/nginx/servers/unibos.conf"
            ;;
        "linux"|"raspberrypi")
            NGINX_CONF="/etc/nginx/sites-available/unibos"
            ;;
    esac
    
    sudo tee $NGINX_CONF > /dev/null <<EOF
server {
    listen 80;
    server_name localhost unibos.local;
    
    client_max_body_size 100M;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    location /static/ {
        alias $(pwd)/../backend/staticfiles/;
    }
    
    location /media/ {
        alias $(pwd)/../backend/media/;
    }
}
EOF
    
    # Enable site on Linux
    if [[ "$OS" == "linux" || "$OS" == "raspberrypi" ]]; then
        sudo ln -sf /etc/nginx/sites-available/unibos /etc/nginx/sites-enabled/
        sudo nginx -t
        sudo systemctl reload nginx
    else
        brew services restart nginx
    fi
    
    echo -e "${GREEN}Nginx configured${NC}"
}

# Create startup script
create_startup_script() {
    echo -e "${BLUE}Creating startup script...${NC}"
    
    cat > start_unibos.sh <<'EOF'
#!/bin/bash

# UNIBOS Startup Script

echo "Starting UNIBOS services..."

# Detect OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    brew services start postgresql redis nginx
    cd backend
    source venv/bin/activate
    gunicorn --bind 0.0.0.0:8000 --workers 3 --reload unibos_backend.wsgi:application &
    echo "UNIBOS is running at http://localhost:8000"
else
    # Linux
    sudo systemctl start postgresql redis-server nginx gunicorn
    echo "UNIBOS is running at http://localhost"
fi
EOF
    
    chmod +x start_unibos.sh
    
    cat > stop_unibos.sh <<'EOF'
#!/bin/bash

# UNIBOS Stop Script

echo "Stopping UNIBOS services..."

if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    pkill -f gunicorn
    brew services stop postgresql redis nginx
else
    # Linux
    sudo systemctl stop gunicorn
fi

echo "UNIBOS services stopped"
EOF
    
    chmod +x stop_unibos.sh
    
    echo -e "${GREEN}Startup scripts created${NC}"
}

# Main installation
main() {
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}     UNIBOS Cross-Platform Setup${NC}"
    echo -e "${GREEN}========================================${NC}"
    
    detect_os
    check_python
    
    # Ask for installation type
    echo -e "${YELLOW}Select installation type:${NC}"
    echo "1) Full installation (with system dependencies)"
    echo "2) Python dependencies only"
    echo "3) Configure services only"
    read -p "Choice [1-3]: " choice
    
    case $choice in
        1)
            install_dependencies
            setup_postgresql
            setup_venv
            install_python_deps
            setup_django
            setup_systemd
            setup_nginx
            create_startup_script
            ;;
        2)
            setup_venv
            install_python_deps
            setup_django
            ;;
        3)
            setup_systemd
            setup_nginx
            create_startup_script
            ;;
    esac
    
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}     Installation Complete!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo
    echo -e "To start UNIBOS: ${YELLOW}./start_unibos.sh${NC}"
    echo -e "To stop UNIBOS: ${YELLOW}./stop_unibos.sh${NC}"
    echo
    echo -e "Access UNIBOS at: ${BLUE}http://localhost${NC}"
}

# Run main
main