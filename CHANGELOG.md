# UNIBOS Changelog

All notable changes to UNIBOS will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **mail**: recaria.org mail server management system
  - SSH-based Postfix/Dovecot mailbox provisioning (create, delete, password reset)
  - OpenDKIM setup and DKIM signing for outgoing emails
  - Local mode support (SSH-free for same-machine deployments)
  - Management command `sync_mailboxes` for bulk operations
  - DNS configuration reference (MX, SPF, DKIM, DMARC)
- **admin**: Enhanced mail administration UI
  - Real-time mail server status monitoring (Postfix, Dovecot, OpenDKIM)
  - Statistics dashboard (mailboxes, storage, pending provisions)
  - Quick actions for mailbox management
  - Searchable mailbox list with storage progress bars
- **auth**: Email verification page (`verify_email.html`)

### Changed
- **mail**: Updated SSH key path default to `id_ed25519`
- **mail**: Added local mode detection for mail.recaria.org

---

## [2.1.5] - 2025-12-06

### Added
- **auth**: Registration screens for web and mobile (terminal-style web UI, Flutter screen)
- **auth**: Password strength indicator for web UI and Flutter mobile

### Changed
- **mobile**: Auth screen links styled orange in Flutter
- **auth**: Registration simplified - removed name fields (email + password only)

---

## [2.1.4] - 2025-12-06

### Added
- **messenger**: File attachments with encrypted transfer
- **messenger**: Read receipts (per-user tracking)
- **messenger**: 38 new security tests (attachments + read receipts)
- **mobile**: Flutter Messenger UI with E2E encryption (`encryption_service.dart`)

---

## [2.1.3] - 2025-12-05

### Added
- **messenger**: Double Ratchet Algorithm for Perfect Forward Secrecy
  - Signal Protocol-compatible ratcheting (`double_ratchet.py`, 726 lines)
  - Per-message key rotation
  - 654 lines of Double Ratchet tests

---

## [2.1.2] - 2025-12-05

### Added
- **messenger**: 69 security tests across 5 test files
  - `test_encryption.py` (828 lines) - Cryptographic integrity
  - `test_integration.py` (891 lines) - End-to-end integration
  - `test_security.py` (628 lines) - Security penetration
  - `test_p2p.py` (405 lines) - P2P session lifecycle
  - `test_delivery.py` (631 lines) - Message delivery reliability
- **docs**: SECURITY_AUDIT.md with A rating

### Fixed
- **migration**: Removed RenameIndex from migration (indexes already named)

---

## [2.1.1] - 2025-12-05

### Added
- **messenger**: Complete E2E encrypted messenger module (10,344 lines, 49 files)
  - X25519 key exchange + AES-256-GCM encryption
  - Ed25519 digital signatures for message authentication
  - Hub relay and P2P direct transport (user-selectable)
  - Group chats with encrypted group key distribution
  - Message reactions, replies, and threading
  - Typing indicators
  - WebSocket consumer for real-time messaging
  - REST API (conversations, messages, keys, P2P, search)
  - DRF serializers and URL routing
- **mobile**: Flutter Messenger client
  - Chat screen, conversation list, settings, new conversation screen
  - Message bubble, message input, conversation tile, typing indicator widgets
  - Messenger models and service layer
  - Riverpod provider integration
- **web**: Messenger dashboard template

---

## [2.1.0] - 2025-12-05

### Added
- **p2p**: P2P mesh networking system (9,936 lines, 68 files)
  - mDNS discovery via Zeroconf (`discovery.py`, 405 lines)
  - WebSocket transport with HMAC-SHA256 signing (`transport.py`, 495 lines)
  - P2P manager with peer registry (`manager.py`, 469 lines)
  - P2P consumers, models, serializers, views, routing
  - WiFi Direct support (AP mode for router-less P2P)
- **sync**: Data synchronization engine
  - Version vector-based sync with conflict resolution (`models.py`, 812 lines)
  - SyncSession, SyncRecord, SyncConflict models
  - Sync init/push/pull/complete workflow
  - Sync middleware (`middleware.py`, 251 lines)
- **export**: Data export control system
  - Master kill switch for data exports
  - Module-level export permissions
  - DataExportSettings, DataExportLog models
  - Audit logging for all export operations
- **auth**: Identity enhancements
  - Account linking (Node to Hub)
  - Email verification flow
  - Offline login with cached credentials (`UserOfflineCache`)
  - Hub key management (RS256 key pairs)
  - Permission sync (Hub to Node)
  - WebSocket auth notifications consumer
- **mobile**: Flutter core infrastructure
  - AuthService, TokenStorage, ApiClient, auth interceptor
  - SyncService, OfflineQueue, SyncScreen
  - AppRouter with GoRouter
  - App theme, colors, environment config
  - Login screen, dashboard, settings, module cards
  - Version info utility
- **install**: SSH clone support with deploy key fallback
- **install**: Updated install script for v2.0 node architecture

### Fixed
- **install**: DB user password CREATE/ALTER pattern
- **node**: LOG_DIR path and REDIS_URL detection in settings

### Documentation
- Comprehensive TODO.md update with API inventory
- Consolidated TODO files with status tracking

---

## [2.0.2] - 2025-12-05

### Added
- **worker**: Celery worker and beat services for hub deployment
  - `unibos-worker.service` systemd service file
  - `unibos-beat.service` systemd service file
  - `celery_app.py` with health_check, cleanup, metrics tasks
  - Deploy integration for worker/beat lifecycle

---

## [2.0.1] - 2025-12-05

### Added
- **git**: Version branch push support in push-all command (`--with-version` flag)

### Fixed
- **deploy**: Updated deploy module and rocksteady config for hub
- **release**: VERSION.json display info sync in release pipeline
- **archive**: Excluded mobile SDK from version archives

