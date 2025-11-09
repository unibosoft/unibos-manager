"""
WebSocket routing for Currencies module
"""

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/currencies/rates/$', consumers.CurrencyRatesConsumer.as_asgi()),
    re_path(r'ws/currencies/portfolio/(?P<portfolio_id>[^/]+)/$', consumers.PortfolioConsumer.as_asgi()),
    re_path(r'ws/currencies/alerts/$', consumers.CurrencyAlertsConsumer.as_asgi()),
]