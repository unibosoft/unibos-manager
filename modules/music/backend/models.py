"""
Music Module Models
Secure and scalable models for music collection management
"""

from django.db import models
from django.contrib.auth import get_user_model
# Use Django's built-in JSONField for database compatibility
# ArrayField functionality will be simulated using JSONField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.db.models import Q, Count, Sum
import uuid
from typing import Optional
from datetime import timedelta

User = get_user_model()


class Artist(models.Model):
    """Artist/Band model with Spotify integration"""
    
    # Unique identifiers
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    spotify_id = models.CharField(max_length=100, unique=True, null=True, blank=True, db_index=True)
    
    # Basic information
    name = models.CharField(max_length=500, db_index=True)
    slug = models.SlugField(max_length=500, unique=True)
    
    # Metadata
    genres = models.JSONField(
        default=list,
        blank=True
    )
    popularity = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    followers = models.IntegerField(default=0)
    
    # Images
    image_url = models.URLField(max_length=500, blank=True)
    thumbnail_url = models.URLField(max_length=500, blank=True)
    
    # Additional info
    bio = models.TextField(blank=True)
    country = models.CharField(max_length=100, blank=True)
    formed_year = models.IntegerField(null=True, blank=True)
    
    # Social/External links
    spotify_url = models.URLField(max_length=500, blank=True)
    website_url = models.URLField(max_length=500, blank=True)
    
    # API data
    spotify_data = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_spotify_sync = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-popularity', 'name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['slug']),
            models.Index(fields=['-popularity']),
            # GinIndex removed for SQLite compatibility
        ]
    
    def __str__(self):
        return self.name
    
    @property
    def album_count(self) -> int:
        """Count of albums by this artist"""
        return self.albums.count()
    
    @property
    def track_count(self) -> int:
        """Count of tracks by this artist"""
        return self.tracks.count()


class Album(models.Model):
    """Album model with Spotify integration"""
    
    ALBUM_TYPE_CHOICES = [
        ('album', 'album'),
        ('single', 'single'),
        ('compilation', 'compilation'),
        ('ep', 'ep'),
    ]
    
    # Unique identifiers
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    spotify_id = models.CharField(max_length=100, unique=True, null=True, blank=True, db_index=True)
    
    # Basic information
    name = models.CharField(max_length=500, db_index=True)
    album_type = models.CharField(max_length=20, choices=ALBUM_TYPE_CHOICES, default='album')
    
    # Relationships
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='albums')
    featured_artists = models.ManyToManyField(Artist, related_name='featured_albums', blank=True)
    
    # Metadata
    release_date = models.DateField(null=True, blank=True, db_index=True)
    total_tracks = models.IntegerField(default=0)
    duration_ms = models.IntegerField(default=0, help_text="Total duration in milliseconds")
    
    # Images
    cover_url = models.URLField(max_length=500, blank=True)
    thumbnail_url = models.URLField(max_length=500, blank=True)
    
    # Additional info
    label = models.CharField(max_length=200, blank=True)
    genres = models.JSONField(
        default=list,
        blank=True
    )
    popularity = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # External links
    spotify_url = models.URLField(max_length=500, blank=True)
    
    # API data
    spotify_data = models.JSONField(default=dict, blank=True)
    
    # Open source artwork support
    artwork_file = models.FileField(upload_to='music/artwork/', null=True, blank=True)
    artwork_source = models.CharField(max_length=200, blank=True, help_text="Source of open artwork")
    artwork_license = models.CharField(max_length=100, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_spotify_sync = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-release_date', 'name']
        indexes = [
            models.Index(fields=['name', 'artist']),
            models.Index(fields=['-release_date']),
            models.Index(fields=['-popularity']),
            # GinIndex removed for SQLite compatibility
        ]
    
    def __str__(self):
        return f"{self.name} by {self.artist.name}"
    
    @property
    def duration_formatted(self) -> str:
        """Format duration as HH:MM:SS"""
        seconds = self.duration_ms // 1000
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        return f"{minutes}:{seconds:02d}"


class Track(models.Model):
    """Track model with Spotify integration"""
    
    # Unique identifiers
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    spotify_id = models.CharField(max_length=100, unique=True, null=True, blank=True, db_index=True)
    isrc = models.CharField(max_length=20, null=True, blank=True, db_index=True, help_text="International Standard Recording Code")
    
    # Basic information
    name = models.CharField(max_length=500, db_index=True)
    track_number = models.IntegerField(default=1)
    disc_number = models.IntegerField(default=1)
    
    # Relationships
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='tracks')
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='tracks')
    featured_artists = models.ManyToManyField(Artist, related_name='featured_tracks', blank=True)
    
    # Metadata
    duration_ms = models.IntegerField(help_text="Duration in milliseconds")
    explicit = models.BooleanField(default=False)
    popularity = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Audio features (from Spotify API)
    acousticness = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    danceability = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    energy = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    instrumentalness = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    key = models.IntegerField(null=True, blank=True)  # Musical key
    liveness = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    loudness = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # in dB
    mode = models.IntegerField(null=True, blank=True)  # Major=1, Minor=0
    speechiness = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    tempo = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)  # BPM
    time_signature = models.IntegerField(null=True, blank=True)
    valence = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)  # Musical positivity
    
    # External links
    spotify_url = models.URLField(max_length=500, blank=True)
    preview_url = models.URLField(max_length=500, blank=True, help_text="30-second preview URL")
    
    # API data
    spotify_data = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['album', 'disc_number', 'track_number']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['album', 'track_number']),
            models.Index(fields=['-popularity']),
            # GinIndex removed for SQLite compatibility
        ]
        unique_together = [['album', 'disc_number', 'track_number']]
    
    def __str__(self):
        return f"{self.name} by {self.artist.name}"
    
    @property
    def duration_formatted(self) -> str:
        """Format duration as MM:SS"""
        seconds = self.duration_ms // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes}:{seconds:02d}"


