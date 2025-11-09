"""
Music Module Admin Configuration
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Artist, Album, Track, UserLibrary,
    Playlist, ListeningHistory, ListeningStats
)


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ['name', 'popularity', 'followers', 'album_count', 'track_count']
    search_fields = ['name', 'spotify_id']
    list_filter = ['popularity', 'country']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ['name', 'artist', 'album_type', 'release_date', 'total_tracks', 'popularity']
    search_fields = ['name', 'artist__name', 'spotify_id']
    list_filter = ['album_type', 'release_date']
    date_hierarchy = 'release_date'


@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ['name', 'artist', 'album', 'duration_formatted', 'popularity', 'explicit']
    search_fields = ['name', 'artist__name', 'album__name', 'spotify_id']
    list_filter = ['explicit', 'popularity']


@admin.register(UserLibrary)
class UserLibraryAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_artists', 'total_albums', 'total_tracks', 'spotify_connected']
    search_fields = ['user__username']
    list_filter = ['spotify_connected', 'auto_sync']


@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'visibility', 'track_count', 'play_count', 'created_at']
    search_fields = ['name', 'user__username']
    list_filter = ['visibility', 'created_at']
    date_hierarchy = 'created_at'


@admin.register(ListeningHistory)
class ListeningHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'track', 'played_at', 'completed', 'skipped', 'device_type']
    search_fields = ['user__username', 'track__name']
    list_filter = ['completed', 'skipped', 'device_type', 'played_at']
    date_hierarchy = 'played_at'


@admin.register(ListeningStats)
class ListeningStatsAdmin(admin.ModelAdmin):
    list_display = ['user', 'period', 'period_date', 'total_tracks_played', 'unique_tracks_played']
    search_fields = ['user__username']
    list_filter = ['period', 'period_date']
    date_hierarchy = 'period_date'