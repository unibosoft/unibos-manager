"""
Extended WIMM (Where Is My Money) Models
Comprehensive financial management with credit cards, subscriptions, and advanced tracking
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import uuid


class CreditCard(models.Model):
    """Credit card management with security and tracking"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='credit_cards')
    
    # Card identification (secure - only store last 4 digits)
    card_nickname = models.CharField(max_length=50)
    last_four_digits = models.CharField(max_length=4)
    card_brand = models.CharField(max_length=20, choices=[
        ('visa', 'Visa'),
        ('mastercard', 'MasterCard'),
        ('amex', 'American Express'),
        ('discover', 'Discover'),
        ('other', 'Other'),
    ])
    
    # Bank information
    issuing_bank = models.CharField(max_length=100)
    bank_branch = models.CharField(max_length=100, blank=True)
    
    # Card limits and balances
    credit_limit = models.DecimalField(max_digits=20, decimal_places=2)
    current_balance = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    available_credit = models.DecimalField(max_digits=20, decimal_places=2, editable=False)
    minimum_payment = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    
    # Important dates
    statement_day = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(31)],
        help_text="Day of month when statement is generated"
    )
    due_day = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(31)],
        help_text="Day of month when payment is due"
    )
    expiry_month = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])
    expiry_year = models.IntegerField(validators=[MinValueValidator(2024), MaxValueValidator(2099)])
    
    # Interest rates and fees
    annual_percentage_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        help_text="APR in percentage"
    )
    annual_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Card features
    has_contactless = models.BooleanField(default=True)
    has_chip = models.BooleanField(default=True)
    rewards_program = models.CharField(max_length=100, blank=True)
    cashback_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_primary = models.BooleanField(default=False)
    
    # Security
    card_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    last_used = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-is_primary', '-created_at']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['card_token']),
        ]
    
    def __str__(self):
        return f"{self.card_nickname} (...{self.last_four_digits})"
    
    def save(self, *args, **kwargs):
        # Calculate available credit
        self.available_credit = self.credit_limit - self.current_balance
        
        # Ensure only one primary card per user
        if self.is_primary:
            CreditCard.objects.filter(user=self.user, is_primary=True).exclude(pk=self.pk).update(is_primary=False)
        
        super().save(*args, **kwargs)
    
    @property
    def utilization_rate(self):
        """Calculate credit utilization percentage"""
        if self.credit_limit == 0:
            return 0
        return (self.current_balance / self.credit_limit) * 100
    
    @property
    def is_expired(self):
        """Check if card is expired"""
        now = timezone.now()
        return self.expiry_year < now.year or (
            self.expiry_year == now.year and self.expiry_month < now.month
        )
    
    @property
    def days_until_due(self):
        """Calculate days until payment due"""
        today = timezone.now().date()
        current_month = today.month
        current_year = today.year
        
        # Calculate next due date
        if today.day > self.due_day:
            # Due date passed this month, calculate for next month
            if current_month == 12:
                due_date = timezone.datetime(current_year + 1, 1, self.due_day).date()
            else:
                due_date = timezone.datetime(current_year, current_month + 1, self.due_day).date()
        else:
            due_date = timezone.datetime(current_year, current_month, self.due_day).date()
        
        return (due_date - today).days


