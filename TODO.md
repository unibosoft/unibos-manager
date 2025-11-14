# UNIBOS v533+ - Yapılacaklar Listesi

**Oluşturulma:** 2025-11-13
**Güncelleme:** 2025-11-15
**Durum:** Aktif - Multi-Platform P2P Architecture Development

> **Not:** Tamamlanan görevler arşivlenir. Bu dosya sadece aktif görevleri içerir.
> Her güncelleme sırasında tamamlanan/vazgeçilen görevler gözden geçirilip düzenlenir.

---

## 🎯 AKTİF ÖNCELIK: Three-Tier CLI Architecture

### KARAR: 3 Ayrı CLI Yapısı
- ✅ **unibos** → Production CLI (son kullanıcılar: local desktop, Raspberry Pi)
- ✅ **unibos-dev** → Developer CLI (geliştirici: git, version, build)
- ✅ **unibos-server** → Server CLI (rocksteady yönetimi: services, monitoring)

### KARAR: Teknoloji Stack
- ✅ **psutil** → Platform detection ve system monitoring
- ✅ **JSON** → Module metadata (YAML yerine - standart ve net)
- ✅ **Hybrid P2P** → mDNS + REST API + WebSocket (phase-based implementation)

---

## 📋 PHASE 1: CLI Separation & Platform Foundation

### 1.1 CLI Restructuring
**Amaç:** Developer, production ve server CLI'larını ayır

- [ ] **Rename:** `core/cli/` → `core/cli-dev/`
  - [ ] Update all internal imports
  - [ ] Update entry point in setup-dev.py
  - [ ] Test `unibos-dev` command

- [ ] **Create:** `core/cli/` (Production CLI)
  - [ ] `core/cli/main.py` - Entry point (simplified splash)
  - [ ] `core/cli/ui/` - Basic UI components
  - [ ] `core/cli/commands/`
    - [ ] `start.py` - Start services (Django/Celery/Redis)
    - [ ] `stop.py` - Stop services
    - [ ] `status.py` - System health (simplified)
    - [ ] `logs.py` - View logs
    - [ ] `update.py` - Update UNIBOS (git pull + migrate + restart)
    - [ ] `backup.py` - Data backup
    - [ ] `network.py` - Network scan (mDNS discovery)
    - [ ] `module.py` - Module management (list, enable, disable)
    - [ ] `node.py` - Node management (register, peers)

- [ ] **Create:** `core/cli-server/` (Server CLI)
  - [ ] `core/cli-server/main.py` - Entry point
  - [ ] `core/cli-server/commands/`
    - [ ] `service.py` - Service management (systemd/supervisor)
    - [ ] `logs.py` - Aggregated log viewer
    - [ ] `health.py` - Comprehensive health checks
    - [ ] `stats.py` - Performance stats (CPU, RAM, disk, network)
    - [ ] `nodes.py` - Connected nodes management
    - [ ] `maintenance.py` - Maintenance mode
    - [ ] `clean.py` - Cleanup (cache, logs)
    - [ ] `update.py` - Safe update with rollback

- [ ] **Setup Files:**
  - [ ] Create `setup-dev.py` → Entry: `unibos-dev`
  - [ ] Create `setup-server.py` → Entry: `unibos-server`
  - [ ] Update `setup.py` → Entry: `unibos`
  - [ ] Update `.prodignore` → Exclude `cli-dev/`
  - [ ] Update `.rsyncignore` → Exclude `cli-dev/`

- [ ] **Testing:**
  - [ ] Test all 3 CLIs install correctly (pipx)
  - [ ] Verify `unibos-dev` only in dev environment
  - [ ] Verify `unibos` works in production
  - [ ] Verify `unibos-server` commands work on rocksteady

**Dependencies:**
```python
# All CLIs
click>=8.0

# unibos (production)
psutil>=5.9  # Platform detection, system monitoring
zeroconf>=0.80  # mDNS discovery

# unibos-server (additional)
supervisor  # Process management (optional)
```

---

### 1.2 Platform Detection Foundation
**Amaç:** Cross-platform deployment desteği

- [ ] **Create:** `core/platform/detector.py`
  - [ ] OS detection (macOS, Linux, Windows, Raspberry Pi)
  - [ ] Hardware detection (CPU, RAM, storage)
  - [ ] Device type classification (server, desktop, edge)
  - [ ] Capability detection (GPU, camera, LoRa, sensors)
  - [ ] Network configuration (IP, gateway, internet access)

- [ ] **Create:** `core/platform/service_manager.py`
  - [ ] Abstraction layer for service management
  - [ ] systemd (Linux/Raspberry Pi)
  - [ ] launchd (macOS)
  - [ ] Windows Services (Windows)
  - [ ] Supervisor (fallback)

