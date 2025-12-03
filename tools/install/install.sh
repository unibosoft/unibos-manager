#!/bin/bash
#
# UNIBOS Edge Node Installer
# ==========================
# Single-line installation for Raspberry Pi and Linux systems
#
# Usage:
#   curl -sSL https://unibos.recaria.org/install.sh | bash
#   wget -qO- https://unibos.recaria.org/install.sh | bash
#
# Supported Platforms:
#   - Raspberry Pi Zero 2W
#   - Raspberry Pi 4 (2GB, 4GB, 8GB)
#   - Raspberry Pi 5
#   - Ubuntu/Debian Linux
#
# Author: UNIBOS Team
# Version: 1.0.0
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
UNIBOS_VERSION="1.1.0"
UNIBOS_REPO="https://github.com/berkhatirli/unibos.git"
UNIBOS_RELEASE_URL="https://unibos.recaria.org/releases/latest.tar.gz"
CENTRAL_REGISTRY_URL="https://unibos.recaria.org"
INSTALL_DIR="$HOME/unibos"
VENV_DIR="$INSTALL_DIR/core/clients/web/venv"
SERVICE_PORT=8000

# Logging
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step() { echo -e "${CYAN}==>${NC} $1"; }

# Banner
print_banner() {
    echo ""
    echo -e "${CYAN}"
    echo "  _   _ _   _ ___ ____   ___  ____  "
    echo " | | | | \ | |_ _| __ ) / _ \/ ___| "
    echo " | | | |  \| || ||  _ \| | | \___ \ "
    echo " | |_| | |\  || || |_) | |_| |___) |"
    echo "  \___/|_| \_|___|____/ \___/|____/ "
    echo ""
    echo -e "${NC}  Edge Node Installer v${UNIBOS_VERSION}"
    echo "  =================================="
    echo ""
}

# =============================================================================
# PLATFORM DETECTION
# =============================================================================

detect_platform() {
    log_step "Detecting platform..."

    PLATFORM="linux"
    PLATFORM_DETAIL="generic"
    RAM_MB=0
    CPU_CORES=0

    # Check if Raspberry Pi
    if [ -f /proc/cpuinfo ]; then
        if grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null || \
           grep -q "BCM" /proc/cpuinfo 2>/dev/null; then
            PLATFORM="raspberry-pi"

            # Detect specific model
            if grep -q "Zero 2" /proc/device-tree/model 2>/dev/null; then
                PLATFORM_DETAIL="zero2w"
            elif grep -q "Pi 5" /proc/device-tree/model 2>/dev/null; then
                PLATFORM_DETAIL="pi5"
            elif grep -q "Pi 4" /proc/device-tree/model 2>/dev/null; then
                PLATFORM_DETAIL="pi4"
            elif grep -q "Pi 3" /proc/device-tree/model 2>/dev/null; then
                PLATFORM_DETAIL="pi3"
            else
                PLATFORM_DETAIL="pi-unknown"
            fi
        fi
    fi

    # Get RAM
    if [ -f /proc/meminfo ]; then
        RAM_MB=$(grep MemTotal /proc/meminfo | awk '{print int($2/1024)}')
    fi

    # Get CPU cores
    CPU_CORES=$(nproc 2>/dev/null || echo 1)

    # Determine recommended configuration
    if [ "$PLATFORM" = "raspberry-pi" ]; then
        case "$PLATFORM_DETAIL" in
            "zero2w")
                WORKER_COUNT=1
                WORKER_TYPE="sync"
                RECOMMENDED_MODULES="wimm"
                log_warn "Pi Zero 2W detected - limited resources, single module recommended"
                ;;
            "pi3")
                WORKER_COUNT=2
                WORKER_TYPE="sync"
                RECOMMENDED_MODULES="wimm,documents"
                log_warn "Pi 3 detected - limited resources"
                ;;
            "pi4")
                if [ $RAM_MB -ge 4000 ]; then
                    WORKER_COUNT=3
                    WORKER_TYPE="uvicorn.workers.UvicornWorker"
                    RECOMMENDED_MODULES="all"
                else
                    WORKER_COUNT=2
                    WORKER_TYPE="uvicorn.workers.UvicornWorker"
                    RECOMMENDED_MODULES="wimm,documents,currencies"
                fi
                ;;
            "pi5")
                WORKER_COUNT=4
                WORKER_TYPE="uvicorn.workers.UvicornWorker"
                RECOMMENDED_MODULES="all"
                log_success "Pi 5 detected - full performance mode"
                ;;
            *)
                WORKER_COUNT=2
                WORKER_TYPE="sync"
                RECOMMENDED_MODULES="wimm,documents"
                ;;
        esac
    else
        # Generic Linux
        if [ $RAM_MB -ge 4000 ]; then
            WORKER_COUNT=$((CPU_CORES > 4 ? 4 : CPU_CORES))
            WORKER_TYPE="uvicorn.workers.UvicornWorker"
            RECOMMENDED_MODULES="all"
        else
            WORKER_COUNT=2
            WORKER_TYPE="sync"
            RECOMMENDED_MODULES="wimm,documents"
        fi
    fi

    log_success "Platform: $PLATFORM ($PLATFORM_DETAIL)"
    log_info "RAM: ${RAM_MB}MB | CPU Cores: $CPU_CORES"
    log_info "Workers: $WORKER_COUNT | Type: $WORKER_TYPE"
    log_info "Recommended modules: $RECOMMENDED_MODULES"

    export PLATFORM PLATFORM_DETAIL RAM_MB CPU_CORES WORKER_COUNT WORKER_TYPE RECOMMENDED_MODULES
}

