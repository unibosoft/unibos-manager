"""
Movies Module Serializers
RESTful API serializers with security and validation
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from .models import (
    Genre, Movie, Collection, CollectionItem,
    WatchList, UserRating, PersonalArchive, WatchHistory
)

User = get_user_model()


class GenreSerializer(serializers.ModelSerializer):
    """Genre serializer"""
    
    class Meta:
        model = Genre
        fields = ['id', 'tmdb_id', 'name', 'slug']
        read_only_fields = ['id']


class MovieListSerializer(serializers.ModelSerializer):
    """Lightweight movie serializer for lists"""
    
    genres = GenreSerializer(many=True, read_only=True)
    average_user_rating = serializers.ReadOnlyField()
    user_rating_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Movie
        fields = [
            'id', 'tmdb_id', 'imdb_id', 'title', 'original_title',
            'content_type', 'release_date', 'runtime', 'poster_path',
            'tmdb_rating', 'average_user_rating', 'user_rating_count',
            'genres', 'popularity'
        ]
        read_only_fields = ['id']


class MovieDetailSerializer(serializers.ModelSerializer):
    """Detailed movie serializer with all information"""
    
    genres = GenreSerializer(many=True, read_only=True)
    average_user_rating = serializers.ReadOnlyField()
    user_rating_count = serializers.ReadOnlyField()
    user_watchlist_status = serializers.SerializerMethodField()
    user_rating = serializers.SerializerMethodField()
    in_user_archive = serializers.SerializerMethodField()
    
    class Meta:
        model = Movie
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_user_watchlist_status(self, obj):
        """Get current user's watchlist status for this movie"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            watchlist = WatchList.objects.filter(
                user=request.user,
                movie=obj
            ).first()
            if watchlist:
                return {
                    'status': watchlist.status,
                    'priority': watchlist.priority,
                    'added_at': watchlist.added_at
                }
        return None
    
    def get_user_rating(self, obj):
        """Get current user's rating for this movie"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            rating = UserRating.objects.filter(
                user=request.user,
                movie=obj
            ).first()
            if rating:
                return {
                    'rating': float(rating.rating),
                    'review_title': rating.review_title,
                    'has_review': bool(rating.review_text),
                    'created_at': rating.created_at
                }
        return None
    
    def get_in_user_archive(self, obj):
        """Check if movie is in user's archive"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return PersonalArchive.objects.filter(
                user=request.user,
                movie=obj
            ).exists()
        return False


class CollectionItemSerializer(serializers.ModelSerializer):
    """Collection item serializer"""
    
    movie = MovieListSerializer(read_only=True)
    movie_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = CollectionItem
        fields = ['id', 'movie', 'movie_id', 'position', 'notes', 'added_at']
        read_only_fields = ['id', 'added_at']


