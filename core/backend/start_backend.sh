#!/bin/bash

# UNIBOS Backend Startup Script
# DevOps Security Enhanced Version with PostgreSQL Auto-Recovery

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="${SCRIPT_DIR}/venv"
PYTHON_BIN="${VENV_PATH}/bin/python"
PID_FILE="${SCRIPT_DIR}/.backend.pid"
LOG_FILE="${SCRIPT_DIR}/server.log"
PORT=8000

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# PostgreSQL configuration
PG_USER="unibos_user"
PG_PASS="unibos_password"
PG_DB="unibos_db"
PG_HOST="localhost"
PG_PORT="5432"

# Function to check PostgreSQL status
check_postgresql() {
    # Try to connect to PostgreSQL
    PGPASSWORD="$PG_PASS" psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DB" -c "SELECT 1;" > /dev/null 2>&1
    return $?
}

# Function to fix PostgreSQL issues
fix_postgresql() {
    echo -e "${YELLOW}🔧 Checking PostgreSQL status...${NC}"
    
    # Check if PostgreSQL is installed
    if ! command -v psql > /dev/null 2>&1; then
        echo -e "${RED}✗ PostgreSQL is not installed${NC}"
        return 1
    fi
    
    # Check PostgreSQL service with brew
    if command -v brew > /dev/null 2>&1; then
        # Get PostgreSQL version
        PG_VERSION=$(brew list --versions | grep "^postgresql@" | head -1 | cut -d' ' -f1)
        if [ -z "$PG_VERSION" ]; then
            PG_VERSION="postgresql"
        fi
        
        # Check service status
        PG_STATUS=$(brew services list | grep "$PG_VERSION" | awk '{print $2}')
        
        if [ "$PG_STATUS" = "error" ] || [ "$PG_STATUS" = "stopped" ] || [ "$PG_STATUS" = "none" ]; then
            echo -e "${YELLOW}⚠ PostgreSQL service is not running properly${NC}"
            
            # Check for stale PID file
            PG_DATA_DIR="/opt/homebrew/var/${PG_VERSION}"
            if [ ! -d "$PG_DATA_DIR" ]; then
                PG_DATA_DIR="/usr/local/var/${PG_VERSION}"
            fi
            
            if [ -f "$PG_DATA_DIR/postmaster.pid" ]; then
                echo -e "${YELLOW}🔍 Found stale PID file, checking process...${NC}"
                OLD_PID=$(head -1 "$PG_DATA_DIR/postmaster.pid")
                if ! ps -p "$OLD_PID" > /dev/null 2>&1; then
                    echo -e "${YELLOW}🧹 Removing stale PID file...${NC}"
                    rm -f "$PG_DATA_DIR/postmaster.pid"
                fi
            fi
            
            # Stop and start PostgreSQL service
            echo -e "${YELLOW}🔄 Restarting PostgreSQL service...${NC}"
            brew services stop "$PG_VERSION" 2>/dev/null
            sleep 2
            brew services start "$PG_VERSION"
            sleep 3
            
            # Check if it started successfully
            if check_postgresql; then
                echo -e "${GREEN}✓ PostgreSQL is now running${NC}"
                return 0
            else
                echo -e "${RED}✗ Failed to start PostgreSQL${NC}"
                echo -e "${YELLOW}Try running: brew services restart $PG_VERSION${NC}"
                return 1
            fi
        elif [ "$PG_STATUS" = "started" ]; then
            # Service is running but maybe not accepting connections
            if check_postgresql; then
                echo -e "${GREEN}✓ PostgreSQL is running and accepting connections${NC}"
                return 0
            else
                echo -e "${YELLOW}⚠ PostgreSQL is running but not accepting connections${NC}"
                echo -e "${YELLOW}🔄 Restarting PostgreSQL...${NC}"
                brew services restart "$PG_VERSION"
                sleep 3
                
                if check_postgresql; then
                    echo -e "${GREEN}✓ PostgreSQL is now accepting connections${NC}"
                    return 0
                else
                    echo -e "${RED}✗ PostgreSQL still not accepting connections${NC}"
                    return 1
                fi
            fi
        fi
    else
        # Non-brew system, try systemctl or pg_ctl
        if check_postgresql; then
            echo -e "${GREEN}✓ PostgreSQL is running${NC}"
            return 0
        else
            echo -e "${RED}✗ PostgreSQL is not running${NC}"
            echo -e "${YELLOW}Please start PostgreSQL manually${NC}"
            return 1
        fi
    fi
}