class Subscription(models.Model):
    """Manage recurring subscriptions and services"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    
    # Service information
    service_name = models.CharField(max_length=100)
    service_category = models.CharField(max_length=50, choices=[
        ('streaming_video', 'Video Streaming'),
        ('streaming_music', 'Music Streaming'),
        ('cloud_storage', 'Cloud Storage'),
        ('software', 'Software/Apps'),
        ('gaming', 'Gaming'),
        ('news_magazines', 'News & Magazines'),
        ('fitness', 'Fitness & Health'),
        ('education', 'Education'),
        ('productivity', 'Productivity'),
        ('utilities', 'Utilities'),
        ('insurance', 'Insurance'),
        ('membership', 'Membership'),
        ('other', 'Other'),
    ])
    
    # Provider details
    provider_name = models.CharField(max_length=100)
    provider_website = models.URLField(blank=True)
    
    # Subscription details
    plan_name = models.CharField(max_length=100)
    plan_description = models.TextField(blank=True)
    
    # Billing information
    billing_cycle = models.CharField(max_length=20, choices=[
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('biweekly', 'Bi-weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('semi_annual', 'Semi-Annual'),
        ('annual', 'Annual'),
        ('biennial', 'Every 2 Years'),
        ('custom', 'Custom'),
    ])
    custom_billing_days = models.IntegerField(
        null=True, blank=True,
        help_text="Number of days for custom billing cycle"
    )
    
    # Payment details
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    currency = models.CharField(max_length=3, default='TRY')
    payment_method = models.ForeignKey(
        CreditCard, on_delete=models.SET_NULL, 
        null=True, blank=True,
        related_name='subscriptions'
    )
    alternative_payment = models.CharField(
        max_length=50, blank=True,
        help_text="Alternative payment method if not credit card"
    )
    
    # Subscription dates
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    next_billing_date = models.DateField()
    last_payment_date = models.DateField(null=True, blank=True)
    trial_end_date = models.DateField(null=True, blank=True)
    
    # Status and notifications
    is_active = models.BooleanField(default=True)
    is_trial = models.BooleanField(default=False)
    auto_renew = models.BooleanField(default=True)
    reminder_days_before = models.IntegerField(default=3)
    send_notifications = models.BooleanField(default=True)
    
    # Cancellation
    cancellation_date = models.DateField(null=True, blank=True)
    cancellation_reason = models.TextField(blank=True)
    
    # Account details
    account_email = models.EmailField(blank=True)
    account_username = models.CharField(max_length=100, blank=True)
    account_id = models.CharField(max_length=100, blank=True)
    
    # Tags and metadata
    tags = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    notes = models.TextField(blank=True)
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['next_billing_date', 'service_name']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['next_billing_date']),
            models.Index(fields=['service_category']),
        ]
    
    def __str__(self):
        return f"{self.service_name} - {self.plan_name}"
    
    def calculate_next_billing_date(self):
        """Calculate next billing date based on cycle"""
        if not self.last_payment_date:
            return self.start_date
        
        from dateutil.relativedelta import relativedelta
        
        cycles = {
            'daily': relativedelta(days=1),
            'weekly': relativedelta(weeks=1),
            'biweekly': relativedelta(weeks=2),
            'monthly': relativedelta(months=1),
            'quarterly': relativedelta(months=3),
            'semi_annual': relativedelta(months=6),
            'annual': relativedelta(years=1),
            'biennial': relativedelta(years=2),
        }
        
        if self.billing_cycle == 'custom' and self.custom_billing_days:
            delta = relativedelta(days=self.custom_billing_days)
        else:
            delta = cycles.get(self.billing_cycle, relativedelta(months=1))
        
        return self.last_payment_date + delta
    
    @property
    def annual_cost(self):
        """Calculate annual cost based on billing cycle"""
        multipliers = {
            'daily': 365,
            'weekly': 52,
            'biweekly': 26,
            'monthly': 12,
            'quarterly': 4,
            'semi_annual': 2,
            'annual': 1,
            'biennial': 0.5,
        }
        
        if self.billing_cycle == 'custom' and self.custom_billing_days:
            multiplier = 365 / self.custom_billing_days
        else:
            multiplier = multipliers.get(self.billing_cycle, 12)
        
        return self.amount * Decimal(str(multiplier))
    
    @property
    def days_until_billing(self):
        """Days until next billing"""
        today = timezone.now().date()
        return (self.next_billing_date - today).days if self.next_billing_date else None
    
    @property
    def is_in_trial(self):
        """Check if subscription is in trial period"""
        if not self.trial_end_date:
            return False
        return timezone.now().date() <= self.trial_end_date


class ExpenseCategory(models.Model):
    """User-defined expense categories with hierarchy"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expense_categories')
    
    # Category information
    name = models.CharField(max_length=100)
    slug = models.SlugField()
    parent = models.ForeignKey(
        'self', null=True, blank=True, 
        on_delete=models.CASCADE, 
        related_name='subcategories'
    )
    
    # Visual representation
    icon = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=7, default='#000000')
    
    # Budget allocation
    monthly_budget = models.DecimalField(
        max_digits=20, decimal_places=2, 
        null=True, blank=True
    )
    
    # Settings
    is_essential = models.BooleanField(default=False)
    is_tax_deductible = models.BooleanField(default=False)
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        unique_together = [['user', 'slug']]
    
    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name
    
    @property
    def full_path(self):
        """Get full category path"""
        if self.parent:
            return f"{self.parent.full_path} > {self.name}"
        return self.name


