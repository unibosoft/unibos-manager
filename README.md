# UNIBOS - Unicorn Bodrum Operating System

> **v2.0.2** - Production-ready modular platform with 5-profile CLI architecture, P2P mesh networking, real-time WebSocket, federated auth, sync engine, and data export control

## Overview

UNIBOS is a comprehensive modular operating system built with Django, featuring:

- **5-Profile CLI Architecture** - dev, hub, manager, node, worker profiles
- **P2P Mesh Networking** - mDNS discovery, WebSocket transport, direct node-to-node communication
- **TUI Framework** - Full-featured terminal interface with i18n support
- **Federated Authentication** - Hub JWT auth with offline mode support
- **Sync Engine** - Version vector-based data synchronization
- **Data Export Control** - Master kill switch with module-level permissions
- **Real-time Updates** - WebSocket via Django Channels
- **Background Tasks** - Celery with Redis for async processing (dedicated worker profile)
- **13 Business Modules** - Finance, media, IoT, emergency alerts

## Quick Start

### Development (unibos-dev)

```bash
# Install development CLI
pipx install -e . --force

# Launch TUI
unibos-dev tui

# Or specific commands
unibos-dev run              # Start development server
unibos-dev status           # Check system status
unibos-dev deploy rocksteady  # Deploy to production
unibos-dev release run patch  # Create patch release
```

### Manager (unibos-manager)

```bash
# Remote management from any machine
unibos-dev manager tui       # Launch manager TUI
unibos-dev manager status    # Check all instances
unibos-dev manager ssh rocksteady  # SSH to server
```

### Hub Server (unibos-hub)

```bash
# On hub server (Rocksteady/Bebop)
unibos-hub tui               # Hub management TUI
unibos-hub status            # Check hub status
unibos-hub logs              # View hub logs
```

### Node (unibos)

```bash
# Local node interface
unibos tui                   # Launch node TUI
unibos status                # Check node status
```

### Worker (unibos-worker)

```bash
# Background task processing
unibos-worker start          # Start Celery workers
unibos-worker start --type ocr  # Start OCR worker
unibos-worker status         # Check worker status
unibos-worker stop           # Stop all workers
```

## Architecture

### 5-Profile CLI System

| Profile | Command | Purpose | Target |
|---------|---------|---------|--------|
| **dev** | `unibos-dev` | Development & DevOps | Developers |
| **hub** | `unibos-hub` | Hub server management | Hub operators |
| **manager** | `unibos-manager` | Multi-node orchestration | System admins |
| **node** | `unibos` | Local node application | End users |
| **worker** | `unibos-worker` | Background task processing | Task workers |

### Project Structure

```
unibos-dev/
├── core/                          # Core system infrastructure
│   ├── clients/                   # Client applications
│   │   ├── cli/                   # CLI framework
│   │   ├── tui/                   # TUI framework (BaseTUI)
│   │   └── web/                   # Django backend
│   ├── profiles/                  # CLI profiles
│   │   ├── dev/                   # Developer profile
│   │   ├── hub/                   # Hub server profile
│   │   ├── manager/               # Manager profile
│   │   ├── node/                  # Node profile
│   │   └── worker/                # Worker profile
│   ├── platform/                  # Platform detection
│   ├── instance/                  # Node identity
│   └── system/                    # System modules
│       ├── authentication/        # Auth & permissions
│       ├── users/                 # User management
│       ├── administration/        # System admin
│       ├── web_ui/                # Web interface
│       ├── common/                # Shared utilities
│       ├── logging/               # Audit logs
│       ├── version_manager/       # Version control
│       ├── nodes/                 # Node registry
│       ├── sync/                  # Data sync engine
│       └── p2p/                   # P2P mesh networking
│
├── modules/                       # Business modules (13)
│   ├── currencies/                # Currency & crypto tracking
│   ├── wimm/                      # Financial management (Where Is My Money)
│   ├── wims/                      # Inventory management (Where Is My Stuff)
│   ├── documents/                 # OCR & document scanning
│   ├── personal_inflation/        # Personal CPI tracker
│   ├── birlikteyiz/              # Earthquake alerts (Turkey)
│   ├── cctv/                      # Camera monitoring
│   ├── recaria/                   # MMORPG game (Ultima Online inspired)
│   ├── movies/                    # Media library
│   ├── music/                     # Music collection
│   ├── restopos/                  # Restaurant POS
│   ├── solitaire/                 # Multiplayer card game
│   └── store/                     # E-commerce
│
├── data/                          # Runtime data (gitignored)
│   ├── logs/                      # Application logs
│   ├── media/                     # User uploads
│   ├── backups/                   # Database backups
│   └── cache/                     # Cache files
│
├── archive/                       # Version archives (local only)
├── tools/                         # Development tools
├── VERSION.json                   # Version information
├── TODO.md                        # Development roadmap
├── CHANGELOG.md                   # Version history
└── RULES.md                       # Project rules
```

## Infrastructure Status

| Component | Status | Notes |
|-----------|--------|-------|
| PostgreSQL | **Active** | Primary database with backup system |
| Redis | **Active** | Cache, sessions, channels, celery |
| Gunicorn/Uvicorn | **Active** | ASGI with WebSocket support |
| Celery Worker | **Active** | 12 tasks discovered |
| Django Channels | **Active** | Real-time WebSocket |
| P2P Mesh | **Active** | mDNS discovery, WebSocket transport |
| Deploy Pipeline | **Active** | 17-step automated deployment |
| Release Pipeline | **Active** | Patch/minor/major to 5 repos |

## P2P Mesh Networking

UNIBOS nodes can communicate directly via P2P mesh networking:

