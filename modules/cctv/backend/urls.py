"""
CCTV URL Configuration
"""

from django.urls import path
from . import views

app_name = 'cctv'

urlpatterns = [
    # Main views
    path('', views.CCTVDashboardView.as_view(), name='dashboard'),
    path('grid/', views.CameraGridView.as_view(), name='camera_grid'),
    path('camera/<uuid:pk>/', views.CameraDetailView.as_view(), name='camera_detail'),
    
    # Live streaming
    path('live/<uuid:camera_id>/', views.LiveStreamView.as_view(), name='live_stream'),
    path('stream/<uuid:camera_id>/', views.StreamProxyView.as_view(), name='stream_proxy'),
    path('snapshot/<uuid:camera_id>/', views.SnapshotView.as_view(), name='snapshot'),
    
    # Recording management
    path('recordings/', views.RecordingListView.as_view(), name='recordings'),
    path('playback/<uuid:pk>/', views.RecordingPlaybackView.as_view(), name='playback'),
    path('record/start/<uuid:camera_id>/', views.start_recording, name='start_recording'),
    path('record/stop/<uuid:camera_id>/', views.stop_recording, name='stop_recording'),
    
    # Alert management
    path('alerts/', views.AlertListView.as_view(), name='alerts'),
    path('alert/resolve/<uuid:alert_id>/', views.resolve_alert, name='resolve_alert'),
    
    # Settings
    path('settings/', views.CameraSettingsView.as_view(), name='settings'),
    
    # API endpoints
    path('api/ptz/<uuid:camera_id>/', views.camera_ptz_control, name='ptz_control'),
    path('api/status/', views.camera_status, name='camera_status'),
]