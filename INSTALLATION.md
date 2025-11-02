# UNIBOS Installation Guide

## 🔗 Related Documentation
- [README.md](README.md) - Project overview
- [DEVELOPMENT.md](DEVELOPMENT.md) - Development setup
- [ARCHITECTURE.md](ARCHITECTURE.md) - System design
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Problem solving

## Table of Contents
- [Quick Start](#quick-start)
- [System Requirements](#system-requirements)
- [Installation Methods](#installation-methods)
  - [Terminal UI Only](#terminal-ui-only)
  - [Full Installation](#full-installation)
  - [Docker Installation](#docker-installation)
  - [Raspberry Pi Installation](#raspberry-pi-installation)
- [Database Setup](#database-setup)
- [Configuration](#configuration)
- [Post-Installation](#post-installation)
- [Troubleshooting](#troubleshooting)

## Quick Start

The fastest way to get UNIBOS running:

```bash
# Clone and run
git clone https://github.com/unibos/unibos.git
cd unibos
python src/main.py
```

This launches the terminal UI with PostgreSQL database - requires PostgreSQL to be installed and configured.

## System Requirements

### Minimum Requirements
- **Operating System**: Linux, macOS 10.15+, Windows 10+
- **Python**: 3.8 or higher
- **RAM**: 2GB
- **Storage**: 10GB free space
- **Terminal**: 80x24 minimum size

### Recommended Requirements
- **Operating System**: Ubuntu 22.04 LTS, macOS 13+, Windows 11
- **Python**: 3.11 or higher
- **RAM**: 8GB or more
- **Storage**: 50GB SSD
- **Terminal**: 120x40 or larger
- **Database**: PostgreSQL 15+
- **Cache**: Redis 7+

### Optional Components
- Docker 20.10+ (for containerized deployment)
- Nginx 1.24+ (for production web deployment)
- Tesseract 4.0+ (for OCR functionality)

## Installation Methods

### Terminal UI Only

Perfect for personal use or testing:

#### 1. Install Python
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv

# macOS (with Homebrew)
brew install python@3.11

# Windows
# Download from https://www.python.org/downloads/
```

#### 2. Clone Repository
```bash
git clone https://github.com/unibos/unibos.git
cd unibos
```

#### 3. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 5. Run Terminal UI
```bash
python src/main.py
```

### Full Installation

Complete installation with web interface and all features:

#### 1. System Dependencies

##### Ubuntu/Debian
```bash
sudo apt update
sudo apt install -y \
    python3.11 python3.11-dev python3-pip \
    postgresql postgresql-contrib \
    redis-server \
    tesseract-ocr tesseract-ocr-eng tesseract-ocr-tur \
    git curl wget \
    build-essential libpq-dev \
    libxml2-dev libxslt1-dev \
    libjpeg-dev libpng-dev
```

##### macOS
```bash
# Install Homebrew if not installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python@3.11 postgresql@15 redis tesseract git
brew services start postgresql@15
brew services start redis
```

##### Windows
```powershell
# Install Chocolatey if not installed
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install dependencies
choco install python311 postgresql15 redis tesseract git
```

#### 2. Clone and Setup
```bash
git clone https://github.com/unibos/unibos.git
cd unibos

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt
pip install -r backend/requirements.txt
```

#### 3. Database Setup

##### PostgreSQL Setup
```bash
# Create database user and database
sudo -u postgres psql <<EOF
CREATE USER unibos WITH PASSWORD 'secure_password_here';
CREATE DATABASE unibos_db OWNER unibos;
\c unibos_db
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
GRANT ALL PRIVILEGES ON DATABASE unibos_db TO unibos;
EOF
```

##### Configure Database Connection
```bash
# Create .env file
cp .env.example .env

# Edit .env file
nano .env
```

Add database configuration:
```env
DATABASE_URL=postgresql://unibos:secure_password_here@localhost/unibos_db
```

#### 4. Run Migrations
```bash
cd backend
python manage.py migrate
python manage.py collectstatic --noinput
```

#### 5. Create Superuser
```bash
python manage.py createsuperuser
```

#### 6. Load Initial Data (Optional)
```bash
python manage.py loaddata initial_data.json
```

#### 7. Start Services

##### Development Mode
```bash
# Terminal 1: Django Backend
cd backend
python manage.py runserver

# Terminal 2: Terminal UI (optional)
cd ..
python src/main.py
```

##### Production Mode
```bash
# Using Gunicorn
cd backend
gunicorn unibos_backend.wsgi:application --bind 0.0.0.0:8000

# Or using the startup script
./start_backend.sh
```

### Docker Installation

The easiest way for production deployment:

#### 1. Install Docker
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# macOS/Windows
# Download Docker Desktop from https://www.docker.com/products/docker-desktop
```

#### 2. Clone Repository
```bash
git clone https://github.com/unibos/unibos.git
cd unibos
```

#### 3. Configure Environment
```bash
cp .env.docker.example .env
nano .env  # Edit with your settings
```

#### 4. Build and Run
```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

#### 5. Initialize Database
```bash
# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Load initial data (optional)
docker-compose exec web python manage.py loaddata initial_data.json
```

#### 6. Access Application
- Web Interface: http://localhost:8000
- Admin Panel: http://localhost:8000/admin
- API Documentation: http://localhost:8000/api/v1/docs

### Raspberry Pi Installation

Special instructions for Raspberry Pi deployment:

#### 1. Prepare Raspberry Pi
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y \
    python3-pip python3-venv \
    postgresql \
    redis-server \
    tesseract-ocr \
    git

# For Birlikteyiz module (LoRa)
sudo apt install -y python3-spidev python3-rpi.gpio
```

#### 2. Clone and Setup
```bash
git clone https://github.com/unibos/unibos.git
cd unibos

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies (use lighter requirements)
pip install -r requirements-rpi.txt
```

#### 3. Configure for Pi
```bash
# Configure PostgreSQL connection
echo "DATABASE_URL=postgresql://unibos:password@localhost/unibos_db" > .env

# Optimize for limited RAM
echo "DJANGO_DEBUG=False" >> .env
echo "CACHE_BACKEND=locmem" >> .env
```

#### 4. Enable Hardware Features
```bash
# Enable SPI for LoRa
sudo raspi-config
# Navigate to Interface Options > SPI > Enable

# Add user to gpio group
sudo usermod -a -G gpio $USER
```

#### 5. Auto-start on Boot
```bash
# Create systemd service
sudo cp unibos.service /etc/systemd/system/
sudo systemctl enable unibos
sudo systemctl start unibos
```

## Database Setup

### PostgreSQL (Required)

UNIBOS uses PostgreSQL exclusively for all deployments.

#### Installation
```bash
# Ubuntu/Debian
sudo apt install postgresql postgresql-contrib

# macOS
brew install postgresql@15
brew services start postgresql@15
```

#### Configuration
```sql
-- Create database and user
CREATE USER unibos WITH PASSWORD 'your_secure_password';
CREATE DATABASE unibos_db OWNER unibos;

-- Enable extensions
\c unibos_db
CREATE EXTENSION postgis;  -- For geographic data
CREATE EXTENSION pg_trgm;  -- For text search
```

#### Connection String
```bash
# In .env file
DATABASE_URL=postgresql://unibos:password@localhost/unibos_db
```

### Redis (Optional)

For caching and real-time features:

```bash
# Install
sudo apt install redis-server  # Ubuntu/Debian
brew install redis             # macOS

# Start service
sudo systemctl start redis     # Linux
brew services start redis       # macOS

# Configure in .env
REDIS_URL=redis://localhost:6379/0
```

## Configuration

### Environment Variables

Create `.env` file in project root:

```env
# Django Settings
SECRET_KEY=your-very-secret-key-here-generate-a-strong-one
DEBUG=False  # Set to True for development
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

# Database (PostgreSQL required)
DATABASE_URL=postgresql://unibos:password@localhost/unibos_db

# Redis (optional)
REDIS_URL=redis://localhost:6379/0

# Email (optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True

# API Keys (optional)
TCMB_API_KEY=your-key
COINGECKO_API_KEY=your-key
BINANCE_API_KEY=your-key
BINANCE_SECRET_KEY=your-secret

# Security
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
CSRF_TRUSTED_ORIGINS=http://localhost:8000,https://yourdomain.com

# OCR Settings
TESSERACT_CMD=/usr/bin/tesseract  # Path to tesseract
OCR_LANGUAGES=eng,tur  # Languages to use

# File Storage
MEDIA_ROOT=/path/to/media/files
STATIC_ROOT=/path/to/static/files
```

### Nginx Configuration (Production)

For production deployment with Nginx:

```nginx
# /etc/nginx/sites-available/unibos
server {
    listen 80;
    server_name your-domain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;

    # Static files
    location /static/ {
        alias /var/www/unibos/static/;
    }

    location /media/ {
        alias /var/www/unibos/media/;
    }

    # Django application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket support
    location /ws/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## Post-Installation

### 1. Verify Installation
```bash
# Check Python version
python --version

# Check Django
python backend/manage.py check

# Test database connection
python backend/manage.py dbshell

# Run tests
python -m pytest tests/
```

### 2. Initial Setup

#### Create Admin User
```bash
cd backend
python manage.py createsuperuser
```

#### Configure Modules
Access admin panel at http://localhost:8000/admin to:
- Configure user roles and permissions
- Set up API keys for external services
- Configure email settings
- Set up CCTV cameras
- Initialize currency data

### 3. Security Hardening

#### Generate Secret Key
```python
# Generate a new secret key
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

#### SSL Certificate (Production)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com
```

#### Firewall Configuration
```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp  # SSH
sudo ufw allow 80/tcp  # HTTP
sudo ufw allow 443/tcp # HTTPS
sudo ufw enable
```

### 4. Backup Configuration

#### Database Backup Script
```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/unibos"

# PostgreSQL backup
pg_dump unibos_db > $BACKUP_DIR/db_$DATE.sql

# Files backup
tar -czf $BACKUP_DIR/files_$DATE.tar.gz /var/www/unibos/media/

# Keep only last 30 days
find $BACKUP_DIR -type f -mtime +30 -delete
```

#### Automated Backups
```bash
# Add to crontab
crontab -e
# Add line:
0 2 * * * /path/to/backup.sh
```

## Troubleshooting

### Common Issues

#### Python Version Issues
```bash
# Issue: Wrong Python version
# Solution: Use specific version
python3.11 -m venv venv
```

#### Database Connection Failed
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check connection
psql -U unibos -d unibos_db -h localhost

# Reset password if needed
sudo -u postgres psql
ALTER USER unibos PASSWORD 'new_password';
```

#### Permission Denied Errors
```bash
# Fix file permissions
sudo chown -R $USER:$USER .
chmod -R 755 .

# For media/static directories
sudo chown -R www-data:www-data media/
sudo chown -R www-data:www-data static/
```

#### Module Import Errors
```bash
# Reinstall dependencies
pip install --upgrade --force-reinstall -r requirements.txt

# Clear Python cache
find . -type d -name __pycache__ -exec rm -r {} +
```

#### OCR Not Working
```bash
# Install Tesseract
sudo apt install tesseract-ocr tesseract-ocr-eng tesseract-ocr-tur

# Verify installation
tesseract --version

# Set path in .env
TESSERACT_CMD=/usr/bin/tesseract
```

### Getting Help

#### Check Logs
```bash
# Django logs
tail -f backend/logs/django.log

# System logs
journalctl -u unibos -f

# Docker logs
docker-compose logs -f
```

#### Run Diagnostics
```bash
# Check system
python src/system_check.py

# Database check
python backend/manage.py dbshell

# Test modules
python -m pytest tests/ -v
```

#### Community Support
- GitHub Issues: https://github.com/unibos/unibos/issues
- Discord: https://discord.gg/unibos
- Documentation: https://docs.unibos.com

## Next Steps

After installation:

1. **Explore Terminal UI**: Run `python src/main.py` and navigate through modules
2. **Access Web Interface**: Open http://localhost:8000 in your browser
3. **Read Documentation**: Check [FEATURES.md](FEATURES.md) for detailed feature information
4. **Configure Modules**: Set up the modules you need via admin panel
5. **Join Community**: Get support and share experiences

---

## Post-Installation Checklist

- [ ] Terminal UI launches successfully
- [ ] Django backend starts without errors
- [ ] Database migrations completed
- [ ] Admin user created
- [ ] Can access web interface at localhost:8000
- [ ] Version manager shows correct version
- [ ] Archive system functioning

---

*Last Updated: 2025-08-12*  
*Installation Guide Version: 2.0*  
*Compatible with UNIBOS v446+*