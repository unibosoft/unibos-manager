"""
WIMM (Where Is My Money) - Financial Management Module
Handles invoices, transactions, cash flow, and financial reporting
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
from apps.core.models import BaseModel, Item, Account


class TransactionCategory(BaseModel):
    """Categories for income/expense transactions"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    type = models.CharField(max_length=10, choices=[
        ('income', 'Income'),
        ('expense', 'Expense'),
        ('transfer', 'Transfer'),
    ])
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='subcategories')
    icon = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=7, default='#000000')  # Hex color
    
    class Meta:
        verbose_name_plural = "Transaction Categories"
        ordering = ['type', 'name']
    
    def __str__(self):
        return f"{self.get_type_display()}: {self.name}"


class Transaction(BaseModel):
    """Financial transactions"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions')
    
    # Transaction details
    transaction_type = models.CharField(max_length=10, choices=[
        ('income', 'Income'),
        ('expense', 'Expense'),
        ('transfer', 'Transfer'),
    ])
    
    # Accounts
    from_account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='outgoing_transactions', null=True, blank=True)
    to_account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='incoming_transactions', null=True, blank=True)
    
    # Payment method - Extended for credit cards
    payment_method = models.CharField(max_length=30, choices=[
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('digital_wallet', 'Digital Wallet'),
        ('crypto', 'Cryptocurrency'),
        ('other', 'Other'),
    ], default='cash')
    
    # Link to credit card if used
    credit_card = models.ForeignKey('documents.CreditCard', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Link to subscription if recurring
    subscription = models.ForeignKey('documents.Subscription', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Link to document/receipt
    source_document = models.ForeignKey('documents.Document', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Expense grouping
    expense_group = models.ForeignKey('documents.ExpenseGroup', on_delete=models.SET_NULL, null=True, blank=True)
    expense_category = models.ForeignKey('documents.ExpenseCategory', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Amount
    amount = models.DecimalField(max_digits=20, decimal_places=4)
    currency = models.CharField(max_length=3, default='TRY')
    exchange_rate = models.DecimalField(max_digits=20, decimal_places=6, default=1)  # For multi-currency
    
    # Category and description
    category = models.ForeignKey(TransactionCategory, on_delete=models.SET_NULL, null=True)
    description = models.TextField()
    
    # Date and time
    transaction_date = models.DateTimeField(default=timezone.now)
    
    # Reference to other models
    invoice = models.ForeignKey('Invoice', on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    
    # Tags for better organization
    tags = models.JSONField(default=list, blank=True)
    
    # Attachments/metadata
    attachments = models.JSONField(default=list, blank=True)  # List of file paths/URLs
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-transaction_date']
        indexes = [
            models.Index(fields=['user', '-transaction_date']),
            models.Index(fields=['category', '-transaction_date']),
        ]
    
    def __str__(self):
        return f"{self.transaction_date.strftime('%Y-%m-%d')} - {self.get_transaction_type_display()}: {self.amount} {self.currency}"
    
    def save(self, *args, **kwargs):
        """Update account balances on save"""
        if not self.pk:  # New transaction
            if self.transaction_type == 'expense' and self.from_account:
                self.from_account.balance -= Decimal(str(self.amount))
                self.from_account.save()
            elif self.transaction_type == 'income' and self.to_account:
                self.to_account.balance += Decimal(str(self.amount))
                self.to_account.save()
            elif self.transaction_type == 'transfer':
                if self.from_account:
                    self.from_account.balance -= Decimal(str(self.amount))
                    self.from_account.save()
                if self.to_account:
                    self.to_account.balance += Decimal(str(self.amount * self.exchange_rate))
                    self.to_account.save()
        super().save(*args, **kwargs)


class Invoice(BaseModel):
    """Invoices for tracking business transactions"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='invoices')
    
    # Invoice type
    invoice_type = models.CharField(max_length=20, choices=[
        ('sales', 'Sales Invoice'),
        ('purchase', 'Purchase Invoice'),
        ('proforma', 'Proforma Invoice'),
        ('credit_note', 'Credit Note'),
        ('debit_note', 'Debit Note'),
    ])
    
    # Invoice details
    invoice_number = models.CharField(max_length=50, unique=True)
    invoice_date = models.DateField(default=timezone.now)
    due_date = models.DateField()
    
    # Parties
    vendor_name = models.CharField(max_length=200)
    vendor_tax_id = models.CharField(max_length=50, blank=True)
    vendor_address = models.TextField(blank=True)
    
    customer_name = models.CharField(max_length=200)
    customer_tax_id = models.CharField(max_length=50, blank=True)
    customer_address = models.TextField(blank=True)
    
    # Amounts
    subtotal = models.DecimalField(max_digits=20, decimal_places=4)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=18)  # Turkish VAT
    tax_amount = models.DecimalField(max_digits=20, decimal_places=4)
    discount_amount = models.DecimalField(max_digits=20, decimal_places=4, default=0)
    total_amount = models.DecimalField(max_digits=20, decimal_places=4)
    currency = models.CharField(max_length=3, default='TRY')
    
    # Payment status
    payment_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('partial', 'Partially Paid'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ], default='pending')
    
    paid_amount = models.DecimalField(max_digits=20, decimal_places=4, default=0)
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Attachments
    attachments = models.JSONField(default=list, blank=True)
    
    class Meta:
        ordering = ['-invoice_date']
        indexes = [
            models.Index(fields=['invoice_number']),
            models.Index(fields=['user', '-invoice_date']),
            models.Index(fields=['payment_status']),
        ]
    
    def __str__(self):
        return f"{self.invoice_number} - {self.total_amount} {self.currency}"
    
    @property
    def is_overdue(self):
        return self.due_date < timezone.now().date() and self.payment_status not in ['paid', 'cancelled']