class ExpenseTag(models.Model):
    """Tags for organizing expenses"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expense_tags')
    name = models.CharField(max_length=50)
    slug = models.SlugField()
    color = models.CharField(max_length=7, default='#808080')
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['name']
        unique_together = [['user', 'slug']]
    
    def __str__(self):
        return self.name


class Expense(models.Model):
    """Enhanced expense tracking with flexible categorization"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expenses')
    
    # Basic information
    description = models.CharField(max_length=500)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    currency = models.CharField(max_length=3, default='TRY')
    
    # Date and time
    expense_date = models.DateTimeField(default=timezone.now)
    
    # Categorization
    category = models.ForeignKey(
        ExpenseCategory, on_delete=models.SET_NULL, 
        null=True, related_name='expenses'
    )
    tags = models.ManyToManyField(ExpenseTag, blank=True, related_name='expenses')
    
    # Payment method
    payment_method = models.CharField(max_length=20, choices=[
        ('cash', 'Cash'),
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('mobile_payment', 'Mobile Payment'),
        ('cryptocurrency', 'Cryptocurrency'),
        ('other', 'Other'),
    ])
    credit_card = models.ForeignKey(
        CreditCard, on_delete=models.SET_NULL, 
        null=True, blank=True,
        related_name='expenses'
    )
    
    # Location and vendor
    vendor_name = models.CharField(max_length=200, blank=True)
    vendor_category = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=200, blank=True)
    
    # Project/purpose grouping
    project = models.CharField(max_length=100, blank=True)
    purpose = models.CharField(max_length=200, blank=True)
    
    # Receipt and documentation
    has_receipt = models.BooleanField(default=False)
    receipt_document = models.ForeignKey(
        'documents.Document', on_delete=models.SET_NULL, 
        null=True, blank=True,
        related_name='related_expenses'
    )
    
    # Tax and business
    is_business_expense = models.BooleanField(default=False)
    is_tax_deductible = models.BooleanField(default=False)
    tax_amount = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    
    # Recurring expense link
    subscription = models.ForeignKey(
        Subscription, on_delete=models.SET_NULL, 
        null=True, blank=True,
        related_name='generated_expenses'
    )
    
    # Notes and metadata
    notes = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-expense_date']
        indexes = [
            models.Index(fields=['user', '-expense_date']),
            models.Index(fields=['category', '-expense_date']),
            models.Index(fields=['payment_method']),
            models.Index(fields=['project']),
        ]
    
    def __str__(self):
        return f"{self.expense_date.strftime('%Y-%m-%d')} - {self.description}: {self.amount} {self.currency}"


class FinancialGoal(models.Model):
    """Financial goals and savings targets"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='financial_goals')
    
    # Goal details
    name = models.CharField(max_length=100)
    description = models.TextField()
    goal_type = models.CharField(max_length=20, choices=[
        ('savings', 'Savings'),
        ('debt_payoff', 'Debt Payoff'),
        ('investment', 'Investment'),
        ('purchase', 'Purchase'),
        ('emergency_fund', 'Emergency Fund'),
        ('retirement', 'Retirement'),
        ('other', 'Other'),
    ])
    
    # Target amounts
    target_amount = models.DecimalField(max_digits=20, decimal_places=2)
    current_amount = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default='TRY')
    
    # Timeline
    start_date = models.DateField(default=timezone.now)
    target_date = models.DateField()
    
    # Progress tracking
    monthly_contribution = models.DecimalField(
        max_digits=20, decimal_places=2, 
        null=True, blank=True
    )
    
    # Priority and status
    priority = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)
    is_achieved = models.BooleanField(default=False)
    achieved_date = models.DateField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['priority', 'target_date']
    
    def __str__(self):
        return f"{self.name} - {self.progress_percentage:.1f}%"
    
    @property
    def progress_percentage(self):
        """Calculate progress percentage"""
        if self.target_amount == 0:
            return 0
        return (self.current_amount / self.target_amount) * 100
    
    @property
    def days_remaining(self):
        """Days until target date"""
        today = timezone.now().date()
        return (self.target_date - today).days
    
    @property
    def required_monthly_contribution(self):
        """Calculate required monthly contribution to reach goal"""
        if self.days_remaining <= 0:
            return Decimal('0')
        
        remaining_amount = self.target_amount - self.current_amount
        months_remaining = self.days_remaining / 30.44  # Average days per month
        
        if months_remaining <= 0:
            return remaining_amount
        
        return remaining_amount / Decimal(str(months_remaining))