from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.management import call_command
from datetime import timedelta
import threading
import json
from decimal import Decimal
from .models import (
    Earthquake, EarthquakeDataSource, CronJob,
    MeshNode, EmergencyMessage, DisasterZone, ResourcePoint
)


@login_required
def birlikteyiz_dashboard(request):
    """Main dashboard for Birlikteyiz module"""

    # Get recent earthquakes (base queryset - NO slice yet)
    recent_earthquakes_qs = Earthquake.objects.filter(
        occurred_at__gte=timezone.now() - timedelta(days=7)
    ).order_by('-occurred_at')

    # Get active disaster zones
    active_zones = DisasterZone.objects.filter(
        is_active=True
    ).order_by('-severity', '-declared_at')[:5]

    # Get mesh network stats
    total_nodes = MeshNode.objects.count()
    online_nodes = MeshNode.objects.filter(is_online=True).count()
    recent_messages = EmergencyMessage.objects.filter(
        created_at__gte=timezone.now() - timedelta(hours=24)
    ).count()

    # Get resource points
    resource_points = ResourcePoint.objects.filter(
        is_operational=True
    ).select_related()[:10]

    # Get data sources with health status
    data_sources = EarthquakeDataSource.objects.all()

    # Enhanced earthquake statistics
    earthquake_count = Earthquake.objects.filter(
        occurred_at__gte=timezone.now() - timedelta(days=1),
        magnitude__gte=3.0
    ).count()

    # Count by magnitude ranges (last 7 days) - use queryset BEFORE slice
    major_quakes = recent_earthquakes_qs.filter(magnitude__gte=5.0).count()
    moderate_quakes = recent_earthquakes_qs.filter(magnitude__gte=4.0, magnitude__lt=5.0).count()
    minor_quakes = recent_earthquakes_qs.filter(magnitude__gte=3.0, magnitude__lt=4.0).count()

    # Get strongest earthquake in last 7 days
    strongest_quake = recent_earthquakes_qs.order_by('-magnitude').first()

    # Get most recent earthquake
    latest_quake = recent_earthquakes_qs.first()

    # NOW apply slice for template display
    recent_earthquakes = recent_earthquakes_qs[:50]

    context = {
        'recent_earthquakes': recent_earthquakes,
        'active_zones': active_zones,
        'total_nodes': total_nodes,
        'online_nodes': online_nodes,
        'recent_messages': recent_messages,
        'resource_points': resource_points,
        'data_sources': data_sources,
        'earthquake_count': earthquake_count,
        'major_quakes': major_quakes,
        'moderate_quakes': moderate_quakes,
        'minor_quakes': minor_quakes,
        'strongest_quake': strongest_quake,
        'latest_quake': latest_quake,
    }

    return render(request, 'birlikteyiz/dashboard.html', context)


