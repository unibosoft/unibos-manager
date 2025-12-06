# UNIBOS Changelog

All notable changes to UNIBOS will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]


---

## [2.1.5] - 2025-12-06

### Breaking Changes

- 💥 **git**: remove all archive/ from git tracking
  - ⚠️ Archive directory is now completely local-only
- 💥 **v533**: Complete core-based architecture migration
  - ⚠️ Major architectural restructure to 2-layer core/modules design

### Added

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

## [2.1.4] - 2025-12-06

### Breaking Changes

- 💥 **git**: remove all archive/ from git tracking
  - ⚠️ Archive directory is now completely local-only
- 💥 **v533**: Complete core-based architecture migration
  - ⚠️ Major architectural restructure to 2-layer core/modules design

### Added

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

## [2.1.3] - 2025-12-05

### Breaking Changes

- 💥 **git**: remove all archive/ from git tracking
  - ⚠️ Archive directory is now completely local-only
- 💥 **v533**: Complete core-based architecture migration
  - ⚠️ Major architectural restructure to 2-layer core/modules design

### Added

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

## [2.1.2] - 2025-12-05

### Breaking Changes

- 💥 **git**: remove all archive/ from git tracking
  - ⚠️ Archive directory is now completely local-only
- 💥 **v533**: Complete core-based architecture migration
  - ⚠️ Major architectural restructure to 2-layer core/modules design

### Added

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

## [2.1.1] - 2025-12-05

### Breaking Changes

- 💥 **git**: remove all archive/ from git tracking
  - ⚠️ Archive directory is now completely local-only
- 💥 **v533**: Complete core-based architecture migration
  - ⚠️ Major architectural restructure to 2-layer core/modules design

### Added

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

## [2.2.0] - 2025-12-05

### Messenger Module (E2E Encrypted Messaging with P2P Support)

- ✨ **End-to-End Encryption**: Complete E2E encryption implementation
  - X25519 key exchange for secure key agreement
  - AES-256-GCM for message encryption
  - Ed25519 for message signing/verification
  - HKDF for key derivation
  - Perfect Forward Secrecy with session keys

- ✨ **Transport Modes**: Flexible message delivery
  - Hub Relay: Messages routed through central server (default)
  - P2P Direct: Direct peer-to-peer with mDNS discovery
  - Hybrid: User-selectable per conversation

- ✨ **Backend Models**: Complete data layer
  - `UserEncryptionKey`: Device-based key management
  - `Conversation`: Group/direct chat support
  - `Participant`: Role-based participants (owner/admin/member)
  - `Message`: Encrypted messages with metadata
  - `MessageAttachment`: Encrypted file transfers
  - `MessageReaction`: Emoji reactions
  - `MessageReadReceipt`: Delivery/read tracking
  - `P2PSession`: P2P connection state management
  - `MessageDeliveryQueue`: Offline message queue

- ✨ **REST API Endpoints**:
  - `/api/v1/messenger/conversations/` - Conversation CRUD
  - `/api/v1/messenger/conversations/{id}/messages/` - Messages
  - `/api/v1/messenger/keys/` - Key management
  - `/api/v1/messenger/keys/generate/` - Key generation
  - `/api/v1/messenger/keys/public/{user_id}/` - Public key fetch
  - `/api/v1/messenger/p2p/connect/` - P2P initiation
  - `/api/v1/messenger/p2p/answer/` - P2P answer
  - `/api/v1/messenger/typing/` - Typing indicators
  - `/api/v1/messenger/search/` - Message search

- ✨ **WebSocket Consumer**: Real-time messaging
  - `MessengerConsumer` at `/ws/messenger/`
  - Real-time message delivery
  - Typing indicators broadcast
  - Read receipt notifications
  - P2P signaling (offer/answer/ice)

- ✨ **Flutter Mobile Client**: Cross-platform support
  - `MessengerService`: API client
  - Data models: Conversation, Message, Participant, etc.
  - UI screens (in progress)

---

## [2.1.0] - 2025-12-05

### Identity Enhancements (Latest)

- ✨ **Account Linking**: Link local Node accounts to Hub accounts
  - `AccountLink` model with verification code flow
  - `/api/v1/auth/link/init/` - Initialize linking with Hub credentials
  - `/api/v1/auth/link/verify/` - Verify with 6-digit code
  - `/api/v1/auth/link/status/` - Get/revoke account link
- ✨ **Email Verification**: Full email verification flow
  - `EmailVerificationToken` model with expiry
  - `/api/v1/auth/email/verify/request/` - Request verification
  - `/api/v1/auth/email/verify/confirm/` - Confirm with token
