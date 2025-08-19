# 🪐 unibos - unicorn bodrum operating system

<div align="center">

[![Version](https://img.shields.io/badge/version-v499-blue.svg)](src/VERSION.json)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/django-4.2+-092e20.svg)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-linux%20%7C%20macos%20%7C%20windows-lightgrey.svg)](https://github.com/unibos/unibos)

**a comprehensive, modular operating system platform combining terminal and web interfaces**

[features](#features) • [quick start](#quick-start) • [documentation](#documentation) • [modules](#modules) • [contributing](#contributing)

</div>

## 🌟 about unibos

unibos is an ambitious project that started as a simple Raspberry Pi system and evolved into a comprehensive platform with 448 versions of continuous development. It combines the simplicity of terminal interfaces with the power of modern web technologies, offering both offline-first capabilities and cloud integration.

### 🎯 key features

- **🔐 enterprise security**: JWT authentication, 2FA support, role-based access control
- **🌍 multi-language**: Support for 10 languages including English, Turkish, Spanish, French, German, Chinese, Japanese
- **📊 comprehensive modules**: Financial tracking, inventory management, document OCR, camera monitoring
- **🚀 446+ versions**: Continuous development from v001 (June 2025) to present
- **💾 dual database**: SQLite for development, PostgreSQL for production
- **🔄 real-time updates**: WebSocket support for live data
- **📱 cross-platform**: Works on Linux, macOS, Windows, and Raspberry Pi

## 📦 modules

| module | description | status |
|--------|-------------|--------|
| **💰 wimm** | where is my money - financial management with multi-currency support | ✅ Active |
| **📦 wims** | where is my stuff - inventory and warehouse management | ✅ Active |
| **💱 currencies** | real-time exchange rates and crypto tracking | ✅ Active |
| **📊 personal inflation** | individual inflation calculator based on receipts | ✅ Active |
| **📄 documents** | ocr-powered document management and receipt parsing | ✅ Active |
| **📹 cctv** | camera monitoring with TP-Link Tapo integration | ✅ Active |
| **🪐 recaria** | space exploration game with real-world maps | ✅ Active |
| **📡 birlikteyiz** | emergency mesh network communication (LoRa) | ✅ Active |
| **🎬 movies** | movie & series collection with TMDB/OMDB integration | ✅ Active |
| **🎵 music** | spotify-integrated music library and statistics | ✅ Active |
| **🍽️ restopos** | professional restaurant POS and management system | ✅ Active |

## 🚀 quick start

### prerequisites

- Python 3.8+ (3.11+ recommended)
- 2GB RAM minimum (8GB recommended)
- 10GB disk space
- PostgreSQL 15+ (for production)
- Redis 7+ (optional, for caching)

### Installation

```bash
# Clone the repository
git clone https://github.com/unibos/unibos.git
cd unibos

# Option 1: Quick start with terminal UI
python src/main.py

# Option 2: Full setup with web interface
pip install -r requirements.txt
python backend/manage.py migrate
python backend/manage.py runserver

# Option 3: Docker deployment
docker-compose up -d
```

## 📖 Usage

### Terminal Interface

```bash
# Launch the main terminal UI
python src/main.py

# Navigation
- Arrow keys: Navigate menus
- Enter: Select option
- ESC/q: Go back or quit
- l: Change language
```

### Web Interface

```bash
# Start the Django backend
python backend/manage.py runserver

# Access at http://localhost:8000
# Admin panel: http://localhost:8000/admin
# API docs: http://localhost:8000/api/v1/docs
```

## 📊 System Requirements

### Minimum Requirements
- **OS**: Linux, macOS 10.15+, Windows 10+
- **CPU**: 2 cores
- **RAM**: 2GB
- **Storage**: 10GB
- **Python**: 3.8+

### Recommended Requirements
- **OS**: Ubuntu 22.04 LTS, macOS 13+, Windows 11
- **CPU**: 4+ cores
- **RAM**: 8GB+
- **Storage**: 50GB SSD
- **Python**: 3.11+
- **Database**: PostgreSQL 15+
- **Cache**: Redis 7+

## 📚 Documentation

### Core Documentation
- [Architecture Overview](ARCHITECTURE.md) - System design and components
- [Development Guide](DEVELOPMENT.md) - Setup and development workflow
- [Installation Guide](INSTALLATION.md) - Detailed setup instructions
- [Features List](FEATURES.md) - Complete feature documentation
- [API Documentation](API.md) - Backend API endpoints

### Development Guidelines
- [CLAUDE Guidelines](CLAUDE.md) - Development rules and standards
- [Development Log](DEVELOPMENT_LOG.md) - Change history and activity tracking
- [Version Management](VERSION_MANAGEMENT.md) - Version control system documentation

### System Documentation
- [Project Structure](PROJECT_STRUCTURE.md) - Directory and file organization
- [Archive Guide](ARCHIVE_GUIDE.md) - Archive system and protection protocols
- [Changelog](CHANGELOG.md) - Version release history
- [Troubleshooting](TROUBLESHOOTING.md) - Common issues and solutions

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

```bash
# Development setup
git clone https://github.com/unibos/unibos.git
cd unibos
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements-dev.txt
python -m pytest tests/
```

## 🔒 Security

- JWT-based authentication with refresh tokens
- Two-factor authentication (2FA) support
- Role-based access control (RBAC)
- Encrypted data storage
- Input validation and sanitization
- Rate limiting and DDoS protection

For security issues, please email security@unibos.com instead of using the issue tracker.

## 📈 Project Statistics

- **Versions Released**: 446+
- **Development Period**: June 2025 - Present
- **Lines of Code**: 55,000+
- **Modules**: 11 major modules
- **Languages Supported**: 10
- **Active Contributors**: Growing community

## 🗺️ Roadmap

- [ ] Mobile applications (iOS/Android)
- [ ] Cloud synchronization
- [ ] AI-powered features
- [ ] Blockchain integration
- [ ] IoT device support
- [ ] Microservices architecture

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Team

**Creator & Lead Developer**  
Berk Hatırlı  
📍 Bitez, Bodrum, Muğla, Turkey

## 🙏 Acknowledgments

- The open-source community for invaluable tools and libraries
- Early adopters and testers for their feedback
- Contributors who helped shape UNIBOS

---

<div align="center">

© 2025 unicorn bodrum software - building the future, one module at a time

[Website](https://unibos.com) • [Documentation](https://docs.unibos.com) • [Community](https://community.unibos.com)

</div>