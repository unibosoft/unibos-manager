"""
Music Module Serializers
RESTful API serializers for music management
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from .models import (
    Artist, Album, Track, UserLibrary, UserArtist,
    UserAlbum, UserTrack, Playlist, PlaylistTrack,
    ListeningHistory, ListeningStats
)

User = get_user_model()


class ArtistSerializer(serializers.ModelSerializer):
    """Artist serializer"""
    
    album_count = serializers.ReadOnlyField()
    track_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Artist
        fields = [
            'id', 'spotify_id', 'name', 'slug', 'genres',
            'popularity', 'followers', 'image_url', 'thumbnail_url',
            'bio', 'country', 'formed_year', 'spotify_url',
            'album_count', 'track_count', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TrackListSerializer(serializers.ModelSerializer):
    """Lightweight track serializer for lists"""
    
    artist_name = serializers.ReadOnlyField(source='artist.name')
    album_name = serializers.ReadOnlyField(source='album.name')
    duration_formatted = serializers.ReadOnlyField()
    
    class Meta:
        model = Track
        fields = [
            'id', 'spotify_id', 'name', 'artist_name', 'album_name',
            'duration_ms', 'duration_formatted', 'explicit',
            'popularity', 'preview_url'
        ]


class AlbumSerializer(serializers.ModelSerializer):
    """Album serializer"""
    
    artist = ArtistSerializer(read_only=True)
    artist_id = serializers.UUIDField(write_only=True, required=False)
    tracks = TrackListSerializer(many=True, read_only=True)
    duration_formatted = serializers.ReadOnlyField()
    
    class Meta:
        model = Album
        fields = [
            'id', 'spotify_id', 'name', 'album_type', 'artist',
            'artist_id', 'release_date', 'total_tracks', 'duration_ms',
            'duration_formatted', 'cover_url', 'thumbnail_url',
            'label', 'genres', 'popularity', 'spotify_url',
            'tracks', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TrackDetailSerializer(serializers.ModelSerializer):
    """Detailed track serializer"""
    
    artist = ArtistSerializer(read_only=True)
    album = AlbumSerializer(read_only=True)
    featured_artists = ArtistSerializer(many=True, read_only=True)
    duration_formatted = serializers.ReadOnlyField()
    
    class Meta:
        model = Track
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserLibrarySerializer(serializers.ModelSerializer):
    """User library serializer"""
    
    user = serializers.ReadOnlyField(source='user.username')
    total_artists = serializers.ReadOnlyField()
    total_albums = serializers.ReadOnlyField()
    total_tracks = serializers.ReadOnlyField()
    total_play_time_formatted = serializers.ReadOnlyField()
    
    class Meta:
        model = UserLibrary
        fields = [
            'id', 'user', 'total_artists', 'total_albums',
            'total_tracks', 'total_play_time_ms', 'total_play_time_formatted',
            'spotify_connected', 'auto_sync', 'created_at', 'last_sync'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class PlaylistSerializer(serializers.ModelSerializer):
    """Playlist serializer"""
    
    user = serializers.ReadOnlyField(source='user.username')
    track_count = serializers.ReadOnlyField()
    total_duration_ms = serializers.ReadOnlyField()
    
    class Meta:
        model = Playlist
        fields = [
            'id', 'user', 'name', 'description', 'visibility',
            'track_count', 'total_duration_ms', 'cover_image',
            'tags', 'play_count', 'like_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'play_count', 'like_count', 'created_at', 'updated_at']


class PlaylistTrackSerializer(serializers.ModelSerializer):
    """Playlist track serializer"""
    
    track = TrackListSerializer(read_only=True)
    track_id = serializers.UUIDField(write_only=True)
    added_by = serializers.ReadOnlyField(source='added_by.username')
    
    class Meta:
        model = PlaylistTrack
        fields = [
            'id', 'track', 'track_id', 'position',
            'added_by', 'added_at'
        ]
        read_only_fields = ['id', 'added_by', 'added_at']


class ListeningHistorySerializer(serializers.ModelSerializer):
    """Listening history serializer"""
    
    user = serializers.ReadOnlyField(source='user.username')
    track = TrackListSerializer(read_only=True)
    track_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = ListeningHistory
        fields = [
            'id', 'user', 'track', 'track_id', 'played_at',
            'duration_played_ms', 'completed', 'skipped',
            'source', 'source_id', 'device_type'
        ]
        read_only_fields = ['id', 'user', 'played_at']


class ListeningStatsSerializer(serializers.ModelSerializer):
    """Listening statistics serializer"""
    
    user = serializers.ReadOnlyField(source='user.username')
    
    class Meta:
        model = ListeningStats
        fields = [
            'id', 'user', 'period', 'period_date',
            'total_tracks_played', 'unique_tracks_played',
            'total_time_ms', 'top_tracks', 'top_artists',
            'top_albums', 'top_genres', 'peak_hour',
            'device_breakdown', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']