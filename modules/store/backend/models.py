from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import json

User = get_user_model()


class Marketplace(models.Model):
    """E-commerce marketplace platforms"""
    PLATFORM_CHOICES = [
        ('amazon', 'Amazon'),
        ('etsy', 'Etsy'),
        ('hepsiburada', 'Hepsiburada'),
        ('trendyol', 'Trendyol'),
        ('n11', 'N11'),
        ('woocommerce', 'WooCommerce'),
        ('shopify', 'Shopify'),
        ('sentos', 'Sentos (All Platforms)'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('pending', 'Pending Setup'),
        ('error', 'Connection Error'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='marketplaces')
    platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES)
    shop_name = models.CharField(max_length=200)
    api_key = models.CharField(max_length=500, blank=True)
    api_secret = models.CharField(max_length=500, blank=True)
    
    # Sentos specific fields
    sentos_api_key = models.CharField(max_length=500, blank=True)
    sentos_shop_url = models.URLField(blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_primary = models.BooleanField(default=False)
    
    # Statistics
    total_orders = models.IntegerField(default=0)
    total_products = models.IntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Sync information
    last_sync = models.DateTimeField(null=True, blank=True)
    sync_interval_minutes = models.IntegerField(default=30)
    auto_sync = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_primary', 'platform', 'shop_name']
        unique_together = ['user', 'platform', 'shop_name']
    
    def __str__(self):
        return f"{self.shop_name} ({self.get_platform_display()})"
    
    def needs_sync(self):
        if not self.last_sync:
            return True
        time_diff = timezone.now() - self.last_sync
        return time_diff.total_seconds() > (self.sync_interval_minutes * 60)


class Order(models.Model):
    """Orders from marketplaces"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('preparing', 'Preparing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
        ('returned', 'Returned'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('partially_paid', 'Partially Paid'),
        ('refunded', 'Refunded'),
        ('failed', 'Failed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='store_orders')
    marketplace = models.ForeignKey(Marketplace, on_delete=models.CASCADE, related_name='orders')
    
    # Order identification
    platform_order_id = models.CharField(max_length=200, unique=True)
    order_number = models.CharField(max_length=100)
    
    # Customer information
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField(blank=True)
    customer_phone = models.CharField(max_length=50, blank=True)
    
    # Shipping address
    shipping_address = models.TextField()
    shipping_city = models.CharField(max_length=100)
    shipping_state = models.CharField(max_length=100, blank=True)
    shipping_country = models.CharField(max_length=100)
    shipping_postal_code = models.CharField(max_length=20)
    
    # Order details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=100, blank=True)
    
    # Financial
    currency = models.CharField(max_length=3, default='TRY')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Tracking
    tracking_number = models.CharField(max_length=200, blank=True)
    tracking_company = models.CharField(max_length=100, blank=True)
    
    # Notes
    customer_note = models.TextField(blank=True)
    internal_note = models.TextField(blank=True)
    
    # Timestamps
    order_date = models.DateTimeField()
    shipped_date = models.DateTimeField(null=True, blank=True)
    delivered_date = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    platform_data = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-order_date']
        indexes = [
            models.Index(fields=['-order_date']),
            models.Index(fields=['status']),
            models.Index(fields=['marketplace', 'status']),
        ]
    
    def __str__(self):
        return f"Order #{self.order_number} - {self.customer_name}"
    
    @property
    def is_paid(self):
        return self.payment_status == 'paid'
    
    @property
    def can_cancel(self):
        return self.status in ['pending', 'processing']
    
    @property
    def can_refund(self):
        return self.status in ['delivered', 'shipped'] and self.payment_status == 'paid'


class OrderItem(models.Model):
    """Items in an order"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    
    # Product information
    product_id = models.CharField(max_length=200)
    product_name = models.CharField(max_length=500)
    product_sku = models.CharField(max_length=100, blank=True)
    product_barcode = models.CharField(max_length=100, blank=True)
    
    # Variant information
    variant_id = models.CharField(max_length=200, blank=True)
    variant_title = models.CharField(max_length=200, blank=True)
    
    # Quantity and pricing
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Additional data
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['id']
    
    def __str__(self):
        return f"{self.product_name} x{self.quantity}"


class Product(models.Model):
    """Products synced from marketplaces"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('out_of_stock', 'Out of Stock'),
        ('discontinued', 'Discontinued'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='store_products')
    marketplace = models.ForeignKey(Marketplace, on_delete=models.CASCADE, related_name='products')
    
    # Product identification
    platform_product_id = models.CharField(max_length=200)
    sku = models.CharField(max_length=100, db_index=True)
    barcode = models.CharField(max_length=100, blank=True, db_index=True)
    
    # Product information
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    brand = models.CharField(max_length=200, blank=True)
    category = models.CharField(max_length=200, blank=True)
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default='TRY')
    
    # Stock
    stock_quantity = models.IntegerField(default=0)
    low_stock_threshold = models.IntegerField(default=5)
    
    # Images
    main_image_url = models.URLField(blank=True)
    additional_images = models.JSONField(default=list, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Statistics
    total_sales = models.IntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Metadata
    platform_data = models.JSONField(default=dict, blank=True)
    
    # Sync
    last_sync = models.DateTimeField(auto_now=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['title']
        unique_together = ['marketplace', 'platform_product_id']
        indexes = [
            models.Index(fields=['sku']),
            models.Index(fields=['barcode']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return self.title
    
    @property
    def is_low_stock(self):
        return self.stock_quantity <= self.low_stock_threshold
    
    @property
    def is_on_sale(self):
        return self.sale_price and self.sale_price < self.price
    
    @property
    def effective_price(self):
        return self.sale_price if self.is_on_sale else self.price


class SyncLog(models.Model):
    """Log of marketplace synchronizations"""
    STATUS_CHOICES = [
        ('running', 'Running'),
        ('success', 'Success'),
        ('partial', 'Partial Success'),
        ('failed', 'Failed'),
    ]
    
    marketplace = models.ForeignKey(Marketplace, on_delete=models.CASCADE, related_name='sync_logs')
    
    sync_type = models.CharField(max_length=50)  # orders, products, inventory, etc.
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    
    # Statistics
    items_processed = models.IntegerField(default=0)
    items_created = models.IntegerField(default=0)
    items_updated = models.IntegerField(default=0)
    items_failed = models.IntegerField(default=0)
    
    # Timing
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.IntegerField(null=True, blank=True)
    
    # Error handling
    error_message = models.TextField(blank=True)
    error_details = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.marketplace.shop_name} - {self.sync_type} - {self.status}"