- ✨ **Permission Sync**: Hub to Node permission synchronization
  - `/api/v1/auth/permissions/sync/` - Sync permissions/roles
  - Stores synced permissions in AccountLink
- ✨ **WebSocket Auth Notifications**: Real-time auth events
  - `AuthNotificationConsumer` for `/ws/auth/notifications/`
  - Session created/revoked notifications
  - Security alerts (failed login attempts)
  - Account link status change notifications
- ✨ **RS256 Key Pairs**: Hub key management for JWT signing
  - `HubKeyPair` model with RSA generation
  - `/api/v1/auth/keys/` - List active keys
  - `/api/v1/auth/keys/create/` - Create new key pair
  - `/api/v1/auth/keys/primary/` - Get primary public key

### Multi-Platform Testing

- ✅ **iOS**: Tested on iPhone 16e Simulator (iOS 26.0)
- ✅ **Android**: Tested on Android 16 Emulator (API 36)
- ✅ **Offline Queue**: SharedPreferences persistence verified
- ✅ **Hub Auth**: JWT token exchange working on both platforms
- 🔧 **Fix**: Android version code overflow (`+20251204072502` → `+114`)

### Breaking Changes

- 💥 **git**: remove all archive/ from git tracking
  - ⚠️ Archive directory is now completely local-only
- 💥 **v533**: Complete core-based architecture migration
  - ⚠️ Major architectural restructure to 2-layer core/modules design

### Added

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

## [2.0.2] - 2025-12-05

### Breaking Changes

- 💥 **git**: remove all archive/ from git tracking
  - ⚠️ Archive directory is now completely local-only
- 💥 **v533**: Complete core-based architecture migration
  - ⚠️ Major architectural restructure to 2-layer core/modules design

### Added

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

## [2.0.1] - 2025-12-05

### Breaking Changes

- 💥 **git**: remove all archive/ from git tracking
  - ⚠️ Archive directory is now completely local-only
- 💥 **v533**: Complete core-based architecture migration
  - ⚠️ Major architectural restructure to 2-layer core/modules design

### Added

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

## [2.0.0] - 2025-12-05

### Breaking Changes

- 💥 **git**: remove all archive/ from git tracking
  - ⚠️ Archive directory is now completely local-only
- 💥 **v533**: Complete core-based architecture migration
  - ⚠️ Major architectural restructure to 2-layer core/modules design

### Added

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

## [1.1.6] - 2025-12-04

### Breaking Changes

- 💥 **git**: remove all archive/ from git tracking
  - ⚠️ Archive directory is now completely local-only
- 💥 **v533**: Complete core-based architecture migration
  - ⚠️ Major architectural restructure to 2-layer core/modules design

### Added

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

## [1.1.5] - 2025-12-04

### Breaking Changes

- 💥 **git**: remove all archive/ from git tracking
  - ⚠️ Archive directory is now completely local-only
- 💥 **v533**: Complete core-based architecture migration
  - ⚠️ Major architectural restructure to 2-layer core/modules design

### Added

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

## [1.1.4] - 2025-12-04

### Breaking Changes

- 💥 **git**: remove all archive/ from git tracking
  - ⚠️ Archive directory is now completely local-only
- 💥 **v533**: Complete core-based architecture migration
  - ⚠️ Major architectural restructure to 2-layer core/modules design

### Added

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

## [1.1.4] - 2025-12-03

### Breaking Changes

- 💥 **git**: remove all archive/ from git tracking
  - ⚠️ Archive directory is now completely local-only
- 💥 **v533**: Complete core-based architecture migration
  - ⚠️ Major architectural restructure to 2-layer core/modules design

### Added

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

## [1.1.4] - 2025-12-03

### Breaking Changes

- 💥 **git**: remove all archive/ from git tracking
  - ⚠️ Archive directory is now completely local-only
- 💥 **v533**: Complete core-based architecture migration
  - ⚠️ Major architectural restructure to 2-layer core/modules design

### Added

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

## [1.1.4] - 2025-12-03

### Breaking Changes

- 💥 **git**: remove all archive/ from git tracking
  - ⚠️ Archive directory is now completely local-only
- 💥 **v533**: Complete core-based architecture migration
  - ⚠️ Major architectural restructure to 2-layer core/modules design

### Added

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

## [1.1.4] - 2025-12-03

### Breaking Changes

- 💥 **git**: remove all archive/ from git tracking
  - ⚠️ Archive directory is now completely local-only
