#!/bin/bash
# UNIBOS Unified Version Management System
# Combines all version management operations in one optimized script
# Author: Berk Hatırlı

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

# Configuration
ARCHIVE_DIR="archive/versions"
COMPRESSED_DIR="archive/compressed"
VERSION_FILE="src/VERSION.json"
DJANGO_VERSION_FILE="backend/apps/web_ui/views.py"
LOGIN_TEMPLATE="backend/templates/authentication/login.html"

# Print functions
print_color() {
    echo -e "${1}${2}${NC}"
}

print_header() {
    print_color "$CYAN" "╔══════════════════════════════════════════════════════╗"
    print_color "$CYAN" "║$(printf "%-56s" " $1")║"
    print_color "$CYAN" "╚══════════════════════════════════════════════════════╝"
}

# Get Istanbul time
get_istanbul_time() {
    TZ='Europe/Istanbul' date "$1"
}

# Version management functions
get_current_version() {
    if [ -f "$VERSION_FILE" ]; then
        grep '"version"' "$VERSION_FILE" | head -1 | sed 's/.*"v\([0-9]*\)".*/\1/'
    else
        echo "0"
    fi
}

get_highest_git_version() {
    git tag 2>/dev/null | grep "^v[0-9]" | sed 's/^v//' | sort -n | tail -1 || echo "0"
}

version_exists() {
    git tag 2>/dev/null | grep -q "^v${1}$"
}

check_version_gaps() {
    local start=${1:-1}
    local end=$2
    local gaps=""
    
    for ((i=start; i<=end; i++)); do
        if ! version_exists "$i"; then
            gaps="$gaps $i"
        fi
    done
    
    echo "$gaps"
}

calculate_next_version() {
    local current=$(get_current_version)
    local highest=$(get_highest_git_version)
    
    if [ "$highest" -gt "$current" ] 2>/dev/null; then
        echo $((highest + 1))
    else
        echo $((current + 1))
    fi
}

# Update functions
update_version_json() {
    local version=$1
    local description=$2
    local timestamp=$(get_istanbul_time "+%Y-%m-%d %H:%M:%S %z")
    local build=$(get_istanbul_time "+%Y%m%d_%H%M")
    
    # Clean version - remove any existing 'v' prefix
    local clean_version=$(echo "$version" | sed 's/^v//')
    
    # Use Python for JSON manipulation
    python3 -c "
import json
with open('$VERSION_FILE', 'r') as f:
    data = json.load(f)
data['version'] = 'v$clean_version'
data['build_number'] = '$build'
data['release_date'] = '$timestamp'
data['description'] = '$description'
with open('$VERSION_FILE', 'w') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
"
    print_color "$GREEN" "✅ VERSION.json updated"
}

update_django_files() {
    local version=$1
    
    # Clean version - remove any existing 'v' prefix
    local clean_version=$(echo "$version" | sed 's/^v//')
    
    # Update Django views.py
    if [ -f "$DJANGO_VERSION_FILE" ]; then
        sed -i.bak "s/'version': 'v[0-9]*'/'version': 'v$clean_version'/" "$DJANGO_VERSION_FILE"
        rm -f "${DJANGO_VERSION_FILE}.bak"
        print_color "$GREEN" "✅ Django views.py updated"
    fi
    
    # Update login template
    if [ -f "$LOGIN_TEMPLATE" ]; then
        sed -i.bak "s/v[0-9]* - /v$clean_version - /" "$LOGIN_TEMPLATE"
        rm -f "${LOGIN_TEMPLATE}.bak"
        print_color "$GREEN" "✅ Login template updated"
    fi
}

