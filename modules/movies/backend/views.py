"""
Movies Module Views
Secure and performant API views with proper authentication and permissions
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Avg, Count, Prefetch
from django.utils import timezone
from django.core.cache import cache
from django.db import transaction
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import logging

from .models import (
    Genre, Movie, Collection, CollectionItem,
    WatchList, UserRating, PersonalArchive, WatchHistory
)
from .serializers import (
    GenreSerializer, MovieListSerializer, MovieDetailSerializer,
    CollectionSerializer, CollectionItemSerializer, WatchListSerializer,
    UserRatingSerializer, PersonalArchiveSerializer, WatchHistorySerializer,
    MovieSearchSerializer
)
from .services import TMDBService, OMDBService
from .permissions import IsOwnerOrReadOnly, IsPublicOrOwner

logger = logging.getLogger(__name__)


class MovieViewSet(viewsets.ModelViewSet):
    """
    Movie/Series management with API integration
    Supports TMDB/OMDB synchronization and advanced search
    """
    
    queryset = Movie.objects.select_related().prefetch_related('genres')
    serializer_class = MovieDetailSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['content_type', 'status', 'genres']
    search_fields = ['title', 'original_title', 'overview', 'tmdb_id', 'imdb_id']
    ordering_fields = ['popularity', 'release_date', 'tmdb_rating', 'created_at']
    ordering = ['-popularity']
    
    def get_serializer_class(self):
        """Use lightweight serializer for list views"""
        if self.action == 'list':
            return MovieListSerializer
        return MovieDetailSerializer
    
    def get_queryset(self):
        """Optimize queryset based on action"""
        queryset = super().get_queryset()
        
        if self.action == 'list':
            # Optimize for list view
            queryset = queryset.select_related().prefetch_related('genres')
        else:
            # Add user-specific data for detail view
            if self.request.user.is_authenticated:
                queryset = queryset.prefetch_related(
                    Prefetch(
                        'watchlisted_by',
                        queryset=WatchList.objects.filter(user=self.request.user),
                        to_attr='user_watchlist'
                    ),
                    Prefetch(
                        'user_ratings',
                        queryset=UserRating.objects.filter(user=self.request.user),
                        to_attr='user_rating_obj'
                    )
                )
        
        return queryset
    
    @action(detail=False, methods=['post'])
    def search_external(self, request):
        """
        Search movies from external APIs (TMDB/OMDB)
        """
        query = request.data.get('query', '')
        source = request.data.get('source', 'tmdb')  # tmdb or omdb
        
        if not query:
            return Response(
                {'error': 'query parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Cache key for search results
        cache_key = f"movie_search_{source}_{query}"
        cached_results = cache.get(cache_key)
        
        if cached_results:
            return Response(cached_results)
        
        try:
            if source == 'tmdb':
                service = TMDBService()
                results = service.search_movies(query)
            elif source == 'omdb':
                service = OMDBService()
                results = service.search_movies(query)
            else:
                return Response(
                    {'error': 'invalid source. use tmdb or omdb'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Cache results for 1 hour
            cache.set(cache_key, results, 3600)
            
            return Response(results)
        
        except Exception as e:
            logger.error(f"External search error: {str(e)}")
            return Response(
                {'error': 'failed to search external api'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
    
    @action(detail=False, methods=['post'])
    def import_from_api(self, request):
        """
        Import movie data from external API
        """
        external_id = request.data.get('external_id')
        source = request.data.get('source', 'tmdb')
        
        if not external_id:
            return Response(
                {'error': 'external_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            with transaction.atomic():
                if source == 'tmdb':
                    service = TMDBService()
                    movie_data = service.get_movie_details(external_id)
                    movie = service.create_or_update_movie(movie_data)
                elif source == 'omdb':
                    service = OMDBService()
                    movie_data = service.get_movie_details(external_id)
                    movie = service.create_or_update_movie(movie_data)
                else:
                    return Response(
                        {'error': 'invalid source'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                serializer = MovieDetailSerializer(movie, context={'request': request})
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            logger.error(f"Import error: {str(e)}")
            return Response(
                {'error': 'failed to import movie'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def sync_with_api(self, request, pk=None):
        """
        Sync movie data with external API
        """
        movie = self.get_object()
        
        try:
            if movie.tmdb_id:
                service = TMDBService()
                updated_data = service.get_movie_details(movie.tmdb_id)
                movie = service.create_or_update_movie(updated_data, movie)
            elif movie.imdb_id:
                service = OMDBService()
                updated_data = service.get_movie_details(movie.imdb_id)
                movie = service.create_or_update_movie(updated_data, movie)
            else:
                return Response(
                    {'error': 'no external id found for syncing'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            movie.last_api_sync = timezone.now()
            movie.save()
            
            serializer = MovieDetailSerializer(movie, context={'request': request})
            return Response(serializer.data)
        
        except Exception as e:
            logger.error(f"Sync error: {str(e)}")
            return Response(
                {'error': 'failed to sync movie data'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def trending(self, request):
        """
        Get trending movies based on popularity and recent activity
        """
        timeframe = request.query_params.get('timeframe', 'week')  # day, week, month
        limit = int(request.query_params.get('limit', 20))
        
        # Calculate date threshold
        if timeframe == 'day':
            date_threshold = timezone.now() - timezone.timedelta(days=1)
        elif timeframe == 'month':
            date_threshold = timezone.now() - timezone.timedelta(days=30)
        else:  # week
            date_threshold = timezone.now() - timezone.timedelta(days=7)
        
        # Get trending movies based on recent ratings and watchlist additions
        trending = Movie.objects.annotate(
            recent_ratings=Count(
                'user_ratings',
                filter=Q(user_ratings__created_at__gte=date_threshold)
            ),
            recent_watchlist=Count(
                'watchlisted_by',
                filter=Q(watchlisted_by__added_at__gte=date_threshold)
            ),
            trend_score=Count('user_ratings') + Count('watchlisted_by') * 0.5
        ).order_by('-trend_score', '-popularity')[:limit]
        
        serializer = MovieListSerializer(trending, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def recommendations(self, request):
        """
        Get personalized movie recommendations for authenticated user
        """
        if not request.user.is_authenticated:
            return Response(
                {'error': 'authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Get user's highly rated movies
        user_favorites = UserRating.objects.filter(
            user=request.user,
            rating__gte=7
        ).values_list('movie__genres', flat=True)
        
        if not user_favorites:
            # Return popular movies if no ratings
            recommendations = Movie.objects.order_by('-popularity')[:20]
        else:
            # Get movies with similar genres
            favorite_genres = set()
            for genres in user_favorites:
                favorite_genres.update(genres)
            
            recommendations = Movie.objects.filter(
                genres__in=favorite_genres
            ).exclude(
                Q(watchlisted_by__user=request.user) |
                Q(user_ratings__user=request.user)
            ).distinct().order_by('-tmdb_rating', '-popularity')[:20]
        
        serializer = MovieListSerializer(
            recommendations,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)


class CollectionViewSet(viewsets.ModelViewSet):
    """
    User movie collections management
    """
    
    serializer_class = CollectionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'tags']
    ordering_fields = ['created_at', 'updated_at', 'like_count']
    ordering = ['-updated_at']
    
    def get_queryset(self):
        """Get user's collections or public collections"""
        if self.action == 'list':
            # Show user's own collections and public collections
            return Collection.objects.filter(
                Q(user=self.request.user) | Q(visibility='public')
            ).select_related('user').prefetch_related('movies')
        return Collection.objects.filter(
            user=self.request.user
        ).select_related('user').prefetch_related('movies')
    
    def perform_create(self, serializer):
        """Set the user when creating collection"""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_movie(self, request, pk=None):
        """Add a movie to collection"""
        collection = self.get_object()
        movie_id = request.data.get('movie_id')
        position = request.data.get('position', 0)
        notes = request.data.get('notes', '')
        
        if not movie_id:
            return Response(
                {'error': 'movie_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            movie = Movie.objects.get(id=movie_id)
            
            # Check if movie already in collection
            if CollectionItem.objects.filter(
                collection=collection,
                movie=movie
            ).exists():
                return Response(
                    {'error': 'movie already in collection'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            item = CollectionItem.objects.create(
                collection=collection,
                movie=movie,
                position=position,
                notes=notes
            )
            
            serializer = CollectionItemSerializer(item)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        except Movie.DoesNotExist:
            return Response(
                {'error': 'movie not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['delete'])
    def remove_movie(self, request, pk=None):
        """Remove a movie from collection"""
        collection = self.get_object()
        movie_id = request.data.get('movie_id')
        
        if not movie_id:
            return Response(
                {'error': 'movie_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            item = CollectionItem.objects.get(
                collection=collection,
                movie_id=movie_id
            )
            item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        except CollectionItem.DoesNotExist:
            return Response(
                {'error': 'movie not in collection'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def reorder(self, request, pk=None):
        """Reorder movies in collection"""
        collection = self.get_object()
        positions = request.data.get('positions', {})
        
        with transaction.atomic():
            for movie_id, position in positions.items():
                CollectionItem.objects.filter(
                    collection=collection,
                    movie_id=movie_id
                ).update(position=position)
        
        return Response({'status': 'reordered'})


class WatchListViewSet(viewsets.ModelViewSet):
    """
    User watchlist management
    """
    
    serializer_class = WatchListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'priority']
    ordering_fields = ['priority', 'added_at', 'updated_at']
    ordering = ['-priority', '-added_at']
    
    def get_queryset(self):
        """Get user's watchlist"""
        return WatchList.objects.filter(
            user=self.request.user
        ).select_related('movie').prefetch_related('movie__genres')
    
    def perform_create(self, serializer):
        """Set the user when creating watchlist entry"""
        movie_id = serializer.validated_data.pop('movie_id')
        movie = Movie.objects.get(id=movie_id)
        serializer.save(user=self.request.user, movie=movie)
    
    def perform_update(self, serializer):
        """Handle status changes"""
        instance = serializer.save()
        
        # Auto-update watched_at when marked as watched
        if instance.status == 'watched' and not instance.watched_at:
            instance.watched_at = timezone.now()
            instance.save()
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get user's watchlist statistics"""
        stats = WatchList.objects.filter(user=request.user).aggregate(
            total=Count('id'),
            want_to_watch=Count('id', filter=Q(status='want_to_watch')),
            watching=Count('id', filter=Q(status='watching')),
            watched=Count('id', filter=Q(status='watched')),
            dropped=Count('id', filter=Q(status='dropped')),
            on_hold=Count('id', filter=Q(status='on_hold'))
        )
        
        return Response(stats)


class UserRatingViewSet(viewsets.ModelViewSet):
    """
    User ratings and reviews management
    """
    
    serializer_class = UserRatingSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['movie', 'is_public', 'contains_spoilers']
    ordering_fields = ['rating', 'created_at', 'helpful_count']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Get ratings based on visibility"""
        if self.request.user.is_authenticated:
            # Show own ratings and public ratings
            return UserRating.objects.filter(
                Q(user=self.request.user) | Q(is_public=True)
            ).select_related('user', 'movie')
        # Show only public ratings for anonymous users
        return UserRating.objects.filter(
            is_public=True
        ).select_related('user', 'movie')
    
    def perform_create(self, serializer):
        """Set the user when creating rating"""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_helpful(self, request, pk=None):
        """Mark a review as helpful"""
        rating = self.get_object()
        
        # Track helpful votes in cache to prevent duplicates
        cache_key = f"helpful_vote_{rating.id}_{request.user.id if request.user.is_authenticated else request.META.get('REMOTE_ADDR')}"
        
        if cache.get(cache_key):
            return Response(
                {'error': 'already marked as helpful'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        rating.helpful_count += 1
        rating.save()
        
        # Cache for 24 hours
        cache.set(cache_key, True, 86400)
        
        return Response({'helpful_count': rating.helpful_count})


class PersonalArchiveViewSet(viewsets.ModelViewSet):
    """
    Personal movie archive management
    """
    
    serializer_class = PersonalArchiveSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['format', 'quality']
    search_fields = ['movie__title', 'location', 'notes', 'tags']
    ordering_fields = ['acquired_date', 'added_at']
    ordering = ['-added_at']
    
    def get_queryset(self):
        """Get user's archive"""
        return PersonalArchive.objects.filter(
            user=self.request.user
        ).select_related('movie').prefetch_related('movie__genres')
    
    def perform_create(self, serializer):
        """Set the user when creating archive entry"""
        movie_id = serializer.validated_data.pop('movie_id')
        movie = Movie.objects.get(id=movie_id)
        serializer.save(user=self.request.user, movie=movie)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get archive statistics"""
        stats = PersonalArchive.objects.filter(user=request.user).aggregate(
            total_movies=Count('id'),
            total_size_gb=Count('file_size_gb'),
            by_format=Count('id', filter=Q(format='digital')),
            unique_movies=Count('movie', distinct=True)
        )
        
        # Add format breakdown
        format_stats = PersonalArchive.objects.filter(
            user=request.user
        ).values('format').annotate(count=Count('id'))
        
        stats['formats'] = {item['format']: item['count'] for item in format_stats}
        
        return Response(stats)


class WatchHistoryViewSet(viewsets.ModelViewSet):
    """
    Watch history tracking
    """
    
    serializer_class = WatchHistorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering = ['-started_at']
    
    def get_queryset(self):
        """Get user's watch history"""
        return WatchHistory.objects.filter(
            user=self.request.user
        ).select_related('movie')
    
    def perform_create(self, serializer):
        """Set the user when creating watch session"""
        movie_id = serializer.validated_data.pop('movie_id')
        movie = Movie.objects.get(id=movie_id)
        serializer.save(user=self.request.user, movie=movie)
    
    @action(detail=True, methods=['post'])
    def end_session(self, request, pk=None):
        """End a watch session"""
        session = self.get_object()
        
        if session.ended_at:
            return Response(
                {'error': 'session already ended'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        session.ended_at = timezone.now()
        session.duration_minutes = int(
            (session.ended_at - session.started_at).total_seconds() / 60
        )
        session.progress_percentage = request.data.get('progress_percentage', 0)
        session.completed = request.data.get('completed', False)
        session.save()
        
        serializer = self.get_serializer(session)
        return Response(serializer.data)


@login_required
def dashboard(request):
    """
    Movies module dashboard view
    """
    context = {
        'module_name': 'Movies',
        'module_description': 'Movie and Series Collection Management',
        'user': request.user,
    }
    
    # Get user statistics
    if request.user.is_authenticated:
        context['stats'] = {
            'watchlist_count': WatchList.objects.filter(user=request.user).count(),
            'collections_count': Collection.objects.filter(user=request.user).count(),
            'ratings_count': UserRating.objects.filter(user=request.user).count(),
            'archive_count': PersonalArchive.objects.filter(user=request.user).count(),
        }
    
    return render(request, 'movies/dashboard.html', context)