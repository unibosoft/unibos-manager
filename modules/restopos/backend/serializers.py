"""
RestoPOS Module Serializers
RESTful API serializers for restaurant POS system
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Restaurant, MenuCategory, MenuItem, Table,
    Order, OrderItem, Receipt, Reservation, Staff
)

User = get_user_model()


class RestaurantSerializer(serializers.ModelSerializer):
    """Restaurant serializer"""
    
    class Meta:
        model = Restaurant
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class MenuCategorySerializer(serializers.ModelSerializer):
    """Menu category serializer"""
    
    class Meta:
        model = MenuCategory
        fields = '__all__'
        read_only_fields = ['id']


class MenuItemSerializer(serializers.ModelSerializer):
    """Menu item serializer"""
    
    profit_margin = serializers.ReadOnlyField()
    category_name = serializers.ReadOnlyField(source='category.name')
    
    class Meta:
        model = MenuItem
        fields = '__all__'
        read_only_fields = ['id', 'times_ordered', 'rating', 'created_at', 'updated_at']


class TableSerializer(serializers.ModelSerializer):
    """Table serializer"""
    
    class Meta:
        model = Table
        fields = '__all__'
        read_only_fields = ['id', 'last_occupied', 'last_cleaned']


class OrderItemSerializer(serializers.ModelSerializer):
    """Order item serializer"""
    
    menu_item_name = serializers.ReadOnlyField(source='menu_item.name')
    
    class Meta:
        model = OrderItem
        fields = '__all__'
        read_only_fields = ['id', 'total_price', 'created_at']


class OrderSerializer(serializers.ModelSerializer):
    """Order serializer"""
    
    items = OrderItemSerializer(many=True, read_only=True)
    table_number = serializers.ReadOnlyField(source='table.table_number')
    waiter_name = serializers.ReadOnlyField(source='waiter.get_full_name')
    
    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = [
            'id', 'order_number', 'subtotal', 'tax_amount',
            'total_amount', 'created_at', 'confirmed_at',
            'completed_at', 'cancelled_at'
        ]


class ReceiptSerializer(serializers.ModelSerializer):
    """Receipt serializer"""
    
    order_number = serializers.ReadOnlyField(source='order.order_number')
    
    class Meta:
        model = Receipt
        fields = '__all__'
        read_only_fields = ['id', 'receipt_number', 'issued_at']


class ReservationSerializer(serializers.ModelSerializer):
    """Reservation serializer"""
    
    table_number = serializers.ReadOnlyField(source='table.table_number')
    
    class Meta:
        model = Reservation
        fields = '__all__'
        read_only_fields = ['id', 'confirmation_code', 'created_at', 'updated_at']


class StaffSerializer(serializers.ModelSerializer):
    """Staff serializer"""
    
    user_name = serializers.ReadOnlyField(source='user.get_full_name')
    restaurant_name = serializers.ReadOnlyField(source='restaurant.name')
    
    class Meta:
        model = Staff
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']