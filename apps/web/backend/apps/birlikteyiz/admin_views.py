"""
Admin views for Birlikteyiz data source management
Only accessible to superusers
"""

from django.shortcuts import get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal
import json

from .models import EarthquakeDataSource, CronJob


@staff_member_required
@csrf_exempt
@require_http_methods(["GET", "PUT"])
def update_data_source(request, source_id):
    """Update data source configuration"""
    source = get_object_or_404(EarthquakeDataSource, id=source_id)

    if request.method == "GET":
        # Return current configuration
        return JsonResponse({
            'success': True,
            'data': {
                'id': source.id,
                'name': source.name,
                'url': source.url,
                'description': source.description,
                'is_active': source.is_active,
                'fetch_interval_minutes': source.fetch_interval_minutes,
                'min_magnitude': float(source.min_magnitude),
                'max_results': source.max_results,
                'use_geographic_filter': source.use_geographic_filter,
                'filter_min_lat': float(source.filter_min_lat) if source.filter_min_lat else None,
                'filter_max_lat': float(source.filter_max_lat) if source.filter_max_lat else None,
                'filter_min_lon': float(source.filter_min_lon) if source.filter_min_lon else None,
                'filter_max_lon': float(source.filter_max_lon) if source.filter_max_lon else None,
                'filter_region_name': source.filter_region_name,
                'fetch_count': source.fetch_count,
                'error_count': source.error_count,
                'success_count': source.success_count,
                'total_earthquakes_fetched': source.total_earthquakes_fetched,
                'success_rate': source.get_success_rate(),
                'avg_response_time': source.avg_response_time,
                'last_response_time': source.last_response_time,
            }
        })

    elif request.method == "PUT":
        # Update configuration
        try:
            data = json.loads(request.body)

            # Update basic fields
            if 'url' in data:
                source.url = data['url']
            if 'description' in data:
                source.description = data['description']
            if 'is_active' in data:
                source.is_active = data['is_active']

            # Update fetch configuration
            if 'fetch_interval_minutes' in data:
                source.fetch_interval_minutes = int(data['fetch_interval_minutes'])
            if 'min_magnitude' in data:
                source.min_magnitude = Decimal(str(data['min_magnitude']))
            if 'max_results' in data:
                source.max_results = int(data['max_results'])

            # Update geographic filter
            if 'use_geographic_filter' in data:
                source.use_geographic_filter = data['use_geographic_filter']
            if 'filter_min_lat' in data:
                source.filter_min_lat = Decimal(str(data['filter_min_lat'])) if data['filter_min_lat'] else None
            if 'filter_max_lat' in data:
                source.filter_max_lat = Decimal(str(data['filter_max_lat'])) if data['filter_max_lat'] else None
            if 'filter_min_lon' in data:
                source.filter_min_lon = Decimal(str(data['filter_min_lon'])) if data['filter_min_lon'] else None
            if 'filter_max_lon' in data:
                source.filter_max_lon = Decimal(str(data['filter_max_lon'])) if data['filter_max_lon'] else None
            if 'filter_region_name' in data:
                source.filter_region_name = data['filter_region_name']

            source.save()

            return JsonResponse({
                'success': True,
                'message': f'{source.name} başarıyla güncellendi'
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)


@staff_member_required
@csrf_exempt
@require_POST
def toggle_data_source(request, source_id):
    """Toggle data source active status"""
    source = get_object_or_404(EarthquakeDataSource, id=source_id)

    try:
        data = json.loads(request.body)
        source.is_active = data.get('is_active', not source.is_active)
        source.save()

        return JsonResponse({
            'success': True,
            'is_active': source.is_active,
            'message': f'{source.name} {"etkinleştirildi" if source.is_active else "devre dışı bırakıldı"}'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@staff_member_required
@csrf_exempt
@require_POST
def reset_source_stats(request, source_id):
    """Reset data source statistics"""
    source = get_object_or_404(EarthquakeDataSource, id=source_id)

    try:
        source.fetch_count = 0
        source.error_count = 0
        source.success_count = 0
        source.total_earthquakes_fetched = 0
        source.last_error = None
        source.last_error_time = None
        source.avg_response_time = None
        source.last_response_time = None
        source.save()

        return JsonResponse({
            'success': True,
            'message': f'{source.name} istatistikleri sıfırlandı'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@staff_member_required
@csrf_exempt
@require_POST
def test_data_source(request, source_id):
    """Test data source connection with source-specific logic"""
    source = get_object_or_404(EarthquakeDataSource, id=source_id)

    try:
        import requests
        import time
        from datetime import datetime, timedelta

        start_time = time.time()

        # Source-specific test logic
        if source.name == 'AFAD':
            # AFAD requires filter parameters
            params = {
                'start': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
                'end': datetime.now().strftime('%Y-%m-%d'),
                'minmag': 2.0,
                'limit': 1
            }
            headers = {
                'User-Agent': 'Mozilla/5.0',
                'Accept': 'application/json',
                'Connection': 'close'
            }
            response = requests.get(source.url, params=params, headers=headers, timeout=15)

        elif source.name == 'EMSC':
            # EMSC is WebSocket - test the website instead
            test_url = 'https://www.seismicportal.eu/realtime.html'
            response = requests.get(test_url, timeout=10)

        elif source.name == 'IRIS':
            # IRIS FDSNWS requires parameters
            params = {
                'format': 'text',
                'minmag': 3.0,
                'starttime': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
                'endtime': datetime.now().strftime('%Y-%m-%d'),
                'limit': 1
            }
            headers = {'User-Agent': 'Mozilla/5.0', 'Connection': 'close'}
            response = requests.get(source.url, params=params, headers=headers, timeout=15)

        elif source.name == 'USGS':
            # USGS GeoJSON feed - direct access
            response = requests.get(source.url, timeout=10)

        elif source.name == 'GFZ':
            # GFZ FDSNWS requires parameters
            params = {
                'format': 'text',
                'minmag': 3.0,
                'starttime': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
                'endtime': datetime.now().strftime('%Y-%m-%d'),
                'limit': 1
            }
            headers = {'User-Agent': 'Mozilla/5.0', 'Connection': 'close'}
            api_url = 'https://geofon.gfz-potsdam.de/fdsnws/event/1/query'
            response = requests.get(api_url, params=params, headers=headers, timeout=15)

        else:
            # KANDILLI or other sources - direct GET
            response = requests.get(source.url, timeout=10)

        response_time = time.time() - start_time

        if response.status_code == 200:
            # Check if we got data
            content_preview = response.text[:200] if hasattr(response, 'text') else str(response.content[:200])

            return JsonResponse({
                'success': True,
                'message': f'{source.name} bağlantısı başarılı',
                'response_time': round(response_time, 2),
                'status_code': response.status_code,
                'content_length': len(response.content),
                'preview': content_preview
            })
        else:
            return JsonResponse({
                'success': False,
                'error': f'HTTP {response.status_code}',
                'response_time': round(response_time, 2)
            }, status=400)

    except requests.exceptions.Timeout:
        return JsonResponse({
            'success': False,
            'error': 'Bağlantı zaman aşımına uğradı (timeout)'
        }, status=400)
    except requests.exceptions.ConnectionError as e:
        return JsonResponse({
            'success': False,
            'error': f'Bağlantı hatası: {str(e)}'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@staff_member_required
def get_preset_regions(request):
    """Get preset geographic regions"""
    presets = {
        'türkiye': {
            'min_lat': 35.0,
            'max_lat': 43.0,
            'min_lon': 25.0,
            'max_lon': 45.0,
            'name': 'Türkiye'
        },
        'küresel': {
            'min_lat': -90.0,
            'max_lat': 90.0,
            'min_lon': -180.0,
            'max_lon': 180.0,
            'name': 'Küresel'
        },
        'avrupa': {
            'min_lat': 35.0,
            'max_lat': 71.0,
            'min_lon': -11.0,
            'max_lon': 40.0,
            'name': 'Avrupa'
        },
        'asya': {
            'min_lat': 10.0,
            'max_lat': 55.0,
            'min_lon': 60.0,
            'max_lon': 145.0,
            'name': 'Asya'
        },
        'kuzey_amerika': {
            'min_lat': 25.0,
            'max_lat': 72.0,
            'min_lon': -168.0,
            'max_lon': -52.0,
            'name': 'Kuzey Amerika'
        },
        'pasifik_halka_ateşi': {
            'min_lat': -60.0,
            'max_lat': 70.0,
            'min_lon': 120.0,
            'max_lon': -60.0,
            'name': 'Pasifik Halka-i Ateşi'
        }
    }

    return JsonResponse({
        'success': True,
        'presets': presets
    })


@staff_member_required
@csrf_exempt
@require_POST
def fetch_all_sources(request):
    """Fetch earthquake data from all active sources"""
    try:
        from django.core.management import call_command
        import threading

        # Run the command in a background thread to not block the request
        def fetch_data():
            call_command('fetch_earthquakes')

        thread = threading.Thread(target=fetch_data)
        thread.daemon = True
        thread.start()

        return JsonResponse({
            'success': True,
            'message': 'tüm kaynaklardan veri çekme işlemi başlatıldı'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@staff_member_required
@csrf_exempt
@require_POST
def fetch_single_source(request, source_id):
    """Fetch earthquake data from a specific source"""
    source = get_object_or_404(EarthquakeDataSource, id=source_id)

    try:
        from django.core.management import call_command
        import threading

        # Run the command in a background thread for this specific source
        def fetch_data():
            call_command('fetch_earthquakes', '--source', source.name)

        thread = threading.Thread(target=fetch_data)
        thread.daemon = True
        thread.start()

        return JsonResponse({
            'success': True,
            'message': f'{source.name} kaynağından veri çekme işlemi başlatıldı'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
