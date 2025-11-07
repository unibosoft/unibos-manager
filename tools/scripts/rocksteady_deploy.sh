#!/bin/bash
# Unified Rocksteady Deployment Script
# Single script for all deployment needs

# Load configuration
source "$(dirname "$0")/rocksteady_config.sh"

# Default action
ACTION="${1:-deploy}"

# Help function
show_help() {
    cat << EOF
UNIBOS Rocksteady Deployment Tool

Usage: ./rocksteady_deploy.sh [action]

Actions:
  deploy       - full deployment with health checks (default)
  quick        - quick sync without full setup
  setup-db     - setup PostgreSQL database only
  setup-deps   - install Python dependencies only
  setup-env    - create .env file only
  check        - comprehensive health check of server
  clean        - clean and reinstall everything
  help         - show this help

Health Checks:
  All deployments now include comprehensive health checks that verify:
  - SSH connection and Python installation
  - virtual environment and Django installation
  - critical Python packages (djangorestframework, psycopg2, channels, etc.)
  - .env file with required variables
  - required directories (logs, staticfiles, media)
  - PostgreSQL database connection
  - Django settings can be imported
  - backend server is running and responding to HTTP requests

Examples:
  ./rocksteady_deploy.sh           # full deployment with health checks
  ./rocksteady_deploy.sh quick     # quick sync only
  ./rocksteady_deploy.sh setup-db  # setup database only
  ./rocksteady_deploy.sh check     # run health checks only
EOF
}

# Check SSH connection
check_connection() {
    print_step "Checking SSH connection to $ROCKSTEADY_HOST..."
    if test_ssh_connection; then
        print_success "Connected to $ROCKSTEADY_HOST"
        return 0
    else
        print_error "Cannot connect to $ROCKSTEADY_HOST"
        echo "Please check:"
        echo "  1. SSH key is loaded: ssh-add -l"
        echo "  2. Host is reachable: ping $ROCKSTEADY_HOST"
        echo "  3. SSH config is correct: ~/.ssh/config"
        return 1
    fi
}

# Sync files to rocksteady
sync_files() {
    print_step "Syncing files to $ROCKSTEADY_HOST..."
    
    # Safety check - ensure archive folder is never synced
    if [ -d "archive" ]; then
        print_warning "Archive folder detected - will be excluded from sync"
    fi
    
    # Use .rsyncignore file for exclusions
    if [ -f ".rsyncignore" ]; then
        print_info "Using .rsyncignore file for safe deployment"
        # CRITICAL: Removed --delete-excluded to prevent deletion of venv and other important files
        if rsync -avz --exclude-from=.rsyncignore . $ROCKSTEADY_HOST:$ROCKSTEADY_DIR/; then
            print_success "Files synced successfully (archive and venv protected)"
            return 0
        else
            print_error "File sync failed"
            return 1
        fi
    else
        print_error ".rsyncignore file not found - aborting for safety"
        print_warning "Archive protection requires .rsyncignore file"
        return 1
    fi
}

# Setup directories
setup_directories() {
    print_step "Setting up directories..."
    
    if run_on_rocksteady "cd $ROCKSTEADY_DIR/apps/web/backend && mkdir -p $REQUIRED_DIRS && touch logs/django.log"; then
        print_success "Directories created"
        return 0
    else
        print_error "Directory setup failed"
        return 1
    fi
}

# Setup Python virtual environment
setup_venv() {
    print_step "Setting up Python virtual environment..."
    
    if run_on_rocksteady "cd $ROCKSTEADY_DIR/apps/web/backend && $PYTHON_VERSION -m venv $VENV_DIR"; then
        print_success "Virtual environment created"
        
        # Upgrade pip
        print_step "Upgrading pip..."
        if run_on_rocksteady "cd $ROCKSTEADY_DIR/apps/web/backend && ./$VENV_DIR/bin/python -m pip install --upgrade pip"; then
            print_success "Pip upgraded"
            return 0
        else
            print_warning "Pip upgrade failed, continuing..."
            return 0
        fi
    else
        print_error "Virtual environment setup failed"
        return 1
    fi
}

