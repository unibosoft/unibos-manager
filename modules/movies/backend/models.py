"""
Movies Module Models
Secure and scalable models for movie/series collection management
"""

from django.db import models
from django.contrib.auth import get_user_model
# Use Django's built-in JSONField for database compatibility
# ArrayField functionality will be simulated using JSONField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.db.models import Q, Avg, Count
import uuid
from typing import Optional

User = get_user_model()


class Genre(models.Model):
    """Movie/Series genres with TMDB mapping"""
    tmdb_id = models.IntegerField(unique=True, db_index=True)
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['slug']),
        ]
    
    def __str__(self):
        return self.name


class Movie(models.Model):
    """Core movie/series model with API integration"""
    
    CONTENT_TYPE_CHOICES = [
        ('movie', 'movie'),
        ('series', 'tv series'),
        ('documentary', 'documentary'),
        ('anime', 'anime'),
    ]
    
    STATUS_CHOICES = [
        ('released', 'released'),
        ('upcoming', 'upcoming'),
        ('in_production', 'in production'),
        ('cancelled', 'cancelled'),
    ]
    
    # Unique identifiers
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tmdb_id = models.CharField(max_length=50, unique=True, null=True, blank=True, db_index=True)
    imdb_id = models.CharField(max_length=20, unique=True, null=True, blank=True, db_index=True)
    
    # Basic information
    title = models.CharField(max_length=500, db_index=True)
    original_title = models.CharField(max_length=500, blank=True)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES, default='movie', db_index=True)
    
    # Metadata
    overview = models.TextField(blank=True)
    tagline = models.CharField(max_length=500, blank=True)
    release_date = models.DateField(null=True, blank=True, db_index=True)
    runtime = models.IntegerField(null=True, blank=True, help_text="Runtime in minutes")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='released')
    
    # Media
    poster_path = models.URLField(max_length=500, blank=True)
    backdrop_path = models.URLField(max_length=500, blank=True)
    trailer_url = models.URLField(max_length=500, blank=True)
    
    # Relationships
    genres = models.ManyToManyField(Genre, related_name='movies', blank=True)
    
    # Production details
    production_companies = models.JSONField(
        default=list,
        blank=True,
        help_text="List of production companies"
    )
    production_countries = models.JSONField(
        default=list,
        blank=True,
        help_text="List of production countries"
    )
    spoken_languages = models.JSONField(
        default=list,
        blank=True,
        help_text="List of spoken languages"
    )
    
    # Financial data
    budget = models.BigIntegerField(null=True, blank=True)
    revenue = models.BigIntegerField(null=True, blank=True)
    
    # Ratings
    tmdb_rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    tmdb_vote_count = models.IntegerField(default=0)
    popularity = models.DecimalField(max_digits=7, decimal_places=3, null=True, blank=True)
    
    # Series specific fields
    number_of_seasons = models.IntegerField(null=True, blank=True)
    number_of_episodes = models.IntegerField(null=True, blank=True)
    episode_runtime = models.JSONField(
        default=list,
        blank=True,
        help_text="For series: typical episode runtime in minutes"
    )
    
    # Additional data from APIs
    api_data = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_api_sync = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-popularity', '-release_date']
        indexes = [
            models.Index(fields=['title', 'release_date']),
            models.Index(fields=['content_type', '-popularity']),
            models.Index(fields=['-created_at']),
            # GinIndex removed for SQLite compatibility
        ]
        verbose_name = 'movie/series'
        verbose_name_plural = 'movies/series'
    
    def __str__(self):
        year = self.release_date.year if self.release_date else "N/A"
        return f"{self.title} ({year})"
    
    @property
    def average_user_rating(self) -> Optional[float]:
        """Calculate average rating from user ratings"""
        avg = self.user_ratings.aggregate(avg_rating=Avg('rating'))['avg_rating']
        return round(avg, 1) if avg else None
    
    @property
    def user_rating_count(self) -> int:
        """Count of user ratings"""
        return self.user_ratings.count()


class Collection(models.Model):
    """User-created movie collections"""
    
    VISIBILITY_CHOICES = [
        ('private', 'private'),
        ('friends', 'friends only'),
        ('public', 'public'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='movie_collections')
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='private')
    
    movies = models.ManyToManyField(Movie, through='CollectionItem', related_name='collections')
    
    # Metadata
    cover_image = models.URLField(max_length=500, blank=True)
    tags = models.JSONField(
        default=list,
        blank=True,
        help_text="List of tags"
    )
    
    # Statistics
    view_count = models.IntegerField(default=0)
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
        unique_together = [['user', 'name']]
    
    def __str__(self):
        return f"{self.user.username}'s {self.name}"


