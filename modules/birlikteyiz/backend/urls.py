from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, api_views, admin_views

app_name = 'birlikteyiz'

# REST API Router
router = DefaultRouter()
router.register(r'earthquakes', api_views.EarthquakeViewSet, basename='api-earthquake')
router.register(r'data-sources', api_views.DataSourceViewSet, basename='api-datasource')
router.register(r'disaster-zones', api_views.DisasterZoneViewSet, basename='api-zone')
router.register(r'mesh-nodes', api_views.MeshNodeViewSet, basename='api-node')

urlpatterns = [
    # Web UI
    path('', views.earthquake_map, name='dashboard'),
    path('earthquakes/', views.earthquake_map, name='earthquake_list'),  # Redirect to map (list is now integrated)
    path('map/', views.earthquake_map, name='earthquake_map'),
    path('cron-jobs/', views.cron_jobs, name='cron_jobs'),
    path('manual-fetch/', views.manual_fetch, name='manual_fetch'),
    path('source-admin/', views.source_admin, name='source_admin'),

    # Admin API for Data Source Management
    path('admin/source/<int:source_id>/', admin_views.update_data_source, name='admin_update_source'),
    path('admin/source/<int:source_id>/toggle/', admin_views.toggle_data_source, name='admin_toggle_source'),
    path('admin/source/<int:source_id>/reset-stats/', admin_views.reset_source_stats, name='admin_reset_stats'),
    path('admin/source/<int:source_id>/test/', admin_views.test_data_source, name='admin_test_source'),
    path('admin/preset-regions/', admin_views.get_preset_regions, name='admin_preset_regions'),
    path('admin/fetch-all/', admin_views.fetch_all_sources, name='admin_fetch_all'),
    path('admin/fetch-source/<int:source_id>/', admin_views.fetch_single_source, name='admin_fetch_source'),

    # REST API
    path('api/', include(router.urls)),
]
