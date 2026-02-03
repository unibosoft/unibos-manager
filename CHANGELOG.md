# UNIBOS Changelog

All notable changes to UNIBOS will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]


---

## [2.1.5] - 2026-02-03

### Breaking Changes

- 💥 **git**: remove all archive/ from git tracking
  - ⚠️ Archive directory is now completely local-only
- 💥 **v533**: Complete core-based architecture migration
  - ⚠️ Major architectural restructure to 2-layer core/modules design

### Added

- ✨ enhance mail server management with local mode and admin dashboard
- ✨ recaria.org mail server management system
- ✨ improve password strength indicator in web UI
- ✨ make first_name and last_name optional in registration
- ✨ add registration screens for web and mobile
- ✨ **messenger**: file attachments and read receipts with 38 security tests
- ✨ **messenger**: file attachments and read receipts with 38 security tests
- ✨ **mobile**: Flutter Messenger UI with E2E encryption
- ✨ Double Ratchet Algorithm for Perfect Forward Secrecy
- ✨ **messenger**: Double Ratchet Algorithm for Perfect Forward Secrecy
- ✨ Messenger module with E2E encryption, P2P support, WebSocket consumer, Flutter client
- ✨ P2P mesh networking, sync engine, export control, Flutter sync client
- ✨ add SSH clone support with deploy key fallback
- ✨ update install script for v2.0 node architecture
- ✨ add Celery worker and beat services for hub deployment
- ✨ implement Celery worker and beat services for hub
- ✨ add version branch push support to push-all command
- ✨ add arrow-key selectable menu to install script
- ✨ add install/repair/uninstall modes to install script
- ✨ add install/repair/uninstall modes to install script
- ✨ add modules_core app, fix gitignore paths
- ✨ add modules_core Django app for shared models
- ✨ **edge**: Raspberry Pi edge node installation system
- ✨ **edge**: add Raspberry Pi edge node installation system
- ✨ **nodes**: Node Registry for P2P foundation
- ✨ **nodes**: add Celery tasks for node heartbeat monitoring
- ✨ **nodes**: add Node Registry Django app for P2P foundation
- ✨ **tui**: alternate screen buffer, multi-server deploy, improved UX
- ✨ **cli**: add help command and release CLI
- ✨ **cli**: add comprehensive help command with topic-based documentation
- ✨ add release CLI commands for version management
- ✨ **dev**: enhance dev profile with uvicorn server and changelog manager
- ✨ **birlikteyiz**: add background earthquake scheduler and EMSC WebSocket
- ✨ **tui**: enhance version manager with new versioning system support
- ✨ **v0.534.0**: 4-tier CLI architecture and comprehensive updates
- ✨ **cli**: simplify CLI usage and create unibos-manager command
- ✨ **tui**: transform TUI to display all content in right panel
- ✨ **git**: add push-all command for 3-repo architecture
- ✨ **phase1**: implement three-CLI architecture with multi-repo deployment
- ✨ **cli**: implement v527 EXACT ui/ux with all lowercase
- ✨ **cli**: implement full v527 UI/UX layout + version v0.534.0
- ✨ **cli**: implement hybrid mode for unibos-dev
- ✨ **cli**: add interactive menu base system
- ✨ **cli**: port v527 interactive CLI UI foundation
- ✨ **cli**: add --setup flag to deploy rocksteady command
- ✨ **packaging**: add modern pyproject.toml for unified CLI packaging
- ✨ **deployment**: add pipx installation for unibos-server
- ✨ **deployment**: update rocksteady deployment for v1.0.0
- ✨ **django**: integrate module registry with Django settings
- ✨ **modules**: implement module registry & discovery system
- ✨ **identity**: implement node identity & persistence system
- ✨ **cli**: complete service management implementation
- ✨ **platform**: add cross-platform service management
- ✨ **versioning**: implement semantic versioning system
- ✨ **platform**: add platform detection system with psutil integration
- ✨ **cli**: add setup files for 3-tier CLI architecture
- ✨ **cli**: create server CLI for rocksteady management
- ✨ **cli**: create production CLI for end users
- ✨ **cli**: rename cli to cli-dev for developer commands
- ✨ **cli**: push to both main and v533 branches
- ✨ **git**: enhance dev/prod workflow safety
- ✨ **devops**: implement dev/prod git workflow with CLI automation
- ✨ **v533**: Complete Priority 1 & 2 - CLI Tool + Module Path Migration
- ✨ **v533**: Complete module architecture migration - Phase 2.3
- ✨ **phase2.3**: migrate module FileFields to new v533 data paths
- ✨ **platform**: add Phase 3 foundation and TODO
- ✨ **architecture**: v533 migration Phase 1 & 2 completed
- ✨ **sdk**: add storage path management to UnibosModule

