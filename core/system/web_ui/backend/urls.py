"""
UNIBOS Web UI URL Configuration
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MainView, ModuleView, ToolView, APIStatusView, 
    LoginView, ProfileView, SettingsView, logout_view, solitaire_view, exit_solitaire,
    store_solitaire_return_url
)
from .api_views import (
    SessionLogViewSet,
    ModuleAccessViewSet,
    UIPreferencesViewSet,
    SystemStatusViewSet,
    CommandHistoryViewSet
)

app_name = 'web_ui'

# API Router
router = DefaultRouter()
router.register(r'api/sessions', SessionLogViewSet, basename='session')
router.register(r'api/module-access', ModuleAccessViewSet, basename='module-access')
router.register(r'api/preferences', UIPreferencesViewSet, basename='preferences')
router.register(r'api/system-status', SystemStatusViewSet, basename='system-status')
router.register(r'api/commands', CommandHistoryViewSet, basename='command')

urlpatterns = [
    # Authentication
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('settings/', SettingsView.as_view(), name='settings'),
    
    # Main dashboard
    path('', MainView.as_view(), name='main'),
    
    # Solitaire (screen lock minimize)
    path('solitaire/', solitaire_view, name='solitaire'),
    path('solitaire/exit/', exit_solitaire, name='exit_solitaire'),
    path('solitaire/store-return-url/', store_solitaire_return_url, name='store_solitaire_return_url'),
    
    # Module views
    path('module/<str:module_id>/', ModuleView.as_view(), name='module'),
    
    # Tool views
    path('tool/<str:tool_id>/', ToolView.as_view(), name='tool'),
    
    # API endpoints
    path('api/status/', APIStatusView.as_view(), name='api_status'),
    
    # Include router URLs
    path('', include(router.urls)),
]