- 💥 **v533**: Complete core-based architecture migration
  - ⚠️ Major architectural restructure to 2-layer core/modules design

### Added

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

## [1.1.4] - 2025-12-03

### Breaking Changes

- 💥 **git**: remove all archive/ from git tracking
  - ⚠️ Archive directory is now completely local-only
- 💥 **v533**: Complete core-based architecture migration
  - ⚠️ Major architectural restructure to 2-layer core/modules design

### Added

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

## [1.1.3] - 2025-12-03

### Breaking Changes

- 💥 **git**: remove all archive/ from git tracking
  - ⚠️ Archive directory is now completely local-only
- 💥 **v533**: Complete core-based architecture migration
  - ⚠️ Major architectural restructure to 2-layer core/modules design

### Added

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

## [1.1.2] - 2025-12-03

### Breaking Changes

- 💥 **git**: remove all archive/ from git tracking
  - ⚠️ Archive directory is now completely local-only
- 💥 **v533**: Complete core-based architecture migration
  - ⚠️ Major architectural restructure to 2-layer core/modules design

### Added

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

## [1.1.2] - 2025-12-03

### Breaking Changes

- 💥 **git**: remove all archive/ from git tracking
  - ⚠️ Archive directory is now completely local-only
- 💥 **v533**: Complete core-based architecture migration
  - ⚠️ Major architectural restructure to 2-layer core/modules design

### Added

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

## [1.2.0] - 2025-12-03

### Breaking Changes

- 💥 **git**: remove all archive/ from git tracking
  - ⚠️ Archive directory is now completely local-only
- 💥 **v533**: Complete core-based architecture migration
  - ⚠️ Major architectural restructure to 2-layer core/modules design

### Added

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

## [1.1.0] - 2025-12-03

### Breaking Changes

- 💥 **git**: remove all archive/ from git tracking
  - ⚠️ Archive directory is now completely local-only
- 💥 **v533**: Complete core-based architecture migration
  - ⚠️ Major architectural restructure to 2-layer core/modules design

### Added

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

## [1.0.10] - 2025-12-03

### Added

- ✨ **middleware**: implement NodeIdentityMiddleware for multi-node architecture
- ✨ **middleware**: implement P2PDiscoveryMiddleware for peer discovery headers
- ✨ **middleware**: implement MaintenanceModeMiddleware with graceful 503 handling
- ✨ **health**: comprehensive health endpoints system
  - `/health/` - Full comprehensive health check
  - `/health/quick/` - Minimal overhead (middleware bypass)
  - `/health/db/` - PostgreSQL connectivity
  - `/health/redis/` - Redis connectivity
  - `/health/celery/` - Celery worker status
  - `/health/channels/` - Django Channels/WebSocket
  - `/health/node/` - Node identity and capabilities
  - `/health/full/` - Aggregated service status
  - `/health/ready/` - Kubernetes readiness probe
  - `/health/live/` - Kubernetes liveness probe

### Changed

- ♻️ **middleware**: enhance HealthCheckMiddleware with bypass paths
- ♻️ **settings**: add new middleware to Django MIDDLEWARE stack

---

## [1.0.9] - 2025-12-03

### Breaking Changes

- 💥 **git**: remove all archive/ from git tracking
  - ⚠️ Archive directory is now completely local-only
- 💥 **v533**: Complete core-based architecture migration
  - ⚠️ Major architectural restructure to 2-layer core/modules design

### Added

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

## [1.0.8] - 2025-12-03

### Changed

- ♻️ **docs**: consolidate all documentation into TODO.md
- ♻️ **docs**: archive 32 docs files to archive/docs_backup_20251203/
- ♻️ **docs**: remove docs/ directory (single source of truth in TODO.md)
- 📝 **readme**: comprehensive update with current features
- 📝 **todo**: rewrite with better organization (11 sections, table of contents)

---

## [1.0.7] - 2025-12-03

### Fixed

- 🐛 **logs**: standardize log paths from /var/log/unibos to data/logs/
- 🐛 **deploy**: update deploy.sh, unibos.service, Dockerfile for new log paths
- 🐛 **server**: update server/manager TUI log path references

---

## [1.0.6] - 2025-12-03

### Fixed

- 🐛 **archive**: exclude data/ directory from release archives
- 🐛 **archive**: exclude .sql files from release archives
- 🐛 **config**: correct database user name (unibos_user)

---

## [1.0.5] - 2025-12-03

### Fixed

