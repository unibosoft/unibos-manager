"""
Documents Module - OCR and Document Management System
Handles receipts, invoices, and all document processing
"""

from django.db import models
from django.conf import settings
from django.core.files.storage import default_storage
from django.utils import timezone
from decimal import Decimal
import json
import uuid
import os


class DocumentType(models.TextChoices):
    UNKNOWN = 'unknown', 'Unknown (Auto-detect)'
    RECEIPT = 'receipt', 'Receipt/Fiş'
    INVOICE = 'invoice', 'Invoice/Fatura'
    BANK_STATEMENT = 'bank_statement', 'Bank Statement'
    CREDIT_CARD_STATEMENT = 'cc_statement', 'Credit Card Statement'
    CONTRACT = 'contract', 'Contract/Sözleşme'
    OTHER = 'other', 'Other'


class ProcessingStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    PROCESSING = 'processing', 'Processing'
    COMPLETED = 'completed', 'Completed'
    FAILED = 'failed', 'Failed'
    MANUAL_REVIEW = 'manual_review', 'Manual Review Needed'


class Document(models.Model):
    """Main document model for storing uploaded files"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='documents')
    
    # Document metadata
    document_type = models.CharField(max_length=20, choices=DocumentType.choices, default=DocumentType.RECEIPT)
    original_filename = models.CharField(max_length=255)
    file_path = models.FileField(upload_to='documents/%Y/%m/')
    thumbnail_path = models.FileField(upload_to='documents/thumbnails/%Y/%m/', null=True, blank=True)
    
    # Processing status
    processing_status = models.CharField(max_length=20, choices=ProcessingStatus.choices, default=ProcessingStatus.PROCESSING)
    ocr_text = models.TextField(blank=True, null=True)
    ocr_confidence = models.FloatField(null=True, blank=True)
    ocr_processed_at = models.DateTimeField(null=True, blank=True)

    # Dual OCR storage - Tesseract and Ollama results
    tesseract_text = models.TextField(blank=True, null=True)
    tesseract_confidence = models.FloatField(null=True, blank=True)
    tesseract_parsed_data = models.JSONField(null=True, blank=True)

    ollama_text = models.TextField(blank=True, null=True)
    ollama_confidence = models.FloatField(null=True, blank=True)
    ollama_parsed_data = models.JSONField(null=True, blank=True)
    ollama_model = models.CharField(max_length=50, blank=True, default='')  # gemma3, llama2, etc.

    # User's preferred OCR method for this document
    preferred_ocr_method = models.CharField(max_length=20, blank=True, default='')  # 'tesseract', 'ollama', or empty for not selected

    # AI Enhancement fields
    ai_processed = models.BooleanField(default=False)
    ai_parsed_data = models.JSONField(null=True, blank=True)
    ai_provider = models.CharField(max_length=50, blank=True, default='')  # mistral, huggingface, local
    ai_confidence = models.FloatField(null=True, blank=True)
    ai_processed_at = models.DateTimeField(null=True, blank=True)

    # OCR Analysis Comparison Results (stores results from all OCR methods)
    analysis_results = models.JSONField(null=True, blank=True, help_text='Stores comparison results from all OCR methods (tesseract, paddleocr, llama_vision, trocr, donut, layoutlmv3, surya, doctr, easyocr, ocrmypdf, hybrid)')
    last_analysis_at = models.DateTimeField(null=True, blank=True, help_text='Timestamp of the last OCR analysis comparison')

    # Timestamps
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Tags and categorization
    tags = models.JSONField(default=list, blank=True)
    custom_metadata = models.JSONField(default=dict, blank=True)
    
    # Soft delete fields for recycle bin
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='deleted_documents')
    
    class Meta:
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['user', '-uploaded_at']),
            models.Index(fields=['document_type', 'processing_status']),
        ]
    
    def __str__(self):
        return f"{self.document_type} - {self.original_filename} ({self.user.username})"


class ParsedReceipt(models.Model):
    """Parsed receipt data from OCR processing"""
    document = models.OneToOneField(Document, on_delete=models.CASCADE, related_name='parsed_receipt')
    
    # Store information
    store_name = models.CharField(max_length=255, blank=True)
    store_address = models.TextField(blank=True)
    store_phone = models.CharField(max_length=50, blank=True)
    store_tax_id = models.CharField(max_length=50, blank=True)
    
    # Transaction details
    transaction_date = models.DateTimeField(null=True, blank=True)
    receipt_number = models.CharField(max_length=100, blank=True)
    cashier_id = models.CharField(max_length=50, blank=True)
    
    # Financial data
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Payment information
    payment_method = models.CharField(max_length=50, blank=True)
    card_last_digits = models.CharField(max_length=4, blank=True)
    
    # Currency
    currency = models.CharField(max_length=3, default='TRY')
    
    # Raw data
    raw_ocr_data = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-transaction_date']
    
    def __str__(self):
        return f"{self.store_name} - {self.total_amount} {self.currency} ({self.transaction_date})"


class ReceiptItem(models.Model):
    """Individual items from parsed receipts"""
    receipt = models.ForeignKey(ParsedReceipt, on_delete=models.CASCADE, related_name='items')
    
    # Item details
    name = models.CharField(max_length=255)
    barcode = models.CharField(max_length=50, blank=True)
    category = models.CharField(max_length=100, blank=True)
    
    # Quantities and pricing
    quantity = models.DecimalField(max_digits=10, decimal_places=3, default=1)
    unit = models.CharField(max_length=20, blank=True)  # kg, adet, litre, etc.
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Discounts
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Tax
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Links to other modules
    linked_product_id = models.IntegerField(null=True, blank=True)  # Link to Kişisel Enflasyon
    linked_stock_item_id = models.IntegerField(null=True, blank=True)  # Link to WIMS
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['id']
    
    def __str__(self):
        return f"{self.name} x{self.quantity} = {self.total_price}"


class DocumentBatch(models.Model):
    """Batch upload tracking for multiple documents"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='document_batches')
    batch_name = models.CharField(max_length=255)
    total_documents = models.IntegerField(default=0)
    processed_documents = models.IntegerField(default=0)
    failed_documents = models.IntegerField(default=0)
    
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=ProcessingStatus.choices, default=ProcessingStatus.PENDING)
    
    class Meta:
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.batch_name} - {self.processed_documents}/{self.total_documents}"