### Changed

- ♻️ clean up web UI sidebar and remove unused tools
- 💄 improve password strength indicator in Flutter mobile
- 💄 remove gray password strength bar background in web UI
- ♻️ simplify registration by removing name fields
- 💄 make auth screen links orange in Flutter mobile
- ♻️ update repo structure for 5-repo architecture
- ♻️ rename profiles (server→hub, prod→node) and add worker
- 💄 lowercase help documentation
- 💄 **cli**: convert help documentation to lowercase
- ♻️ **system**: improve admin views and context processors
- ♻️ **tui**: improve TUI architecture and i18n system
- ♻️ **tui**: atomic navigation redraw to prevent flicker
- ♻️ **tui**: remove redundant navigation hints from content area
- ♻️ **tui**: simplify version manager content area UX
- 💄 **tui**: convert version manager to lowercase (v527 style)
- ♻️ **gitignore**: implement Approach 1 - templates only in dev repo
- ♻️ **core**: Phase 9 - Update configuration files
- ♻️ **core**: Phase 8 - Update all imports and references
- ♻️ remove old core/cli (replaced by core/clients/cli/framework/)
- ♻️ **core**: Phase 6-7 - TUI/CLI frameworks + profiles migration
- ♻️ **core**: Phase 1-5 - Major architecture restructuring
- ♻️ **ignore**: update all ignore files for v533 architecture

### Fixed

- 🐛 remove RenameIndex from migration (indexes already named)
- 🐛 update DB user password if already exists
- 🐛 node settings LOG_DIR and REDIS detection
- 🐛 update deploy module and rocksteady config for hub
- 🐛 update VERSION.json display info in release pipeline
- 🐛 exclude mobile SDK from version archives
- 🐛 update deploy system for hub architecture
- 🐛 update release pipeline and manager gitignore for 5-repo
- 🐛 exclude flutter sdk from archive
- 🐛 copy install.sh to staticfiles after collectstatic in deploy
- 🐛 uninstall confirmation reads from /dev/tty, lowercase text
- 🐛 menu redraw cursor positioning
- 🐛 read from /dev/tty to support curl pipe input
- 🐛 correct version parsing in install script
- 🐛 install script with lowercase text, system info display, and proper menu selection
- 🐛 correct gitignore paths (core/web → core/clients/web)
- 🐛 update log paths from /var/log/unibos to data/logs
- 🐛 correct database user name in config (unibos_user not unibos_db_user)
- 🐛 deploy improvements - correct health endpoint, logging to data dir, config sync
- 🐛 exclude sql files from release archives
- 🐛 exclude data directory from release archives
- 🐛 infrastructure improvements and documentation updates
- 🐛 deploy system improvements and prometheus fix
- 🐛 **web_ui**: Q+W solitaire shortcut now works on first press
- 🐛 **tui**: disable terminal echo during render to prevent escape sequence leak
- 🐛 **tui**: prevent render corruption with rendering lock and higher debounce
- 🐛 **tui**: remove line-above clear that was erasing sidebar
- 🐛 **tui**: aggressive input flush and line clear in footer
- 🐛 **tui**: flush input buffer before redrawing header/footer
- 🐛 **tui**: redraw header/footer after sidebar navigation
- 🐛 **tui**: full render on section change to preserve header
- 🐛 **tui**: add terminal resize detection to version manager submenu
- 🐛 **tui**: fix version manager submenu navigation blinking
- 🐛 **tui**: implement v527-style navigation for sidebar and submenus
- 🐛 **tui**: implement circular navigation and fix content area input
- 🐛 **tui**: implement v527-based emoji spacing and navigation fixes
- 🐛 **tui**: improve Django server process management with PID tracking
- 🐛 **tui**: fix Enter key handling by adding missing show_command_output method
- 🐛 **cli**: restore splash screen and fix syntax errors in production CLI
- 🐛 **cli**: correct PYTHONPATH and Django paths for TUI functionality
- 🐛 **tui**: correct ModuleInfo attribute access in platform_modules
- 🐛 **tui**: improve dev_shell and platform_identity actions
- 🐛 **tui**: fix all TUI menu actions and update Django paths
- 🐛 **tui**: resolve interactive mode path issues and improve action handling
- 🐛 **packaging**: resolve pipx installation and import path issues
- 🐛 **setup**: update setup.py entry points for profiles structure
- 🐛 **cli**: implement v527 exact navigation structure
- 🐛 **cli**: complete lowercase conversion (final 2 descriptions)
- 🐛 **cli**: navigation wrapping + complete lowercase conversion
- 🐛 **cli**: fix corrupted spinner characters in terminal.py
- 🐛 **cli**: rename CLI dirs to Python-compatible names
- 🐛 **cli**: use Django venv Python instead of CLI Python
- 🐛 **cli**: use sys.executable instead of hardcoded 'python' command
- 🐛 **cli**: use git root for project path detection
- 🐛 **cli**: remove dangerous git add -A from push-prod command
- 🐛 **birlikteyiz**: Change default time range to 30 days for earthquake map
- 🐛 **v533**: Add db_table meta to core models for backward compatibility
- 🐛 **v533**: Custom migration for JSONB→ArrayField + emergency settings update
- 🐛 **version**: Restore VERSION.json and fix v533 display in web UI
- 🐛 **backup**: Replace Django dumpdata with pg_dump for database backups

