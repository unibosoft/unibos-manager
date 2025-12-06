from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

User = get_user_model()
from django.db.models import Count, Q
from django.utils import timezone
from django.http import JsonResponse
from .models import Role, UserRole, Department, PermissionRequest, AuditLog, SystemSetting, ScreenLock, RecariaMailbox
from .mail_service import MailProvisioner
from modules.solitaire.backend.models import SolitairePlayer, SolitaireGameSession, SolitaireActivity, SolitaireMoveHistory
from modules.birlikteyiz.backend.models import CronJob, EarthquakeDataSource
import json
import logging
from datetime import timedelta
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.db.models import Avg
import csv

logger = logging.getLogger('unibos.mail')


def is_admin(user):
    """Check if user is admin or has admin role"""
    if user.is_superuser:
        return True
    return user.user_roles.filter(
        Q(role__can_access_admin=True) | Q(role__code='admin')
    ).exists()


@login_required(login_url='/login/')
@user_passes_test(is_admin, login_url='/login/')
def administration_dashboard(request):
    """Main administration dashboard"""
    pending_requests_count = PermissionRequest.objects.filter(status='pending').count()
    
    # Get recent activities for the table
    recent_activities = []
    recent_logs = AuditLog.objects.all()[:10]
    for log in recent_logs:
        recent_activities.append({
            'user': log.user.username if log.user else 'system',
            'action': log.get_action_display() if hasattr(log, 'get_action_display') else log.action,
            'target': log.target_object or '',
            'time': log.timestamp.strftime('%H:%M') if log.timestamp else '',
            'status': 'active'
        })
    
    # Count active sessions
    from django.contrib.sessions.models import Session
    active_sessions = Session.objects.filter(
        expire_date__gte=timezone.now()
    ).count()
    
    context = {
        'total_users': User.objects.count(),
        'total_roles': Role.objects.count(),
        'total_departments': Department.objects.count(),
        'pending_requests': pending_requests_count,
        'pending_requests_count': pending_requests_count,  # For sidebar badge
        'recent_logs': recent_logs,
        'recent_activities': recent_activities,
        'active_users': User.objects.filter(last_login__gte=timezone.now() - timezone.timedelta(days=7)).count(),
        'active_sessions': active_sessions,
        'system_roles': Role.objects.filter(is_system=True),
        'custom_roles': Role.objects.filter(is_system=False),
    }
    
    # Log the access
    AuditLog.objects.create(
        user=request.user,
        action='data_export',
        target_object='Administration Dashboard',
        details={'page': 'dashboard'},
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    
    # Add more context data
    context.update({
        'recent_users': User.objects.order_by('-date_joined')[:5],
        'departments_count': Department.objects.count(),
        'today_logs': AuditLog.objects.filter(
            timestamp__gte=timezone.now() - timezone.timedelta(hours=24)
        ).count(),
    })
    
    return render(request, 'administration/dashboard.html', context)


@login_required(login_url='/login/')
@user_passes_test(is_admin, login_url='/login/')
def users_list(request):
    """List all users with their roles"""
    users = User.objects.all().prefetch_related(
        'user_roles__role',
        'groups',
        'departments'
    ).annotate(
        role_count=Count('user_roles')
    )
    
    # Filter by department if specified
    dept_id = request.GET.get('dept')
    if dept_id:
        users = users.filter(departments__id=dept_id)
    
    # Filter by role if specified
    role_id = request.GET.get('role')
    if role_id:
        users = users.filter(user_roles__role__id=role_id)
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    
    context = {
        'users': users,
        'departments': Department.objects.all(),
        'roles': Role.objects.all(),
        'pending_requests_count': PermissionRequest.objects.filter(status='pending').count(),
    }
    
    return render(request, 'administration/users.html', context)


@login_required(login_url='/login/')
@user_passes_test(is_admin, login_url='/login/')
def user_detail(request, user_id):
    """View and edit user details"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add_role':
            role_id = request.POST.get('role_id')
            role = get_object_or_404(Role, id=role_id)
            expires_at = request.POST.get('expires_at')
            
            UserRole.objects.create(
                user=user,
                role=role,
                assigned_by=request.user,
                expires_at=expires_at if expires_at else None,
                is_temporary=bool(expires_at),
                notes=request.POST.get('notes', '')
            )
            
            AuditLog.objects.create(
                user=request.user,
                action='role_assign',
                target_user=user,
                target_object=f'Role: {role.name}',
                details={'role_id': role.id, 'expires_at': expires_at},
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, f'Role {role.name} assigned to {user.username}')
        
        elif action == 'remove_role':
            user_role_id = request.POST.get('user_role_id')
            user_role = get_object_or_404(UserRole, id=user_role_id, user=user)
            role_name = user_role.role.name
            user_role.delete()
            
            AuditLog.objects.create(
                user=request.user,
                action='role_remove',
                target_user=user,
                target_object=f'Role: {role_name}',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, f'Role {role_name} removed from {user.username}')
        
        elif action == 'update_user':
            user.first_name = request.POST.get('first_name', '')
            user.last_name = request.POST.get('last_name', '')
            user.email = request.POST.get('email', '')
            user.is_active = request.POST.get('is_active') == 'on'
            user.save()
            
            AuditLog.objects.create(
                user=request.user,
                action='user_update',
                target_user=user,
                details={'fields': ['first_name', 'last_name', 'email', 'is_active']},
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, f'User {user.username} updated')
        
        elif action == 'reset_screen_lock':
            # Reset screen lock for the user
            screen_lock, created = ScreenLock.objects.get_or_create(user=user)
            screen_lock.is_enabled = False
            screen_lock.password_hash = ''
            screen_lock.failed_attempts = 0
            screen_lock.locked_until = None
            screen_lock.save()
            
            AuditLog.objects.create(
                user=request.user,
                action='password_change',
                target_user=user,
                target_object='Screen Lock Reset',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, f'screen lock reset for {user.username}')
        
        elif action == 'configure_screen_lock':
            # Configure screen lock settings
            screen_lock, created = ScreenLock.objects.get_or_create(user=user)
            password = request.POST.get('screen_lock_password')
            
            if password:
                screen_lock.set_password(password)
                screen_lock.is_enabled = True
                screen_lock.auto_lock = request.POST.get('auto_lock') == 'on'
                screen_lock.lock_timeout = int(request.POST.get('lock_timeout', 300))
                screen_lock.require_on_startup = request.POST.get('require_on_startup') == 'on'
                screen_lock.save()
                
                messages.success(request, f'screen lock configured for {user.username}')
            else:
                messages.error(request, 'password is required to configure screen lock')
        
        return redirect('administration:user_detail', user_id=user.id)
    
    # Get screen lock info
    try:
        screen_lock = user.screen_lock
    except ScreenLock.DoesNotExist:
        screen_lock = None
    
    context = {
        'target_user': user,
        'user_roles': user.user_roles.all().select_related('role', 'assigned_by'),
        'available_roles': Role.objects.exclude(id__in=user.user_roles.values_list('role_id', flat=True)),
        'audit_logs': AuditLog.objects.filter(
            Q(user=user) | Q(target_user=user)
        ).order_by('-timestamp')[:20],
        'pending_requests_count': PermissionRequest.objects.filter(status='pending').count(),
        'screen_lock': screen_lock,
    }
    
    return render(request, 'administration/user_detail.html', context)


@login_required(login_url='/login/')
@user_passes_test(is_admin, login_url='/login/')
def roles_list(request):
    """List all roles"""
    roles = Role.objects.all().annotate(
        user_count=Count('user_assignments__user', distinct=True),
        permission_count=Count('permissions', distinct=True)
    )
    
    context = {
        'roles': roles,
        'pending_requests_count': PermissionRequest.objects.filter(status='pending').count(),  # For sidebar badge
    }
    
    return render(request, 'administration/roles.html', context)


@login_required(login_url='/login/')
@user_passes_test(is_admin, login_url='/login/')
def role_detail(request, role_id):
    """View and edit role details"""
    role = get_object_or_404(Role, id=role_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_role' and not role.is_system:
            role.name = request.POST.get('name', role.name)
            role.description = request.POST.get('description', '')
            role.priority = int(request.POST.get('priority', 0))
            
            # Update boolean permissions
            role.can_manage_users = request.POST.get('can_manage_users') == 'on'
            role.can_manage_roles = request.POST.get('can_manage_roles') == 'on'
            role.can_view_logs = request.POST.get('can_view_logs') == 'on'
            role.can_access_admin = request.POST.get('can_access_admin') == 'on'
            role.can_export_data = request.POST.get('can_export_data') == 'on'
            role.can_import_data = request.POST.get('can_import_data') == 'on'
            
            role.save()
            
            messages.success(request, f'Role {role.name} updated')
        
        elif action == 'add_permission':
            perm_id = request.POST.get('permission_id')
            permission = get_object_or_404(Permission, id=perm_id)
            role.permissions.add(permission)
            messages.success(request, f'Permission added to {role.name}')
        
        elif action == 'remove_permission':
            perm_id = request.POST.get('permission_id')
            permission = get_object_or_404(Permission, id=perm_id)
            role.permissions.remove(permission)
            messages.success(request, f'Permission removed from {role.name}')
        
        return redirect('administration:role_detail', role_id=role.id)
    
    # Get available permissions grouped by app
    from django.contrib.contenttypes.models import ContentType
    permissions_by_app = {}
    for ct in ContentType.objects.all():
        app_perms = Permission.objects.filter(content_type=ct)
        if app_perms.exists():
            permissions_by_app[ct.app_label] = app_perms
    
    context = {
        'role': role,
        'role_users': UserRole.objects.filter(role=role).select_related('user', 'assigned_by'),
        'permissions_by_app': permissions_by_app,
        'current_permissions': role.permissions.all(),
        'pending_requests_count': PermissionRequest.objects.filter(status='pending').count(),  # For sidebar badge
    }
    
    return render(request, 'administration/role_detail.html', context)


@login_required(login_url='/login/')
@user_passes_test(is_admin, login_url='/login/')
def departments_list(request):
    """List all departments"""
    departments = Department.objects.all().annotate(
        member_count=Count('members', distinct=True),
        subdept_count=Count('subdepartments', distinct=True)
    ).select_related('parent', 'manager', 'default_role')
    
    context = {
        'departments': departments,
        'pending_requests_count': PermissionRequest.objects.filter(status='pending').count(),  # For sidebar badge
    }
    
    return render(request, 'administration/departments.html', context)


@login_required(login_url='/login/')
@user_passes_test(is_admin, login_url='/login/')
def permission_requests(request):
    """View and manage permission requests"""
    requests_list = PermissionRequest.objects.all().select_related('user', 'role', 'reviewed_by')
    
    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        perm_request = get_object_or_404(PermissionRequest, id=request_id)
        action = request.POST.get('action')
        
        if action == 'approve':
            perm_request.status = 'approved'
            perm_request.reviewed_by = request.user
            perm_request.reviewed_at = timezone.now()
            perm_request.review_notes = request.POST.get('notes', '')
            perm_request.save()
            
            # Assign the role
            if perm_request.role:
                expires_at = None
                if perm_request.duration_days:
                    expires_at = timezone.now() + timezone.timedelta(days=perm_request.duration_days)
                
                UserRole.objects.create(
                    user=perm_request.user,
                    role=perm_request.role,
                    assigned_by=request.user,
                    expires_at=expires_at,
                    is_temporary=bool(expires_at),
                    notes=f'Approved request: {perm_request.reason}'
                )
            
            messages.success(request, f'Request approved for {perm_request.user.username}')
        
        elif action == 'reject':
            perm_request.status = 'rejected'
            perm_request.reviewed_by = request.user
            perm_request.reviewed_at = timezone.now()
            perm_request.review_notes = request.POST.get('notes', '')
            perm_request.save()
            
            messages.warning(request, f'Request rejected for {perm_request.user.username}')
        
        return redirect('administration:permission_requests')
    
    context = {
        'requests': requests_list,
        'pending_count': requests_list.filter(status='pending').count(),
    }
    
    return render(request, 'administration/permission_requests.html', context)


@login_required(login_url='/login/')
@user_passes_test(is_admin, login_url='/login/')
def system_logs(request):
    """System logs viewer with filtering and search"""
    from core.system.logging.backend.models import SystemLog
    
    # Get filter parameters
    level = request.GET.get('level', '')
    category = request.GET.get('category', '')
    search = request.GET.get('search', '')
    timerange = request.GET.get('timerange', '1h')
    export_format = request.GET.get('export', '')
    
    # Base queryset
    logs = SystemLog.objects.select_related('user').order_by('-timestamp')
    
    # Apply time range filter
    now = timezone.now()
    if timerange == '1h':
        logs = logs.filter(timestamp__gte=now - timedelta(hours=1))
    elif timerange == '24h':
        logs = logs.filter(timestamp__gte=now - timedelta(hours=24))
    elif timerange == '7d':
        logs = logs.filter(timestamp__gte=now - timedelta(days=7))
    elif timerange == '30d':
        logs = logs.filter(timestamp__gte=now - timedelta(days=30))
    
    # Apply other filters
    if level:
        logs = logs.filter(level=level)
    if category:
        logs = logs.filter(category=category)
    if search:
        logs = logs.filter(
            Q(message__icontains=search) |
            Q(module__icontains=search) |
            Q(function__icontains=search) |
            Q(path__icontains=search)
        )
    
    # Handle exports
    if export_format == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="system_logs.csv"'
        writer = csv.writer(response)
        writer.writerow(['Timestamp', 'Level', 'Category', 'Message', 'User', 'IP', 'Path', 'Duration'])
        for log in logs[:1000]:  # Limit export
            writer.writerow([
                log.timestamp,
                log.level,
                log.category,
                log.message,
                log.user.username if log.user else '',
                log.ip_address,
                log.path,
                log.duration_ms
            ])
        return response
    
    elif export_format == 'json':
        data = list(logs[:1000].values(
            'timestamp', 'level', 'category', 'message',
            'user__username', 'ip_address', 'path', 'duration_ms'
        ))
        return JsonResponse(data, safe=False)
    
    # Get statistics
    total_logs = logs.count()
    error_count = logs.filter(level='error').count()
    error_rate = (error_count / total_logs * 100) if total_logs > 0 else 0
    
    # Active users in last hour
    active_users = logs.filter(
        timestamp__gte=now - timedelta(hours=1),
        user__isnull=False
    ).values('user').distinct().count()
    
    # Average response time
    avg_response_time = logs.filter(
        duration_ms__isnull=False
    ).aggregate(avg=Avg('duration_ms'))['avg'] or 0
    
    # Chart data for last 24 hours
    chart_labels = []
    chart_data = []
    error_data = []
    for i in range(24):
        hour_start = now - timedelta(hours=23-i)
        hour_end = hour_start + timedelta(hours=1)
        hour_logs = logs.filter(timestamp__gte=hour_start, timestamp__lt=hour_end)
        chart_labels.append(hour_start.strftime('%H:00'))
        chart_data.append(hour_logs.count())
        error_data.append(hour_logs.filter(level='error').count())
    
    # Pagination
    paginator = Paginator(logs, 50)
    page = request.GET.get('page', 1)
    page_obj = paginator.get_page(page)
    
    context = {
        'logs': page_obj,
        'page_obj': page_obj,
        'total_logs': total_logs,
        'error_rate': round(error_rate, 2),
        'active_users': active_users,
        'avg_response_time': round(avg_response_time),
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
        'error_data': json.dumps(error_data),
        'pending_requests_count': PermissionRequest.objects.filter(status='pending').count(),
    }
    
    return render(request, 'administration/system_logs.html', context)


@login_required(login_url='/login/')
@user_passes_test(is_admin, login_url='/login/')
def audit_logs(request):
    """View audit logs"""
    logs = AuditLog.objects.all().select_related('user', 'target_user')
    
    # Filters
    action_type = request.GET.get('action')
    if action_type:
        logs = logs.filter(action=action_type)
    
    user_id = request.GET.get('user')
    if user_id:
        logs = logs.filter(user_id=user_id)
    
    date_from = request.GET.get('date_from')
    if date_from:
        logs = logs.filter(timestamp__gte=date_from)
    
    date_to = request.GET.get('date_to')
    if date_to:
        logs = logs.filter(timestamp__lte=date_to)
    
    context = {
        'logs': logs[:500],  # Limit to 500 most recent
        'action_types': AuditLog.ACTION_TYPES,
        'users': User.objects.filter(audit_logs__isnull=False).distinct(),
        'pending_requests_count': PermissionRequest.objects.filter(status='pending').count(),  # For sidebar badge
    }
    
    return render(request, 'administration/audit_logs.html', context)


@login_required(login_url='/login/')
@user_passes_test(is_admin, login_url='/login/') 
def system_settings(request):
    """Manage system settings"""
    if request.method == 'POST':
        key = request.POST.get('key')
        value = request.POST.get('value')
        description = request.POST.get('description', '')
        
        try:
            # Try to parse as JSON
            import json
            value = json.loads(value)
        except:
            # Keep as string if not valid JSON
            pass
        
        SystemSetting.set(key, value, description)
        messages.success(request, f'Setting {key} updated')
        
        return redirect('administration:system_settings')
    
    settings = SystemSetting.objects.all()
    
    context = {
        'settings': settings,
        'pending_requests_count': PermissionRequest.objects.filter(status='pending').count(),  # For sidebar badge
    }
    
    return render(request, 'administration/system_settings.html', context)


@login_required(login_url='/login/')
def screen_lock_settings(request):
    """Manage screen lock settings for current user"""
    screen_lock, created = ScreenLock.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'enable':
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            
            if password and password == confirm_password:
                screen_lock.set_password(password)
                screen_lock.is_enabled = True
                screen_lock.auto_lock = request.POST.get('auto_lock') == 'on'
                screen_lock.lock_timeout = int(request.POST.get('lock_timeout', 300))
                screen_lock.require_on_startup = request.POST.get('require_on_startup') == 'on'
                screen_lock.save()
                messages.success(request, 'screen lock enabled successfully')
            else:
                messages.error(request, 'passwords do not match')
        
        elif action == 'disable':
            current_password = request.POST.get('current_password')
            if screen_lock.check_password(current_password):
                screen_lock.is_enabled = False
                screen_lock.password_hash = ''
                screen_lock.save()
                messages.success(request, 'screen lock disabled')
            else:
                messages.error(request, 'incorrect password')
        
        elif action == 'update':
            current_password = request.POST.get('current_password')
            if screen_lock.check_password(current_password):
                screen_lock.auto_lock = request.POST.get('auto_lock') == 'on'
                screen_lock.lock_timeout = int(request.POST.get('lock_timeout', 300))
                screen_lock.require_on_startup = request.POST.get('require_on_startup') == 'on'
                screen_lock.save()
                messages.success(request, 'settings updated')
            else:
                messages.error(request, 'incorrect password')
        
        elif action == 'change_password':
            current_password = request.POST.get('current_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            
            if screen_lock.check_password(current_password):
                if new_password and new_password == confirm_password:
                    screen_lock.set_password(new_password)
                    messages.success(request, 'password changed successfully')
                else:
                    messages.error(request, 'new passwords do not match')
            else:
                messages.error(request, 'incorrect current password')
        
        return redirect('administration:screen_lock_settings')
    
    context = {
        'screen_lock': screen_lock,
        'timeout_options': [
            (60, '1 minute'),
            (180, '3 minutes'),
            (300, '5 minutes'),
            (600, '10 minutes'),
            (900, '15 minutes'),
            (1800, '30 minutes'),
            (3600, '1 hour'),
        ],
        'pending_requests_count': PermissionRequest.objects.filter(status='pending').count(),
    }
    
    return render(request, 'administration/screen_lock.html', context)


@login_required(login_url='/login/')
def unlock_screen(request):
    """Handle screen unlock"""
    if request.method == 'POST':
        password = request.POST.get('password')
        screen_lock = get_object_or_404(ScreenLock, user=request.user)
        
        if screen_lock.is_locked_out():
            return JsonResponse({
                'success': False,
                'error': 'too many failed attempts. please wait.'
            })
        
        if screen_lock.check_password(password):
            screen_lock.reset_failed_attempts()
            screen_lock.last_unlocked = timezone.now()
            screen_lock.save()

            # Clear session lock flag
            request.session['screen_locked'] = False

            # Get redirect URL from referer or default to home
            redirect_url = request.META.get('HTTP_REFERER', '/')
            # If coming from solitaire, redirect to home
            if 'solitaire' in redirect_url.lower():
                redirect_url = '/'

            return JsonResponse({'success': True, 'redirect_url': redirect_url})
        else:
            screen_lock.record_failed_attempt()
            remaining = screen_lock.max_failed_attempts - screen_lock.failed_attempts
            
            return JsonResponse({
                'success': False,
                'error': f'incorrect password. {remaining} attempts remaining.'
            })
    
    # Show lock screen
    return render(request, 'administration/lock_screen.html')


@login_required(login_url='/login/')
def lock_screen(request):
    """Lock the screen immediately"""
    screen_lock = get_object_or_404(ScreenLock, user=request.user)
    
    if screen_lock.is_enabled:
        screen_lock.last_locked = timezone.now()
        screen_lock.save()
        
        # Set session flag
        request.session['screen_locked'] = True
        
        return redirect('administration:unlock_screen')
    
    return redirect('/')


@login_required(login_url='/login/')
@user_passes_test(is_admin, login_url='/login/')
def delete_user(request, user_id):
    """Delete a user"""
    if request.method in ['POST', 'DELETE']:
        try:
            user = get_object_or_404(User, id=user_id)
            
            # Don't allow deleting superusers or self
            if user.is_superuser or user == request.user:
                return JsonResponse({'error': 'cannot delete this user'}, status=403)
            
            username = user.username
            user.delete()
            
            # Log the deletion
            AuditLog.objects.create(
                user=request.user,
                action='user_delete',
                target_object=f'User: {username}',
                details={'deleted_user_id': str(user_id), 'deleted_username': username},
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            messages.success(request, f'user {username} has been deleted')
            return JsonResponse({'success': True, 'message': f'user {username} deleted successfully'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'method not allowed'}, status=405)


@login_required(login_url='/login/')
@user_passes_test(is_admin, login_url='/login/')
def bulk_delete_users(request):
    """Delete multiple users at once"""
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            user_ids = data.get('user_ids', [])
            
            deleted_count = 0
            deleted_users = []
            skipped_users = []
            
            for user_id in user_ids:
                try:
                    user = User.objects.get(id=user_id)
                    # Don't allow deleting superusers or self
                    if user.is_superuser or user == request.user:
                        skipped_users.append(user.username)
                    else:
                        username = user.username
                        user.delete()
                        deleted_count += 1
                        deleted_users.append(username)
                except User.DoesNotExist:
                    continue
                except Exception as e:
                    print(f"Error deleting user {user_id}: {e}")
                    continue
            
            # Log the bulk deletion
            if deleted_count > 0:
                AuditLog.objects.create(
                    user=request.user,
                    action='user_delete',
                    target_object=f'Bulk delete: {deleted_count} users',
                    details={
                        'deleted_users': deleted_users, 
                        'skipped_users': skipped_users,
                        'user_ids': [str(uid) for uid in user_ids]
                    },
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
                messages.success(request, f'successfully deleted {deleted_count} users')
            
            return JsonResponse({
                'success': True, 
                'deleted_count': deleted_count,
                'deleted_users': deleted_users,
                'skipped_users': skipped_users
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'method not allowed'}, status=405)


@login_required(login_url='/login/')
@user_passes_test(is_admin, login_url='/login/')
def reset_user_password(request, user_id):
    """Reset user password and send email"""
    if request.method == 'POST':
        try:
            user = get_object_or_404(User, id=user_id)
            
            # Generate random password
            import string
            import random
            new_password = ''.join(random.choices(string.ascii_letters + string.digits + '!@#$%', k=12))
            
            # Set new password
            user.set_password(new_password)
            user.save()
            
            # Log the password reset
            AuditLog.objects.create(
                user=request.user,
                action='password_change',
                target_object=f'User: {user.username}',
                target_user=user,
                details={'reset_by_admin': True, 'user_id': str(user_id)},
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            # Send email with new password
            from django.core.mail import send_mail
            from django.conf import settings
            
            email_sent = False
            if user.email:
                try:
                    send_mail(
                        subject='password reset - unibos',
                        message=f'''hello {user.username},

your unibos password has been reset by an administrator.

your new temporary password is: {new_password}

please login and change this password immediately at:
https://recaria.org/login/

for security reasons, this password will expire in 24 hours.

regards,
unibos admin team
''',
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email],
                        fail_silently=False,
                    )
                    email_sent = True
                except Exception as email_error:
                    print(f"Email error: {email_error}")
            
            messages.success(request, f'password reset for {user.username}')
            
            return JsonResponse({
                'success': True, 
                'message': f'password reset successfully',
                'email_sent': email_sent,
                'email': user.email if email_sent else None,
                'temp_password': new_password  # Still return for testing, remove in production
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'method not allowed'}, status=405)


@login_required(login_url='/login/')
@user_passes_test(is_admin, login_url='/login/')
def toggle_user_status(request, user_id):
    """Toggle user active status"""
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        
        # Don't allow toggling superusers or self
        if user.is_superuser or user == request.user:
            return JsonResponse({'error': 'Cannot modify this user'}, status=403)
        
        user.is_active = not user.is_active
        user.save()
        
        status = 'activated' if user.is_active else 'deactivated'
        
        # Log the status change
        AuditLog.objects.create(
            user=request.user,
            action='user_status_change',
            target_user=user,
            target_object=f'User status: {status}',
            details={'user_id': user_id, 'is_active': user.is_active},
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        messages.success(request, f'User {user.username} has been {status}')
        return JsonResponse({'success': True, 'is_active': user.is_active})
    
    return JsonResponse({'error': 'method not allowed'}, status=405)


@login_required(login_url='/login/')
@user_passes_test(is_admin, login_url='/login/')
def bulk_status_users(request):
    """Change status for multiple users at once"""
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        user_ids = data.get('user_ids', [])
        active = data.get('active', True)
        
        updated_count = 0
        updated_users = []
        
        for user_id in user_ids:
            try:
                user = User.objects.get(id=user_id)
                # Don't allow modifying superusers or self
                if not user.is_superuser and user != request.user:
                    user.is_active = active
                    user.save()
                    updated_count += 1
                    updated_users.append(user.username)
            except User.DoesNotExist:
                continue
        
        status = 'activated' if active else 'deactivated'
        
        # Log the bulk status change
        if updated_count > 0:
            AuditLog.objects.create(
                user=request.user,
                action='bulk_status_change',
                target_object=f'Bulk {status}: {updated_count} users',
                details={'updated_users': updated_users, 'user_ids': user_ids, 'active': active},
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            messages.success(request, f'Successfully {status} {updated_count} users')
        
        return JsonResponse({'success': True, 'updated_count': updated_count})
    
    return JsonResponse({'error': 'method not allowed'}, status=405)


@login_required(login_url='/login/')
@user_passes_test(is_admin, login_url='/login/')
def solitaire_dashboard(request):
    """Enhanced Solitaire management dashboard with real-time stats"""
    from django.db.models import Sum, Avg, Max, Count, Q
    from datetime import timedelta
    
    now = timezone.now()
    today = now.date()
    
    # Get statistics with proper null handling
    total_players = SolitairePlayer.objects.count()
    active_players = SolitairePlayer.objects.filter(
        last_seen__gte=now - timedelta(days=7)
    ).count()
    
    # Today's active players
    today_players = SolitaireGameSession.objects.filter(
        started_at__date=today
    ).values('player').distinct().count()
    
    # Count games properly
    total_games = SolitaireGameSession.objects.filter(
        Q(is_completed=True) | Q(is_abandoned=True) | Q(is_won=True)
    ).count()
    
    # If no completed games, count all sessions
    if total_games == 0:
        total_games = SolitaireGameSession.objects.count()
    
    games_won = SolitaireGameSession.objects.filter(is_won=True).count()
    
    # Today's games
    today_games = SolitaireGameSession.objects.filter(started_at__date=today).count()
    today_won = SolitaireGameSession.objects.filter(started_at__date=today, is_won=True).count()
    
    # Recent activity - get last 20 sessions with real-time updates
    recent_sessions = SolitaireGameSession.objects.select_related("player").order_by("-started_at")[:20]
    
    # Active sessions - games started recently and not finished (real-time tracking)
    active_sessions = SolitaireGameSession.objects.filter(
        is_completed=False,
        is_abandoned=False,
        is_won=False,
        started_at__gte=now - timedelta(hours=1)
    ).select_related("player").order_by("-started_at")
    
    # Top players - group by player properly
    top_players = SolitairePlayer.objects.annotate(
        wins=Count("game_sessions", filter=Q(game_sessions__is_won=True)),
        total_games=Count("game_sessions"),
        total_score=Sum("game_sessions__score", filter=Q(game_sessions__is_won=True)),
        avg_score=Avg("game_sessions__score", filter=Q(game_sessions__is_won=True))
    ).filter(total_games__gt=0).order_by("-wins")[:10]
    
    # Format top players for display
    top_players_list = []
    for player in top_players:
        top_players_list.append({
            "player__id": player.id,
            "player__display_name": player.display_name,
            "player__user__username": player.user.username if player.user else None,
            "wins": player.wins or 0,
            "total_score": player.total_score or 0,
            "avg_score": player.avg_score or 0
        })
    
    # Calculate additional real-time statistics
    total_moves_today = SolitaireMoveHistory.objects.filter(
        timestamp__date=today
    ).count()
    
    avg_score_today = SolitaireGameSession.objects.filter(
        started_at__date=today,
        is_completed=True
    ).aggregate(avg=Avg('score'))['avg'] or 0
    
    # Real-time dashboard link
    realtime_dashboard_url = '/administration/solitaire/realtime/dashboard/'
    
    context = {
        "total_players": total_players,
        "active_players": active_players,
        "today_players": today_players,
        "total_games": total_games,
        "today_games": today_games,
        "games_won": games_won,
        "today_won": today_won,
        "win_rate": round((games_won / total_games * 100) if total_games > 0 else 0, 1),
        "today_win_rate": round((today_won / today_games * 100) if today_games > 0 else 0, 1),
        "total_moves_today": total_moves_today,
        "avg_score_today": round(avg_score_today, 0),
        "recent_sessions": recent_sessions,
        "active_sessions": active_sessions,
        "active_sessions_count": active_sessions.count(),
        "top_players": top_players_list,
        "pending_requests_count": PermissionRequest.objects.filter(status="pending").count(),
        "realtime_dashboard_url": realtime_dashboard_url,
        "auto_refresh": True,  # Enable auto-refresh for real-time updates
        "refresh_interval": 30,  # Refresh every 30 seconds
    }
    
    return render(request, "administration/solitaire/dashboard.html", context)


@login_required(login_url="/login/")
@user_passes_test(is_admin, login_url="/login/")
def solitaire_players(request):
    """List all solitaire players"""
    # Get players with proper statistics
    players = SolitairePlayer.objects.all().annotate(
        games_count=Count("game_sessions", distinct=True),
        wins_count=Count("game_sessions", filter=Q(game_sessions__is_won=True), distinct=True),
        total_score=Sum("game_sessions__score", filter=Q(game_sessions__score__isnull=False)),
        avg_score=Avg("game_sessions__score", filter=Q(game_sessions__score__isnull=False)),
        last_game=Max("game_sessions__started_at")
    ).order_by("-last_seen")
    
    # Filter by status
    status = request.GET.get("status")
    if status == "active":
        players = players.filter(is_active=True)
    elif status == "banned":
        players = players.filter(is_banned=True)
    elif status == "anonymous":
        players = players.filter(is_anonymous=True)
    elif status == "registered":
        players = players.filter(is_anonymous=False)
    
    # Search
    search = request.GET.get("search")
    if search:
        players = players.filter(
            Q(ip_address__icontains=search) |
            Q(display_name__icontains=search) |
            Q(user__username__icontains=search) |
            Q(country__icontains=search) |
            Q(city__icontains=search)
        )
    
    context = {
        "players": players,
        "total_count": players.count(),
        "active_count": players.filter(is_active=True).count(),
        "banned_count": players.filter(is_banned=True).count(),
        "pending_requests_count": PermissionRequest.objects.filter(status="pending").count(),
    }
    
    return render(request, "administration/solitaire/players.html", context)


@login_required(login_url="/login/")
@user_passes_test(is_admin, login_url="/login/")
def solitaire_sessions(request):
    """List all game sessions with filtering"""
    from django.db.models import Avg, F, ExpressionWrapper, DurationField
    from datetime import timedelta
    
    # Get sessions with calculated duration
    sessions = SolitaireGameSession.objects.select_related("player").annotate(
        duration=ExpressionWrapper(
            F("ended_at") - F("started_at"),
            output_field=DurationField()
        )
    ).order_by("-started_at")
    
    # Filter by status
    status = request.GET.get("status")
    if status == "active":
        sessions = sessions.filter(is_completed=False, is_abandoned=False)
    elif status == "won":
        sessions = sessions.filter(is_won=True)
    elif status == "abandoned":
        sessions = sessions.filter(is_abandoned=True)
    elif status == "completed":
        sessions = sessions.filter(is_completed=True)
    
    # Filter by date range
    date_from = request.GET.get("date_from")
    if date_from:
        sessions = sessions.filter(started_at__gte=date_from)
    
    date_to = request.GET.get("date_to")
    if date_to:
        sessions = sessions.filter(started_at__lte=date_to)
    
    # Search
    search = request.GET.get("search")
    if search:
        sessions = sessions.filter(
            Q(session_id__icontains=search) |
            Q(player__ip_address__icontains=search) |
            Q(player__display_name__icontains=search)
        )
    
    # Paginate
    from django.core.paginator import Paginator
    paginator = Paginator(sessions, 50)  # Show 50 sessions per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    # Get statistics with proper null handling
    total_sessions = sessions.count()
    won_sessions = sessions.filter(is_won=True).count()
    abandoned_sessions = sessions.filter(is_abandoned=True).count()
    
    # Calculate average score only for completed games with scores
    completed_with_score = sessions.filter(is_completed=True, score__isnull=False)
    avg_score = completed_with_score.aggregate(Avg("score"))["score__avg"] or 0
    
    # Calculate average time for completed games
    completed_with_time = sessions.filter(is_completed=True, time_played__isnull=False, time_played__gt=0)
    avg_time = completed_with_time.aggregate(Avg("time_played"))["time_played__avg"] or 0
    
    context = {
        "sessions": page_obj,
        "total_sessions": total_sessions,
        "won_sessions": won_sessions,
        "abandoned_sessions": abandoned_sessions,
        "win_rate": round((won_sessions / total_sessions * 100) if total_sessions > 0 else 0, 1),
        "avg_score": round(avg_score, 0),
        "avg_time": round(avg_time / 60, 1) if avg_time else 0,  # Convert to minutes
        "pending_requests_count": PermissionRequest.objects.filter(status="pending").count(),
    }
    
    return render(request, "administration/solitaire/sessions.html", context)


@login_required(login_url="/login/")
@user_passes_test(is_admin, login_url="/login/")
def cron_jobs_admin(request):
    """Manage system cron jobs"""
    from django.core.management import call_command
    from datetime import timedelta
    
    # Handle actions
    if request.method == 'POST':
        action = request.POST.get('action')
        job_id = request.POST.get('job_id')
        
        if action == 'toggle' and job_id:
            job = get_object_or_404(CronJob, id=job_id)
            job.is_active = not job.is_active
            job.save()
            
            status = 'enabled' if job.is_active else 'disabled'
            messages.success(request, f'cron job "{job.name}" {status}')
            
            AuditLog.objects.create(
                user=request.user,
                action='system_config',
                target_object=f'CronJob: {job.name}',
                details={'action': 'toggle', 'is_active': job.is_active},
                ip_address=request.META.get('REMOTE_ADDR')
            )
        
        elif action == 'run_now' and job_id:
            job = get_object_or_404(CronJob, id=job_id)
            
            # Run the job manually
            try:
                job.status = 'running'
                job.last_run = timezone.now()
                job.save()
                
                # Execute command based on job name
                if job.name == 'Fetch Earthquakes':
                    call_command('fetch_earthquakes')
                    messages.success(request, f'manually triggered: {job.name}')
                else:
                    messages.warning(request, f'manual trigger not configured for: {job.name}')
                
                AuditLog.objects.create(
                    user=request.user,
                    action='system_config',
                    target_object=f'CronJob: {job.name}',
                    details={'action': 'manual_run'},
                    ip_address=request.META.get('REMOTE_ADDR')
                )
            except Exception as e:
                messages.error(request, f'error running job: {str(e)}')
        
        elif action == 'reset_errors' and job_id:
            job = get_object_or_404(CronJob, id=job_id)
            job.error_count = 0
            job.last_error = None
            job.save()
            messages.success(request, f'error count reset for: {job.name}')
        
        elif action == 'create':
            name = request.POST.get('name')
            command = request.POST.get('command')
            schedule = request.POST.get('schedule', '*/5 * * * *')
            
            if name and command:
                CronJob.objects.create(
                    name=name,
                    command=command,
                    schedule=schedule,
                    is_active=False
                )
                messages.success(request, f'cron job "{name}" created (disabled by default)')
        
        return redirect('administration:cron_jobs')
    
    # Get all cron jobs
    jobs = CronJob.objects.all().order_by('name')
    
    # Get earthquake data sources for additional info
    data_sources = EarthquakeDataSource.objects.all()
    
    # Calculate statistics
    active_jobs = jobs.filter(is_active=True).count()
    failed_jobs = jobs.filter(status='failed').count()
    
    # Find jobs that need attention
    jobs_needing_attention = []
    for job in jobs:
        if job.error_count > 5:
            jobs_needing_attention.append({
                'job': job,
                'reason': f'high error count ({job.error_count})'
            })
        elif job.status == 'failed' and job.is_active:
            jobs_needing_attention.append({
                'job': job,
                'reason': 'last run failed'
            })
        elif job.next_run and job.next_run < timezone.now() - timedelta(hours=1):
            jobs_needing_attention.append({
                'job': job,
                'reason': 'overdue (not running)'
            })
    
    context = {
        'jobs': jobs,
        'data_sources': data_sources,
        'active_jobs': active_jobs,
        'failed_jobs': failed_jobs,
        'total_jobs': jobs.count(),
        'jobs_needing_attention': jobs_needing_attention,
        'pending_requests_count': PermissionRequest.objects.filter(status='pending').count(),
        'schedule_examples': [
            ('*/5 * * * *', 'every 5 minutes'),
            ('0 * * * *', 'every hour'),
            ('0 */6 * * *', 'every 6 hours'),
            ('0 0 * * *', 'daily at midnight'),
            ('0 3 * * 1', 'weekly on monday at 3am'),
        ]
    }
    
    return render(request, 'administration/cron_jobs.html', context)


@login_required(login_url='/login/')
@user_passes_test(is_admin, login_url='/login/')
def mailbox_list(request):
    """list all recaria.org mailboxes"""
    mailboxes = RecariaMailbox.objects.all().select_related('user')
    users_without_mailbox = User.objects.exclude(
        id__in=RecariaMailbox.objects.values_list('user_id', flat=True)
    )
    
    context = {
        'mailboxes': mailboxes,
        'users_without_mailbox': users_without_mailbox,
        'pending_requests_count': PermissionRequest.objects.filter(status='pending').count(),
    }
    
    return render(request, 'administration/mailboxes.html', context)


@login_required(login_url='/login/')
@user_passes_test(is_admin, login_url='/login/')
def mailbox_create(request):
    """create a new recaria.org mailbox for a user"""
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        email_prefix = request.POST.get('email_prefix', '').lower()
        provision_now = request.POST.get('provision_now') == 'on'

        if not user_id or not email_prefix:
            messages.error(request, 'user and email prefix are required')
            return redirect('administration:mailbox_list')

        user = get_object_or_404(User, id=user_id)
        email_address = f"{email_prefix}@recaria.org"

        # Check if email already exists
        if RecariaMailbox.objects.filter(email_address=email_address).exists():
            messages.error(request, f'email address {email_address} already exists')
            return redirect('administration:mailbox_list')

        # Check if user already has a mailbox
        if RecariaMailbox.objects.filter(user=user).exists():
            messages.error(request, f'user {user.username} already has a mailbox')
            return redirect('administration:mailbox_list')

        mailbox_size = int(request.POST.get('mailbox_size_mb', 1024))

        # Create mailbox record
        mailbox = RecariaMailbox.objects.create(
            user=user,
            email_address=email_address,
            mailbox_size_mb=mailbox_size,
            daily_send_limit=int(request.POST.get('daily_send_limit', 500)),
            attachment_size_limit_mb=int(request.POST.get('attachment_size_limit_mb', 25)),
            imap_enabled=request.POST.get('imap_enabled') == 'on',
            pop3_enabled=request.POST.get('pop3_enabled') == 'on',
            smtp_enabled=request.POST.get('smtp_enabled') == 'on',
        )

        temp_password = None

        # Provision on mail server if requested
        if provision_now:
            try:
                provisioner = MailProvisioner()
                success, msg, temp_password = provisioner.create_mailbox(
                    email=email_address,
                    quota_mb=mailbox_size
                )

                if success:
                    mailbox.mailbox_created = True
                    mailbox.password_set = True
                    mailbox.save()
                    messages.success(request, f'mailbox provisioned on server. temp password: {temp_password}')
                    logger.info(f'mailbox provisioned: {email_address}')
                else:
                    messages.warning(request, f'mailbox record created but server provisioning failed: {msg}')
                    logger.warning(f'mailbox provisioning failed: {email_address} - {msg}')
            except Exception as e:
                messages.warning(request, f'mailbox record created but server error: {str(e)}')
                logger.error(f'mailbox provisioning error: {email_address} - {e}')

        # Log the action
        AuditLog.objects.create(
            user=request.user,
            action='user_create',
            target_user=user,
            target_object=f'mailbox: {email_address}',
            details={
                'mailbox_id': str(mailbox.id),
                'email': email_address,
                'provisioned': mailbox.mailbox_created
            },
            ip_address=request.META.get('REMOTE_ADDR')
        )

        messages.success(request, f'mailbox {email_address} created for {user.username}')
        return redirect('administration:mailbox_detail', mailbox_id=mailbox.id)

    return redirect('administration:mailbox_list')


@login_required(login_url='/login/')
@user_passes_test(is_admin, login_url='/login/')
def mailbox_detail(request, mailbox_id):
    """view and manage a specific mailbox"""
    mailbox = get_object_or_404(RecariaMailbox, id=mailbox_id)
    provisioner = MailProvisioner()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update_settings':
            mailbox.mailbox_size_mb = int(request.POST.get('mailbox_size_mb', 1024))
            mailbox.daily_send_limit = int(request.POST.get('daily_send_limit', 500))
            mailbox.attachment_size_limit_mb = int(request.POST.get('attachment_size_limit_mb', 25))
            mailbox.imap_enabled = request.POST.get('imap_enabled') == 'on'
            mailbox.pop3_enabled = request.POST.get('pop3_enabled') == 'on'
            mailbox.smtp_enabled = request.POST.get('smtp_enabled') == 'on'
            mailbox.save()

            messages.success(request, 'mailbox settings updated')

        elif action == 'provision':
            # Provision mailbox on server
            try:
                success, msg, temp_password = provisioner.create_mailbox(
                    email=mailbox.email_address,
                    quota_mb=mailbox.mailbox_size_mb
                )

                if success:
                    mailbox.mailbox_created = True
                    mailbox.password_set = True
                    mailbox.save()
                    messages.success(request, f'mailbox provisioned! temp password: {temp_password}')
                    logger.info(f'mailbox provisioned: {mailbox.email_address}')
                else:
                    messages.error(request, f'provisioning failed: {msg}')
            except Exception as e:
                messages.error(request, f'server error: {str(e)}')
                logger.error(f'mailbox provisioning error: {e}')

        elif action == 'toggle_active':
            mailbox.is_active = not mailbox.is_active
            if not mailbox.is_active:
                mailbox.suspended_reason = request.POST.get('reason', '')
            else:
                mailbox.suspended_reason = ''
            mailbox.save()

            # Sync with mail server
            if mailbox.mailbox_created:
                try:
                    provisioner.suspend_mailbox(mailbox.email_address, not mailbox.is_active)
                except Exception as e:
                    logger.warning(f'could not sync suspend status to server: {e}')

            status = 'activated' if mailbox.is_active else 'suspended'
            messages.success(request, f'mailbox {status}')

        elif action == 'set_forwarding':
            mailbox.forwarding_enabled = request.POST.get('forwarding_enabled') == 'on'
            mailbox.forwarding_address = request.POST.get('forwarding_address', '')
            mailbox.save()

            # Sync forwarding with mail server
            if mailbox.mailbox_created:
                try:
                    forward_to = mailbox.forwarding_address if mailbox.forwarding_enabled else ''
                    provisioner.set_forwarding(mailbox.email_address, forward_to, keep_copy=True)
                except Exception as e:
                    logger.warning(f'could not sync forwarding to server: {e}')

            if mailbox.forwarding_enabled:
                messages.success(request, f'forwarding enabled to {mailbox.forwarding_address}')
            else:
                messages.success(request, 'forwarding disabled')

        elif action == 'set_autoresponder':
            mailbox.auto_responder_enabled = request.POST.get('auto_responder_enabled') == 'on'
            mailbox.auto_responder_message = request.POST.get('auto_responder_message', '')
            mailbox.save()

            # Sync auto-responder with mail server
            if mailbox.mailbox_created:
                try:
                    provisioner.set_auto_responder(
                        mailbox.email_address,
                        mailbox.auto_responder_enabled,
                        mailbox.auto_responder_message
                    )
                except Exception as e:
                    logger.warning(f'could not sync auto-responder to server: {e}')

            if mailbox.auto_responder_enabled:
                messages.success(request, 'auto-responder enabled')
            else:
                messages.success(request, 'auto-responder disabled')

        elif action == 'reset_password':
            # Generate and set new password
            try:
                from .mail_service import generate_password
                new_password = generate_password()
                success, msg = provisioner.change_password(mailbox.email_address, new_password)

                if success:
                    messages.success(request, f'password reset! new password: {new_password}')
                    logger.info(f'password reset for: {mailbox.email_address}')
                else:
                    messages.error(request, f'password reset failed: {msg}')
            except Exception as e:
                messages.error(request, f'error resetting password: {str(e)}')
                logger.error(f'password reset error: {e}')

        elif action == 'refresh_stats':
            # Refresh usage statistics from server
            if mailbox.mailbox_created:
                try:
                    success, stats = provisioner.get_mailbox_usage(mailbox.email_address)
                    if success:
                        mailbox.current_usage_mb = stats['size_mb']
                        mailbox.messages_received = stats.get('message_count', mailbox.messages_received)
                        mailbox.save()
                        messages.success(request, f'stats updated: {stats["size_mb"]}mb, {stats["message_count"]} messages')
                    else:
                        messages.warning(request, f'could not fetch stats: {stats.get("error", "unknown")}')
                except Exception as e:
                    messages.error(request, f'error fetching stats: {str(e)}')
            else:
                messages.warning(request, 'mailbox not provisioned on server yet')

        elif action == 'delete':
            email = mailbox.email_address
            user = mailbox.user
            delete_data = request.POST.get('delete_data') == 'on'

            # Delete from mail server if provisioned
            if mailbox.mailbox_created:
                try:
                    provisioner.delete_mailbox(email, delete_data=delete_data)
                    logger.info(f'mailbox deleted from server: {email}')
                except Exception as e:
                    logger.warning(f'could not delete mailbox from server: {e}')

            mailbox.delete()

            AuditLog.objects.create(
                user=request.user,
                action='user_delete',
                target_user=user,
                target_object=f'mailbox: {email}',
                details={'deleted_server_data': delete_data},
                ip_address=request.META.get('REMOTE_ADDR')
            )

            messages.success(request, f'mailbox {email} deleted')
            return redirect('administration:mailbox_list')

        return redirect('administration:mailbox_detail', mailbox_id=mailbox.id)

    # Get server status for context
    server_status = None
    try:
        server_status = provisioner.get_server_status()
    except Exception:
        pass

    context = {
        'mailbox': mailbox,
        'server_status': server_status,
        'pending_requests_count': PermissionRequest.objects.filter(status='pending').count(),
    }

    return render(request, 'administration/mailbox_detail.html', context)
