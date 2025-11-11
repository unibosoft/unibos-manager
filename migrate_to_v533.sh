#!/bin/bash
# UNIBOS v533 Migration Script
# Migrates from v532 modular structure to v533 core-based architecture

set -e  # Exit on error

echo "====================================="
echo "UNIBOS v533 Migration Script"
echo "====================================="
echo ""

# Check if we're in the right directory
if [ ! -d "modules" ] || [ ! -d "platform" ]; then
    echo "Error: This script must be run from the UNIBOS root directory"
    exit 1
fi

echo "Step 1: Creating core directory structure..."
mkdir -p core/backend
mkdir -p core/models
mkdir -p core/system
mkdir -p core/instance
mkdir -p core/p2p
mkdir -p core/sync
mkdir -p core/services
mkdir -p core/sdk

echo "Step 2: Moving platform/runtime/web/backend to core/backend..."
if [ -d "platform/runtime/web/backend" ]; then
    rsync -av platform/runtime/web/backend/ core/backend/
    echo "✓ Django backend moved to core/backend/"
else
    echo "Warning: platform/runtime/web/backend not found"
fi

echo "Step 3: Moving platform/sdk to core/sdk..."
if [ -d "platform/sdk" ]; then
    rsync -av platform/sdk/ core/sdk/
    echo "✓ SDK moved to core/sdk/"
fi

echo "Step 4: Extracting models from modules/core to core/models..."
if [ -f "modules/core/backend/models.py" ]; then
    cp modules/core/backend/models.py core/models/base.py
    echo "✓ Core models extracted to core/models/base.py"
fi

echo "Step 5: Moving system modules to core/system..."
SYSTEM_MODULES=("authentication" "users" "web_ui" "common" "administration" "logging" "version_manager")

for module in "${SYSTEM_MODULES[@]}"; do
    if [ -d "modules/$module" ]; then
        echo "  Moving modules/$module to core/system/$module..."
        mv "modules/$module" "core/system/$module"
    fi
done

echo "✓ System modules moved to core/system/"

echo "Step 6: Removing old modules/core directory..."
if [ -d "modules/core" ]; then
    rm -rf "modules/core"
    echo "✓ modules/core removed"
fi

echo "Step 7: Creating P2P infrastructure placeholder files..."

# core/instance/identity.py
cat > core/instance/identity.py << 'EOF'
"""
Instance Identity Management
Each UNIBOS instance has a unique UUID
"""
import uuid
from django.conf import settings

class InstanceIdentity:
    """Unique identity for this UNIBOS instance"""

    def __init__(self):
        self.uuid = self._get_or_create_uuid()
        self.instance_type = getattr(settings, 'INSTANCE_TYPE', 'personal')

    def _get_or_create_uuid(self):
        # TODO: Load from database or create new
        return uuid.uuid4()
EOF

# core/instance/__init__.py
cat > core/instance/__init__.py << 'EOF'
from .identity import InstanceIdentity

__all__ = ['InstanceIdentity']
EOF

# core/p2p/__init__.py
touch core/p2p/__init__.py

# core/sync/__init__.py
touch core/sync/__init__.py

# core/services/__init__.py
touch core/services/__init__.py

echo "✓ P2P infrastructure placeholders created"

echo "Step 8: Creating core/models/__init__.py..."
cat > core/models/__init__.py << 'EOF'
"""
Core Domain Models (Essentials)
Shared models used across all modules
"""
from .base import BaseModel, ItemCategory, Unit, Item, ItemPrice, Account, UserProfile

__all__ = [
    'BaseModel',
    'ItemCategory',
    'Unit',
    'Item',
    'ItemPrice',
    'Account',
    'UserProfile',
]
EOF

echo "✓ core/models/__init__.py created"

echo ""
echo "====================================="
echo "Migration Complete!"
echo "====================================="
echo ""
echo "Next steps:"
echo "1. Update import paths in all modules"
echo "2. Configure PostgreSQL settings"
echo "3. Run database migrations"
echo "4. Test the application"
echo ""
echo "New structure:"
echo "  core/"
echo "    ├── backend/       (Django application)"
echo "    ├── models/        (Shared domain models)"
echo "    ├── system/        (System modules)"
echo "    ├── instance/      (P2P identity)"
echo "    ├── p2p/           (P2P communication)"
echo "    ├── sync/          (Sync engine)"
echo "    ├── services/      (Core services)"
echo "    └── sdk/           (Development SDK)"
echo "  modules/"
echo "    ├── currencies/"
echo "    ├── wimm/"
echo "    ├── wims/"
echo "    └── ... (business modules)"
echo ""
