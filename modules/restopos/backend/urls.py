"""
RestoPOS Module URL Configuration
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'restopos'

router = DefaultRouter()
router.register(r'restaurants', views.RestaurantViewSet, basename='restaurant')
router.register(r'categories', views.MenuCategoryViewSet, basename='category')
router.register(r'menu-items', views.MenuItemViewSet, basename='menuitem')
router.register(r'tables', views.TableViewSet, basename='table')
router.register(r'orders', views.OrderViewSet, basename='order')
router.register(r'receipts', views.ReceiptViewSet, basename='receipt')
router.register(r'reservations', views.ReservationViewSet, basename='reservation')
router.register(r'staff', views.StaffViewSet, basename='staff')

urlpatterns = [
    # Web views
    path('', views.dashboard, name='dashboard'),
    
    # API endpoints
    path('api/', include(router.urls)),
]