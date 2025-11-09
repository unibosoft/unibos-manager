# UNIBOS Web UI - Terminal-Style Web Interface

A Django web interface that exactly mirrors the unibos cli interface with a retro-terminal aesthetic.

## Features

- **Terminal-Style Design**: Orange header bar, dark sidebar, and monospace fonts matching the CLI
- **Real-Time Updates**: WebSocket support for live data streaming
- **Module System**: All 4 main modules (Recaria, Birlikteyiz, Kişisel Enflasyon, Currencies)
- **Tools Integration**: System Scrolls, Web UI, Database Setup, and more
- **RESTful APIs**: Complete API endpoints for all module data
- **PostgreSQL Integration**: Full database support with models and migrations
- **User Preferences**: Customizable themes and settings
- **Command History**: Terminal-like command execution and history

## Installation

### 1. Install Dependencies

```bash
cd /Users/berkhatirli/Desktop/unibos/backend
pip install -r requirements.txt
```

### 2. Run Migrations

```bash
python manage.py makemigrations web_ui
python manage.py migrate
```

### 3. Initialize Web UI

```bash
python manage.py init_web_ui
```

### 4. Create Superuser (if not exists)

```bash
python manage.py createsuperuser
```

### 5. Run the Development Server

```bash
# Standard Django server
python manage.py runserver

# Or with ASGI for WebSocket support
daphne -b 0.0.0.0 -p 8000 unibos_backend.asgi:application
```

## Access the Web Interface

Open your browser and navigate to:
- **Main Interface**: http://localhost:8000/
- **Admin Panel**: http://localhost:8000/admin/
- **API Documentation**: http://localhost:8000/api/v1/schema/swagger/

## API Endpoints

### Web UI Specific APIs

- `GET /api/status/` - System status
- `GET /api/sessions/` - Session management
- `GET /api/module-access/` - Module access tracking
- `GET /api/preferences/current/` - User preferences
- `GET /api/system-status/overall/` - Overall system status
- `POST /api/commands/execute/` - Execute commands

### WebSocket Endpoints

- `ws://localhost:8000/ws/status/` - Real-time status updates
- `ws://localhost:8000/ws/module/<module_id>/` - Module-specific updates

## UI Structure

```
┌──────────────────────────────────────────────────────┐
│     UNIBOS - Universal Basic Operating System v354    │ <- Orange Header
├──────────────────┬───────────────────────────────────┤
│                  │                                   │
│  MODULES         │                                   │
│  ▸ Recaria      │                                   │
│  ▸ Birlikteyiz  │      Main Content Area           │
│  ▸ Kişisel Enf. │                                   │
│  ▸ Currencies   │                                   │
│                  │                                   │
│  TOOLS           │                                   │
│  ▸ System Scrolls│                                   │
│  ▸ Web Forge    │                                   │
│                  │                                   │
│  DEV TOOLS       │                                   │
│  ▸ AI Builder   │                                   │
│  ▸ Database     │                                   │
│                  │                                   │
├──────────────────┴───────────────────────────────────┤
│ ESC: Back | TAB: Navigate | 2025-08-07 | Online ✓   │ <- Footer
└──────────────────────────────────────────────────────┘
```

## Keyboard Shortcuts

- **ESC**: Go back / Exit current view
- **TAB**: Navigate through sidebar items
- **ENTER**: Select current item
- **Arrow Keys**: Navigate menus (when implemented)

## Customization

### Themes

The UI supports multiple terminal themes:
- **Dark Terminal** (default)
- **Light Terminal**
- **Retro Green** (classic terminal)
- **Amber CRT** (vintage monitor)

### Configuration

Update settings in `/backend/unibos_backend/settings/base.py`:

```python
# Web UI specific settings
WEB_UI_CONFIG = {
    'DEFAULT_THEME': 'dark',
    'ENABLE_ANIMATIONS': True,
    'WEBSOCKET_RECONNECT_INTERVAL': 5,  # seconds
    'SESSION_TIMEOUT': 3600,  # 1 hour
}
```

## Development

### Adding New Modules

1. Create view in `apps/web_ui/views.py`
2. Add template in `templates/web_ui/`
3. Update URL routing
4. Add WebSocket consumer if needed

### Testing

```bash
# Run tests
python manage.py test apps.web_ui

# Test WebSocket connections
python manage.py shell
>>> from apps.web_ui.models import SystemStatus
>>> SystemStatus.get_overall_status()
```

## Production Deployment

### Using Gunicorn + Uvicorn

```bash
gunicorn unibos_backend.asgi:application -k uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --workers 4
```

### Using Nginx

```nginx
server {
    listen 80;
    server_name unibos.local;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /ws/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

## Troubleshooting

### WebSocket Connection Issues

If WebSockets don't connect:
1. Ensure Redis is running: `redis-cli ping`
2. Check ASGI server is running (not just Django dev server)
3. Verify ALLOWED_HOSTS includes your domain

### Database Connection

```bash
# Test PostgreSQL connection
python manage.py dbshell

# Reset database (CAUTION: deletes all data)
python manage.py reset_db --noinput
python manage.py migrate
```

### Static Files

```bash
# Collect static files for production
python manage.py collectstatic --noinput
```

## Security Considerations

1. **Authentication**: Implement proper user authentication before production
2. **CORS**: Configure CORS headers for API access
3. **Rate Limiting**: Implement rate limiting on API endpoints
4. **SSL/TLS**: Use HTTPS in production
5. **Environment Variables**: Store sensitive data in `.env` file

## Support

For issues or questions, check:
- CLAUDE.md files in the project root
- Django logs: `/backend/logs/django.log`
- System status: http://localhost:8000/api/system-status/overall/

---

**Author**: Berk Hatırlı
**Location**: Bitez, Bodrum, Muğla, Turkey
**Version**: v354 (matching CLI version)