- [ ] **CLI Integration:**
  - [ ] `unibos platform info` → Show platform details
  - [ ] `unibos-server service start/stop` → Use service_manager

**Test Cases:**
- [ ] Test on macOS (development)
- [ ] Test on Ubuntu (rocksteady)
- [ ] Test on Raspberry Pi OS (when available)

---

### 1.3 Node Identity & Persistence
**Amaç:** Her UNIBOS instance unique identity

- [ ] **Extend:** `core/instance/identity.py`
  - [ ] UUID persistence (save to `data/core/node.uuid`)
  - [ ] Node type detection (central, local, edge)
  - [ ] Platform integration (use PlatformInfo)
  - [ ] Capability declaration (modules, hardware, services)
  - [ ] Registration method (register with central server)

- [ ] **Create:** Django app `core/system/nodes/`
  - [ ] Models: `Node`, `NodeCapability`, `NodeStatus`
  - [ ] API: `/api/nodes/register`, `/api/nodes/list`, `/api/nodes/<uuid>/`
  - [ ] Admin interface
  - [ ] WebSocket for real-time status updates

- [ ] **CLI Commands:**
  - [ ] `unibos node info` → Show this node's identity
  - [ ] `unibos node register <central-url>` → Register with central
  - [ ] `unibos node peers` → List known peers
  - [ ] `unibos-server nodes list` → List all registered nodes (central only)

---

## 📋 PHASE 2: Module System Enhancement

### 2.1 Module Metadata (JSON)
**Amaç:** Standardize module metadata

- [ ] **Create template:** `module.json` schema
  ```json
  {
    "name": "string",
    "version": "semver",
    "description": "string",
    "author": "string",
    "license": "string",
    "category": "emergency|finance|media|iot|game",
    "dependencies": {
      "core": ">=version",
      "modules": ["module_name"]
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
    },
    "settings": {
      "SETTING_NAME": "default_value"
    }
  }
  ```

- [ ] **Add to all modules:** (13 modules)
  - [ ] birlikteyiz/module.json
  - [ ] cctv/module.json
  - [ ] currencies/module.json
  - [ ] documents/module.json
  - [ ] movies/module.json
  - [ ] music/module.json
  - [ ] personal_inflation/module.json
  - [ ] recaria/module.json *(Not: MMORPG game, Ultima Online benzeri)*
  - [ ] restopos/module.json
  - [ ] solitaire/module.json
  - [ ] store/module.json
  - [ ] wimm/module.json
  - [ ] wims/module.json

- [ ] **Create:** `core/system/modules/registry.py`
  - [ ] Auto-discovery (scan `modules/*/module.json`)
  - [ ] Dependency resolution
  - [ ] Platform compatibility check
  - [ ] Capability matching
  - [ ] Dynamic INSTALLED_APPS generation

- [ ] **CLI Commands:**
  - [ ] `unibos module list` → List all modules (installed, available)
  - [ ] `unibos module info <name>` → Show module details
  - [ ] `unibos module enable <name>` → Enable module
  - [ ] `unibos module disable <name>` → Disable module
  - [ ] `unibos-dev module create <name>` → Create new module template

**Integration with settings:**
```python
# settings/base.py
from core.system.modules.registry import ModuleRegistry

registry = ModuleRegistry()
UNIBOS_MODULES = registry.get_installable_apps()
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + CORE_APPS + UNIBOS_modules
```

---

## 📋 PHASE 3: P2P Network Foundation (Hybrid Approach)

### 3.1 Local Network Discovery (mDNS/Zeroconf)
**Amaç:** Auto-discover UNIBOS nodes on local network

- [ ] **Install:** `pip install zeroconf`

- [ ] **Create:** `core/p2p/discovery.py`
  - [ ] `NodeDiscovery` class
  - [ ] Advertise this node (`_unibos._tcp.local.`)
  - [ ] Scan for other nodes
  - [ ] Callback handlers (on_service_added, on_service_removed)
  - [ ] Maintain peer list

- [ ] **CLI Commands:**
  - [ ] `unibos network scan` → Scan local network for nodes
  - [ ] `unibos network advertise` → Start advertising this node

**Test:**
- [ ] Test with 2 nodes on same WiFi (MacBook + another machine)
- [ ] Verify auto-discovery works
- [ ] Verify peer list updates

---

### 3.2 Central Registry (REST API)
**Amaç:** Central server tracks all nodes

- [ ] **API Endpoints:** (Already in 1.3)
  - [ ] POST `/api/nodes/register` → Register node
  - [ ] GET `/api/nodes/list` → List all nodes
  - [ ] GET `/api/nodes/<uuid>/` → Node details
  - [ ] PUT `/api/nodes/<uuid>/heartbeat` → Update last_seen
  - [ ] DELETE `/api/nodes/<uuid>/` → Unregister

