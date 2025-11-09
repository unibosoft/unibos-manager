"""
OMDB API Service
Handles all OMDB API interactions with caching and rate limiting
"""

import requests
import hashlib
import json
from typing import Dict, List, Optional, Tuple
from django.utils import timezone
from django.core.files.base import ContentFile
from django.conf import settings
from django.db import models
from datetime import datetime, timedelta
import time
import os

from .models import Movie, Genre
from .omdb_models import APIKeyManager, OMDBCache, APIUsageLog, MovieImportQueue


class OMDBService:
    """Main service for OMDB API interactions"""
    
    BASE_URL = "http://www.omdbapi.com/"
    POSTER_URL = "http://img.omdbapi.com/"
    
    def __init__(self, user=None):
        self.user = user
        self.api_key_manager = self._get_api_key_manager()
        self.api_key = self.api_key_manager.get_api_key() if self.api_key_manager else None
    
    def _get_api_key_manager(self) -> Optional[APIKeyManager]:
        """Get active API key manager"""
        try:
            return APIKeyManager.objects.filter(is_active=True).first()
        except:
            return None
    
    def _generate_cache_key(self, params: Dict) -> str:
        """Generate cache key from parameters"""
        # Sort params for consistent hashing
        sorted_params = json.dumps(params, sort_keys=True)
        return hashlib.md5(sorted_params.encode()).hexdigest()
    
    def _make_request(self, params: Dict, cache_type: str = 'search', 
                     cache_hours: int = 24) -> Tuple[Dict, bool]:
        """Make API request with caching and rate limiting"""
        
        start_time = time.time()
        
        # Check cache first
        cache_key = self._generate_cache_key(params)
        cached_data = OMDBCache.get_cache(cache_key, cache_type)
        
        if cached_data:
            # Log cached response
            response_time = int((time.time() - start_time) * 1000)
            APIUsageLog.log_request(
                user=self.user,
                request_type=cache_type,
                query_params=params,
                response_status=200,
                response_time_ms=response_time,
                from_cache=True
            )
            return cached_data, True
        
        # Check API rate limit
        if not self.api_key_manager or not self.api_key_manager.can_make_request():
            raise Exception(f"API rate limit reached. {self.get_usage_stats()['remaining']} requests remaining today.")
        
        # Make API request
        params['apikey'] = self.api_key
        
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response_time = int((time.time() - start_time) * 1000)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for API error response
                if data.get('Response') == 'False':
                    error_msg = data.get('Error', 'Unknown error')
                    APIUsageLog.log_request(
                        user=self.user,
                        request_type=cache_type,
                        query_params={k: v for k, v in params.items() if k != 'apikey'},
                        response_status=400,
                        response_time_ms=response_time,
                        from_cache=False,
                        error_message=error_msg
                    )
                    
                    # Don't increment usage for "Movie not found" errors
                    if "Movie not found" not in error_msg:
                        self.api_key_manager.increment_usage()
                    
                    return {'error': error_msg, 'success': False}, False
                
                # Success - cache the response
                OMDBCache.set_cache(
                    cache_key=cache_key,
                    query_params={k: v for k, v in params.items() if k != 'apikey'},
                    response_data=data,
                    cache_type=cache_type,
                    hours=cache_hours
                )
                
                # Increment usage counter
                self.api_key_manager.increment_usage()
                
                # Log successful request
                APIUsageLog.log_request(
                    user=self.user,
                    request_type=cache_type,
                    query_params={k: v for k, v in params.items() if k != 'apikey'},
                    response_status=200,
                    response_time_ms=response_time,
                    from_cache=False
                )
                
                return data, False
            
            else:
                # Log error
                APIUsageLog.log_request(
                    user=self.user,
                    request_type=cache_type,
                    query_params={k: v for k, v in params.items() if k != 'apikey'},
                    response_status=response.status_code,
                    response_time_ms=response_time,
                    from_cache=False,
                    error_message=f"HTTP {response.status_code}"
                )
                raise Exception(f"API request failed with status {response.status_code}")
                
        except requests.RequestException as e:
            response_time = int((time.time() - start_time) * 1000)
            APIUsageLog.log_request(
                user=self.user,
                request_type=cache_type,
                query_params={k: v for k, v in params.items() if k != 'apikey'},
                response_status=500,
                response_time_ms=response_time,
                from_cache=False,
                error_message=str(e)
            )
            raise Exception(f"Network error: {str(e)}")
    
    def search_movies(self, query: str, year: Optional[int] = None, 
                     movie_type: Optional[str] = None, page: int = 1) -> Dict:
        """Search for movies by title"""
        
        # First check local database
        local_results = self._search_local_database(query, year, movie_type)
        
        params = {
            's': query,
            'page': page,
            'r': 'json'
        }
        
        if year:
            params['y'] = year
        if movie_type:
            params['type'] = movie_type
        
        # Get from OMDB
        try:
            omdb_data, from_cache = self._make_request(params, cache_type='search')
            
            if omdb_data.get('Response') == 'True':
                # Merge local and OMDB results
                return self._merge_search_results(local_results, omdb_data, from_cache)
            else:
                # Return only local results if OMDB fails
                return {
                    'Search': local_results,
                    'totalResults': str(len(local_results)),
                    'Response': 'True' if local_results else 'False',
                    'from_cache': False,
                    'from_local': True
                }
        except Exception as e:
            # Return local results on error
            return {
                'Search': local_results,
                'totalResults': str(len(local_results)),
                'Response': 'True' if local_results else 'False',
                'Error': str(e),
                'from_local': True
            }
    
    def get_movie_details(self, imdb_id: str = None, title: str = None, 
                         year: Optional[int] = None, plot: str = 'full') -> Dict:
        """Get detailed movie information"""
        
        # Check local database first
        if imdb_id:
            try:
                movie = Movie.objects.get(imdb_id=imdb_id)
                if movie.last_api_sync and (timezone.now() - movie.last_api_sync).days < 30:
                    return self._format_movie_for_api(movie, from_local=True)
            except Movie.DoesNotExist:
                pass
        
        params = {'r': 'json', 'plot': plot}
        
        if imdb_id:
            params['i'] = imdb_id
        elif title:
            params['t'] = title
            if year:
                params['y'] = year
        else:
            raise ValueError("Either imdb_id or title must be provided")
        
        # Get from OMDB
        data, from_cache = self._make_request(params, cache_type='detail', cache_hours=168)  # Cache for 1 week
        
        if data.get('Response') == 'True':
            # Save to local database
            movie = self._save_movie_to_database(data)
            data['local_id'] = str(movie.id)
            data['from_cache'] = from_cache
        
        return data
    
    def _search_local_database(self, query: str, year: Optional[int] = None,
                               movie_type: Optional[str] = None) -> List[Dict]:
        """Search local database for movies"""
        movies = Movie.objects.filter(title__icontains=query)
        
        if year:
            movies = movies.filter(release_date__year=year)
        if movie_type:
            movies = movies.filter(content_type=movie_type)
        
        # Limit to 10 results
        movies = movies[:10]
        
        results = []
        for movie in movies:
            results.append({
                'Title': movie.title,
                'Year': str(movie.release_date.year) if movie.release_date else 'N/A',
                'imdbID': movie.imdb_id or '',
                'Type': movie.content_type,
                'Poster': movie.poster_path or 'N/A',
                'local_id': str(movie.id),
                'from_local': True
            })
        
        return results
    
    def _merge_search_results(self, local_results: List[Dict], 
                             omdb_data: Dict, from_cache: bool) -> Dict:
        """Merge local and OMDB search results"""
        
        # Create a set of IMDB IDs from local results
        local_imdb_ids = {r['imdbID'] for r in local_results if r.get('imdbID')}
        
        # Add OMDB results that aren't in local
        omdb_results = omdb_data.get('Search', [])
        for result in omdb_results:
            if result.get('imdbID') not in local_imdb_ids:
                result['from_local'] = False
        
        # Mark local results
        for result in local_results:
            result['from_local'] = True
        
        # Combine and return
        all_results = local_results + [r for r in omdb_results if r.get('imdbID') not in local_imdb_ids]
        
        return {
            'Search': all_results[:10],  # Limit to 10 results
            'totalResults': str(len(all_results)),
            'Response': 'True',
            'from_cache': from_cache,
            'mixed_source': True
        }
    
    def _save_movie_to_database(self, omdb_data: Dict) -> Movie:
        """Save or update movie in local database"""
        
        # Parse release date
        release_date = None
        if omdb_data.get('Released') and omdb_data['Released'] != 'N/A':
            try:
                release_date = datetime.strptime(omdb_data['Released'], '%d %b %Y').date()
            except:
                if omdb_data.get('Year') and omdb_data['Year'] != 'N/A':
                    try:
                        release_date = datetime(int(omdb_data['Year']), 1, 1).date()
                    except:
                        pass
        
        # Parse runtime
        runtime = None
        if omdb_data.get('Runtime') and omdb_data['Runtime'] != 'N/A':
            try:
                runtime = int(omdb_data['Runtime'].split()[0])
            except:
                pass
        
        # Parse ratings
        imdb_rating = None
        imdb_votes = 0
        if omdb_data.get('imdbRating') and omdb_data['imdbRating'] != 'N/A':
            try:
                imdb_rating = float(omdb_data['imdbRating'])
            except:
                pass
        if omdb_data.get('imdbVotes') and omdb_data['imdbVotes'] != 'N/A':
            try:
                imdb_votes = int(omdb_data['imdbVotes'].replace(',', ''))
            except:
                pass
        
        # Determine content type
        content_type = 'movie'
        if omdb_data.get('Type'):
            if omdb_data['Type'] == 'series':
                content_type = 'series'
            elif omdb_data['Type'] == 'documentary':
                content_type = 'documentary'
        
        # Create or update movie
        movie, created = Movie.objects.update_or_create(
            imdb_id=omdb_data.get('imdbID'),
            defaults={
                'title': omdb_data.get('Title', ''),
                'content_type': content_type,
                'overview': omdb_data.get('Plot', ''),
                'release_date': release_date,
                'runtime': runtime,
                'poster_path': omdb_data.get('Poster') if omdb_data.get('Poster') != 'N/A' else '',
                'tmdb_rating': imdb_rating,
                'tmdb_vote_count': imdb_votes,
                'api_data': omdb_data,
                'last_api_sync': timezone.now(),
                'production_countries': [omdb_data.get('Country', '')] if omdb_data.get('Country') else [],
                'spoken_languages': [omdb_data.get('Language', '')] if omdb_data.get('Language') else [],
            }
        )
        
        # Handle genres
        if omdb_data.get('Genre') and omdb_data['Genre'] != 'N/A':
            genres = [g.strip() for g in omdb_data['Genre'].split(',')]
            for genre_name in genres:
                genre, _ = Genre.objects.get_or_create(
                    name=genre_name,
                    defaults={'slug': genre_name.lower().replace(' ', '-'), 'tmdb_id': 0}
                )
                movie.genres.add(genre)
        
        # Download and save poster if needed
        if movie.poster_path and not movie.poster_path.startswith('/'):
            self._download_poster(movie)
        
        return movie
    
    def _download_poster(self, movie: Movie):
        """Download and save poster locally"""
        if not movie.poster_path or movie.poster_path == 'N/A':
            return
        
        try:
            # Create media directory if not exists
            poster_dir = os.path.join(settings.MEDIA_ROOT, 'movies', 'posters')
            os.makedirs(poster_dir, exist_ok=True)
            
            # Generate filename
            filename = f"{movie.imdb_id or movie.id}.jpg"
            filepath = os.path.join(poster_dir, filename)
            
            # Check if already downloaded
            if os.path.exists(filepath):
                movie.poster_path = f"/media/movies/posters/{filename}"
                movie.save()
                return
            
            # Download poster
            response = requests.get(movie.poster_path, timeout=10)
            if response.status_code == 200:
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                # Update movie with local path
                movie.poster_path = f"/media/movies/posters/{filename}"
                movie.save()
        except Exception as e:
            print(f"Error downloading poster for {movie.title}: {e}")
    
    def _format_movie_for_api(self, movie: Movie, from_local: bool = False) -> Dict:
        """Format local movie object as API response"""
        return {
            'Title': movie.title,
            'Year': str(movie.release_date.year) if movie.release_date else 'N/A',
            'Rated': movie.api_data.get('Rated', 'N/A') if movie.api_data else 'N/A',
            'Released': movie.release_date.strftime('%d %b %Y') if movie.release_date else 'N/A',
            'Runtime': f"{movie.runtime} min" if movie.runtime else 'N/A',
            'Genre': ', '.join([g.name for g in movie.genres.all()]),
            'Director': movie.api_data.get('Director', 'N/A') if movie.api_data else 'N/A',
            'Writer': movie.api_data.get('Writer', 'N/A') if movie.api_data else 'N/A',
            'Actors': movie.api_data.get('Actors', 'N/A') if movie.api_data else 'N/A',
            'Plot': movie.overview,
            'Language': ', '.join(movie.spoken_languages) if movie.spoken_languages else 'N/A',
            'Country': ', '.join(movie.production_countries) if movie.production_countries else 'N/A',
            'Awards': movie.api_data.get('Awards', 'N/A') if movie.api_data else 'N/A',
            'Poster': movie.poster_path or 'N/A',
            'Ratings': movie.api_data.get('Ratings', []) if movie.api_data else [],
            'Metascore': movie.api_data.get('Metascore', 'N/A') if movie.api_data else 'N/A',
            'imdbRating': str(movie.tmdb_rating) if movie.tmdb_rating else 'N/A',
            'imdbVotes': f"{movie.tmdb_vote_count:,}" if movie.tmdb_vote_count else 'N/A',
            'imdbID': movie.imdb_id or '',
            'Type': movie.content_type,
            'Response': 'True',
            'from_local': from_local,
            'local_id': str(movie.id)
        }
    
    def get_usage_stats(self) -> Dict:
        """Get current API usage statistics"""
        if not self.api_key_manager:
            return {
                'used': 0,
                'remaining': 0,
                'limit': 0,
                'percentage': 0
            }
        
        self.api_key_manager.check_and_reset_daily_limit()
        
        return {
            'used': self.api_key_manager.requests_today,
            'remaining': self.api_key_manager.remaining_requests,
            'limit': self.api_key_manager.daily_limit,
            'percentage': round((self.api_key_manager.requests_today / self.api_key_manager.daily_limit) * 100, 1)
        }
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        total_cached = OMDBCache.objects.count()
        expired = OMDBCache.objects.filter(expires_at__lt=timezone.now()).count()
        
        # Get hit rates by type
        search_stats = OMDBCache.objects.filter(cache_type='search').aggregate(
            count=models.Count('id'),
            total_hits=models.Sum('hit_count')
        )
        
        detail_stats = OMDBCache.objects.filter(cache_type='detail').aggregate(
            count=models.Count('id'),
            total_hits=models.Sum('hit_count')
        )
        
        return {
            'total_entries': total_cached,
            'expired_entries': expired,
            'search_cached': search_stats['count'] or 0,
            'search_hits': search_stats['total_hits'] or 0,
            'detail_cached': detail_stats['count'] or 0,
            'detail_hits': detail_stats['total_hits'] or 0,
        }