class InvoiceItem(BaseModel):
    """Line items in an invoice"""
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Item details (can be custom if item is null)
    description = models.CharField(max_length=500)
    quantity = models.DecimalField(max_digits=20, decimal_places=4)
    unit_price = models.DecimalField(max_digits=20, decimal_places=4)
    
    # Discounts and taxes
    discount_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=20, decimal_places=4, default=0)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=18)
    tax_amount = models.DecimalField(max_digits=20, decimal_places=4)
    
    # Total
    total = models.DecimalField(max_digits=20, decimal_places=4)
    
    class Meta:
        ordering = ['id']
    
    def __str__(self):
        return f"{self.description} x {self.quantity}"
    
    def save(self, *args, **kwargs):
        """Calculate totals before saving"""
        subtotal = self.quantity * self.unit_price
        self.discount_amount = subtotal * (self.discount_rate / 100)
        after_discount = subtotal - self.discount_amount
        self.tax_amount = after_discount * (self.tax_rate / 100)
        self.total = after_discount + self.tax_amount
        super().save(*args, **kwargs)


class Budget(BaseModel):
    """Budget planning and tracking"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='budgets')
    name = models.CharField(max_length=100)
    
    # Period
    period_type = models.CharField(max_length=20, choices=[
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
        ('custom', 'Custom'),
    ])
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Category-based budgeting
    category = models.ForeignKey(TransactionCategory, on_delete=models.CASCADE, null=True, blank=True)
    
    # Budget amount
    amount = models.DecimalField(max_digits=20, decimal_places=4)
    currency = models.CharField(max_length=3, default='TRY')
    
    # Alert settings
    alert_percentage = models.IntegerField(default=80)  # Alert when 80% spent
    
    class Meta:
        ordering = ['-start_date']
        unique_together = [['user', 'name', 'start_date']]
    
    def __str__(self):
        return f"{self.name} ({self.start_date} - {self.end_date})"
    
    @property
    def spent_amount(self):
        """Calculate spent amount for this budget period"""
        transactions = Transaction.objects.filter(
            user=self.user,
            transaction_type='expense',
            transaction_date__gte=self.start_date,
            transaction_date__lte=self.end_date
        )
        if self.category:
            transactions = transactions.filter(category=self.category)
        return transactions.aggregate(total=models.Sum('amount'))['total'] or Decimal('0')
    
    @property
    def remaining_amount(self):
        return self.amount - self.spent_amount
    
    @property
    def spent_percentage(self):
        if self.amount == 0:
            return 0
        return (self.spent_amount / self.amount) * 100


class RecurringTransaction(BaseModel):
    """Templates for recurring transactions"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recurring_transactions')
    name = models.CharField(max_length=100)
    
    # Base transaction details (copy from Transaction model)
    transaction_type = models.CharField(max_length=10, choices=[
        ('income', 'Income'),
        ('expense', 'Expense'),
    ])
    from_account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='recurring_outgoing', null=True, blank=True)
    to_account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='recurring_incoming', null=True, blank=True)
    amount = models.DecimalField(max_digits=20, decimal_places=4)
    currency = models.CharField(max_length=3, default='TRY')
    category = models.ForeignKey(TransactionCategory, on_delete=models.SET_NULL, null=True)
    description = models.TextField()
    
    # Recurrence pattern
    frequency = models.CharField(max_length=20, choices=[
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('biweekly', 'Bi-weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ])
    
    # Schedule
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    next_date = models.DateField()
    
    # Status
    is_active = models.BooleanField(default=True)
    last_created = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['next_date']
    
    def __str__(self):
        return f"{self.name} - {self.get_frequency_display()}"