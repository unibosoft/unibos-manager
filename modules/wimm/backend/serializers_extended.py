"""
Extended WIMM Serializers
REST API serializers for comprehensive financial management
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db import transaction as db_transaction
from decimal import Decimal
from datetime import datetime, timedelta

from .models_extended import (
    CreditCard, Subscription, ExpenseCategory, 
    ExpenseTag, Expense, FinancialGoal
)


class CreditCardSerializer(serializers.ModelSerializer):
    """Credit card serializer with computed fields"""
    utilization_rate = serializers.ReadOnlyField()
    is_expired = serializers.ReadOnlyField()
    days_until_due = serializers.ReadOnlyField()
    masked_number = serializers.SerializerMethodField()
    
    class Meta:
        model = CreditCard
        fields = [
            'id', 'card_nickname', 'last_four_digits', 'masked_number',
            'card_brand', 'issuing_bank', 'bank_branch',
            'credit_limit', 'current_balance', 'available_credit',
            'minimum_payment', 'utilization_rate',
            'statement_day', 'due_day', 'days_until_due',
            'expiry_month', 'expiry_year', 'is_expired',
            'annual_percentage_rate', 'annual_fee',
            'has_contactless', 'has_chip', 'rewards_program',
            'cashback_rate', 'is_active', 'is_primary',
            'last_used', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['available_credit', 'card_token', 'created_at', 'updated_at']
    
    def get_masked_number(self, obj):
        """Generate masked card number"""
        return f"****-****-****-{obj.last_four_digits}"
    
    def validate_last_four_digits(self, value):
        """Ensure last four digits are numeric and 4 characters"""
        if not value.isdigit() or len(value) != 4:
            raise serializers.ValidationError("Last four digits must be exactly 4 numeric characters")
        return value
    
    def validate(self, data):
        """Validate card data"""
        # Check expiry date
        if 'expiry_year' in data and 'expiry_month' in data:
            now = datetime.now()
            if data['expiry_year'] < now.year or (
                data['expiry_year'] == now.year and data['expiry_month'] < now.month
            ):
                raise serializers.ValidationError("Card expiry date cannot be in the past")
        
        # Check credit limit and balance
        if 'credit_limit' in data and 'current_balance' in data:
            if data['current_balance'] > data['credit_limit']:
                raise serializers.ValidationError("Current balance cannot exceed credit limit")
        
        return data


class CreditCardSummarySerializer(serializers.ModelSerializer):
    """Lightweight credit card serializer for listings"""
    utilization_rate = serializers.ReadOnlyField()
    
    class Meta:
        model = CreditCard
        fields = [
            'id', 'card_nickname', 'last_four_digits', 'card_brand',
            'issuing_bank', 'credit_limit', 'available_credit',
            'utilization_rate', 'is_primary', 'is_active'
        ]


class SubscriptionSerializer(serializers.ModelSerializer):
    """Subscription serializer with calculated fields"""
    annual_cost = serializers.ReadOnlyField()
    days_until_billing = serializers.ReadOnlyField()
    is_in_trial = serializers.ReadOnlyField()
    payment_method_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Subscription
        fields = [
            'id', 'service_name', 'service_category', 'provider_name',
            'provider_website', 'plan_name', 'plan_description',
            'billing_cycle', 'custom_billing_days', 'amount', 'currency',
            'annual_cost', 'payment_method', 'payment_method_display',
            'alternative_payment', 'start_date', 'end_date',
            'next_billing_date', 'days_until_billing', 'last_payment_date',
            'trial_end_date', 'is_trial', 'is_in_trial', 'is_active',
            'auto_renew', 'reminder_days_before', 'send_notifications',
            'cancellation_date', 'cancellation_reason',
            'account_email', 'account_username', 'account_id',
            'tags', 'metadata', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_payment_method_display(self, obj):
        """Get payment method display string"""
        if obj.payment_method:
            return f"{obj.payment_method.card_nickname} (...{obj.payment_method.last_four_digits})"
        return obj.alternative_payment or "Not specified"
    
    def validate(self, data):
        """Validate subscription data"""
        # Check date logic
        if 'start_date' in data and 'end_date' in data:
            if data['end_date'] and data['end_date'] < data['start_date']:
                raise serializers.ValidationError("End date cannot be before start date")
        
        # Check billing cycle
        if data.get('billing_cycle') == 'custom' and not data.get('custom_billing_days'):
            raise serializers.ValidationError("Custom billing days required for custom billing cycle")
        
        return data


class SubscriptionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating subscriptions with auto-calculation"""
    
    class Meta:
        model = Subscription
        fields = [
            'service_name', 'service_category', 'provider_name',
            'provider_website', 'plan_name', 'plan_description',
            'billing_cycle', 'custom_billing_days', 'amount', 'currency',
            'payment_method', 'alternative_payment', 'start_date',
            'end_date', 'trial_end_date', 'is_trial', 'auto_renew',
            'reminder_days_before', 'send_notifications',
            'account_email', 'account_username', 'account_id',
            'tags', 'notes'
        ]
    
    def create(self, validated_data):
        """Create subscription with calculated next billing date"""
        # Calculate next billing date
        if not validated_data.get('next_billing_date'):
            validated_data['next_billing_date'] = validated_data['start_date']
        
        return super().create(validated_data)