# Function to check if backend is running
check_backend() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            # Also check if it's actually our Django process
            if ps -p "$PID" | grep -q "manage.py runserver"; then
                return 0  # Running
            else
                # PID exists but it's not our process
                rm -f "$PID_FILE"
                return 1  # Not running
            fi
        else
            rm -f "$PID_FILE"
            return 1  # Not running
        fi
    fi
    return 1  # Not running
}

# Function to stop backend
stop_backend() {
    if check_backend; then
        PID=$(cat "$PID_FILE")
        echo -e "${YELLOW}Stopping backend (PID: $PID)...${NC}"
        kill "$PID" 2>/dev/null
        sleep 2
        if ps -p "$PID" > /dev/null 2>&1; then
            echo -e "${YELLOW}Force stopping...${NC}"
            kill -9 "$PID" 2>/dev/null
        fi
        rm -f "$PID_FILE"
        echo -e "${GREEN}Backend stopped${NC}"
    else
        # Check for orphaned Django processes
        ORPHAN_PIDS=$(ps aux | grep "[m]anage.py runserver" | awk '{print $2}')
        if [ ! -z "$ORPHAN_PIDS" ]; then
            echo -e "${YELLOW}Found orphaned Django processes, cleaning up...${NC}"
            for pid in $ORPHAN_PIDS; do
                kill "$pid" 2>/dev/null
                echo -e "${YELLOW}Killed orphaned process: $pid${NC}"
            done
            sleep 2
        fi
        echo -e "${YELLOW}Backend is not running${NC}"
    fi
}

# Function to start backend
start_backend() {
    if check_backend; then
        PID=$(cat "$PID_FILE")
        echo -e "${YELLOW}Backend is already running (PID: $PID)${NC}"
        return 0
    fi
    
    # First ensure PostgreSQL is running
    if ! fix_postgresql; then
        echo -e "${RED}✗ Cannot start backend without PostgreSQL${NC}"
        return 1
    fi
    
    # Check if port is in use
    if lsof -i :$PORT > /dev/null 2>&1; then
        echo -e "${YELLOW}Port $PORT is in use, checking if it's our service...${NC}"
        
        # Check if it's a Django process
        PORT_PID=$(lsof -ti :$PORT)
        if ps -p "$PORT_PID" | grep -q "manage.py"; then
            echo -e "${YELLOW}Found Django process on port $PORT (PID: $PORT_PID)${NC}"
            echo "$PORT_PID" > "$PID_FILE"
            echo -e "${GREEN}✓ Backend recovered (PID: $PORT_PID)${NC}"
            return 0
        else
            echo -e "${RED}Port $PORT is used by another process!${NC}"
            lsof -i :$PORT
            return 1
        fi
    fi
    
    # Activate virtual environment and start server
    echo -e "${GREEN}Starting backend on port $PORT...${NC}"
    
    # Rotate log file if it's too large (>10MB)
    if [ -f "$LOG_FILE" ] && [ $(stat -f%z "$LOG_FILE" 2>/dev/null || stat --format=%s "$LOG_FILE" 2>/dev/null || echo 0) -gt 10485760 ]; then
        mv "$LOG_FILE" "${LOG_FILE}.$(date +%Y%m%d_%H%M%S)"
        echo "Log file rotated"
    fi
    
    # Start Django with development settings
    cd "$SCRIPT_DIR"
    export SECRET_KEY='dev-secret-key-for-testing'
    nohup "$PYTHON_BIN" manage.py runserver --settings=unibos_backend.settings.development 0.0.0.0:$PORT >> "$LOG_FILE" 2>&1 &
    PID=$!
    echo $PID > "$PID_FILE"
    
    # Wait a moment and check if it started successfully
    sleep 3
    if check_backend; then
        echo -e "${GREEN}✓ Backend started successfully (PID: $PID)${NC}"
        echo -e "${GREEN}✓ Web UI: http://localhost:$PORT${NC}"
        echo -e "${GREEN}✓ API Status: http://localhost:$PORT/api/status/${NC}"
        
        # Check API status
        if curl -s http://localhost:$PORT/api/status/ > /dev/null 2>&1; then
            echo -e "${GREEN}✓ API is responding${NC}"
        else
            echo -e "${YELLOW}⚠ API may still be initializing...${NC}"
        fi
    else
        echo -e "${RED}✗ Failed to start backend${NC}"
        echo "Check the log file: $LOG_FILE"
        tail -20 "$LOG_FILE"
        return 1
    fi
}