- 🐛 **deploy**: correct health endpoint path
- 🐛 **deploy**: config sync improvements

---

## [1.0.4] - 2025-12-03

### Fixed

- 🐛 **deploy**: infrastructure improvements

---

## [1.0.3] - 2025-12-03

### Fixed

- 🐛 **prometheus**: fix metrics export port conflicts

---

## [1.0.2] - 2025-12-03

### Changed

- 🔧 **web**: update gunicorn config and requirements

---

## [1.0.1] - 2025-12-03

### Changed

- 🔧 **archiveignore**: remove deprecated file

---

## [1.0.0] - 2025-12-01

### Breaking Changes

- 💥 **git**: remove all archive/ from git tracking
  - Archive directory is now completely local-only
- 💥 **v533**: Complete core-based architecture migration
  - Major architectural restructure to 2-layer core/modules design

### Added

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

## [1.0.7] - 2025-12-03

### Breaking Changes

- 💥 **git**: remove all archive/ from git tracking
  - ⚠️ Archive directory is now completely local-only
- 💥 **v533**: Complete core-based architecture migration
  - ⚠️ Major architectural restructure to 2-layer core/modules design

### Added

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

## [1.0.6] - 2025-12-03

### Breaking Changes

- 💥 **git**: remove all archive/ from git tracking
  - ⚠️ Archive directory is now completely local-only
- 💥 **v533**: Complete core-based architecture migration
  - ⚠️ Major architectural restructure to 2-layer core/modules design

### Added

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

## [1.0.5] - 2025-12-03

### Breaking Changes

- 💥 **git**: remove all archive/ from git tracking
  - ⚠️ Archive directory is now completely local-only
- 💥 **v533**: Complete core-based architecture migration
  - ⚠️ Major architectural restructure to 2-layer core/modules design

### Added

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

## [1.0.4] - 2025-12-03

### Breaking Changes

- 💥 **git**: remove all archive/ from git tracking
  - ⚠️ Archive directory is now completely local-only
- 💥 **v533**: Complete core-based architecture migration
  - ⚠️ Major architectural restructure to 2-layer core/modules design

### Added

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

## [1.0.3] - 2025-12-03

### Breaking Changes

- 💥 **git**: remove all archive/ from git tracking
  - ⚠️ Archive directory is now completely local-only
- 💥 **v533**: Complete core-based architecture migration
  - ⚠️ Major architectural restructure to 2-layer core/modules design

### Added

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

## [1.0.2] - 2025-12-03

### Breaking Changes

- 💥 **git**: remove all archive/ from git tracking
  - ⚠️ Archive directory is now completely local-only
- 💥 **v533**: Complete core-based architecture migration
  - ⚠️ Major architectural restructure to 2-layer core/modules design

### Added

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

## [1.0.1] - 2025-12-03

### Breaking Changes

- 💥 **git**: remove all archive/ from git tracking
  - ⚠️ Archive directory is now completely local-only
- 💥 **v533**: Complete core-based architecture migration
  - ⚠️ Major architectural restructure to 2-layer core/modules design

### Added

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

## [1.0.1] - 2025-12-03

### Added

- ✨ **tui**: add alternate screen buffer to prevent terminal scroll pollution
- ✨ **tui**: add scroll navigation keys (PageUp/PageDown, g/G for top/bottom)
- ✨ **tui**: add live footer clock updates during submenu and streaming operations
- ✨ **tui**: add terminal resize support during streaming with full redraw
- ✨ **tui**: add spinner animation during long-running operations
- ✨ **deploy**: add multi-server support (rocksteady/bebop) with hierarchical menu
- ✨ **colors**: add BG_ORANGE_DIM for inactive sidebar selection state

### Changed

- ♻️ **tui**: use _navigation_redraw() instead of render() to prevent blink on submenu exit
- ♻️ **tui**: buffer-based rendering in sidebar and content components
- ♻️ **tui**: keep cursor hidden during navigation to prevent character blink
- ♻️ **deploy**: use sudo rm -rf for locked venv files during deployment

### Fixed

- 🐛 **tui**: fix sidebar not dimming on first ENTER (content area focus)
- 🐛 **tui**: fix blink when transitioning between sidebar and submenu
- 🐛 **tui**: fix header disappearing on terminal resize during streaming
- 🐛 **tui**: fix footer blink on resize by resetting update timer
- 🐛 **tui**: fix cursor blink in header/footer/content areas
- 🐛 **deploy**: fix EXISTS check matching NOT_EXISTS (changed to YES/NO)

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
