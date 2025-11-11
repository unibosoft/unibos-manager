"""
URL Configuration for UNIBOS Backend
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView
)
from django.views.generic import TemplateView

# API version prefix
API_V1_PREFIX = 'api/v1/'

urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),
    
    # Health checks (disabled - module not installed)
    # path('health/', include('health_check.urls')),
    
    # Prometheus metrics (disabled - module not installed)
    # path('metrics/', include('django_prometheus.urls')),
    
    # API Documentation
    path(f'{API_V1_PREFIX}schema/', SpectacularAPIView.as_view(), name='schema'),
    path(f'{API_V1_PREFIX}schema/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path(f'{API_V1_PREFIX}schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # API URLs
    path(f'{API_V1_PREFIX}', include('modules.core.backend.urls')),  # Core auth/profile
    path(f'{API_V1_PREFIX}auth/', include('modules.authentication.backend.urls')),
    path(f'{API_V1_PREFIX}users/', include('modules.users.backend.urls')),
    path(f'{API_V1_PREFIX}currencies/', include('modules.currencies.backend.urls')),
    # path(f'{API_V1_PREFIX}inflation/', include('modules.personal_inflation.backend.urls')),
    # API URLs don't need namespace since they're already defined in main URLs
    # path(f'{API_V1_PREFIX}recaria/', include('modules.recaria.backend.urls')),
    # path(f'{API_V1_PREFIX}birlikteyiz/', include('modules.birlikteyiz.backend.urls')),
    path(f'{API_V1_PREFIX}wimm/', include('modules.wimm.backend.urls')),
    path(f'{API_V1_PREFIX}wims/', include('modules.wims.backend.urls')),
    path(f'{API_V1_PREFIX}cctv/', include('modules.cctv.backend.urls', namespace='cctv-api')),

    # CCTV Module (separate from API for web interface)
    path('cctv/', include('modules.cctv.backend.urls', namespace='cctv')),

    # Documents Module (Recaria OCR & Document Management)
    path('documents/', include('modules.documents.backend.urls', namespace='documents')),

    # Store Module - Marketplace Integration & Order Management
    path('store/', include('modules.store.backend.urls', namespace='store')),

    # Version Manager Module
    path('version-manager/', include('modules.version_manager.backend.urls', namespace='version_manager')),

    # Administration Module
    path('administration/', include('modules.administration.backend.urls', namespace='administration')),

    # Movies Module - Movie/Series Collection Management
    path('movies/', include('modules.movies.backend.urls', namespace='movies')),

    # Music Module - Music Collection with Spotify Integration
    path('music/', include('modules.music.backend.urls', namespace='music')),

    # RestoPOS Module - Restaurant POS System
    path('restopos/', include('modules.restopos.backend.urls', namespace='restopos')),

    # Personal Inflation Module - Personal consumption tracking
    path('personal-inflation/', include('modules.personal_inflation.backend.urls', namespace='personal_inflation')),

    # Recaria Module - MMORPG System
    path('recaria/', include('modules.recaria.backend.urls', namespace='recaria')),

    # Birlikteyiz Module - Emergency Mesh Network
    path('birlikteyiz/', include('modules.birlikteyiz.backend.urls', namespace='birlikteyiz')),
    
    # WebSocket URLs (handled by ASGI)
    # ws/currencies/ - Real-time currency updates
    # ws/recaria/ - Game real-time features
    # ws/birlikteyiz/ - Emergency mesh network updates
    
    # Root API endpoint
    path(f'{API_V1_PREFIX}', TemplateView.as_view(
        template_name='api_root.html',
        extra_context={
            'api_version': 'v1',
            'endpoints': [
                'auth',
                'users',
                'currencies',
                'inflation',
                'recaria',
                'birlikteyiz',
            ]
        }
    ), name='api-root'),
    
    # Web UI - Terminal-style interface (includes solitaire at /solitaire/)
    path('', include('modules.web_ui.backend.urls')),
    
    # Solitaire Game Module API endpoints
    # Note: /solitaire/ is handled by web_ui, this is just for API
    path('solitaire/', include('modules.solitaire.backend.urls', namespace='solitaire')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Django Debug Toolbar (disabled - not installed)
    # import debug_toolbar
    # urlpatterns = [
    #     path('__debug__/', include(debug_toolbar.urls)),
    # ] + urlpatterns

# Custom error handlers
handler400 = 'modules.common.backend.views.bad_request'
handler403 = 'modules.common.backend.views.permission_denied'
handler404 = 'modules.common.backend.views.not_found'
handler500 = 'modules.common.backend.views.server_error'

# Admin customization
admin.site.site_header = "UNIBOS Administration"
admin.site.site_title = "UNIBOS Admin Portal"
admin.site.index_title = "Welcome to UNIBOS Administration"