# =============================================================================
# DEPENDENCY INSTALLATION
# =============================================================================

check_root() {
    if [ "$EUID" -eq 0 ]; then
        log_error "Do not run this script as root!"
        log_info "Run as normal user: curl -sSL .../install.sh | bash"
        exit 1
    fi
}

check_sudo() {
    if ! sudo -n true 2>/dev/null; then
        log_info "This script requires sudo privileges for some operations."
        log_info "You may be prompted for your password."
        sudo -v
    fi
}

install_system_dependencies() {
    log_step "Installing system dependencies..."

    # Detect package manager
    if command -v apt-get &> /dev/null; then
        PKG_MANAGER="apt"
    elif command -v dnf &> /dev/null; then
        PKG_MANAGER="dnf"
    elif command -v yum &> /dev/null; then
        PKG_MANAGER="yum"
    else
        log_error "Unsupported package manager"
        exit 1
    fi

    case $PKG_MANAGER in
        apt)
            sudo apt-get update -qq

            # Core dependencies
            sudo apt-get install -y -qq \
                python3 python3-pip python3-venv python3-dev \
                postgresql postgresql-contrib libpq-dev \
                redis-server \
                git curl wget \
                build-essential \
                avahi-daemon avahi-utils libnss-mdns \
                libffi-dev libssl-dev

            # Pi-specific optimizations
            if [ "$PLATFORM" = "raspberry-pi" ]; then
                # Reduce swappiness for SD card longevity
                sudo sysctl -w vm.swappiness=10 2>/dev/null || true
                echo "vm.swappiness=10" | sudo tee -a /etc/sysctl.conf > /dev/null 2>/dev/null || true
            fi
            ;;
        dnf|yum)
            sudo $PKG_MANAGER install -y -q \
                python3 python3-pip python3-devel \
                postgresql postgresql-server postgresql-contrib \
                redis \
                git curl wget \
                gcc make \
                avahi avahi-tools nss-mdns \
                libffi-devel openssl-devel
            ;;
    esac

    # Ensure services are running
    sudo systemctl enable postgresql redis-server avahi-daemon 2>/dev/null || \
    sudo systemctl enable postgresql redis avahi-daemon 2>/dev/null || true

    sudo systemctl start postgresql 2>/dev/null || true
    sudo systemctl start redis-server 2>/dev/null || sudo systemctl start redis 2>/dev/null || true
    sudo systemctl start avahi-daemon 2>/dev/null || true

    log_success "System dependencies installed"
}

# =============================================================================
# UNIBOS INSTALLATION
# =============================================================================

