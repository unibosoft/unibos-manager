# UNIBOS - Unicorn Bodrum Operating System

> **v2.1.5** - Modular distributed platform with 5-profile CLI architecture, P2P mesh networking, E2E encrypted messenger (Signal-grade), federated auth, sync engine, data export control, mail server management, and cross-platform mobile client (Flutter)

## Overview

UNIBOS is a distributed modular business operating system designed to run across a network of nodes (Hub servers, Raspberry Pi edge nodes, local machines) with full offline capability, P2P communication, and centralized identity management.

**Codebase:** 528 Python files (108K+ lines), 161 Dart files, 71 HTML templates

### Core Capabilities

- **5-Profile CLI/TUI Architecture** - dev, hub, manager, node, worker
- **14 Business Modules** - Finance, media, IoT, emergency alerts, secure messaging, e-commerce, POS
- **E2E Encrypted Messenger** - X25519, AES-256-GCM, Ed25519, Double Ratchet (Signal Protocol)
- **P2P Mesh Networking** - mDNS discovery, WebSocket transport, WiFi Direct, Hub fallback
- **Federated Authentication** - Hub JWT auth, offline login, account linking, 2FA, email verification
- **Sync Engine** - Version vector-based data synchronization with conflict resolution
- **Data Export Control** - Master kill switch with module-level permissions and audit logging
- **Real-time WebSocket** - 7 WebSocket consumers via Django Channels (ASGI)
- **Background Tasks** - Celery with Redis for async processing
- **Flutter Mobile Client** - iOS/Android with Riverpod state management
- **Mail Server Management** - Postfix/Dovecot provisioning, DKIM signing, DNS config

## Quick Start

### Development (unibos-dev)

```bash
# Install development CLI
pipx install -e . --force

# Launch TUI
unibos-dev tui

# Or specific commands
unibos-dev run                # Start development server
unibos-dev status             # Check system status
unibos-dev deploy rocksteady  # Deploy to production
unibos-dev release run patch  # Create patch release
unibos-dev git push-all       # Push to all 5 repos
```

### Hub Server (unibos-hub)

```bash
# On hub server (recaria.org)
unibos-hub tui               # Hub management TUI
unibos-hub status             # Check hub status
unibos-hub logs               # View hub logs
```

### Manager (unibos-manager)

```bash
# Remote management from any machine
unibos-dev manager tui        # Launch manager TUI
unibos-dev manager status     # Check all instances
unibos-dev manager ssh rocksteady  # SSH to server
```

### Node (unibos)

```bash
# On edge node (Raspberry Pi)
unibos tui                    # Launch node TUI
unibos status                 # Check node status
```

### Worker (unibos-worker)

```bash
# Background task processing
unibos-worker start           # Start Celery workers
unibos-worker start --type ocr  # Start OCR worker
unibos-worker status          # Check worker status
unibos-worker stop            # Stop all workers
```

### Development Server (Manual)

```bash
# Django dev server
PYTHONPATH="$(pwd)/core/clients/web:$(pwd)" \
DJANGO_SETTINGS_MODULE=unibos_backend.settings.development \
./core/clients/web/venv/bin/python3 core/clients/web/manage.py runserver 0.0.0.0:8000

# With ASGI/WebSocket support (Uvicorn)
PYTHONPATH="$(pwd)/core/clients/web:$(pwd)" \
DJANGO_SETTINGS_MODULE=unibos_backend.settings.development \
./core/clients/web/venv/bin/uvicorn unibos_backend.asgi:application --reload

# Celery Worker
PYTHONPATH="$(pwd)/core/clients/web:$(pwd)" \
DJANGO_SETTINGS_MODULE=unibos_backend.settings.development \
./core/clients/web/venv/bin/celery -A unibos_backend worker --loglevel=info

# Celery Beat (Scheduler)
PYTHONPATH="$(pwd)/core/clients/web:$(pwd)" \
DJANGO_SETTINGS_MODULE=unibos_backend.settings.development \
./core/clients/web/venv/bin/celery -A unibos_backend beat --loglevel=info
```

