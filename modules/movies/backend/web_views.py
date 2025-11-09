"""
Movies Module Web UI Views
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, Count, Avg
from django.utils import timezone
from django.core.paginator import Paginator
from django.conf import settings
from cryptography.fernet import Fernet
import json
import os

from .models import Movie, WatchList, UserRating, Collection, WatchHistory
from .omdb_models import APIKeyManager, APIUsageLog
from .omdb_service import OMDBService


@login_required
def movies_home(request):
    """Main movies module page"""
    
    # Get user's watchlist summary
    watchlist_stats = WatchList.objects.filter(user=request.user).aggregate(
        total=Count('id'),
        want_to_watch=Count('id', filter=Q(status='want_to_watch')),
        watching=Count('id', filter=Q(status='watching')),
        watched=Count('id', filter=Q(status='watched'))
    )
    
    # Get recent movies from database
    recent_movies = Movie.objects.all()[:12]
    
    # Get user's recent ratings
    recent_ratings = UserRating.objects.filter(user=request.user).select_related('movie')[:5]
    
    # Get API usage stats
    omdb_service = OMDBService(user=request.user)
    api_stats = omdb_service.get_usage_stats()
    
    # Get popular movies
    popular_movies = Movie.objects.annotate(
        watchlist_count=Count('watchlisted_by')
    ).order_by('-watchlist_count', '-tmdb_rating')[:6]
    
    context = {
        'watchlist_stats': watchlist_stats,
        'recent_movies': recent_movies,
        'recent_ratings': recent_ratings,
        'api_stats': api_stats,
        'popular_movies': popular_movies,
    }
    
    return render(request, 'movies/home.html', context)


@login_required
def search_movies(request):
    """AJAX endpoint for movie search with debouncing"""
    
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    query = request.GET.get('q', '').strip()
    
    # Require at least 3 characters
    if len(query) < 3:
        return JsonResponse({
            'results': [],
            'message': 'Please enter at least 3 characters to search'
        })
    
    # Get optional filters
    year = request.GET.get('year')
    movie_type = request.GET.get('type')
    page = request.GET.get('page', 1)
    
    try:
        # Initialize OMDB service
        omdb_service = OMDBService(user=request.user)
        
        # Search movies
        results = omdb_service.search_movies(
            query=query,
            year=int(year) if year else None,
            movie_type=movie_type,
            page=int(page)
        )
        
        # Get updated usage stats
        api_stats = omdb_service.get_usage_stats()
        
        # Format response
        response_data = {
            'success': results.get('Response') == 'True',
            'results': results.get('Search', []),
            'total_results': results.get('totalResults', '0'),
            'from_cache': results.get('from_cache', False),
            'from_local': results.get('from_local', False),
            'api_usage': api_stats,
            'error': results.get('Error', None)
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'results': []
        }, status=500)


@login_required
def get_movie_details(request, imdb_id=None):
    """Get detailed movie information"""
    
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Get imdb_id from URL or query params
    if not imdb_id:
        imdb_id = request.GET.get('imdb_id')
        title = request.GET.get('title')
    else:
        title = None
    
    if not imdb_id and not title:
        return JsonResponse({'error': 'Either imdb_id or title required'}, status=400)
    
    try:
        # Initialize OMDB service
        omdb_service = OMDBService(user=request.user)
        
        # Get movie details
        movie_data = omdb_service.get_movie_details(
            imdb_id=imdb_id,
            title=title,
            year=request.GET.get('year'),
            plot=request.GET.get('plot', 'full')
        )
        
        # Check if user has this in watchlist
        in_watchlist = False
        watchlist_status = None
        if movie_data.get('local_id'):
            try:
                watchlist = WatchList.objects.get(
                    user=request.user,
                    movie_id=movie_data['local_id']
                )
                in_watchlist = True
                watchlist_status = watchlist.status
            except WatchList.DoesNotExist:
                pass
        
        # Get user's rating if exists
        user_rating = None
        if movie_data.get('local_id'):
            try:
                rating = UserRating.objects.get(
                    user=request.user,
                    movie_id=movie_data['local_id']
                )
                user_rating = {
                    'rating': float(rating.rating),
                    'review': rating.review_text
                }
            except UserRating.DoesNotExist:
                pass
        
        # Get updated usage stats
        api_stats = omdb_service.get_usage_stats()
        
        # Format response
        response_data = {
            'success': movie_data.get('Response') == 'True',
            'movie': movie_data,
            'in_watchlist': in_watchlist,
            'watchlist_status': watchlist_status,
            'user_rating': user_rating,
            'api_usage': api_stats,
            'error': movie_data.get('Error', None)
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@csrf_exempt
def add_to_watchlist(request):
    """Add movie to user's watchlist"""
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        movie_id = data.get('movie_id')
        imdb_id = data.get('imdb_id')
        status = data.get('status', 'want_to_watch')
        priority = data.get('priority', 'medium')
        
        # Get or create movie
        if movie_id:
            movie = Movie.objects.get(id=movie_id)
        elif imdb_id:
            # Fetch from OMDB if not in database
            omdb_service = OMDBService(user=request.user)
            movie_data = omdb_service.get_movie_details(imdb_id=imdb_id)
            
            if movie_data.get('Response') != 'True':
                return JsonResponse({'error': 'Movie not found'}, status=404)
            
            movie = Movie.objects.get(id=movie_data['local_id'])
        else:
            return JsonResponse({'error': 'movie_id or imdb_id required'}, status=400)
        
        # Add to watchlist
        watchlist, created = WatchList.objects.update_or_create(
            user=request.user,
            movie=movie,
            defaults={
                'status': status,
                'priority': priority,
                'updated_at': timezone.now()
            }
        )
        
        return JsonResponse({
            'success': True,
            'created': created,
            'watchlist_id': str(watchlist.id),
            'status': watchlist.status,
            'message': 'Added to watchlist' if created else 'Watchlist updated'
        })
        
    except Movie.DoesNotExist:
        return JsonResponse({'error': 'Movie not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@csrf_exempt
def remove_from_watchlist(request):
    """Remove movie from user's watchlist"""
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        movie_id = data.get('movie_id')
        
        if not movie_id:
            return JsonResponse({'error': 'movie_id required'}, status=400)
        
        # Remove from watchlist
        deleted_count = WatchList.objects.filter(
            user=request.user,
            movie_id=movie_id
        ).delete()[0]
        
        return JsonResponse({
            'success': True,
            'deleted': deleted_count > 0,
            'message': 'Removed from watchlist' if deleted_count > 0 else 'Not in watchlist'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def my_watchlist(request):
    """View user's watchlist"""
    
    status_filter = request.GET.get('status', 'all')
    priority_filter = request.GET.get('priority', 'all')
    
    # Build query
    watchlist_query = WatchList.objects.filter(user=request.user).select_related('movie')
    
    if status_filter != 'all':
        watchlist_query = watchlist_query.filter(status=status_filter)
    if priority_filter != 'all':
        watchlist_query = watchlist_query.filter(priority=priority_filter)
    
    # Paginate
    paginator = Paginator(watchlist_query, 20)
    page_number = request.GET.get('page', 1)
    watchlist_page = paginator.get_page(page_number)
    
    # Get stats
    stats = WatchList.objects.filter(user=request.user).aggregate(
        total=Count('id'),
        want_to_watch=Count('id', filter=Q(status='want_to_watch')),
        watching=Count('id', filter=Q(status='watching')),
        watched=Count('id', filter=Q(status='watched'))
    )
    
    context = {
        'watchlist': watchlist_page,
        'stats': stats,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
    }
    
    return render(request, 'movies/watchlist.html', context)


@login_required
@csrf_exempt
def rate_movie(request):
    """Rate a movie"""
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        movie_id = data.get('movie_id')
        rating_value = data.get('rating')
        review_text = data.get('review', '')
        
        if not movie_id or not rating_value:
            return JsonResponse({'error': 'movie_id and rating required'}, status=400)
        
        movie = Movie.objects.get(id=movie_id)
        
        # Create or update rating
        rating, created = UserRating.objects.update_or_create(
            user=request.user,
            movie=movie,
            defaults={
                'rating': rating_value,
                'review_text': review_text,
                'updated_at': timezone.now()
            }
        )
        
        return JsonResponse({
            'success': True,
            'created': created,
            'rating_id': str(rating.id),
            'message': 'Rating added' if created else 'Rating updated'
        })
        
    except Movie.DoesNotExist:
        return JsonResponse({'error': 'Movie not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def api_status(request):
    """Get API usage status"""
    
    try:
        omdb_service = OMDBService(user=request.user)
        api_stats = omdb_service.get_usage_stats()
        cache_stats = omdb_service.get_cache_stats()
        
        # Get recent API calls
        recent_calls = APIUsageLog.objects.filter(user=request.user)[:10]
        
        recent_calls_data = []
        for call in recent_calls:
            recent_calls_data.append({
                'type': call.request_type,
                'query': call.query_params.get('s') or call.query_params.get('t') or call.query_params.get('i', ''),
                'from_cache': call.from_cache,
                'time': call.requested_at.isoformat(),
                'response_time': call.response_time_ms
            })
        
        return JsonResponse({
            'api_usage': api_stats,
            'cache_stats': cache_stats,
            'recent_calls': recent_calls_data
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@csrf_exempt
def setup_api_key(request):
    """Setup OMDB API key (first time setup or for admin)"""
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            api_key = data.get('api_key')
            
            if not api_key:
                return JsonResponse({'error': 'API key required'}, status=400)
            
            # Generate encryption key if not exists
            encryption_key_path = os.path.join(settings.BASE_DIR, '.movies_encryption_key')
            if not os.path.exists(encryption_key_path):
                key = Fernet.generate_key()
                with open(encryption_key_path, 'wb') as f:
                    f.write(key)
                settings.MOVIES_ENCRYPTION_KEY = key
            else:
                with open(encryption_key_path, 'rb') as f:
                    settings.MOVIES_ENCRYPTION_KEY = f.read()
            
            # Check if there's already an API key
            existing = APIKeyManager.objects.filter(is_active=True).first()
            
            # Only allow setup if no key exists or user is admin
            if existing and not request.user.is_staff:
                return JsonResponse({'error': 'API key already configured. Contact admin to change.'}, status=403)
            
            # Create or update API key
            api_manager, created = APIKeyManager.objects.get_or_create(
                is_active=True,
                defaults={'key_name': 'OMDB API'}
            )
            
            api_manager.set_api_key(api_key)
            api_manager.save()
            
            return JsonResponse({
                'success': True,
                'message': 'API key saved successfully',
                'created': created
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    # GET request - show current status
    try:
        api_manager = APIKeyManager.objects.filter(is_active=True).first()
        
        if api_manager:
            api_manager.check_and_reset_daily_limit()
            return JsonResponse({
                'has_key': True,
                'key_name': api_manager.key_name,
                'usage': api_manager.requests_today,
                'limit': api_manager.daily_limit,
                'remaining': api_manager.remaining_requests,
                'last_reset': api_manager.last_reset_date.isoformat(),
                'is_admin': request.user.is_staff
            })
        else:
            return JsonResponse({
                'has_key': False,
                'message': 'No API key configured. Please setup your OMDB API key.',
                'is_admin': request.user.is_staff
            })
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)