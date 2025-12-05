#!/bin/bash
#
# UNIBOS Node Installer
# =====================
# Install, repair, or uninstall UNIBOS Node on Raspberry Pi and Linux systems
#
# Usage:
#   curl -sSL https://recaria.org/install.sh | bash              # Install
#   curl -sSL https://recaria.org/install.sh | bash -s repair    # Repair
#   curl -sSL https://recaria.org/install.sh | bash -s uninstall # Uninstall
#
# Supported Platforms:
#   - Raspberry Pi Zero 2W, Pi 3, Pi 4, Pi 5
#   - Ubuntu/Debian Linux
#
# Architecture: v2.0
#   - Uses unibos (node) repository
#   - Connects to Hub at recaria.org
#   - Local Celery worker for background tasks
#
# Author: UNIBOS Team
# Version: 2.0.2
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
DIM='\033[2m'
NC='\033[0m'

# Configuration
UNIBOS_VERSION="2.0.2"
UNIBOS_REPO_HTTPS="https://github.com/unibosoft/unibos.git"
UNIBOS_REPO_SSH="git@github.com:unibosoft/unibos.git"
HUB_URL="https://recaria.org"
INSTALL_DIR="$HOME/unibos"
VENV_DIR="$INSTALL_DIR/core/clients/web/venv"
SERVICE_PORT=8000
SETTINGS_MODULE="unibos_backend.settings.node"

# Logging
log() { echo -e "  $1"; }
log_ok() { echo -e "  ${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "  ${YELLOW}[!]${NC} $1"; }
log_err() { echo -e "  ${RED}[X]${NC} $1"; }
log_step() { echo -e "\n${CYAN}$1${NC}"; }

# =============================================================================
# BANNER
# =============================================================================

print_banner() {
    clear
    echo ""
    echo -e "${CYAN}"
    echo "  _   _ _   _ ___ ____   ___  ____  "
    echo " | | | | \ | |_ _| __ ) / _ \/ ___| "
    echo " | | | |  \| || ||  _ \| | | \___ \ "
    echo " | |_| | |\  || || |_) | |_| |___) |"
    echo "  \___/|_| \_|___|____/ \___/|____/ "
    echo -e "${NC}"
    echo -e "  ${DIM}node installer v${UNIBOS_VERSION}${NC}"
    echo ""
}

# =============================================================================
# SYSTEM INFO
# =============================================================================

detect_system_info() {
    # Platform detection
    PLATFORM="linux"
    PLATFORM_NAME="linux"
    PLATFORM_DETAIL="generic"

    if [ -f /proc/cpuinfo ]; then
        if grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null || \
           grep -q "BCM" /proc/cpuinfo 2>/dev/null; then
            PLATFORM="raspberry-pi"
            if grep -q "Zero 2" /proc/device-tree/model 2>/dev/null; then
                PLATFORM_NAME="raspberry pi zero 2w"
                PLATFORM_DETAIL="zero2w"
            elif grep -q "Pi 5" /proc/device-tree/model 2>/dev/null; then
                PLATFORM_NAME="raspberry pi 5"
                PLATFORM_DETAIL="pi5"
            elif grep -q "Pi 4" /proc/device-tree/model 2>/dev/null; then
                PLATFORM_NAME="raspberry pi 4"
                PLATFORM_DETAIL="pi4"
            elif grep -q "Pi 3" /proc/device-tree/model 2>/dev/null; then
                PLATFORM_NAME="raspberry pi 3"
                PLATFORM_DETAIL="pi3"
            else
                PLATFORM_NAME="raspberry pi"
                PLATFORM_DETAIL="pi"
            fi
        fi
    fi

    # RAM and CPU
    RAM_MB=0
    [ -f /proc/meminfo ] && RAM_MB=$(grep MemTotal /proc/meminfo | awk '{print int($2/1024)}')
    CPU_CORES=$(nproc 2>/dev/null || echo 1)

    # Detect capabilities
    HAS_GPIO="false"
    HAS_CAMERA="false"
    HAS_GPU="false"

    [ -d /sys/class/gpio ] && HAS_GPIO="true"
    [ -e /dev/video0 ] && HAS_CAMERA="true"
    command -v vcgencmd &>/dev/null && HAS_GPU="true"

    # Worker config based on platform
    case "$PLATFORM_DETAIL" in
        "zero2w"|"pi3")
            WORKER_COUNT=1
            CELERY_CONCURRENCY=1
            ;;
        "pi4")
            WORKER_COUNT=$((RAM_MB >= 4000 ? 2 : 1))
            CELERY_CONCURRENCY=2
            ;;
        "pi5")
            WORKER_COUNT=2
            CELERY_CONCURRENCY=4
            ;;
        *)
            WORKER_COUNT=$((CPU_CORES > 4 ? 4 : CPU_CORES))
            CELERY_CONCURRENCY=$CPU_CORES
            ;;
    esac

    # UNIBOS status
    UNIBOS_INSTALLED="no"
    UNIBOS_RUNNING="no"
    INSTALLED_VERSION=""

    if [ -d "$INSTALL_DIR" ]; then
        UNIBOS_INSTALLED="yes"
        if [ -f "$INSTALL_DIR/VERSION.json" ]; then
            INSTALLED_VERSION=$(grep -o '"semantic"[[:space:]]*:[[:space:]]*"[^"]*"' "$INSTALL_DIR/VERSION.json" 2>/dev/null | head -1 | cut -d'"' -f4)
        fi
        if systemctl is-active --quiet unibos 2>/dev/null; then
            UNIBOS_RUNNING="yes"
        fi
    fi

    export PLATFORM PLATFORM_NAME PLATFORM_DETAIL RAM_MB CPU_CORES
    export HAS_GPIO HAS_CAMERA HAS_GPU
    export WORKER_COUNT CELERY_CONCURRENCY
}