## Architecture

### System Design

```
                    ┌──────────────────────┐
                    │    Hub Server         │
                    │   (recaria.org)       │
                    │                       │
                    │  Identity Provider    │
                    │  Node Registry        │
                    │  Sync Engine          │
                    │  Message Relay        │
                    │  Mail Management      │
                    └──────────┬───────────┘
                               │
                  ┌────────────┼────────────┐
                  │            │            │
           ┌──────┴──────┐ ┌──┴──────┐ ┌──┴──────────┐
           │ Pi 5 (8GB)  │ │ Pi 4    │ │ Pi Zero 2W  │
           │ unicorn-main│ │ unicorn │ │ birlikteyiz │
           │ AP Mode     │ │ station │ │ -000000003  │
           └──────┬──────┘ └──┬──────┘ └─────────────┘
                  │            │
                  └──── P2P ───┘
                  (mDNS / WiFi Direct)
```

### 5-Profile System

| Profile | CLI Command | Repo | Purpose |
|---------|-------------|------|---------|
| **dev** | `unibos-dev` | unibos-dev | Full development + DevOps tools |
| **hub** | `unibos-hub` | unibos-hub | Central server (identity, registry, relay) |
| **manager** | `unibos-manager` | unibos-manager | Remote multi-node management |
| **node** | `unibos` | unibos | Edge node application (Raspberry Pi) |
| **worker** | `unibos-worker` | unibos-worker | Celery background task processing |

### Project Structure

```
unibos-dev/
├── core/                              # Core system layer
│   ├── base/                          # Platform foundation
│   │   ├── registry/                  #   Module registry & discovery
│   │   ├── platform/                  #   Platform detection (OS, arch, capabilities)
│   │   └── instance/                  #   Node identity & UUID persistence
│   │
│   ├── system/                        # System modules (10)
│   │   ├── authentication/            #   JWT auth, 2FA, offline auth, sessions, account linking
│   │   ├── users/                     #   User management & profiles
│   │   ├── administration/            #   Admin panel, mail server management
│   │   ├── web_ui/                    #   Web interface (login, register, main dashboard)
│   │   ├── common/                    #   Shared utilities, health checks, middleware
│   │   ├── logging/                   #   Audit logging
│   │   ├── version_manager/           #   Version tracking & analysis
│   │   ├── nodes/                     #   Node registry, heartbeat, discovery
│   │   ├── sync/                      #   Sync engine, export control, version vectors
│   │   └── p2p/                       #   P2P mesh (mDNS, WebSocket transport, HMAC)
│   │
│   ├── clients/                       # Client applications
│   │   ├── web/                       #   Django backend (settings, templates, static)
│   │   │   ├── templates/             #     71 HTML templates
│   │   │   ├── unibos_backend/        #     Django project (settings, urls, asgi)
│   │   │   └── venv/                  #     Python virtual environment
│   │   ├── mobile/                    #   Flutter app (iOS/Android)
│   │   │   └── lib/                   #     Dart source (161 files)
│   │   │       ├── core/              #       API, auth, sync, messenger, theme, config
│   │   │       ├── features/          #       auth, dashboard, messenger, settings, sync
│   │   │       └── shared/            #       Shared models
│   │   ├── tui/                       #   Terminal UI framework (BaseTUI)
│   │   └── cli/                       #   CLI framework
│   │
│   ├── profiles/                      # CLI profile implementations
│   │   ├── dev/                       #   TUI, release pipeline, changelog, git commands
│   │   ├── hub/                       #   Hub server management
│   │   ├── manager/                   #   Remote management
│   │   ├── node/                      #   Edge node operations
│   │   └── worker/                    #   Celery app, task definitions
│   │
│   ├── deployment/                    # Deploy scripts (rocksteady_deploy.sh)
│   └── version.py                     # Version metadata (__version__, __build__)
│
├── modules/                           # Business modules (14)
│   ├── messenger/                     #   E2E encrypted messaging (Signal-grade)
│   ├── birlikteyiz/                   #   Earthquake monitoring (AFAD/Kandilli/EMSC)
│   ├── currencies/                    #   Currency & crypto tracking
│   ├── documents/                     #   Multi-engine OCR & document management
│   ├── wimm/                          #   Personal finance (Where Is My Money)
│   ├── wims/                          #   Inventory management (Where Is My Stuff)
│   ├── cctv/                          #   Security camera monitoring
│   ├── movies/                        #   Movie/series library
│   ├── music/                         #   Music collection (Spotify integration)
│   ├── personal_inflation/            #   Personal CPI tracker
│   ├── recaria/                       #   MMORPG game (Ultima Online inspired)
│   ├── restopos/                      #   Restaurant POS system
│   ├── solitaire/                     #   Multiplayer card game
│   └── store/                         #   E-commerce marketplace
│
├── tools/                             # Development & ops tools
│   ├── install/                       #   Node install script (curl | bash)
│   ├── systemd/                       #   Service files (web, worker, beat)
│   ├── scripts/                       #   Backup, verify scripts
│   └── test/                          #   Test utilities
│
├── deploy/                            # Deployment configuration
├── data/                              # Runtime data (gitignored)
│   ├── logs/                          #   Application logs
│   ├── media/                         #   User uploads
│   ├── backups/                       #   Database backups
│   └── cache/                         #   Cache files
│
├── archive/                           # Version archives (local only, gitignored)
│   └── versions/                      #   500+ archived versions (v0.1.0 - v2.1.5)
│
├── VERSION.json                       # Version info (semantic + timestamp build)
├── CHANGELOG.md                       # Full version history (Conventional Commits)
├── TODO.md                            # Development roadmap & API inventory
├── RULES.md                           # Project rules & conventions
├── pyproject.toml                     # Python packaging
├── rocksteady.config.json             # Production server config
└── docker-compose.yml                 # Docker setup
```

