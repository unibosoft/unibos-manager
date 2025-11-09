"""
Document Module Serializers
REST API serializers for document management and OCR
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db import transaction as db_transaction
import hashlib
import mimetypes
from pathlib import Path

from .models import (
    DocumentCategory, Document, OCRResult,
    DocumentBatch, DocumentTemplate, DocumentIntegration
)


class DocumentCategorySerializer(serializers.ModelSerializer):
    """Document category serializer"""
    document_count = serializers.SerializerMethodField()
    
    class Meta:
        model = DocumentCategory
        fields = [
            'id', 'name', 'slug', 'icon', 'color',
            'keywords', 'document_count'
        ]
    
    def get_document_count(self, obj):
        """Get number of documents in this category"""
        return obj.document_set.count()


class OCRResultSerializer(serializers.ModelSerializer):
    """OCR result serializer"""
    
    class Meta:
        model = OCRResult
        fields = [
            'id', 'ocr_provider', 'vendor_name', 'vendor_address',
            'vendor_tax_id', 'vendor_phone', 'transaction_date',
            'transaction_number', 'subtotal', 'tax_amount',
            'discount_amount', 'total_amount', 'currency',
            'payment_method', 'card_last_four', 'line_items',
            'confidence_scores', 'processing_time',
            'is_verified', 'verified_by', 'verified_at',
            'manual_corrections', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class DocumentSerializer(serializers.ModelSerializer):
    """Document serializer with OCR results"""
    ocr_result = OCRResultSerializer(read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    file_size_mb = serializers.SerializerMethodField()
    is_expired = serializers.ReadOnlyField()
    
    class Meta:
        model = Document
        fields = [
            'id', 'document_id', 'original_file', 'processed_file',
            'original_filename', 'file_size', 'file_size_mb',
            'mime_type', 'document_type', 'category', 'category_name',
            'tags', 'document_date', 'expiry_date', 'is_expired',
            'ocr_status', 'ocr_confidence', 'processing_started_at',
            'processing_completed_at', 'processing_error',
            'extracted_text', 'extracted_text_language',
            'is_sensitive', 'is_encrypted', 'is_shared',
            'share_token', 'share_expires_at', 'notes',
            'metadata', 'created_at', 'updated_at',
            'last_accessed_at', 'access_count', 'is_archived',
            'archived_at', 'ocr_result'
        ]
        read_only_fields = [
            'document_id', 'file_hash', 'file_size',
            'processing_started_at', 'processing_completed_at',
            'extracted_text', 'searchable_content',
            'created_at', 'updated_at', 'last_accessed_at',
            'access_count'
        ]
    
    def get_file_size_mb(self, obj):
        """Get file size in MB"""
        return round(obj.file_size / (1024 * 1024), 2) if obj.file_size else 0


class DocumentUploadSerializer(serializers.ModelSerializer):
    """Serializer for document upload"""
    auto_process = serializers.BooleanField(default=True, write_only=True)
    extract_to_modules = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        write_only=True,
        help_text="List of modules to extract data to: ['wimm', 'wims', 'personal_inflation']"
    )
    
    class Meta:
        model = Document
        fields = [
            'original_file', 'document_type', 'category',
            'tags', 'document_date', 'expiry_date',
            'is_sensitive', 'notes', 'metadata',
            'auto_process', 'extract_to_modules'
        ]
    
    def validate_original_file(self, value):
        """Validate uploaded file"""
        # Check file size (max 50MB)
        if value.size > 50 * 1024 * 1024:
            raise serializers.ValidationError("File size cannot exceed 50MB")
        
        # Check file type
        mime_type, _ = mimetypes.guess_type(value.name)
        allowed_types = [
            'application/pdf', 'image/jpeg', 'image/jpg',
            'image/png', 'image/tiff', 'image/bmp', 'image/gif'
        ]
        if mime_type not in allowed_types:
            raise serializers.ValidationError(f"File type {mime_type} is not supported")
        
        return value
    
    @db_transaction.atomic
    def create(self, validated_data):
        """Create document and trigger processing"""
        # Extract custom fields
        auto_process = validated_data.pop('auto_process', True)
        extract_to_modules = validated_data.pop('extract_to_modules', [])
        
        # Set file metadata
        file = validated_data['original_file']
        validated_data['original_filename'] = file.name
        validated_data['file_size'] = file.size
        validated_data['mime_type'], _ = mimetypes.guess_type(file.name)
        
        # Calculate file hash for deduplication
        sha256_hash = hashlib.sha256()
        for chunk in file.chunks():
            sha256_hash.update(chunk)
        validated_data['file_hash'] = sha256_hash.hexdigest()
        
        # Check for duplicate
        existing = Document.objects.filter(
            user=validated_data['user'],
            file_hash=validated_data['file_hash']
        ).first()
        
        if existing:
            raise serializers.ValidationError({
                'original_file': 'This file has already been uploaded',
                'existing_id': existing.id
            })
        
        # Create document
        document = super().create(validated_data)
        
        # Trigger OCR processing if requested
        if auto_process:
            from .tasks import process_document_ocr
            process_document_ocr.delay(document.id)
        
        # Create integration records for requested modules
        for module in extract_to_modules:
            DocumentIntegration.objects.create(
                document=document,
                module=module,
                related_model='',
                related_object_id=0
            )
        
        return document


class DocumentBatchSerializer(serializers.ModelSerializer):
    """Document batch upload serializer"""
    progress_percentage = serializers.ReadOnlyField()
    
    class Meta:
        model = DocumentBatch
        fields = [
            'id', 'batch_id', 'total_documents',
            'processed_documents', 'failed_documents',
            'status', 'progress_percentage',
            'started_at', 'completed_at', 'errors'
        ]
        read_only_fields = [
            'batch_id', 'total_documents', 'processed_documents',
            'failed_documents', 'status', 'started_at',
            'completed_at', 'errors'
        ]


class DocumentBatchUploadSerializer(serializers.Serializer):
    """Serializer for batch document upload"""
    documents = serializers.ListField(
        child=serializers.FileField(),
        max_length=100,
        help_text="List of document files to upload (max 100)"
    )
    document_type = serializers.CharField(required=False)
    category = serializers.PrimaryKeyRelatedField(
        queryset=DocumentCategory.objects.all(),
        required=False
    )
    auto_process = serializers.BooleanField(default=True)
    extract_to_modules = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    
    def validate_documents(self, value):
        """Validate batch of documents"""
        if len(value) > 100:
            raise serializers.ValidationError("Cannot upload more than 100 documents at once")
        
        total_size = sum(file.size for file in value)
        if total_size > 500 * 1024 * 1024:  # 500MB total
            raise serializers.ValidationError("Total batch size cannot exceed 500MB")
        
        return value


class DocumentTemplateSerializer(serializers.ModelSerializer):
    """Document template serializer"""
    
    class Meta:
        model = DocumentTemplate
        fields = [
            'id', 'name', 'document_type',
            'extraction_patterns', 'field_mappings',
            'vendor_keywords', 'validation_rules',
            'sample_document', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class DocumentIntegrationSerializer(serializers.ModelSerializer):
    """Document integration serializer"""
    document_name = serializers.CharField(
        source='document.original_filename',
        read_only=True
    )
    
    class Meta:
        model = DocumentIntegration
        fields = [
            'id', 'document', 'document_name', 'module',
            'related_model', 'related_object_id',
            'status', 'processed_at', 'error_message',
            'synced_data', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'processed_at', 'created_at', 'updated_at'
        ]


class DocumentSearchSerializer(serializers.Serializer):
    """Serializer for document search"""
    query = serializers.CharField(required=True, min_length=2)
    document_types = serializers.MultipleChoiceField(
        choices=[
            'receipt', 'invoice', 'statement', 'contract',
            'report', 'tax_document', 'warranty', 'manual',
            'identification', 'medical', 'insurance', 'other'
        ],
        required=False
    )
    categories = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
    has_ocr = serializers.BooleanField(required=False)
    is_verified = serializers.BooleanField(required=False)
    
    def validate(self, data):
        """Validate search parameters"""
        if 'date_from' in data and 'date_to' in data:
            if data['date_from'] > data['date_to']:
                raise serializers.ValidationError("date_from cannot be after date_to")
        return data


class DocumentStatisticsSerializer(serializers.Serializer):
    """Document statistics serializer"""
    total_documents = serializers.IntegerField()
    total_size_mb = serializers.FloatField()
    documents_by_type = serializers.DictField()
    documents_by_category = serializers.ListField()
    ocr_statistics = serializers.DictField()
    recent_uploads = DocumentSerializer(many=True)
    storage_usage = serializers.DictField()
    processing_queue = serializers.IntegerField()
    integration_status = serializers.DictField()