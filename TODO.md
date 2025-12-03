# UNIBOS Development Roadmap

**Version:** v1.0.8
**Last Update:** 2025-12-03
**Current Phase:** Production Ready - Active Development
**Architecture:** 4-Tier CLI (dev, manager, server, prod)

---

## Table of Contents

1. [Project Status Overview](#project-status-overview)
2. [Completed Infrastructure](#completed-infrastructure)
3. [Active Development Tasks](#active-development-tasks)
4. [Phase Roadmap](#phase-roadmap)
5. [Module Development](#module-development)
6. [P2P Network Architecture](#p2p-network-architecture)
7. [Deployment & Operations](#deployment--operations)
8. [Hardware Integration](#hardware-integration)
9. [Future Enhancements](#future-enhancements)
10. [Code Patterns & Best Practices](#code-patterns--best-practices)
11. [Appendices](#appendices)

---

## Project Status Overview

### Current Architecture

| Component | Status | Notes |
|-----------|--------|-------|
| 4-Tier CLI | **COMPLETED** | unibos-dev, unibos-manager, unibos-server, unibos |
| TUI Framework | **COMPLETED** | BaseTUI + profile-based inheritance |
| Platform Detection | **COMPLETED** | macOS, Linux, Raspberry Pi support |
| Deploy Pipeline | **COMPLETED** | 17-step with DB backup |
| Release Pipeline | **COMPLETED** | patch/minor/major to 4 repos |
| WebSocket/Channels | **COMPLETED** | Uvicorn + Redis Channel Layer |
| Celery Task Queue | **COMPLETED** | 12 tasks discovered and active |
| Redis Integration | **COMPLETED** | Cache, session, channels, celery |
| PostgreSQL | **COMPLETED** | Working with backup system |
| Gunicorn/ASGI | **COMPLETED** | Production WSGI/ASGI server |

### Version History (Recent)

- **v1.0.8** (2025-12-03): Docs consolidation, README/CHANGELOG update
- **v1.0.7** (2025-12-03): Log path standardization (data/logs/)
- **v1.0.6** (2025-12-03): Archive exclusion fixes
- **v1.0.5** (2025-12-03): Deploy pipeline improvements
- **v1.0.0** (2025-12-01): First stable release

---

## Completed Infrastructure

### WebSocket/Channels - COMPLETED

- Django Channels installed and configured
- Redis Channel Layer active
- 4 modules with WebSocket consumers (currencies, documents, birlikteyiz, recaria)
- Uvicorn ASGI server (better performance than Daphne)

### Celery Task Queue - COMPLETED

- Celery worker running
- 12 tasks discovered and active
- Redis broker/result backend
- Beat scheduler configured

### Redis Integration - COMPLETED

- Cache backend active
- Session storage in Redis
- Channel Layer (WebSocket)
- Celery broker

### Middleware Stack - PARTIAL

**Completed:**
- SecurityHeadersMiddleware
- RequestLoggingMiddleware
- RateLimitMiddleware
- JWTAuthMiddleware (WebSocket)
- HealthCheckMiddleware (/health/quick/)

**Pending:**
- [ ] NodeIdentityMiddleware
- [ ] P2PDiscoveryMiddleware
- [ ] MaintenanceModeMiddleware

### TUI Framework - COMPLETED

- BaseTUI class with profile inheritance
- DevTUI, ServerTUI, ManagerTUI, ProdTUI
- 3-section menu structure
- Keyboard navigation
- i18n support (TR/EN)

---

## Active Development Tasks

### Priority 1: TUI Bug Fixes (v527 Patterns)

**Problem:** Ghost keypresses, navigation jumps 2-3 items, sidebar flicker

- [ ] **Triple-Flush Input Buffer**
  - File: `core/clients/tui/base.py`
  - Add `clear_input_buffer()` method
  - Call before/after submenu entry/exit
  - Pattern from v527/src/submenu_handler.py

- [ ] **50ms Debouncing Threshold**
  - File: `core/clients/tui/base.py` - run() method
  - Pattern from v527/src/main.py lines 3206-3216

- [ ] **Selective Sidebar Redraw**
  - File: `core/clients/tui/components/sidebar.py`
  - Update only 2 lines instead of 30+
  - Pattern from v527/src/sidebar_fix.py

- [ ] **Emoji-Safe String Handling**
  - Copy `emoji_safe_slice.py` from v527
  - Destination: `core/clients/tui/utils/`

### Priority 2: UX Enhancements

- [ ] **Breadcrumb Navigation**
  - File: `core/clients/tui/components/header.py`
  - Display: `UNIBOS v1.0.8 > tools > version manager`

- [ ] **Terminal Resize Detection**
  - File: `core/clients/tui/base.py`
  - Handle SIGWINCH signal

### Priority 3: Middleware Completion

- [ ] Complete remaining 3 middleware items
- [ ] Test security headers on all responses
- [ ] Verify rate limiting on API endpoints

### Priority 4: Health Endpoints Enhancement

- [ ] Expand `/health/quick/` to full health check
- [ ] Add service-specific health endpoints
- [ ] Database connectivity check
- [ ] Redis connectivity check
- [ ] Celery worker status

---

## Phase Roadmap

### Phase 1: Service Management & Node Identity (IN PROGRESS)

#### Service Manager Implementation

- [ ] Create `core/platform/service_manager.py`
  - systemd support (Linux/Raspberry Pi)
  - launchd support (macOS)
  - Windows Services support
  - Supervisor fallback

- [ ] CLI Integration:
  - `unibos service start`
  - `unibos service stop`
  - `unibos service status`
  - `unibos-server service restart`

#### Node Identity & Persistence

- [ ] Extend `core/instance/identity.py`
  - UUID persistence (`data/core/node.uuid`)
  - Node type detection (central, local, edge)
  - Capability declaration
  - Registration method

- [ ] Create Django app `core/system/nodes/`
  - Models: Node, NodeCapability, NodeStatus
  - API: `/api/nodes/register`, `/api/nodes/list`
  - Admin interface
  - WebSocket for real-time status

### Phase 2: Module System Enhancement

#### Module Metadata (JSON)

- [ ] Create `module.json` schema template
- [ ] Add module.json to all 13 modules:
  - birlikteyiz, cctv, currencies, documents
  - movies, music, personal_inflation, recaria
  - restopos, solitaire, store, wimm, wims

- [ ] Create `core/system/modules/registry.py`
  - Auto-discovery
  - Dependency resolution
  - Platform compatibility check
  - Dynamic INSTALLED_APPS generation

- [ ] CLI Commands:
  - `unibos module list`
  - `unibos module enable <name>`
  - `unibos module disable <name>`
  - `unibos-dev module create <name>`

#### Critical Module Features

**Currencies Module:**
- [ ] Implement PortfolioConsumer
- [ ] Implement CurrencyAlertsConsumer
- [ ] Copy services.py from v532 (22,240 bytes)

**Documents Module:**
- [ ] Copy ocr_service.py from v532 (55,651 bytes - 11 OCR engines)
- [ ] Add confidence tracking to Document model
- [ ] Implement Turkish receipt parsing

**Birlikteyiz Module:**
- [ ] EMSC WebSocket integration
- [ ] Enhanced interactive map (Leaflet.js)

### Phase 3: P2P Network Foundation

See [P2P Network Architecture](#p2p-network-architecture) section.

### Phase 4: Production Features

#### Administration Module

- [ ] Copy entire module from v532
- [ ] Database Models: Role, Department, AuditLog, SystemSetting
- [ ] Run migrations and create defaults
- [ ] Test RBAC permissions

#### Advanced Security

- [ ] Copy authentication validators from v532
- [ ] Implement custom exception handler
- [ ] Configure Sentry error tracking

#### Deployment Automation

- [ ] Local Production: `unibos-dev deploy local`
- [ ] Raspberry Pi: `unibos-dev deploy raspberry <ip>`
- [ ] Rollback support
- [ ] Health checks post-deployment

### Phase 5: Hardware Integration

See [Hardware Integration](#hardware-integration) section.

### Phase 6+: Future Enhancements

See [Future Enhancements](#future-enhancements) section.

---

## Module Development

### Module Status

| Module | Backend | WebSocket | Celery Tasks | Status |
|--------|---------|-----------|--------------|--------|
| birlikteyiz | **DONE** | **DONE** | **DONE** | Production |
| currencies | **DONE** | **DONE** | **DONE** | Production |
| documents | **DONE** | **DONE** | Partial | Development |
| personal_inflation | **DONE** | - | **DONE** | Production |
| recaria | Basic | - | - | Prototype |
| cctv | Basic | - | - | Prototype |
| movies | **DONE** | - | - | Production |
| music | **DONE** | - | - | Production |
| restopos | Basic | - | - | Development |
| solitaire | Basic | - | - | Development |
| store | Basic | - | - | Development |
| wimm | **DONE** | - | - | Production |
| wims | **DONE** | - | - | Production |

### Module JSON Schema

```json
{
  "name": "module_name",
  "version": "1.0.0",
  "description": "Module description",
  "author": "UNIBOS Team",
  "license": "proprietary",
  "category": "emergency|finance|media|iot|game",
  "dependencies": {
    "core": ">=1.0.0",
    "modules": []
  },
  "capabilities": {
    "requires_lora": false,
    "requires_gps": false,
    "requires_camera": false,
    "offline_capable": true,
    "p2p_enabled": false
  },
  "platforms": ["linux", "macos", "windows", "raspberry_pi"],
  "entry_points": {
    "backend": "modules.name.backend",
    "cli": "modules.name.cli",
    "mobile": "modules.name.mobile"
  }
}
```

---

## P2P Network Architecture

### Architecture Overview

```
Local Network (LAN)              Wide Area (WAN)
+---------------------+         +---------------------+
|   mDNS Discovery    |         |  Central Registry   |
|  (Zero-config)      |         |  (Cloud fallback)   |
+---------------------+         +---------------------+
         |                               |
         v                               v
+---------------------+         +---------------------+
|  REST API Endpoints |<------->|   REST API Sync     |
|  (Node discovery)   |         |  (Cross-network)    |
+---------------------+         +---------------------+
         |                               |
         v                               v
+---------------------+         +---------------------+
|  WebSocket Channels |<------->|   WebRTC Data       |
|  (Real-time events) |         |   (Direct P2P)      |
+---------------------+         +---------------------+
```

### Node Identity Schema

```python
{
    "node_id": "uuid4",
    "node_name": "rocksteady",
    "device_type": "server",  # server/desktop/raspberry_pi/edge
    "capabilities": ["gpu", "camera", "gpio"],
    "services": ["web", "api", "celery"],
    "network": {
        "local_ip": "192.168.0.100",
        "public_ip": "158.178.201.117",
        "mdns_name": "rocksteady.local"
    }
}
```

### Phase 3.1: Local Network Discovery (mDNS)

- [ ] Install zeroconf package
- [ ] Create `core/p2p/discovery.py`
  - NodeDiscovery class
  - Advertise this node (`_unibos._tcp.local.`)
  - Scan for other nodes
  - Callback handlers

- [ ] CLI Commands:
  - `unibos network scan`
  - `unibos network advertise`

### Phase 3.2: Central Registry (REST API)

- [ ] API Endpoints:
  - POST `/api/nodes/register`
  - GET `/api/nodes/list`
  - GET `/api/nodes/<uuid>/`
  - PUT `/api/nodes/<uuid>/heartbeat`
  - DELETE `/api/nodes/<uuid>/`

- [ ] Heartbeat System:
  - Celery beat task (every 60s)
  - Mark nodes offline if no heartbeat >5min

### Phase 3.3: Real-Time Communication (WebSocket)

- [ ] Create `core/p2p/consumers.py`
  - WebSocket consumer for node-to-node messaging
  - Routing: `/ws/p2p/<node_uuid>/`
  - Message types: ping, data, command, status

### Phase 3.4: WebRTC (Future)

- [ ] Research aiortc library
- [ ] STUN/TURN server setup
- [ ] Signaling server
- [ ] Use case: Remote CCTV streaming

---

## Deployment & Operations

### 4-Repo Architecture

| Repo | Purpose | gitignore Template |
|------|---------|-------------------|
| unibos-dev | Full development environment | .gitignore.dev |
| unibos-manager | Manager tools only | .gitignore.manager |
| unibos-server | Server deployment | .gitignore.server |
| unibos (prod) | Production nodes | .gitignore.prod |

### Deploy Pipeline (17 Steps)

1. Pre-flight checks
2. Git operations
3. SSH connection
4. Database backup
5. Code pull
6. Dependency installation
7. Database migrations
8. Static file collection
9. Service restart
10. Health check
11. Notification
12. Cleanup
13. Logging
14. Rollback preparation
15. Version tagging
16. Changelog update
17. Post-deployment verification

### Release Types

- **patch**: Bug fixes (v1.0.x)
- **minor**: New features (v1.x.0)
- **major**: Breaking changes (vX.0.0)

### Server Configuration (rocksteady)

```json
{
  "name": "rocksteady",
  "host": "rocksteady",
  "user": "ubuntu",
  "port": 22,
  "deploy_path": "/home/ubuntu/unibos",
  "venv_path": "/home/ubuntu/unibos/core/clients/web/venv",
  "django_settings": "unibos_backend.settings.server",
  "server_port": 8000
}
```

### Log Paths (Standardized)

- **Production**: `~/unibos/data/logs/`
- **Local Dev**: `data/logs/`
- **Docker**: `/app/data/logs/`

### Environment-Specific Settings

- [ ] Create `settings/targets/raspberry_pi.py`
- [ ] Create `settings/targets/central_server.py`
- [ ] Create `settings/targets/local_desktop.py`

---

## Hardware Integration

### Birlikteyiz - LoRa Mesh Network

**Priority:** HIGH (Emergency network proof-of-concept)

**Hardware:**
- [ ] LoRa module (SX1276/SX1278, 868MHz EU)
- [ ] GPS module (NEO-6M)
- [ ] Test on Raspberry Pi Zero 2 W

**Software:**
- [ ] Python LoRa library
- [ ] GPS library (gpsd)
- [ ] Mesh protocol implementation
- [ ] Message relay algorithm

**Integration:**
- [ ] `modules/birlikteyiz/backend/lora_gateway.py`
- [ ] Celery task for message processing
- [ ] WebSocket for real-time updates

**Tests:**
- [ ] 2-node mesh test (A→B)
- [ ] 3-node relay test (A→B→C)
- [ ] Offline queue test

### CCTV - Camera Monitoring

**Hardware:**
- [ ] USB camera or Pi Camera Module
- [ ] Test on Raspberry Pi 4

**Software:**
- [ ] OpenCV for camera access
- [ ] Motion detection
- [ ] Video recording (H.264)
- [ ] Thumbnail generation

**Integration:**
- [ ] `modules/cctv/backend/camera_manager.py`
- [ ] Stream via WebSocket
- [ ] Future: WebRTC for remote access

### Raspberry Pi Deployment

- [ ] Custom OS image preparation
- [ ] Auto-configuration on first boot
- [ ] SD card manager tool
- [ ] Platform-specific optimizations

---

## Future Enhancements

### High Priority

- [ ] **Test Suite (pytest)**
  - Unit tests for core modules
  - Integration tests for API
  - TUI tests

- [ ] **Celery Worker Monitoring TUI**
  - Real-time task status
  - Worker health
  - Queue lengths

- [ ] **Auto SSL/Let's Encrypt**
  - Certbot integration
  - Auto-renewal

### Medium Priority

- [ ] **Offline Mode & Sync**
  - Offline detection
  - Operation queue
  - CRDT-based conflict resolution
  - Sync engine

- [ ] **Module Marketplace**
  - Module package format
  - Installation mechanism
  - Security scanning

- [ ] **Multi-Platform Installers**
  - macOS: .dmg or Homebrew
  - Linux: .deb and .rpm
  - Windows: .exe installer

### Low Priority

- [ ] **Castle Guard (Security Dashboard)**
  - Security metrics visualization
  - Threat detection
  - Audit logs viewer

- [ ] **Forge Smithy (Setup Wizard)**
  - Guided initial setup
  - Module selection
  - Configuration wizard

- [ ] **Anvil Repair (Diagnostics)**
  - System diagnostics
  - Auto-repair capabilities
  - Health reports

- [ ] **AI Builder Integration**
  - AI-assisted development
  - Code generation
  - Documentation generation

---

## Code Patterns & Best Practices

### Celery Task Pattern (Production-Grade)

```python
@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def import_data_incremental(self):
    """Production-grade import with all best practices"""

    # 1. Create import log for tracking
    import_log = ImportLog.objects.create(
        import_type='scheduled',
        status='in_progress'
    )

    try:
        # 2. Fetch data with timeout
        response = requests.get(API_URL, timeout=30)
        response.raise_for_status()
        data = response.json()

        # 3. Get existing IDs in ONE query (performance)
        existing_ids = set(Model.objects.values_list('entry_id', flat=True))

        # 4. Bulk insert with statistics tracking
        batch = []
        batch_size = 100
        stats = {'total': 0, 'new': 0, 'updated': 0, 'failed': 0}

        for entry_id, entry_data in data.items():
            if self._validate_entry(entry_data):
                batch.append(self._process_entry(entry_id, entry_data))
                stats['new'] += 1

            if len(batch) >= batch_size:
                with transaction.atomic():
                    Model.objects.bulk_create(batch, batch_size=50)
                batch = []

        # 5. Update import log
        import_log.status = 'completed'
        import_log.new_entries = stats['new']
        import_log.save()

        # 6. Cache invalidation
        if stats['new'] > 0:
            cache.delete('data:latest')
            notify_updates.delay(stats['new'])

        return {'status': 'success', 'stats': stats}

    except Exception as e:
        import_log.status = 'failed'
        import_log.error_message = str(e)
        import_log.save()
        raise self.retry(exc=e)
```

### WebSocket Consumer Pattern

```python
class DataConsumer(AsyncJsonWebsocketConsumer):
    """Production-ready WebSocket with subscription model"""

    async def connect(self):
        # 1. Authentication
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            await self.close()
            return

        # 2. Join room
        self.room_group_name = "data_updates"
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # 3. Accept and send initial data
        await self.accept()
        await self.send_initial_data()

        # 4. Start periodic updates
        self.update_task = asyncio.create_task(
            self.periodic_update()
        )

    async def periodic_update(self):
        while True:
            try:
                await asyncio.sleep(10)
                updates = await self.get_updates()
                if updates:
                    await self.send_json({
                        'type': 'update',
                        'data': updates
                    })
            except asyncio.CancelledError:
                break
```

### Query Optimization Pattern

```python
# 1. Prefetch related objects
items = Model.objects.prefetch_related(
    'related__nested'
).select_related('user')

# 2. Annotate for aggregations
holdings = Holding.objects.annotate(
    current_value=F('amount') * F('rate')
)

# 3. Values for lightweight queries
summary = Model.objects.values('category').annotate(
    avg=Avg('value'),
    count=Count('id')
)

# 4. Bulk operations
Model.objects.bulk_create(batch, batch_size=100)
Model.objects.bulk_update(items, fields=['field'], batch_size=100)
```

---

## Appendices

### Appendix A: Required Packages

```txt
# Core
Django>=5.1
djangorestframework
psutil>=5.9

# WebSocket & Real-time
channels>=4.0.0
channels-redis>=4.1.0
uvicorn[standard]>=0.25.0

# Task Queue
celery>=5.3.0
django-celery-beat>=2.5.0
django-celery-results>=2.5.0

# P2P & Discovery
zeroconf>=0.80.0
websockets>=12.0
aiohttp>=3.9.0

# Cache & Session
django-redis>=5.4.0

# Monitoring
django-prometheus>=2.3.0
sentry-sdk>=1.40.0

# Static Files
whitenoise>=6.6.0

# API Documentation
drf-spectacular>=0.27.0
```

### Appendix B: Archive File Locations

**v527 (TUI Patterns):**
```
archive/versions/.../unibos_v527_.../src/
├── emoji_safe_slice.py → core/clients/tui/utils/
└── submenu_handler.py → core/clients/tui/framework/
```

**v532 (Backend Features):**
```
archive/versions/.../unibos_v532_.../
├── apps/common/middleware.py → core/system/common/backend/
├── apps/currencies/consumers.py → modules/currencies/backend/
├── apps/currencies/tasks.py → modules/currencies/backend/
├── apps/currencies/services.py → modules/currencies/backend/
├── apps/documents/ocr_service.py → modules/documents/backend/
└── apps/administration/ → core/system/administration/
```

### Appendix C: CLI Reference

**Development (unibos-dev):**
```bash
unibos-dev tui              # Launch development TUI
unibos-dev run              # Start development server
unibos-dev status           # Check development status
unibos-dev deploy rocksteady # Deploy to production
unibos-dev release patch    # Create patch release
unibos-dev manager tui      # Launch manager TUI
```

**Server (unibos-server):**
```bash
unibos-server tui           # Launch server TUI
unibos-server status        # Check server status
unibos-server restart       # Restart services
unibos-server logs          # View server logs
```

**Production (unibos):**
```bash
unibos tui                  # Launch production TUI
unibos status               # Check system status
unibos module list          # List enabled modules
```

### Appendix D: Project Structure

```
unibos-dev/
├── core/
│   ├── clients/
│   │   ├── cli/            # Production CLI
│   │   ├── tui/            # TUI Framework
│   │   └── web/            # Django Backend
│   ├── profiles/
│   │   ├── dev/            # Development profile
│   │   ├── manager/        # Manager profile
│   │   ├── server/         # Server profile
│   │   └── prod/           # Production profile
│   ├── platform/           # Platform detection
│   ├── instance/           # Node identity
│   └── system/             # System modules
├── modules/                # Application modules
├── data/                   # Runtime data (gitignored)
├── archive/                # Version archives (local only)
├── tools/                  # Development tools
├── VERSION.json            # Version information
├── TODO.md                 # This file
└── RULES.md                # Project rules
```

---

**Last Update:** 2025-12-03
**Next Review:** Weekly Monday
**Current Focus:** TUI bug fixes, middleware completion
