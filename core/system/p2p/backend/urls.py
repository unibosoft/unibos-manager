"""
P2P API URL configuration
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    PeerViewSet,
    P2PStatusView,
    P2PStartView,
    P2PStopView,
    SendMessageView,
    BroadcastView,
    RelayView,
)

router = DefaultRouter()
router.register('peers', PeerViewSet, basename='peer')

app_name = 'p2p'

urlpatterns = [
    # Service control
    path('status/', P2PStatusView.as_view(), name='p2p-status'),
    path('start/', P2PStartView.as_view(), name='p2p-start'),
    path('stop/', P2PStopView.as_view(), name='p2p-stop'),

    # Messaging
    path('send/', SendMessageView.as_view(), name='p2p-send'),
    path('broadcast/', BroadcastView.as_view(), name='p2p-broadcast'),
    path('relay/', RelayView.as_view(), name='p2p-relay'),

    # ViewSets
    path('', include(router.urls)),
]
