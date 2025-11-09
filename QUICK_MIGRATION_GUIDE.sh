#!/bin/bash
# UNIBOS Module Migration Quick Reference Script
# This script demonstrates the migration process for each module

# Configuration
PROJECT_ROOT="/Users/berkhatirli/Desktop/unibos"
OLD_APPS="$PROJECT_ROOT/apps/web/backend/apps"
NEW_MODULES="$PROJECT_ROOT/modules"

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to migrate a single module
migrate_module() {
    local module_name=$1
    local module_id=$2  # Can be same as module_name

    echo -e "${YELLOW}=== Migrating ${module_name} ===${NC}"

    # Step 1: Analyze module
    echo "Step 1: Analyzing module..."
    echo "  Models:"
    grep "^class.*models.Model" "$OLD_APPS/$module_name/models.py" 2>/dev/null | sed 's/class /    - /' | sed 's/(.*$//'

    echo "  Files:"
    ls -1 "$OLD_APPS/$module_name/" 2>/dev/null | grep -v __pycache__ | sed 's/^/    - /'

    # Step 2: Create directory structure
    echo -e "\nStep 2: Creating module structure..."
    mkdir -p "$NEW_MODULES/$module_id/backend"

    # Step 3: Copy files
    echo "Step 3: Copying files..."
    cp -r "$OLD_APPS/$module_name/"* "$NEW_MODULES/$module_id/backend/" 2>/dev/null

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Files copied successfully${NC}"
    else
        echo -e "${RED}✗ Error copying files${NC}"
        return 1
    fi

    # Step 4: Create module.json (placeholder - needs manual editing)
    echo "Step 4: Creating module.json template..."
    cat > "$NEW_MODULES/$module_id/module.json" <<EOF
{
  "id": "$module_id",
  "name": "$(echo $module_name | sed 's/_/ /g' | awk '{for(i=1;i<=NF;i++)sub(/./,toupper(substr($i,1,1)),$i)}1')",
  "display_name": {
    "tr": "TODO",
    "en": "TODO"
  },
  "version": "1.0.0",
  "description": "TODO: Add description",
  "icon": "📦",
  "author": "Berk Hatırlı",

  "capabilities": {
    "backend": true,
    "web": true,
    "mobile": false,
    "cli": false,
    "realtime": false
  },

  "dependencies": {
    "core_modules": ["authentication", "users"],
    "python_packages": ["djangorestframework"],
    "system_requirements": ["postgresql"]
  },

  "database": {
    "uses_shared_db": true,
    "tables_prefix": "${module_id}_",
    "models": []
  },

  "api": {
    "base_path": "/api/v1/$module_id/",
    "endpoints": []
  },

  "permissions": [],
  "celery_tasks": [],
  "features": [],

  "integration": {
    "sidebar": {
      "enabled": true,
      "position": 10,
      "category": "tools"
    }
  },

  "development": {
    "repository": "https://github.com/berkhatira/unibos",
    "documentation": "",
    "maintainer": "berk@berkhatirli.com"
  }
}
EOF

    echo -e "${YELLOW}⚠ module.json created - REQUIRES MANUAL EDITING${NC}"
    echo -e "${YELLOW}⚠ apps.py REQUIRES MANUAL EDITING${NC}"
    echo -e "${YELLOW}⚠ settings/base.py REQUIRES MANUAL UPDATE${NC}"

    echo -e "${GREEN}=== Module $module_name migration prepared ===${NC}\n"
}

# Main migration function
main() {
    echo -e "${GREEN}UNIBOS Module Migration Tool${NC}"
    echo "========================================"
    echo ""

    # Check if project root exists
    if [ ! -d "$PROJECT_ROOT" ]; then
        echo -e "${RED}Error: Project root not found at $PROJECT_ROOT${NC}"
        exit 1
    fi

    # List of modules to migrate (excluding already migrated ones)
    modules=(
        "personal_inflation:personal_inflation"
        "recaria:recaria"
        "cctv:cctv"
        "movies:movies"
        "music:music"
        "restopos:restopos"
        "wimm:wimm"
        "wims:wims"
        "solitaire:solitaire"
        "version_manager:version_manager"
        "administration:administration"
        "logging:logging"
    )

    # Migrate each module
    for module_spec in "${modules[@]}"; do
        IFS=':' read -r module_name module_id <<< "$module_spec"
        migrate_module "$module_name" "$module_id"
    done

    echo -e "${GREEN}=== Migration preparation complete ===${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Review and edit each module.json file"
    echo "2. Update each apps.py file with SDK integration"
    echo "3. Update settings/base.py:"
    echo "   - Add modules to UNIBOS_MODULES"
    echo "   - Comment out from LOCAL_APPS"
    echo "4. Run migrations: python manage.py makemigrations && python manage.py migrate"
    echo "5. Test each module"
}

# Run if executed directly
if [ "$1" == "run" ]; then
    main
else
    echo "This is a reference script showing the migration process."
    echo "To actually run migrations, execute: $0 run"
    echo ""
    echo "Or migrate individual modules:"
    echo "  migrate_module <module_name> <module_id>"
fi
