# UNIBOS SDK

The official SDK for building UNIBOS modules. This SDK provides all the tools you need to create modular, pluggable applications that integrate seamlessly with the UNIBOS platform.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Core Components](#core-components)
- [Module Manifest](#module-manifest)
- [API Reference](#api-reference)
- [Best Practices](#best-practices)
- [Examples](#examples)

## Overview

The UNIBOS SDK enables you to build modules that:

- **Plug into UNIBOS Core** - Automatic discovery and registration
- **Share resources** - Single database, shared cache, event system
- **Communicate** - Event-driven architecture for inter-module communication
- **Scale independently** - Each module can have web, mobile, and CLI interfaces
- **Maintain isolation** - Clear boundaries while enabling collaboration

## Installation

The SDK is already included in the UNIBOS monorepo. To use it in your module:

```python
from unibos_sdk import (
    UnibosModule,
    UnibosAuth,
    UnibosStorage,
    UnibosCache,
    UnibosEvents,
)
```

## Quick Start

### 1. Create Module Structure

```bash
modules/
└── my_module/
    ├── module.json          # Module manifest
    ├── backend/             # Django app
    │   ├── __init__.py
    │   ├── models.py
    │   ├── views.py
    │   ├── urls.py
    │   └── apps.py
    ├── web/                 # Optional: standalone web app
    └── mobile/              # Optional: mobile app
```

### 2. Create Module Manifest

`modules/my_module/module.json`:

```json
{
  "id": "my_module",
  "name": "My Module",
  "version": "1.0.0",
  "description": "A sample UNIBOS module",
  "icon": "🚀",
  "author": "Your Name",

  "capabilities": {
    "backend": true,
    "web": false,
    "mobile": false,
    "cli": false,
    "realtime": false
  },

  "database": {
    "uses_shared_db": true,
    "tables_prefix": "my_module_",
    "models": ["Item", "Category"]
  },

  "api": {
    "base_path": "/api/v1/my_module/",
    "endpoints": [
      {
        "path": "items/",
        "methods": ["GET", "POST"],
        "auth_required": true
      }
    ]
  },

  "integration": {
    "sidebar": {
      "enabled": true,
      "position": 10,
      "category": "general"
    }
  }
}
```

### 3. Initialize Module

`modules/my_module/backend/apps.py`:

```python
from django.apps import AppConfig
from unibos_sdk import UnibosModule

class MyModuleConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'modules.my_module.backend'
    verbose_name = 'My Module'

    def ready(self):
        # Initialize UNIBOS module
        self.module = UnibosModule('my_module')

        # Register event handlers
        from . import signals  # Import your signal handlers
```

## Core Components

### UnibosModule

Main module wrapper that provides:
- Manifest loading
- Path management
- Configuration access

```python
from unibos_sdk import UnibosModule

module = UnibosModule('my_module')

# Get paths
storage_path = module.get_storage_path()  # /data/runtime/media/modules/my_module/
cache_path = module.get_cache_path()
logs_path = module.get_logs_path()

# Access manifest
manifest = module.get_manifest()
version = module.manifest['version']
```

### UnibosAuth

Authentication and authorization helpers:

```python
from unibos_sdk import UnibosAuth

# Decorator for views
@UnibosAuth.require_authentication
def my_view(request):
    user = UnibosAuth.get_current_user(request)
    return JsonResponse({'user': user.username})

# Permission checking
@UnibosAuth.require_permission('my_module.view_item')
def view_item(request, item_id):
    # User guaranteed to have permission
    pass

# Multiple permissions
@UnibosAuth.require_all_permissions('my_module.view', 'my_module.edit')
def edit_view(request):
    pass

# Superuser only
@UnibosAuth.require_superuser
def admin_view(request):
    pass
```

### UnibosStorage

File storage using Universal Data Directory:

```python
from unibos_sdk import UnibosStorage

# Get module storage path
storage_path = UnibosStorage.get_module_storage_path('my_module', 'uploads/')

# Save file
file_path = UnibosStorage.save_file(
    module_id='my_module',
    file_obj=request.FILES['file'],
    filename='document.pdf',
    subpath='uploads/'
)

# File operations
UnibosStorage.copy_file(source, destination)
UnibosStorage.move_file(source, destination)
UnibosStorage.delete_file(file_path)

# List files
files = UnibosStorage.list_files(storage_path, pattern='*.pdf')

# Check existence
if UnibosStorage.file_exists(file_path):
    size = UnibosStorage.get_file_size(file_path)
```

### UnibosCache

Redis cache for inter-module communication:

```python
from unibos_sdk import UnibosCache

# Basic operations
UnibosCache.set('my_module', 'user_count', 150, timeout=300)
count = UnibosCache.get('my_module', 'user_count', default=0)
UnibosCache.delete('my_module', 'user_count')

# Atomic counters
UnibosCache.increment('my_module', 'page_views')
UnibosCache.decrement('my_module', 'available_slots')

# User-specific data
UnibosCache.set_user_data(user_id=123, key='preferences', value={...})
prefs = UnibosCache.get_user_data(user_id=123, key='preferences')

# Module-specific data (convenience)
UnibosCache.set_module_data('my_module', 'config', {...})
config = UnibosCache.get_module_data('my_module', 'config')
```

### UnibosEvents

Event-driven inter-module communication:

```python
from unibos_sdk import UnibosEvents, document_uploaded

# Emit event
UnibosEvents.emit_document_uploaded(
    sender=self.__class__,
    user=request.user,
    document=doc_instance,
    file_type='pdf'
)

# Listen to event
from unibos_sdk import event_handler, earthquake_detected

@event_handler(earthquake_detected)
def handle_earthquake(sender, earthquake, magnitude, location, **kwargs):
    if magnitude >= 5.0:
        # Send notifications
        notify_users_in_area(location)
```

#### Available Events

- `earthquake_detected` - Emergency events (birlikteyiz)
- `user_location_changed` - Location updates
- `payment_completed` - Financial transactions
- `document_uploaded` - Document management
- `currency_rate_updated` - Currency rate changes
- `user_registered` - New user registration
- `module_enabled` - Module activation
- `module_disabled` - Module deactivation

## Module Manifest

The `module.json` file defines your module's metadata and configuration.

### Required Fields

```json
{
  "id": "my_module",           // snake_case, lowercase only
  "name": "My Module",         // Human-readable name
  "version": "1.0.0",          // Semantic versioning
  "description": "Module description (10-200 chars)",
  "icon": "🚀"                 // Emoji icon
}
```

### Optional Fields

#### Capabilities

```json
{
  "capabilities": {
    "backend": true,          // Has Django backend
    "web": false,             // Has standalone web app
    "mobile": false,          // Has mobile app
    "cli": false,             // Has CLI interface
    "realtime": false         // Uses WebSocket features
  }
}
```

#### Dependencies

```json
{
  "dependencies": {
    "core_modules": ["authentication", "users"],
    "other_modules": ["currencies"],
    "python_packages": ["pandas>=1.0.0", "requests"],
    "system_requirements": ["redis", "postgresql", "celery"]
  }
}
```

#### Database

```json
{
  "database": {
    "uses_shared_db": true,
    "tables_prefix": "my_module_",  // Must end with _
    "models": ["Item", "Category"]
  }
}
```

#### API

```json
{
  "api": {
    "base_path": "/api/v1/my_module/",
    "endpoints": [
      {
        "path": "items/",
        "methods": ["GET", "POST"],
        "public": false,
        "auth_required": true
      }
    ]
  }
}
```

#### Integration

```json
{
  "integration": {
    "sidebar": {
      "enabled": true,
      "position": 10,        // Lower = higher in sidebar
      "category": "general"  // general|finance|content|security|tools
    },
    "dashboard_widgets": [
      {
        "id": "my_widget",
        "title": "My Widget",
        "size": "medium"     // small|medium|large
      }
    ]
  }
}
```

## API Reference

### UnibosModule

```python
class UnibosModule:
    def __init__(self, module_id: str)
    def get_manifest(self) -> Dict
    def get_storage_path(self, subpath: str = '') -> Path
    def get_cache_path(self, subpath: str = '') -> Path
    def get_logs_path(self, subpath: str = '') -> Path
```

### UnibosAuth

```python
class UnibosAuth:
    @staticmethod
    def get_current_user(request)

    @staticmethod
    def check_permission(user, permission: str) -> bool

    @staticmethod
    def require_authentication(func)

    @staticmethod
    def require_permission(permission: str)

    @staticmethod
    def require_superuser(func)
```

### UnibosStorage

```python
class UnibosStorage:
    @staticmethod
    def get_module_storage_path(module_id: str, subpath: str = '') -> Path

    @staticmethod
    def save_file(module_id: str, file_obj: BinaryIO,
                  filename: str, subpath: str = '') -> Path

    @staticmethod
    def delete_file(file_path: Path) -> bool

    @staticmethod
    def file_exists(file_path: Path) -> bool

    @staticmethod
    def list_files(dir_path: Path, pattern: str = '*') -> list
```

### UnibosCache

```python
class UnibosCache:
    @staticmethod
    def set(namespace: str, key: str, value: Any, timeout: Optional[int] = None) -> bool

    @staticmethod
    def get(namespace: str, key: str, default: Any = None) -> Any

    @staticmethod
    def delete(namespace: str, key: str) -> bool

    @staticmethod
    def increment(namespace: str, key: str, delta: int = 1) -> Optional[int]
```

### UnibosEvents

```python
class UnibosEvents:
    @staticmethod
    def emit(signal: Signal, sender: Any = None, **kwargs)

    @staticmethod
    def listen(signal: Signal, handler: Callable)

    @staticmethod
    def emit_document_uploaded(sender, user, document, file_type: str)
```

## Best Practices

### 1. Module Naming

- Use lowercase snake_case for module IDs
- Use descriptive, unique names
- Follow pattern: `{domain}_{function}` (e.g., `finance_reports`, `user_analytics`)

### 2. Database Tables

- Always use table prefix from manifest
- Keep prefix format: `{module_id}_` (must end with underscore)
- Example: `birlikteyiz_earthquake`, `currencies_rate`

### 3. File Storage

- Always use `UnibosStorage` helpers
- Never hardcode paths
- Use subpaths for organization: `uploads/`, `exports/`, `temp/`

### 4. Caching

- Use module_id as namespace
- Set appropriate timeouts
- Use atomic operations (increment/decrement) for counters

### 5. Events

- Emit events for significant actions
- Use descriptive event names
- Include all relevant context in event data
- Handle events asynchronously when possible

### 6. Error Handling

```python
from django.core.exceptions import ValidationError
from rest_framework.exceptions import APIException

try:
    UnibosStorage.save_file(...)
except Exception as e:
    logger.error(f"Failed to save file: {e}")
    raise APIException("File upload failed")
```

## Examples

### Complete Module Example

```python
# modules/my_module/backend/models.py
from django.db import models

class Item(models.Model):
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'my_module_item'  # Use prefix!

# modules/my_module/backend/views.py
from django.http import JsonResponse
from unibos_sdk import UnibosAuth, UnibosCache, UnibosEvents
from .models import Item

@UnibosAuth.require_permission('my_module.view_item')
def list_items(request):
    # Check cache first
    cached_items = UnibosCache.get('my_module', 'items_list')
    if cached_items:
        return JsonResponse({'items': cached_items})

    # Query database
    items = list(Item.objects.values())

    # Cache results
    UnibosCache.set('my_module', 'items_list', items, timeout=300)

    return JsonResponse({'items': items})

@UnibosAuth.require_authentication
def create_item(request):
    item = Item.objects.create(name=request.POST['name'])

    # Emit event
    UnibosEvents.emit(
        signal=item_created,
        sender=Item,
        item=item,
        user=request.user
    )

    # Invalidate cache
    UnibosCache.delete('my_module', 'items_list')

    return JsonResponse({'id': item.id, 'name': item.name})
```

### Event Handling Example

```python
# modules/notification/backend/signals.py
from unibos_sdk import event_handler, document_uploaded
from .tasks import send_notification

@event_handler(document_uploaded)
def notify_on_document_upload(sender, user, document, file_type, **kwargs):
    """Notify admins when important documents are uploaded"""
    if file_type in ['pdf', 'docx']:
        send_notification.delay(
            title=f"New {file_type} uploaded",
            message=f"{user.username} uploaded {document.name}",
            recipients=['admin@example.com']
        )
```

### Cross-Module Communication

```python
# Module A emits event
from unibos_sdk import UnibosEvents
from django.dispatch import Signal

payment_processed = Signal()

UnibosEvents.emit(
    payment_processed,
    sender=self.__class__,
    user=user,
    amount=100.50,
    currency='USD'
)

# Module B listens
from unibos_sdk import event_handler

@event_handler(payment_processed)
def update_user_balance(sender, user, amount, currency, **kwargs):
    # Update user's balance in this module
    UserBalance.objects.filter(user=user).update(
        balance=F('balance') + amount
    )
```

## Support

For questions and issues:
- Check the [UNIBOS Documentation](../../docs/)
- Review existing modules in [modules/](../../modules/)
- Contact: berk@berkhatirli.com

## License

Part of the UNIBOS platform.
© 2024 Berk Hatırlı