print_system_info() {
    echo -e "  ${DIM}─────────────────────────────────────${NC}"
    echo -e "  ${CYAN}system${NC}"
    echo -e "    platform    : ${PLATFORM_NAME}"
    echo -e "    ram         : ${RAM_MB} mb"
    echo -e "    cpu cores   : ${CPU_CORES}"
    echo -e "    capabilities: gpio=${HAS_GPIO} camera=${HAS_CAMERA} gpu=${HAS_GPU}"
    echo ""
    echo -e "  ${CYAN}unibos${NC}"
    if [ "$UNIBOS_INSTALLED" == "yes" ]; then
        echo -e "    installed   : ${GREEN}yes${NC} (v${INSTALLED_VERSION:-unknown})"
        if [ "$UNIBOS_RUNNING" == "yes" ]; then
            echo -e "    status      : ${GREEN}running${NC}"
        else
            echo -e "    status      : ${YELLOW}stopped${NC}"
        fi
    else
        echo -e "    installed   : ${DIM}no${NC}"
    fi
    echo -e "  ${DIM}─────────────────────────────────────${NC}"
    echo ""
}

# =============================================================================
# MODE SELECTION (Arrow Key Navigation)
# =============================================================================

MENU_OPTIONS=("install" "repair" "uninstall")
MENU_DESCRIPTIONS=("fresh installation" "fix existing installation" "remove unibos")
MENU_COLORS=("$GREEN" "$YELLOW" "$RED")

draw_menu() {
    local selected=$1

    if [ "$2" == "redraw" ]; then
        printf "\033[5A"
        printf "\033[K"
    fi

    echo ""
    for i in "${!MENU_OPTIONS[@]}"; do
        printf "\033[K"
        if [ $i -eq $selected ]; then
            echo -e "   ${MENU_COLORS[$i]}▸ ${MENU_OPTIONS[$i]}${NC}  ${DIM}- ${MENU_DESCRIPTIONS[$i]}${NC}"
        else
            echo -e "     ${DIM}${MENU_OPTIONS[$i]}  - ${MENU_DESCRIPTIONS[$i]}${NC}"
        fi
    done
    echo ""
}

