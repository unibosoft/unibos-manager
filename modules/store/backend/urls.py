from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    # Dashboard
    path('', views.StoreDashboardView.as_view(), name='dashboard'),
    
    # Orders
    path('orders/', views.OrderListView.as_view(), name='order_list'),
    path('orders/<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('orders/<int:pk>/update-status/', views.order_update_status, name='order_update_status'),
    
    # Products
    path('products/', views.ProductListView.as_view(), name='product_list'),
    
    # Marketplaces
    path('marketplaces/', views.MarketplaceListView.as_view(), name='marketplace_list'),
    path('marketplaces/add/', views.marketplace_add, name='marketplace_add'),
    path('marketplaces/<int:pk>/sync/', views.marketplace_sync, name='marketplace_sync'),
    
    # API endpoints
    path('api/order-stats/', views.api_order_stats, name='api_order_stats'),
    path('api/inventory-status/', views.api_inventory_status, name='api_inventory_status'),
]