# Archive functions
create_archive() {
    local version=$1
    
    # Clean version - remove any existing 'v' prefix
    local clean_version=$(echo "$version" | sed 's/^v//')
    
    local timestamp=$(get_istanbul_time "+%Y%m%d_%H%M")
    local archive_name="unibos_v${clean_version}_${timestamp}"
    
    print_color "$YELLOW" "\n📦 Creating archive (open folder format)..."
    
    # Check and archive screenshots before main archive
    if ls Screenshot*.png >/dev/null 2>&1; then
        print_color "$CYAN" "📷 Found screenshots, archiving..."
        
        # Create screenshots archive directory based on version ranges
        local version_num=$(echo "$version" | sed 's/v//')
        local range_dir=""
        
        if [ "$version_num" -le 20 ]; then
            range_dir="v001-v020"
        elif [ "$version_num" -le 40 ]; then
            range_dir="v021-v040"
        elif [ "$version_num" -le 60 ]; then
            range_dir="v041-v060"
        elif [ "$version_num" -le 100 ]; then
            range_dir="v061-v100"
        elif [ "$version_num" -le 150 ]; then
            range_dir="v101-v150"
        elif [ "$version_num" -le 200 ]; then
            range_dir="v151-v200"
        elif [ "$version_num" -le 300 ]; then
            range_dir="v201-v300"
        elif [ "$version_num" -le 400 ]; then
            range_dir="v301-v400"
        elif [ "$version_num" -le 500 ]; then
            range_dir="v401-v500"
        else
            range_dir="v501-current"
        fi
        
        # Create directory and move screenshots
        mkdir -p "archive/media/screenshots/$range_dir"
        
        for screenshot in Screenshot*.png; do
            if [ -f "$screenshot" ]; then
                # Rename with version number (ensure clean version)
                local new_name="v${clean_version}_${screenshot}"
                mv "$screenshot" "archive/media/screenshots/$range_dir/$new_name"
                print_color "$GREEN" "   ✓ Archived: $screenshot → $range_dir/$new_name"
            fi
        done
    fi
    
    # Create archive directory
    mkdir -p "$ARCHIVE_DIR"
    
    # Create uncompressed archive only (no ZIP)
    print_color "$CYAN" "📂 Creating folder archive: $archive_name"
    rsync -av --exclude='archive' --exclude='.git' --exclude='venv' \
              --exclude='__pycache__' --exclude='*.pyc' --exclude='.DS_Store' \
              --exclude='*.zip' --exclude='node_modules' --exclude='.env.local' \
              --exclude='archive_backup_*' --exclude='**/archive_backup_*' \
              --exclude='berk_claude_file_pool_DONT_DELETE' \
              --exclude='data_db' --exclude='data_db_backup_*' \
              --exclude='quarantine' --exclude='docs' \
              --exclude='data' --exclude='projects' \
              --exclude='backend/media' --exclude='backend/documents/2025' \
              --exclude='*.sqlite3' --exclude='*.sqlite3.backup' \
              --exclude='*.log' --exclude='backend/staticfiles' \
              --exclude='backend/logs' \
              . "$ARCHIVE_DIR/$archive_name/"
    
    # Show archive size
    local size=$(du -sh "$ARCHIVE_DIR/$archive_name" | cut -f1)
    print_color "$GREEN" "✅ Archive created: ${ARCHIVE_DIR}/${archive_name} (Size: $size)"
    print_color "$CYAN" "📍 Location: $(pwd)/${ARCHIVE_DIR}/${archive_name}"
}

# Git operations
git_operations() {
    local version=$1
    local description=$2
    
    print_color "$YELLOW" "\n📝 Git operations..."
    
    # Ensure version doesn't already have 'v' prefix to prevent double 'v'
    clean_version=$(echo "$version" | sed 's/^v//')
    
    # Add and commit on main
    git checkout main 2>/dev/null || true
    git add -A
    git commit -m "v${clean_version}: ${description}" || true
    
    # Create version branch from main (they will be identical)
    git checkout -b "v${clean_version}" 2>/dev/null || git checkout "v${clean_version}"
    
    # Push version branch
    git push origin "v${clean_version}"
    
    # Go back to main and push (main and vXXX are the same)
    git checkout main
    git push origin main
    
    # Create and push tag
    git tag "v${clean_version}" 2>/dev/null || true
    git push origin --tags
    
    print_color "$GREEN" "✅ Git operations completed (v${clean_version} and main are identical)"
}