select_menu() {
    local selected=0
    local key

    if [ "$UNIBOS_INSTALLED" == "yes" ]; then
        selected=1
    fi

    echo -e "  ${CYAN}select action${NC}  ${DIM}(↑↓ navigate, enter select, q quit)${NC}"

    draw_menu $selected

    printf "\033[?25l"
    trap 'printf "\033[?25h"' EXIT

    exec 3</dev/tty

    while true; do
        IFS= read -rsn1 key <&3

        if [ -z "$key" ]; then
            printf "\033[?25h"
            exec 3<&-
            echo ""
            SELECTED_MODE="${MENU_OPTIONS[$selected]}"
            return 0
        fi

        case "$key" in
            $'\x1b')
                read -rsn2 -t 0.1 rest <&3
                case "$rest" in
                    '[A')
                        ((selected--)) || true
                        [ $selected -lt 0 ] && selected=$((${#MENU_OPTIONS[@]} - 1))
                        draw_menu $selected "redraw"
                        ;;
                    '[B')
                        ((selected++)) || true
                        [ $selected -ge ${#MENU_OPTIONS[@]} ] && selected=0
                        draw_menu $selected "redraw"
                        ;;
                esac
                ;;
            'q'|'Q')
                printf "\033[?25h"
                exec 3<&-
                echo ""
                log "cancelled."
                exit 0
                ;;
            '1')
                printf "\033[?25h"
                exec 3<&-
                echo ""
                SELECTED_MODE="install"
                return 0
                ;;
            '2')
                printf "\033[?25h"
                exec 3<&-
                echo ""
                SELECTED_MODE="repair"
                return 0
                ;;
            '3')
                printf "\033[?25h"
                exec 3<&-
                echo ""
                SELECTED_MODE="uninstall"
                return 0
                ;;
        esac
    done
}

# =============================================================================
# PRE-FLIGHT CHECKS
# =============================================================================

check_requirements() {
    log_step "Checking requirements..."

    if [ "$EUID" -eq 0 ]; then
        log_err "Do not run as root! Use: curl ... | bash"
        exit 1
    fi

    if ! sudo -n true 2>/dev/null; then
        log "Sudo password required for system packages..."
        sudo -v || { log_err "Sudo required"; exit 1; }
    fi

    log_ok "Requirements OK"
}

# =============================================================================
# INSTALL FUNCTIONS
# =============================================================================

install_dependencies() {
    log_step "Installing dependencies..."

    if command -v apt-get &>/dev/null; then
        sudo apt-get update -qq
        sudo apt-get install -y -qq \
            python3 python3-pip python3-venv python3-dev \
            postgresql postgresql-contrib libpq-dev \
            redis-server git curl wget build-essential \
            avahi-daemon avahi-utils libnss-mdns \
            libffi-dev libssl-dev 2>/dev/null
    else
        log_err "Only apt-based systems supported currently"
        exit 1
    fi

    # Enable services
    sudo systemctl enable postgresql redis-server avahi-daemon 2>/dev/null || true
    sudo systemctl start postgresql redis-server avahi-daemon 2>/dev/null || true

    log_ok "Dependencies installed"
}

install_unibos() {
    log_step "Installing UNIBOS Node..."

    if [ -d "$INSTALL_DIR" ]; then
        log_warn "Existing installation found, updating..."
        cd "$INSTALL_DIR" && git pull origin main 2>/dev/null || true
    else
        log "Cloning repository..."
        # Try SSH first (for deploy key), fallback to HTTPS
        if ssh -o BatchMode=yes -o ConnectTimeout=5 git@github.com 2>&1 | grep -q "successfully authenticated"; then
            git clone --depth 1 "$UNIBOS_REPO_SSH" "$INSTALL_DIR" || {
                log_warn "SSH clone failed, trying HTTPS..."
                git clone --depth 1 "$UNIBOS_REPO_HTTPS" "$INSTALL_DIR" || {
                    log_err "Clone failed. Setup SSH key or use GitHub PAT."
                    exit 1
                }
            }
        else
            git clone --depth 1 "$UNIBOS_REPO_HTTPS" "$INSTALL_DIR" || {
                log_err "Clone failed. Check network or use GitHub PAT."
                exit 1
            }
        fi
    fi

    # Create venv and install
    cd "$INSTALL_DIR"
    python3 -m venv "$VENV_DIR"
    "$VENV_DIR/bin/pip" install --upgrade pip wheel -q

    cd "$INSTALL_DIR/core/clients/web"
    "$VENV_DIR/bin/pip" install -r requirements.txt -q 2>/dev/null || \
    "$VENV_DIR/bin/pip" install django djangorestframework psycopg2-binary \
        redis celery channels daphne uvicorn django-environ django-redis \
        djangorestframework-simplejwt django-cors-headers django-filter \
        drf-spectacular django-extensions django-celery-beat channels-redis \
        django-prometheus psutil -q

    # Install unibos CLI
    cd "$INSTALL_DIR"
    "$VENV_DIR/bin/pip" install -e . -q 2>/dev/null || true

    log_ok "UNIBOS Node installed"
}

