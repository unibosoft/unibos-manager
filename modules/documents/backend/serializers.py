"""
Document Module Serializers
REST API serializers for document management and OCR
"""
from rest_framework import serializers
from django.core.files.base import ContentFile
import mimetypes

from .models import (
    Document, ParsedReceipt, ReceiptItem,
    DocumentBatch, OCRTemplate,
    CreditCard, Subscription, ExpenseCategory, ExpenseGroup,
    DocumentType, ProcessingStatus
)


class ReceiptItemSerializer(serializers.ModelSerializer):
    """Individual receipt item serializer"""

    class Meta:
        model = ReceiptItem
        fields = [
            'id', 'name', 'barcode', 'category',
            'quantity', 'unit', 'unit_price', 'total_price',
            'discount_amount', 'discount_percentage', 'tax_rate',
            'linked_product_id', 'linked_stock_item_id',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ParsedReceiptSerializer(serializers.ModelSerializer):
    """Parsed receipt data serializer"""
    items = ReceiptItemSerializer(many=True, read_only=True)
    items_count = serializers.SerializerMethodField()

    class Meta:
        model = ParsedReceipt
        fields = [
            'id', 'document', 'store_name', 'store_address',
            'store_phone', 'store_tax_id',
            'transaction_date', 'receipt_number', 'cashier_id',
            'subtotal', 'tax_amount', 'discount_amount', 'total_amount',
            'payment_method', 'card_last_digits', 'currency',
            'raw_ocr_data', 'items', 'items_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_items_count(self, obj):
        return obj.items.count()


class DocumentSerializer(serializers.ModelSerializer):
    """Document serializer with optional parsed receipt"""
    parsed_receipt = ParsedReceiptSerializer(read_only=True)
    status_display = serializers.CharField(
        source='get_processing_status_display', read_only=True
    )
    type_display = serializers.CharField(
        source='get_document_type_display', read_only=True
    )
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            'id', 'user', 'document_type', 'type_display',
            'original_filename', 'file_path', 'thumbnail_path',
            'processing_status', 'status_display',
            'ocr_text', 'ocr_confidence', 'ocr_processed_at',
            'tesseract_text', 'tesseract_confidence', 'tesseract_parsed_data',
            'ollama_text', 'ollama_confidence', 'ollama_parsed_data', 'ollama_model',
            'preferred_ocr_method',
            'ai_processed', 'ai_parsed_data', 'ai_provider',
            'ai_confidence', 'ai_processed_at',
            'analysis_results', 'last_analysis_at',
            'uploaded_at', 'updated_at',
            'tags', 'custom_metadata',
            'is_deleted', 'deleted_at',
            'parsed_receipt', 'thumbnail_url'
        ]
        read_only_fields = [
            'id', 'user', 'uploaded_at', 'updated_at',
            'ocr_processed_at', 'ai_processed_at', 'last_analysis_at',
            'deleted_at'
        ]

    def get_thumbnail_url(self, obj):
        if obj.thumbnail_path:
            try:
                return obj.thumbnail_path.url
            except Exception:
                return None
        return None


class DocumentListSerializer(serializers.ModelSerializer):
    """Lightweight document serializer for list views"""
    status_display = serializers.CharField(
        source='get_processing_status_display', read_only=True
    )
    type_display = serializers.CharField(
        source='get_document_type_display', read_only=True
    )
    thumbnail_url = serializers.SerializerMethodField()
    store_name = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            'id', 'document_type', 'type_display',
            'original_filename', 'processing_status', 'status_display',
            'ocr_confidence', 'uploaded_at',
            'thumbnail_url', 'store_name', 'total_amount',
            'is_deleted', 'tags'
        ]

    def get_thumbnail_url(self, obj):
        if obj.thumbnail_path:
            try:
                return obj.thumbnail_path.url
            except Exception:
                return None
        return None

    def get_store_name(self, obj):
        try:
            if hasattr(obj, 'parsed_receipt') and obj.parsed_receipt:
                return obj.parsed_receipt.store_name
        except Exception:
            pass
        return None

    def get_total_amount(self, obj):
        try:
            if hasattr(obj, 'parsed_receipt') and obj.parsed_receipt:
                return str(obj.parsed_receipt.total_amount) if obj.parsed_receipt.total_amount else None
        except Exception:
            pass
        return None