class CollectionSerializer(serializers.ModelSerializer):
    """Collection serializer with items"""
    
    user = serializers.ReadOnlyField(source='user.username')
    items = CollectionItemSerializer(source='collectionitem_set', many=True, read_only=True)
    movie_count = serializers.IntegerField(source='movies.count', read_only=True)
    
    class Meta:
        model = Collection
        fields = [
            'id', 'user', 'name', 'description', 'visibility',
            'items', 'movie_count', 'cover_image', 'tags',
            'view_count', 'like_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'view_count', 'like_count', 'created_at', 'updated_at']
    
    def validate_name(self, value):
        """Ensure collection name is unique for user"""
        request = self.context.get('request')
        if request and request.user:
            exists = Collection.objects.filter(
                user=request.user,
                name=value
            ).exclude(pk=self.instance.pk if self.instance else None).exists()
            if exists:
                raise serializers.ValidationError("you already have a collection with this name")
        return value


class WatchListSerializer(serializers.ModelSerializer):
    """Watchlist serializer"""
    
    movie = MovieListSerializer(read_only=True)
    movie_id = serializers.UUIDField(write_only=True)
    user = serializers.ReadOnlyField(source='user.username')
    
    class Meta:
        model = WatchList
        fields = [
            'id', 'user', 'movie', 'movie_id', 'status', 'priority',
            'current_season', 'current_episode', 'notes', 'tags',
            'added_at', 'updated_at', 'watched_at'
        ]
        read_only_fields = ['id', 'user', 'added_at', 'updated_at']
    
    def validate(self, data):
        """Validate watchlist entry"""
        request = self.context.get('request')
        movie_id = data.get('movie_id')
        
        if request and request.user and movie_id:
            # Check if already in watchlist
            exists = WatchList.objects.filter(
                user=request.user,
                movie_id=movie_id
            ).exclude(pk=self.instance.pk if self.instance else None).exists()
            if exists:
                raise serializers.ValidationError("this movie is already in your watchlist")
        
        # Auto-set watched_at when status changes to watched
        if data.get('status') == 'watched' and not self.instance:
            data['watched_at'] = timezone.now()
        elif self.instance and data.get('status') == 'watched' and self.instance.status != 'watched':
            data['watched_at'] = timezone.now()
        
        return data


class UserRatingSerializer(serializers.ModelSerializer):
    """User rating and review serializer"""
    
    user = serializers.ReadOnlyField(source='user.username')
    movie_title = serializers.ReadOnlyField(source='movie.title')
    
    class Meta:
        model = UserRating
        fields = [
            'id', 'user', 'movie', 'movie_title', 'rating',
            'review_title', 'review_text', 'contains_spoilers',
            'is_public', 'helpful_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'movie_title', 'helpful_count', 'created_at', 'updated_at']
    
    def validate_rating(self, value):
        """Validate rating is within range"""
        if value < 0.5 or value > 10:
            raise serializers.ValidationError("rating must be between 0.5 and 10")
        return value
    
    def validate(self, data):
        """Validate rating"""
        request = self.context.get('request')
        movie = data.get('movie')
        
        if request and request.user and movie:
            # Check if already rated
            exists = UserRating.objects.filter(
                user=request.user,
                movie=movie
            ).exclude(pk=self.instance.pk if self.instance else None).exists()
            if exists:
                raise serializers.ValidationError("you have already rated this movie")
        
        return data


class PersonalArchiveSerializer(serializers.ModelSerializer):
    """Personal archive serializer"""
    
    user = serializers.ReadOnlyField(source='user.username')
    movie = MovieListSerializer(read_only=True)
    movie_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = PersonalArchive
        fields = [
            'id', 'user', 'movie', 'movie_id', 'format', 'quality',
            'location', 'file_size_gb', 'subtitles', 'audio_languages',
            'notes', 'tags', 'acquired_date', 'added_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'added_at', 'updated_at']
    
    def validate(self, data):
        """Validate archive entry"""
        request = self.context.get('request')
        movie_id = data.get('movie_id')
        format_type = data.get('format')
        
        if request and request.user and movie_id and format_type:
            # Check if already in archive with same format
            exists = PersonalArchive.objects.filter(
                user=request.user,
                movie_id=movie_id,
                format=format_type
            ).exclude(pk=self.instance.pk if self.instance else None).exists()
            if exists:
                raise serializers.ValidationError(
                    f"you already have this movie in {format_type} format"
                )
        
        return data


class WatchHistorySerializer(serializers.ModelSerializer):
    """Watch history serializer"""
    
    user = serializers.ReadOnlyField(source='user.username')
    movie = MovieListSerializer(read_only=True)
    movie_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = WatchHistory
        fields = [
            'id', 'user', 'movie', 'movie_id', 'started_at', 'ended_at',
            'duration_minutes', 'completed', 'progress_percentage',
            'season', 'episode', 'device_type'
        ]
        read_only_fields = ['id', 'user', 'started_at']
    
    def create(self, validated_data):
        """Create watch history entry"""
        # Set IP address from request
        request = self.context.get('request')
        if request:
            validated_data['ip_address'] = self.get_client_ip(request)
        
        return super().create(validated_data)
    
    def get_client_ip(self, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class MovieSearchSerializer(serializers.Serializer):
    """Serializer for movie search parameters"""
    
    query = serializers.CharField(required=False, allow_blank=True)
    content_type = serializers.ChoiceField(
        choices=['movie', 'series', 'documentary', 'anime'],
        required=False
    )
    genres = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    year_from = serializers.IntegerField(required=False, min_value=1900)
    year_to = serializers.IntegerField(required=False)
    rating_min = serializers.DecimalField(
        required=False,
        max_digits=3,
        decimal_places=1,
        min_value=0,
        max_value=10
    )
    sort_by = serializers.ChoiceField(
        choices=['popularity', 'release_date', 'rating', 'title'],
        default='popularity'
    )