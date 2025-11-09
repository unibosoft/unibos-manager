"""
Version Manager URL Configuration
"""

from django.urls import path
from . import views

app_name = 'version_manager'

urlpatterns = [
    # Main dashboard
    path('', views.VersionManagerView.as_view(), name='dashboard'),
    
    # Archive analyzer
    path('analyzer/', views.ArchiveAnalyzerView.as_view(), name='analyzer'),
    
    # New feature pages
    path('anomaly-detection/', views.AnomalyDetectionView.as_view(), name='anomaly_detection'),
    path('scan-history/', views.ScanHistoryView.as_view(), name='scan_history'),
    path('archive-operations/', views.ArchiveOperationsView.as_view(), name='archive_operations'),
    
    # API endpoints for AJAX
    path('api/scan/start/', views.StartScanView.as_view(), name='start_scan'),
    path('api/scan/progress/<int:session_id>/', views.ScanProgressView.as_view(), name='scan_progress'),
    path('api/scan/stop/<int:session_id>/', views.StopScanView.as_view(), name='stop_scan'),
    path('api/git/status/', views.GitStatusView.as_view(), name='git_status'),
    path('api/archives/refresh/', views.RefreshArchivesView.as_view(), name='refresh_archives'),
]