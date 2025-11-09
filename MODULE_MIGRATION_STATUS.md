# UNIBOS Module Migration Status

## Migration Progress: 2/13 Complete (15%)

### Completed Migrations ✅

#### 1. **currencies** - COMPLETED
- **Models**: 12 models (Currency, ExchangeRate, CurrencyAlert, Portfolio, PortfolioHolding, PortfolioTransaction, PortfolioPerformance, Transaction, MarketData, CryptoExchangeRate, BankExchangeRate, BankRateImportLog)
- **API Endpoints**: 27 endpoints
- **Celery Tasks**: 7 tasks (update_exchange_rates, check_currency_alerts, update_portfolio_performance, fetch_crypto_prices, import_bank_rates, cleanup_old_rates, calculate_technical_indicators)
- **WebSocket Routes**: 3 routes (ws/currencies/rates/, ws/currencies/alerts/, ws/currencies/portfolio/)
- **Key Features**: Real-time currency tracking, portfolio management, cryptocurrency analytics, bank rate comparison, technical indicators
- **Location**: `/Users/berkhatirli/Desktop/unibos/modules/currencies/`
- **Settings**: Added to UNIBOS_MODULES, removed from LOCAL_APPS

#### 2. **birlikteyiz** - COMPLETED (Reference Implementation)
- Already migrated
- Emergency mesh network and earthquake monitoring

#### 3. **documents** - COMPLETED
- Already migrated
- OCR and document management

### In Progress 🔄

#### 2. **personal_inflation** - 80% COMPLETE
- **Models**: 8 models (ProductCategory, Product, Store, PersonalBasket, BasketItem, PriceRecord, InflationReport, PriceAlert)
- **API Endpoints**: 4+ endpoints
- **Celery Tasks**: 2 tasks (check_price_alerts, generate_monthly_reports)
- **Key Features**: Personal basket tracking, inflation calculation, price alerts
- **Location**: `/Users/berkhatirli/Desktop/unibos/modules/personal_inflation/`
- **Status**: module.json created, backend files copied
- **TODO**: Update apps.py, add to settings

### Pending Migrations ⏳

#### 3. recaria
- **Estimated Complexity**: Low
- **Dependencies**: Core modules only
- **Notes**: Simple module structure

#### 4. cctv
- **Estimated Complexity**: Medium
- **Dependencies**: Core modules
- **Key Features**: Camera monitoring, motion detection

#### 5. movies
- **Estimated Complexity**: Medium
- **Dependencies**: Core modules
- **Key Features**: Movie/series collection management

#### 6. music
- **Estimated Complexity**: Medium
- **Dependencies**: Core modules
- **Key Features**: Music collection, Spotify integration

#### 7. restopos
- **Estimated Complexity**: High
- **Dependencies**: Core modules
- **Key Features**: Restaurant POS system

#### 8. wimm (Where Is My Money)
- **Estimated Complexity**: High
- **Dependencies**: currencies
- **Key Features**: Personal finance tracking

#### 9. wims (Where Is My Stuff)
- **Estimated Complexity**: Medium
- **Dependencies**: Core modules
- **Key Features**: Inventory management

#### 10. solitaire
- **Estimated Complexity**: Low
- **Dependencies**: Core modules
- **Key Features**: Solitaire game with session tracking

#### 11. version_manager
- **Estimated Complexity**: Low
- **Dependencies**: Core modules
- **Key Features**: Version archive management

#### 12. administration
- **Estimated Complexity**: Medium
- **Dependencies**: Core modules, users, authentication
- **Key Features**: User/role management

#### 13. logging
- **Estimated Complexity**: Low
- **Dependencies**: Core modules
- **Key Features**: System and activity logging

## Migration Process (Standard Pattern)

For each module, follow these exact steps:

### Step 1: Analyze Module
```bash
# Check models
cat apps/web/backend/apps/{module}/models.py

# Check views/API
cat apps/web/backend/apps/{module}/views.py
cat apps/web/backend/apps/{module}/api_views.py  # if exists

# Check URLs
cat apps/web/backend/apps/{module}/urls.py

# List all files
ls -la apps/web/backend/apps/{module}/

# Check for Celery tasks
grep -l "@shared_task\|@task" apps/web/backend/apps/{module}/*.py

# Check for WebSocket consumers
grep -l "Consumer\|AsyncConsumer" apps/web/backend/apps/{module}/*.py
```

### Step 2: Create Module Structure
```bash
# Create directory
mkdir -p modules/{module_id}/backend

# Copy all files
cp -r apps/web/backend/apps/{module}/* modules/{module_id}/backend/
```

### Step 3: Create module.json
Use this template (adjust for each module):

```json
{
  "id": "{module_id}",
  "name": "{Module Name}",
  "display_name": {
    "tr": "{Turkish Name}",
    "en": "{English Name}"
  },
  "version": "1.0.0",
  "description": "{Description}",
  "icon": "{emoji}",
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
    "tables_prefix": "{module_}_",
    "models": [
      "Model1",
      "Model2"
    ]
  },

  "api": {
    "base_path": "/api/v1/{module}/",
    "endpoints": [
      {
        "path": "resource/",
        "methods": ["GET", "POST"],
        "public": false,
        "auth_required": true,
        "description": "Description"
      }
    ]
  },

  "permissions": [
    "{module}.view_model",
    "{module}.add_model"
  ],

  "celery_tasks": [
    "task_name"
  ],

  "channels": {
    "websocket_routes": [
      "ws/{module}/resource/"
    ]
  },

  "features": [
    "Feature 1",
    "Feature 2"
  ],

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
```

