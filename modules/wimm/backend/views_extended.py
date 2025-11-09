"""
Extended WIMM Views
REST API views for comprehensive financial management
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.db.models import Sum, Avg, Count, Q, F
from django.db import transaction as db_transaction
from django.utils import timezone
from django.core.cache import cache
from datetime import datetime, timedelta, date
from decimal import Decimal
import logging

from .models_extended import (
    CreditCard, Subscription, ExpenseCategory,
    ExpenseTag, Expense, FinancialGoal
)
from .serializers_extended import (
    CreditCardSerializer, CreditCardSummarySerializer,
    SubscriptionSerializer, SubscriptionCreateSerializer,
    ExpenseCategorySerializer, ExpenseTagSerializer,
    ExpenseSerializer, ExpenseCreateSerializer,
    FinancialGoalSerializer, FinancialDashboardSerializer
)

logger = logging.getLogger(__name__)


class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination for API results"""
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 100


class CreditCardViewSet(viewsets.ModelViewSet):
    """
    Credit Card Management API
    
    Endpoints:
    - GET /api/wimm/credit-cards/ - List all credit cards
    - POST /api/wimm/credit-cards/ - Create new credit card
    - GET /api/wimm/credit-cards/{id}/ - Get credit card details
    - PUT /api/wimm/credit-cards/{id}/ - Update credit card
    - DELETE /api/wimm/credit-cards/{id}/ - Delete credit card
    - POST /api/wimm/credit-cards/{id}/update-balance/ - Update card balance
    - GET /api/wimm/credit-cards/utilization-report/ - Get utilization report
    """
    serializer_class = CreditCardSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['card_nickname', 'issuing_bank', 'last_four_digits']
    ordering_fields = ['created_at', 'credit_limit', 'utilization_rate']
    ordering = ['-is_primary', '-created_at']
    
    def get_queryset(self):
        """Get user's credit cards"""
        return CreditCard.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Create credit card for current user"""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def update_balance(self, request, pk=None):
        """Update credit card balance"""
        card = self.get_object()
        new_balance = request.data.get('current_balance')
        
        if new_balance is None:
            return Response(
                {'error': 'current_balance is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            card.current_balance = Decimal(str(new_balance))
            card.save()
            serializer = self.get_serializer(card)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def utilization_report(self, request):
        """Get credit utilization report"""
        cards = self.get_queryset().filter(is_active=True)
        
        total_limit = cards.aggregate(total=Sum('credit_limit'))['total'] or Decimal('0')
        total_used = cards.aggregate(total=Sum('current_balance'))['total'] or Decimal('0')
        total_available = total_limit - total_used
        
        # Calculate average utilization
        if total_limit > 0:
            avg_utilization = (total_used / total_limit) * 100
        else:
            avg_utilization = 0
        
        # Get cards with high utilization (>70%)
        high_utilization_cards = []
        for card in cards:
            if card.utilization_rate > 70:
                high_utilization_cards.append({
                    'id': card.id,
                    'card_nickname': card.card_nickname,
                    'utilization_rate': card.utilization_rate,
                    'available_credit': card.available_credit
                })
        
        return Response({
            'total_credit_limit': total_limit,
            'total_used': total_used,
            'total_available': total_available,
            'average_utilization': avg_utilization,
            'cards_count': cards.count(),
            'high_utilization_cards': high_utilization_cards,
            'recommendations': self._get_credit_recommendations(avg_utilization, high_utilization_cards)
        })
    
    def _get_credit_recommendations(self, avg_utilization, high_util_cards):
        """Generate credit management recommendations"""
        recommendations = []
        
        if avg_utilization > 30:
            recommendations.append({
                'type': 'warning',
                'message': f'Your average credit utilization is {avg_utilization:.1f}%. Consider keeping it below 30% for better credit score.'
            })
        
        if high_util_cards:
            recommendations.append({
                'type': 'alert',
                'message': f'{len(high_util_cards)} cards have utilization above 70%. Pay down these balances to improve credit health.'
            })
        
        return recommendations


class SubscriptionViewSet(viewsets.ModelViewSet):
    """
    Subscription Management API
    
    Endpoints:
    - GET /api/wimm/subscriptions/ - List all subscriptions
    - POST /api/wimm/subscriptions/ - Create new subscription
    - GET /api/wimm/subscriptions/{id}/ - Get subscription details
    - PUT /api/wimm/subscriptions/{id}/ - Update subscription
    - DELETE /api/wimm/subscriptions/{id}/ - Delete subscription
    - POST /api/wimm/subscriptions/{id}/cancel/ - Cancel subscription
    - POST /api/wimm/subscriptions/{id}/renew/ - Renew subscription
    - GET /api/wimm/subscriptions/upcoming-payments/ - Get upcoming payments
    - GET /api/wimm/subscriptions/cost-analysis/ - Get subscription cost analysis
    """
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.OrderingFilter, filters.SearchFilter, filters.SearchFilter]
    search_fields = ['service_name', 'provider_name', 'plan_name']
    ordering_fields = ['next_billing_date', 'amount', 'created_at']
    ordering = ['next_billing_date']
    
    def get_queryset(self):
        """Get user's subscriptions with filtering"""
        queryset = Subscription.objects.filter(user=self.request.user)
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(service_category=category)
        
        # Filter by upcoming payments (next 7 days)
        upcoming = self.request.query_params.get('upcoming')
        if upcoming and upcoming.lower() == 'true':
            next_week = timezone.now().date() + timedelta(days=7)
            queryset = queryset.filter(
                next_billing_date__lte=next_week,
                is_active=True
            )
        
        return queryset.select_related('payment_method')
    
    def get_serializer_class(self):
        """Use different serializer for create action"""
        if self.action == 'create':
            return SubscriptionCreateSerializer
        return SubscriptionSerializer
    
    def perform_create(self, serializer):
        """Create subscription for current user"""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a subscription"""
        subscription = self.get_object()
        
        subscription.is_active = False
        subscription.cancellation_date = timezone.now().date()
        subscription.cancellation_reason = request.data.get('reason', '')
        subscription.save()
        
        serializer = self.get_serializer(subscription)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def renew(self, request, pk=None):
        """Renew a subscription"""
        subscription = self.get_object()
        
        # Calculate next billing date
        subscription.last_payment_date = timezone.now().date()
        subscription.next_billing_date = subscription.calculate_next_billing_date()
        subscription.is_active = True
        subscription.save()
        
        # Create expense record if requested
        if request.data.get('create_expense'):
            from .models_extended import Expense
            Expense.objects.create(
                user=request.user,
                description=f"Subscription: {subscription.service_name}",
                amount=subscription.amount,
                currency=subscription.currency,
                expense_date=timezone.now(),
                payment_method='credit_card' if subscription.payment_method else 'other',
                credit_card=subscription.payment_method,
                vendor_name=subscription.provider_name,
                subscription=subscription,
                is_business_expense=request.data.get('is_business', False)
            )
        
        serializer = self.get_serializer(subscription)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def upcoming_payments(self, request):
        """Get upcoming subscription payments"""
        days = int(request.query_params.get('days', 30))
        end_date = timezone.now().date() + timedelta(days=days)
        
        subscriptions = self.get_queryset().filter(
            is_active=True,
            next_billing_date__lte=end_date
        ).order_by('next_billing_date')
        
        # Group by date
        payments_by_date = {}
        total_amount = Decimal('0')
        
        for sub in subscriptions:
            date_str = sub.next_billing_date.strftime('%Y-%m-%d')
            if date_str not in payments_by_date:
                payments_by_date[date_str] = {
                    'date': date_str,
                    'subscriptions': [],
                    'total': Decimal('0')
                }
            
            payments_by_date[date_str]['subscriptions'].append({
                'id': sub.id,
                'service_name': sub.service_name,
                'amount': sub.amount,
                'currency': sub.currency
            })
            payments_by_date[date_str]['total'] += sub.amount
            total_amount += sub.amount
        
        return Response({
            'payments': list(payments_by_date.values()),
            'total_amount': total_amount,
            'subscription_count': subscriptions.count()
        })
    
    @action(detail=False, methods=['get'])
    def cost_analysis(self, request):
        """Analyze subscription costs"""
        subscriptions = self.get_queryset().filter(is_active=True)
        
        # Calculate costs by category
        category_costs = subscriptions.values('service_category').annotate(
            count=Count('id'),
            monthly_total=Sum(F('amount') * 12 / 365 * 30.44),  # Average monthly
            annual_total=Sum('annual_cost')
        ).order_by('-annual_total')
        
        # Calculate total costs
        total_monthly = sum(sub.amount for sub in subscriptions if sub.billing_cycle == 'monthly')
        total_annual = sum(sub.annual_cost for sub in subscriptions)
        
        # Find most expensive subscriptions
        expensive_subs = subscriptions.order_by('-amount')[:5]
        
        return Response({
            'total_active_subscriptions': subscriptions.count(),
            'total_monthly_cost': total_monthly,
            'total_annual_cost': total_annual,
            'average_subscription_cost': total_annual / subscriptions.count() if subscriptions else 0,
            'costs_by_category': category_costs,
            'most_expensive': SubscriptionSerializer(expensive_subs, many=True).data,
            'insights': self._get_subscription_insights(subscriptions, total_annual)
        })
    
    def _get_subscription_insights(self, subscriptions, total_annual):
        """Generate subscription insights"""
        insights = []
        
        # Check for duplicate services
        service_names = subscriptions.values_list('service_name', flat=True)
        duplicates = [name for name in service_names if list(service_names).count(name) > 1]
        if duplicates:
            insights.append({
                'type': 'warning',
                'message': f'You have duplicate subscriptions for: {", ".join(set(duplicates))}'
            })
        
        # Check for unused subscriptions (no expenses in last 30 days)
        unused_subs = []
        for sub in subscriptions:
            if not sub.generated_expenses.filter(
                expense_date__gte=timezone.now() - timedelta(days=30)
            ).exists():
                unused_subs.append(sub.service_name)
        
        if unused_subs:
            insights.append({
                'type': 'info',
                'message': f'Consider reviewing these potentially unused subscriptions: {", ".join(unused_subs[:3])}'
            })
        
        # Cost optimization suggestion
        if total_annual > 5000:  # Threshold in TRY
            insights.append({
                'type': 'tip',
                'message': f'Your annual subscription cost is {total_annual:.2f} TRY. Consider bundled services or annual plans for savings.'
            })
        
        return insights


class ExpenseViewSet(viewsets.ModelViewSet):
    """
    Expense Management API
    
    Endpoints:
    - GET /api/wimm/expenses/ - List all expenses
    - POST /api/wimm/expenses/ - Create new expense
    - GET /api/wimm/expenses/{id}/ - Get expense details
    - PUT /api/wimm/expenses/{id}/ - Update expense
    - DELETE /api/wimm/expenses/{id}/ - Delete expense
    - GET /api/wimm/expenses/summary/ - Get expense summary
    - GET /api/wimm/expenses/by-category/ - Get expenses grouped by category
    - POST /api/wimm/expenses/bulk-create/ - Create multiple expenses
    """
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['description', 'vendor_name', 'project', 'purpose']
    ordering_fields = ['expense_date', 'amount', 'created_at']
    ordering = ['-expense_date']
    
    def get_queryset(self):
        """Get user's expenses with filtering"""
        queryset = Expense.objects.filter(user=self.request.user)
        
        # Date range filter
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(expense_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(expense_date__lte=end_date)
        
        # Category filter
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # Payment method filter
        payment_method = self.request.query_params.get('payment_method')
        if payment_method:
            queryset = queryset.filter(payment_method=payment_method)
        
        # Project filter
        project = self.request.query_params.get('project')
        if project:
            queryset = queryset.filter(project=project)
        
        # Business expense filter
        is_business = self.request.query_params.get('is_business')
        if is_business is not None:
            queryset = queryset.filter(is_business_expense=is_business.lower() == 'true')
        
        return queryset.select_related('category', 'credit_card', 'subscription').prefetch_related('tags')
    
    def get_serializer_class(self):
        """Use different serializer for create action"""
        if self.action in ['create', 'bulk_create']:
            return ExpenseCreateSerializer
        return ExpenseSerializer
    
    def perform_create(self, serializer):
        """Create expense for current user"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get expense summary for date range"""
        # Get date range (default to current month)
        today = timezone.now().date()
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not start_date:
            start_date = today.replace(day=1)
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        
        if not end_date:
            end_date = today
        else:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # Get expenses in range
        expenses = self.get_queryset().filter(
            expense_date__gte=start_date,
            expense_date__lte=end_date
        )
        
        # Calculate summary
        summary = expenses.aggregate(
            total=Sum('amount'),
            count=Count('id'),
            avg=Avg('amount'),
            tax_total=Sum('tax_amount')
        )
        
        # Group by payment method
        by_payment = expenses.values('payment_method').annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('-total')
        
        # Group by day
        daily_expenses = expenses.values('expense_date').annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('expense_date')
        
        return Response({
            'period': {
                'start_date': start_date,
                'end_date': end_date
            },
            'summary': summary,
            'by_payment_method': by_payment,
            'daily_expenses': daily_expenses,
            'insights': self._get_expense_insights(expenses, summary)
        })
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get expenses grouped by category"""
        # Get date range
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        queryset = self.get_queryset()
        if start_date:
            queryset = queryset.filter(expense_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(expense_date__lte=end_date)
        
        # Group by category
        category_expenses = queryset.values(
            'category__id',
            'category__name',
            'category__color'
        ).annotate(
            total=Sum('amount'),
            count=Count('id'),
            avg=Avg('amount')
        ).order_by('-total')
        
        # Calculate percentages
        total_expenses = sum(cat['total'] for cat in category_expenses)
        for cat in category_expenses:
            cat['percentage'] = (cat['total'] / total_expenses * 100) if total_expenses else 0
        
        return Response({
            'categories': category_expenses,
            'total': total_expenses,
            'uncategorized': queryset.filter(category__isnull=True).aggregate(
                total=Sum('amount'),
                count=Count('id')
            )
        })
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """Create multiple expenses at once"""
        expenses_data = request.data.get('expenses', [])
        
        if not expenses_data:
            return Response(
                {'error': 'No expenses provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        created_expenses = []
        errors = []
        
        with db_transaction.atomic():
            for expense_data in expenses_data:
                serializer = ExpenseCreateSerializer(data=expense_data)
                if serializer.is_valid():
                    serializer.save(user=request.user)
                    created_expenses.append(serializer.data)
                else:
                    errors.append({
                        'data': expense_data,
                        'errors': serializer.errors
                    })
        
        return Response({
            'created': created_expenses,
            'errors': errors,
            'summary': {
                'created_count': len(created_expenses),
                'error_count': len(errors),
                'total_amount': sum(exp.get('amount', 0) for exp in created_expenses)
            }
        }, status=status.HTTP_201_CREATED if created_expenses else status.HTTP_400_BAD_REQUEST)
    
    def _get_expense_insights(self, expenses, summary):
        """Generate expense insights"""
        insights = []
        
        if not expenses:
            return insights
        
        # Compare to previous period
        period_days = (expenses.last().expense_date - expenses.first().expense_date).days + 1
        previous_start = expenses.first().expense_date - timedelta(days=period_days)
        previous_expenses = Expense.objects.filter(
            user=self.request.user,
            expense_date__gte=previous_start,
            expense_date__lt=expenses.first().expense_date
        )
        
        previous_total = previous_expenses.aggregate(total=Sum('amount'))['total'] or 0
        current_total = summary['total'] or 0
        
        if previous_total > 0:
            change = ((current_total - previous_total) / previous_total) * 100
            if abs(change) > 10:
                insights.append({
                    'type': 'info',
                    'message': f'Your expenses {"increased" if change > 0 else "decreased"} by {abs(change):.1f}% compared to previous period'
                })
        
        # Check for high single expenses
        if summary['avg'] and summary['total']:
            high_expenses = expenses.filter(amount__gt=summary['avg'] * 3)
            if high_expenses.exists():
                insights.append({
                    'type': 'warning',
                    'message': f'You have {high_expenses.count()} unusually high expenses'
                })
        
        return insights


class FinancialDashboardView(viewsets.ViewSet):
    """
    Financial Dashboard API
    
    Endpoints:
    - GET /api/wimm/dashboard/ - Get complete financial dashboard
    - GET /api/wimm/dashboard/insights/ - Get AI-powered insights
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get complete financial dashboard"""
        user = request.user
        today = timezone.now().date()
        
        # Cache key for dashboard
        cache_key = f'dashboard_{user.id}_{today}'
        cached_data = cache.get(cache_key)
        
        if cached_data and not request.query_params.get('refresh'):
            return Response(cached_data)
        
        # Credit Cards Summary
        credit_cards = CreditCard.objects.filter(user=user, is_active=True)
        total_limit = credit_cards.aggregate(Sum('credit_limit'))['credit_limit__sum'] or Decimal('0')
        total_used = credit_cards.aggregate(Sum('current_balance'))['current_balance__sum'] or Decimal('0')
        
        # Subscriptions Summary
        active_subs = Subscription.objects.filter(user=user, is_active=True)
        upcoming_subs = active_subs.filter(
            next_billing_date__lte=today + timedelta(days=7)
        ).order_by('next_billing_date')[:5]
        
        # Expenses Summary
        current_month_start = today.replace(day=1)
        previous_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
        
        current_expenses = Expense.objects.filter(
            user=user,
            expense_date__gte=current_month_start
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        previous_expenses = Expense.objects.filter(
            user=user,
            expense_date__gte=previous_month_start,
            expense_date__lt=current_month_start
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        # Top expense categories
        top_categories = Expense.objects.filter(
            user=user,
            expense_date__gte=current_month_start
        ).values('category__name').annotate(
            total=Sum('amount')
        ).order_by('-total')[:5]
        
        # Financial Goals
        active_goals = FinancialGoal.objects.filter(user=user, is_active=True)
        
        # Build dashboard data
        dashboard_data = {
            'credit_cards': {
                'total_limit': total_limit,
                'total_used': total_used,
                'total_available': total_limit - total_used,
                'average_utilization': (total_used / total_limit * 100) if total_limit else 0,
                'cards': CreditCardSummarySerializer(credit_cards, many=True).data
            },
            'subscriptions': {
                'active_count': active_subs.count(),
                'monthly_cost': sum(s.amount for s in active_subs if s.billing_cycle == 'monthly'),
                'annual_cost': sum(s.annual_cost for s in active_subs),
                'upcoming': SubscriptionSerializer(upcoming_subs, many=True).data
            },
            'expenses': {
                'current_month': current_expenses,
                'previous_month': previous_expenses,
                'trend': ((current_expenses - previous_expenses) / previous_expenses * 100) if previous_expenses else 0,
                'top_categories': top_categories,
                'recent': ExpenseSerializer(
                    Expense.objects.filter(user=user).order_by('-expense_date')[:10],
                    many=True
                ).data
            },
            'goals': {
                'active_count': active_goals.count(),
                'total_progress': active_goals.aggregate(
                    avg=Avg('progress_percentage')
                )['avg'] or 0,
                'goals': FinancialGoalSerializer(active_goals[:5], many=True).data
            },
            'insights': self._generate_insights(user),
            'last_updated': timezone.now()
        }
        
        # Cache for 1 hour
        cache.set(cache_key, dashboard_data, 3600)
        
        return Response(dashboard_data)
    
    def _generate_insights(self, user):
        """Generate AI-powered financial insights"""
        insights = []
        warnings = []
        recommendations = []
        
        # Check credit utilization
        cards = CreditCard.objects.filter(user=user, is_active=True)
        high_util_cards = [c for c in cards if c.utilization_rate > 70]
        if high_util_cards:
            warnings.append({
                'type': 'credit_utilization',
                'message': f'{len(high_util_cards)} credit cards have high utilization. Consider paying down balances.',
                'severity': 'high'
            })
        
        # Check upcoming subscriptions
        upcoming_subs = Subscription.objects.filter(
            user=user,
            is_active=True,
            next_billing_date__lte=timezone.now().date() + timedelta(days=3)
        )
        if upcoming_subs.exists():
            insights.append({
                'type': 'upcoming_payments',
                'message': f'{upcoming_subs.count()} subscriptions will be charged in the next 3 days',
                'amount': sum(s.amount for s in upcoming_subs)
            })
        
        # Spending pattern analysis
        today = timezone.now().date()
        this_month_expenses = Expense.objects.filter(
            user=user,
            expense_date__month=today.month,
            expense_date__year=today.year
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        last_month = today.replace(day=1) - timedelta(days=1)
        last_month_expenses = Expense.objects.filter(
            user=user,
            expense_date__month=last_month.month,
            expense_date__year=last_month.year
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        if last_month_expenses and this_month_expenses > last_month_expenses * 1.2:
            warnings.append({
                'type': 'spending_increase',
                'message': 'Your spending this month is 20% higher than last month',
                'severity': 'medium'
            })
        
        # Goal recommendations
        goals = FinancialGoal.objects.filter(user=user, is_active=True)
        behind_goals = [g for g in goals if g.progress_percentage < 50 and g.days_remaining < 180]
        if behind_goals:
            recommendations.append({
                'type': 'goal_adjustment',
                'message': f'{len(behind_goals)} financial goals may need attention to meet targets'
            })
        
        return {
            'insights': insights,
            'warnings': warnings,
            'recommendations': recommendations
        }