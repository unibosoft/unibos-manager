"""
Solitaire Admin URLs
"""

from django.urls import path
from . import admin_dashboard

urlpatterns = [
    path('dashboard/', admin_dashboard.solitaire_dashboard, name='realtime_dashboard'),
    path('live/<str:session_id>/', admin_dashboard.live_game_view, name='live_game'),
    path('live/<str:session_id>/moves/', admin_dashboard.get_session_moves, name='session_moves'),
    path('player/<int:player_id>/', admin_dashboard.player_profile, name='player_profile'),
    path('api/live-data/', admin_dashboard.get_live_data, name='live_data'),
    path('api/bulk-delete/', admin_dashboard.bulk_delete_sessions, name='bulk_delete_sessions'),
    path('api/delete-session/<str:session_id>/', admin_dashboard.delete_session, name='delete_session'),
]