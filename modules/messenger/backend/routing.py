"""
Messenger WebSocket URL Routing
"""

from django.urls import path
from .consumers import MessengerConsumer

websocket_urlpatterns = [
    path('ws/messenger/', MessengerConsumer.as_asgi()),
]