## Technology Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Django 5.x, Django REST Framework, drf-spectacular (OpenAPI) |
| **ASGI/WebSocket** | Django Channels 4.x, Daphne/Uvicorn |
| **Database** | PostgreSQL 15+ |
| **Cache/Broker** | Redis 7+ |
| **Task Queue** | Celery 5.3+ with Beat scheduler |
| **Mobile** | Flutter 3.x, Riverpod, Dio, flutter_secure_storage |
| **Encryption** | cryptography (X25519, AES-256-GCM, Ed25519, HKDF) |
| **P2P** | Zeroconf (mDNS), WebSocket, HMAC-SHA256 |
| **Mail** | Postfix, Dovecot, OpenDKIM (SSH-based provisioning) |
| **Deployment** | systemd, rsync, SSH, pipx |
| **Platforms** | macOS, Linux, Windows, Raspberry Pi (ARM) |

## API Reference

### Authentication (`/api/v1/auth/`)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `login/` | POST | JWT login with rate limiting |
| `register/` | POST | User registration with email verification |
| `refresh/` | POST | Refresh access token |
| `logout/` | POST | Logout with token blacklist |
| `change-password/` | POST | Change password |
| `reset-password/` | POST | Password reset flow |
| `2fa/setup/` | POST | Setup two-factor authentication |
| `2fa/verify/` | POST | Verify 2FA code |
| `login/offline/` | POST | Offline login (Node only, cached credentials) |
| `link/init/` | POST | Initialize account linking (Node to Hub) |
| `link/verify/` | POST | Verify link with 6-digit code |
| `link/status/` | GET/DELETE | Get or revoke link status |
| `email/verify/request/` | POST | Request email verification |
| `email/verify/confirm/` | POST | Confirm email with token |
| `keys/` | GET | List active RS256 keys |
| `keys/create/` | POST | Create new key pair (Hub only) |
| `keys/primary/` | GET | Get primary public key |
| `permissions/sync/` | POST | Sync permissions from Hub to Node |

