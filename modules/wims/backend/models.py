"""
WIMS (Where Is My Stuff) - Inventory Management Module
Handles stock tracking, warehouse management, and item movements
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
from modules.core.backend.models import BaseModel, Item, ItemPrice
from modules.wimm.backend.models import Invoice, InvoiceItem


class Warehouse(BaseModel):
    """Physical or logical storage locations"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='warehouses')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    
    # Location details
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=2, default='TR')  # ISO country code
    
    # Type
    warehouse_type = models.CharField(max_length=20, choices=[
        ('physical', 'Physical Warehouse'),
        ('virtual', 'Virtual Location'),
        ('store', 'Retail Store'),
        ('transit', 'In Transit'),
        ('customer', 'Customer Location'),
        ('supplier', 'Supplier Location'),
    ], default='physical')
    
    # Contact
    manager = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    
    # Settings
    allow_negative_stock = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['name']
        unique_together = [['user', 'code']]
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class StockLocation(BaseModel):
    """Specific locations within a warehouse (shelf, bin, etc.)"""
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='locations')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50)  # A-01-02 (Aisle-Rack-Shelf)
    
    # Hierarchy
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='sublocations')
    
    # Capacity
    max_weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # kg
    max_volume = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # m³
    
    # Type
    location_type = models.CharField(max_length=20, choices=[
        ('rack', 'Rack'),
        ('shelf', 'Shelf'),
        ('bin', 'Bin'),
        ('floor', 'Floor'),
        ('refrigerated', 'Refrigerated'),
        ('frozen', 'Frozen'),
        ('hazmat', 'Hazardous Materials'),
    ], default='shelf')
    
    class Meta:
        ordering = ['warehouse', 'code']
        unique_together = [['warehouse', 'code']]
    
    def __str__(self):
        return f"{self.warehouse.code}/{self.code}"


class StockItem(BaseModel):
    """Current stock levels for items in warehouses"""
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='stock_items')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='stock_items')
    location = models.ForeignKey(StockLocation, on_delete=models.SET_NULL, null=True, blank=True, related_name='stock_items')
    
    # Quantities
    quantity = models.DecimalField(max_digits=20, decimal_places=4, default=0)
    reserved_quantity = models.DecimalField(max_digits=20, decimal_places=4, default=0)  # Reserved for orders
    
    # Batch/Lot tracking
    batch_number = models.CharField(max_length=50, blank=True)
    serial_number = models.CharField(max_length=100, blank=True)
    
    # Dates
    manufacture_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    
    # Cost tracking
    unit_cost = models.DecimalField(max_digits=20, decimal_places=4, default=0)
    currency = models.CharField(max_length=3, default='TRY')
    
    # Reorder levels
    min_stock_level = models.DecimalField(max_digits=20, decimal_places=4, default=0)
    max_stock_level = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True)
    reorder_point = models.DecimalField(max_digits=20, decimal_places=4, default=0)
    reorder_quantity = models.DecimalField(max_digits=20, decimal_places=4, default=0)
    
    class Meta:
        ordering = ['item__name', 'warehouse__name']
        indexes = [
            models.Index(fields=['item', 'warehouse']),
            models.Index(fields=['expiry_date']),
        ]
        unique_together = [['item', 'warehouse', 'batch_number', 'serial_number']]
    
    def __str__(self):
        return f"{self.item.name} @ {self.warehouse.name}: {self.quantity}"
    
    @property
    def available_quantity(self):
        """Quantity available for use (not reserved)"""
        return self.quantity - self.reserved_quantity
    
    @property
    def total_value(self):
        """Total value of stock"""
        return self.quantity * self.unit_cost
    
    @property
    def is_expired(self):
        """Check if item is expired"""
        if self.expiry_date:
            return self.expiry_date < timezone.now().date()
        return False
    
    @property
    def days_until_expiry(self):
        """Days until expiry"""
        if self.expiry_date:
            delta = self.expiry_date - timezone.now().date()
            return delta.days
        return None
    
    @property
    def needs_reorder(self):
        """Check if reorder is needed"""
        return self.available_quantity <= self.reorder_point


