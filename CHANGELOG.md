# UNIBOS Changelog

All notable changes to UNIBOS will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]




---

## [1.0.0] - 2025-12-03

### Breaking Changes

- 💥 **git**: remove all archive/ from git tracking
  - ⚠️ Archive directory is now completely local-only
- 💥 **v533**: Complete core-based architecture migration
  - ⚠️ Major architectural restructure to 2-layer core/modules design

### Added

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

## [1.0.0] - 2025-12-03

### Breaking Changes

- 💥 **git**: remove all archive/ from git tracking
  - ⚠️ Archive directory is now completely local-only
- 💥 **v533**: Complete core-based architecture migration
  - ⚠️ Major architectural restructure to 2-layer core/modules design

### Added

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

## [1.0.0] - 2025-12-03

### Breaking Changes

- 💥 **git**: remove all archive/ from git tracking
  - ⚠️ Archive directory is now completely local-only
- 💥 **v533**: Complete core-based architecture migration
  - ⚠️ Major architectural restructure to 2-layer core/modules design

### Added

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