### Node Registry (`/api/v1/nodes/`)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `register/` | POST | Register new node |
| `{id}/heartbeat/` | POST | Send heartbeat with metrics |
| `discover/` | GET | Discover online nodes |
| `summary/` | GET | Network summary |
| `{id}/metrics/` | GET | Node metrics history |
| `{id}/events/` | GET | Node events |
| `{id}/maintenance/` | POST | Toggle maintenance mode |

### Sync Engine (`/api/v1/sync/`)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `init/` | POST | Initialize sync session |
| `push/` | POST | Push changes to Hub |
| `pull/` | POST | Pull changes from Hub |
| `complete/` | POST | Complete sync session |
| `status/` | GET | Get sync status |
| `conflicts/` | GET/POST | Manage sync conflicts |
| `offline/` | GET/POST | Manage offline operations |
| `export/settings/` | GET/PUT | Export control settings |
| `export/kill-switch/` | POST | Toggle master kill switch |
| `export/module-permission/` | POST | Set module export permission |
| `export/check/` | POST | Check if export is allowed |
| `export/logs/` | GET | View export audit logs |
| `export/stats/` | GET | Export statistics |

### P2P Mesh (`/api/v1/p2p/`)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `status/` | GET | P2P service status |
| `start/` | POST | Start P2P service |
| `stop/` | POST | Stop P2P service |
| `peers/` | GET | List discovered peers |
| `send/` | POST | Send P2P message |
| `broadcast/` | POST | Broadcast to all peers |

### Messenger (`/api/v1/messenger/`)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `conversations/` | GET/POST | List or create conversations |
| `conversations/{id}/` | GET/PATCH/DELETE | Conversation details |
| `conversations/{id}/messages/` | GET/POST | Messages (paginated) |
| `conversations/{id}/participants/` | POST | Add participants |
| `conversations/{id}/participants/{uid}/` | DELETE | Remove participant |
| `conversations/{id}/read-all/` | POST | Mark all as read |
| `messages/{id}/` | PATCH/DELETE | Edit or delete message |
| `messages/{id}/read/` | POST | Mark as read |
| `messages/{id}/reactions/` | POST/DELETE | Add or remove reaction |
| `keys/generate/` | POST | Generate encryption key pair |
| `keys/` | GET | Get user's keys |
| `keys/public/{user_id}/` | GET | Get user's public keys |
| `keys/{id}/revoke/` | POST | Revoke key |
| `p2p/status/` | GET | P2P connection status |
| `p2p/connect/` | POST | Initiate P2P connection |
| `p2p/answer/` | POST | Answer P2P connection |
| `p2p/disconnect/{session_id}/` | POST | Close P2P session |
| `typing/` | POST | Send typing indicator |
| `search/` | POST | Search messages |

### WebSocket Endpoints

| Endpoint | Consumers | Description |
|----------|-----------|-------------|
| `/ws/messenger/` | MessengerConsumer | Real-time messaging, typing, P2P signaling |
| `/ws/auth/notifications/` | AuthNotificationConsumer | Session events, security alerts |
| `/ws/p2p/` | P2PConsumer | P2P peer communication |
| `/ws/documents/` | DocumentConsumer | OCR processing updates |
| `/ws/currencies/` | CurrencyConsumer | Real-time price updates |
| `/ws/birlikteyiz/` | BirlikteyizConsumer | Earthquake alerts |
| `/ws/recaria/` | RecariaConsumer | Game real-time features |

### Other Module Endpoints

