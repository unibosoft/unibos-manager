# UNIBOS Changelog

All notable changes to UNIBOS will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

---

## [1.0.0] - 2025-11-15

### 🚀 First Public Release - "Foundation"
**Production-ready personal operating system with modular architecture**

### Added

- **Service Management (Phase 1.3)**
  - Cross-platform service manager (systemd, launchd, supervisor)
  - `unibos stop` command with graceful/force modes
  - `unibos-server service` commands (start, stop, restart, status)
  - Automatic service manager detection
  - Support for macOS (launchd), Linux (systemd), Supervisor fallback

- **Node Identity & Persistence (Phase 1.4)**
  - Unique UUID for each UNIBOS instance
  - Node type auto-detection (CENTRAL, LOCAL, EDGE, DESKTOP)
  - Platform-integrated capability detection
  - Persistent identity storage (`data/core/node.json`)
  - `unibos node info` - Show node identity and capabilities
  - `unibos node register` - Register with central server
  - `unibos node peers` - List peer nodes (placeholder)

- **Module System (Phase 2.1 & 2.2)**
  - Auto-discovery of 13 modules from `modules/` directory
  - Dynamic module loading with `.enabled` marker system
  - Module metadata from `module.json` files
  - `unibos module list` - List all/enabled/available modules
  - `unibos module info <name>` - Detailed module information
  - `unibos module enable/disable <name>` - Runtime module control
  - `unibos module stats` - Module statistics
  - Django integration with dynamic INSTALLED_APPS
  - Git root detection for pipx installations
  - UNIBOS_ROOT environment variable support

- **13 Production Modules**
  - 🌍 **birlikteyiz** - Emergency mesh network & earthquake alerts
  - 📄 **documents** - OCR & document management with AI
  - 💱 **currencies** - Cryptocurrency & currency tracking
  - 📈 **personal_inflation** - Personal inflation tracking
  - 🎮 **recaria** - Medieval MMORPG (Ultima Online inspired)
  - 📹 **cctv** - Security camera management
  - 🎬 **movies** - Movie & TV series collection
  - 🎵 **music** - Music collection with Spotify integration
  - 🍽️ **restopos** - Restaurant POS system
  - 💰 **wimm** - Personal finance tracker
  - 📦 **wims** - Inventory management
  - 🃏 **solitaire** - Card game with multiplayer
  - 🛒 **store** - Marketplace integration

### Changed
- Module loading now dynamic based on `.enabled` status
- Django settings use ModuleRegistry for INSTALLED_APPS
- Improved version management with semantic versioning
- Updated archive structure (`archive/versions/old/` for pre-1.0.0)

### Technical Details
- **CLI Tools**: 3 distinct CLIs (unibos, unibos-dev, unibos-server)
- **Module Discovery**: Automatic scan of `modules/` directory
- **Platform Support**: macOS, Linux, Windows, Raspberry Pi
- **Python**: 3.9, 3.10, 3.11, 3.12, 3.13
- **Installation**: pipx for isolated environments
- **Architecture**: Modular, extensible, production-ready

### Breaking Changes
- None (first public release)

### Migration Notes
- Pre-1.0.0 versions (v0.1.0-v0.533.0) archived in `archive/versions/old/`
- 533 development iterations leading to this release
- All development history preserved in git

### Documentation
- Module system documentation
- Node identity guide
- Service management guide
- Installation and deployment guides
- Semantic versioning adoption

---

## [0.533.0] - 2025-11-15

### 🎯 Pre-Release Milestone - "Architect"
**Three-tier CLI architecture complete and production-ready**

### Added
- **Three-tier CLI Architecture**
  - `unibos` - Production CLI for end users
  - `unibos-dev` - Developer CLI for development workflow
  - `unibos-server` - Server CLI for Rocksteady management
  - Security model: Dev/Server CLIs excluded from production

- **Platform Detection System**
  - Cross-platform OS detection (macOS, Linux, Windows, Raspberry Pi)
  - Hardware specification detection (CPU, RAM, disk, GPU)
  - Device type classification (server, desktop, edge, raspberry_pi)
  - Raspberry Pi model detection via `/proc/device-tree/model`
  - Capability detection (GPU, camera, GPIO, LoRa)
  - Network information (hostname, local IP)
  - Platform suitability checks for server/edge deployments

- **CLI Commands**
  - `unibos status` - System health check
  - `unibos start` - Start UNIBOS services
  - `unibos logs` - View system logs
  - `unibos platform` - Platform information (human/JSON/verbose)
  - `unibos-dev dev run` - Django development server
  - `unibos-dev deploy` - Deployment commands
  - `unibos-dev git` - Git workflow management
  - `unibos-dev db` - Database operations
  - `unibos-server health` - Comprehensive health checks
  - `unibos-server stats` - Performance statistics

