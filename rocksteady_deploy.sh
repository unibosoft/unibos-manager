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
  deploy       - Full deployment (default)
  quick        - Quick sync without setup
  setup-db     - Setup PostgreSQL database
  setup-deps   - Install Python dependencies
  setup-env    - Create .env file
  check        - Check server status
  clean        - Clean and reinstall everything
  help         - Show this help

Examples:
  ./rocksteady_deploy.sh           # Full deployment
  ./rocksteady_deploy.sh quick     # Quick sync only
  ./rocksteady_deploy.sh setup-db  # Setup database only
  ./rocksteady_deploy.sh check     # Check server status
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
        if rsync -avz --exclude-from=.rsyncignore --delete-excluded . $ROCKSTEADY_HOST:$ROCKSTEADY_DIR/; then
            print_success "Files synced successfully (archive protected)"
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
    
    if run_on_rocksteady "cd $ROCKSTEADY_DIR/backend && mkdir -p $REQUIRED_DIRS && touch logs/django.log"; then
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
    
    if run_on_rocksteady "cd $ROCKSTEADY_DIR/backend && $PYTHON_VERSION -m venv $VENV_DIR"; then
        print_success "Virtual environment created"
        
        # Upgrade pip
        print_step "Upgrading pip..."
        if run_on_rocksteady "cd $ROCKSTEADY_DIR/backend && ./$VENV_DIR/bin/python -m pip install --upgrade pip"; then
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
    if run_on_rocksteady "cd $ROCKSTEADY_DIR/backend && [ -f requirements_minimal.txt ]"; then
        print_info "Installing from requirements_minimal.txt..."
        if run_on_rocksteady "cd $ROCKSTEADY_DIR/backend && ./$VENV_DIR/bin/pip install -r requirements_minimal.txt"; then
            print_success "Dependencies installed from requirements_minimal.txt"
            return 0
        fi
    fi
    
    # Fallback to individual packages
    print_info "Installing packages individually..."
    if run_on_rocksteady "cd $ROCKSTEADY_DIR/backend && ./$VENV_DIR/bin/pip install $ALL_PACKAGES"; then
        print_success "All packages installed"
        return 0
    else
        print_warning "Some packages may have failed, trying core packages only..."
        if run_on_rocksteady "cd $ROCKSTEADY_DIR/backend && ./$VENV_DIR/bin/pip install $CORE_PACKAGES $DB_PACKAGES"; then
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
    if run_on_rocksteady "cd $ROCKSTEADY_DIR/backend && cat > .env << 'EOF'
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
    
    if run_on_rocksteady "cd $ROCKSTEADY_DIR/backend && ./$VENV_DIR/bin/python manage.py migrate --noinput"; then
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
    
    if run_on_rocksteady "cd $ROCKSTEADY_DIR/backend && ./$VENV_DIR/bin/python manage.py collectstatic --noinput"; then
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
    
    # Kill existing server
    run_on_rocksteady "pkill -f 'manage.py runserver' || true"
    
    # Start new server
    if run_on_rocksteady "cd $ROCKSTEADY_DIR/backend && nohup ./$VENV_DIR/bin/python manage.py runserver 0.0.0.0:$DJANGO_PORT > logs/server.log 2>&1 &"; then
        print_success "Backend server started on port $DJANGO_PORT"
        return 0
    else
        print_error "Failed to start backend server"
        return 1
    fi
}

# Check server status
check_status() {
    print_step "Checking server status..."
    
    echo ""
    echo "SSH Connection:"
    if test_ssh_connection; then
        echo "  ✅ Connected"
    else
        echo "  ❌ Not connected"
        return 1
    fi
    
    echo ""
    echo "Python:"
    run_on_rocksteady "$PYTHON_VERSION --version"
    
    echo ""
    echo "Django:"
    if run_on_rocksteady "cd $ROCKSTEADY_DIR/backend && [ -d $VENV_DIR ] && ./$VENV_DIR/bin/python -c 'import django; print(f\"  ✅ Django {django.__version__}\")'"; then
        :
    else
        echo "  ❌ Django not installed"
    fi
    
    echo ""
    echo "Database:"
    if run_on_rocksteady "PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c 'SELECT version();' >/dev/null 2>&1"; then
        echo "  ✅ PostgreSQL connected"
    else
        echo "  ❌ PostgreSQL not connected"
    fi
    
    echo ""
    echo "Backend Server:"
    if run_on_rocksteady "pgrep -f 'manage.py runserver' >/dev/null"; then
        echo "  ✅ Running on port $DJANGO_PORT"
    else
        echo "  ❌ Not running"
    fi
    
    echo ""
    echo "Project Location: $ROCKSTEADY_HOST:$ROCKSTEADY_DIR"
    echo ""
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
    
    echo ""
    print_success "Deployment complete!"
    echo ""
    echo "Access the application at:"
    echo "  http://$ROCKSTEADY_HOST:$DJANGO_PORT"
    echo ""
}

# Quick deployment (sync only)
quick_deploy() {
    echo "⚡ Quick deployment to $ROCKSTEADY_HOST"
    echo ""
    
    check_connection || exit 1
    sync_files || exit 1
    
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
    run_on_rocksteady "cd $ROCKSTEADY_DIR/backend && rm -rf $VENV_DIR logs staticfiles media"
    
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