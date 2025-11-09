"""
WebSocket routing for Recaria module
"""

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/recaria/game/$', consumers.GameConsumer.as_asgi()),
    re_path(r'ws/recaria/realm/(?P<realm_id>[^/]+)/$', consumers.RealmConsumer.as_asgi()),
    re_path(r'ws/recaria/combat/$', consumers.CombatConsumer.as_asgi()),
    re_path(r'ws/recaria/guild/(?P<guild_id>[^/]+)/$', consumers.GuildConsumer.as_asgi()),
]