### Step 4: Update apps.py
Replace the existing apps.py with this pattern:

```python
"""
{Module Name} Django App Configuration
{Description}

UNIBOS Module Integration
"""

from django.apps import AppConfig
from pathlib import Path
import sys


class {ModuleName}Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'modules.{module_id}.backend'
    verbose_name = '{Module Display Name}'

    def ready(self):
        """
        Initialize UNIBOS module and register signals
        """
        # Add shared SDK to Python path
        self._add_sdk_to_path()

        # Initialize UNIBOS module
        self._initialize_module()

        # Import and register signals (if any)
        # from . import signals  # noqa

    def _add_sdk_to_path(self):
        """Add UNIBOS SDK to Python path if not already there"""
        try:
            # Get project root (from modules/{module}/backend -> go up 3 levels)
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
            logger.info(f"✓ Initialized UNIBOS module: {module_id} v{self.unibos_module.manifest.get('version')}")

            # Ensure storage paths exist
            self.unibos_module.get_storage_path('uploads/')
            self.unibos_module.get_cache_path()
            self.unibos_module.get_logs_path()

        except ImportError as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"UNIBOS SDK not available, running in legacy mode: {e}")
```

### Step 5: Update settings/base.py
```python
# Add to UNIBOS_MODULES
UNIBOS_MODULES = [
    'modules.birlikteyiz.backend',
    'modules.documents.backend',
    'modules.currencies.backend',
    'modules.{module_id}.backend',  # Add this line
]

# Comment out from LOCAL_APPS
LOCAL_APPS = [
    # 'apps.{module}',  # MIGRATED to modules/{module_id}/
]
```

## Critical Requirements Checklist

For EACH module, ensure:

- [ ] All models are listed in module.json
- [ ] All API endpoints are documented
- [ ] All Celery tasks are listed
- [ ] All WebSocket routes are listed (if any)
- [ ] All features are described
- [ ] Dependencies are correctly specified
- [ ] apps.py follows the standard pattern
- [ ] Module is added to UNIBOS_MODULES in settings
- [ ] Old app is commented out in LOCAL_APPS

## Commands to Speed Up Migration

```bash
# Count models in a module
grep "^class.*models.Model" apps/web/backend/apps/{module}/models.py | wc -l

# List all models
grep "^class.*models.Model" apps/web/backend/apps/{module}/models.py

# Find Celery tasks
grep "@shared_task\|@task" apps/web/backend/apps/{module}/*.py -A 1

# Find WebSocket consumers
grep "class.*Consumer" apps/web/backend/apps/{module}/*.py

# Count API endpoints (in urls.py)
grep "path\|url" apps/web/backend/apps/{module}/urls.py | wc -l
```

## Module-Specific Notes

### currencies ✅
- Has 12 models
- 27 API endpoints
- 7 Celery tasks
- 3 WebSocket routes
- Depends on no other custom modules
- Very complex module with real-time features

### personal_inflation 🔄
- Has 8 models
- Depends on currencies module
- Simpler than currencies but still substantial
- Has price alert system

### wimm ⏳
- Will depend on currencies module
- Financial tracking module
- Should be migrated after currencies and personal_inflation

## Next Steps

1. Complete personal_inflation migration:
   - Update apps.py
   - Add to settings.py
   - Test migration

2. Migrate remaining modules in order:
   - recaria
   - cctv
   - movies
   - music
   - restopos
   - wimm (requires currencies)
   - wims
   - solitaire
   - version_manager
   - administration
   - logging

3. Test each migration:
   - Run migrations
   - Check API endpoints
   - Verify WebSocket connections (if any)
   - Test Celery tasks (if any)

## File Locations

- **Source**: `/Users/berkhatirli/Desktop/unibos/apps/web/backend/apps/`
- **Destination**: `/Users/berkhatirli/Desktop/unibos/modules/`
- **Settings**: `/Users/berkhatirli/Desktop/unibos/apps/web/backend/unibos_backend/settings/base.py`

## Progress Tracking

| Module | Status | Models | Endpoints | Tasks | WebSockets | Complexity |
|--------|--------|--------|-----------|-------|------------|------------|
| currencies | ✅ | 12 | 27 | 7 | 3 | High |
| personal_inflation | 🔄 | 8 | 4+ | 2 | 0 | Medium |
| recaria | ⏳ | ? | ? | ? | ? | Low |
| cctv | ⏳ | ? | ? | ? | ? | Medium |
| movies | ⏳ | ? | ? | ? | ? | Medium |
| music | ⏳ | ? | ? | ? | ? | Medium |
| restopos | ⏳ | ? | ? | ? | ? | High |
| wimm | ⏳ | ? | ? | ? | ? | High |
| wims | ⏳ | ? | ? | ? | ? | Medium |
| solitaire | ⏳ | ? | ? | ? | ? | Low |
| version_manager | ⏳ | ? | ? | ? | ? | Low |
| administration | ⏳ | ? | ? | ? | ? | Medium |
| logging | ⏳ | ? | ? | ? | ? | Low |

---
**Last Updated**: 2025-11-09
**Migrated by**: Claude (Sonnet 4.5)