setup_database() {
    log_step "Setting up database..."

    DB_NAME="unibos_node"
    DB_USER="unibos_user"
    DB_PASS=$(openssl rand -base64 24 | tr -dc 'a-zA-Z0-9' | head -c 24)

    sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';" 2>/dev/null || true
    sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;" 2>/dev/null || true
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;" 2>/dev/null || true
    sudo -u postgres psql -d $DB_NAME -c "GRANT ALL ON SCHEMA public TO $DB_USER;" 2>/dev/null || true

    # Save credentials
    mkdir -p "$INSTALL_DIR/data/config"
    cat > "$INSTALL_DIR/data/config/db.env" << EOF
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASS=$DB_PASS
EOF
    chmod 600 "$INSTALL_DIR/data/config/db.env"

    log_ok "Database configured"
}

generate_node_uuid() {
    # Generate unique node UUID
    NODE_UUID=$(cat /proc/sys/kernel/random/uuid)

    # Try to use MAC address for deterministic UUID on same hardware
    if [ -f /sys/class/net/eth0/address ]; then
        MAC=$(cat /sys/class/net/eth0/address | tr -d ':')
        NODE_UUID="${MAC:0:8}-${MAC:8:4}-4${MAC:12:3}-8000-$(hostname | md5sum | head -c 12)"
    elif [ -f /sys/class/net/wlan0/address ]; then
        MAC=$(cat /sys/class/net/wlan0/address | tr -d ':')
        NODE_UUID="${MAC:0:8}-${MAC:8:4}-4${MAC:12:3}-8000-$(hostname | md5sum | head -c 12)"
    fi

    echo "$NODE_UUID"
}

setup_environment() {
    log_step "Configuring environment..."

    SECRET_KEY=$(openssl rand -base64 48 | tr -dc 'a-zA-Z0-9' | head -c 64)
    LOCAL_IP=$(hostname -I 2>/dev/null | awk '{print $1}' || echo "127.0.0.1")
    NODE_UUID=$(generate_node_uuid)
    source "$INSTALL_DIR/data/config/db.env"

    cat > "$INSTALL_DIR/.env" << EOF
# UNIBOS Node Configuration
# Generated: $(date -Iseconds)
# Version: $UNIBOS_VERSION

# Django Settings
DJANGO_SETTINGS_MODULE=$SETTINGS_MODULE
UNIBOS_SETTINGS=node
SECRET_KEY=$SECRET_KEY
DEBUG=False
ALLOWED_HOSTS=$LOCAL_IP,localhost,127.0.0.1,$(hostname),$(hostname).local

# Database
DATABASE_URL=postgres://$DB_USER:$DB_PASS@localhost:5432/$DB_NAME
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASS
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0

# Node Identity
NODE_UUID=$NODE_UUID
NODE_TYPE=edge
NODE_PLATFORM=$PLATFORM
NODE_PLATFORM_DETAIL=$PLATFORM_DETAIL
NODE_HOSTNAME=$(hostname)

# Hub Connection
HUB_URL=$HUB_URL
CENTRAL_REGISTRY_URL=$HUB_URL

# Capabilities
NODE_HAS_GPIO=$HAS_GPIO
NODE_HAS_CAMERA=$HAS_CAMERA
NODE_HAS_GPU=$HAS_GPU
NODE_RAM_MB=$RAM_MB
NODE_CPU_CORES=$CPU_CORES

# Performance
WORKER_COUNT=$WORKER_COUNT
CELERY_CONCURRENCY=$CELERY_CONCURRENCY
EOF

    chmod 600 "$INSTALL_DIR/.env"
    ln -sf "$INSTALL_DIR/.env" "$INSTALL_DIR/core/clients/web/.env" 2>/dev/null || true

    # Save node UUID for future reference
    echo "$NODE_UUID" > "$INSTALL_DIR/data/config/node_uuid"
    chmod 644 "$INSTALL_DIR/data/config/node_uuid"

    log_ok "Environment configured (Node UUID: ${NODE_UUID:0:8}...)"
}