install_unibos() {
    log_step "Installing UNIBOS..."

    # Remove existing installation if present
    if [ -d "$INSTALL_DIR" ]; then
        log_warn "Existing installation found at $INSTALL_DIR"
        read -p "Remove and reinstall? [y/N] " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$INSTALL_DIR"
        else
            log_info "Keeping existing installation, updating..."
            cd "$INSTALL_DIR"
            git pull origin main 2>/dev/null || true
            return 0
        fi
    fi

    # Clone repository
    if command -v git &> /dev/null; then
        log_info "Cloning from git repository..."
        git clone --depth 1 "$UNIBOS_REPO" "$INSTALL_DIR" 2>/dev/null || {
            log_warn "Git clone failed, trying release archive..."
            mkdir -p "$INSTALL_DIR"
            curl -sSL "$UNIBOS_RELEASE_URL" | tar xz -C "$INSTALL_DIR" --strip-components=1
        }
    else
        log_info "Downloading release archive..."
        mkdir -p "$INSTALL_DIR"
        curl -sSL "$UNIBOS_RELEASE_URL" | tar xz -C "$INSTALL_DIR" --strip-components=1
    fi

    cd "$INSTALL_DIR"

    # Create Python virtual environment
    log_info "Creating Python virtual environment..."
    python3 -m venv "$VENV_DIR"

    # Upgrade pip
    "$VENV_DIR/bin/pip" install --upgrade pip wheel setuptools -q

    # Install UNIBOS
    log_info "Installing UNIBOS packages..."
    cd "$INSTALL_DIR/core/clients/web"
    "$VENV_DIR/bin/pip" install -r requirements.txt -q 2>/dev/null || \
    "$VENV_DIR/bin/pip" install django djangorestframework psycopg2-binary redis celery channels gunicorn uvicorn -q

    # Install CLI
    cd "$INSTALL_DIR"
    "$VENV_DIR/bin/pip" install -e . -q 2>/dev/null || true

    # Also install via pipx for system-wide CLI access
    if command -v pipx &> /dev/null; then
        pipx install -e "$INSTALL_DIR" --force 2>/dev/null || true
    else
        python3 -m pip install --user pipx 2>/dev/null || true
        ~/.local/bin/pipx install -e "$INSTALL_DIR" --force 2>/dev/null || true
    fi

    log_success "UNIBOS installed"
}

# =============================================================================
# DATABASE SETUP
# =============================================================================

setup_database() {
    log_step "Setting up PostgreSQL database..."

    DB_NAME="unibos_db"
    DB_USER="unibos_user"
    DB_PASS=$(openssl rand -base64 32 | tr -dc 'a-zA-Z0-9' | head -c 24)

    # Create PostgreSQL user and database
    sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';" 2>/dev/null || \
        log_warn "User $DB_USER may already exist"

    sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;" 2>/dev/null || \
        log_warn "Database $DB_NAME may already exist"

    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;" 2>/dev/null || true

    # Save credentials
    mkdir -p "$INSTALL_DIR/data/config"
    cat > "$INSTALL_DIR/data/config/db.env" << EOF
DATABASE_URL=postgres://$DB_USER:$DB_PASS@localhost:5432/$DB_NAME
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASS=$DB_PASS
DB_HOST=localhost
DB_PORT=5432
EOF
    chmod 600 "$INSTALL_DIR/data/config/db.env"

    log_success "Database configured"
}

# =============================================================================
# ENVIRONMENT CONFIGURATION
# =============================================================================

setup_environment() {
    log_step "Setting up environment..."

    # Generate secret key
    SECRET_KEY=$(openssl rand -base64 48 | tr -dc 'a-zA-Z0-9' | head -c 64)

    # Get IP address
    LOCAL_IP=$(hostname -I 2>/dev/null | awk '{print $1}' || echo "127.0.0.1")

    # Source database credentials
    source "$INSTALL_DIR/data/config/db.env"

    # Create .env file
    cat > "$INSTALL_DIR/.env" << EOF
# UNIBOS Edge Node Configuration
# Generated: $(date -Iseconds)

# Django Settings
DJANGO_SETTINGS_MODULE=unibos_backend.settings.edge
SECRET_KEY=$SECRET_KEY
DEBUG=False
ALLOWED_HOSTS=$LOCAL_IP,localhost,127.0.0.1,$(hostname),$(hostname).local

# Database
DATABASE_URL=$DATABASE_URL

# Redis
REDIS_URL=redis://localhost:6379/0

# Node Identity
NODE_TYPE=edge
NODE_PLATFORM=$PLATFORM
NODE_PLATFORM_DETAIL=$PLATFORM_DETAIL

# Central Registry
CENTRAL_REGISTRY_URL=$CENTRAL_REGISTRY_URL

# Performance
WORKER_COUNT=$WORKER_COUNT
WORKER_TYPE=$WORKER_TYPE

# Modules
ENABLED_MODULES=$RECOMMENDED_MODULES
EOF

    chmod 600 "$INSTALL_DIR/.env"

    log_success "Environment configured"
}

# =============================================================================
# mDNS SETUP (AVAHI)
# =============================================================================