class StockMovement(BaseModel):
    """Track all inventory movements"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='stock_movements')
    
    # Movement type
    movement_type = models.CharField(max_length=20, choices=[
        ('receipt', 'Receipt'),  # Incoming from supplier
        ('issue', 'Issue'),  # Outgoing to customer
        ('transfer', 'Transfer'),  # Between warehouses
        ('adjustment', 'Adjustment'),  # Inventory count adjustment
        ('production', 'Production'),  # Manufacturing output
        ('consumption', 'Consumption'),  # Manufacturing input
        ('return', 'Return'),  # Customer/supplier return
        ('damage', 'Damage'),  # Damaged goods
        ('expired', 'Expired'),  # Expired items
    ])
    
    # Item and quantity
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='movements')
    quantity = models.DecimalField(max_digits=20, decimal_places=4)
    unit_cost = models.DecimalField(max_digits=20, decimal_places=4, default=0)
    currency = models.CharField(max_length=3, default='TRY')
    
    # Locations
    from_warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='outgoing_movements', null=True, blank=True)
    from_location = models.ForeignKey(StockLocation, on_delete=models.SET_NULL, null=True, blank=True, related_name='outgoing_movements')
    to_warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='incoming_movements', null=True, blank=True)
    to_location = models.ForeignKey(StockLocation, on_delete=models.SET_NULL, null=True, blank=True, related_name='incoming_movements')
    
    # Batch tracking
    batch_number = models.CharField(max_length=50, blank=True)
    serial_number = models.CharField(max_length=100, blank=True)
    
    # References to other modules
    invoice = models.ForeignKey(Invoice, on_delete=models.SET_NULL, null=True, blank=True, related_name='stock_movements')
    invoice_item = models.ForeignKey(InvoiceItem, on_delete=models.SET_NULL, null=True, blank=True, related_name='stock_movements')
    
    # Document reference
    reference_number = models.CharField(max_length=50, blank=True)
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Movement date
    movement_date = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-movement_date']
        indexes = [
            models.Index(fields=['item', '-movement_date']),
            models.Index(fields=['movement_type', '-movement_date']),
        ]
    
    def __str__(self):
        return f"{self.movement_date.strftime('%Y-%m-%d')} - {self.get_movement_type_display()}: {self.item.name} x {self.quantity}"
    
    def save(self, *args, **kwargs):
        """Update stock levels on save"""
        if not self.pk:  # New movement
            # Update source warehouse
            if self.from_warehouse and self.movement_type in ['issue', 'transfer', 'consumption', 'damage', 'expired']:
                stock, created = StockItem.objects.get_or_create(
                    item=self.item,
                    warehouse=self.from_warehouse,
                    batch_number=self.batch_number or '',
                    serial_number=self.serial_number or '',
                    defaults={'location': self.from_location}
                )
                stock.quantity -= self.quantity
                stock.save()
            
            # Update destination warehouse
            if self.to_warehouse and self.movement_type in ['receipt', 'transfer', 'production', 'return', 'adjustment']:
                stock, created = StockItem.objects.get_or_create(
                    item=self.item,
                    warehouse=self.to_warehouse,
                    batch_number=self.batch_number or '',
                    serial_number=self.serial_number or '',
                    defaults={
                        'location': self.to_location,
                        'unit_cost': self.unit_cost,
                        'currency': self.currency
                    }
                )
                stock.quantity += self.quantity
                # Update cost using weighted average
                if stock.quantity > 0:
                    total_value = (stock.quantity * stock.unit_cost) + (self.quantity * self.unit_cost)
                    stock.unit_cost = total_value / (stock.quantity + self.quantity)
                stock.save()
        
        super().save(*args, **kwargs)


class StockCount(BaseModel):
    """Physical inventory counts"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='stock_counts')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='stock_counts')
    
    # Count details
    count_date = models.DateTimeField(default=timezone.now)
    count_type = models.CharField(max_length=20, choices=[
        ('full', 'Full Count'),
        ('cycle', 'Cycle Count'),
        ('spot', 'Spot Check'),
    ])
    
    # Status
    status = models.CharField(max_length=20, choices=[
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('approved', 'Approved'),
        ('cancelled', 'Cancelled'),
    ], default='planned')
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Approval
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_counts')
    approved_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-count_date']
    
    def __str__(self):
        return f"{self.warehouse.name} - {self.count_date.strftime('%Y-%m-%d')}"


class StockCountItem(BaseModel):
    """Items in a stock count"""
    stock_count = models.ForeignKey(StockCount, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    location = models.ForeignKey(StockLocation, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Quantities
    system_quantity = models.DecimalField(max_digits=20, decimal_places=4)  # What system shows
    counted_quantity = models.DecimalField(max_digits=20, decimal_places=4)  # What was counted
    
    # Batch info
    batch_number = models.CharField(max_length=50, blank=True)
    serial_number = models.CharField(max_length=100, blank=True)
    
    # Notes
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['item__name']
        unique_together = [['stock_count', 'item', 'location', 'batch_number', 'serial_number']]
    
    def __str__(self):
        return f"{self.item.name}: {self.system_quantity} → {self.counted_quantity}"
    
    @property
    def variance(self):
        """Difference between counted and system quantity"""
        return self.counted_quantity - self.system_quantity
    
    @property
    def variance_percentage(self):
        """Variance as percentage"""
        if self.system_quantity == 0:
            return 100 if self.counted_quantity > 0 else 0
        return ((self.variance / self.system_quantity) * 100)


class ItemSupplier(BaseModel):
    """Link items to suppliers with pricing"""
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='suppliers')
    supplier_name = models.CharField(max_length=200)
    supplier_code = models.CharField(max_length=50, blank=True)
    
    # Supplier's item code
    supplier_item_code = models.CharField(max_length=50, blank=True)
    supplier_item_name = models.CharField(max_length=200, blank=True)
    
    # Pricing
    unit_price = models.DecimalField(max_digits=20, decimal_places=4)
    currency = models.CharField(max_length=3, default='TRY')
    
    # Lead times
    lead_time_days = models.IntegerField(default=0)  # Days to deliver
    
    # Minimum order
    min_order_quantity = models.DecimalField(max_digits=20, decimal_places=4, default=1)
    order_multiple = models.DecimalField(max_digits=20, decimal_places=4, default=1)  # Must order in multiples
    
    # Priority
    is_preferred = models.BooleanField(default=False)
    priority = models.IntegerField(default=0)  # Lower number = higher priority
    
    class Meta:
        ordering = ['item', 'priority', 'supplier_name']
        unique_together = [['item', 'supplier_name']]
    
    def __str__(self):
        return f"{self.item.name} from {self.supplier_name}"