# Install Python dependencies
install_dependencies() {
    print_step "Installing Python dependencies..."
    
    # Try minimal requirements first if file exists
    if run_on_rocksteady "cd $ROCKSTEADY_DIR/apps/web/backend && [ -f requirements_minimal.txt ]"; then
        print_info "Installing from requirements_minimal.txt..."
        if run_on_rocksteady "cd $ROCKSTEADY_DIR/apps/web/backend && ./$VENV_DIR/bin/pip install -r requirements_minimal.txt"; then
            print_success "Dependencies installed from requirements_minimal.txt"
            return 0
        fi
    fi
    
    # Fallback to individual packages
    print_info "Installing packages individually..."
    if run_on_rocksteady "cd $ROCKSTEADY_DIR/apps/web/backend && ./$VENV_DIR/bin/pip install $ALL_PACKAGES"; then
        print_success "All packages installed"
        return 0
    else
        print_warning "Some packages may have failed, trying core packages only..."
        if run_on_rocksteady "cd $ROCKSTEADY_DIR/apps/web/backend && ./$VENV_DIR/bin/pip install $CORE_PACKAGES $DB_PACKAGES"; then
            print_success "Core packages installed"
            return 0
        else
            print_error "Failed to install core packages"
            return 1
        fi
    fi
}

# Setup environment file
setup_env_file() {
    print_step "Setting up environment file..."
    
    # Generate .env content and write to remote
    ENV_CONTENT=$(generate_env_content)
    if run_on_rocksteady "cd $ROCKSTEADY_DIR/apps/web/backend && cat > .env << 'EOF'
$ENV_CONTENT
EOF"; then
        print_success ".env file created"
        return 0
    else
        print_error "Failed to create .env file"
        return 1
    fi
}

# Setup PostgreSQL database
setup_database() {
    print_step "Setting up PostgreSQL database..."
    
    # Check if PostgreSQL is installed
    if ! run_on_rocksteady "command -v psql >/dev/null 2>&1"; then
        print_warning "PostgreSQL not installed, installing..."
        run_on_rocksteady "sudo apt update && sudo apt install -y postgresql postgresql-contrib"
    fi
    
    # Create database and user
    run_on_rocksteady "sudo -u postgres psql" << EOF
-- Create user if not exists
DO
\$do\$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_user
      WHERE usename = '$DB_USER') THEN
      CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';
   END IF;
END
\$do\$;

-- Create database if not exists
SELECT 'CREATE DATABASE $DB_NAME OWNER $DB_USER'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$DB_NAME')\gexec

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
EOF
    
    # Test connection
    if run_on_rocksteady "PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c 'SELECT version();' >/dev/null 2>&1"; then
        print_success "Database setup complete"
        return 0
    else
        print_warning "Database setup may need manual intervention"
        return 1
    fi
}

# Run Django migrations
run_migrations() {
    print_step "Running Django migrations..."
    
    if run_on_rocksteady "cd $ROCKSTEADY_DIR/apps/web/backend && ./$VENV_DIR/bin/python manage.py migrate --noinput"; then
        print_success "Migrations completed"
        return 0
    else
        print_warning "Migrations failed, may need manual check"
        return 1
    fi
}

# Collect static files
collect_static() {
    print_step "Collecting static files..."
    
    if run_on_rocksteady "cd $ROCKSTEADY_DIR/apps/web/backend && ./$VENV_DIR/bin/python manage.py collectstatic --noinput"; then
        print_success "Static files collected"
        return 0
    else
        print_warning "Static collection failed, continuing..."
        return 0
    fi
}

# Start backend server
start_backend() {
    print_step "Starting backend server..."

    # Check if gunicorn systemd service exists
    if run_on_rocksteady "sudo systemctl list-units --type=service --all | grep -q gunicorn.service"; then
        print_info "Restarting Gunicorn service..."
        if run_on_rocksteady "sudo systemctl restart gunicorn"; then
            print_success "Gunicorn service restarted"

            # Also restart nginx to ensure it picks up any changes
            if run_on_rocksteady "sudo systemctl restart nginx"; then
                print_success "Nginx restarted"
            else
                print_warning "Nginx restart failed, but Gunicorn is running"
            fi
            return 0
        else
            print_error "Failed to restart Gunicorn service"
            return 1
        fi
    else
        # Fallback to runserver if gunicorn service doesn't exist
        print_info "Gunicorn service not found, using runserver..."

        # Kill existing server
        run_on_rocksteady "pkill -f 'manage.py runserver' || true"

        # Start new server
        if run_on_rocksteady "cd $ROCKSTEADY_DIR/apps/web/backend && nohup ./$VENV_DIR/bin/python manage.py runserver 0.0.0.0:$DJANGO_PORT > logs/server.log 2>&1 &"; then
            print_success "Backend server started on port $DJANGO_PORT"
            return 0
        else
            print_error "Failed to start backend server"
            return 1
        fi
    fi
}

