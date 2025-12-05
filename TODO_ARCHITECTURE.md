# UNIBOS Platform Architecture

**Version:** v2.0.2
**Created:** 2025-12-05
**Updated:** 2025-12-05
**Status:** Phase 1 Complete - Phase 2 In Progress
**Priority:** HIGH - Foundation for All Development

---

## Quick Status

| Phase | Status | Notes |
|-------|--------|-------|
| Phase 1: Foundation Refactor | ✅ Complete | Profile restructure, settings refactor |
| Phase 2: Hub Features | 🔄 In Progress | Auth API next |
| Phase 3: Worker System | ✅ Partial | Celery services deployed |
| Phase 4: Node Enhancements | ⏳ Pending | After auth complete |
| Phase 5: Build Pipeline | ⏳ Pending | Future |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [System Overview](#2-system-overview)
3. [Hub Architecture](#3-hub-architecture)
4. [Node Architecture](#4-node-architecture)
5. [Worker System](#5-worker-system)
6. [Multi-Tenant Architecture](#6-multi-tenant-architecture)
7. [CLI & Profile Structure](#7-cli--profile-structure)
8. [Settings & Configuration](#8-settings--configuration)
9. [Colocation Support](#9-colocation-support)
10. [Build & Deploy Pipeline](#10-build--deploy-pipeline)
11. [Implementation Roadmap](#11-implementation-roadmap)
12. [Technical Specifications](#12-technical-specifications)

---

## 1. Executive Summary

### Vision

UNIBOS, merkezi olmayan (decentralized) ve cogu zaman cevrimdisi (offline-first) calisabilen, modular bir platform. Hub'lar kimlik yonetimi ve senkronizasyon saglayarak, Node'lar yerel veri isleme yaparak, Worker'lar ise dagitik islem gucu sunarak calisir.

### Key Architecture Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Hub Naming | "Hub" (not "central") | Daha esnek, multi-hub destegi |
| Hub Hierarchy | Hybrid (Primary write, regional read) | Performans + consistency dengesi |
| Worker Naming | Function-based packages | Modular, bagimsiz olceklenebilir |
| Worker Routing | Configurable per-task | Maksimum esneklik |
| Node Multi-Hub | Multiple hubs simultaneously | Load balancing, redundancy |
| CLI Count | 5 CLIs | Clear separation of concerns |
| Colocation | Full support | Tek cihazda tum profiller |

### Architecture Layers

```
+------------------------------------------------------------------+
|                     UNIBOS ARCHITECTURE                           |
|                                                                   |
|  +--------------------------+  +--------------------------+       |
|  |         CLIENTS          |  |         CLIENTS          |       |
|  |  (Mobile, Web, TUI, CLI) |  |  (Mobile, Web, TUI, CLI) |       |
|  +------------+-------------+  +------------+-------------+       |
|               |                             |                     |
|               v                             v                     |
|  +--------------------------+  +--------------------------+       |
|  |          NODE            |  |          NODE            |       |
|  |   (Local Data Server)    |  |   (Local Data Server)    |       |
|  +------------+-------------+  +------------+-------------+       |
|               |                             |                     |
|               +-------------+---------------+                     |
|                             |                                     |
|               +-------------+-------------+                       |
|               |             |             |                       |
|               v             v             v                       |
|  +----------+   +----------+   +----------+                       |
|  |   HUB    |   |   HUB    |   |   HUB    |                       |
|  |   (EU)   |   |   (US)   |   |  (Asia)  |                       |
|  +----+-----+   +----+-----+   +----+-----+                       |
|       |              |              |                             |
|       +-------+------+------+-------+                             |
|               |             |                                     |
|               v             v                                     |
|  +------------------------+------------------------+              |
|  |                    WORKERS                      |              |
|  |  +--------+ +--------+ +--------+ +--------+   |              |
|  |  | Core   | | OCR    | | Media  | | Sync   |   |              |
|  |  +--------+ +--------+ +--------+ +--------+   |              |
|  |  +--------+ +--------+                         |              |
|  |  |Finance | |Analytics|                        |              |
|  |  +--------+ +--------+                         |              |
|  +------------------------------------------------+              |
|                                                                   |
+------------------------------------------------------------------+
```

---

## 2. System Overview

### 2.1 Component Roles

| Component | Role | Description |
|-----------|------|-------------|
| **Hub** | Identity Provider, Sync Coordinator | Global kullanici yonetimi, node kayit, veri senkronizasyonu |
| **Node** | Local Data Server | Yerel veri depolama, API servisi, offline calisma |
| **Worker** | Distributed Processor | CPU/GPU yogun islemler (OCR, transcoding, analytics) |
| **Client** | User Interface | Mobile, Web UI, TUI, CLI |

### 2.2 Component Relationships

```
+------------------------------------------------------------------+
|                   COMPONENT COMMUNICATION                          |
|                                                                   |
|  Hub <---> Hub           : Geo-replication, failover              |
|  Hub <---> Node          : Auth, sync, registry                   |
|  Hub <---> Worker        : Task assignment, results               |
|  Node <---> Node         : P2P mesh, data relay (LoRa, WiFi)      |
|  Node <---> Worker       : Local task offload                     |
|  Client <---> Node       : Primary data access                    |
|  Client <---> Hub        : Auth fallback, cross-node access       |
|                                                                   |
+------------------------------------------------------------------+
```

---

## 3. Hub Architecture

### 3.1 Hub Definition

Hub, UNIBOS agindaki merkezi koordinasyon noktasidir. Ancak "merkezi" olmasi tek bir hub oldugu anlamina gelmez - birden fazla hub cografi olarak dagitilebilir.

### 3.2 Hub Hierarchy: Hybrid Model

```
+------------------------------------------------------------------+
|                    HUB HIERARCHY MODEL                            |
|                                                                   |
|  USER WRITES:                                                     |
|  +------------------------------------------------------------+  |
|  | User -> Primary Hub (EU)                                   |  |
|  | - Tum yazma islemleri primary hub'a gider                  |  |
|  | - Primary hub diger hub'lara replicate eder                |  |
|  +------------------------------------------------------------+  |
|                                                                   |
|  USER READS:                                                      |
|  +------------------------------------------------------------+  |
|  | User -> Nearest Regional Hub                               |  |
|  | - Okuma islemleri en yakin hub'dan                         |  |
|  | - Eventual consistency (saniyeler icinde)                  |  |
|  +------------------------------------------------------------+  |
|                                                                   |
|  FAILOVER:                                                        |
|  +------------------------------------------------------------+  |
|  | Primary Down -> Secondary Promotes                         |  |
|  | - Otomatik veya manuel failover                            |  |
|  | - DNS-based veya API-based routing                         |  |
|  +------------------------------------------------------------+  |
|                                                                   |
+------------------------------------------------------------------+
```

### 3.3 Hub Instances

| Hub | Location | Role | Server |
|-----|----------|------|--------|
| **Primary** | EU (Turkey) | Write master, primary IDP | Rocksteady |
| **Standby** | EU (Turkey) | Hot standby, read replica | Bebop |
| **US** | Americas | Read replica, regional auth | TBD |
| **Asia** | Asia-Pacific | Read replica, regional auth | TBD |

### 3.4 Hub Features

```python
# Hub-specific capabilities
HUB_FEATURES = {
    # Identity & Auth
    'jwt_issuer': True,              # Can issue JWTs
    'user_registry': True,           # Global user database
    'node_registry': True,           # Registered nodes

    # Data Management
    'data_aggregation': True,        # Collect from nodes
    'cross_node_sync': True,         # Sync between nodes
    'backup_coordination': True,     # Manage backups

    # Worker Management
    'worker_registry': True,         # Available workers
    'task_routing': True,            # Route tasks to workers
    'result_collection': True,       # Collect task results

    # Multi-Hub
    'hub_replication': True,         # Replicate to other hubs
    'hub_failover': True,            # Handle failover
}
```

### 3.5 High Availability (Rocksteady + Bebop)

```
+------------------------------------------------------------------+
|                    HIGH AVAILABILITY SETUP                         |
|                                                                   |
|              +-------------------+                                |
|              |    LOAD BALANCER  |                                |
|              |   (DNS or HAProxy)|                                |
|              +---------+---------+                                |
|                        |                                          |
|           +------------+------------+                             |
|           |                         |                             |
|  +--------v--------+       +--------v--------+                    |
|  |   ROCKSTEADY    |       |     BEBOP       |                    |
|  |    (Primary)    |       |   (Standby)     |                    |
|  +-----------------+       +-----------------+                    |
|  | PostgreSQL (RW) |       | PostgreSQL (RO) |                    |
|  | Redis Primary   |       | Redis Replica   |                    |
|  | Celery Workers  |       | Celery Workers  |                    |
|  +-----------------+       +-----------------+                    |
|           |                         ^                             |
|           | Streaming Replication   |                             |
|           +-------------------------+                             |
|                                                                   |
|  Failover Triggers:                                               |
|  - Health check failure (3 consecutive)                           |
|  - Manual promotion (unibos-hub promote bebop)                    |
|  - Network partition (split-brain prevention)                     |
|                                                                   |
+------------------------------------------------------------------+
```

---

## 4. Node Architecture

### 4.1 Node Definition

Node, yerel veri depolama ve API servisi saglayan UNIBOS bilesendir. Her node bagimsiz calisabilir (offline-first) ve bir veya birden fazla hub'a baglanabilir.

### 4.2 Node Types

| Type | Description | Example | Capabilities |
|------|-------------|---------|--------------|
| **Standard** | Full-featured node | Raspberry Pi 4/5, Mac | All modules, full API |
| **Edge** | Minimal node | Pi Zero 2W, sensors | Limited modules, minimal API |
| **Desktop** | Developer node | Mac, Linux, Windows | All modules, dev tools |

### 4.3 Node Multi-Hub Connection

```
+------------------------------------------------------------------+
|                  NODE MULTI-HUB CONNECTION                         |
|                                                                   |
|  Node Configuration:                                               |
|  +------------------------------------------------------------+  |
|  | {                                                          |  |
|  |   "hubs": [                                                |  |
|  |     {"url": "eu.unibos.recaria.org", "priority": 1},      |  |
|  |     {"url": "us.unibos.recaria.org", "priority": 2},      |  |
|  |     {"url": "asia.unibos.recaria.org", "priority": 3}     |  |
|  |   ],                                                       |  |
|  |   "write_hub": "eu.unibos.recaria.org",                   |  |
|  |   "read_strategy": "nearest",                              |  |
|  |   "failover_timeout": 5000                                 |  |
|  | }                                                          |  |
|  +------------------------------------------------------------+  |
|                                                                   |
|  Connection Logic:                                                 |
|  1. Primary hub'a baglan (yazmalar icin)                          |
|  2. En yakin hub'a baglan (okumalar icin)                         |
|  3. Primary basarisiz olursa secondary'ye failover                 |
|  4. Tum hub'lar basarisiz olursa offline mode                     |
|                                                                   |
+------------------------------------------------------------------+
```

### 4.4 Node Features

```python
# Node-specific capabilities
NODE_FEATURES = {
    # Data Storage
    'local_database': True,          # PostgreSQL or SQLite
    'local_cache': True,             # Redis or file-based
    'media_storage': True,           # Local media files

    # Auth
    'local_auth': True,              # Local user accounts
    'federated_auth': True,          # Hub token verification
    'offline_auth': True,            # Cached credentials

    # P2P
    'mdns_discovery': True,          # Local network discovery
    'p2p_mesh': True,                # Node-to-node communication
    'lora_support': False,           # Optional LoRa radio

    # Privacy
    'export_control': True,          # Data export settings
    'local_first': True,             # Data stays local by default
}
```

---

## 5. Worker System

### 5.1 Design Philosophy: Start Simple, Scale Later

Worker mimarisi "minimal baslangic, genisleyebilir tasarim" prensibine dayanir. Baslangicta tek bir monolitik worker, ihtiyac olustukca modular worker'lara ayrilir.

### 5.2 Current Implementation (v1.0) - Monolithic

Tek bir `unibos-worker` CLI ile tum worker islevleri yonetilir:

```bash
# Tum queue'lari dinle (default)
unibos-worker start

# Belirli queue'lari dinle
unibos-worker start --queues ocr,media

# Belirli worker tipi
unibos-worker start --type ocr

# Status ve control
unibos-worker status
unibos-worker stop
```

### 5.3 Worker Types (v1.0)

| Type | Queue | Gorevler | Resource |
|------|-------|----------|----------|
| `core` | `default` | Genel gorevler, health check | Minimal |
| `ocr` | `ocr` | Belge OCR, text extraction | CPU/GPU |
| `media` | `media` | Image resize, video transcode | CPU/GPU |

### 5.4 v1.0 Architecture

```
+------------------------------------------------------------------+
|                    WORKER v1.0 (MONOLITHIC)                        |
|                                                                   |
|  +------------------------------------------------------------+  |
|  |                    unibos-worker                            |  |
|  |                                                            |  |
|  |  +------------------+                                      |  |
|  |  |   Celery App     |                                      |  |
|  |  |------------------|                                      |  |
|  |  | - Task discovery |                                      |  |
|  |  | - Queue routing  |                                      |  |
|  |  | - Result backend |                                      |  |
|  |  +------------------+                                      |  |
|  |           |                                                |  |
|  |           v                                                |  |
|  |  +------------------+------------------+------------------+ |  |
|  |  |   tasks/core.py  |  tasks/ocr.py   | tasks/media.py   | |  |
|  |  |------------------|------------------|------------------| |  |
|  |  | - health_check   | - process_doc   | - resize_image   | |  |
|  |  | - cleanup        | - extract_text  | - transcode      | |  |
|  |  | - notifications  | - batch_ocr     | - thumbnail      | |  |
|  |  +------------------+------------------+------------------+ |  |
|  |                                                            |  |
|  +------------------------------------------------------------+  |
|                                                                   |
|  Queues:                                                          |
|  [default] -----> core tasks                                      |
|  [ocr] ---------> OCR tasks                                       |
|  [media] -------> Media processing tasks                          |
|                                                                   |
+------------------------------------------------------------------+
```

### 5.5 Future Expansion Path (v2.0+)

Sistem buyudukce worker'lar ayri paketlere bolunebilir:

```
EVOLUTION PATH
==============

Phase 1 (v1.0 - Current): Monolithic Worker
+------------------------------------------+
| unibos-worker --type {core|ocr|media}    |
+------------------------------------------+

Phase 2 (v2.0 - Growth): Specialized Workers
+------------------------------------------+
| unibos-worker-core                       |
| unibos-worker-ocr                        |
| unibos-worker-media                      |
| unibos-worker-sync                       |
+------------------------------------------+

Phase 3 (v3.0 - Scale): Independent Packages
+------------------------------------------+
| pip install unibos-worker-core           |
| pip install unibos-worker-ocr            |
| pip install unibos-worker-media          |
| pip install unibos-worker-sync           |
| pip install unibos-worker-realtime       |
| pip install unibos-worker-analytics      |
| pip install unibos-worker-finance        |
| pip install unibos-worker-backup         |
| pip install unibos-worker-notify         |
+------------------------------------------+
```

### 5.6 Extension Points (Designed Now, Implemented Later)

Bu extension point'ler v1.0'da placeholder olarak tasarlanir, gerektiginde aktive edilir:

#### Task Routing (Future v2.0)
```python
# v1.0: Basit queue-based
CELERY_TASK_ROUTES = {
    'tasks.ocr.*': {'queue': 'ocr'},
    'tasks.media.*': {'queue': 'media'},
}

# v2.0: Intelligent routing
TASK_ROUTING = {
    'ocr.process': {
        'prefer': 'gpu',
        'fallback': 'cpu',
        'locality': 'any',      # 'local', 'hub', 'any'
        'max_size_mb': 100,
    }
}
```

#### Resource Awareness (Future v2.0)
```python
# v1.0: Yok (tum worker'lar esit)

# v2.0: Resource-aware scheduling
WORKER_RESOURCES = {
    'memory_mb': 512,
    'gpu': False,
    'capabilities': ['ocr-basic', 'media-thumbnail'],
}
```

#### Multi-tenant Isolation (Future v2.0)
```python
# v1.0: Tek tenant

# v2.0: Tenant-aware
WORKER_TENANT_MODE = 'shared'  # 'dedicated', 'isolated'
TENANT_QUEUES = {
    'org-premium': ['ocr-priority', 'media-priority'],
    'org-free': ['ocr-throttled'],
}
```

#### Privacy Constraints (Future v2.0)
```python
# v1.0: Tum worker'lar esit

# v2.0: Privacy-bound workers
TASK_PRIVACY = {
    'wimm.*': {'locality': 'node_only'},
    'documents.sensitive.*': {'locality': 'node_only'},
    'cctv.*': {'locality': 'node_only', 'never_hub': True},
}
```

### 5.7 Colocation Matrix

| Cihaz | core | ocr | media | Notlar |
|-------|------|-----|-------|--------|
| Pi Zero 2W (512MB) | ✓ | ✗ | ✗ | Sadece core, memory limit |
| Pi 4 (4GB) | ✓ | ✓ | △ | Media sadece kucuk dosyalar |
| Pi 5 (8GB) | ✓ | ✓ | ✓ | Tum tipler |
| Mac/Linux Desktop | ✓ | ✓ | ✓ | Tum tipler, dev ortami |
| Hub Server | ✓ | ✓ | ✓ | Tum tipler + horizontal scale |
| GPU Server | ✓ | ✓✓ | ✓✓ | GPU-accelerated OCR/Media |

### 5.8 Queue Architecture

```
v1.0 Queues (Current):
+------------------+
| default          | --> Core tasks (health, cleanup, notify)
| ocr              | --> OCR tasks
| media            | --> Media processing
+------------------+

v2.0 Queues (Future - when needed):
+------------------+
| default          |
| ocr              |
| ocr-gpu          | --> GPU-accelerated OCR
| media            |
| media-gpu        | --> GPU-accelerated transcoding
| sync             | --> Hub-node sync tasks
| realtime         | --> High-priority, low-latency
| analytics        | --> Low-priority, batch processing
| {tenant}-*       | --> Tenant-specific queues
+------------------+
```

### 5.9 Worker Deployment Options

| Option | Description | Use Case |
|--------|-------------|----------|
| **Hub-hosted** | Worker on hub server | Default, centralized |
| **Node-hosted** | Worker on powerful node | Edge processing, privacy |
| **Colocated** | Same device as hub/node | Development, small setups |
| **Dedicated** | Separate worker server | GPU workloads (future) |

### 5.10 v1.0 File Structure

```
core/profiles/worker/
├── __init__.py
├── main.py              # unibos-worker CLI entry point
├── tui.py               # WorkerTUI (basit status/control)
├── celery_app.py        # Celery configuration
└── tasks/
    ├── __init__.py      # Task discovery
    ├── core.py          # Core tasks (health, cleanup)
    ├── ocr.py           # OCR tasks (optional import)
    └── media.py         # Media tasks (optional import)
```

### 5.11 Scenarios for Future Consideration

Bu senaryolar v1.0'da handle edilmez, ancak mimari bunlara izin verecek sekilde tasarlanmistir:

| Senaryo | v1.0 | v2.0+ |
|---------|------|-------|
| GPU paylaşımı | Yok | Worker resource limits |
| Cascade tasks | Manual chain | Celery Canvas |
| Node-local vs Hub-remote | Manual | Smart routing |
| Offline queue migration | Yok | Queue transfer API |
| Worker versioning | Yok | Capability matching |
| Resource-aware scheduling | Yok | Scheduler integration |
| Multi-tenant isolation | Yok | Tenant queues |
| Privacy-bound tasks | Yok | Locality constraints |
| Real-time vs batch | Same queue | Priority queues |
| Auto-discovery | Manual | Heartbeat + registry |

---

## 6. Multi-Tenant Architecture

### 6.1 Tenant Types

UNIBOS, farkli kullanici tiplerine hizmet verecek sekilde tasarlanmistir:

| Tenant Type | Description | Example |
|-------------|-------------|---------|
| **Individual** | Tek kullanici | Personal use |
| **Family** | Aile uyeleri | Home automation |
| **Team** | Kucuk takim | Startup |
| **Organization** | Buyuk organizasyon | Company |
| **Nonprofit** | Kar amaci gutmeyen | NGO |
| **Self-Hosted** | Kendi altyapisi | Enterprise |
| **SaaS** | Hosted service | Cloud customers |

### 6.2 Organization Model

```python
class Organization(models.Model):
    """Multi-tenant organization model"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    # Organization type
    type = models.CharField(max_length=20, choices=[
        ('individual', 'Individual'),
        ('family', 'Family'),
        ('team', 'Team'),
        ('organization', 'Organization'),
        ('nonprofit', 'Nonprofit'),
        ('enterprise', 'Enterprise'),
    ])

    # Billing & Plan
    plan = models.CharField(max_length=20, choices=[
        ('free', 'Free'),
        ('starter', 'Starter'),
        ('professional', 'Professional'),
        ('enterprise', 'Enterprise'),
        ('self_hosted', 'Self-Hosted'),
    ])

    # Limits
    max_users = models.IntegerField(default=1)
    max_nodes = models.IntegerField(default=1)
    max_storage_gb = models.IntegerField(default=5)

    # Features
    enabled_modules = models.JSONField(default=list)
    custom_domain = models.CharField(max_length=255, blank=True)

    # Ownership
    owner = models.ForeignKey('User', on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'organizations'


class OrganizationMember(models.Model):
    """Organization membership"""

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=[
        ('owner', 'Owner'),
        ('admin', 'Admin'),
        ('member', 'Member'),
        ('viewer', 'Viewer'),
    ])
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['organization', 'user']
```

### 6.3 Data Isolation

```
+------------------------------------------------------------------+
|                    MULTI-TENANT DATA ISOLATION                     |
|                                                                   |
|  Hub Level:                                                        |
|  +------------------------------------------------------------+  |
|  | - Tum organization verileri hub'da                         |  |
|  | - Tenant ID ile izolasyon                                  |  |
|  | - Cross-tenant query engelleme                             |  |
|  +------------------------------------------------------------+  |
|                                                                   |
|  Node Level:                                                       |
|  +------------------------------------------------------------+  |
|  | - Node tek bir organization'a ait                          |  |
|  | - Lokal veri tamamen izole                                 |  |
|  | - Hub'dan sadece kendi org verileri sync                   |  |
|  +------------------------------------------------------------+  |
|                                                                   |
|  Isolation Methods:                                                |
|  - Row-level security (PostgreSQL RLS)                            |
|  - Middleware tenant injection                                    |
|  - API authentication context                                     |
|                                                                   |
+------------------------------------------------------------------+
```

---

## 7. CLI & Profile Structure

### 7.1 CLI Overview

| CLI | Purpose | Target |
|-----|---------|--------|
| `unibos-dev` | Development, testing, building | Developer machine |
| `unibos-manager` | Multi-node orchestration | Ops machine |
| `unibos-hub` | Hub server management | Hub servers |
| `unibos` | Node operation | User devices |
| `unibos-worker` | Worker process | Worker hosts |

### 7.2 Profile Directory Structure

```
core/profiles/
├── dev/                    # unibos-dev
│   ├── __init__.py
│   ├── main.py             # Entry point
│   ├── tui.py              # DevTUI
│   └── commands/
│       ├── run.py          # Run dev server
│       ├── test.py         # Run tests
│       ├── build.py        # Build packages
│       ├── release.py      # Release management
│       ├── deploy.py       # Deploy to targets
│       └── db.py           # Database operations
│
├── manager/                # unibos-manager
│   ├── __init__.py
│   ├── main.py
│   ├── tui.py              # ManagerTUI
│   └── commands/
│       ├── nodes.py        # Node management
│       ├── hubs.py         # Hub management
│       ├── workers.py      # Worker management
│       ├── deploy.py       # Deployment
│       └── logs.py         # Log aggregation
│
├── hub/                    # unibos-hub
│   ├── __init__.py
│   ├── main.py
│   ├── tui.py              # HubTUI
│   └── commands/
│       ├── users.py        # User management
│       ├── nodes.py        # Node registry
│       ├── orgs.py         # Organization management
│       ├── backup.py       # Backup management
│       ├── failover.py     # HA failover
│       └── status.py       # System status
│
├── node/                   # unibos
│   ├── __init__.py
│   ├── main.py
│   ├── tui.py              # NodeTUI
│   └── commands/
│       ├── modules.py      # Module management
│       ├── sync.py         # Sync with hub
│       ├── export.py       # Export control
│       ├── peers.py        # P2P management
│       ├── backup.py       # Local backup
│       └── status.py       # Node status
│
└── worker/                 # unibos-worker
    ├── __init__.py
    ├── main.py
    └── commands/
        ├── start.py        # Start worker
        ├── stop.py         # Stop worker
        ├── status.py       # Worker status
        └── tasks.py        # Task management
```

### 7.3 Entry Points

```toml
# pyproject.toml
[project.scripts]
# Development
unibos-dev = "core.profiles.dev.main:main"

# Orchestration
unibos-manager = "core.profiles.manager.main:main"

# Hub Server
unibos-hub = "core.profiles.hub.main:main"

# Node (End User)
unibos = "core.profiles.node.main:main"

# Worker
unibos-worker = "core.profiles.worker.main:main"
```

---

## 8. Settings & Configuration

### 8.1 Django Settings Structure

```
core/clients/web/unibos_backend/settings/
├── __init__.py
├── base.py                 # Shared base settings
├── hub.py                  # Hub server settings
├── node.py                 # Node settings
├── worker.py               # Worker settings
└── development.py          # Development settings
```

### 8.2 Settings Comparison

| Setting | Hub | Node | Development |
|---------|-----|------|-------------|
| DEBUG | False | False | True |
| HTTPS | Required | Optional | No |
| JWT Issuer | Yes | No | Yes |
| JWT Verifier | No | Yes | Yes |
| All Modules | Yes | Selective | Yes |
| Redis Required | Yes | Optional | Optional |
| Celery Required | Yes | Optional | Optional |
| PostgreSQL Required | Yes | Yes | Yes |

### 8.3 Hub Settings (hub.py)

```python
"""
UNIBOS Hub Settings
Identity Provider, Registry, Data Hub
"""

UNIBOS_DEPLOYMENT_TYPE = 'hub'
UNIBOS_IS_IDENTITY_PROVIDER = True
UNIBOS_JWT_ISSUER = True
UNIBOS_NODE_REGISTRY = True
UNIBOS_WORKER_REGISTRY = True

# Multi-hub configuration
UNIBOS_HUB_ROLE = os.environ.get('HUB_ROLE', 'primary')  # primary, standby, regional
UNIBOS_HUB_REGION = os.environ.get('HUB_REGION', 'eu')

# HA Configuration
UNIBOS_HA_ENABLED = True
UNIBOS_HA_PEER = os.environ.get('HA_PEER', '')
```

### 8.4 Node Settings (node.py)

```python
"""
UNIBOS Node Settings
Local server, P2P mesh participant
"""

UNIBOS_DEPLOYMENT_TYPE = 'node'
UNIBOS_IS_IDENTITY_PROVIDER = False
UNIBOS_JWT_VERIFIER = True
UNIBOS_LOCAL_AUTH = True
UNIBOS_OFFLINE_MODE = True
UNIBOS_P2P_ENABLED = True

# Multi-hub connection
UNIBOS_HUBS = os.environ.get('UNIBOS_HUBS', 'https://unibos.recaria.org').split(',')
UNIBOS_PRIMARY_HUB = UNIBOS_HUBS[0] if UNIBOS_HUBS else None

# Export control
UNIBOS_EXPORT_ENABLED = True
UNIBOS_EXPORT_DEFAULT = False  # Opt-in
```

---

## 9. Colocation Support

### 9.1 Colocation Definition

Colocation, ayni fiziksel cihazda birden fazla UNIBOS profilinin calistirilmasidir.

### 9.2 Colocation Scenarios

| Scenario | Components | Use Case |
|----------|------------|----------|
| **Full Stack (Dev)** | Hub + Node + All Workers | Developer MacBook |
| **Mini Cluster (Pi5)** | Hub + Node + Core Workers | Raspberry Pi 5 8GB |
| **Production Hub** | Hub + Sync Worker | Rocksteady/Bebop |
| **Standalone Node** | Node only | Typical end-user |
| **GPU Workstation** | Node + Media/OCR Workers | ML/AI processing |

### 9.3 Colocation Architecture

```
+------------------------------------------------------------------+
|                    COLOCATION: SINGLE DEVICE                       |
|                                                                   |
|  Developer MacBook Pro:                                            |
|  +------------------------------------------------------------+  |
|  |                                                            |  |
|  |  +------------------+  +------------------+                |  |
|  |  |   Hub Process    |  |   Node Process   |                |  |
|  |  |------------------|  |------------------|                |  |
|  |  | Port: 8000       |  | Port: 8001       |                |  |
|  |  | DB: unibos_hub   |  | DB: unibos_node  |                |  |
|  |  +------------------+  +------------------+                |  |
|  |                                                            |  |
|  |  +------------------+  +------------------+                |  |
|  |  | Worker: Core     |  | Worker: OCR      |                |  |
|  |  |------------------|  |------------------|                |  |
|  |  | Queue: core      |  | Queue: ocr       |                |  |
|  |  +------------------+  +------------------+                |  |
|  |                                                            |  |
|  |  +------------------------------------------+              |  |
|  |  |        Shared Services                   |              |  |
|  |  |------------------------------------------|              |  |
|  |  | PostgreSQL (single instance, multi-DB)   |              |  |
|  |  | Redis (single instance, key prefixes)    |              |  |
|  |  +------------------------------------------+              |  |
|  |                                                            |  |
|  +------------------------------------------------------------+  |
|                                                                   |
+------------------------------------------------------------------+
```

### 9.4 Colocation Configuration

```yaml
# data/config/colocation.yaml
colocation:
  enabled: true
  mode: 'full_stack'  # full_stack, hub_node, node_workers

  hub:
    enabled: true
    port: 8000
    database: 'unibos_hub'
    redis_prefix: 'hub:'

  node:
    enabled: true
    port: 8001
    database: 'unibos_node'
    redis_prefix: 'node:'
    connect_to_local_hub: true

  workers:
    - name: 'core'
      enabled: true
      queue: 'core'
    - name: 'ocr'
      enabled: true
      queue: 'ocr'
    - name: 'media'
      enabled: false
      queue: 'media'
```

---

## 10. Build & Deploy Pipeline

### 10.1 Build Targets

| Target | Package | Contents |
|--------|---------|----------|
| `hub` | `unibos-hub-vX.X.X.tar.gz` | Hub profile + core + modules |
| `node` | `unibos-node-vX.X.X.tar.gz` | Node profile + core + modules |
| `worker-core` | `unibos-worker-core-vX.X.X.tar.gz` | Core worker |
| `worker-ocr` | `unibos-worker-ocr-vX.X.X.tar.gz` | OCR worker |
| `worker-media` | `unibos-worker-media-vX.X.X.tar.gz` | Media worker |
| `mobile` | `unibos-vX.X.X.{ipa,apk}` | Mobile apps |

### 10.2 Build Commands

```bash
# Build specific target
unibos-dev build hub
unibos-dev build node
unibos-dev build worker-core
unibos-dev build worker-ocr
unibos-dev build mobile

# Build all
unibos-dev build all

# Build with options
unibos-dev build node --platform raspberry-pi
unibos-dev build hub --include-debug
```

### 10.3 Deploy Commands

```bash
# Deploy hub
unibos-dev deploy hub rocksteady
unibos-dev deploy hub bebop --standby

# Deploy node
unibos-dev deploy node pi-001
unibos-dev deploy node mac-home

# Deploy worker
unibos-dev deploy worker-ocr gpu-server-01
unibos-dev deploy worker-media gpu-server-01

# Manager-based deploy
unibos-manager deploy --all nodes
unibos-manager deploy --group home-pis
```

### 10.4 Build Output Structure

```
build/
├── hub/
│   └── unibos-hub-v1.2.0.tar.gz
├── node/
│   └── unibos-node-v1.2.0.tar.gz
├── workers/
│   ├── unibos-worker-core-v1.2.0.tar.gz
│   ├── unibos-worker-ocr-v1.2.0.tar.gz
│   ├── unibos-worker-media-v1.2.0.tar.gz
│   ├── unibos-worker-sync-v1.2.0.tar.gz
│   ├── unibos-worker-finance-v1.2.0.tar.gz
│   └── unibos-worker-analytics-v1.2.0.tar.gz
├── mobile/
│   ├── unibos-v1.2.0.ipa
│   └── unibos-v1.2.0.apk
└── checksums.sha256
```

---

## 11. Implementation Roadmap

### Phase 1: Foundation Refactor (Week 1-2) ✅ COMPLETED

```
[x] 1.1 Profile Restructure
    [x] Rename server/ -> hub/
    [x] Rename prod/ -> node/
    [x] Create worker/ profile
    [x] Update pyproject.toml entry points

[x] 1.2 Settings Refactor
    [x] Create hub.py from server.py
    [x] Create worker.py for worker settings
    [x] Remove deprecated settings files (10 files removed)
    [ ] Add colocation support (future)

[ ] 1.3 Directory Structure
    [ ] Create core/system/workers/
    [ ] Create deploy/hub/, deploy/node/
    [ ] Create build/ directory structure
```

### Phase 2: Hub Features (Week 3-4)

```
[ ] 2.1 Multi-Hub Support
    [ ] Hub role configuration (primary/standby/regional)
    [ ] Hub-to-hub replication
    [ ] Failover mechanism

[ ] 2.2 Organization Model
    [ ] Organization Django model
    [ ] OrganizationMember model
    [ ] Tenant isolation middleware

[ ] 2.3 Worker Registry
    [ ] Worker registration API
    [ ] Task routing configuration
    [ ] Worker health monitoring
```

### Phase 3: Worker System (Week 5-6)

```
[ ] 3.1 Worker Base
    [ ] Worker profile structure
    [ ] Celery queue configuration
    [ ] Worker discovery protocol

[ ] 3.2 Worker Packages
    [ ] worker-core implementation
    [ ] worker-ocr implementation
    [ ] worker-sync implementation

[ ] 3.3 Task Routing
    [ ] Configurable routing rules
    [ ] GPU preference handling
    [ ] Load balancing
```

### Phase 4: Node Enhancements (Week 7-8)

```
[ ] 4.1 Multi-Hub Connection
    [ ] Hub list configuration
    [ ] Write/read hub separation
    [ ] Automatic failover

[ ] 4.2 P2P Improvements
    [ ] Enhanced mDNS discovery
    [ ] Mesh routing optimization
    [ ] LoRa integration (optional)
```

### Phase 5: Build Pipeline (Week 9-10)

```
[ ] 5.1 Build System
    [ ] Target-specific builds
    [ ] Code filtering logic
    [ ] Package generation

[ ] 5.2 Deploy System
    [ ] Multi-target deployment
    [ ] Rolling updates
    [ ] Rollback support
```

---

## 12. Technical Specifications

### 12.1 Technology Stack

| Layer | Technology |
|-------|------------|
| Backend | Django 5.1+, Django REST Framework |
| Database | PostgreSQL 14+ |
| Cache | Redis 7+ |
| Task Queue | Celery 5.3+ |
| ASGI Server | Uvicorn |
| P2P Discovery | Zeroconf (mDNS) |
| Mobile | Flutter 3.16+ |
| CLI | Python, Click |

### 12.2 System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **Hub** | 4 CPU, 8GB RAM | 8 CPU, 16GB RAM |
| **Node (Pi 4)** | 2GB RAM | 4GB RAM |
| **Node (Pi 5)** | 4GB RAM | 8GB RAM |
| **Node (Desktop)** | 4GB RAM | 8GB RAM |
| **Worker (CPU)** | 2 CPU, 4GB RAM | 4 CPU, 8GB RAM |
| **Worker (GPU)** | 4 CPU, 8GB RAM, GPU | 8 CPU, 16GB RAM, GPU |

### 12.3 Port Allocations

| Service | Port | Description |
|---------|------|-------------|
| Hub API | 8000 | Main hub API |
| Node API | 8001 | Node API (colocation) |
| Redis | 6379 | Cache/queue |
| PostgreSQL | 5432 | Database |
| Celery Flower | 5555 | Task monitoring |

---

## Appendix A: Quick Reference

### CLI Commands

```bash
# Development
unibos-dev run                    # Run dev server
unibos-dev build hub              # Build hub package
unibos-dev build node             # Build node package
unibos-dev deploy hub rocksteady  # Deploy to hub
unibos-dev release patch          # Release new version

# Manager
unibos-manager nodes              # List all nodes
unibos-manager hubs               # List all hubs
unibos-manager deploy --all       # Deploy to all

# Hub
unibos-hub status                 # Hub status
unibos-hub users                  # User management
unibos-hub failover               # Trigger failover

# Node
unibos status                     # Node status
unibos sync                       # Sync with hub
unibos export                     # Export settings

# Worker
unibos-worker start --queue ocr   # Start OCR worker
unibos-worker status              # Worker status
```

### Environment Variables

```bash
# Hub
UNIBOS_DEPLOYMENT_TYPE=hub
HUB_ROLE=primary                  # primary, standby, regional
HUB_REGION=eu
HA_PEER=bebop.local

# Node
UNIBOS_DEPLOYMENT_TYPE=node
UNIBOS_HUBS=https://eu.unibos.recaria.org,https://us.unibos.recaria.org
UNIBOS_OFFLINE_MODE=true

# Worker
WORKER_TYPE=ocr                   # core, ocr, media, sync, finance, analytics
CELERY_QUEUES=ocr
GPU_ENABLED=true
```

---

## Appendix B: Glossary

| Term | Definition |
|------|------------|
| **Hub** | Identity provider and sync coordinator |
| **Node** | Local data server |
| **Worker** | Distributed task processor |
| **Colocation** | Running multiple profiles on same device |
| **Multi-Hub** | Multiple hub instances for geo-distribution |
| **Multi-Tenant** | Supporting multiple organizations |
| **P2P Mesh** | Node-to-node direct communication |
| **Offline-First** | Designed to work without internet |

---

**Document Version:** 2.0.0
**Last Updated:** 2025-12-05
**Author:** Claude (AI Assistant) based on Berk Hatirli's specifications
**Previous Versions:** See archive/planning/TODO_ARCHITECTURE_REFACTOR_v1.0.0.md