### Documentation

- 📝 rewrite CHANGELOG and comprehensively update README
- 📝 Messenger security tests and documentation update
- 📝 Messenger security tests and documentation update
- 📝 comprehensive TODO.md update with API inventory
- 📝 consolidate TODO files with status tracking
- 📝 document version branch strategy (immutable snapshot)
- 📝 update README, RULES for v2.0.0 5-profile architecture
- 📝 consolidate TODO files, update worker architecture
- 📝 **todo**: mark Node Registry as completed
- 📝 update README and CHANGELOG with current features
- 📝 **changelog**: add entries for Q+W fix, birlikteyiz scheduler, TUI improvements
- 📝 update RULES.md and CLI splash screen
- 📝 add comprehensive TUI server management documentation
- 📝 **platform**: add comprehensive platform detection documentation
- 📝 **cli**: add comprehensive three-tier CLI architecture documentation
- 📝 **dev-prod**: improve dev/prod workflow documentation and rules
- 📝 add comprehensive git workflow usage guide
- 📝 add comprehensive guides for setup, CLI, development, and deployment
- 📝 reorganize into 3-category structure (rules/guides/design)
- 📝 **planning**: Organize roadmaps and create comprehensive future planning

### Maintenance

- 🔧 release v2.0.1
- 🔧 release v2.0.0
- 🔧 add mobile gitignore rules - dev includes source, others exclude entirely
- 🔧 rollback version to v1.1.1, update raspberry roadmap
- 🔧 consolidate docs into TODO.md, remove docs directory
- 🔧 release v1.0.1
- 🔧 remove deprecated .archiveignore file
- 🔧 **web**: update gunicorn config and requirements
- 🔧 release v1.0.0
- 🔧 release v1.0.0
- 🔧 release v1.0.0
- 🔧 add archive to all releases
- 🔧 release v1.0.0
- 🔧 release v1.0.0
- 🔧 fix branch naming format
- 🔧 test release/v branch format
- 🔧 pipeline multi-repo test
- 🔧 release v1.0.0
- 🔧 test release pipeline
- 🔧 migrate to v1.0.0 with timestamp-based versioning
- 🔧 **dev**: restore dev gitignore
- 🔧 **prod**: update gitignore for prod repo
- 🔧 **manager**: update gitignore for manager repo
- 🔧 **server**: update gitignore for server repo
- 🔧 **dev**: restore dev gitignore template
- 🔧 **prod**: configure gitignore for prod repo
- 🔧 **server**: configure gitignore for server repo
- 🔧 **manager**: configure gitignore for manager repo
- 🔧 clean up test files after TUI fix verification
- 🔧 **setup**: update for v1.0.0 stable release
- 🔧 **git**: remove SQL file from tracking
- 🔧 **archive**: remove erroneously committed v532 legacy structures
- 🔧 clean up root directory - move deprecated files to archive
- 🔧 configure egg-info to build in build/ directory
- 🔧 update .rsyncignore for platform/ structure

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