class ExpenseCategorySerializer(serializers.ModelSerializer):
    """Expense category serializer with hierarchy"""
    full_path = serializers.ReadOnlyField()
    subcategories = serializers.SerializerMethodField()
    expense_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ExpenseCategory
        fields = [
            'id', 'name', 'slug', 'parent', 'full_path',
            'icon', 'color', 'monthly_budget', 'is_essential',
            'is_tax_deductible', 'subcategories', 'expense_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_subcategories(self, obj):
        """Get subcategories"""
        subcategories = obj.subcategories.all()
        return ExpenseCategorySerializer(subcategories, many=True, read_only=True).data
    
    def get_expense_count(self, obj):
        """Get number of expenses in this category"""
        return obj.expenses.count()


class ExpenseTagSerializer(serializers.ModelSerializer):
    """Expense tag serializer"""
    expense_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ExpenseTag
        fields = [
            'id', 'name', 'slug', 'color', 'description',
            'expense_count'
        ]
    
    def get_expense_count(self, obj):
        """Get number of expenses with this tag"""
        return obj.expenses.count()


class ExpenseSerializer(serializers.ModelSerializer):
    """Comprehensive expense serializer"""
    category_display = serializers.SerializerMethodField()
    tags_display = serializers.SerializerMethodField()
    payment_method_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Expense
        fields = [
            'id', 'description', 'amount', 'currency', 'expense_date',
            'category', 'category_display', 'tags', 'tags_display',
            'payment_method', 'payment_method_display', 'credit_card',
            'vendor_name', 'vendor_category', 'location',
            'project', 'purpose', 'has_receipt', 'receipt_document',
            'is_business_expense', 'is_tax_deductible', 'tax_amount',
            'subscription', 'notes', 'metadata',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_category_display(self, obj):
        """Get category full path"""
        return obj.category.full_path if obj.category else None
    
    def get_tags_display(self, obj):
        """Get tag names"""
        return [tag.name for tag in obj.tags.all()]
    
    def get_payment_method_display(self, obj):
        """Get payment method display"""
        if obj.payment_method == 'credit_card' and obj.credit_card:
            return f"Credit Card: {obj.credit_card.card_nickname}"
        return obj.get_payment_method_display()
    
    def validate(self, data):
        """Validate expense data"""
        # Check credit card requirement
        if data.get('payment_method') == 'credit_card' and not data.get('credit_card'):
            raise serializers.ValidationError("Credit card must be specified for credit card payments")
        
        # Check tax amount
        if data.get('tax_amount', 0) > data.get('amount', 0):
            raise serializers.ValidationError("Tax amount cannot exceed total amount")
        
        return data


class ExpenseCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating expenses with auto-updates"""
    
    class Meta:
        model = Expense
        fields = [
            'description', 'amount', 'currency', 'expense_date',
            'category', 'tags', 'payment_method', 'credit_card',
            'vendor_name', 'vendor_category', 'location',
            'project', 'purpose', 'has_receipt',
            'is_business_expense', 'is_tax_deductible', 'tax_amount',
            'subscription', 'notes', 'metadata'
        ]
    
    @db_transaction.atomic
    def create(self, validated_data):
        """Create expense and update credit card balance if needed"""
        tags = validated_data.pop('tags', [])
        expense = super().create(validated_data)
        
        # Set tags
        if tags:
            expense.tags.set(tags)
        
        # Update credit card balance
        if expense.payment_method == 'credit_card' and expense.credit_card:
            expense.credit_card.current_balance += expense.amount
            expense.credit_card.last_used = datetime.now()
            expense.credit_card.save()
        
        return expense


class FinancialGoalSerializer(serializers.ModelSerializer):
    """Financial goal serializer with progress tracking"""
    progress_percentage = serializers.ReadOnlyField()
    days_remaining = serializers.ReadOnlyField()
    required_monthly_contribution = serializers.ReadOnlyField()
    
    class Meta:
        model = FinancialGoal
        fields = [
            'id', 'name', 'description', 'goal_type',
            'target_amount', 'current_amount', 'currency',
            'progress_percentage', 'start_date', 'target_date',
            'days_remaining', 'monthly_contribution',
            'required_monthly_contribution', 'priority',
            'is_active', 'is_achieved', 'achieved_date',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'achieved_date']
    
    def validate(self, data):
        """Validate goal data"""
        # Check dates
        if 'target_date' in data and 'start_date' in data:
            if data['target_date'] <= data['start_date']:
                raise serializers.ValidationError("Target date must be after start date")
        
        # Check amounts
        if data.get('current_amount', 0) > data.get('target_amount', 0):
            data['is_achieved'] = True
            data['achieved_date'] = datetime.now().date()
        
        return data


class FinancialDashboardSerializer(serializers.Serializer):
    """Dashboard statistics serializer"""
    # Credit cards
    total_credit_limit = serializers.DecimalField(max_digits=20, decimal_places=2)
    total_credit_used = serializers.DecimalField(max_digits=20, decimal_places=2)
    total_available_credit = serializers.DecimalField(max_digits=20, decimal_places=2)
    average_utilization = serializers.FloatField()
    cards_summary = CreditCardSummarySerializer(many=True)
    
    # Subscriptions
    active_subscriptions_count = serializers.IntegerField()
    total_monthly_subscriptions = serializers.DecimalField(max_digits=20, decimal_places=2)
    total_annual_subscriptions = serializers.DecimalField(max_digits=20, decimal_places=2)
    upcoming_payments = SubscriptionSerializer(many=True)
    
    # Expenses
    current_month_expenses = serializers.DecimalField(max_digits=20, decimal_places=2)
    previous_month_expenses = serializers.DecimalField(max_digits=20, decimal_places=2)
    expense_trend = serializers.FloatField()
    top_categories = serializers.ListField()
    recent_expenses = ExpenseSerializer(many=True)
    
    # Financial goals
    active_goals_count = serializers.IntegerField()
    total_goal_progress = serializers.FloatField()
    goals_summary = FinancialGoalSerializer(many=True)
    
    # Insights
    insights = serializers.ListField()
    warnings = serializers.ListField()
    recommendations = serializers.ListField()