# Comprehensive health check
health_check() {
    print_step "Running comprehensive health checks..."

    local FAILED=0
    echo ""

    # Check SSH connection
    echo "SSH Connection:"
    if test_ssh_connection; then
        print_success "  connected"
    else
        print_error "  not connected"
        return 1
    fi

    # Check Python version
    echo ""
    echo "Python:"
    if run_on_rocksteady "$PYTHON_VERSION --version" 2>&1 | grep -q "Python 3"; then
        local PY_VERSION=$(run_on_rocksteady "$PYTHON_VERSION --version" 2>&1)
        print_success "  $PY_VERSION"
    else
        print_error "  python3 not found"
        FAILED=1
    fi

    # Check virtual environment
    echo ""
    echo "Virtual Environment:"
    if run_on_rocksteady "[ -d $ROCKSTEADY_DIR/apps/web/backend/$VENV_DIR ]"; then
        print_success "  venv exists at $ROCKSTEADY_DIR/apps/web/backend/$VENV_DIR"
    else
        print_error "  venv not found"
        FAILED=1
    fi

    # Check Django installation
    echo ""
    echo "Django:"
    if run_on_rocksteady "cd $ROCKSTEADY_DIR/apps/web/backend && ./$VENV_DIR/bin/python -c 'import django; print(django.__version__)' 2>/dev/null"; then
        local DJANGO_VERSION=$(run_on_rocksteady "cd $ROCKSTEADY_DIR/apps/web/backend && ./$VENV_DIR/bin/python -c 'import django; print(django.__version__)' 2>/dev/null")
        print_success "  Django $DJANGO_VERSION installed"
    else
        print_error "  Django not installed or import failed"
        FAILED=1
    fi

    # Check critical Python packages
    echo ""
    echo "Critical Packages:"
    local PACKAGES=("djangorestframework" "psycopg2" "channels" "daphne" "aiohttp" "django_environ")
    for pkg in "${PACKAGES[@]}"; do
        if run_on_rocksteady "cd $ROCKSTEADY_DIR/apps/web/backend && ./$VENV_DIR/bin/python -c 'import $pkg' 2>/dev/null"; then
            print_success "  $pkg installed"
        else
            print_warning "  $pkg not installed"
            FAILED=1
        fi
    done

    # Check .env file
    echo ""
    echo "Environment Configuration:"
    if run_on_rocksteady "[ -f $ROCKSTEADY_DIR/apps/web/backend/.env ]"; then
        print_success "  .env file exists"

        # Check critical env vars
        local ENV_VARS=("SECRET_KEY" "DB_NAME" "DB_USER" "DB_PASSWORD" "ALLOWED_HOSTS")
        for var in "${ENV_VARS[@]}"; do
            if run_on_rocksteady "grep -q '^$var=' $ROCKSTEADY_DIR/apps/web/backend/.env"; then
                print_success "    $var configured"
            else
                print_warning "    $var missing"
                FAILED=1
            fi
        done
    else
        print_error "  .env file not found"
        FAILED=1
    fi

    # Check required directories
    echo ""
    echo "Required Directories:"
    local DIRS=("logs" "staticfiles" "media")
    for dir in "${DIRS[@]}"; do
        if run_on_rocksteady "[ -d $ROCKSTEADY_DIR/apps/web/backend/$dir ]"; then
            print_success "  $dir/ exists"
        else
            print_warning "  $dir/ missing"
            FAILED=1
        fi
    done

    # Check PostgreSQL
    echo ""
    echo "Database:"
    if run_on_rocksteady "command -v psql >/dev/null 2>&1"; then
        print_success "  PostgreSQL client installed"

        if run_on_rocksteady "PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c 'SELECT 1;' >/dev/null 2>&1"; then
            print_success "  Database connection successful"
        else
            print_error "  Cannot connect to database"
            FAILED=1
        fi
    else
        print_error "  PostgreSQL not installed"
        FAILED=1
    fi

    # Check Django settings can be imported
    echo ""
    echo "Django Settings:"
    if run_on_rocksteady "cd $ROCKSTEADY_DIR/apps/web/backend && ./$VENV_DIR/bin/python -c 'import os; os.environ.setdefault(\"DJANGO_SETTINGS_MODULE\", \"unibos_backend.settings.development\"); import django; django.setup()' 2>/dev/null"; then
        print_success "  Settings import successful"
    else
        print_error "  Settings import failed"
        run_on_rocksteady "cd $ROCKSTEADY_DIR/apps/web/backend && ./$VENV_DIR/bin/python -c 'import os; os.environ.setdefault(\"DJANGO_SETTINGS_MODULE\", \"unibos_backend.settings.development\"); import django; django.setup()' 2>&1 | tail -10"
        FAILED=1
    fi

    # Check backend server status
    echo ""
    echo "Backend Server:"
    if run_on_rocksteady "pgrep -f 'manage.py runserver' >/dev/null"; then
        print_success "  Process running (port $DJANGO_PORT)"

        # Try HTTP request
        if run_on_rocksteady "curl -s -o /dev/null -w '%{http_code}' http://localhost:$DJANGO_PORT 2>/dev/null | grep -q '200\|301\|302'"; then
            print_success "  HTTP server responding"
        else
            print_warning "  Server process running but not responding to HTTP"
            FAILED=1
        fi
    else
        print_error "  Not running"
        FAILED=1
    fi

    # Check nginx if exists
    echo ""
    echo "Nginx (optional):"
    if run_on_rocksteady "command -v nginx >/dev/null 2>&1"; then
        if run_on_rocksteady "systemctl is-active nginx >/dev/null 2>&1"; then
            print_success "  nginx running"
        else
            print_warning "  nginx installed but not running"
        fi
    else
        print_info "  nginx not installed (optional)"
    fi

    echo ""
    if [ $FAILED -eq 0 ]; then
        print_success "All health checks passed!"
        echo ""
        echo "Access the application at:"
        echo "  http://$ROCKSTEADY_HOST:$DJANGO_PORT"
        return 0
    else
        print_error "Some health checks failed!"
        echo ""
        echo "Please review the errors above and fix them."
        return 1
    fi
}