class DocumentUploadSerializer(serializers.Serializer):
    """Serializer for document upload"""
    files = serializers.ListField(
        child=serializers.FileField(),
        max_length=100,
        help_text="Document files to upload (max 100)"
    )
    document_type = serializers.ChoiceField(
        choices=DocumentType.choices,
        default=DocumentType.RECEIPT
    )
    batch_name = serializers.CharField(required=False, max_length=255)
    auto_ocr = serializers.BooleanField(default=True)

    def validate_files(self, value):
        """Validate uploaded files"""
        allowed_types = [
            'application/pdf', 'image/jpeg', 'image/jpg',
            'image/png', 'image/tiff', 'image/bmp', 'image/gif'
        ]

        for file in value:
            # Check file size (max 50MB per file)
            if file.size > 50 * 1024 * 1024:
                raise serializers.ValidationError(
                    f"File '{file.name}' exceeds 50MB limit"
                )

            # Check file type
            mime_type, _ = mimetypes.guess_type(file.name)
            if mime_type not in allowed_types:
                raise serializers.ValidationError(
                    f"File type '{mime_type}' is not supported for '{file.name}'"
                )

        # Check total size (max 500MB)
        total_size = sum(f.size for f in value)
        if total_size > 500 * 1024 * 1024:
            raise serializers.ValidationError(
                "Total batch size cannot exceed 500MB"
            )

        return value


class DocumentBatchSerializer(serializers.ModelSerializer):
    """Document batch serializer"""
    progress_percentage = serializers.SerializerMethodField()

    class Meta:
        model = DocumentBatch
        fields = [
            'id', 'user', 'batch_name',
            'total_documents', 'processed_documents', 'failed_documents',
            'status', 'progress_percentage',
            'started_at', 'completed_at'
        ]
        read_only_fields = [
            'id', 'user', 'started_at', 'completed_at'
        ]

    def get_progress_percentage(self, obj):
        if obj.total_documents > 0:
            return round(
                (obj.processed_documents + obj.failed_documents)
                / obj.total_documents * 100, 1
            )
        return 0


class OCRTemplateSerializer(serializers.ModelSerializer):
    """OCR template serializer"""

    class Meta:
        model = OCRTemplate
        fields = [
            'id', 'store_name', 'store_aliases',
            'field_mappings', 'regex_patterns',
            'layout_type', 'has_header', 'has_footer',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DocumentSearchSerializer(serializers.Serializer):
    """Serializer for document search"""
    q = serializers.CharField(required=True, min_length=2)
    type = serializers.ChoiceField(
        choices=DocumentType.choices,
        required=False
    )
    status = serializers.ChoiceField(
        choices=ProcessingStatus.choices,
        required=False
    )
    limit = serializers.IntegerField(
        required=False, default=10, min_value=1, max_value=100
    )


class CreditCardSerializer(serializers.ModelSerializer):
    """Credit card serializer"""
    utilization_rate = serializers.ReadOnlyField()

    class Meta:
        model = CreditCard
        fields = [
            'id', 'user', 'bank_name', 'card_name',
            'last_four_digits', 'card_type',
            'credit_limit', 'current_balance', 'available_credit',
            'statement_day', 'payment_due_day',
            'is_active', 'expiry_date',
            'color', 'notes', 'utilization_rate',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class SubscriptionSerializer(serializers.ModelSerializer):
    """Subscription serializer"""
    yearly_cost = serializers.ReadOnlyField()

    class Meta:
        model = Subscription
        fields = [
            'id', 'user', 'service_name', 'category',
            'amount', 'currency', 'billing_cycle',
            'payment_method', 'billing_day',
            'is_active', 'start_date', 'end_date', 'next_billing_date',
            'notify_before_days', 'auto_renew',
            'icon', 'color', 'notes', 'yearly_cost',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class ExpenseCategorySerializer(serializers.ModelSerializer):
    """Expense category serializer"""
    subcategories = serializers.SerializerMethodField()

    class Meta:
        model = ExpenseCategory
        fields = [
            'id', 'user', 'name', 'parent',
            'icon', 'color', 'monthly_budget',
            'is_system', 'subcategories',
            'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']

    def get_subcategories(self, obj):
        children = obj.subcategories.all()
        if children.exists():
            return ExpenseCategorySerializer(children, many=True).data
        return []


class ExpenseGroupSerializer(serializers.ModelSerializer):
    """Expense group serializer"""

    class Meta:
        model = ExpenseGroup
        fields = [
            'id', 'user', 'name', 'description',
            'budget', 'start_date', 'end_date',
            'color', 'is_active',
            'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']


class DocumentStatisticsSerializer(serializers.Serializer):
    """Document statistics serializer"""
    total_documents = serializers.IntegerField()
    pending_documents = serializers.IntegerField()
    processing_documents = serializers.IntegerField()
    completed_documents = serializers.IntegerField()
    failed_documents = serializers.IntegerField()
    deleted_documents = serializers.IntegerField()
    documents_by_type = serializers.DictField()
    recent_uploads = DocumentListSerializer(many=True)