class OCRTemplate(models.Model):
    """Templates for parsing specific store/company receipts"""
    store_name = models.CharField(max_length=255, unique=True)
    store_aliases = models.JSONField(default=list)  # Alternative names
    
    # Field mappings for OCR parsing
    field_mappings = models.JSONField(default=dict)
    # Example: {"date": "TARIH", "total": "TOPLAM", "tax": "KDV"}
    
    # Regular expressions for parsing
    regex_patterns = models.JSONField(default=dict)
    # Example: {"date": r"\d{2}/\d{2}/\d{4}", "total": r"TOPLAM\s*:\s*([\d,\.]+)"}
    
    # Layout hints
    layout_type = models.CharField(max_length=50, default='standard')
    has_header = models.BooleanField(default=True)
    has_footer = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"OCR Template: {self.store_name}"


# Extension to WIMM models
class CreditCard(models.Model):
    """Credit card management for WIMM module"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='credit_cards')
    
    # Card details
    bank_name = models.CharField(max_length=100)
    card_name = models.CharField(max_length=100)  # e.g., "Bonus Card", "Maximum Card"
    last_four_digits = models.CharField(max_length=4)
    card_type = models.CharField(max_length=20, choices=[
        ('visa', 'Visa'),
        ('mastercard', 'MasterCard'),
        ('amex', 'American Express'),
        ('other', 'Other')
    ])
    
    # Financial details
    credit_limit = models.DecimalField(max_digits=10, decimal_places=2)
    current_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    available_credit = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Billing cycle
    statement_day = models.IntegerField()  # Day of month (1-31)
    payment_due_day = models.IntegerField()  # Day of month (1-31)
    
    # Status
    is_active = models.BooleanField(default=True)
    expiry_date = models.DateField()
    
    # Metadata
    color = models.CharField(max_length=7, default='#ff8c00')  # For UI
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['bank_name', 'card_name']
        unique_together = ['user', 'last_four_digits', 'bank_name']
    
    def __str__(self):
        return f"{self.bank_name} ***{self.last_four_digits}"
    
    @property
    def utilization_rate(self):
        if self.credit_limit > 0:
            return (self.current_balance / self.credit_limit) * 100
        return 0


class Subscription(models.Model):
    """Recurring subscriptions and payments"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscriptions')
    
    # Service details
    service_name = models.CharField(max_length=100)  # Netflix, Spotify, etc.
    category = models.CharField(max_length=50, choices=[
        ('streaming', 'Streaming'),
        ('software', 'Software'),
        ('utilities', 'Utilities'),
        ('insurance', 'Insurance'),
        ('membership', 'Membership'),
        ('other', 'Other')
    ])
    
    # Billing details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='TRY')
    billing_cycle = models.CharField(max_length=20, choices=[
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
        ('quarterly', 'Quarterly'),
        ('weekly', 'Weekly')
    ])
    
    # Payment details
    payment_method = models.ForeignKey(CreditCard, on_delete=models.SET_NULL, null=True, blank=True)
    billing_day = models.IntegerField()  # Day of month/year
    
    # Status
    is_active = models.BooleanField(default=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    next_billing_date = models.DateField()
    
    # Notifications
    notify_before_days = models.IntegerField(default=3)
    auto_renew = models.BooleanField(default=True)
    
    # Metadata
    icon = models.CharField(max_length=50, blank=True)  # emoji or icon name
    color = models.CharField(max_length=7, default='#ff8c00')
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['service_name']
    
    def __str__(self):
        return f"{self.service_name} - {self.amount} {self.currency}/{self.billing_cycle}"
    
    @property
    def yearly_cost(self):
        multipliers = {
            'monthly': 12,
            'yearly': 1,
            'quarterly': 4,
            'weekly': 52
        }
        return self.amount * multipliers.get(self.billing_cycle, 1)


class ExpenseCategory(models.Model):
    """Flexible expense categorization"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='expense_categories')
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')
    
    # Visual
    icon = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=7, default='#ff8c00')
    
    # Budget
    monthly_budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # System categories (cannot be deleted)
    is_system = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
        unique_together = ['user', 'name', 'parent']
    
    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name


class ExpenseGroup(models.Model):
    """Group expenses by project or purpose"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='expense_groups')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Budget and tracking
    budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    
    # Visual
    color = models.CharField(max_length=7, default='#ff8c00')
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'name']
    
    def __str__(self):
        return self.name

# Import enhanced document models
from .document_models import DocumentType as EnhancedDocumentType, DocumentShare, DEFAULT_DOCUMENT_TYPES