| Module | Path | Description |
|--------|------|-------------|
| Currencies | `/api/v1/currencies/` | Currency & crypto tracking API |
| WIMM | `/api/v1/wimm/` | Personal finance API |
| WIMS | `/api/v1/wims/` | Inventory management API |
| CCTV | `/api/v1/cctv/` | Camera monitoring API |
| Documents | `/documents/` | OCR & document management |
| Movies | `/movies/` | Movie/series library |
| Music | `/music/` | Music collection |
| RestoPOS | `/restopos/` | Restaurant POS |
| Personal Inflation | `/personal-inflation/` | CPI tracking |
| Recaria | `/recaria/` | MMORPG game |
| Birlikteyiz | `/birlikteyiz/` | Earthquake monitoring |
| Store | `/store/` | E-commerce marketplace |
| Solitaire | `/solitaire/` | Card game |
| Administration | `/administration/` | Admin panel & mail management |
| Version Manager | `/version-manager/` | Version analysis |
| API Schema | `/api/v1/schema/swagger/` | OpenAPI Swagger UI |
| API Schema | `/api/v1/schema/redoc/` | ReDoc documentation |

## Messenger Module (Detail)

Signal-grade encrypted messaging built from scratch.

### Cryptography

| Component | Algorithm | Purpose |
|-----------|-----------|---------|
| Key Exchange | X25519 (Curve25519) | Diffie-Hellman key agreement |
| Message Encryption | AES-256-GCM | Authenticated encryption |
| Message Signing | Ed25519 | Digital signatures |
| Key Derivation | HKDF-SHA256 | Session key derivation |
| Forward Secrecy | Double Ratchet | Per-message key rotation (Signal Protocol) |
| Replay Prevention | Nonce + client_message_id | Deduplication |

### Transport Modes (User Selectable)

- **Hub Relay** (default) - Messages routed through Hub server, offline queuing, cross-network
- **P2P Direct** - Direct WebSocket between peers via mDNS, lower latency, no server storage
- **Hybrid** - P2P when available, automatic Hub fallback

### Features

- Direct and group conversations with encrypted group key distribution
- Message reactions, replies, and threading
- File attachments with encrypted transfer
- Typing indicators and per-user read receipts
- Multi-device key synchronization and rotation
- Message expiration support

### Security Testing

69 automated security tests covering:
- Cryptographic integrity (43 encryption tests)
- Security penetration (18 tests: timing attacks, key management, input validation)
- P2P session lifecycle (connection state, transport switching)
- Message delivery reliability (retry, exponential backoff, deduplication)

## P2P Mesh Networking

### Features

- **mDNS Discovery** - Automatic node discovery on local network via Zeroconf
- **WebSocket Transport** - Real-time bidirectional communication
- **Message Signing** - HMAC-SHA256 message authentication
- **Dual-path Routing** - Direct P2P with Hub relay fallback
- **WiFi Direct** - AP mode for router-less P2P (hostapd + dnsmasq)
- **Avahi Compatible** - Works with existing avahi-daemon installations

### Active Nodes

| Node | Platform | WiFi Direct | Status |
|------|----------|-------------|--------|
| unicorn-main | Raspberry Pi 5 (8GB) | AP Mode (SSID: UNIBOS-P2P, 10.42.0.1) | Active |
| unicorn-station | Raspberry Pi 4 (8GB) | Client (10.42.0.67) | Active |
| birlikteyiz-000000003 | Raspberry Pi Zero 2W (416MB) | - | Active |

## Mail Server Management

SSH-based mail server provisioning for recaria.org:

- Postfix/Dovecot mailbox CRUD (create, delete, password reset)
- OpenDKIM setup and DKIM signing for outgoing emails
- Forwarding and auto-responder configuration
- Usage statistics from mail server
- DNS configuration guide (MX, SPF, DKIM, DMARC)
- Local mode support (SSH-free for same-machine deployments)
- Web UI in Administration > Recaria Mail
- `sync_mailboxes` management command for bulk operations

## Module Highlights

### messenger
E2E encrypted messaging with Signal-grade cryptography, P2P support, and 69 security tests.

### birlikteyiz
Turkey earthquake monitoring with AFAD/Kandilli/EMSC data sources, interactive maps, real-time WebSocket alerts, and background scheduler (5-minute intervals).

### currencies
Real-time currency and crypto tracking with portfolio management, alerts, and bank rate comparison.

