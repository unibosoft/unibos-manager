from django.urls import path, include
from . import views

app_name = 'administration'

urlpatterns = [
    path('', views.administration_dashboard, name='dashboard'),
    path('users/', views.users_list, name='users'),
    path('users/<uuid:user_id>/', views.user_detail, name='user_detail'),
    path('users/<uuid:user_id>/delete/', views.delete_user, name='delete_user'),
    path('users/<uuid:user_id>/reset-password/', views.reset_user_password, name='reset_user_password'),
    path('users/<uuid:user_id>/toggle-status/', views.toggle_user_status, name='toggle_user_status'),
    path('users/bulk-delete/', views.bulk_delete_users, name='bulk_delete_users'),
    path('users/bulk-status/', views.bulk_status_users, name='bulk_status_users'),
    path('roles/', views.roles_list, name='roles'),
    path('roles/<int:role_id>/', views.role_detail, name='role_detail'),
    path('departments/', views.departments_list, name='departments'),
    path('requests/', views.permission_requests, name='permission_requests'),
    path('logs/', views.audit_logs, name='audit_logs'),
    path('system-logs/', views.system_logs, name='system_logs'),
    path('settings/', views.system_settings, name='system_settings'),
    path('screen-lock/', views.screen_lock_settings, name='screen_lock_settings'),
    path('unlock/', views.unlock_screen, name='unlock_screen'),
    path('lock/', views.lock_screen, name='lock_screen'),
    
    # System and Activity Logging
    path('system-logs/', include('core.system.logging.backend.urls')),
    
    # Solitaire management
    path('solitaire/', views.solitaire_dashboard, name='solitaire_dashboard'),
    path('solitaire/players/', views.solitaire_players, name='solitaire_players'),
    path('solitaire/sessions/', views.solitaire_sessions, name='solitaire_sessions'),
    
    # Enhanced Solitaire Dashboard
    path('solitaire/realtime/', include('modules.solitaire.backend.admin_urls')),
    
    # Cron job management
    path('cron-jobs/', views.cron_jobs_admin, name='cron_jobs'),
    
    # Recaria.org mailbox management
    path('mailboxes/', views.mailbox_list, name='mailbox_list'),
    path('mailboxes/create/', views.mailbox_create, name='mailbox_create'),
    path('mailboxes/<int:mailbox_id>/', views.mailbox_detail, name='mailbox_detail'),
]