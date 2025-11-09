"""
RestoPOS Module Admin Configuration
"""

from django.contrib import admin
from .models import (
    Restaurant, MenuCategory, MenuItem, Table,
    Order, OrderItem, Receipt, Reservation, Staff
)


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ['name', 'branch_code', 'city', 'country', 'currency']
    search_fields = ['name', 'branch_code', 'city']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(MenuCategory)
class MenuCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'restaurant', 'display_order', 'is_active']
    list_filter = ['restaurant', 'is_active']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['restaurant', 'display_order']


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'is_available', 'times_ordered', 'rating']
    search_fields = ['name', 'description']
    list_filter = ['category', 'item_type', 'is_available', 'is_vegetarian', 'is_vegan']
    prepopulated_fields = {'slug': ('name',)}


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'restaurant', 'status', 'order_type', 'table', 'total_amount', 'created_at']
    list_filter = ['status', 'order_type', 'payment_status', 'created_at']
    search_fields = ['order_number', 'customer_name', 'customer_phone']
    date_hierarchy = 'created_at'
    inlines = [OrderItemInline]


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ['table_number', 'restaurant', 'section', 'capacity', 'status']
    list_filter = ['restaurant', 'status', 'section']
    search_fields = ['table_number']


@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ['receipt_number', 'order', 'total_amount', 'payment_method', 'issued_at']
    search_fields = ['receipt_number', 'order__order_number']
    list_filter = ['payment_method', 'issued_at']
    date_hierarchy = 'issued_at'


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['customer_name', 'restaurant', 'reservation_date', 'reservation_time', 'guest_count', 'status']
    list_filter = ['status', 'restaurant', 'reservation_date']
    search_fields = ['customer_name', 'customer_phone', 'confirmation_code']
    date_hierarchy = 'reservation_date'


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ['user', 'restaurant', 'role', 'employee_id', 'is_active', 'is_on_duty']
    list_filter = ['restaurant', 'role', 'is_active', 'is_on_duty']
    search_fields = ['user__username', 'employee_id']