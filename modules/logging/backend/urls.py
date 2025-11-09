"""
URL configuration for logging app
"""

from django.urls import path
from . import views

app_name = 'logging'

urlpatterns = [
    # Dashboard
    path('', views.log_dashboard, name='dashboard'),
    
    # System logs
    path('system/', views.system_logs_view, name='system_logs'),
    
    # Activity logs
    path('activity/', views.activity_logs_view, name='activity_logs'),
    
    # API endpoints
    path('api/detail/<int:log_id>/', views.log_detail_api, name='log_detail'),
    path('export/', views.export_logs, name='export_logs'),
]