setup_services() {
    log_step "Setting up services..."

    # Main service (uvicorn)
    sudo tee /etc/systemd/system/unibos.service > /dev/null << EOF
[Unit]
Description=UNIBOS Node
After=network.target postgresql.service redis.service
Wants=postgresql.service redis.service

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=$INSTALL_DIR/core/clients/web
EnvironmentFile=$INSTALL_DIR/.env
Environment="PYTHONPATH=$INSTALL_DIR:$INSTALL_DIR/core/clients/web"
Environment="UNIBOS_ROOT=$INSTALL_DIR"
ExecStart=$VENV_DIR/bin/uvicorn unibos_backend.asgi:application --host 0.0.0.0 --port $SERVICE_PORT --workers $WORKER_COUNT
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

    # Worker service (celery)
    sudo tee /etc/systemd/system/unibos-worker.service > /dev/null << EOF
[Unit]
Description=UNIBOS Worker
After=network.target redis.service
Requires=redis.service

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=$INSTALL_DIR
EnvironmentFile=$INSTALL_DIR/.env
Environment="PYTHONPATH=$INSTALL_DIR:$INSTALL_DIR/core/clients/web"
Environment="UNIBOS_ROOT=$INSTALL_DIR"
ExecStart=$VENV_DIR/bin/celery -A core.profiles.worker.celery_app worker --loglevel=INFO -Q default,ocr,media -c $CELERY_CONCURRENCY
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    # Beat scheduler (only on capable nodes)
    if [ "$RAM_MB" -ge 2000 ]; then
        sudo tee /etc/systemd/system/unibos-beat.service > /dev/null << EOF
[Unit]
Description=UNIBOS Beat Scheduler
After=network.target redis.service
Requires=redis.service

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=$INSTALL_DIR
EnvironmentFile=$INSTALL_DIR/.env
Environment="PYTHONPATH=$INSTALL_DIR:$INSTALL_DIR/core/clients/web"
Environment="UNIBOS_ROOT=$INSTALL_DIR"
ExecStart=$VENV_DIR/bin/celery -A core.profiles.worker.celery_app beat --loglevel=INFO --pidfile=$INSTALL_DIR/data/run/celerybeat.pid --schedule=$INSTALL_DIR/data/run/celerybeat-schedule
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    fi

    # mDNS service for node discovery
    sudo tee /etc/avahi/services/unibos.service > /dev/null << EOF
<?xml version="1.0" standalone='no'?>
<!DOCTYPE service-group SYSTEM "avahi-service.dtd">
<service-group>
  <name replace-wildcards="yes">UNIBOS Node on %h</name>
  <service>
    <type>_unibos._tcp</type>
    <port>$SERVICE_PORT</port>
    <txt-record>version=$UNIBOS_VERSION</txt-record>
    <txt-record>platform=$PLATFORM_DETAIL</txt-record>
    <txt-record>type=node</txt-record>
  </service>
</service-group>
EOF

    # Create run directory
    mkdir -p "$INSTALL_DIR/data/run"
    mkdir -p "$INSTALL_DIR/data/logs"

    sudo systemctl daemon-reload
    log_ok "Services configured"
}