# Check server status (simple version for backwards compatibility)
check_status() {
    health_check
}

# Full deployment
full_deploy() {
    echo "🚀 Starting full deployment to $ROCKSTEADY_HOST"
    echo ""

    check_connection || exit 1
    sync_files || exit 1
    setup_directories || exit 1
    setup_venv || exit 1
    install_dependencies || exit 1
    setup_env_file || exit 1
    run_migrations || exit 1
    collect_static || exit 1
    start_backend || exit 1

    # Wait for server to start
    print_step "Waiting for server to start..."
    sleep 3

    echo ""
    print_success "Deployment steps completed!"
    echo ""

    # Run health checks
    echo "═══════════════════════════════════════════"
    echo "Running post-deployment health checks..."
    echo "═══════════════════════════════════════════"
    if health_check; then
        echo ""
        print_success "Deployment successful and all checks passed!"
        return 0
    else
        echo ""
        print_error "Deployment completed but health checks failed!"
        print_warning "Please review the issues above before using the system."
        return 1
    fi
}

# Quick deployment (sync only)
quick_deploy() {
    echo "⚡ Quick deployment to $ROCKSTEADY_HOST"
    echo ""

    check_connection || exit 1
    sync_files || exit 1

    # Ensure required directories exist
    print_step "Checking required directories..."
    if run_on_rocksteady "cd $ROCKSTEADY_DIR && mkdir -p logs apps/web/backend/logs apps/web/backend/venv && touch logs/django.log apps/web/backend/logs/django.log"; then
        print_success "Directories verified"
    fi

    # Restart backend if running
    if run_on_rocksteady "pgrep -f 'manage.py runserver' >/dev/null"; then
        print_step "Restarting backend..."
        run_on_rocksteady "pkill -f 'manage.py runserver' || true"
        start_backend
    fi

    print_success "Quick deployment complete!"
}

# Clean deployment (remove everything and start fresh)
clean_deploy() {
    echo "🧹 Clean deployment to $ROCKSTEADY_HOST"
    echo ""
    
    print_warning "This will remove all existing data and start fresh!"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Cancelled"
        exit 0
    fi
    
    check_connection || exit 1
    
    print_step "Removing old installation..."
    run_on_rocksteady "cd $ROCKSTEADY_DIR/apps/web/backend && rm -rf $VENV_DIR logs staticfiles media"
    
    full_deploy
}

# Main execution
case "$ACTION" in
    deploy)
        full_deploy
        ;;
    quick)
        quick_deploy
        ;;
    setup-db)
        check_connection && setup_database
        ;;
    setup-deps)
        check_connection && setup_venv && install_dependencies
        ;;
    setup-env)
        check_connection && setup_env_file
        ;;
    check)
        check_status
        ;;
    clean)
        clean_deploy
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown action: $ACTION"
        echo ""
        show_help
        exit 1
        ;;
esac