"""
WebSocket routing for Birlikteyiz module
"""

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/birlikteyiz/mesh/$', consumers.MeshNetworkConsumer.as_asgi()),
    re_path(r'ws/birlikteyiz/emergency/$', consumers.EmergencyConsumer.as_asgi()),
    re_path(r'ws/birlikteyiz/resources/$', consumers.ResourceConsumer.as_asgi()),
]