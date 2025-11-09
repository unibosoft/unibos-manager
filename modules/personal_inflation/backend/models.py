"""
Personal Inflation models for UNIBOS
Tracks individual inflation rates based on personal consumption
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
import uuid
import json

# Check if using PostgreSQL
from django.conf import settings
try:
    from django.contrib.postgres.fields import ArrayField
    from django.contrib.postgres.indexes import GinIndex
    HAS_POSTGRES = 'postgresql' in settings.DATABASES.get('default', {}).get('ENGINE', '')
except ImportError:
    HAS_POSTGRES = False
    ArrayField = None
    GinIndex = None

User = get_user_model()


class ProductCategory(models.Model):
    """Product categories for inflation tracking"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcategories'
    )
    
    # Category metadata
    icon = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=7, blank=True)  # Hex color
    order = models.PositiveIntegerField(default=0)
    
    # Official inflation weight (TUIK)
    official_weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Official weight in CPI basket (%)"
    )
    
    # Tracking
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'product_categories'
        verbose_name_plural = 'Product Categories'
        ordering = ['order', 'name']
        indexes = [
            models.Index(fields=['parent', 'is_active']),
        ]
    
    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name


class Product(models.Model):
    """Products tracked for personal inflation"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.CASCADE,
        related_name='products'
    )
    
    # Product details
    barcode = models.CharField(max_length=50, blank=True, db_index=True)
    brand = models.CharField(max_length=100, blank=True)
    unit = models.CharField(max_length=20)  # kg, litre, adet, etc.
    
    # Metadata
    description = models.TextField(blank=True)
    image_url = models.URLField(blank=True)
    
    # Tracking
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Search optimization - use JSONField for SQLite compatibility
    search_vector = models.JSONField(
        blank=True,
        default=list,
        help_text="Search keywords for this product"
    ) if not HAS_POSTGRES else ArrayField(
        models.CharField(max_length=200),
        blank=True,
        default=list
    )
    
    class Meta:
        db_table = 'products'
        ordering = ['name']
        indexes = [
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['barcode']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.unit})"


class Store(models.Model):
    """Stores where products are purchased"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    
    # Store details
    store_type = models.CharField(
        max_length=50,
        choices=[
            ('supermarket', 'Supermarket'),
            ('market', 'Local Market'),
            ('bazaar', 'Bazaar'),
            ('online', 'Online Store'),
            ('other', 'Other'),
        ]
    )
    
    # Location
    address = models.TextField(blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    
    # Metadata
    website = models.URLField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'stores'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class PersonalBasket(models.Model):
    """User's personal consumption basket"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='baskets')
    name = models.CharField(max_length=100, default='Ana Sepet')
    
    # Basket settings
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    
    # Period settings
    calculation_period = models.CharField(
        max_length=20,
        choices=[
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
            ('quarterly', 'Quarterly'),
            ('yearly', 'Yearly'),
        ],
        default='monthly'
    )
    
    # Metadata
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'personal_baskets'
        unique_together = ['user', 'name']
        indexes = [
            models.Index(fields=['user', 'is_active', 'is_default']),
        ]
    
    def __str__(self):
        return f"{self.user.username}'s {self.name}"
    
    def calculate_inflation(self, start_date=None, end_date=None):
        """Calculate inflation rate for this basket"""
        if not start_date:
            start_date = timezone.now() - timezone.timedelta(days=30)
        if not end_date:
            end_date = timezone.now()
        
        total_start = Decimal('0')
        total_end = Decimal('0')
        
        for item in self.items.filter(is_active=True):
            # Get prices for start and end dates
            start_price = item.get_price_at_date(start_date)
            end_price = item.get_price_at_date(end_date)
            
            if start_price and end_price:
                total_start += start_price * item.quantity
                total_end += end_price * item.quantity
        
        if total_start > 0:
            inflation_rate = ((total_end - total_start) / total_start) * 100
            return round(inflation_rate, 2)
        return Decimal('0')


class BasketItem(models.Model):
    """Items in a personal basket"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    basket = models.ForeignKey(PersonalBasket, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    
    # Consumption details
    quantity = models.DecimalField(max_digits=10, decimal_places=3)
    frequency = models.CharField(
        max_length=20,
        choices=[
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
            ('quarterly', 'Quarterly'),
        ],
        default='monthly'
    )
    
    # Custom weight (override automatic calculation)
    custom_weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Custom weight in basket (%)"
    )
    
    # Tracking
    is_active = models.BooleanField(default=True)
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'basket_items'
        unique_together = ['basket', 'product']
        indexes = [
            models.Index(fields=['basket', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.quantity} {self.product.unit} {self.product.name}"
    
    def get_price_at_date(self, date):
        """Get product price at specific date"""
        try:
            price_record = PriceRecord.objects.filter(
                product=self.product,
                recorded_at__date__lte=date
            ).order_by('-recorded_at').first()
            return price_record.price if price_record else None
        except PriceRecord.DoesNotExist:
            return None


class PriceRecord(models.Model):
    """Price records for products"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='price_records')
    store = models.ForeignKey(Store, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Price information
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='TRY')
    
    # Discount information
    is_discounted = models.BooleanField(default=False)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Source
    source = models.CharField(
        max_length=20,
        choices=[
            ('user', 'User Input'),
            ('crowdsource', 'Crowdsourced'),
            ('official', 'Official Data'),
            ('scraper', 'Web Scraper'),
        ],
        default='user'
    )
    
    # Verification
    is_verified = models.BooleanField(default=False)
    verification_count = models.PositiveIntegerField(default=0)
    
    # Metadata
    notes = models.TextField(blank=True)
    receipt_image = models.FileField(upload_to='receipts/', blank=True, null=True)
    
    # Timestamps
    recorded_at = models.DateTimeField(default=timezone.now, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'price_records'
        ordering = ['-recorded_at']
        indexes = [
            models.Index(fields=['product', 'recorded_at']),
            models.Index(fields=['store', 'recorded_at']),
            models.Index(fields=['recorded_at']),
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.product.name} - {self.price} {self.currency} @ {self.recorded_at}"


class InflationReport(models.Model):
    """Generated inflation reports for users"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inflation_reports')
    basket = models.ForeignKey(PersonalBasket, on_delete=models.CASCADE)
    
    # Report period
    period_start = models.DateField()
    period_end = models.DateField()
    report_type = models.CharField(
        max_length=20,
        choices=[
            ('monthly', 'Monthly'),
            ('quarterly', 'Quarterly'),
            ('yearly', 'Yearly'),
            ('custom', 'Custom Period'),
        ]
    )
    
    # Calculated values
    inflation_rate = models.DecimalField(max_digits=10, decimal_places=4)
    total_start_cost = models.DecimalField(max_digits=12, decimal_places=2)
    total_end_cost = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Category breakdown
    category_breakdown = models.JSONField(default=dict)
    
    # Comparison with official rates
    official_inflation_rate = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True
    )
    
    # Report data
    detailed_data = models.JSONField(default=dict)
    
    # Metadata
    generated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'inflation_reports'
        ordering = ['-period_end', '-generated_at']
        indexes = [
            models.Index(fields=['user', 'period_end']),
            models.Index(fields=['basket', 'period_end']),
        ]
        unique_together = ['user', 'basket', 'period_start', 'period_end']
    
    def __str__(self):
        return f"{self.user.username}'s {self.report_type} report: {self.inflation_rate}%"


class PriceAlert(models.Model):
    """Price alerts for specific products"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='price_alerts')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    
    # Alert configuration
    alert_type = models.CharField(
        max_length=20,
        choices=[
            ('price_drop', 'Price Drop'),
            ('price_increase', 'Price Increase'),
            ('threshold', 'Price Threshold'),
        ]
    )
    threshold_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    percentage_change = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Alert status
    is_active = models.BooleanField(default=True)
    last_triggered = models.DateTimeField(null=True, blank=True)
    trigger_count = models.PositiveIntegerField(default=0)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'price_alerts'
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['product', 'is_active']),
        ]
    
    def __str__(self):
        return f"Alert: {self.product.name} - {self.alert_type}"