setup_mdns() {
    log_step "Setting up mDNS advertisement..."

    # Get node info
    LOCAL_IP=$(hostname -I 2>/dev/null | awk '{print $1}' || echo "127.0.0.1")
    NODE_NAME=$(hostname)

    # Create Avahi service file
    sudo tee /etc/avahi/services/unibos.service > /dev/null << EOF
<?xml version="1.0" standalone='no'?>
<!DOCTYPE service-group SYSTEM "avahi-service.dtd">
<service-group>
  <name replace-wildcards="yes">UNIBOS on %h</name>
  <service>
    <type>_unibos._tcp</type>
    <port>$SERVICE_PORT</port>
    <txt-record>version=$UNIBOS_VERSION</txt-record>
    <txt-record>platform=$PLATFORM</txt-record>
    <txt-record>platform_detail=$PLATFORM_DETAIL</txt-record>
    <txt-record>node_type=edge</txt-record>
    <txt-record>api=/api/v1/</txt-record>
    <txt-record>health=/health/</txt-record>
  </service>
  <service>
    <type>_http._tcp</type>
    <port>$SERVICE_PORT</port>
    <txt-record>path=/</txt-record>
  </service>
</service-group>
EOF

    # Restart Avahi
    sudo systemctl restart avahi-daemon 2>/dev/null || true

    log_success "mDNS configured: ${NODE_NAME}.local:$SERVICE_PORT"
    log_info "Service type: _unibos._tcp"
}

# =============================================================================
# SYSTEMD SERVICE
# =============================================================================

setup_systemd_service() {
    log_step "Setting up systemd service..."

    # Determine worker command based on platform
    if [ "$WORKER_TYPE" = "uvicorn.workers.UvicornWorker" ]; then
        EXEC_CMD="$VENV_DIR/bin/gunicorn unibos_backend.asgi:application -k uvicorn.workers.UvicornWorker -w $WORKER_COUNT -b 0.0.0.0:$SERVICE_PORT"
    else
        EXEC_CMD="$VENV_DIR/bin/gunicorn unibos_backend.wsgi:application -w $WORKER_COUNT -b 0.0.0.0:$SERVICE_PORT"
    fi

    # Create systemd service
    sudo tee /etc/systemd/system/unibos.service > /dev/null << EOF
[Unit]
Description=UNIBOS Edge Node
Documentation=https://unibos.recaria.org/docs
After=network.target postgresql.service redis.service avahi-daemon.service
Wants=postgresql.service redis.service

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=$INSTALL_DIR/core/clients/web
EnvironmentFile=$INSTALL_DIR/.env
Environment="PYTHONPATH=$INSTALL_DIR:$INSTALL_DIR/core/clients/web"

ExecStart=$EXEC_CMD
ExecReload=/bin/kill -s HUP \$MAINPID
ExecStop=/bin/kill -s TERM \$MAINPID

Restart=always
RestartSec=5
StartLimitInterval=60
StartLimitBurst=3

# Security
NoNewPrivileges=true
PrivateTmp=true

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=unibos

[Install]
WantedBy=multi-user.target
EOF

    # Create Celery worker service
    sudo tee /etc/systemd/system/unibos-celery.service > /dev/null << EOF
[Unit]
Description=UNIBOS Celery Worker
After=network.target redis.service unibos.service

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=$INSTALL_DIR/core/clients/web
EnvironmentFile=$INSTALL_DIR/.env
Environment="PYTHONPATH=$INSTALL_DIR:$INSTALL_DIR/core/clients/web"

ExecStart=$VENV_DIR/bin/celery -A unibos_backend worker --loglevel=info --concurrency=2
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

    # Reload systemd
    sudo systemctl daemon-reload

    log_success "Systemd services configured"
}

# =============================================================================
# DATABASE MIGRATIONS
# =============================================================================

run_migrations() {
    log_step "Running database migrations..."

    cd "$INSTALL_DIR/core/clients/web"

    # Set environment
    export PYTHONPATH="$INSTALL_DIR:$INSTALL_DIR/core/clients/web"
    source "$INSTALL_DIR/.env"

    # Run migrations
    "$VENV_DIR/bin/python" manage.py migrate --noinput 2>/dev/null || {
        log_warn "Some migrations may have failed, continuing..."
    }

    log_success "Migrations completed"
}

# =============================================================================
# NODE REGISTRATION
# =============================================================================

