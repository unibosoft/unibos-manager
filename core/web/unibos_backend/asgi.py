"""
ASGI config for UNIBOS Backend project.
Exposes the ASGI callable for WebSocket support.
"""

import sys
import os
from pathlib import Path
import django
from django.core.asgi import get_asgi_application

# Add UNIBOS root directory to Python path so modules/ can be imported
# This file is in: platform/runtime/web/backend/unibos_backend/asgi.py
# Path: asgi.py → unibos_backend/ → backend/ → web/ → runtime/ → core/ → (UNIBOS root)
# UNIBOS root is 6 levels up
_unibos_root = Path(__file__).resolve().parent.parent.parent.parent.parent.parent
if str(_unibos_root) not in sys.path:
    sys.path.insert(0, str(_unibos_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unibos_backend.settings.production')
django.setup()

# Import after Django setup
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from core.system.common.backend.middleware import JWTAuthMiddleware
import modules.documents.backend.routing

# Django ASGI application
django_asgi_app = get_asgi_application()

# WebSocket routing
websocket_urlpatterns = []
websocket_urlpatterns += modules.documents.backend.routing.websocket_urlpatterns

# Import other app routings if their consumers exist
try:
    import modules.currencies.backend.routing
    websocket_urlpatterns += modules.currencies.backend.routing.websocket_urlpatterns
except (ImportError, AttributeError):
    pass

try:
    import modules.recaria.backend.routing
    websocket_urlpatterns += modules.recaria.backend.routing.websocket_urlpatterns
except (ImportError, AttributeError):
    pass

try:
    import modules.birlikteyiz.backend.routing
    websocket_urlpatterns += modules.birlikteyiz.backend.routing.websocket_urlpatterns
except (ImportError, AttributeError):
    pass

try:
    import core.system.web_ui.backend.routing
    websocket_urlpatterns += core.system.web_ui.backend.routing.websocket_urlpatterns
except (ImportError, AttributeError):
    pass

# ASGI application with WebSocket support
application = ProtocolTypeRouter({
    # HTTP protocol
    "http": django_asgi_app,
    
    # WebSocket protocol
    "websocket": AllowedHostsOriginValidator(
        JWTAuthMiddleware(
            AuthMiddlewareStack(
                URLRouter(websocket_urlpatterns)
            )
        )
    ),
})