# Function to restart backend
restart_backend() {
    echo -e "${BLUE}🔄 Restarting UNIBOS Web Core...${NC}"
    stop_backend
    sleep 2
    start_backend
}

# Function to show status
status_backend() {
    echo -e "${BLUE}📊 UNIBOS Web Core Status${NC}"
    echo -e "${BLUE}═══════════════════════════${NC}"
    
    # Check PostgreSQL
    if check_postgresql; then
        echo -e "${GREEN}✓ PostgreSQL: Running${NC}"
    else
        echo -e "${RED}✗ PostgreSQL: Not running${NC}"
    fi
    
    # Check Backend
    if check_backend; then
        PID=$(cat "$PID_FILE")
        echo -e "${GREEN}✓ Backend: Running (PID: $PID)${NC}"
        
        # Check API health
        if curl -s http://localhost:$PORT/api/status/ > /dev/null 2>&1; then
            echo -e "${GREEN}✓ API: Healthy${NC}"
            API_VERSION=$(curl -s http://localhost:$PORT/api/status/ | python3 -c "import sys, json; print(json.load(sys.stdin).get('version', 'unknown'))" 2>/dev/null)
            echo -e "${BLUE}  Version: $API_VERSION${NC}"
        else
            echo -e "${YELLOW}⚠ API: Not responding${NC}"
        fi
        
        # Show memory usage
        if command -v ps > /dev/null; then
            MEM_USAGE=$(ps aux | grep "$PID" | grep -v grep | awk '{print $4}')
            echo -e "${BLUE}  Memory: ${MEM_USAGE}%${NC}"
        fi
    else
        echo -e "${RED}✗ Backend: Not running${NC}"
    fi
}

# Function to tail logs
tail_logs() {
    echo -e "${YELLOW}Tailing server logs (Ctrl+C to stop)...${NC}"
    tail -f "$LOG_FILE"
}

# Function for auto-recovery (used by CLI)
auto_recovery() {
    echo -e "${BLUE}🔧 Running auto-recovery...${NC}"
    
    # Check and fix PostgreSQL
    if ! check_postgresql; then
        fix_postgresql
    fi
    
    # Check and restart backend if needed
    if ! check_backend; then
        start_backend
    elif ! curl -s http://localhost:$PORT/api/status/ > /dev/null 2>&1; then
        echo -e "${YELLOW}Backend is running but API not responding, restarting...${NC}"
        restart_backend
    else
        echo -e "${GREEN}✓ All services are healthy${NC}"
    fi
}

# Main script logic
case "${1:-}" in
    start)
        start_backend
        ;;
    stop)
        stop_backend
        ;;
    restart)
        restart_backend
        ;;
    status)
        status_backend
        ;;
    logs)
        tail_logs
        ;;
    auto-recovery)
        auto_recovery
        ;;
    *)
        echo "UNIBOS Backend Control Script"
        echo "Usage: $0 {start|stop|restart|status|logs|auto-recovery}"
        echo ""
        echo "Commands:"
        echo "  start         - Start the backend server"
        echo "  stop          - Stop the backend server"
        echo "  restart       - Restart the backend server"
        echo "  status        - Check backend status"
        echo "  logs          - Tail server logs"
        echo "  auto-recovery - Auto-fix common issues"
        exit 1
        ;;
esac

exit 0