# Main menu
show_menu() {
    print_header "UNIBOS Unified Version Manager"
    
    echo -e "\n${BLUE}Select an operation:${NC}"
    echo "1) Quick Release (auto version + commit + archive)"
    echo "2) Status Check (versions, gaps, sync)"
    echo "3) Manual Version (specify version number)"
    echo "4) Fix Version Sync (align VERSION.json with git)"
    echo "5) Archive Only (no git operations)"
    echo "6) Cleanup Old Archives"
    echo "0) Exit"
    
    echo -e "\n${YELLOW}Enter choice [0-6]:${NC} "
}

# Status check
status_check() {
    print_header "Version Status Check"
    
    local current=$(get_current_version)
    local highest=$(get_highest_git_version)
    
    echo -e "\n${BLUE}📊 Current Status:${NC}"
    echo "   VERSION.json: v${current}"
    echo "   Highest Git Tag: v${highest}"
    
    if [ "$current" != "$highest" ]; then
        print_color "$YELLOW" "\n⚠️  Version mismatch detected!"
    else
        print_color "$GREEN" "\n✅ Versions are synchronized"
    fi
    
    # Check gaps
    echo -e "\n${BLUE}🔍 Checking for gaps:${NC}"
    local start=$((highest - 10))
    [ $start -lt 1 ] && start=1
    
    local gaps=$(check_version_gaps $start $highest)
    if [ -z "$gaps" ]; then
        print_color "$GREEN" "   No gaps found"
    else
        for gap in $gaps; do
            print_color "$RED" "   Missing: v${gap}"
        done
    fi
    
    # Recent versions
    echo -e "\n${BLUE}📝 Recent versions:${NC}"
    git tag | grep "^v[0-9]" | sort -V | tail -5
}