### documents
Multi-engine OCR (Tesseract, PaddleOCR, EasyOCR) with document scanning, Turkish receipt parsing, and gamification (achievements, leaderboard).

### wimm / wims
Personal finance (Where Is My Money) and inventory management (Where Is My Stuff).

### cctv
Security camera monitoring with live grid view, recording management, and motion detection settings.

### recaria
MMORPG game system (Ultima Online inspired) with real-time WebSocket gameplay.

### restopos
Restaurant POS system with order management.

### solitaire
Multiplayer card game with live game view and admin dashboard.

### movies / music
Media library management with movie/series tracking and Spotify integration for music collection.

### store
E-commerce marketplace with order management.

### personal_inflation
Personal CPI tracker for individual inflation measurement.

## Deployment

### Infrastructure

| Component | Status | Details |
|-----------|--------|---------|
| PostgreSQL | Active | Primary database with pg_dump backup system |
| Redis | Active | Cache, sessions, channel layer, Celery broker |
| Daphne/Uvicorn | Active | ASGI server with WebSocket support |
| Celery Worker | Active | Background task processing |
| Celery Beat | Active | Periodic task scheduler |
| Django Channels | Active | 7 WebSocket consumers |
| P2P Mesh | Active | 3 Raspberry Pi nodes |
| Deploy Pipeline | Active | 17-step automated deployment |
| Release Pipeline | Active | Semantic versioning to 5 repos |
| systemd | Active | Service management (web, worker, beat) |

### Deploy to Production

```bash
# Automated deployment (17 steps)
unibos-dev deploy rocksteady live

# Release with version bump
unibos-dev release run patch -m "fix: description"
unibos-dev release run minor -m "feat: description"
unibos-dev release run major -m "feat!: breaking change"

# Push to all repos
unibos-dev git push-all --repos all
unibos-dev git push-all --with-version  # Include version branch
```

### Node Installation (Raspberry Pi)

```bash
# One-command install on any node
curl -sSL https://recaria.org/install.sh | bash
```

Interactive installer with arrow-key menu: install, repair, or uninstall modes.

### Server Configuration

| Server | Type | IP | Domain |
|--------|------|-----|--------|
| Rocksteady | Oracle Cloud VPS | 158.178.201.117 | recaria.org |
| unicorn-main | Raspberry Pi 5 | Local network | - |
| unicorn-station | Raspberry Pi 4 | Local network | - |
| birlikteyiz-000000003 | Raspberry Pi Zero 2W | Local network | - |

## Versioning

Semantic Versioning with timestamp build:

```
Format:  MAJOR.MINOR.PATCH+BUILD_TIMESTAMP
Example: v2.1.5+20251206172920

MAJOR: Breaking changes (CLI structure, API incompatible)
MINOR: New features (backward compatible)
PATCH: Bug fixes
BUILD: Auto-generated timestamp (YYYYMMDDHHmmss)
```

Archive naming: `unibos_v{VERSION}_b{BUILD}/`

## Requirements

### Minimum

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- 4GB RAM (8GB recommended)
- 20GB disk space

### Supported Platforms

- macOS (Apple Silicon & Intel)
- Linux (x86_64, ARM64)
- Windows (WSL recommended)
- Raspberry Pi (Pi 5, Pi 4, Pi Zero 2W)

## Documentation

| File | Description |
|------|-------------|
| `TODO.md` | Development roadmap, completed phases, API inventory |
| `CHANGELOG.md` | Full version history (Conventional Commits format) |
| `RULES.md` | Project rules, versioning, deployment conventions |
| `VERSION.json` | Version metadata, module registry, build info |
| `SECURITY_AUDIT.md` | Messenger security audit report (A rating) |
| `docs/development/` | Developer guides (versioning, session protocol, code quality) |

## Author

**Berk Hatirli**
Bitez, Bodrum, Mugla, Turkiye

---

**Current Version**: v2.1.5+20251206172920
**Codename**: Phoenix Rising
**Last Updated**: 2026-02-03