@login_required
def earthquake_list(request):
    """List all earthquakes with filtering"""
    
    earthquakes = Earthquake.objects.all()
    
    # Filtering
    magnitude_min = request.GET.get('magnitude_min')
    if magnitude_min:
        earthquakes = earthquakes.filter(magnitude__gte=magnitude_min)
    
    source = request.GET.get('source')
    if source:
        earthquakes = earthquakes.filter(source=source)
    
    city = request.GET.get('city')
    if city:
        earthquakes = earthquakes.filter(
            Q(city__icontains=city) | Q(location__icontains=city)
        )
    
    days = request.GET.get('days', 7)
    try:
        days = int(days)
    except:
        days = 7
    
    earthquakes = earthquakes.filter(
        occurred_at__gte=timezone.now() - timedelta(days=days)
    ).order_by('-occurred_at')
    
    # Pagination
    paginator = Paginator(earthquakes, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get data sources
    sources = EarthquakeDataSource.objects.all()
    
    context = {
        'page_obj': page_obj,
        'sources': sources,
        'filter_magnitude': magnitude_min,
        'filter_source': source,
        'filter_city': city,
        'filter_days': days,
    }
    
    return render(request, 'birlikteyiz/earthquake_list.html', context)


@login_required
def cron_jobs(request):
    """Display and manage cron jobs - redirects to admin page if superuser"""

    # Superusers go to the full admin panel
    if request.user.is_superuser:
        return source_admin(request)

    # Regular users see simplified view
    # Ensure earthquake fetch job exists
    fetch_job, _ = CronJob.objects.get_or_create(
        name='Fetch Earthquakes',
        defaults={
            'command': 'cd /Users/berkhatirli/Desktop/unibos/apps/web/backend && DJANGO_SETTINGS_MODULE=unibos_backend.settings.development ./venv/bin/python3 manage.py fetch_earthquakes',
            'schedule': '*/5 * * * *',
            'is_active': True
        }
    )

    jobs = CronJob.objects.all().order_by('name')
    data_sources = EarthquakeDataSource.objects.all().order_by('name')

    context = {
        'jobs': jobs,
        'data_sources': data_sources,
    }

    return render(request, 'birlikteyiz/cron_jobs.html', context)


@login_required
def source_admin(request):
    """Full admin panel for data source management - superusers only"""

    data_sources = EarthquakeDataSource.objects.all().order_by('name')

    context = {
        'data_sources': data_sources,
    }

    return render(request, 'birlikteyiz/source_admin.html', context)


@login_required
@csrf_exempt
@require_POST
def manual_fetch(request):
    """Manually trigger earthquake data fetch"""

    try:
        # Run the command in a background thread to not block the request
        def fetch_data():
            call_command('fetch_earthquakes')

        thread = threading.Thread(target=fetch_data)
        thread.daemon = True
        thread.start()

        return JsonResponse({'success': True, 'message': 'veri çekme işlemi başlatıldı'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def earthquake_map(request):
    """Interactive map view of earthquakes with list"""
    import json

    # Get filter parameters
    days = request.GET.get('days', 30)
    try:
        days = int(days)
    except:
        days = 30

    magnitude_min = request.GET.get('magnitude_min', 2.5)
    try:
        magnitude_min = float(magnitude_min)
    except:
        magnitude_min = 2.5

    source_filter = request.GET.get('source', None)

    # Get earthquakes for both map and list (using same queryset)
    earthquakes_qs = Earthquake.objects.filter(
        occurred_at__gte=timezone.now() - timedelta(days=days),
        magnitude__gte=magnitude_min
    )

    # Apply source filter if provided
    if source_filter:
        earthquakes_qs = earthquakes_qs.filter(source=source_filter)

    earthquakes_qs = earthquakes_qs.order_by('-occurred_at')

    # For map: limit to 500 for performance
    earthquakes_for_map = earthquakes_qs[:500]

    # Convert to list for JSON serialization
    earthquake_data = []
    for eq in earthquakes_for_map:
        earthquake_data.append({
            'id': eq.id,
            'lat': float(eq.latitude),
            'lon': float(eq.longitude),
            'magnitude': float(eq.magnitude),
            'depth': float(eq.depth),
            'location': eq.location,
            'city': eq.city or '',
            'source': eq.source,
            'occurred_at': eq.occurred_at.strftime('%Y-%m-%d %H:%M:%S'),
            'time_ago': f'{(timezone.now() - eq.occurred_at).days} gün önce' if (timezone.now() - eq.occurred_at).days > 0 else f'{(timezone.now() - eq.occurred_at).seconds // 3600} saat önce'
        })

    # For list: paginate
    from django.core.paginator import Paginator
    paginator = Paginator(earthquakes_qs, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Statistics
    total_earthquakes = len(earthquake_data)
    major_count = len([e for e in earthquake_data if e['magnitude'] >= 5.0])
    moderate_count = len([e for e in earthquake_data if 4.0 <= e['magnitude'] < 5.0])
    minor_count = len([e for e in earthquake_data if 3.0 <= e['magnitude'] < 4.0])

    # Get data sources with statistics
    data_sources = EarthquakeDataSource.objects.all().order_by('name')

    context = {
        'earthquake_data_json': json.dumps(earthquake_data),  # Convert to JSON string
        'page_obj': page_obj,  # For the list
        'total_earthquakes': total_earthquakes,
        'major_count': major_count,
        'moderate_count': moderate_count,
        'minor_count': minor_count,
        'filter_days': days,
        'filter_magnitude_min': magnitude_min,
        'filter_source': source_filter,
        'data_sources': data_sources,
    }

    return render(request, 'birlikteyiz/earthquake_map.html', context)