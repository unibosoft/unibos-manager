"""
Solitaire URL Configuration
"""

from django.urls import path
from . import views
from . import admin_dashboard

app_name = 'solitaire'

urlpatterns = [
    path('', views.solitaire_game, name='game'),
    path('api/<str:action>/', views.solitaire_api, name='api'),
    path('stats/', views.solitaire_stats, name='stats'),
    
    # Admin dashboard URLs
    path('admin/dashboard/', admin_dashboard.solitaire_dashboard, name='admin_dashboard'),
    path('admin/live/<str:session_id>/', admin_dashboard.live_game_view, name='live_game'),
    path('admin/player/<int:player_id>/', admin_dashboard.player_profile, name='player_profile'),
]