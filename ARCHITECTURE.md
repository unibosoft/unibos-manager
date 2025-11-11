# UNIBOS v533 Architecture

**Version:** 533
**Last Updated:** 2025-11-11
**Status:** Active Development

## Overview

UNIBOS v533 introduces a **core-based architecture** that establishes a clean separation between system infrastructure and business modules, enabling true modularity, P2P synchronization, and multi-platform support.

## Architecture Principles

1. **Core + Modules**: 2-layer structure for maximum flexibility
2. **P2P-First**: Distributed architecture with local-first data
3. **Multi-Platform**: Single codebase, multiple platforms (Web, iOS, Android, CLI, Desktop)
4. **Module Marketplace Ready**: Plugin system for extensibility

## Directory Structure

```
unibos/
├── core/                      # Core system infrastructure
│   ├── backend/              # Django application (main runtime)
│   ├── models/               # Shared domain models (Django app)
│   ├── system/               # System modules
│   │   ├── authentication/
│   │   ├── users/
│   │   ├── web_ui/
│   │   ├── common/
│   │   ├── administration/
│   │   ├── logging/
│   │   └── version_manager/
│   ├── instance/             # P2P instance identity
│   ├── p2p/                  # P2P communication layer
│   ├── sync/                 # Synchronization engine
│   ├── services/             # Core services
│   └── sdk/                  # Development SDK
│       ├── python/
│       ├── dart/
│       └── docs/
├── modules/                   # Business modules (plugins)
│   ├── currencies/
│   ├── wimm/                 # Where Is My Money
│   ├── wims/                 # Where Is My Stuff
│   ├── documents/
│   ├── personal_inflation/
│   ├── birlikteyiz/         # Together (earthquake alert)
│   └── [13 total modules]
├── data/                      # Runtime data
├── docs/                      # Documentation
├── tools/                     # Development tools
│   └── scripts/
└── archive/                   # Version archives
    ├── versions/
    └── docs/
```

## Core Components

### 1. Django Backend (`core/backend/`)

**Purpose:** Main application runtime, database, API, WebSocket

**Key Features:**
- Django 4.2+ with ASGI
- PostgreSQL 15+ (primary database)
- Django Channels (WebSocket support)
- REST API endpoints
- Module loader and registry

**Location:** `core/backend/`

### 2. Core Models (`core/models/`)

**Purpose:** Shared domain models used across all modules

**Key Models:**
- `BaseModel` - Base with sync metadata
- `Item`, `ItemCategory`, `Unit`, `ItemPrice`
- `Account`, `UserProfile`

**Import Example:**
```python
from core_models.models import BaseModel, Item, Account
```

### 3. System Modules (`core/system/`)

**Purpose:** Essential system functionality

**Modules:**
- `authentication` - Login, OAuth, 2FA
- `users` - User management
- `web_ui` - Web interface
- `common` - Shared utilities
- `administration` - System admin
- `logging` - Audit logs
- `version_manager` - Version control

### 4. P2P Infrastructure

**Purpose:** Peer-to-peer synchronization and distributed data

**Components:**
- `core/instance/` - Unique instance identity (UUID)
- `core/p2p/` - mDNS discovery, STUN, relay
- `core/sync/` - Sync engine with conflict resolution

**Status:** Placeholder (v533), Full implementation planned for v534-v536

### 5. SDK (`core/sdk/`)

**Purpose:** Multi-platform development support

**Platforms:**
- Python SDK (Django integration)
- Dart SDK (Flutter/mobile)
- Documentation and examples

## Business Modules

**Location:** `modules/`

**Current Modules (13):**
1. **currencies** - Multi-currency tracking
2. **wimm** - Financial management (Where Is My Money)
3. **wims** - Inventory management (Where Is My Stuff)
4. **documents** - Document scanning with OCR (MiniCPM-v 2.6)
5. **personal_inflation** - Personal CPI tracking
6. **birlikteyiz** - Earthquake alert system
7. **cctv** - Camera monitoring
8. **recaria** - Recipe management
9. **movies** - Media library
10. **music** - Music player
11. **restopos** - Restaurant POS
12. **solitaire** - Game (multiplayer)
13. **store** - E-commerce

**Module Structure:**
```
modules/<module_name>/
├── backend/          # Django app
│   ├── models.py
│   ├── views.py
│   ├── api_views.py
│   └── urls.py
├── frontend/         # Optional web UI
├── mobile/           # Optional mobile app
└── module.json       # Module metadata
```

## Data Flow

```
User Request
    ↓
Django Backend (core/backend/)
    ↓
Module Router
    ↓
Business Module (modules/*)
    ↓
Core Models (core/models/)
    ↓
Database (PostgreSQL)
    ↓
P2P Sync (core/sync/) ← → Other Instances
```

## Key Technologies

**Backend:**
- Django 4.2+
- PostgreSQL 15+
- Channels (WebSocket)
- Celery (async tasks)
- Redis (cache/broker)

**Frontend:**
- Vanilla JavaScript
- Leaflet (maps)
- WebSocket (real-time)

**Mobile:**
- Flutter (iOS/Android)
- Dart SDK

**OCR/AI:**
- MiniCPM-v 2.6 (multilingual OCR)
- Ollama (local LLM)

## Development Workflow

### Creating a New Module

1. Create module directory: `modules/my_module/`
2. Create Django app: `modules/my_module/backend/`
3. Define models (inherit from `core_models.models.BaseModel`)
4. Create `module.json` metadata
5. Register module in core
6. Import models:
   ```python
   from core_models.models import BaseModel
   from core.system.authentication.models import User
   ```

### Running Development Server

```bash
cd core/backend
source venv/bin/activate
DJANGO_SETTINGS_MODULE=unibos_backend.settings.development ./venv/bin/python3 manage.py runserver
```

### Database Migrations

```bash
cd core/backend
./venv/bin/python3 manage.py makemigrations
./venv/bin/python3 manage.py migrate
```

## Versioning

**Current Version:** v533
**Previous Version:** v532
**Next Planned:** v534 (P2P foundation)

**Version Manager:** `core/system/version_manager/`
**Script:** `tools/scripts/unibos_version.sh`

## Future Roadmap

**v534-v536:** P2P Infrastructure
- mDNS local discovery
- STUN/TURN for NAT traversal
- Sync protocol with conflict resolution

**v537-v538:** Multi-Platform SDKs
- iOS app (Swift)
- Android app (Kotlin)
- Desktop (Electron)

**v539-v540:** Module Marketplace
- Module discovery
- Installation system
- Versioning and dependencies

## Documentation

**Main Docs:** `docs/`
- `docs/architecture/` - Architecture details
- `docs/development/` - Development guides
- `docs/features/` - Feature documentation
- `docs/deployment/` - Deployment guides

**Migration Docs:** `archive/docs/v533_migration/`
- Full architectural specification
- Impact analysis
- Roadmap

## Project Rules

**Critical File:** `RULES.md` - Read before making changes

**Key Principles:**
- NEVER manual operations (always use scripts)
- Version every significant change
- Archive before major migrations
- Test before deployment

## Support

**Version Manager:** v533 introduces comprehensive version management
**Deployment:** Production deployment to rocksteady server
**Backup:** Automated database backups in `archive/database_backups/`

---

For detailed technical specifications, see `archive/docs/v533_migration/ARCHITECTURE_v533_COMPREHENSIVE.md`
