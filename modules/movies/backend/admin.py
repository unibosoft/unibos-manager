"""
Movies Module Admin Configuration
"""

from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Avg, Count
from .models import (
    Genre, Movie, Collection, CollectionItem,
    WatchList, UserRating, PersonalArchive, WatchHistory
)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'tmdb_id', 'movie_count']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    
    def movie_count(self, obj):
        return obj.movies.count()
    movie_count.short_description = 'movies'


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'content_type', 'release_date', 'tmdb_rating',
        'user_rating_avg', 'popularity', 'poster_thumbnail'
    ]
    list_filter = ['content_type', 'status', 'genres', 'release_date']
    search_fields = ['title', 'original_title', 'tmdb_id', 'imdb_id']
    filter_horizontal = ['genres']
    readonly_fields = [
        'id', 'created_at', 'updated_at', 'last_api_sync',
        'average_user_rating', 'user_rating_count'
    ]
    date_hierarchy = 'release_date'
    ordering = ['-popularity']
    
    fieldsets = (
        ('basic information', {
            'fields': (
                'id', 'tmdb_id', 'imdb_id', 'title', 'original_title',
                'content_type', 'status'
            )
        }),
        ('content', {
            'fields': ('overview', 'tagline', 'genres')
        }),
        ('media', {
            'fields': ('poster_path', 'backdrop_path', 'trailer_url')
        }),
        ('details', {
            'fields': (
                'release_date', 'runtime', 'budget', 'revenue',
                'production_companies', 'production_countries', 'spoken_languages'
            )
        }),
        ('ratings', {
            'fields': (
                'tmdb_rating', 'tmdb_vote_count', 'popularity',
                'average_user_rating', 'user_rating_count'
            )
        }),
        ('series info', {
            'fields': ('number_of_seasons', 'number_of_episodes', 'episode_runtime'),
            'classes': ('collapse',)
        }),
        ('metadata', {
            'fields': ('api_data', 'created_at', 'updated_at', 'last_api_sync'),
            'classes': ('collapse',)
        })
    )
    
    def poster_thumbnail(self, obj):
        if obj.poster_path:
            return format_html(
                '<img src="{}" width="50" height="75" />',
                obj.poster_path
            )
        return '-'
    poster_thumbnail.short_description = 'poster'
    
    def user_rating_avg(self, obj):
        avg = obj.user_ratings.aggregate(avg=Avg('rating'))['avg']
        return f"{avg:.1f}" if avg else '-'
    user_rating_avg.short_description = 'user rating'
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('genres')


class CollectionItemInline(admin.TabularInline):
    model = CollectionItem
    extra = 0
    fields = ['movie', 'position', 'notes']
    ordering = ['position']


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'user', 'visibility', 'movie_count',
        'view_count', 'like_count', 'created_at'
    ]
    list_filter = ['visibility', 'created_at']
    search_fields = ['name', 'description', 'user__username']
    readonly_fields = ['id', 'view_count', 'like_count', 'created_at', 'updated_at']
    inlines = [CollectionItemInline]
    
    def movie_count(self, obj):
        return obj.movies.count()
    movie_count.short_description = 'movies'


@admin.register(WatchList)
class WatchListAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'movie', 'status', 'priority',
        'current_progress', 'added_at', 'watched_at'
    ]
    list_filter = ['status', 'priority', 'added_at', 'watched_at']
    search_fields = ['user__username', 'movie__title', 'notes']
    readonly_fields = ['id', 'added_at', 'updated_at']
    date_hierarchy = 'added_at'
    
    def current_progress(self, obj):
        if obj.current_season and obj.current_episode:
            return f"S{obj.current_season}E{obj.current_episode}"
        return '-'
    current_progress.short_description = 'progress'


@admin.register(UserRating)
class UserRatingAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'movie', 'rating', 'has_review',
        'is_public', 'helpful_count', 'created_at'
    ]
    list_filter = ['rating', 'is_public', 'contains_spoilers', 'created_at']
    search_fields = ['user__username', 'movie__title', 'review_title', 'review_text']
    readonly_fields = ['id', 'helpful_count', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    def has_review(self, obj):
        return bool(obj.review_text)
    has_review.boolean = True
    has_review.short_description = 'reviewed'


@admin.register(PersonalArchive)
class PersonalArchiveAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'movie', 'format', 'quality',
        'file_size_gb', 'acquired_date', 'added_at'
    ]
    list_filter = ['format', 'quality', 'acquired_date', 'added_at']
    search_fields = ['user__username', 'movie__title', 'location', 'notes']
    readonly_fields = ['id', 'added_at', 'updated_at']
    date_hierarchy = 'acquired_date'


@admin.register(WatchHistory)
class WatchHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'movie', 'started_at', 'duration_minutes',
        'progress_percentage', 'completed', 'device_type'
    ]
    list_filter = ['completed', 'device_type', 'started_at']
    search_fields = ['user__username', 'movie__title']
    readonly_fields = ['id', 'ip_address']
    date_hierarchy = 'started_at'