"""
Movies Module URL Configuration
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'movies'

router = DefaultRouter()
router.register(r'movies', views.MovieViewSet, basename='movie')
router.register(r'collections', views.CollectionViewSet, basename='collection')
router.register(r'watchlist', views.WatchListViewSet, basename='watchlist')
router.register(r'ratings', views.UserRatingViewSet, basename='rating')
router.register(r'archive', views.PersonalArchiveViewSet, basename='archive')
router.register(r'history', views.WatchHistoryViewSet, basename='history')

urlpatterns = [
    # Web views
    path('', views.dashboard, name='dashboard'),
    
    # API endpoints
    path('api/', include(router.urls)),
]