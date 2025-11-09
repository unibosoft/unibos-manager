"""
Movies Module External API Services
Integration with TMDB and OMDB APIs
"""

import requests
import logging
from typing import Dict, List, Optional
from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from datetime import datetime

from .models import Movie, Genre

logger = logging.getLogger(__name__)


class TMDBService:
    """
    The Movie Database (TMDB) API integration service
    """
    
    BASE_URL = 'https://api.themoviedb.org/3'
    IMAGE_BASE_URL = 'https://image.tmdb.org/t/p'
    
    def __init__(self):
        self.api_key = getattr(settings, 'TMDB_API_KEY', None)
        if not self.api_key:
            logger.warning("TMDB API key not configured")
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make API request with error handling"""
        if not self.api_key:
            return None
        
        if params is None:
            params = {}
        params['api_key'] = self.api_key
        
        try:
            response = requests.get(
                f"{self.BASE_URL}/{endpoint}",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"TMDB API error: {str(e)}")
            return None
    
    def search_movies(self, query: str, page: int = 1) -> List[Dict]:
        """Search for movies and TV shows"""
        cache_key = f"tmdb_search_{query}_{page}"
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        results = []
        
        # Search movies
        movie_data = self._make_request('search/movie', {
            'query': query,
            'page': page
        })
        if movie_data:
            for item in movie_data.get('results', []):
                item['content_type'] = 'movie'
                results.append(self._format_search_result(item))
        
        # Search TV shows
        tv_data = self._make_request('search/tv', {
            'query': query,
            'page': page
        })
        if tv_data:
            for item in tv_data.get('results', []):
                item['content_type'] = 'series'
                results.append(self._format_search_result(item))
        
        # Cache for 1 hour
        cache.set(cache_key, results, 3600)
        return results
    
    def get_movie_details(self, tmdb_id: str, content_type: str = 'movie') -> Optional[Dict]:
        """Get detailed movie or TV show information"""
        endpoint = f"{'movie' if content_type == 'movie' else 'tv'}/{tmdb_id}"
        
        data = self._make_request(endpoint, {
            'append_to_response': 'credits,videos,external_ids'
        })
        
        if not data:
            return None
        
        return self._format_detailed_result(data, content_type)
    
    def _format_search_result(self, item: Dict) -> Dict:
        """Format search result for consistency"""
        return {
            'tmdb_id': str(item.get('id')),
            'title': item.get('title') or item.get('name'),
            'original_title': item.get('original_title') or item.get('original_name'),
            'overview': item.get('overview'),
            'release_date': item.get('release_date') or item.get('first_air_date'),
            'poster_path': self._get_image_url(item.get('poster_path')),
            'backdrop_path': self._get_image_url(item.get('backdrop_path'), size='w1280'),
            'popularity': item.get('popularity'),
            'vote_average': item.get('vote_average'),
            'content_type': item.get('content_type', 'movie')
        }
    
    def _format_detailed_result(self, item: Dict, content_type: str) -> Dict:
        """Format detailed result with all information"""
        result = {
            'tmdb_id': str(item.get('id')),
            'imdb_id': item.get('external_ids', {}).get('imdb_id'),
            'title': item.get('title') or item.get('name'),
            'original_title': item.get('original_title') or item.get('original_name'),
            'content_type': content_type,
            'overview': item.get('overview'),
            'tagline': item.get('tagline'),
            'release_date': item.get('release_date') or item.get('first_air_date'),
            'runtime': item.get('runtime') or (item.get('episode_run_time', [None])[0] if item.get('episode_run_time') else None),
            'status': item.get('status', '').lower().replace(' ', '_'),
            'poster_path': self._get_image_url(item.get('poster_path')),
            'backdrop_path': self._get_image_url(item.get('backdrop_path'), size='w1280'),
            'genres': [{'id': g['id'], 'name': g['name']} for g in item.get('genres', [])],
            'production_companies': [c['name'] for c in item.get('production_companies', [])],
            'production_countries': [c['iso_3166_1'] for c in item.get('production_countries', [])],
            'spoken_languages': [l['iso_639_1'] for l in item.get('spoken_languages', [])],
            'budget': item.get('budget'),
            'revenue': item.get('revenue'),
            'tmdb_rating': item.get('vote_average'),
            'tmdb_vote_count': item.get('vote_count'),
            'popularity': item.get('popularity'),
            'api_data': item
        }
        
        # Add series-specific fields
        if content_type == 'series':
            result.update({
                'number_of_seasons': item.get('number_of_seasons'),
                'number_of_episodes': item.get('number_of_episodes'),
                'episode_runtime': item.get('episode_run_time', [])
            })
        
        # Extract trailer URL
        videos = item.get('videos', {}).get('results', [])
        for video in videos:
            if video.get('type') == 'Trailer' and video.get('site') == 'YouTube':
                result['trailer_url'] = f"https://www.youtube.com/watch?v={video['key']}"
                break
        
        return result
    
    def _get_image_url(self, path: str, size: str = 'w500') -> str:
        """Get full image URL"""
        if not path:
            return ''
        return f"{self.IMAGE_BASE_URL}/{size}{path}"
    
    @transaction.atomic
    def create_or_update_movie(self, data: Dict, instance: Movie = None) -> Movie:
        """Create or update movie from TMDB data"""
        # Handle genres first
        genre_objects = []
        for genre_data in data.get('genres', []):
            genre, _ = Genre.objects.get_or_create(
                tmdb_id=genre_data['id'],
                defaults={'name': genre_data['name'], 'slug': genre_data['name'].lower().replace(' ', '-')}
            )
            genre_objects.append(genre)
        
        # Prepare movie data
        movie_data = {
            'tmdb_id': data.get('tmdb_id'),
            'imdb_id': data.get('imdb_id'),
            'title': data.get('title'),
            'original_title': data.get('original_title', ''),
            'content_type': data.get('content_type', 'movie'),
            'overview': data.get('overview', ''),
            'tagline': data.get('tagline', ''),
            'runtime': data.get('runtime'),
            'status': data.get('status', 'released'),
            'poster_path': data.get('poster_path', ''),
            'backdrop_path': data.get('backdrop_path', ''),
            'trailer_url': data.get('trailer_url', ''),
            'production_companies': data.get('production_companies', []),
            'production_countries': data.get('production_countries', []),
            'spoken_languages': data.get('spoken_languages', []),
            'budget': data.get('budget'),
            'revenue': data.get('revenue'),
            'tmdb_rating': data.get('tmdb_rating'),
            'tmdb_vote_count': data.get('tmdb_vote_count', 0),
            'popularity': data.get('popularity'),
            'number_of_seasons': data.get('number_of_seasons'),
            'number_of_episodes': data.get('number_of_episodes'),
            'episode_runtime': data.get('episode_runtime', []),
            'api_data': data.get('api_data', {}),
            'last_api_sync': datetime.now()
        }
        
        # Parse release date
        if data.get('release_date'):
            try:
                movie_data['release_date'] = datetime.strptime(
                    data['release_date'], '%Y-%m-%d'
                ).date()
            except (ValueError, TypeError):
                pass
        
        if instance:
            # Update existing movie
            for key, value in movie_data.items():
                if value is not None:
                    setattr(instance, key, value)
            instance.save()
            movie = instance
        else:
            # Create new movie
            movie = Movie.objects.create(**movie_data)
        
        # Update genres
        movie.genres.set(genre_objects)
        
        return movie


class OMDBService:
    """
    Open Movie Database (OMDB) API integration service
    """
    
    BASE_URL = 'http://www.omdbapi.com/'
    
    def __init__(self):
        self.api_key = getattr(settings, 'OMDB_API_KEY', None)
        if not self.api_key:
            logger.warning("OMDB API key not configured")
    
    def _make_request(self, params: Dict) -> Optional[Dict]:
        """Make API request with error handling"""
        if not self.api_key:
            return None
        
        params['apikey'] = self.api_key
        
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('Response') == 'False':
                logger.error(f"OMDB API error: {data.get('Error')}")
                return None
            
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"OMDB API error: {str(e)}")
            return None
    
    def search_movies(self, query: str, page: int = 1) -> List[Dict]:
        """Search for movies"""
        cache_key = f"omdb_search_{query}_{page}"
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        data = self._make_request({
            's': query,
            'page': page
        })
        
        if not data or 'Search' not in data:
            return []
        
        results = [self._format_search_result(item) for item in data['Search']]
        
        # Cache for 1 hour
        cache.set(cache_key, results, 3600)
        return results
    
    def get_movie_details(self, imdb_id: str) -> Optional[Dict]:
        """Get detailed movie information by IMDB ID"""
        data = self._make_request({
            'i': imdb_id,
            'plot': 'full'
        })
        
        if not data:
            return None
        
        return self._format_detailed_result(data)
    
    def _format_search_result(self, item: Dict) -> Dict:
        """Format search result for consistency"""
        return {
            'imdb_id': item.get('imdbID'),
            'title': item.get('Title'),
            'year': item.get('Year'),
            'content_type': 'series' if item.get('Type') == 'series' else 'movie',
            'poster_path': item.get('Poster') if item.get('Poster') != 'N/A' else ''
        }
    
    def _format_detailed_result(self, item: Dict) -> Dict:
        """Format detailed result with all information"""
        # Parse runtime
        runtime = None
        if item.get('Runtime') and item['Runtime'] != 'N/A':
            try:
                runtime = int(item['Runtime'].split()[0])
            except (ValueError, IndexError):
                pass
        
        # Parse ratings
        imdb_rating = None
        if item.get('imdbRating') and item['imdbRating'] != 'N/A':
            try:
                imdb_rating = float(item['imdbRating'])
            except ValueError:
                pass
        
        # Parse box office
        revenue = None
        if item.get('BoxOffice') and item['BoxOffice'] != 'N/A':
            try:
                revenue = int(item['BoxOffice'].replace('$', '').replace(',', ''))
            except ValueError:
                pass
        
        return {
            'imdb_id': item.get('imdbID'),
            'title': item.get('Title'),
            'content_type': 'series' if item.get('Type') == 'series' else 'movie',
            'overview': item.get('Plot') if item.get('Plot') != 'N/A' else '',
            'release_date': self._parse_date(item.get('Released')),
            'runtime': runtime,
            'poster_path': item.get('Poster') if item.get('Poster') != 'N/A' else '',
            'genres': [{'name': g.strip()} for g in item.get('Genre', '').split(',') if g.strip() and g != 'N/A'],
            'production_countries': [item.get('Country')] if item.get('Country') and item['Country'] != 'N/A' else [],
            'spoken_languages': [item.get('Language')] if item.get('Language') and item['Language'] != 'N/A' else [],
            'revenue': revenue,
            'tmdb_rating': imdb_rating,
            'tmdb_vote_count': self._parse_votes(item.get('imdbVotes')),
            'api_data': item
        }
    
    def _parse_date(self, date_str: str) -> Optional[str]:
        """Parse date string to ISO format"""
        if not date_str or date_str == 'N/A':
            return None
        
        try:
            # Try different date formats
            for fmt in ['%d %b %Y', '%Y-%m-%d', '%Y']:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return dt.strftime('%Y-%m-%d')
                except ValueError:
                    continue
        except Exception:
            pass
        
        return None
    
    def _parse_votes(self, votes_str: str) -> int:
        """Parse vote count string"""
        if not votes_str or votes_str == 'N/A':
            return 0
        
        try:
            return int(votes_str.replace(',', ''))
        except ValueError:
            return 0
    
    @transaction.atomic
    def create_or_update_movie(self, data: Dict, instance: Movie = None) -> Movie:
        """Create or update movie from OMDB data"""
        # Prepare movie data
        movie_data = {
            'imdb_id': data.get('imdb_id'),
            'title': data.get('title'),
            'content_type': data.get('content_type', 'movie'),
            'overview': data.get('overview', ''),
            'runtime': data.get('runtime'),
            'poster_path': data.get('poster_path', ''),
            'production_countries': data.get('production_countries', []),
            'spoken_languages': data.get('spoken_languages', []),
            'revenue': data.get('revenue'),
            'tmdb_rating': data.get('tmdb_rating'),
            'tmdb_vote_count': data.get('tmdb_vote_count', 0),
            'api_data': data.get('api_data', {}),
            'last_api_sync': datetime.now()
        }
        
        # Parse release date
        if data.get('release_date'):
            try:
                movie_data['release_date'] = datetime.strptime(
                    data['release_date'], '%Y-%m-%d'
                ).date()
            except (ValueError, TypeError):
                pass
        
        if instance:
            # Update existing movie
            for key, value in movie_data.items():
                if value is not None:
                    setattr(instance, key, value)
            instance.save()
            movie = instance
        else:
            # Create new movie
            movie = Movie.objects.create(**movie_data)
        
        # Handle genres
        for genre_data in data.get('genres', []):
            genre, _ = Genre.objects.get_or_create(
                name=genre_data['name'],
                defaults={'tmdb_id': 0, 'slug': genre_data['name'].lower().replace(' ', '-')}
            )
            movie.genres.add(genre)
        
        return movie