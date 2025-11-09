"""
Music Module URL Configuration
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'music'

router = DefaultRouter()
router.register(r'artists', views.ArtistViewSet, basename='artist')
router.register(r'albums', views.AlbumViewSet, basename='album')
router.register(r'tracks', views.TrackViewSet, basename='track')
router.register(r'library', views.UserLibraryViewSet, basename='library')
router.register(r'playlists', views.PlaylistViewSet, basename='playlist')
router.register(r'history', views.ListeningHistoryViewSet, basename='history')
router.register(r'stats', views.ListeningStatsViewSet, basename='stats')

urlpatterns = [
    # Web views
    path('', views.dashboard, name='dashboard'),
    
    # API endpoints
    path('api/', include(router.urls)),
]