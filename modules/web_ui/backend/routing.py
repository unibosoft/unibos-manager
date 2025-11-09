"""
UNIBOS Web UI WebSocket Routing
"""

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/status/$', consumers.StatusConsumer.as_asgi()),
    re_path(r'ws/module/(?P<module_id>\w+)/$', consumers.ModuleConsumer.as_asgi()),
]