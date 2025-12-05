"""
Sync API URL configuration
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    SyncInitView,
    SyncPullView,
    SyncPushView,
    SyncCompleteView,
    SyncStatusView,
    SyncConflictViewSet,
    OfflineOperationViewSet,
    ExportSettingsView,
    KillSwitchView,
    ModulePermissionView,
    ExportCheckView,
    ExportLogsView,
    ExportStatsView,
)

router = DefaultRouter()
router.register('conflicts', SyncConflictViewSet, basename='sync-conflict')
router.register('offline', OfflineOperationViewSet, basename='offline-operation')

app_name = 'sync'

urlpatterns = [
    # Core sync endpoints
    path('init/', SyncInitView.as_view(), name='sync-init'),
    path('pull/', SyncPullView.as_view(), name='sync-pull'),
    path('push/', SyncPushView.as_view(), name='sync-push'),
    path('complete/', SyncCompleteView.as_view(), name='sync-complete'),
    path('status/', SyncStatusView.as_view(), name='sync-status'),

    # Data export control endpoints
    path('export/settings/', ExportSettingsView.as_view(), name='export-settings'),
    path('export/kill-switch/', KillSwitchView.as_view(), name='export-kill-switch'),
    path('export/module-permission/', ModulePermissionView.as_view(), name='export-module-permission'),
    path('export/check/', ExportCheckView.as_view(), name='export-check'),
    path('export/logs/', ExportLogsView.as_view(), name='export-logs'),
    path('export/stats/', ExportStatsView.as_view(), name='export-stats'),

    # ViewSets
    path('', include(router.urls)),
]
