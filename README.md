# UNIBOS - Universal Integrated Backend and Operating System

> **v533** - Core-based modular platform with P2P architecture, multi-platform support, and plugin marketplace foundation

## 🗂️ Project Structure (v533)

```
unibos/
├── core/                          # Core system infrastructure
│   ├── backend/                   # Django application (main runtime)
│   ├── models/                    # Shared domain models (Django app)
│   ├── system/                    # System modules
│   │   ├── authentication/        # User auth & permissions
│   │   ├── users/                 # User management
│   │   ├── web_ui/                # Web interface
│   │   ├── common/                # Shared utilities
│   │   ├── administration/        # System admin
│   │   ├── logging/               # Audit logs
│   │   └── version_manager/       # Version control
│   ├── instance/                  # P2P instance identity
│   ├── p2p/                       # P2P communication (planned)
│   ├── sync/                      # Sync engine (planned)
│   ├── services/                  # Core services
│   └── sdk/                       # Multi-platform SDK
│
├── modules/                       # Business modules (13 modules)
│   ├── currencies/                # Currency & crypto tracking
│   ├── wimm/                      # Financial management
│   ├── wims/                      # Inventory management
│   ├── documents/                 # OCR & document scanning
│   ├── personal_inflation/        # Personal CPI tracker
│   ├── birlikteyiz/              # Earthquake alerts
│   ├── cctv/                      # Camera monitoring
│   ├── recaria/                   # Recipe management
│   ├── movies/                    # Media library
│   ├── music/                     # Music player
│   ├── restopos/                  # Restaurant POS
│   ├── solitaire/                 # Multiplayer game
│   └── store/                     # E-commerce
│
├── docs/                          # Documentation
│   ├── architecture/              # System design
│   ├── development/               # Dev guides
│   ├── features/                  # Feature docs
│   └── deployment/                # Deployment guides
│
├── tools/                         # Development tools
│   └── scripts/                   # Automation scripts
│
├── data/                          # Runtime data (gitignored)
│
├── archive/                       # Version archives & docs
│   ├── versions/                  # v529-v533 archives
│   └── docs/                      # Historical documentation
│
├── ARCHITECTURE.md                # v533 architecture guide
├── RULES.md                       # Project rules & workflow
└── README.md                      # This file
```

## ⚡ quick start

### terminal ui (cli)
```bash
python apps/cli/src/main.py
```

### web backend
```bash
cd apps/web/backend
python manage.py runserver
```

### mobile app
```bash
cd apps/mobile/birlikteyiz
flutter run
```

## 📋 requirements

### minimum
- python 3.8+
- 2GB RAM minimum (8GB recommended)
- 10GB disk space
- postgresql 15+ (mandatory - sqlite not supported)
- Redis 7+ (optional, for caching)

### recommended
- python 3.11+
- postgresql 15+
- redis 7+
- docker (for containerized deployment)

## 📖 documentation

comprehensive documentation is organized in `docs/`:

- **architecture/**: system design, api documentation, project structure
- **development/**: installation guide, development setup, troubleshooting
- **features/**: feature guides and module documentation
- **deployment/**: deployment guides and server setup
- **claude/**: ai assistant instructions and technical specs

## 🚀 key features

- **terminal ui**: full-featured cli interface with curses
- **web backend**: django rest framework api
- **mobile apps**: flutter cross-platform applications
- **monorepo**: organized structure for multiple applications
- **version management**: automated versioning and archiving
- **postgresql**: production-ready database architecture
- **modular design**: independent yet integrated components

## 🛠️ development

see [docs/development/DEVELOPMENT.md](docs/development/DEVELOPMENT.md) for detailed development instructions.

## 📦 modules

- **authentication**: user management and permissions
- **currencies**: real-time exchange rates and crypto tracking
- **documents**: ocr processing and document management
- **personal inflation**: inflation calculator with custom baskets
- **cctv**: camera monitoring and recording system
- **movies**: movie/series collection management
- **music**: spotify-integrated music library
- **restopos**: restaurant pos system
- **wimm**: financial management (where is my money)
- **wims**: inventory management (where is my stuff)
- **birlikteyiz**: earthquake tracking and alerts

## 📝 version management

use the unified version manager:

```bash
./unibos_version.sh
```

see [docs/development/VERSION_MANAGEMENT.md](docs/development/VERSION_MANAGEMENT.md) for details.

## 🌍 deployment

for production deployment:

```bash
tools/scripts/rocksteady_deploy.sh deploy
```

see [docs/deployment/](docs/deployment/) for comprehensive deployment guides.

## 📊 development log

all development activities are tracked in [DEVELOPMENT_LOG.md](DEVELOPMENT_LOG.md).

## 🤝 contributing

this is a personal project, but suggestions and feedback are welcome.

## 📄 license

proprietary - all rights reserved

---

**author**: berk hatırlı
**location**: bitez, bodrum, muğla, türkiye
**project start**: 2024

*built with ❤️ and claude code*
