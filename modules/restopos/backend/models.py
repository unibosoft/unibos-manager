"""
RestoPOS Module Models
Secure and scalable models for restaurant POS system
"""

from django.db import models
from django.contrib.auth import get_user_model
# Use Django's built-in JSONField for database compatibility
# ArrayField functionality will be simulated using JSONField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.db.models import Q, Sum, Count, Avg, F
from decimal import Decimal
import uuid
from typing import Optional
from datetime import datetime, timedelta

User = get_user_model()


class Restaurant(models.Model):
    """Restaurant/Branch model"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Basic information
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    branch_code = models.CharField(max_length=20, unique=True)
    
    # Location
    address = models.TextField()
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    
    # Business details
    tax_number = models.CharField(max_length=50, blank=True)
    currency = models.CharField(max_length=3, default='USD')
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('18.00'))
    service_charge_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('10.00'))
    
    # Operating hours (JSON format: {"monday": {"open": "09:00", "close": "22:00"}, ...})
    operating_hours = models.JSONField(default=dict)
    
    # Settings
    auto_gratuity_enabled = models.BooleanField(default=False)
    auto_gratuity_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('15.00'))
    allow_split_bills = models.BooleanField(default=True)
    require_table_assignment = models.BooleanField(default=True)
    
    # Integration settings (for WIMM and WIMS modules)
    wimm_integration_enabled = models.BooleanField(default=True)
    wims_integration_enabled = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['branch_code']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.branch_code})"


class MenuCategory(models.Model):
    """Menu categories"""
    
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menu_categories')
    
    name = models.CharField(max_length=100)
    slug = models.SlugField()
    description = models.TextField(blank=True)
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    # Display settings
    icon = models.CharField(max_length=50, blank=True, help_text="Icon class or emoji")
    color_code = models.CharField(max_length=7, blank=True, help_text="Hex color code")
    
    class Meta:
        ordering = ['display_order', 'name']
        unique_together = [['restaurant', 'slug']]
        verbose_name_plural = 'menu categories'
    
    def __str__(self):
        return f"{self.name} - {self.restaurant.name}"


class MenuItem(models.Model):
    """Menu items"""
    
    ITEM_TYPE_CHOICES = [
        ('food', 'food'),
        ('beverage', 'beverage'),
        ('dessert', 'dessert'),
        ('addon', 'add-on'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menu_items')
    category = models.ForeignKey(MenuCategory, on_delete=models.CASCADE, related_name='items')
    
    # Basic information
    name = models.CharField(max_length=200)
    slug = models.SlugField()
    description = models.TextField(blank=True)
    item_type = models.CharField(max_length=20, choices=ITEM_TYPE_CHOICES, default='food')
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Cost to prepare")
    
    # Inventory tracking (integrated with WIMS)
    track_inventory = models.BooleanField(default=False)
    wims_product_id = models.CharField(max_length=100, blank=True, help_text="WIMS module product ID")
    
    # Dietary information
    is_vegetarian = models.BooleanField(default=False)
    is_vegan = models.BooleanField(default=False)
    is_gluten_free = models.BooleanField(default=False)
    is_halal = models.BooleanField(default=False)
    allergens = models.JSONField(
        models.CharField(max_length=50),
        default=list,
        blank=True
    )
    calories = models.IntegerField(null=True, blank=True)
    
    # Availability
    is_available = models.BooleanField(default=True)
    available_times = models.JSONField(default=dict, blank=True, help_text="Time-based availability")
    preparation_time_minutes = models.IntegerField(default=15)
    
    # Customization options
    customization_options = models.JSONField(default=list, blank=True)
    
    # Statistics
    times_ordered = models.IntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category', 'name']
        unique_together = [['restaurant', 'slug']]
        indexes = [
            models.Index(fields=['restaurant', 'is_available']),
            models.Index(fields=['category', 'is_available']),
        ]
    
    def __str__(self):
        return f"{self.name} - ${self.price}"
    
    @property
    def profit_margin(self) -> Optional[Decimal]:
        """Calculate profit margin percentage"""
        if self.cost:
            return ((self.price - self.cost) / self.price) * 100
        return None


class Table(models.Model):
    """Restaurant tables"""
    
    STATUS_CHOICES = [
        ('available', 'available'),
        ('occupied', 'occupied'),
        ('reserved', 'reserved'),
        ('cleaning', 'cleaning'),
        ('closed', 'closed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='tables')
    
    # Basic information
    table_number = models.CharField(max_length=20)
    section = models.CharField(max_length=50, blank=True, help_text="Restaurant section/area")
    capacity = models.IntegerField(validators=[MinValueValidator(1)])
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    current_order = models.ForeignKey('Order', on_delete=models.SET_NULL, null=True, blank=True, related_name='current_table')
    
    # QR code for digital menu
    qr_code = models.CharField(max_length=100, unique=True, blank=True)
    
    # Position for floor plan
    position_x = models.IntegerField(null=True, blank=True)
    position_y = models.IntegerField(null=True, blank=True)
    
    # Timestamps
    last_occupied = models.DateTimeField(null=True, blank=True)
    last_cleaned = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['section', 'table_number']
        unique_together = [['restaurant', 'table_number']]
    
    def __str__(self):
        return f"Table {self.table_number} ({self.status})"


class Order(models.Model):
    """Customer orders"""
    
    STATUS_CHOICES = [
        ('draft', 'draft'),
        ('pending', 'pending'),
        ('confirmed', 'confirmed'),
        ('preparing', 'preparing'),
        ('ready', 'ready'),
        ('served', 'served'),
        ('completed', 'completed'),
        ('cancelled', 'cancelled'),
    ]
    
    ORDER_TYPE_CHOICES = [
        ('dine_in', 'dine in'),
        ('takeout', 'takeout'),
        ('delivery', 'delivery'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='orders')
    
    # Order information
    order_number = models.CharField(max_length=20, unique=True)
    order_type = models.CharField(max_length=20, choices=ORDER_TYPE_CHOICES, default='dine_in')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Table assignment (for dine-in)
    table = models.ForeignKey(Table, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    
    # Customer information
    customer_name = models.CharField(max_length=100, blank=True)
    customer_phone = models.CharField(max_length=20, blank=True)
    customer_email = models.EmailField(blank=True)
    guest_count = models.IntegerField(default=1)
    
    # Staff assignment
    waiter = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='served_orders')
    chef = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='prepared_orders')
    
    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    service_charge = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    tip_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    # Special instructions
    notes = models.TextField(blank=True)
    kitchen_notes = models.TextField(blank=True)
    
    # Payment
    payment_method = models.CharField(max_length=50, blank=True)
    payment_status = models.CharField(max_length=20, default='pending')
    wimm_transaction_id = models.CharField(max_length=100, blank=True, help_text="WIMM module transaction ID")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['restaurant', '-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['table', 'status']),
        ]
    
    def __str__(self):
        return f"Order {self.order_number} - {self.status}"
    
    def calculate_totals(self):
        """Recalculate order totals"""
        self.subtotal = self.items.aggregate(
            total=Sum(F('quantity') * F('unit_price'))
        )['total'] or Decimal('0.00')
        
        self.tax_amount = (self.subtotal - self.discount_amount) * (self.restaurant.tax_rate / 100)
        self.service_charge = self.subtotal * (self.restaurant.service_charge_rate / 100)
        
        self.total_amount = (
            self.subtotal +
            self.tax_amount +
            self.service_charge -
            self.discount_amount +
            self.tip_amount
        )
        
        self.save()


class OrderItem(models.Model):
    """Items in an order"""
    
    STATUS_CHOICES = [
        ('pending', 'pending'),
        ('preparing', 'preparing'),
        ('ready', 'ready'),
        ('served', 'served'),
        ('cancelled', 'cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='order_items')
    
    # Quantity and pricing
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Customizations
    customizations = models.JSONField(default=dict, blank=True)
    special_instructions = models.TextField(blank=True)
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    prepared_at = models.DateTimeField(null=True, blank=True)
    served_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.quantity}x {self.menu_item.name}"
    
    def save(self, *args, **kwargs):
        """Calculate total price before saving"""
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)


class Receipt(models.Model):
    """Order receipts"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='receipt')
    
    # Receipt information
    receipt_number = models.CharField(max_length=50, unique=True)
    
    # Payment details
    payment_method = models.CharField(max_length=50)
    payment_reference = models.CharField(max_length=100, blank=True)
    
    # Amounts
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2)
    service_charge = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    tip_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Change (for cash payments)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    change_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Digital receipt
    email_sent = models.BooleanField(default=False)
    email_sent_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    issued_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-issued_at']
        indexes = [
            models.Index(fields=['-issued_at']),
        ]
    
    def __str__(self):
        return f"Receipt {self.receipt_number}"