- **Documentation**
  - Three-tier CLI architecture guide
  - Platform detection documentation
  - Installation and testing guides
  - Security model documentation

### Changed
- Reorganized CLI structure from single to three-tier architecture
- Updated `.prodignore` and `.rsyncignore` for security
- Migrated to Python module naming (underscores instead of hyphens)

### Technical Details
- Dependencies: click>=8.0.0, psutil>=5.9.0, zeroconf>=0.80.0
- Python support: 3.9, 3.10, 3.11, 3.12, 3.13
- Installation: pipx for isolated environments
- Entry points: 3 separate console scripts

---

## Development History (Pre-Release)

### [0.1.0 - 0.533.0] - 2024-XX to 2025-11-15
**533 development iterations**

This period represents the complete development history before the first public release.
Detailed history preserved in:
- `archive/versions/pre-release/README.md`
- Git commit history
- `development_logs/` directory

### Major Milestones

#### Phase 0: Initial Development (v0.1.0 - v0.100.0)
- Django backend setup
- PostgreSQL + Redis integration
- Initial module structure
- First deployment to Rocksteady server

#### Phase 1: Module Development (v0.101.0 - v0.300.0)
- Birlikteyiz earthquake monitoring app
- CCTV surveillance module
- Recaria MMORPG game infrastructure
- Wimm/Wims management modules
- Music, Movies, Solitaire modules

#### Phase 2: Architecture Refinement (v0.301.0 - v0.450.0)
- CLI development begins
- Version management system
- Git workflow (dev/prod separation)
- Deployment automation (Rocksteady)

#### Phase 3: Monorepo Restructuring (v0.451.0 - v0.532.0)
- Apps directory structure (cli, web, mobile)
- Modules organization
- Documentation restructuring
- Archive system implementation
- Tools and scripts organization

#### Phase 4: v533 Architecture (v0.533.0)
- Three-tier CLI separation
- Platform detection foundation
- Production-ready state
- Security model implementation
- Comprehensive documentation

### Key Features Implemented During Pre-Release

#### Backend
- Django web framework
- PostgreSQL database
- Redis caching and queuing
- Celery async task processing
- REST API endpoints
- WebSocket support

#### Frontend
- Django templates
- HTMX dynamic updates
- Responsive design
- Document OCR and analysis

#### Mobile
- Flutter birlikteyiz app
- Real-time earthquake alerts
- Location-based features

#### Infrastructure
- Nginx reverse proxy
- Gunicorn WSGI server
- Systemd service management
- Automated deployment scripts
- Database backup system

#### Development Tools
- Version management CLI
- Git workflow automation
- Archive system
- Development logging
- Testing infrastructure

---

## Version History Notes

### Pre-Release to v1.0.0 Transition

The transition from v0.533.0 to v1.0.0 marks:
- **First public release**
- **Semantic versioning adoption**
- **Production-ready declaration**
- **API stability commitment**

### Version Numbering Strategy

Starting from v1.0.0, UNIBOS follows semantic versioning:

- **MAJOR (X.0.0)**: Breaking changes, API incompatibility
- **MINOR (0.X.0)**: New features, backward compatible
- **PATCH (0.0.X)**: Bug fixes, backward compatible

### Release Types

- `development`: Pre-release development versions
- `alpha`: Early testing versions
- `beta`: Feature-complete testing versions
- `rc`: Release candidates
- `stable`: Production-ready releases

---

## Future Roadmap

### v1.1.0 - Service Management
- Cross-platform service management
- systemd/launchd/Windows Services support
- Service start/stop/restart commands

### v1.2.0 - Module System
- Module metadata (JSON)
- Module enable/disable
- Module dependency management
- Module discovery

### v1.3.0 - P2P Network Foundation
- mDNS node discovery
- REST API for P2P communication
- WebSocket real-time updates
- Node registration and management

### v1.4.0 - Deployment Targets
- Raspberry Pi deployment automation
- Desktop installation (macOS, Linux, Windows)
- Configuration management

### v2.0.0 - Advanced P2P Features
- LoRa mesh networking
- WebRTC peer-to-peer
- Distributed data sync
- Edge computing capabilities

---

## Links

- **Homepage**: https://github.com/berkhatirli/unibos
- **Documentation**: https://github.com/berkhatirli/unibos/wiki
- **Issues**: https://github.com/berkhatirli/unibos/issues
- **PyPI**: https://pypi.org/project/unibos/ (Coming soon)

---

**Legend:**
- 🎯 Milestone
- ✅ Complete
- 🔄 In Progress
- 📋 Planned
- ⚠️ Breaking Change
- 🐛 Bug Fix
- 🚀 New Feature
- 📝 Documentation