run_migrations() {
    log_step "Running migrations..."

    cd "$INSTALL_DIR/core/clients/web"
    export PYTHONPATH="$INSTALL_DIR:$INSTALL_DIR/core/clients/web"
    set -a && source "$INSTALL_DIR/.env" && set +a

    "$VENV_DIR/bin/python" manage.py migrate --noinput 2>/dev/null || log_warn "Some migrations skipped"
    "$VENV_DIR/bin/python" manage.py collectstatic --noinput 2>/dev/null || log_warn "Static files skipped"

    log_ok "Migrations complete"
}

register_with_hub() {
    log_step "Registering with Hub..."

    source "$INSTALL_DIR/.env"
    LOCAL_IP=$(hostname -I 2>/dev/null | awk '{print $1}' || echo "127.0.0.1")

    # Prepare registration data
    REG_DATA=$(cat << EOF
{
    "id": "$NODE_UUID",
    "hostname": "$(hostname)",
    "node_type": "edge",
    "platform": "$PLATFORM_DETAIL",
    "ip_address": "$LOCAL_IP",
    "port": $SERVICE_PORT,
    "version": "$UNIBOS_VERSION",
    "capabilities": {
        "has_gpio": $HAS_GPIO,
        "has_camera": $HAS_CAMERA,
        "has_gpu": $HAS_GPU,
        "ram_gb": $((RAM_MB / 1024)),
        "cpu_cores": $CPU_CORES,
        "can_run_celery": true
    }
}
EOF
)

    # Try to register
    RESPONSE=$(curl -s -X POST "$HUB_URL/api/v1/nodes/register/" \
        -H "Content-Type: application/json" \
        -d "$REG_DATA" 2>/dev/null || echo '{"error": "connection failed"}')

    if echo "$RESPONSE" | grep -q '"id"'; then
        log_ok "Registered with Hub"
    else
        log_warn "Hub registration deferred (Hub may be offline)"
    fi
}

start_services() {
    log_step "Starting services..."

    sudo systemctl enable unibos unibos-worker 2>/dev/null || true
    [ "$RAM_MB" -ge 2000 ] && sudo systemctl enable unibos-beat 2>/dev/null || true

    sudo systemctl restart avahi-daemon 2>/dev/null || true
    sudo systemctl start unibos unibos-worker 2>/dev/null || true
    [ "$RAM_MB" -ge 2000 ] && sudo systemctl start unibos-beat 2>/dev/null || true

    sleep 3

    if systemctl is-active --quiet unibos; then
        log_ok "UNIBOS Node is running"
    else
        log_warn "Service may still be starting..."
    fi
}

# =============================================================================
# REPAIR FUNCTIONS
# =============================================================================

repair_installation() {
    log_step "Repairing UNIBOS Node installation..."

    if [ ! -d "$INSTALL_DIR" ]; then
        log_err "No installation found at $INSTALL_DIR"
        log "Run install instead."
        exit 1
    fi

    # Stop services
    sudo systemctl stop unibos unibos-worker unibos-beat 2>/dev/null || true

    # Update code
    log "Updating code..."
    cd "$INSTALL_DIR" && git pull origin main 2>/dev/null || log_warn "Git pull failed"

    # Reinstall dependencies
    log "Reinstalling Python packages..."
    cd "$INSTALL_DIR/core/clients/web"
    "$VENV_DIR/bin/pip" install -r requirements.txt -q 2>/dev/null || true

    # Run migrations
    log "Running migrations..."
    export PYTHONPATH="$INSTALL_DIR:$INSTALL_DIR/core/clients/web"
    set -a && source "$INSTALL_DIR/.env" && set +a
    "$VENV_DIR/bin/python" manage.py migrate --noinput 2>/dev/null || true
    "$VENV_DIR/bin/python" manage.py collectstatic --noinput 2>/dev/null || true

    # Restart services
    sudo systemctl daemon-reload
    sudo systemctl start unibos unibos-worker 2>/dev/null || true
    [ -f /etc/systemd/system/unibos-beat.service ] && sudo systemctl start unibos-beat 2>/dev/null || true

    sleep 2

    if systemctl is-active --quiet unibos; then
        log_ok "Repair complete - UNIBOS Node is running"
    else
        log_warn "Repair complete - check logs: journalctl -u unibos -f"
    fi
}

