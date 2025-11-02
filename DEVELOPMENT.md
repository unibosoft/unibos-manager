# UNIBOS Development Guide

## Essential References
- [CLAUDE.md](CLAUDE.md) - Development guidelines for Claude AI
- [DEVELOPMENT_LOG.md](DEVELOPMENT_LOG.md) - Track all changes
- [VERSION_MANAGEMENT.md](VERSION_MANAGEMENT.md) - Version control system
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture

## Table of Contents
- [Development Environment Setup](#development-environment-setup)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Module Development](#module-development)
- [Database Management](#database-management)
- [Version Management](#version-management)
- [Debugging Tips](#debugging-tips)
- [Performance Optimization](#performance-optimization)

## Development Environment Setup

### Prerequisites

Before starting development, ensure you have:

```bash
# Required
- Python 3.8+ (3.11+ recommended)
- Git 2.25+
- pip 20.0+
- virtualenv or venv

# Optional but recommended
- Docker 20.10+
- PostgreSQL 15+
- Redis 7+
- VS Code or PyCharm
```

### Initial Setup

#### 1. Clone and Setup Repository

```bash
# Clone the repository
git clone https://github.com/unibos/unibos.git
cd unibos

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development tools
```

#### 2. Database Setup

```bash
# PostgreSQL setup (required)
createdb unibos_dev
psql unibos_dev -c "CREATE EXTENSION postgis;"
python backend/manage.py migrate
```

#### 3. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your settings
nano .env
```

Required environment variables:
```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (PostgreSQL required)
DATABASE_URL=postgresql://user:pass@localhost/unibos_dev

# Redis (optional)
REDIS_URL=redis://localhost:6379/0

# API Keys (optional)
TCMB_API_KEY=your-key
COINGECKO_API_KEY=your-key
```

## Project Structure

```
unibos/
├── src/                    # Core terminal application
│   ├── main.py            # Main entry point
│   ├── VERSION.json       # Version tracking
│   ├── translations.py    # i18n support
│   └── modules/           # Terminal UI modules
│
├── backend/               # Django web backend
│   ├── manage.py         # Django management
│   ├── apps/             # Django applications
│   │   ├── authentication/
│   │   ├── users/
│   │   ├── currencies/
│   │   ├── documents/
│   │   ├── wimm/
│   │   ├── wims/
│   │   └── ...
│   └── unibos_backend/   # Core settings
│
├── archive/              # Version history
│   ├── versions/         # Historical versions
│   └── communication_logs/
│
├── tests/                # Test suites
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
└── docs/                 # Documentation
```

## Development Workflow

### 1. Creating a New Feature

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes
# ... edit files ...

# Run tests
python -m pytest tests/

# Commit with conventional commits
git add .
git commit -m "feat: add new feature description"

# Push to remote
git push origin feature/your-feature-name
```

### 2. Conventional Commits

Use these prefixes for commit messages:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes
- `refactor:` Code refactoring
- `test:` Test additions/changes
- `chore:` Maintenance tasks

### 3. Version Management

UNIBOS uses automatic version management:

```python
# src/version_manager.py handles versioning
from version_manager import VersionManager

vm = VersionManager()
vm.increment_version()  # Automatically increments and archives
```

### 4. Archive System

The project maintains comprehensive archives:

```bash
# Archive current version
python src/archive_version.py

# This creates:
# - archive/versions/unibos_vXXX_YYYYMMDD_HHMM/
# - Complete snapshot of current state
# - Communication log
```

## Coding Standards

### Python Style Guide

Follow PEP 8 with these additions:

```python
# File header template
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module description here.

Author: Your Name
Date: YYYY-MM-DD
Version: vXXX
"""

# Import order
import os
import sys
from datetime import datetime  # Standard library

import django  # Third-party
import requests

from .models import User  # Local imports
from ..utils import helper
```

### Code Quality Tools

```bash
# Linting
flake8 src/ backend/ --max-line-length=120

# Type checking
mypy src/ backend/

# Code formatting
black src/ backend/ --line-length=120

# Import sorting
isort src/ backend/

# Security scanning
bandit -r src/ backend/
```

### Documentation Standards

```python
def process_document(document_id: int, ocr: bool = True) -> dict:
    """
    Process a document with optional OCR.
    
    Args:
        document_id: The ID of the document to process
        ocr: Whether to perform OCR (default: True)
        
    Returns:
        A dictionary containing:
            - status: Processing status ('success', 'error')
            - data: Processed document data
            - ocr_text: OCR extracted text (if ocr=True)
            
    Raises:
        DocumentNotFound: If document doesn't exist
        OCRError: If OCR processing fails
        
    Example:
        >>> result = process_document(123, ocr=True)
        >>> print(result['status'])
        'success'
    """
    pass
```

## Testing Guidelines

### Test Structure

```python
# tests/test_module.py
import pytest
from unittest.mock import Mock, patch

class TestModuleName:
    """Test suite for ModuleName."""
    
    @pytest.fixture
    def setup_data(self):
        """Setup test data."""
        return {"test": "data"}
    
    def test_feature_success(self, setup_data):
        """Test feature with valid input."""
        assert feature(setup_data) == expected_result
    
    def test_feature_error(self):
        """Test feature with invalid input."""
        with pytest.raises(ValueError):
            feature(invalid_input)
```

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
pytest --cov=src --cov=backend tests/

# Run specific test file
pytest tests/test_currencies.py

# Run with verbose output
pytest -v

# Run only marked tests
pytest -m "slow"
```

### Test Coverage Requirements

- Minimum 80% coverage for new code
- Critical paths must have 100% coverage
- Integration tests for all API endpoints
- E2E tests for user workflows

## Module Development

### Creating a New Module

#### 1. Terminal UI Module

```python
# src/modules/your_module.py
from typing import Optional
import curses

class YourModule:
    """Your module description."""
    
    def __init__(self, stdscr: curses.window):
        self.stdscr = stdscr
        self.title = "Your Module"
        
    def run(self) -> Optional[str]:
        """Main module loop."""
        while True:
            self.draw_interface()
            key = self.stdscr.getch()
            if key == ord('q'):
                return None
                
    def draw_interface(self):
        """Draw the module interface."""
        self.stdscr.clear()
        self.stdscr.addstr(0, 0, self.title)
        self.stdscr.refresh()
```

#### 2. Django Backend Module

```bash
# Create Django app
python backend/manage.py startapp your_module

# Move to apps directory
mv your_module backend/apps/

# Add to INSTALLED_APPS in settings.py
INSTALLED_APPS = [
    ...
    'apps.your_module',
]
```

### Module Integration Checklist

- [ ] Create module directory/app
- [ ] Implement core functionality
- [ ] Add translations (10 languages)
- [ ] Write unit tests (>80% coverage)
- [ ] Add integration tests
- [ ] Update documentation
- [ ] Add to main menu
- [ ] Test with all databases
- [ ] Performance testing
- [ ] Security review

## Database Management

### Migrations

```bash
# Create migrations
python backend/manage.py makemigrations

# Review migration SQL
python backend/manage.py sqlmigrate app_name 0001

# Apply migrations
python backend/manage.py migrate

# Rollback migration
python backend/manage.py migrate app_name 0001
```

### Database Operations

```python
# Using Django ORM
from apps.users.models import User

# Create
user = User.objects.create(username="test", email="test@example.com")

# Read
users = User.objects.filter(is_active=True)

# Update
User.objects.filter(id=1).update(last_login=datetime.now())

# Delete
User.objects.filter(id=1).delete()

# Raw SQL (when necessary)
from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("SELECT * FROM users WHERE created_at > %s", [date])
    results = cursor.fetchall()
```

### Database Optimization

```python
# Use select_related for foreign keys
orders = Order.objects.select_related('user').all()

# Use prefetch_related for many-to-many
products = Product.objects.prefetch_related('categories').all()

# Use only() for specific fields
users = User.objects.only('id', 'username', 'email').all()

# Use bulk operations
User.objects.bulk_create([
    User(username=f"user{i}") for i in range(1000)
])
```

## Version Management

### Version Format

UNIBOS uses the format: `vXXX_YYYYMMDD_HHMM`
- `vXXX`: Version number (e.g., v429)
- `YYYYMMDD`: Date
- `HHMM`: Time

### Automatic Versioning

```python
# Version is automatically incremented on significant changes
from git_manager import GitManager

gm = GitManager()
gm.commit_and_version("feat: added new feature")
# Automatically creates v430, archives v429, updates VERSION.json
```

### Manual Version Control

```bash
# Check current version
cat src/VERSION.json

# Create new version manually
python src/archive_version.py --version v430 --message "Major update"

# Restore previous version
python src/restore_version.py --version v429
```

## Debugging Tips

### Terminal UI Debugging

```python
# Debug output to file (doesn't interfere with curses)
import logging

logging.basicConfig(
    filename='debug.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.debug("Debug message")
```

### Django Debugging

```python
# Enable Django Debug Toolbar
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']

# Use Django shell
python backend/manage.py shell_plus

# SQL query logging
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

### Performance Profiling

```python
# Using cProfile
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Your code here
expensive_function()

profiler.disable()
stats = pstats.Stats(profiler).sort_stats('cumulative')
stats.print_stats(10)  # Top 10 functions
```

## Performance Optimization

### Code Optimization

```python
# Use generators for large datasets
def process_large_file(filename):
    with open(filename) as f:
        for line in f:  # Generator, doesn't load entire file
            yield process_line(line)

# Cache expensive operations
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_calculation(n):
    return sum(i**2 for i in range(n))

# Use appropriate data structures
# Set for membership testing (O(1) vs O(n) for lists)
valid_ids = {1, 2, 3, 4, 5}
if user_id in valid_ids:  # Fast
    process_user()
```

### Database Optimization

```python
# Index frequently queried fields
class Document(models.Model):
    created_at = models.DateTimeField(db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['created_at', 'user']),
        ]

# Use database functions
from django.db.models import Count, Sum, Avg

stats = Order.objects.aggregate(
    total=Sum('amount'),
    average=Avg('amount'),
    count=Count('id')
)
```

### Caching Strategy

```python
# Redis caching
from django.core.cache import cache

def get_user_stats(user_id):
    cache_key = f"user_stats_{user_id}"
    stats = cache.get(cache_key)
    
    if stats is None:
        stats = calculate_user_stats(user_id)
        cache.set(cache_key, stats, timeout=3600)  # 1 hour
    
    return stats
```

## Continuous Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.11'
        
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
        
    - name: Run tests
      run: pytest --cov=src --cov=backend
      
    - name: Lint
      run: flake8 src/ backend/
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Import Errors
```bash
# Issue: ModuleNotFoundError
# Solution: Add parent directory to path
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```

#### 2. Database Connection Issues
```bash
# Issue: psycopg2 not found
# Solution:
pip install psycopg2-binary

# Issue: PostgreSQL connection refused
# Solution: Check PostgreSQL is running
sudo systemctl status postgresql
sudo systemctl start postgresql
```

#### 3. Terminal UI Issues
```bash
# Issue: Curses not available on Windows
# Solution: Install windows-curses
pip install windows-curses

# Issue: Terminal too small
# Solution: Resize terminal to at least 80x24
```

## Resources

### Documentation
- [Python Documentation](https://docs.python.org/3/)
- [Django Documentation](https://docs.djangoproject.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

### Tools
- [VS Code Python Extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
- [PyCharm Professional](https://www.jetbrains.com/pycharm/)
- [Django Debug Toolbar](https://django-debug-toolbar.readthedocs.io/)

### Community
- GitHub Issues: Report bugs and request features
- Discord: Join our developer community
- Stack Overflow: Tag questions with `unibos`

---

## Quick Reference Commands

### Most Used Commands
```bash
# Start terminal UI
python src/main.py

# Start Django backend
python backend/manage.py runserver

# Create new version
./unibos_version.sh

# Add development log entry
./add_dev_log.sh "Category" "Title" "Details" "Result"

# Run tests
python -m pytest tests/
```

---

*Last Updated: 2025-08-12*  
*Development Guide Version: 2.0*
*Compatible with UNIBOS v446+*