### Documentation
- Version branch strategy documented (immutable snapshot model)
- README and RULES updated for v2.0.0 5-profile architecture

---

## [2.0.0] - 2025-12-05

### Breaking Changes
- **profiles**: Renamed `server` profile to `hub`, `prod` profile to `node`
- **repos**: Expanded from 3-repo to 5-repo architecture
  - Added `unibos-worker` for background task processing
  - `unibos-server` renamed to `unibos-hub`
  - `unibos-prod` renamed to `unibos` (node)

### Added
- **worker**: New worker profile with Celery integration
- **git**: Updated push-all command for 5 repos with per-repo .gitignore templates

### Changed
- 57 files renamed for hub/node/worker profile structure
- Deploy system updated for hub architecture
- Release pipeline updated for 5-repo push
- Per-repo .gitignore templates (`.gitignore.{profile}`)

### Documentation
- Consolidated TODO files with worker architecture details

---

## [1.1.6] - 2025-12-04

### Fixed
- **archive**: Excluded Flutter SDK from archive

---

## [1.1.5] - 2025-12-04

### Changed
- **mobile**: Added mobile gitignore rules (dev includes source, others exclude entirely)

---

## [1.1.4] - 2025-12-04

### Fixed
- **deploy**: Copy install.sh to staticfiles after collectstatic
- **install**: Uninstall confirmation reads from /dev/tty, lowercase text
- **tui**: Menu redraw cursor positioning
- **install**: Read from /dev/tty to support `curl | bash` pipe input
- **install**: Correct version parsing
- **install**: Lowercase text, system info display, proper menu selection

---

## [1.1.3] - 2025-12-03

### Added
- **install**: Arrow-key selectable menu to install script

---

## [1.1.2] - 2025-12-03

### Added
- **install**: Install/repair/uninstall modes to install script
- **django**: modules_core app for shared models
- **edge**: Raspberry Pi edge node installation system

---

## [1.1.0] - 2025-12-03

### Added
- **nodes**: Node Registry for P2P foundation
  - Node registration, heartbeat monitoring, discovery
  - Celery tasks for heartbeat processing
  - Django app with models, serializers, views, URLs

---

## [1.0.9] - 2025-12-03

### Changed
- Consolidated docs into TODO.md, removed docs directory

### Fixed
- Log paths updated from /var/log/unibos to data/logs
- Database user name corrected in config
- Deploy improvements (health endpoint, logging, config sync)
- Excluded SQL files and data directory from release archives
- Infrastructure improvements and deploy system fixes

---

## [1.0.1] - 2025-12-03

### Added
- **tui**: Alternate screen buffer, multi-server deploy, improved UX

---

## [1.0.0] - 2025-12-01

First stable release with new timestamp-based versioning system.
Migration from 533+ development iterations to semantic versioning.

### Added
- **cli**: 5-profile CLI architecture (dev, hub, manager, node, worker)
  - Help command with topic-based documentation
  - Release CLI commands for version management
  - Push-all command for multi-repo deployment
  - Interactive menu system with v527-style lowercase UI
  - Hybrid TUI/CLI mode for unibos-dev
- **tui**: Full-featured terminal UI framework
  - Profile-based inheritance (BaseTUI, DevTUI, HubTUI, etc.)
  - 3-section menu structure with vim-style navigation
  - i18n support (Turkish/English)
  - Version manager with new versioning system
  - Alternate screen buffer, terminal resize detection
- **packaging**: Modern pyproject.toml with pipx installation
- **deployment**: Rocksteady deployment automation (17-step pipeline)
- **django**: Module registry integration with Django settings
- **modules**: Module registry & discovery system
- **identity**: Node identity system with UUID persistence
- **platform**: Cross-platform detection (OS, arch, service management)
- **versioning**: Semantic versioning with timestamp build
  - ReleasePipeline class for automated releases
  - ChangelogManager for Conventional Commits
  - Archive system with .archiveignore
- **dev**: Uvicorn server support and changelog manager
- **birlikteyiz**: Background earthquake scheduler (5-min intervals) and EMSC WebSocket

### Changed
- Major 9-phase architecture restructuring (v533 core migration)
  - 2-layer core/modules design
  - TUI/CLI frameworks moved to core/clients/
  - Profiles moved to core/profiles/
  - All imports and references updated
- Template-based gitignore approach (per-repo templates)

### Fixed
- **web_ui**: Q+W solitaire shortcut now works on first press
- **tui**: Multiple rendering fixes (echo leak, corruption, sidebar, flicker)
- **tui**: Navigation fixes (circular nav, emoji spacing, resize detection)
- **tui**: Django server process management with PID tracking
- **cli**: PYTHONPATH and Django path corrections
- **packaging**: pipx installation and import path resolution

---

## [0.533.0] - 2025-11-15

Pre-semantic versioning era. 533 development iterations covering:

- 14 business modules built and integrated (currencies, wimm, wims, documents, personal_inflation, birlikteyiz, cctv, movies, music, recaria, restopos, solitaire, store, messenger)
- Django REST API backend with PostgreSQL
- Redis for cache, sessions, and WebSocket channel layer
- Django Channels for real-time WebSocket communication
- Celery for background task processing
- Web UI with terminal-style design (71 HTML templates)
- Administration panel with roles, departments, audit logs
- CCTV monitoring with camera grid and recording management
- OCR document scanning (Tesseract, PaddleOCR, EasyOCR)
- Currency and crypto tracking with portfolio management
- Earthquake monitoring (AFAD/Kandilli data sources)
- Restaurant POS, e-commerce, personal finance modules
- Solitaire multiplayer card game with live view
- Module architecture with v533 migration phases
