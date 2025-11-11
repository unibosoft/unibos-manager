"""
Views for system and activity logging administration
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg, Max, Min
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from .models import SystemLog, ActivityLog, LogAggregation, LogLevel, LogCategory
import json


def is_admin(user):
    """Check if user is admin"""
    return user.is_superuser or user.groups.filter(name='admin').exists()


@login_required
@user_passes_test(is_admin)
def system_logs_view(request):
    """System logs viewer with filtering and search"""
    
    # Get filter parameters
    level = request.GET.get('level', '')
    category = request.GET.get('category', '')
    search = request.GET.get('search', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # Base queryset
    logs = SystemLog.objects.select_related('user')
    
    # Apply filters
    if level:
        logs = logs.filter(level=level)
    if category:
        logs = logs.filter(category=category)
    if search:
        logs = logs.filter(
            Q(message__icontains=search) |
            Q(module__icontains=search) |
            Q(function__icontains=search)
        )
    if date_from:
        logs = logs.filter(timestamp__gte=date_from)
    if date_to:
        logs = logs.filter(timestamp__lte=date_to)
    
    # Get statistics
    stats = logs.aggregate(
        total=Count('id'),
        errors=Count('id', filter=Q(level=LogLevel.ERROR)),
        warnings=Count('id', filter=Q(level=LogLevel.WARNING)),
        avg_duration=Avg('duration_ms')
    )
    
    # Pagination
    paginator = Paginator(logs, 50)
    page = request.GET.get('page', 1)
    logs_page = paginator.get_page(page)
    
    context = {
        'logs': logs_page,
        'stats': stats,
        'levels': LogLevel.choices,
        'categories': LogCategory.choices,
        'filters': {
            'level': level,
            'category': category,
            'search': search,
            'date_from': date_from,
            'date_to': date_to,
        }
    }
    
    return render(request, 'logging/system_logs.html', context)


@login_required
@user_passes_test(is_admin)
def activity_logs_view(request):
    """Activity logs viewer for user tracking"""
    
    # Get filter parameters
    user_id = request.GET.get('user', '')
    action = request.GET.get('action', '')
    module = request.GET.get('module', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # Base queryset
    logs = ActivityLog.objects.select_related('user')
    
    # Apply filters
    if user_id:
        logs = logs.filter(user_id=user_id)
    if action:
        logs = logs.filter(action__icontains=action)
    if module:
        logs = logs.filter(module=module)
    if date_from:
        logs = logs.filter(timestamp__gte=date_from)
    if date_to:
        logs = logs.filter(timestamp__lte=date_to)
    
    # Get unique users and modules for filters
    users = ActivityLog.objects.values_list('user__username', 'user__id').distinct()
    modules = ActivityLog.objects.values_list('module', flat=True).distinct()
    
    # Get statistics
    stats = logs.aggregate(
        total_actions=Count('id'),
        unique_users=Count('user', distinct=True),
        avg_duration=Avg('duration_ms'),
        success_rate=Avg('success') * 100 if logs.exists() else 0
    )
    
    # Pagination
    paginator = Paginator(logs, 50)
    page = request.GET.get('page', 1)
    logs_page = paginator.get_page(page)
    
    context = {
        'logs': logs_page,
        'stats': stats,
        'users': users,
        'modules': modules,
        'filters': {
            'user': user_id,
            'action': action,
            'module': module,
            'date_from': date_from,
            'date_to': date_to,
        }
    }
    
    return render(request, 'logging/activity_logs.html', context)


@login_required
@user_passes_test(is_admin)
def log_dashboard(request):
    """Main logging dashboard with aggregated statistics"""
    
    # Time ranges
    now = timezone.now()
    last_hour = now - timedelta(hours=1)
    last_24h = now - timedelta(hours=24)
    last_7d = now - timedelta(days=7)
    
    # System log statistics
    system_stats = {
        'last_hour': SystemLog.objects.filter(timestamp__gte=last_hour).aggregate(
            total=Count('id'),
            errors=Count('id', filter=Q(level=LogLevel.ERROR)),
            warnings=Count('id', filter=Q(level=LogLevel.WARNING)),
            avg_duration=Avg('duration_ms')
        ),
        'last_24h': SystemLog.objects.filter(timestamp__gte=last_24h).aggregate(
            total=Count('id'),
            errors=Count('id', filter=Q(level=LogLevel.ERROR)),
            warnings=Count('id', filter=Q(level=LogLevel.WARNING)),
            avg_duration=Avg('duration_ms')
        ),
        'last_7d': SystemLog.objects.filter(timestamp__gte=last_7d).aggregate(
            total=Count('id'),
            errors=Count('id', filter=Q(level=LogLevel.ERROR)),
            warnings=Count('id', filter=Q(level=LogLevel.WARNING)),
            avg_duration=Avg('duration_ms')
        ),
    }
    
    # Activity statistics
    activity_stats = {
        'last_hour': ActivityLog.objects.filter(timestamp__gte=last_hour).aggregate(
            total=Count('id'),
            unique_users=Count('user', distinct=True),
            success_rate=Avg('success') * 100
        ),
        'last_24h': ActivityLog.objects.filter(timestamp__gte=last_24h).aggregate(
            total=Count('id'),
            unique_users=Count('user', distinct=True),
            success_rate=Avg('success') * 100
        ),
        'last_7d': ActivityLog.objects.filter(timestamp__gte=last_7d).aggregate(
            total=Count('id'),
            unique_users=Count('user', distinct=True),
            success_rate=Avg('success') * 100
        ),
    }
    
    # Recent errors
    recent_errors = SystemLog.objects.filter(
        level=LogLevel.ERROR,
        timestamp__gte=last_24h
    ).select_related('user')[:10]
    
    # Most active users
    active_users = ActivityLog.objects.filter(
        timestamp__gte=last_24h
    ).values('user__username').annotate(
        action_count=Count('id')
    ).order_by('-action_count')[:10]
    
    # Error trends (hourly for last 24 hours)
    error_trends = []
    for i in range(24):
        hour_start = now - timedelta(hours=i+1)
        hour_end = now - timedelta(hours=i)
        count = SystemLog.objects.filter(
            level=LogLevel.ERROR,
            timestamp__gte=hour_start,
            timestamp__lt=hour_end
        ).count()
        error_trends.append({
            'hour': hour_start.strftime('%H:00'),
            'count': count
        })
    error_trends.reverse()
    
    context = {
        'system_stats': system_stats,
        'activity_stats': activity_stats,
        'recent_errors': recent_errors,
        'active_users': active_users,
        'error_trends': json.dumps(error_trends),
    }
    
    return render(request, 'logging/dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def log_detail_api(request, log_id):
    """API endpoint to get detailed log information"""
    
    log_type = request.GET.get('type', 'system')
    
    try:
        if log_type == 'system':
            log = SystemLog.objects.get(id=log_id)
            data = {
                'id': log.id,
                'timestamp': log.timestamp.isoformat(),
                'level': log.level,
                'category': log.category,
                'message': log.message,
                'module': log.module,
                'function': log.function,
                'user': log.user.username if log.user else None,
                'ip_address': log.ip_address,
                'request_method': log.request_method,
                'request_path': log.request_path,
                'duration_ms': log.duration_ms,
                'exception_type': log.exception_type,
                'traceback': log.traceback,
                'extra_data': log.extra_data,
            }
        else:
            log = ActivityLog.objects.get(id=log_id)
            data = {
                'id': log.id,
                'timestamp': log.timestamp.isoformat(),
                'user': log.user.username,
                'action': log.action,
                'module': log.module,
                'page_url': log.page_url,
                'object_type': log.object_type,
                'object_id': log.object_id,
                'object_repr': log.object_repr,
                'ip_address': log.ip_address,
                'success': log.success,
                'error_message': log.error_message,
                'duration_ms': log.duration_ms,
                'metadata': log.metadata,
            }
        
        return JsonResponse({'success': True, 'data': data})
    
    except (SystemLog.DoesNotExist, ActivityLog.DoesNotExist):
        return JsonResponse({'success': False, 'error': 'Log not found'}, status=404)


@login_required
@user_passes_test(is_admin)
def export_logs(request):
    """Export logs to CSV or JSON"""
    
    format = request.GET.get('format', 'csv')
    log_type = request.GET.get('type', 'system')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # Get logs
    if log_type == 'system':
        logs = SystemLog.objects.all()
    else:
        logs = ActivityLog.objects.all()
    
    # Apply date filters
    if date_from:
        logs = logs.filter(timestamp__gte=date_from)
    if date_to:
        logs = logs.filter(timestamp__lte=date_to)
    
    # Limit to last 10000 records for performance
    logs = logs[:10000]
    
    if format == 'json':
        # Export as JSON
        import json
        from django.core.serializers.json import DjangoJSONEncoder
        
        data = list(logs.values())
        response = JsonResponse(data, safe=False, encoder=DjangoJSONEncoder)
        response['Content-Disposition'] = f'attachment; filename="{log_type}_logs.json"'
    
    else:
        # Export as CSV
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{log_type}_logs.csv"'
        
        writer = csv.writer(response)
        
        # Write headers
        if log_type == 'system':
            writer.writerow(['Timestamp', 'Level', 'Category', 'Message', 'User', 'IP', 'Path', 'Duration'])
            for log in logs:
                writer.writerow([
                    log.timestamp,
                    log.level,
                    log.category,
                    log.message,
                    log.user.username if log.user else '',
                    log.ip_address,
                    log.request_path,
                    log.duration_ms
                ])
        else:
            writer.writerow(['Timestamp', 'User', 'Action', 'Module', 'URL', 'Success', 'Duration'])
            for log in logs:
                writer.writerow([
                    log.timestamp,
                    log.user.username,
                    log.action,
                    log.module,
                    log.page_url,
                    log.success,
                    log.duration_ms
                ])
    
    return response