- [ ] **Heartbeat System:**
  - [ ] Celery beat task (every 60s)
  - [ ] Send heartbeat to central server
  - [ ] Mark nodes offline if no heartbeat >5min

---

### 3.3 Real-Time Communication (WebSocket)
**Amaç:** Real-time node-to-node messaging

- [ ] **Extend:** Django Channels (already installed)
  - [ ] `core/p2p/consumers.py` → WebSocket consumer
  - [ ] Routing: `/ws/p2p/<node_uuid>/`
  - [ ] Message types: ping, data, command, status

- [ ] **Node-to-Node:**
  - [ ] Direct connection (if local network)
  - [ ] Relay via central (if internet only)

**Messages:**
```json
{
  "type": "ping",
  "from": "node-uuid-123",
  "to": "node-uuid-456",
  "timestamp": "2025-11-15T12:00:00Z"
}
```

---

### 3.4 WebRTC (Future - Remote Access)
**Deferred to Phase 4+**

- [ ] Research `aiortc` library
- [ ] STUN/TURN server setup
- [ ] Signaling server (via Rocksteady)
- [ ] Use case: Remote CCTV streaming

---

## 📋 PHASE 4: Deployment Target Configurations

### 4.1 Environment-Specific Settings
**Amaç:** Settings for different deployment targets

- [ ] **Create:** `core/web/unibos_backend/settings/targets/`
  - [ ] `raspberry_pi.py` → Lightweight, edge device
  - [ ] `central_server.py` → Full features, orchestrator
  - [ ] `local_desktop.py` → User-selected modules

**raspberry_pi.py example:**
```python
from ..base import *

DEBUG = False
ALLOWED_HOSTS = ['*']  # Local network

# Minimal modules
ENABLED_MODULES = ['birlikteyiz', 'cctv', 'wimm']

# Hardware-specific
BIRLIKTEYIZ_LORA_ENABLED = True
CCTV_CAMERA_DEVICE = '/dev/video0'

# Performance
DATABASES['default']['CONN_MAX_AGE'] = 0
CELERY_WORKER_CONCURRENCY = 2
```

- [ ] **CLI Detection:**
  - [ ] Auto-detect platform on first run
  - [ ] Suggest appropriate settings file
  - [ ] `DJANGO_SETTINGS_MODULE=unibos_backend.settings.targets.raspberry_pi`

---

### 4.2 Deployment Implementations

- [ ] **Local Production:**
  - [ ] Implement `unibos-dev deploy local`
  - [ ] Target: `/Users/berkhatirli/Applications/unibos/`
  - [ ] Use rsync with `.prodignore`
  - [ ] Setup systemd/launchd service

- [ ] **Raspberry Pi:**
  - [ ] Implement `unibos-dev deploy raspberry <ip>`
  - [ ] SSH deployment
  - [ ] Platform-specific setup script
  - [ ] Service installation (systemd)
  - [ ] Test on actual Raspberry Pi hardware

- [ ] **Rocksteady (Enhanced):**
  - [ ] Already works, but integrate with CLI
  - [ ] `unibos-dev deploy rocksteady` (already exists)
  - [ ] Add rollback support
  - [ ] Health checks post-deployment

---

## 📋 PHASE 5: Raspberry Pi Hardware Integration

### 5.1 Birlikteyiz - LoRa Mesh Network
**Priority: HIGH** (Emergency network proof-of-concept)

- [ ] **Hardware:**
  - [ ] LoRa module (SX1276/SX1278, 868MHz EU)
  - [ ] GPS module (NEO-6M)
  - [ ] Test on Raspberry Pi Zero 2 W

- [ ] **Software:**
  - [ ] Python LoRa library (pyLoRa or CircuitPython)
  - [ ] GPS library (gpsd)
  - [ ] Mesh protocol implementation
  - [ ] Message relay algorithm
  - [ ] Deduplication logic

- [ ] **Integration:**
  - [ ] `modules/birlikteyiz/backend/lora_gateway.py`
  - [ ] Celery task for message processing
  - [ ] WebSocket for real-time updates

**Test:**
- [ ] 2-node mesh test (send message A→B)
- [ ] 3-node relay test (A→B→C)
- [ ] Offline queue test

---

### 5.2 CCTV - Camera Monitoring

- [ ] **Hardware:**
  - [ ] USB camera or Pi Camera Module
  - [ ] Test on Raspberry Pi 4

- [ ] **Software:**
  - [ ] OpenCV for camera access
  - [ ] Motion detection
  - [ ] Video recording (H.264)
  - [ ] Thumbnail generation

