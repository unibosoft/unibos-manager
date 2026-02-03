"""
Documents Module - Django Admin Registration
"""

from django.contrib import admin
from .models import (
    Document, ParsedReceipt, ReceiptItem,
    DocumentBatch, OCRTemplate,
    CreditCard, Subscription, ExpenseCategory, ExpenseGroup
)
from .gamification_models import (
    UserProfile, Achievement, PointTransaction,
    Challenge, UserChallenge, Leaderboard,
    ValidationFeedback, LearningModel
)
from .document_models import DocumentType, DocumentShare


class ReceiptItemInline(admin.TabularInline):
    model = ReceiptItem
    extra = 0
    readonly_fields = ['created_at']


class ParsedReceiptInline(admin.StackedInline):
    model = ParsedReceipt
    extra = 0
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = [
        'original_filename', 'user', 'document_type',
        'processing_status', 'ocr_confidence', 'uploaded_at', 'is_deleted'
    ]
    list_filter = ['document_type', 'processing_status', 'is_deleted', 'ai_processed']
    search_fields = ['original_filename', 'ocr_text', 'user__username']
    readonly_fields = ['id', 'uploaded_at', 'updated_at', 'ocr_processed_at', 'ai_processed_at']
    date_hierarchy = 'uploaded_at'
    inlines = [ParsedReceiptInline]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(ParsedReceipt)
class ParsedReceiptAdmin(admin.ModelAdmin):
    list_display = [
        'store_name', 'total_amount', 'currency',
        'transaction_date', 'payment_method'
    ]
    list_filter = ['currency', 'payment_method']
    search_fields = ['store_name', 'receipt_number']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [ReceiptItemInline]


@admin.register(ReceiptItem)
class ReceiptItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'quantity', 'unit_price', 'total_price', 'category']
    list_filter = ['category']
    search_fields = ['name', 'barcode']
    readonly_fields = ['created_at']


@admin.register(DocumentBatch)
class DocumentBatchAdmin(admin.ModelAdmin):
    list_display = [
        'batch_name', 'user', 'total_documents',
        'processed_documents', 'failed_documents', 'status', 'started_at'
    ]
    list_filter = ['status']
    search_fields = ['batch_name', 'user__username']
    readonly_fields = ['started_at', 'completed_at']


@admin.register(OCRTemplate)
class OCRTemplateAdmin(admin.ModelAdmin):
    list_display = ['store_name', 'layout_type', 'has_header', 'has_footer', 'created_at']
    search_fields = ['store_name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(CreditCard)
class CreditCardAdmin(admin.ModelAdmin):
    list_display = [
        'bank_name', 'card_name', 'last_four_digits',
        'credit_limit', 'current_balance', 'is_active', 'user'
    ]
    list_filter = ['card_type', 'is_active', 'bank_name']
    search_fields = ['bank_name', 'card_name', 'user__username']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = [
        'service_name', 'category', 'amount', 'currency',
        'billing_cycle', 'is_active', 'next_billing_date', 'user'
    ]
    list_filter = ['category', 'billing_cycle', 'is_active']
    search_fields = ['service_name', 'user__username']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'monthly_budget', 'is_system', 'user']
    list_filter = ['is_system']
    search_fields = ['name', 'user__username']


@admin.register(ExpenseGroup)
class ExpenseGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'budget', 'start_date', 'end_date', 'is_active', 'user']
    list_filter = ['is_active']
    search_fields = ['name', 'user__username']


# Gamification models

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'total_points', 'current_level',
        'receipts_processed', 'streak_days', 'accuracy_score'
    ]
    list_filter = ['current_level']
    search_fields = ['user__username']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'achievement_type', 'rarity', 'points_awarded', 'unlocked_at']
    list_filter = ['achievement_type', 'rarity']
    search_fields = ['name', 'user__username']


@admin.register(PointTransaction)
class PointTransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'points', 'transaction_type', 'reason', 'created_at']
    list_filter = ['transaction_type']
    search_fields = ['user__username', 'reason']
    readonly_fields = ['created_at']


@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'challenge_type', 'target_type',
        'target_count', 'points_reward', 'is_active',
        'start_date', 'end_date'
    ]
    list_filter = ['challenge_type', 'is_active', 'target_type']
    search_fields = ['title']


@admin.register(UserChallenge)
class UserChallengeAdmin(admin.ModelAdmin):
    list_display = ['user', 'challenge', 'current_progress', 'completed', 'completed_at']
    list_filter = ['completed']
    search_fields = ['user__username', 'challenge__title']


@admin.register(Leaderboard)
class LeaderboardAdmin(admin.ModelAdmin):
    list_display = ['user', 'period_type', 'rank', 'points_earned', 'receipts_processed']
    list_filter = ['period_type']
    search_fields = ['user__username']


@admin.register(ValidationFeedback)
class ValidationFeedbackAdmin(admin.ModelAdmin):
    list_display = ['user', 'field_name', 'is_correct', 'points_awarded', 'created_at']
    list_filter = ['field_name', 'is_correct']
    search_fields = ['user__username']


@admin.register(LearningModel)
class LearningModelAdmin(admin.ModelAdmin):
    list_display = ['pattern_type', 'store_name', 'confidence_score', 'usage_count', 'success_count']
    list_filter = ['pattern_type']
    search_fields = ['store_name']


# Document sharing models

@admin.register(DocumentType)
class DocumentTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'requires_ocr', 'privacy_level', 'is_active']
    list_filter = ['category', 'is_active', 'requires_ocr']
    search_fields = ['name']


@admin.register(DocumentShare)
class DocumentShareAdmin(admin.ModelAdmin):
    list_display = [
        'document', 'share_type', 'shared_by', 'shared_with',
        'permission', 'access_count', 'created_at'
    ]
    list_filter = ['share_type', 'permission']
    search_fields = ['shared_by__username', 'shared_with__username']
    readonly_fields = ['created_at']