class Reservation(models.Model):
    """Table reservations"""
    
    STATUS_CHOICES = [
        ('pending', 'pending'),
        ('confirmed', 'confirmed'),
        ('seated', 'seated'),
        ('completed', 'completed'),
        ('cancelled', 'cancelled'),
        ('no_show', 'no show'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='reservations')
    table = models.ForeignKey(Table, on_delete=models.SET_NULL, null=True, blank=True, related_name='reservations')
    
    # Customer information
    customer_name = models.CharField(max_length=100)
    customer_phone = models.CharField(max_length=20)
    customer_email = models.EmailField(blank=True)
    guest_count = models.IntegerField(validators=[MinValueValidator(1)])
    
    # Reservation details
    reservation_date = models.DateField()
    reservation_time = models.TimeField()
    duration_minutes = models.IntegerField(default=120)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Special requests
    special_requests = models.TextField(blank=True)
    
    # Confirmation
    confirmation_code = models.CharField(max_length=20, unique=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['reservation_date', 'reservation_time']
        indexes = [
            models.Index(fields=['restaurant', 'reservation_date', 'status']),
            models.Index(fields=['table', 'reservation_date']),
        ]
    
    def __str__(self):
        return f"{self.customer_name} - {self.reservation_date} {self.reservation_time}"


class Staff(models.Model):
    """Restaurant staff members"""
    
    ROLE_CHOICES = [
        ('manager', 'manager'),
        ('waiter', 'waiter'),
        ('chef', 'chef'),
        ('cashier', 'cashier'),
        ('host', 'host'),
        ('bartender', 'bartender'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='staff')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='restaurant_staff')
    
    # Staff information
    employee_id = models.CharField(max_length=50, unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    
    # Permissions
    can_manage_orders = models.BooleanField(default=False)
    can_manage_tables = models.BooleanField(default=False)
    can_manage_menu = models.BooleanField(default=False)
    can_process_payments = models.BooleanField(default=False)
    can_view_reports = models.BooleanField(default=False)
    
    # Work schedule
    shift_schedule = models.JSONField(default=dict, blank=True)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_on_duty = models.BooleanField(default=False)
    
    # Timestamps
    hired_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['restaurant', 'role', 'user__first_name']
        unique_together = [['restaurant', 'user']]
        verbose_name_plural = 'staff'
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.role} at {self.restaurant.name}"