# Generate auto commit message
generate_commit_message() {
    local changes=""
    local details=()
    
    # Get all changed files
    local all_files=$(git diff --name-only; git ls-files --others --exclude-standard)
    
    # Count file types
    local py_files=$(echo "$all_files" | grep "\.py$" | wc -l | xargs)
    local js_files=$(echo "$all_files" | grep "\.js$" | wc -l | xargs)
    local html_files=$(echo "$all_files" | grep "\.html$" | wc -l | xargs)
    local sh_files=$(echo "$all_files" | grep "\.sh$" | wc -l | xargs)
    local md_files=$(echo "$all_files" | grep "\.md$" | wc -l | xargs)
    local css_files=$(echo "$all_files" | grep "\.css$" | wc -l | xargs)
    
    # Analyze Django apps changes
    if echo "$all_files" | grep -q "backend/apps/"; then
        local modules=$(echo "$all_files" | grep "backend/apps/" | cut -d'/' -f3 | sort -u)
        for module in $modules; do
            case $module in
                movies) details+=("Movies module updates") ;;
                music) details+=("Music module updates") ;;
                restopos) details+=("RestoPOS module updates") ;;
                documents) details+=("Documents module improvements") ;;
                currencies) details+=("Currencies module updates") ;;
                authentication) details+=("Authentication system changes") ;;
                web_ui) details+=("Web UI enhancements") ;;
                wimm) details+=("WIMM module updates") ;;
                wims) details+=("WIMS module updates") ;;
                cctv) details+=("CCTV module improvements") ;;
                *) details+=("$module module changes") ;;
            esac
        done
    fi
    
    # Check for specific file patterns
    if echo "$all_files" | grep -q "models\.py"; then
        details+=("database model changes")
    fi
    
    if echo "$all_files" | grep -q "views\.py"; then
        details+=("view logic updates")
    fi
    
    if echo "$all_files" | grep -q "urls\.py"; then
        details+=("URL routing updates")
    fi
    
    if echo "$all_files" | grep -q "templates/"; then
        details+=("template improvements")
    fi
    
    if echo "$all_files" | grep -q "static/"; then
        details+=("static files updates")
    fi
    
    if echo "$all_files" | grep -q "migrations/"; then
        details+=("database migrations")
    fi
    
    # Check for version management changes
    if echo "$all_files" | grep -q -E "(version|VERSION)"; then
        details+=("version management improvements")
    fi
    
    # Check for script changes
    if [ $sh_files -gt 0 ]; then
        if echo "$all_files" | grep -q "unibos_version\.sh"; then
            details+=("unified version manager updates")
        else
            details+=("script optimizations")
        fi
    fi
    
    # Check for documentation
    if [ $md_files -gt 0 ]; then
        details+=("documentation updates")
    fi
    
    # Check for CSS changes
    if [ $css_files -gt 0 ]; then
        details+=("styling improvements")
    fi
    
    # Check for screenshots
    if echo "$all_files" | grep -q "screenshot\|Screenshot"; then
        details+=("screenshots archived")
    fi
    
    # Analyze git diff for keywords
    local diff_content=$(git diff 2>/dev/null | head -500)
    
    if echo "$diff_content" | grep -qi "fix\|bug\|error\|issue"; then
        changes="Fixed "
    elif echo "$diff_content" | grep -qi "add\|new\|create\|implement"; then
        changes="Added "
    elif echo "$diff_content" | grep -qi "optimize\|improve\|enhance\|refactor"; then
        changes="Optimized "
    elif echo "$diff_content" | grep -qi "update\|modify\|change"; then
        changes="Updated "
    elif echo "$diff_content" | grep -qi "remove\|delete\|clean"; then
        changes="Cleaned "
    else
        changes="Updated "
    fi
    
    # Build final message
    if [ ${#details[@]} -gt 0 ]; then
        # Join details with comma
        local joined_details=$(IFS=", "; echo "${details[*]}")
        changes="${changes}${joined_details}"
        
        # Add file count summary if significant
        local total_files=$(echo "$all_files" | wc -l | xargs)
        if [ $total_files -gt 5 ]; then
            changes="$changes ($total_files files)"
        fi
    else
        # Fallback to generic message with file counts
        local parts=()
        [ $py_files -gt 0 ] && parts+=("$py_files Python")
        [ $js_files -gt 0 ] && parts+=("$js_files JS")
        [ $html_files -gt 0 ] && parts+=("$html_files HTML")
        [ $sh_files -gt 0 ] && parts+=("$sh_files scripts")
        [ $md_files -gt 0 ] && parts+=("$md_files docs")
        
        if [ ${#parts[@]} -gt 0 ]; then
            changes="${changes}$(IFS=", "; echo "${parts[*]}") files"
        else
            changes="${changes}project files"
        fi
    fi
    
    echo "$changes"
}

# Quick release
quick_release() {
    local next_version=$(calculate_next_version)
    
    print_header "Quick Release - v${next_version}"
    
    # Check for uncommitted changes
    if [[ -n $(git status -s) ]]; then
        print_color "$CYAN" "\n📊 Analyzing changes..."
        
        # Show changed files
        echo -e "\n${BLUE}Changed files:${NC}"
        git status -s | head -10
        
        local file_count=$(git status -s | wc -l)
        if [ $file_count -gt 10 ]; then
            echo "... and $((file_count - 10)) more files"
        fi
        
        # Generate auto commit message
        local auto_message=$(generate_commit_message)
        
        echo -e "\n${CYAN}Auto-generated description:${NC}"
        echo "  $auto_message"
        
        echo -e "\n${YELLOW}Enter commit description (or press Enter to use auto):${NC}"
        read -r description
        
        # Use auto message if empty
        if [ -z "$description" ]; then
            description="$auto_message"
            print_color "$GREEN" "✓ Using auto-generated message"
        fi
    else
        echo -e "\n${YELLOW}Enter commit description:${NC}"
        read -r description
        
        if [ -z "$description" ]; then
            description="Regular update and maintenance"
        fi
    fi
    
    # Perform all operations
    update_version_json "$next_version" "$description"
    update_django_files "$next_version"
    create_archive "$next_version"
    git_operations "$next_version" "$description"
    
    print_color "$GREEN" "\n✅ Version v${next_version} released successfully!"
    
    # Restart services to apply new version
    print_color "$YELLOW" "\n🔄 Restarting services with new version..."
    
    # Restart web core (Django backend)
    if [ -f "backend/start_backend.sh" ]; then
        print_color "$CYAN" "   Restarting web core..."
        ./backend/start_backend.sh restart
        sleep 2
        print_color "$GREEN" "   ✅ Web core restarted"
        
        # Open web UI in browser to show new version
        print_color "$CYAN" "   Opening web UI in browser..."
        if command -v open > /dev/null 2>&1; then
            # macOS
            open "http://localhost:8000" 2>/dev/null
        elif command -v xdg-open > /dev/null 2>&1; then
            # Linux
            xdg-open "http://localhost:8000" 2>/dev/null &
        elif command -v wslview > /dev/null 2>&1; then
            # WSL
            wslview "http://localhost:8000" 2>/dev/null &
        fi
    else
        print_color "$YELLOW" "   ⚠️  Could not find backend/start_backend.sh"
    fi
    
    # Restart CLI (unibos.sh) in background
    print_color "$CYAN" "   Restarting CLI..."
    print_color "$GREEN" "\n✨ Version v${next_version} is now active!"
    print_color "$CYAN" "   The CLI will restart automatically in 3 seconds..."
    
    # Use exec to replace current process with new unibos.sh
    sleep 3
    exec ./unibos.sh
}

# Cleanup old archives
cleanup_archives() {
    print_header "Archive Cleanup"
    
    echo -e "\n${BLUE}Archive sizes:${NC}"
    du -sh "$ARCHIVE_DIR"/* 2>/dev/null | sort -h | tail -10
    
    echo -e "\n${YELLOW}Keep how many recent versions? (default: 10):${NC}"
    read -r keep_count
    keep_count=${keep_count:-10}
    
    # Find and remove old archives
    local count=$(ls -1 "$ARCHIVE_DIR" | wc -l)
    if [ $count -gt $keep_count ]; then
        local remove_count=$((count - keep_count))
        ls -1t "$ARCHIVE_DIR" | tail -n $remove_count | while read dir; do
            print_color "$YELLOW" "Removing: $dir"
            rm -rf "$ARCHIVE_DIR/$dir"
            rm -f "$COMPRESSED_DIR/${dir}.zip"
        done
        print_color "$GREEN" "✅ Cleanup completed"
    else
        print_color "$GREEN" "No cleanup needed"
    fi
}

# Main loop
main() {
    while true; do
        show_menu
        read -r choice
        
        case $choice in
            1) quick_release ;;
            2) status_check ;;
            3) 
                echo "Enter version number (without 'v'):"
                read -r version
                echo "Enter description:"
                read -r desc
                update_version_json "$version" "$desc"
                update_django_files "$version"
                create_archive "$version"
                git_operations "$version" "$desc"
                
                print_color "$GREEN" "\n✅ Version v${version} released successfully!"
                
                # Restart services to apply new version
                print_color "$YELLOW" "\n🔄 Restarting services with new version..."
                
                # Restart web core (Django backend)
                if [ -f "backend/start_backend.sh" ]; then
                    print_color "$CYAN" "   Restarting web core..."
                    ./backend/start_backend.sh restart
                    sleep 2
                    print_color "$GREEN" "   ✅ Web core restarted"
                else
                    print_color "$YELLOW" "   ⚠️  Could not find backend/start_backend.sh"
                fi
                
                # Restart CLI
                print_color "$CYAN" "   Restarting CLI..."
                print_color "$GREEN" "\n✨ Version v${version} is now active!"
                print_color "$CYAN" "   The CLI will restart automatically in 3 seconds..."
                
                sleep 3
                exec ./unibos.sh
                ;;
            4)
                highest=$(get_highest_git_version)
                update_version_json "$highest" "Version sync fix"
                print_color "$GREEN" "✅ VERSION.json synced to v${highest}"
                ;;
            5)
                version=$(get_current_version)
                create_archive "$version"
                ;;
            6) cleanup_archives ;;
            0) 
                print_color "$GREEN" "Goodbye!"
                exit 0
                ;;
            *)
                print_color "$RED" "Invalid option!"
                ;;
        esac
        
        echo -e "\n${YELLOW}Press Enter to continue...${NC}"
        read
    done
}

# Check prerequisites
if [ ! -f "unibos.sh" ]; then
    print_color "$RED" "❌ Must run from UNIBOS root directory"
    exit 1
fi

# Run main program
main