# =============================================================================
# UNINSTALL FUNCTIONS
# =============================================================================

uninstall_unibos() {
    log_step "uninstalling unibos node..."

    echo ""
    echo -e "  ${RED}warning: this will remove:${NC}"
    echo "    - unibos installation at $INSTALL_DIR"
    echo "    - systemd services (unibos, unibos-worker, unibos-beat)"
    echo "    - mdns service configuration"
    echo ""
    echo -e "  ${YELLOW}database and system packages will not be removed.${NC}"
    echo ""

    echo -n "  are you sure? [y/N] "
    read -n 1 -r REPLY </dev/tty
    echo ""

    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log "cancelled."
        exit 0
    fi

    # Stop and disable services
    log "Stopping services..."
    sudo systemctl stop unibos unibos-worker unibos-beat 2>/dev/null || true
    sudo systemctl disable unibos unibos-worker unibos-beat 2>/dev/null || true

    # Remove service files
    log "Removing service files..."
    sudo rm -f /etc/systemd/system/unibos.service
    sudo rm -f /etc/systemd/system/unibos-worker.service
    sudo rm -f /etc/systemd/system/unibos-beat.service
    sudo rm -f /etc/avahi/services/unibos.service
    sudo systemctl daemon-reload

    # Remove installation
    log "Removing installation..."
    rm -rf "$INSTALL_DIR"

    log_ok "UNIBOS Node uninstalled"
    echo ""
    log "To remove database: sudo -u postgres dropdb unibos_node"
    log "To remove db user:  sudo -u postgres dropuser unibos_user"
}

# =============================================================================
# SUMMARY
# =============================================================================

print_summary() {
    LOCAL_IP=$(hostname -I 2>/dev/null | awk '{print $1}' || echo "127.0.0.1")
    NODE_NAME=$(hostname)
    source "$INSTALL_DIR/.env" 2>/dev/null || true

    echo ""
    echo -e "${GREEN}============================================${NC}"
    echo -e "${GREEN}     UNIBOS Node Installation Complete!    ${NC}"
    echo -e "${GREEN}============================================${NC}"
    echo ""
    echo -e "  ${CYAN}Node Info:${NC}"
    echo -e "    UUID:     ${NODE_UUID:-unknown}"
    echo -e "    Platform: $PLATFORM_NAME"
    echo -e "    Hub:      $HUB_URL"
    echo ""
    echo -e "  ${CYAN}Access:${NC}"
    echo -e "    http://$LOCAL_IP:$SERVICE_PORT"
    echo -e "    http://${NODE_NAME}.local:$SERVICE_PORT"
    echo ""
    echo -e "  ${CYAN}Commands:${NC}"
    echo -e "    Status:   sudo systemctl status unibos"
    echo -e "    Logs:     journalctl -u unibos -f"
    echo -e "    Restart:  sudo systemctl restart unibos"
    echo ""

    # Quick health check
    echo -n "  Health: "
    if curl -s "http://localhost:$SERVICE_PORT/health/" 2>/dev/null | grep -q "ok"; then
        echo -e "${GREEN}OK${NC}"
    else
        echo -e "${YELLOW}Starting...${NC}"
    fi
    echo ""
}

# =============================================================================
# MAIN
# =============================================================================

main() {
    print_banner

    detect_system_info
    print_system_info

    MODE="${1:-}"

    if [ -z "$MODE" ]; then
        select_menu
        MODE="$SELECTED_MODE"
    fi

    case "$MODE" in
        install)
            check_requirements
            install_dependencies
            install_unibos
            setup_database
            setup_environment
            setup_services
            run_migrations
            start_services
            register_with_hub
            print_summary
            ;;
        repair)
            check_requirements
            repair_installation
            ;;
        uninstall)
            uninstall_unibos
            ;;
        *)
            log_err "Unknown mode: $MODE"
            log "Usage: $0 [install|repair|uninstall]"
            exit 1
            ;;
    esac
}

main "$@"
