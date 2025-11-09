# Module Migration Guide

Complete guide for migrating existing Django apps to UNIBOS modular architecture.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Migration Steps](#migration-steps)
- [Module Structure](#module-structure)
- [Apps.py Integration](#appspy-integration)
- [Testing](#testing)
- [Rollback](#rollback)

## Prerequisites

Before migrating a module, ensure:

1. **UNIBOS SDK is installed**: `shared/python/unibos_sdk/` directory exists
2. **ModuleRegistry is configured**: `core/backend/core_apps/module_registry/` is in INSTALLED_APPS
3. **Database backup**: Always backup before migration
4. **Clean git state**: Commit current work first

## Migration Steps

### Step 1: Create Module Directory

Create the new module structure in `modules/`:

```bash
mkdir -p modules/{module_id}/backend
mkdir -p modules/{module_id}/mobile  # Optional
mkdir -p modules/{module_id}/web      # Optional
```

### Step 2: Copy Backend Code

Copy the existing Django app to the module:

```bash
# From apps/web/backend/apps/{module_name}/ → modules/{module_id}/backend/
cp -r apps/web/backend/apps/{module_name}/* modules/{module_id}/backend/
```

**Important**: Preserve all files:
- models.py
- views.py
- serializers.py
- urls.py
- admin.py
- signals.py
- tasks.py (Celery)
- consumers.py (Channels, if any)
- services/ (service layer)
- migrations/

### Step 3: Create module.json Manifest

Create `modules/{module_id}/module.json`:

```json
{
  "id": "module_id",
  "name": "Module Name",
  "display_name": {
    "tr": "Turkish Name",
    "en": "English Name"
  },
  "version": "1.0.0",
  "description": "Module description (10-200 chars)",
  "icon": "📦",
  "author": "Your Name",

  "capabilities": {
    "backend": true,
    "web": false,
    "mobile": false,
    "cli": false,
    "realtime": false
  },

  "dependencies": {
    "core_modules": ["authentication", "users"],
    "python_packages": [
      "djangorestframework",
      "celery"
    ],
    "system_requirements": ["redis", "postgresql"]
  },

  "database": {
    "uses_shared_db": true,
    "tables_prefix": "module_id_",
    "models": ["Model1", "Model2"]
  },

  "api": {
    "base_path": "/api/v1/module_id/",
    "endpoints": [
      {
        "path": "items/",
        "methods": ["GET", "POST"],
        "public": false,
        "auth_required": true
      }
    ]
  },

  "permissions": [
    "module_id.view_item",
    "module_id.add_item"
  ],

  "celery_tasks": [
    "process_items",
    "send_notifications"
  ],

  "integration": {
    "sidebar": {
      "enabled": true,
      "position": 10,
      "category": "general"
    },
    "dashboard_widgets": [
      {
        "id": "widget_id",
        "title": "Widget Title",
        "size": "medium"
      }
    ]
  },

  "development": {
    "repository": "https://github.com/berkhatira/unibos",
    "documentation": "",
    "maintainer": "your@email.com"
  }
}
```

**Key Fields**:

- `id`: Lowercase snake_case, must match directory name
- `tables_prefix`: Must end with underscore (`_`)
- `models`: List all Django model class names
- `category`: One of: general, finance, content, security, tools

### Step 4: Update apps.py

Modify `modules/{module_id}/backend/apps.py`:

```python
"""
Module Name Django App Configuration

UNIBOS Module Integration
"""

from django.apps import AppConfig
from pathlib import Path
import sys


class ModuleNameConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'modules.{module_id}.backend'
    verbose_name = 'Module Name'

    def ready(self):
        """
        Initialize UNIBOS module and register signals
        """
        # Add shared SDK to Python path
        self._add_sdk_to_path()

        # Initialize UNIBOS module
        self._initialize_module()

        # Import and register signals
        from . import signals  # noqa

    def _add_sdk_to_path(self):
        """Add UNIBOS SDK to Python path if not already there"""
        try:
            # Get project root (from modules/{module_id}/backend -> go up 3 levels)
            module_dir = Path(__file__).resolve().parent.parent.parent.parent
            sdk_path = module_dir / 'shared' / 'python'

            if sdk_path.exists() and str(sdk_path) not in sys.path:
                sys.path.insert(0, str(sdk_path))
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Could not add SDK to path: {e}")

    def _initialize_module(self):
        """Initialize UNIBOS module wrapper"""
        try:
            from unibos_sdk import UnibosModule

            # Initialize module
            self.unibos_module = UnibosModule('{module_id}')

            # Log initialization
            import logging
            logger = logging.getLogger(__name__)
            logger.info(
                f"✓ Initialized UNIBOS module: {module_id} "
                f"v{self.unibos_module.manifest.get('version')}"
            )

            # Ensure storage paths exist
            self.unibos_module.get_storage_path('uploads/')
            self.unibos_module.get_cache_path()
            self.unibos_module.get_logs_path()

        except ImportError as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"UNIBOS SDK not available, running in legacy mode: {e}")
```

**Important Changes**:
- Update `name` from `apps.{module_name}` to `modules.{module_id}.backend`
- Add SDK path management
- Initialize UnibosModule instance
- Import signals with relative import (`from . import signals`)

### Step 5: Update Django Settings

Add the module to `INSTALLED_APPS` in `apps/web/backend/unibos_backend/settings/base.py`:

```python
INSTALLED_APPS = [
    # ...existing apps...

    # UNIBOS Core
    'core.backend.core_apps.module_registry',

    # UNIBOS Modules
    'modules.birlikteyiz.backend',
    'modules.{module_id}.backend',  # Add your module here
]
```

### Step 6: Sync Module Registry

Run management command to discover and register the module:

```bash
cd apps/web/backend
python manage.py modules sync
```

Expected output:
```
Syncing modules from disk...
✓ Discovered module: {module_id} v1.0.0
✓ Successfully synced 2 modules
```

### Step 7: Verify Module

List all modules:

```bash
python manage.py modules list
```

Check module info:

```bash
python manage.py modules info {module_id}
```

### Step 8: Test Module

1. **Start Django server**:
   ```bash
   python manage.py runserver
   ```

2. **Check logs** for initialization message:
   ```
   ✓ Initialized UNIBOS module: {module_id} v1.0.0
   ```

3. **Test API endpoints**:
   ```bash
   curl http://localhost:8000/api/v1/{module_id}/items/
   ```

4. **Check Django admin**: Module should appear with status badges

## Module Structure

Final structure should look like:

```
modules/{module_id}/
├── module.json              # Module manifest
├── backend/                 # Django app
│   ├── __init__.py
│   ├── apps.py             # Updated with SDK integration
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   ├── urls.py
│   ├── admin.py
│   ├── signals.py
│   ├── tasks.py            # Celery tasks
│   ├── consumers.py        # WebSocket consumers (optional)
│   ├── services/           # Service layer (optional)
│   │   ├── __init__.py
│   │   └── item_service.py
│   └── migrations/
│       ├── __init__.py
│       └── 0001_initial.py
├── web/                    # Optional: standalone web app
│   ├── index.html
│   └── ...
└── mobile/                 # Optional: mobile app
    ├── pubspec.yaml
    ├── lib/
    └── ...
```

## Apps.py Integration

The updated `apps.py` provides:

1. **SDK Path Management**: Automatically adds `shared/python/` to Python path
2. **Module Initialization**: Creates UnibosModule instance
3. **Storage Paths**: Ensures module-specific directories exist
4. **Graceful Degradation**: Falls back to legacy mode if SDK unavailable
5. **Signal Registration**: Imports and registers Django signals

## Testing

### Test Checklist

- [ ] Module appears in `python manage.py modules list`
- [ ] Module status shows ENABLED
- [ ] Django server starts without errors
- [ ] Initialization log appears: `✓ Initialized UNIBOS module: {module_id}`
- [ ] API endpoints respond correctly
- [ ] Database queries work (models accessible)
- [ ] Admin interface shows module
- [ ] Signals fire correctly
- [ ] Celery tasks execute (if applicable)
- [ ] WebSocket connections work (if applicable)

### Manual Testing

1. **Import module in shell**:
   ```bash
   python manage.py shell
   ```
   ```python
   from modules.{module_id}.backend.models import Item
   Item.objects.all()
   ```

2. **Check SDK integration**:
   ```python
   from unibos_sdk import UnibosModule
   module = UnibosModule('{module_id}')
   print(module.manifest)
   print(module.get_storage_path())
   ```

3. **Test caching**:
   ```python
   from unibos_sdk import UnibosCache
   UnibosCache.set('{module_id}', 'test', 'value')
   print(UnibosCache.get('{module_id}', 'test'))
   ```

## Rollback

If migration fails, rollback steps:

1. **Remove from INSTALLED_APPS**:
   ```python
   # Comment out or remove
   # 'modules.{module_id}.backend',
   ```

2. **Restore original app** (if you kept backup):
   ```bash
   # Original is still at apps/web/backend/apps/{module_name}/
   # Just keep using it
   ```

3. **Restart Django server**:
   ```bash
   python manage.py runserver
   ```

## Common Issues

### Issue: ModuleNotFoundError: No module named 'unibos_sdk'

**Solution**: SDK path not added correctly. Check `_add_sdk_to_path()` method.

```python
# Verify path calculation
module_dir = Path(__file__).resolve().parent.parent.parent.parent
sdk_path = module_dir / 'shared' / 'python'
print(f"SDK path: {sdk_path}")
print(f"Exists: {sdk_path.exists()}")
```

### Issue: Module not appearing in modules list

**Solution**: Run sync command:
```bash
python manage.py modules sync
```

Check `module.json` is valid JSON and has required fields.

### Issue: Table names incorrect

**Solution**: Ensure `tables_prefix` in `module.json` matches model `Meta.db_table`.

Example:
```python
# module.json
"tables_prefix": "documents_"

# models.py
class Document(models.Model):
    class Meta:
        db_table = 'documents_document'  # Prefix matches!
```

### Issue: Signals not firing

**Solution**: Check import in `apps.py`:
```python
def ready(self):
    from . import signals  # Must use relative import
```

## Best Practices

1. **Gradual Migration**: Migrate one module at a time
2. **Keep Backups**: Don't delete original code until fully tested
3. **Database First**: Ensure table prefixes are correct before migration
4. **Test Thoroughly**: Check all endpoints, signals, tasks
5. **Document Changes**: Update module README if needed
6. **Version Bump**: Increment version in `module.json` after migration

## Example: Birlikteyiz Migration

The `birlikteyiz` module is the reference implementation. Study it for:

- Complete `module.json` with all fields
- Proper `apps.py` SDK integration
- Signal registration
- Celery task configuration
- WebSocket consumer setup
- Multi-capability module (backend + mobile)

Location: `modules/birlikteyiz/`

## Next Steps

After successful migration:

1. Update module documentation
2. Add module to sidebar navigation (check `integration.sidebar` in manifest)
3. Create dashboard widgets if needed
4. Set up inter-module communication (events, cache)
5. Migrate next module

## Support

Questions or issues? Check:
- [UNIBOS SDK README](../../shared/python/unibos_sdk/README.md)
- [ROADMAP.md](../../ROADMAP.md)
- Existing modules in `modules/` directory

Contact: berk@berkhatirli.com
