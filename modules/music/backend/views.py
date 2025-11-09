"""
Music Module Views
Secure and performant API views for music management
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required

from .models import (
    Artist, Album, Track, UserLibrary, 
    Playlist, ListeningHistory, ListeningStats
)
from .serializers import (
    ArtistSerializer, AlbumSerializer, TrackDetailSerializer,
    UserLibrarySerializer, PlaylistSerializer,
    ListeningHistorySerializer, ListeningStatsSerializer
)


class ArtistViewSet(viewsets.ModelViewSet):
    """Artist management"""
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    

class AlbumViewSet(viewsets.ModelViewSet):
    """Album management"""
    queryset = Album.objects.all()
    serializer_class = AlbumSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class TrackViewSet(viewsets.ModelViewSet):
    """Track management"""
    queryset = Track.objects.all()
    serializer_class = TrackDetailSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class UserLibraryViewSet(viewsets.ModelViewSet):
    """User library management"""
    serializer_class = UserLibrarySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return UserLibrary.objects.filter(user=self.request.user)


class PlaylistViewSet(viewsets.ModelViewSet):
    """Playlist management"""
    serializer_class = PlaylistSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Playlist.objects.filter(user=self.request.user)


class ListeningHistoryViewSet(viewsets.ModelViewSet):
    """Listening history tracking"""
    serializer_class = ListeningHistorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ListeningHistory.objects.filter(user=self.request.user)


class ListeningStatsViewSet(viewsets.ModelViewSet):
    """Listening statistics"""
    serializer_class = ListeningStatsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ListeningStats.objects.filter(user=self.request.user)


@login_required
def dashboard(request):
    """
    Music module dashboard view
    """
    context = {
        'module_name': 'Music',
        'module_description': 'Music Collection with Spotify Integration',
        'user': request.user,
    }
    
    # Get user statistics
    if request.user.is_authenticated:
        context['stats'] = {
            'library_count': UserLibrary.objects.filter(user=request.user).count(),
            'playlists_count': Playlist.objects.filter(user=request.user).count(),
            'history_count': ListeningHistory.objects.filter(user=request.user).count(),
        }
    
    return render(request, 'music/dashboard.html', context)