class UserLibrary(models.Model):
    """User's music library"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='music_library')
    
    # Library content
    artists = models.ManyToManyField(Artist, through='UserArtist', related_name='in_libraries')
    albums = models.ManyToManyField(Album, through='UserAlbum', related_name='in_libraries')
    tracks = models.ManyToManyField(Track, through='UserTrack', related_name='in_libraries')
    
    # Settings
    spotify_connected = models.BooleanField(default=False)
    spotify_user_id = models.CharField(max_length=100, blank=True)
    auto_sync = models.BooleanField(default=True)
    
    # Statistics
    total_play_time_ms = models.BigIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_sync = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name_plural = 'user libraries'
    
    def __str__(self):
        return f"{self.user.username}'s music library"
    
    @property
    def total_artists(self) -> int:
        """Total number of artists in library"""
        return self.artists.count()
    
    @property
    def total_albums(self) -> int:
        """Total number of albums in library"""
        return self.albums.count()
    
    @property
    def total_tracks(self) -> int:
        """Total number of tracks in library"""
        return self.tracks.count()
    
    @property
    def total_play_time_formatted(self) -> str:
        """Format total play time as days:hours:minutes"""
        seconds = self.total_play_time_ms // 1000
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        minutes = (seconds % 3600) // 60
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"


class UserArtist(models.Model):
    """User's relationship with artists"""
    
    library = models.ForeignKey(UserLibrary, on_delete=models.CASCADE)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    
    # User interaction
    is_favorite = models.BooleanField(default=False)
    play_count = models.IntegerField(default=0)
    
    # Timestamps
    added_at = models.DateTimeField(auto_now_add=True)
    last_played = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = [['library', 'artist']]
        ordering = ['-is_favorite', '-play_count']


class UserAlbum(models.Model):
    """User's relationship with albums"""
    
    library = models.ForeignKey(UserLibrary, on_delete=models.CASCADE)
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    
    # User interaction
    is_favorite = models.BooleanField(default=False)
    play_count = models.IntegerField(default=0)
    rating = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    # Timestamps
    added_at = models.DateTimeField(auto_now_add=True)
    last_played = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = [['library', 'album']]
        ordering = ['-is_favorite', '-added_at']


