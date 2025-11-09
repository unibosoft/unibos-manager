"""
WIMM (Where Is My Money) Views
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q, Count
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from modules.core.backend.models import Account
from .models import (
    Transaction, TransactionCategory, Invoice, Budget,
    RecurringTransaction
)


def wimm_dashboard(request):
    """Main WIMM dashboard"""
    context = {
        'module_name': 'wimm - where is my money',
        'description': 'financial management system'
    }
    
    if request.user.is_authenticated:
        # Get user's accounts
        accounts = Account.objects.filter(user=request.user)
        
        # Calculate totals
        total_balance = accounts.aggregate(total=Sum('balance'))['total'] or Decimal('0')
        
        # Recent transactions
        recent_transactions = Transaction.objects.filter(
            user=request.user
        ).order_by('-transaction_date')[:10]
        
        # This month's summary
        today = timezone.now()
        month_start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        month_income = Transaction.objects.filter(
            user=request.user,
            transaction_type='income',
            transaction_date__gte=month_start
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        month_expense = Transaction.objects.filter(
            user=request.user,
            transaction_type='expense',
            transaction_date__gte=month_start
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        # Pending invoices
        pending_invoices = Invoice.objects.filter(
            user=request.user,
            payment_status__in=['pending', 'partial']
        ).count()
        
        # Active budgets
        active_budgets = Budget.objects.filter(
            user=request.user,
            start_date__lte=today,
            end_date__gte=today
        )
        
        context.update({
            'accounts': accounts,
            'total_balance': total_balance,
            'recent_transactions': recent_transactions,
            'month_income': month_income,
            'month_expense': month_expense,
            'month_net': month_income - month_expense,
            'pending_invoices': pending_invoices,
            'active_budgets': active_budgets,
        })
    
    return render(request, 'web_ui/modules/wimm.html', context)


def wimm_transactions(request):
    """Transaction list and management"""
    transactions = Transaction.objects.filter(user=request.user).order_by('-transaction_date')
    
    # Filters
    category_id = request.GET.get('category')
    account_id = request.GET.get('account')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if category_id:
        transactions = transactions.filter(category_id=category_id)
    if account_id:
        transactions = transactions.filter(
            Q(from_account_id=account_id) | Q(to_account_id=account_id)
        )
    if date_from:
        transactions = transactions.filter(transaction_date__gte=date_from)
    if date_to:
        transactions = transactions.filter(transaction_date__lte=date_to)
    
    context = {
        'transactions': transactions[:100],  # Limit to 100 for performance
        'categories': TransactionCategory.objects.all(),
        'accounts': Account.objects.filter(user=request.user),
    }
    
    return render(request, 'web_ui/modules/wimm_transactions.html', context)


def wimm_invoices(request):
    """Invoice management"""
    invoices = Invoice.objects.filter(user=request.user).order_by('-invoice_date')
    
    # Statistics
    total_pending = invoices.filter(
        payment_status__in=['pending', 'partial']
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
    
    overdue_count = sum(1 for inv in invoices if inv.is_overdue)
    
    context = {
        'invoices': invoices[:100],
        'total_pending': total_pending,
        'overdue_count': overdue_count,
    }
    
    return render(request, 'web_ui/modules/wimm_invoices.html', context)


def wimm_budgets(request):
    """Budget planning and tracking"""
    budgets = Budget.objects.filter(user=request.user).order_by('-start_date')
    
    # Add spent amounts and percentages
    budget_data = []
    for budget in budgets:
        budget_data.append({
            'budget': budget,
            'spent': budget.spent_amount,
            'remaining': budget.remaining_amount,
            'percentage': budget.spent_percentage,
            'is_over': budget.spent_percentage > 100,
            'is_warning': budget.spent_percentage > budget.alert_percentage,
        })
    
    context = {
        'budget_data': budget_data,
        'categories': TransactionCategory.objects.filter(type='expense'),
    }
    
    return render(request, 'web_ui/modules/wimm_budgets.html', context)


def wimm_accounts(request):
    """Account management"""
    accounts = Account.objects.filter(user=request.user)
    
    # Group by type
    account_groups = {}
    for account in accounts:
        account_type = account.get_account_type_display()
        if account_type not in account_groups:
            account_groups[account_type] = []
        account_groups[account_type].append(account)
    
    context = {
        'account_groups': account_groups,
        'total_balance': accounts.aggregate(total=Sum('balance'))['total'] or Decimal('0'),
    }
    
    return render(request, 'web_ui/modules/wimm_accounts.html', context)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_module_data(request):
    """Get financial data for current user via API"""
    user = request.user
    
    # Get accounts
    accounts = Account.objects.filter(user=user, is_active=True)
    
    # Get recent transactions
    recent_transactions = Transaction.objects.filter(
        user=user
    ).order_by('-transaction_date')[:10]
    
    # Get pending invoices
    pending_invoices = Invoice.objects.filter(
        user=user,
        payment_status='pending'
    ).order_by('-invoice_date')[:5]
    
    # Get active budgets
    active_budgets = Budget.objects.filter(
        user=user,
        is_active=True
    )
    
    # Calculate totals
    total_balance = sum(acc.balance for acc in accounts)
    
    return Response({
        'summary': {
            'total_accounts': accounts.count(),
            'total_balance': float(total_balance),
            'pending_invoices': pending_invoices.count(),
            'active_budgets': active_budgets.count(),
        },
        'accounts': [{
            'id': acc.id,
            'name': acc.name,
            'type': acc.account_type,
            'balance': float(acc.balance),
            'currency': acc.currency,
        } for acc in accounts],
        'recent_transactions': [{
            'id': t.id,
            'type': t.transaction_type,
            'amount': float(t.amount),
            'description': t.description,
            'date': t.transaction_date.isoformat(),
            'account': t.from_account.name if t.from_account else None,
        } for t in recent_transactions],
        'message': 'WIMM module loaded successfully'
    })