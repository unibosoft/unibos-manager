"""
RestoPOS Module Views
Secure and performant API views for restaurant POS
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils import timezone

from .models import (
    Restaurant, MenuCategory, MenuItem, Table,
    Order, Receipt, Reservation, Staff
)
from .serializers import (
    RestaurantSerializer, MenuCategorySerializer, MenuItemSerializer,
    TableSerializer, OrderSerializer, ReceiptSerializer,
    ReservationSerializer, StaffSerializer
)


class RestaurantAccessMixin:
    """
    Mixin to filter queryset based on user's restaurant access.
    Implements multi-tenant data isolation.
    """
    
    def get_user_restaurants(self):
        """Get restaurants where the current user has access"""
        user = self.request.user
        
        if user.is_superuser:
            # Superusers can access all restaurants
            return Restaurant.objects.all()
        
        # Get restaurants where user is a staff member
        staff_records = Staff.objects.filter(
            user=user,
            is_active=True
        ).select_related('restaurant')
        
        return Restaurant.objects.filter(
            id__in=staff_records.values_list('restaurant_id', flat=True)
        ).distinct()
    
    def filter_queryset_by_restaurant(self, queryset):
        """Filter queryset to only include records from user's restaurants"""
        user_restaurants = self.get_user_restaurants()
        
        # Determine the field name to filter on
        model = queryset.model
        if model == Restaurant:
            return queryset.filter(id__in=user_restaurants.values_list('id', flat=True))
        elif hasattr(model, 'restaurant'):
            return queryset.filter(restaurant__in=user_restaurants)
        
        return queryset
    
    def get_queryset(self):
        """Override to apply restaurant-based filtering"""
        queryset = super().get_queryset()
        return self.filter_queryset_by_restaurant(queryset)


class RestaurantViewSet(RestaurantAccessMixin, viewsets.ModelViewSet):
    """Restaurant management"""
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = [IsAuthenticated]


class MenuCategoryViewSet(RestaurantAccessMixin, viewsets.ModelViewSet):
    """Menu category management"""
    queryset = MenuCategory.objects.all()
    serializer_class = MenuCategorySerializer
    permission_classes = [IsAuthenticated]


class MenuItemViewSet(RestaurantAccessMixin, viewsets.ModelViewSet):
    """Menu item management"""
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsAuthenticated]


class TableViewSet(RestaurantAccessMixin, viewsets.ModelViewSet):
    """Table management"""
    queryset = Table.objects.all()
    serializer_class = TableSerializer
    permission_classes = [IsAuthenticated]


class OrderViewSet(RestaurantAccessMixin, viewsets.ModelViewSet):
    """Order management"""
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]


class ReceiptViewSet(RestaurantAccessMixin, viewsets.ModelViewSet):
    """Receipt management"""
    queryset = Receipt.objects.all()
    serializer_class = ReceiptSerializer
    permission_classes = [IsAuthenticated]


class ReservationViewSet(RestaurantAccessMixin, viewsets.ModelViewSet):
    """Reservation management"""
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]


class StaffViewSet(RestaurantAccessMixin, viewsets.ModelViewSet):
    """Staff management"""
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer
    permission_classes = [IsAuthenticated]


@login_required
def dashboard(request):
    """
    RestoPOS module dashboard view
    """
    context = {
        'module_name': 'RestoPOS',
        'module_description': 'Restaurant Point of Sale System',
        'user': request.user,
    }
    
    # Get restaurant statistics for the user
    if request.user.is_authenticated:
        # Get restaurants where user is a staff member (manager role has full access)
        # Using select_related to optimize database queries
        user_staff_records = Staff.objects.filter(
            user=request.user,
            is_active=True
        ).select_related('restaurant')
        
        # Extract unique restaurants where user has access
        user_restaurants = Restaurant.objects.filter(
            id__in=user_staff_records.values_list('restaurant_id', flat=True)
        ).distinct()
        
        # For superusers, show all restaurants
        if request.user.is_superuser:
            user_restaurants = Restaurant.objects.all()
        
        context['stats'] = {
            'restaurants_count': user_restaurants.count(),
            'active_orders': Order.objects.filter(
                restaurant__in=user_restaurants,
                status__in=['pending', 'in_progress', 'preparing', 'ready']
            ).count() if user_restaurants.exists() else 0,
            'reservations_today': Reservation.objects.filter(
                restaurant__in=user_restaurants,
                reservation_date=timezone.now().date(),
                status__in=['pending', 'confirmed']
            ).count() if user_restaurants.exists() else 0,
        }
        
        # Add user's role information if they are staff
        if user_staff_records.exists():
            context['user_roles'] = list(user_staff_records.values_list('role', flat=True).distinct())
        else:
            context['user_roles'] = []
    
    return render(request, 'restopos/dashboard.html', context)