class UserTrack(models.Model):
    """User's relationship with tracks"""
    
    library = models.ForeignKey(UserLibrary, on_delete=models.CASCADE)
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    
    # User interaction
    is_favorite = models.BooleanField(default=False)
    play_count = models.IntegerField(default=0)
    skip_count = models.IntegerField(default=0)
    
    # Timestamps
    added_at = models.DateTimeField(auto_now_add=True)
    last_played = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = [['library', 'track']]
        ordering = ['-is_favorite', '-play_count']


class Playlist(models.Model):
    """User-created playlists"""
    
    VISIBILITY_CHOICES = [
        ('private', 'private'),
        ('public', 'public'),
        ('collaborative', 'collaborative'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='playlists')
    
    # Basic info
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='private')
    
    # Content
    tracks = models.ManyToManyField(Track, through='PlaylistTrack', related_name='in_playlists')
    
    # Metadata
    cover_image = models.ImageField(upload_to='playlists/', null=True, blank=True)
    tags = models.JSONField(
        default=list,
        blank=True
    )
    
    # Collaboration
    collaborators = models.ManyToManyField(User, related_name='collaborative_playlists', blank=True)
    
    # Statistics
    play_count = models.IntegerField(default=0)
    like_count = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user', '-updated_at']),
            models.Index(fields=['visibility', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.name} by {self.user.username}"
    
    @property
    def total_duration_ms(self) -> int:
        """Calculate total playlist duration"""
        return self.tracks.aggregate(total=Sum('duration_ms'))['total'] or 0
    
    @property
    def track_count(self) -> int:
        """Number of tracks in playlist"""
        return self.tracks.count()


class PlaylistTrack(models.Model):
    """Tracks in a playlist with ordering"""
    
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    
    position = models.IntegerField(default=0)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['position']
        unique_together = [['playlist', 'track', 'position']]


class ListeningHistory(models.Model):
    """Track user listening history"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listening_history')
    track = models.ForeignKey(Track, on_delete=models.CASCADE, related_name='play_history')
    
    # Play session info
    played_at = models.DateTimeField(auto_now_add=True)
    duration_played_ms = models.IntegerField(help_text="How long the track was played")
    completed = models.BooleanField(default=False, help_text="Was the track played to completion")
    skipped = models.BooleanField(default=False)
    
    # Context
    source = models.CharField(max_length=50, blank=True, help_text="Playlist, album, search, etc.")
    source_id = models.CharField(max_length=100, blank=True)
    device_type = models.CharField(max_length=50, blank=True)
    
    # Location (optional)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['-played_at']
        indexes = [
            models.Index(fields=['user', '-played_at']),
            models.Index(fields=['track', '-played_at']),
            models.Index(fields=['user', 'track', '-played_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} played {self.track.name} at {self.played_at}"


class ListeningStats(models.Model):
    """Aggregated listening statistics"""
    
    PERIOD_CHOICES = [
        ('daily', 'daily'),
        ('weekly', 'weekly'),
        ('monthly', 'monthly'),
        ('yearly', 'yearly'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listening_stats')
    
    # Period
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES)
    period_date = models.DateField()
    
    # Statistics
    total_tracks_played = models.IntegerField(default=0)
    unique_tracks_played = models.IntegerField(default=0)
    total_time_ms = models.BigIntegerField(default=0)
    
    # Top items
    top_tracks = models.JSONField(default=list)  # List of track IDs with play counts
    top_artists = models.JSONField(default=list)  # List of artist IDs with play counts
    top_albums = models.JSONField(default=list)  # List of album IDs with play counts
    top_genres = models.JSONField(default=list)  # List of genres with counts
    
    # Listening patterns
    peak_hour = models.IntegerField(null=True, blank=True)  # 0-23
    device_breakdown = models.JSONField(default=dict)  # Device type: count
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-period_date']
        indexes = [
            models.Index(fields=['user', 'period', '-period_date']),
        ]
        unique_together = [['user', 'period', 'period_date']]
    
    def __str__(self):
        return f"{self.user.username}'s {self.period} stats for {self.period_date}"