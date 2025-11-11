"""
Core shared models for all UNIBOS modules
This ensures no data duplication across modules
"""
from django.db import models
from django.conf import settings
from decimal import Decimal


class BaseModel(models.Model):
    """Base model with common fields"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        abstract = True


class ItemCategory(BaseModel):
    """Global category for all items/products"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='children')
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)  # Emoji or icon class
    
    class Meta:
        app_label = 'modules_core'
        verbose_name_plural = "Item Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Unit(BaseModel):
    """Units of measurement"""
    name = models.CharField(max_length=50)  # kilogram, litre, piece, etc.
    symbol = models.CharField(max_length=10)  # kg, L, pcs, etc.
    category = models.CharField(max_length=50, choices=[
        ('weight', 'Weight'),
        ('volume', 'Volume'),
        ('count', 'Count'),
        ('length', 'Length'),
        ('area', 'Area'),
        ('time', 'Time'),
        ('digital', 'Digital'),
        ('other', 'Other'),
    ])
    
    class Meta:
        app_label = 'modules_core'
    
    def __str__(self):
        return f"{self.name} ({self.symbol})"


class Item(BaseModel):
    """
    Master Item/Product table - shared across all modules
    Used in: recaria, kişisel enflasyon, wimm, future inventory module
    """
    # Basic info
    name = models.CharField(max_length=200, db_index=True)
    code = models.CharField(max_length=50, unique=True, db_index=True)  # SKU/barcode
    category = models.ForeignKey(ItemCategory, on_delete=models.SET_NULL, null=True, related_name='items')
    
    # Description
    description = models.TextField(blank=True)
    brand = models.CharField(max_length=100, blank=True)
    
    # Units
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True)
    
    # Attributes (flexible JSON for module-specific data)
    attributes = models.JSONField(default=dict, blank=True)
    # Example: {"color": "red", "size": "L", "expiry_days": 30, "is_perishable": true}
    
    # Module flags
    is_tradeable = models.BooleanField(default=True)  # Can be bought/sold
    is_service = models.BooleanField(default=False)  # Service vs physical product
    is_digital = models.BooleanField(default=False)  # Digital product
    
    # Search
    tags = models.JSONField(default=list, blank=True)  # ["food", "organic", "fruit"]
    
    class Meta:
        app_label = 'modules_core'
        ordering = ['name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['name']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class ItemPrice(BaseModel):
    """
    Price history for items across different sources
    Used by multiple modules to track price changes
    """
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='prices')
    source = models.CharField(max_length=100)  # "migros", "carrefour", "btcturk", etc.
    price = models.DecimalField(max_digits=20, decimal_places=4)
    currency = models.CharField(max_length=3, default='TRY')
    
    # Optional location/branch info
    location = models.CharField(max_length=200, blank=True)
    
    # Validity
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    # Example: {"discount": 10, "campaign": "summer_sale", "min_quantity": 1}
    
    class Meta:
        app_label = 'modules_core'
        ordering = ['-valid_from']
        indexes = [
            models.Index(fields=['item', 'source', '-valid_from']),
        ]
    
    def __str__(self):
        return f"{self.item.name} @ {self.source}: {self.price} {self.currency}"


class Account(BaseModel):
    """
    Financial accounts - shared across financial modules
    Used by: wimm, currencies (for wallets), future banking module
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='accounts')
    name = models.CharField(max_length=100)
    account_type = models.CharField(max_length=50, choices=[
        ('cash', 'Cash'),
        ('bank', 'Bank Account'),
        ('credit_card', 'Credit Card'),
        ('crypto', 'Crypto Wallet'),
        ('investment', 'Investment Account'),
        ('loan', 'Loan'),
        ('other', 'Other'),
    ])
    
    currency = models.CharField(max_length=3, default='TRY')
    balance = models.DecimalField(max_digits=20, decimal_places=4, default=0)
    
    # Bank/institution details
    institution = models.CharField(max_length=100, blank=True)
    account_number = models.CharField(max_length=50, blank=True)
    iban = models.CharField(max_length=34, blank=True)
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    # Example: {"interest_rate": 2.5, "credit_limit": 10000, "wallet_address": "0x..."}
    
    class Meta:
        app_label = 'modules_core'
        ordering = ['name']
        unique_together = [['user', 'name']]
    
    def __str__(self):
        return f"{self.name} ({self.get_account_type_display()})"


class UserProfile(BaseModel):
    """
    Extended user profile for UNIBOS users
    Imported from Unicorn backup
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='core_profile')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    mail_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    preferred_language = models.CharField(max_length=5, default='tr', choices=[
        ('tr', 'Türkçe'),
        ('en', 'English'),
    ])
    
    # Additional profile fields
    avatar = models.URLField(blank=True, null=True)
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    company = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True, null=True)
    
    # Settings
    theme = models.CharField(max_length=20, default='dark', choices=[
        ('dark', 'Dark'),
        ('light', 'Light'),
        ('auto', 'Auto'),
    ])
    notifications_enabled = models.BooleanField(default=True)
    
    class Meta:
        app_label = 'modules_core'
        ordering = ['user__username']
    
    def __str__(self):
        return f"{self.user.username}'s profile"