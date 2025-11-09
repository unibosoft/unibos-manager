"""
Document Type and Sharing Models
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()


class DocumentType(models.Model):
    """Detailed document type classification"""
    
    CATEGORY_CHOICES = [
        ('financial', 'Financial'),
        ('medical', 'Medical'),
        ('legal', 'Legal'),
        ('personal', 'Personal'),
        ('government', 'Government'),
        ('education', 'Education'),
        ('business', 'Business'),
        ('utility', 'Utility'),
        ('retail', 'Retail'),
        ('transportation', 'Transportation'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    
    # Document type patterns for auto-detection
    keywords = models.JSONField(default=list, help_text="Keywords to detect this document type")
    regex_patterns = models.JSONField(default=list, help_text="Regex patterns for detection")
    
    # Processing configuration
    requires_ocr = models.BooleanField(default=True)
    requires_validation = models.BooleanField(default=False)
    privacy_level = models.IntegerField(default=1, help_text="1=Public, 2=Private, 3=Restricted")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['category', 'name']
        
    def __str__(self):
        return f"{self.category} - {self.name}"


class DocumentShare(models.Model):
    """Document sharing functionality"""
    
    PERMISSION_CHOICES = [
        ('view', 'View Only'),
        ('comment', 'View and Comment'),
        ('edit', 'View and Edit'),
        ('admin', 'Full Access'),
    ]
    
    SHARE_TYPE_CHOICES = [
        ('user', 'Individual User'),
        ('group', 'User Group'),
        ('public', 'Public Link'),
        ('restricted', 'Restricted Access'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey('Document', on_delete=models.CASCADE, related_name='shares')
    
    # Sharing configuration
    share_type = models.CharField(max_length=20, choices=SHARE_TYPE_CHOICES, default='user')
    shared_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents_shared')
    shared_with = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents_received', null=True, blank=True)
    shared_with_group = models.CharField(max_length=100, blank=True, help_text="Group name if sharing with group")
    
    # Permissions
    permission = models.CharField(max_length=20, choices=PERMISSION_CHOICES, default='view')
    can_reshare = models.BooleanField(default=False)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Access tracking
    share_link = models.CharField(max_length=100, unique=True, blank=True)
    access_count = models.IntegerField(default=0)
    last_accessed = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        unique_together = [('document', 'shared_with'), ('document', 'shared_with_group')]
        ordering = ['-created_at']
        
    def __str__(self):
        if self.shared_with:
            return f"{self.document} shared with {self.shared_with.username}"
        elif self.shared_with_group:
            return f"{self.document} shared with group {self.shared_with_group}"
        return f"{self.document} - {self.share_type}"
    
    def is_valid(self):
        """Check if share is still valid"""
        if self.revoked_at:
            return False
        if self.expires_at and self.expires_at < timezone.now():
            return False
        return True
    
    def record_access(self):
        """Record access to shared document"""
        self.access_count += 1
        self.last_accessed = timezone.now()
        self.save(update_fields=['access_count', 'last_accessed'])


# Predefined document types
DEFAULT_DOCUMENT_TYPES = [
    # Financial
    {'name': 'Receipt', 'category': 'financial', 'keywords': ['fiş', 'receipt', 'makbuz', 'total', 'toplam', 'kdv']},
    {'name': 'Invoice', 'category': 'financial', 'keywords': ['fatura', 'invoice', 'vergi no', 'tax']},
    {'name': 'Bank Statement', 'category': 'financial', 'keywords': ['hesap özeti', 'statement', 'bakiye', 'balance']},
    {'name': 'Credit Card Statement', 'category': 'financial', 'keywords': ['kredi kartı', 'credit card', 'ekstre', 'minimum ödeme']},
    
    # Medical
    {'name': 'Prescription', 'category': 'medical', 'keywords': ['reçete', 'prescription', 'ilaç', 'doz', 'doktor']},
    {'name': 'Lab Report', 'category': 'medical', 'keywords': ['tahlil', 'laboratuvar', 'sonuç', 'test', 'analiz']},
    {'name': 'Medical Report', 'category': 'medical', 'keywords': ['rapor', 'tanı', 'tedavi', 'muayene']},
    
    # Legal
    {'name': 'Contract', 'category': 'legal', 'keywords': ['sözleşme', 'contract', 'taraf', 'madde', 'imza']},
    {'name': 'Title Deed', 'category': 'legal', 'keywords': ['tapu', 'mülkiyet', 'parsel', 'ada', 'malik']},
    {'name': 'Power of Attorney', 'category': 'legal', 'keywords': ['vekalet', 'vekaletname', 'yetki', 'temsil']},
    
    # Transportation
    {'name': 'Parking Ticket', 'category': 'transportation', 'keywords': ['otopark', 'park', 'plaka', 'giriş', 'çıkış', 'ücret']},
    {'name': 'Traffic Fine', 'category': 'transportation', 'keywords': ['trafik cezası', 'hız', 'radar', 'plaka', 'ceza tutarı']},
    {'name': 'Gas Receipt', 'category': 'transportation', 'keywords': ['akaryakıt', 'benzin', 'petrol', 'litre', 'pompa']},
    
    # Government
    {'name': 'Tax Document', 'category': 'government', 'keywords': ['vergi', 'beyanname', 'matrah', 'tahakkuk']},
    {'name': 'ID Document', 'category': 'government', 'keywords': ['kimlik', 'tc', 'nüfus', 'pasaport', 'ehliyet']},
    
    # Utility
    {'name': 'Electricity Bill', 'category': 'utility', 'keywords': ['elektrik', 'fatura', 'kwh', 'sayaç', 'tüketim']},
    {'name': 'Water Bill', 'category': 'utility', 'keywords': ['su', 'fatura', 'm3', 'sayaç', 'tüketim']},
    {'name': 'Internet Bill', 'category': 'utility', 'keywords': ['internet', 'adsl', 'fiber', 'mbps', 'modem']},
]