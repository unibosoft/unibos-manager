"""
WebSocket routing for Documents module
"""

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/ocr/analysis/(?P<document_id>[0-9a-f-]+)/$', consumers.OCRAnalysisConsumer.as_asgi()),
]
