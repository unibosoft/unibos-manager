"""
WebSocket routing for authentication module.
"""

from django.urls import path
from .consumers import AuthNotificationConsumer

websocket_urlpatterns = [
    path('ws/auth/notifications/', AuthNotificationConsumer.as_asgi()),
]