class CollectionItem(models.Model):
    """Items in a collection with ordering"""
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    
    position = models.IntegerField(default=0)
    notes = models.TextField(blank=True)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['position', 'added_at']
        unique_together = [['collection', 'movie']]


class WatchList(models.Model):
    """User's watchlist with priority and categories"""
    
    STATUS_CHOICES = [
        ('want_to_watch', 'want to watch'),
        ('watching', 'currently watching'),
        ('watched', 'watched'),
        ('dropped', 'dropped'),
        ('on_hold', 'on hold'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'low priority'),
        ('medium', 'medium priority'),
        ('high', 'high priority'),
        ('urgent', 'must watch'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlist')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='watchlisted_by')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='want_to_watch', db_index=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    # Progress tracking (for series)
    current_season = models.IntegerField(null=True, blank=True)
    current_episode = models.IntegerField(null=True, blank=True)
    
    # Personal notes
    notes = models.TextField(blank=True)
    tags = models.JSONField(
        default=list,
        blank=True,
        help_text="List of tags"
    )
    
    # Timestamps
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    watched_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-priority', '-added_at']
        indexes = [
            models.Index(fields=['user', 'status', '-priority']),
            models.Index(fields=['user', '-added_at']),
        ]
        unique_together = [['user', 'movie']]
    
    def __str__(self):
        return f"{self.user.username} - {self.movie.title} ({self.status})"


class UserRating(models.Model):
    """User ratings and reviews for movies"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='movie_ratings')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='user_ratings')
    
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        validators=[MinValueValidator(0.5), MaxValueValidator(10.0)]
    )
    
    # Review
    review_title = models.CharField(max_length=200, blank=True)
    review_text = models.TextField(blank=True)
    contains_spoilers = models.BooleanField(default=False)
    
    # Metadata
    is_public = models.BooleanField(default=True)
    helpful_count = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['movie', '-rating']),
            models.Index(fields=['is_public', '-helpful_count']),
        ]
        unique_together = [['user', 'movie']]
    
    def __str__(self):
        return f"{self.user.username} rated {self.movie.title}: {self.rating}/10"


class PersonalArchive(models.Model):
    """Track personal movie archive/library"""
    
    QUALITY_CHOICES = [
        ('4k', '4K Ultra HD'),
        ('1080p', '1080p Full HD'),
        ('720p', '720p HD'),
        ('dvd', 'DVD Quality'),
        ('other', 'Other'),
    ]
    
    FORMAT_CHOICES = [
        ('digital', 'Digital'),
        ('bluray', 'Blu-ray'),
        ('dvd', 'DVD'),
        ('vhs', 'VHS'),
        ('streaming', 'Streaming Service'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='movie_archive')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='archived_by')
    
    # Archive details
    format = models.CharField(max_length=20, choices=FORMAT_CHOICES)
    quality = models.CharField(max_length=20, choices=QUALITY_CHOICES, null=True, blank=True)
    location = models.CharField(max_length=500, blank=True, help_text="Physical or digital location")
    
    # Additional metadata
    file_size_gb = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    subtitles = models.JSONField(
        default=list,
        blank=True,
        help_text="Available subtitle languages"
    )
    audio_languages = models.JSONField(
        default=list,
        blank=True,
        help_text="Available audio languages"
    )
    
    # Personal info
    notes = models.TextField(blank=True)
    tags = models.JSONField(
        default=list,
        blank=True,
        help_text="List of tags"
    )
    
    # Timestamps
    acquired_date = models.DateField(default=timezone.now)
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-added_at']
        indexes = [
            models.Index(fields=['user', '-added_at']),
            models.Index(fields=['format', 'quality']),
        ]
        unique_together = [['user', 'movie', 'format']]
    
    def __str__(self):
        return f"{self.user.username}'s {self.format} copy of {self.movie.title}"


class WatchHistory(models.Model):
    """Track watching history and sessions"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watch_history')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='watch_sessions')
    
    # Watch session details
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.IntegerField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    
    # Progress
    progress_percentage = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Series specific
    season = models.IntegerField(null=True, blank=True)
    episode = models.IntegerField(null=True, blank=True)
    
    # Device/location info
    device_type = models.CharField(max_length=50, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['user', '-started_at']),
            models.Index(fields=['movie', '-started_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} watched {self.movie.title} on {self.started_at}"