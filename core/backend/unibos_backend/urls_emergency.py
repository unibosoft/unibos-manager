"""
Emergency URL Configuration for UNIBOS Backend
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin interface (disabled in emergency mode)
    # path('admin/', admin.site.urls),
    
    # CCTV Module (with namespace for web interface)
    path('cctv/', include('modules.cctv.backend.urls', namespace='cctv')),

    # Documents Module (with namespace for consistency)
    path('documents/', include('modules.documents.backend.urls', namespace='documents')),

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

    # Solitaire Game Module
    path('solitaire/', include('modules.solitaire.backend.urls', namespace='solitaire')),

    # Birlikteyiz Module - Emergency Response and Earthquake Tracking
    path('birlikteyiz/', include('modules.birlikteyiz.backend.urls', namespace='birlikteyiz')),

    # Store Module - E-commerce Marketplace Integration
    path('store/', include('modules.store.backend.urls', namespace='store')),

    # Web UI
    path('', include('modules.web_ui.backend.urls')),
]

# Serve media files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Django Debug Toolbar (if installed and in INSTALLED_APPS)
    try:
        # Check if debug_toolbar is in INSTALLED_APPS before trying to use it
        from django.conf import settings
        if 'debug_toolbar' in settings.INSTALLED_APPS:
            import debug_toolbar
            urlpatterns = [
                path('__debug__/', include(debug_toolbar.urls)),
            ] + urlpatterns
    except ImportError:
        pass