### Features
- **mDNS Discovery** - Automatic node discovery on local network via Zeroconf
- **WebSocket Transport** - Real-time bidirectional communication
- **Message Signing** - HMAC-based message authentication
- **Dual-path Routing** - Direct P2P or Hub relay fallback
- **Avahi Compatible** - Works with existing avahi-daemon installations
- **WiFi Direct** - Direct AP mode for router-less P2P communication

### API Endpoints
```
GET  /api/v1/p2p/status/     # P2P service status
POST /api/v1/p2p/start/      # Start P2P service
POST /api/v1/p2p/stop/       # Stop P2P service
GET  /api/v1/p2p/peers/      # List discovered peers
POST /api/v1/p2p/send/       # Send P2P message
POST /api/v1/p2p/broadcast/  # Broadcast to all peers
```

### Active Nodes
| Node | Platform | WiFi Direct | Status |
|------|----------|-------------|--------|
| unicorn-main | Raspberry Pi 5 (8GB) | AP Mode (UNIBOS-P2P) | P2P Active |
| unicorn-station | Raspberry Pi 4 (8GB) | Client (10.42.0.67) | P2P Active |
| birlikteyiz-000000003 | Raspberry Pi Zero 2W | - | P2P Active |

## Requirements

### Minimum

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- 4GB RAM (8GB recommended)
- 20GB disk space

### Production Stack

- **ASGI Server**: Gunicorn + Uvicorn workers
- **Database**: PostgreSQL 15+
- **Cache/Broker**: Redis 7+
- **Task Queue**: Celery 5.3+
- **WebSocket**: Django Channels 4.0+

## Development

### Web Server

```bash
cd core/clients/web
./venv/bin/python manage.py runserver
```

### With Uvicorn (WebSocket support)

```bash
PYTHONPATH="$(pwd):$(pwd)/core/clients/web" \
DJANGO_SETTINGS_MODULE=unibos_backend.settings.development \
./venv/bin/uvicorn unibos_backend.asgi:application --reload
```

### Celery Worker

```bash
PYTHONPATH="$(pwd):$(pwd)/core/clients/web" \
DJANGO_SETTINGS_MODULE=unibos_backend.settings.development \
./venv/bin/celery -A unibos_backend worker --loglevel=info
```

### Celery Beat (Scheduler)

```bash
PYTHONPATH="$(pwd):$(pwd)/core/clients/web" \
DJANGO_SETTINGS_MODULE=unibos_backend.settings.development \
./venv/bin/celery -A unibos_backend beat --loglevel=info
```

## Deployment

### 5-Repo Architecture

| Repo | Purpose | Contains |
|------|---------|----------|
| `unibos-dev` | Development | Full codebase + dev tools |
| `unibos-hub` | Hub Server | Hub profile for central servers |
| `unibos-manager` | Manager | Remote management tools |
| `unibos` | Node | Local node application |
| `unibos-worker` | Worker | Background task processing |

### Deploy to Rocksteady Server

```bash
# Preview deployment
unibos-dev deploy rocksteady

# Live deployment
unibos-dev deploy rocksteady live
```

### Deploy Pipeline (17 Steps)

1. Validate configuration
2. Check SSH connectivity
3. **Backup database**
4. Prepare deployment directory
5. Clone repository
6. Setup Python environment
7. Install dependencies
8. Install CLI
9. Create environment file
10. Setup module registry
11. Setup data directories
12. Setup PostgreSQL
13. Run migrations
14. Collect static files
15. Setup systemd service
16. Start service
17. Health check

### Release Pipeline

```bash
# Patch release (bug fixes)
unibos-dev release run patch -m "fix: bug description"

# Minor release (new features)
unibos-dev release run minor -m "feat: new feature"

# Major release (breaking changes)
unibos-dev release run major -m "feat!: breaking change"
```

## Key Features

### TUI Framework

- Full-featured terminal interface
- Profile-based inheritance (DevTUI, HubTUI, ManagerTUI, NodeTUI)
- 3-section menu structure
- Keyboard navigation with vim-style bindings
- i18n support (Turkish/English)

### Real-time Updates

- Django Channels for WebSocket
- Redis Channel Layer
- 4 modules with WebSocket consumers
- Uvicorn ASGI server

### Background Tasks

- Celery worker with 12 discovered tasks
- Redis broker/result backend
- Beat scheduler for periodic tasks
- Task monitoring and logging

### Multi-node Architecture (Foundation)

- Node identity system with UUID persistence
- mDNS local discovery support
- Central registry API
- P2P communication foundation

### Version Archive System

- Timestamp-based version snapshots
- Automatic archiving on release
- Archive browsing via CLI
- Complete codebase preservation

## Module Highlights

### currencies

Real-time currency and crypto tracking with portfolio management, alerts, and bank rate comparison.

### birlikteyiz

Turkey earthquake monitoring with AFAD/Kandilli data sources, interactive maps, and real-time alerts.

### documents

Multi-engine OCR (Tesseract, PaddleOCR, EasyOCR) with document scanning and Turkish receipt parsing.

### wimm/wims

Personal finance (Where Is My Money) and inventory (Where Is My Stuff) management.

## Documentation

- `TODO.md` - Comprehensive development roadmap
- `CHANGELOG.md` - Complete version history
- `RULES.md` - Project rules and conventions

## Server Configuration

### Rocksteady (Production)

- **Host**: rocksteady (Oracle Cloud)
- **IP**: 158.178.201.117
- **Domain**: recaria.org
- **Path**: /home/ubuntu/unibos
- **Logs**: ~/unibos/data/logs/

## Author

**Berk Hatirli**
Bitez, Bodrum, Mugla, Turkiye

*Built with Claude Code*

---

**Current Version**: v2.0.2
**Last Updated**: 2025-12-05