- [ ] **Integration:**
  - [ ] `modules/cctv/backend/camera_manager.py`
  - [ ] Stream via WebSocket (for live view)
  - [ ] Future: WebRTC for remote access

---

## 📋 İLERİ TARİHLİ GÖREVLER (Phase 6+)

### Offline Mode & Sync
- [ ] Offline detection
- [ ] Operation queue
- [ ] CRDT-based conflict resolution (research Automerge, Yjs)
- [ ] Sync engine (`core/sync/`)

### Module Marketplace
- [ ] Module package format (.zip with module.json)
- [ ] Installation mechanism
- [ ] Marketplace server (registry)
- [ ] Security scanning

### Multi-Platform Installers
- [ ] macOS: .dmg or Homebrew formula
- [ ] Linux: .deb and .rpm packages
- [ ] Windows: .exe installer (PyInstaller)
- [ ] Raspberry Pi: Custom OS image

---

## 📌 KURALLAR

### TODO Dosyası Yönetimi
1. **Ana dizinde sadece bu dosya** (`TODO.md`)
2. **Güncellemeler sırasında:**
   - Tamamlanan görevler → `✅` işaretle ve "TAMAMLANDI" bölümüne taşı
   - Vazgeçilen görevler → Sil veya "VAZGEÇILDI" notu ile arşivle
   - Değişen öncelikler → Yeniden sırala
   - Yeni detaylar → İlgili bölüme ekle
3. **Tamamlanan phase'ler** → `archive/planning/completed/phase-N.md`
4. **Eski roadmap'ler** → `archive/planning/`
5. **Her hafta gözden geçirme**: Tamamlanan görevler arşivlenir, yeni görevler eklenir
6. **Atomik commits**: TODO + ilgili code/docs birlikte commit edilir

### Commit Kuralı
```bash
# Todo'yu güncelle + ilgili değişiklikleri yap
git add TODO.md core/cli-dev/main.py
git commit -m "feat(cli): rename cli to cli-dev for developer commands

- Renamed core/cli/ → core/cli-dev/
- Updated TODO.md Phase 1.1 progress
- Entry point now: unibos-dev

Refs: TODO.md Phase 1.1"
```

### Todo Gözden Geçirme Checklistü
Her güncelleme sırasında:
- [ ] Tamamlanan görevler işaretlendi mi?
- [ ] Vazgeçilen görevler silindi/not düşüldü mü?
- [ ] Yeni keşfedilen görevler eklendi mi?
- [ ] Öncelikler güncellendi mi?
- [ ] Tarihler doğru mu?
- [ ] Bağlantılar (refs) eksiksiz mi?
- [ ] Bölümler organize mi? (TAMAMLANDI yukarı, aktif ortada, ilerisi altta)

---

## 📅 Haftalık Gözden Geçirme

**Her Pazartesi:**
1. Geçen hafta tamamlananları arşivle
2. Bu haftaki öncelikleri belirle
3. Engelleyicileri (blockers) tespit et

**Her Cuma:**
1. Haftalık ilerleme özeti
2. Gelecek hafta planlaması
3. Risk değerlendirmesi

---

## 📊 GÜNCEL DURUM

**Tamamlanan Phase'ler:**
- ✅ Phase 0: CLI Tool (2025-11-13)
- ✅ Phase 0: Module Path Migration (2025-11-13)

**Aktif Phase:**
- 🔄 Phase 1: CLI Separation & Platform Foundation (başladı 2025-11-15)

**Sonraki Phase:**
- 📋 Phase 2: Module System Enhancement
- 📋 Phase 3: P2P Network Foundation

---

## 🎯 KARARLAR VE NOTLAR

### CLI Architecture (2025-11-15)
- ✅ **3 ayrı CLI**: unibos, unibos-dev, unibos-server
- ✅ **psutil kullanımı**: Platform detection ve monitoring için onaylandı
- ✅ **JSON metadata**: Module.json için YAML yerine JSON tercih edildi
- ✅ **Hybrid P2P**: mDNS (local) + REST API (central) + WebSocket (real-time) + WebRTC (future)

### Module Corrections (2025-11-15)
- ✅ **Recaria:** MMORPG game project (Ultima Online benzeri), henüz başlanmadı

### Platform Priorities (2025-11-15)
- 🔴 **Phase 1:** Raspberry Pi + Birlikteyiz (LoRa mesh) - Emergency network PoC
- 🟡 **Phase 2:** CCTV camera monitoring
- 🟢 **Phase 3:** Full home server (tüm modüller)

---

**Son Güncelleme:** 2025-11-15
**Sonraki Gözden Geçirme:** 2025-11-18 (Pazartesi)
**Aktif Çalışma:** Phase 1 - CLI Separation