register_node() {
    log_step "Registering with central server..."

    LOCAL_IP=$(hostname -I 2>/dev/null | awk '{print $1}' || echo "127.0.0.1")
    NODE_NAME=$(hostname)

    # Try to register with central
    REGISTRATION_RESPONSE=$(curl -s -X POST "$CENTRAL_REGISTRY_URL/api/v1/nodes/register/" \
        -H "Content-Type: application/json" \
        -d "{
            \"hostname\": \"$NODE_NAME\",
            \"node_type\": \"edge\",
            \"platform\": \"$PLATFORM_DETAIL\",
            \"ip_address\": \"$LOCAL_IP\",
            \"port\": $SERVICE_PORT,
            \"version\": \"$UNIBOS_VERSION\",
            \"capabilities\": {
                \"has_gpio\": $([ \"$PLATFORM\" = \"raspberry-pi\" ] && echo \"true\" || echo \"false\"),
                \"can_run_django\": true,
                \"can_run_celery\": true,
                \"can_run_websocket\": $([ \"$WORKER_TYPE\" = \"uvicorn.workers.UvicornWorker\" ] && echo \"true\" || echo \"false\"),
                \"ram_gb\": $((RAM_MB / 1024)),
                \"cpu_cores\": $CPU_CORES
            }
        }" 2>/dev/null) || true

    if echo "$REGISTRATION_RESPONSE" | grep -q "id"; then
        NODE_ID=$(echo "$REGISTRATION_RESPONSE" | grep -o '"id":"[^"]*"' | cut -d'"' -f4)
        echo "NODE_ID=$NODE_ID" >> "$INSTALL_DIR/.env"
        log_success "Registered with central server (ID: $NODE_ID)"
    else
        log_warn "Could not register with central server (offline mode)"
        log_info "Node will operate independently"
    fi
}

# =============================================================================
# START SERVICES
# =============================================================================

start_services() {
    log_step "Starting UNIBOS services..."

    sudo systemctl enable unibos unibos-celery 2>/dev/null || true
    sudo systemctl start unibos 2>/dev/null || true
    sudo systemctl start unibos-celery 2>/dev/null || true

    # Wait for service to start
    sleep 3

    # Check status
    if systemctl is-active --quiet unibos; then
        log_success "UNIBOS service is running"
    else
        log_warn "UNIBOS service may not have started properly"
        log_info "Check logs: journalctl -u unibos -f"
    fi
}

# =============================================================================
# FINAL SUMMARY
# =============================================================================

print_summary() {
    LOCAL_IP=$(hostname -I 2>/dev/null | awk '{print $1}' || echo "127.0.0.1")
    NODE_NAME=$(hostname)

    echo ""
    echo -e "${GREEN}============================================${NC}"
    echo -e "${GREEN}   UNIBOS Edge Node Installation Complete   ${NC}"
    echo -e "${GREEN}============================================${NC}"
    echo ""
    echo -e "  ${CYAN}Platform:${NC}     $PLATFORM ($PLATFORM_DETAIL)"
    echo -e "  ${CYAN}RAM:${NC}          ${RAM_MB}MB"
    echo -e "  ${CYAN}CPU Cores:${NC}    $CPU_CORES"
    echo -e "  ${CYAN}Workers:${NC}      $WORKER_COUNT"
    echo ""
    echo -e "  ${CYAN}Access URLs:${NC}"
    echo -e "    Local:    ${GREEN}http://$LOCAL_IP:$SERVICE_PORT${NC}"
    echo -e "    mDNS:     ${GREEN}http://${NODE_NAME}.local:$SERVICE_PORT${NC}"
    echo ""
    echo -e "  ${CYAN}Services:${NC}"
    echo -e "    Status:   sudo systemctl status unibos"
    echo -e "    Logs:     journalctl -u unibos -f"
    echo -e "    Restart:  sudo systemctl restart unibos"
    echo ""
    echo -e "  ${CYAN}CLI:${NC}"
    echo -e "    TUI:      unibos-server tui"
    echo -e "    Status:   unibos-server status"
    echo ""
    echo -e "  ${CYAN}mDNS Discovery:${NC}"
    echo -e "    Service:  _unibos._tcp.local"
    echo -e "    Test:     avahi-browse -r _unibos._tcp"
    echo ""

    # Health check
    echo -n "  Health Check: "
    if curl -s "http://localhost:$SERVICE_PORT/health/quick/" | grep -q "ok"; then
        echo -e "${GREEN}OK${NC}"
    else
        echo -e "${YELLOW}Pending (service may still be starting)${NC}"
    fi

    echo ""
    echo -e "${BLUE}Happy hacking!${NC}"
    echo ""
}

# =============================================================================
# MAIN
# =============================================================================

main() {
    print_banner

    # Pre-flight checks
    check_root
    check_sudo

    # Installation steps
    detect_platform
    install_system_dependencies
    install_unibos
    setup_database
    setup_environment
    setup_mdns
    setup_systemd_service
    run_migrations
    register_node
    start_services

    # Done
    print_summary
}

# Run main function
main "$@"
