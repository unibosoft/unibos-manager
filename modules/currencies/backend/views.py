"""
Advanced Currencies API Views with security and performance optimizations
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework.pagination import PageNumberPagination
from django.core.cache import cache
from django.db.models import Q, Sum, Avg, Count, F, Max, Min
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model
from decimal import Decimal
import logging
# import requests  # TODO: Install requests package
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import json
import hashlib

from .models import (
    Currency, ExchangeRate, CurrencyAlert,
    Portfolio, PortfolioHolding, Transaction,
    MarketData, BankExchangeRate, BankRateImportLog,
    PortfolioTransaction, PortfolioPerformance
)
from .serializers import (
    CurrencySerializer, ExchangeRateSerializer,
    CurrencyAlertSerializer, PortfolioSerializer,
    PortfolioHoldingSerializer, TransactionSerializer,
    MarketDataSerializer, PortfolioDetailSerializer,
    BankExchangeRateSerializer, BankRateComparisonSerializer,
    BankRateHistorySerializer, BankRateLatestSerializer,
    BankRateImportLogSerializer, BankRateExportSerializer
)
# from .services import CurrencyService, TCMBService, CoinGeckoService  # TODO: Fix services imports
from .permissions import IsOwnerOrReadOnly

logger = logging.getLogger(__name__)
User = get_user_model()


class CurrencyRateThrottle(UserRateThrottle):
    """Custom throttle for currency API"""
    rate = '100/hour'


class ConversionThrottle(UserRateThrottle):
    """Throttle for conversion API"""
    rate = '500/hour'


class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination for API responses"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class CurrencyViewSet(viewsets.ModelViewSet):
    """
    Currency CRUD operations with caching and rate limiting
    """
    queryset = Currency.objects.filter(is_active=True)
    serializer_class = CurrencySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    throttle_classes = [CurrencyRateThrottle]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Filter currencies based on query parameters"""
        queryset = super().get_queryset()
        
        # Filter by currency type
        currency_type = self.request.query_params.get('type')
        if currency_type:
            queryset = queryset.filter(currency_type=currency_type)
        
        # Search by code or name
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(code__icontains=search) |
                Q(name__icontains=search)
            )
        
        return queryset.order_by('code')
    
    @action(detail=False, methods=['get'])
    def rates(self, request):
        """
        Get current exchange rates with caching
        """
        base = request.query_params.get('base', 'TRY')
        targets = request.query_params.get('targets', '').split(',')
        
        # Generate cache key
        cache_key = f"rates:{base}:{','.join(sorted(targets))}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            logger.info(f"Returning cached rates for {cache_key}")
            return Response(cached_data)
        
        try:
            # Get latest rates
            rates = {}
            query = ExchangeRate.objects.filter(
                base_currency__code=base
            )
            
            if targets and targets[0]:
                query = query.filter(target_currency__code__in=targets)
            
            # Get latest rate for each pair
            latest_rates = {}
            for rate in query.order_by('target_currency', '-timestamp').distinct('target_currency'):
                latest_rates[rate.target_currency.code] = {
                    'rate': float(rate.rate),
                    'bid': float(rate.bid) if rate.bid else None,
                    'ask': float(rate.ask) if rate.ask else None,
                    'change_24h': float(rate.change_24h) if rate.change_24h else None,
                    'change_percentage_24h': float(rate.change_percentage_24h) if rate.change_percentage_24h else None,
                    'timestamp': rate.timestamp.isoformat(),
                    'source': rate.source
                }
            
            response_data = {
                'base': base,
                'rates': latest_rates,
                'timestamp': timezone.now().isoformat()
            }
            
            # Cache for 5 minutes
            cache.set(cache_key, response_data, 300)
            
            return Response(response_data)
            
        except Exception as e:
            logger.error(f"Error fetching rates: {str(e)}")
            return Response(
                {'error': 'Failed to fetch exchange rates'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def convert(self, request):
        """
        Convert between currencies with validation
        """
        from_currency = request.data.get('from_currency', '').upper()
        to_currency = request.data.get('to_currency', '').upper()
        amount = Decimal(str(request.data.get('amount', 0)))
        
        # Validate input
        if not from_currency or not to_currency:
            return Response(
                {'error': 'Both from_currency and to_currency are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if amount <= 0:
            return Response(
                {'error': 'Amount must be positive'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if amount > Decimal('1000000000'):  # 1 billion limit
            return Response(
                {'error': 'Amount exceeds maximum limit'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Direct conversion
            if from_currency == to_currency:
                converted_amount = amount
                rate = Decimal('1')
            else:
                # Try to get direct rate
                try:
                    latest_rate = ExchangeRate.objects.filter(
                        base_currency__code=from_currency,
                        target_currency__code=to_currency
                    ).latest('timestamp')
                    rate = latest_rate.rate
                    converted_amount = amount * rate
                except ExchangeRate.DoesNotExist:
                    # Try reverse rate
                    try:
                        reverse_rate = ExchangeRate.objects.filter(
                            base_currency__code=to_currency,
                            target_currency__code=from_currency
                        ).latest('timestamp')
                        rate = Decimal('1') / reverse_rate.rate
                        converted_amount = amount * rate
                    except ExchangeRate.DoesNotExist:
                        # Try through TRY as intermediate
                        to_try = ExchangeRate.objects.filter(
                            base_currency__code=from_currency,
                            target_currency__code='TRY'
                        ).latest('timestamp')
                        
                        from_try = ExchangeRate.objects.filter(
                            base_currency__code=to_currency,
                            target_currency__code='TRY'
                        ).latest('timestamp')
                        
                        rate = to_try.rate / from_try.rate
                        converted_amount = amount * rate
            
            return Response({
                'from_currency': from_currency,
                'to_currency': to_currency,
                'amount': float(amount),
                'converted_amount': float(converted_amount),
                'rate': float(rate),
                'timestamp': timezone.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Conversion error: {str(e)}")
            return Response(
                {'error': 'Conversion failed. Exchange rate not available.'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def update_rates(self, request):
        """
        Update exchange rates from external APIs (admin only)
        """
        if not request.user.is_staff:
            return Response(
                {'error': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # TODO: Fix service imports first
        return Response(
            {'error': 'Service temporarily unavailable - please install required packages'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """
        Get historical rates for a currency
        """
        currency = self.get_object()
        days = int(request.query_params.get('days', 30))
        interval = request.query_params.get('interval', '1d')
        
        # Limit days for performance
        days = min(days, 365)
        
        start_date = timezone.now() - timedelta(days=days)
        
        # Get historical rates
        rates = ExchangeRate.objects.filter(
            base_currency=currency,
            target_currency__code='TRY',
            timestamp__gte=start_date
        ).order_by('timestamp')
        
        # Aggregate by interval
        if interval == '1h':
            # Hourly data
            rates = rates.extra(
                select={'interval': "date_trunc('hour', timestamp)"}
            ).values('interval').annotate(
                avg_rate=Avg('rate'),
                high=Max('rate'),
                low=Min('rate'),
                volume=Sum('volume_24h')
            ).order_by('interval')
        elif interval == '1d':
            # Daily data
            rates = rates.extra(
                select={'interval': "date_trunc('day', timestamp)"}
            ).values('interval').annotate(
                avg_rate=Avg('rate'),
                high=Max('rate'),
                low=Min('rate'),
                volume=Sum('volume_24h')
            ).order_by('interval')
        
        return Response({
            'currency': currency.code,
            'base_currency': 'TRY',
            'period': f'{days} days',
            'interval': interval,
            'data': list(rates)
        })


class PortfolioViewSet(viewsets.ModelViewSet):
    """
    Portfolio management with advanced analytics and real-time crypto prices
    """
    serializer_class = PortfolioSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Get user portfolio (one per user)"""
        return Portfolio.objects.filter(
            user=self.request.user
        ).annotate(
            holdings_count=Count('holdings'),
            total_transactions=Count('portfolio_transactions')
        )
    
    def get_serializer_class(self):
        """Use detailed serializer for retrieve"""
        if self.action == 'retrieve':
            return PortfolioDetailSerializer
        return super().get_serializer_class()
    
    def perform_create(self, serializer):
        """Create or get portfolio for current user (one per user)"""
        # Get or create portfolio for user
        portfolio, created = Portfolio.objects.get_or_create(
            user=self.request.user,
            defaults=serializer.validated_data
        )
        if not created:
            # Update existing portfolio
            for attr, value in serializer.validated_data.items():
                setattr(portfolio, attr, value)
            portfolio.save()
    
    @action(detail=False, methods=['get'])
    def my_portfolio(self, request):
        """
        Get or create user's portfolio with real-time values
        """
        portfolio, created = Portfolio.objects.get_or_create(
            user=request.user,
            defaults={'name': f"{request.user.username}'s Portfolio"}
        )
        
        # Update real-time values
        from .real_crypto_service import crypto_service
        
        holdings_data = []
        for holding in portfolio.holdings.all():
            holdings_data.append({
                'symbol': holding.currency.code,
                'amount': float(holding.amount),
                'buy_price': float(holding.average_buy_price),
                'currency': 'USD'
            })
        
        portfolio_value = {'total_value': 0, 'holdings': []}
        if holdings_data:
            portfolio_value = crypto_service.calculate_portfolio_value(holdings_data, 'USD')
        
        # Get latest performance snapshot
        latest_performance = portfolio.performance_history.first()
        
        return Response({
            'portfolio': PortfolioSerializer(portfolio).data,
            'real_time_value': portfolio_value,
            'performance': {
                'daily_pnl': float(latest_performance.daily_pnl) if latest_performance else 0,
                'daily_pnl_percentage': float(latest_performance.daily_pnl_percentage) if latest_performance else 0,
                'weekly_pnl': float(latest_performance.weekly_pnl) if latest_performance else 0,
                'weekly_pnl_percentage': float(latest_performance.weekly_pnl_percentage) if latest_performance else 0,
                'monthly_pnl': float(latest_performance.monthly_pnl) if latest_performance else 0,
                'monthly_pnl_percentage': float(latest_performance.monthly_pnl_percentage) if latest_performance else 0,
                'yearly_pnl': float(latest_performance.yearly_pnl) if latest_performance else 0,
                'yearly_pnl_percentage': float(latest_performance.yearly_pnl_percentage) if latest_performance else 0,
            } if latest_performance else None
        })
    
    @action(detail=False, methods=['post'])
    def add_asset(self, request):
        """
        Add new asset to portfolio with real price fetching
        """
        portfolio, _ = Portfolio.objects.get_or_create(
            user=request.user,
            defaults={'name': f"{request.user.username}'s Portfolio"}
        )
        
        # Get parameters
        asset_type = request.data.get('asset_type', 'crypto')
        symbol = request.data.get('symbol', '').upper()
        amount = Decimal(str(request.data.get('amount', 0)))
        buy_price = request.data.get('buy_price')
        buy_date = request.data.get('buy_date')
        price_currency = request.data.get('price_currency', 'USD')
        
        # Validate
        if symbol not in ['BTC', 'ETH', 'AVAX']:
            return Response(
                {'error': 'Only BTC, ETH, and AVAX are supported'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if amount <= 0:
            return Response(
                {'error': 'Amount must be positive'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get or create currency
        currency, created = Currency.objects.get_or_create(
            code=symbol,
            defaults={
                'name': {'BTC': 'Bitcoin', 'ETH': 'Ethereum', 'AVAX': 'Avalanche'}.get(symbol, symbol),
                'symbol': symbol,
                'currency_type': 'crypto',
                'decimal_places': 8,
                'is_active': True
            }
        )
        
        # If no buy price provided, get current price
        if not buy_price:
            from .real_crypto_service import crypto_service
            prices = crypto_service.get_all_prices([symbol])
            if price_currency == 'TRY':
                buy_price = prices[symbol]['aggregated'].get('try_price', 0)
            else:
                buy_price = prices[symbol]['aggregated'].get('usd_price', 0)
        
        buy_price = Decimal(str(buy_price))
        
        if buy_price <= 0:
            return Response(
                {'error': 'Could not determine asset price'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create transaction
        with transaction.atomic():
            txn = PortfolioTransaction.objects.create(
                portfolio=portfolio,
                transaction_type='buy',
                currency=currency,
                amount=amount,
                price=buy_price,
                price_currency=price_currency,
                total_value=amount * buy_price,
                executed_at=buy_date if buy_date else timezone.now(),
                notes=f"Added via API: {symbol} @ {buy_price} {price_currency}"
            )
            
            # Get updated holding
            holding = PortfolioHolding.objects.get(
                portfolio=portfolio,
                currency=currency
            )
            
            # Capture performance snapshot
            PortfolioPerformance.capture_snapshot(portfolio)
            
            return Response({
                'transaction': {
                    'id': str(txn.id),
                    'type': txn.transaction_type,
                    'symbol': symbol,
                    'amount': float(txn.amount),
                    'price': float(txn.price),
                    'total_value': float(txn.total_value),
                    'currency': txn.price_currency
                },
                'holding': {
                    'symbol': holding.currency.code,
                    'total_amount': float(holding.amount),
                    'average_buy_price': float(holding.average_buy_price),
                    'total_invested': float(holding.total_invested)
                }
            }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'])
    def remove_asset(self, request):
        """
        Remove or reduce asset from portfolio
        """
        portfolio = Portfolio.objects.filter(user=request.user).first()
        if not portfolio:
            return Response(
                {'error': 'Portfolio not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        symbol = request.data.get('symbol', '').upper()
        amount = Decimal(str(request.data.get('amount', 0)))
        sell_price = request.data.get('sell_price')
        price_currency = request.data.get('price_currency', 'USD')
        
        # Validate
        if not symbol or amount <= 0:
            return Response(
                {'error': 'Valid symbol and positive amount required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            currency = Currency.objects.get(code=symbol)
            holding = PortfolioHolding.objects.get(
                portfolio=portfolio,
                currency=currency
            )
        except (Currency.DoesNotExist, PortfolioHolding.DoesNotExist):
            return Response(
                {'error': f'You do not have {symbol} in your portfolio'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if amount > holding.amount:
            return Response(
                {'error': f'Insufficient {symbol}. You have {holding.amount}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get current price if not provided
        if not sell_price:
            from .real_crypto_service import crypto_service
            prices = crypto_service.get_all_prices([symbol])
            if price_currency == 'TRY':
                sell_price = prices[symbol]['aggregated'].get('try_price', 0)
            else:
                sell_price = prices[symbol]['aggregated'].get('usd_price', 0)
        
        sell_price = Decimal(str(sell_price))
        
        # Create sell transaction
        with transaction.atomic():
            txn = PortfolioTransaction.objects.create(
                portfolio=portfolio,
                transaction_type='sell',
                currency=currency,
                amount=amount,
                price=sell_price,
                price_currency=price_currency,
                total_value=amount * sell_price,
                executed_at=timezone.now(),
                notes=f"Sold via API: {symbol} @ {sell_price} {price_currency}"
            )
            
            # Capture performance snapshot
            PortfolioPerformance.capture_snapshot(portfolio)
            
            return Response({
                'transaction': {
                    'id': str(txn.id),
                    'type': txn.transaction_type,
                    'symbol': symbol,
                    'amount': float(txn.amount),
                    'price': float(txn.price),
                    'total_value': float(txn.total_value),
                    'realized_pnl': float(txn.realized_pnl) if txn.realized_pnl else 0,
                    'currency': txn.price_currency
                },
                'remaining_holding': {
                    'symbol': holding.currency.code,
                    'amount': float(holding.amount),
                    'average_buy_price': float(holding.average_buy_price)
                } if holding.amount > 0 else None
            })
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get comprehensive portfolio statistics with P&L
        """
        portfolio = Portfolio.objects.filter(user=request.user).first()
        if not portfolio:
            return Response({'message': 'No portfolio found'})
        
        # Get or create today's performance snapshot
        performance = PortfolioPerformance.capture_snapshot(portfolio)
        
        from .real_crypto_service import portfolio_analytics
        
        # Get holdings for P&L calculation
        holdings_data = []
        for holding in portfolio.holdings.filter(amount__gt=0):
            holdings_data.append({
                'symbol': holding.currency.code,
                'amount': float(holding.amount),
                'buy_price': float(holding.average_buy_price),
                'currency': 'USD'
            })
        
        # Calculate detailed P&L
        pnl_data = portfolio_analytics.calculate_pnl(holdings_data) if holdings_data else None
        
        # Get transaction history metrics
        transactions = portfolio.portfolio_transactions.all()
        transaction_metrics = portfolio_analytics.calculate_performance_metrics([
            {
                'symbol': t.currency.code,
                'amount': float(t.amount),
                'price': float(t.price),
                'type': t.transaction_type,
                'date': t.executed_at
            } for t in transactions
        ]) if transactions else None
        
        return Response({
            'portfolio_id': str(portfolio.id),
            'current_performance': {
                'total_value_usd': float(performance.total_value_usd),
                'total_value_try': float(performance.total_value_try),
                'total_invested_usd': float(performance.total_invested_usd),
                'daily_pnl': float(performance.daily_pnl),
                'daily_pnl_percentage': float(performance.daily_pnl_percentage),
                'weekly_pnl': float(performance.weekly_pnl),
                'weekly_pnl_percentage': float(performance.weekly_pnl_percentage),
                'monthly_pnl': float(performance.monthly_pnl),
                'monthly_pnl_percentage': float(performance.monthly_pnl_percentage),
                'yearly_pnl': float(performance.yearly_pnl),
                'yearly_pnl_percentage': float(performance.yearly_pnl_percentage),
                'total_pnl': float(performance.total_pnl),
                'total_pnl_percentage': float(performance.total_pnl_percentage),
            },
            'holdings_pnl': pnl_data,
            'transaction_metrics': transaction_metrics,
            'last_updated': performance.snapshot_time
        })
    
    @action(detail=False, methods=['get'])
    def history(self, request):
        """
        Get historical portfolio performance
        """
        portfolio = Portfolio.objects.filter(user=request.user).first()
        if not portfolio:
            return Response({'message': 'No portfolio found'})
        
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now().date() - timedelta(days=days)
        
        history = PortfolioPerformance.objects.filter(
            portfolio=portfolio,
            snapshot_date__gte=start_date
        ).order_by('snapshot_date')
        
        return Response({
            'portfolio_id': str(portfolio.id),
            'period': f'{days} days',
            'data': [
                {
                    'date': h.snapshot_date,
                    'total_value_usd': float(h.total_value_usd),
                    'total_value_try': float(h.total_value_try),
                    'daily_pnl': float(h.daily_pnl),
                    'daily_pnl_percentage': float(h.daily_pnl_percentage),
                    'total_pnl': float(h.total_pnl),
                    'total_pnl_percentage': float(h.total_pnl_percentage)
                } for h in history
            ]
        })
    
    @action(detail=True, methods=['get'])
    def performance(self, request, pk=None):
        """
        Get portfolio performance analytics (kept for compatibility)
        """
        portfolio = self.get_object()
        period = request.query_params.get('period', '30d')
        
        # Parse period
        period_map = {
            '1d': 1,
            '7d': 7,
            '30d': 30,
            '90d': 90,
            '180d': 180,
            '365d': 365,
            '1y': 365,
            'all': None
        }
        
        days = period_map.get(period, 30)
        
        # Calculate performance metrics
        metrics = {
            'portfolio_id': portfolio.id,
            'portfolio_name': portfolio.name,
            'period': period,
            'total_value_try': float(portfolio.calculate_total_value('TRY')),
            'total_value_usd': float(portfolio.calculate_total_value('USD')),
            'holdings': []
        }
        
        # Get holdings performance
        for holding in portfolio.holdings.all():
            current_value = holding.get_current_value('TRY')
            if current_value:
                cost_basis = holding.amount * holding.average_buy_price
                profit_loss = current_value - cost_basis
                profit_loss_pct = (profit_loss / cost_basis * 100) if cost_basis > 0 else 0
                
                metrics['holdings'].append({
                    'currency': holding.currency.code,
                    'amount': float(holding.amount),
                    'avg_buy_price': float(holding.average_buy_price),
                    'current_value': float(current_value),
                    'cost_basis': float(cost_basis),
                    'profit_loss': float(profit_loss),
                    'profit_loss_percent': float(profit_loss_pct),
                    'allocation_percent': float(
                        (current_value / metrics['total_value_try'] * 100)
                        if metrics['total_value_try'] > 0 else 0
                    )
                })
        
        # Sort by allocation
        metrics['holdings'].sort(key=lambda x: x['allocation_percent'], reverse=True)
        
        # Calculate totals
        metrics['total_cost_basis'] = sum(h['cost_basis'] for h in metrics['holdings'])
        metrics['total_profit_loss'] = sum(h['profit_loss'] for h in metrics['holdings'])
        metrics['total_profit_loss_percent'] = (
            (metrics['total_profit_loss'] / metrics['total_cost_basis'] * 100)
            if metrics['total_cost_basis'] > 0 else 0
        )
        
        # Find best and worst performers
        if metrics['holdings']:
            metrics['best_performer'] = max(
                metrics['holdings'],
                key=lambda x: x['profit_loss_percent']
            )
            metrics['worst_performer'] = min(
                metrics['holdings'],
                key=lambda x: x['profit_loss_percent']
            )
        
        return Response(metrics)
    
    @action(detail=True, methods=['post'])
    def add_holding(self, request, pk=None):
        """
        Add or update a holding in portfolio
        """
        portfolio = self.get_object()
        
        currency_code = request.data.get('currency_code', '').upper()
        amount = Decimal(str(request.data.get('amount', 0)))
        avg_price = Decimal(str(request.data.get('average_buy_price', 0)))
        
        # Validate
        if not currency_code:
            return Response(
                {'error': 'Currency code is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if amount <= 0:
            return Response(
                {'error': 'Amount must be positive'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if avg_price <= 0:
            return Response(
                {'error': 'Average buy price must be positive'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            currency = Currency.objects.get(code=currency_code, is_active=True)
            
            with transaction.atomic():
                holding, created = PortfolioHolding.objects.get_or_create(
                    portfolio=portfolio,
                    currency=currency,
                    defaults={
                        'amount': amount,
                        'average_buy_price': avg_price
                    }
                )
                
                if not created:
                    # Update existing holding
                    total_cost = holding.amount * holding.average_buy_price
                    new_cost = amount * avg_price
                    new_amount = holding.amount + amount
                    
                    holding.amount = new_amount
                    holding.average_buy_price = (total_cost + new_cost) / new_amount
                    holding.save()
                
                # Create transaction record
                Transaction.objects.create(
                    portfolio=portfolio,
                    transaction_type='buy',
                    currency=currency,
                    amount=amount,
                    price=avg_price,
                    total_value=amount * avg_price,
                    executed_at=timezone.now()
                )
                
                serializer = PortfolioHoldingSerializer(holding)
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
                )
                
        except Currency.DoesNotExist:
            return Response(
                {'error': f'Currency {currency_code} not found'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error adding holding: {str(e)}")
            return Response(
                {'error': 'Failed to add holding'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def transactions(self, request, pk=None):
        """
        Get portfolio transactions with filtering
        """
        portfolio = self.get_object()
        
        # Filter parameters
        transaction_type = request.query_params.get('type')
        currency_code = request.query_params.get('currency')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        transactions = portfolio.transactions.all()
        
        if transaction_type:
            transactions = transactions.filter(transaction_type=transaction_type)
        
        if currency_code:
            transactions = transactions.filter(currency__code=currency_code.upper())
        
        if start_date:
            transactions = transactions.filter(executed_at__gte=start_date)
        
        if end_date:
            transactions = transactions.filter(executed_at__lte=end_date)
        
        # Paginate
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(transactions.order_by('-executed_at'), request)
        
        if page is not None:
            serializer = TransactionSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)


class CurrencyAlertViewSet(viewsets.ModelViewSet):
    """
    Price alert management
    """
    serializer_class = CurrencyAlertSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Get user alerts"""
        queryset = CurrencyAlert.objects.filter(user=self.request.user)
        
        # Filter by status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Filter by currency
        currency = self.request.query_params.get('currency')
        if currency:
            queryset = queryset.filter(
                Q(base_currency__code=currency.upper()) |
                Q(target_currency__code=currency.upper())
            )
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        """Create alert for current user"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def check_alerts(self, request):
        """
        Check and trigger alerts (called by background task)
        """
        if not request.user.is_staff:
            return Response(
                {'error': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        triggered_count = 0
        checked_count = 0
        
        try:
            active_alerts = CurrencyAlert.objects.filter(is_active=True)
            
            for alert in active_alerts:
                checked_count += 1
                
                # Get current rate
                try:
                    current_rate = ExchangeRate.objects.filter(
                        base_currency=alert.base_currency,
                        target_currency=alert.target_currency
                    ).latest('timestamp')
                    
                    if alert.check_condition(current_rate.rate):
                        # Trigger alert
                        alert.last_triggered = timezone.now()
                        alert.trigger_count += 1
                        alert.save()
                        
                        triggered_count += 1
                        
                        # Send notifications (implement based on your notification system)
                        if alert.notify_email:
                            # Send email notification
                            pass
                        
                        if alert.notify_push:
                            # Send push notification
                            pass
                        
                        if alert.notify_in_app:
                            # Create in-app notification
                            pass
                        
                        logger.info(f"Alert triggered: {alert.id}")
                
                except ExchangeRate.DoesNotExist:
                    logger.warning(f"No rate found for alert {alert.id}")
            
            return Response({
                'checked': checked_count,
                'triggered': triggered_count,
                'timestamp': timezone.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Alert check failed: {str(e)}")
            return Response(
                {'error': 'Alert check failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MarketDataViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Historical market data for charts
    """
    queryset = MarketData.objects.all()
    serializer_class = MarketDataSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Filter market data"""
        queryset = super().get_queryset()
        
        # Filter by currency pair
        pair = self.request.query_params.get('pair')
        if pair:
            queryset = queryset.filter(currency_pair=pair.upper())
        
        # Filter by interval
        interval = self.request.query_params.get('interval')
        if interval:
            queryset = queryset.filter(interval=interval)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        if start_date:
            queryset = queryset.filter(period_start__gte=start_date)
        
        end_date = self.request.query_params.get('end_date')
        if end_date:
            queryset = queryset.filter(period_end__lte=end_date)
        
        return queryset.order_by('-period_start')
    
    @action(detail=False, methods=['get'])
    def chart_data(self, request):
        """
        Get formatted chart data for frontend
        """
        pair = request.query_params.get('pair', 'USD/TRY')
        interval = request.query_params.get('interval', '1d')
        days = int(request.query_params.get('days', 30))
        
        start_date = timezone.now() - timedelta(days=days)
        
        data = self.get_queryset().filter(
            currency_pair=pair.upper(),
            interval=interval,
            period_start__gte=start_date
        ).order_by('period_start')
        
        # Format for chart library
        chart_data = {
            'labels': [],
            'datasets': [{
                'label': pair,
                'data': [],
                'borderColor': 'rgb(75, 192, 192)',
                'tension': 0.1
            }]
        }
        
        for item in data:
            chart_data['labels'].append(item.period_start.isoformat())
            chart_data['datasets'][0]['data'].append(float(item.close_price))
        
        return Response(chart_data)


class ChartDataViewSet(viewsets.ViewSet):
    """
    API endpoints for chart data with TradingView-style formatting
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    @action(detail=False, methods=['get'], url_path='ohlc/(?P<currency_pair>[^/]+)/(?P<timeframe>[^/]+)')
    def ohlc_data(self, request, currency_pair=None, timeframe=None):
        """
        Get OHLC (Open, High, Low, Close) data for candlestick charts
        
        Timeframes: 1H, 4H, 1D, 1W, 1M, 3M, 6M, 1Y, ALL
        Currency pairs: USDTRY, EURTRY, XAUTRY, etc.
        """
        from django.db.models import Max, Min, Avg
        from django.db.models.functions import TruncHour, TruncDay, TruncWeek, TruncMonth
        import pytz
        
        # Validate parameters
        valid_timeframes = ['1H', '4H', '1D', '1W', '1M', '3M', '6M', '1Y', 'ALL']
        if timeframe not in valid_timeframes:
            return Response(
                {'error': f'Invalid timeframe. Valid options: {", ".join(valid_timeframes)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        valid_pairs = ['USDTRY', 'EURTRY', 'XAUTRY', 'GBPTRY', 'CHFTRY', 'JPYTRY']
        if currency_pair not in valid_pairs:
            return Response(
                {'error': f'Invalid currency pair. Valid options: {", ".join(valid_pairs)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get bank filter
        bank = request.query_params.get('bank')
        
        # Cache key
        cache_key = f'chart:ohlc:{currency_pair}:{timeframe}:{bank or "all"}'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)
        
        # Determine date range
        istanbul_tz = pytz.timezone('Europe/Istanbul')
        end_date = timezone.now()
        
        if timeframe == '1H':
            start_date = end_date - timedelta(hours=24)
            interval = 'hour'
        elif timeframe == '4H':
            start_date = end_date - timedelta(hours=96)
            interval = '4hour'
        elif timeframe == '1D':
            start_date = end_date - timedelta(days=30)
            interval = 'day'
        elif timeframe == '1W':
            start_date = end_date - timedelta(weeks=12)
            interval = 'week'
        elif timeframe == '1M':
            start_date = end_date - timedelta(days=30)
            interval = 'day'
        elif timeframe == '3M':
            start_date = end_date - timedelta(days=90)
            interval = 'day'
        elif timeframe == '6M':
            start_date = end_date - timedelta(days=180)
            interval = 'day'
        elif timeframe == '1Y':
            start_date = end_date - timedelta(days=365)
            interval = 'day'
        else:  # ALL
            start_date = BankExchangeRate.objects.filter(
                currency_pair=currency_pair
            ).earliest('timestamp').timestamp
            interval = 'day'
        
        # Query data
        queryset = BankExchangeRate.objects.filter(
            currency_pair=currency_pair,
            timestamp__gte=start_date,
            timestamp__lte=end_date
        )
        
        if bank:
            queryset = queryset.filter(bank=bank)
        
        # Group and aggregate based on interval
        if interval == 'hour':
            queryset = queryset.annotate(
                period=TruncHour('timestamp')
            )
        elif interval == '4hour':
            # Custom 4-hour grouping
            queryset = queryset.extra(
                select={'period': "DATE_TRUNC('hour', timestamp) - INTERVAL '1 hour' * (EXTRACT(HOUR FROM timestamp)::INT % 4)"}
            )
        elif interval == 'day':
            queryset = queryset.annotate(
                period=TruncDay('timestamp')
            )
        elif interval == 'week':
            queryset = queryset.annotate(
                period=TruncWeek('timestamp')
            )
        elif interval == 'month':
            queryset = queryset.annotate(
                period=TruncMonth('timestamp')
            )
        
        # Aggregate OHLC data
        ohlc_data = []
        
        if interval != '4hour':
            grouped = queryset.values('period').annotate(
                open=Avg('buy_rate'),  # Using average as approximation
                high=Max('buy_rate'),
                low=Min('buy_rate'),
                close=Avg('buy_rate'),  # Last value would be better
                volume=Count('id')
            ).order_by('period')
        else:
            # Handle 4-hour grouping differently
            grouped = queryset.values('period').annotate(
                open=Avg('buy_rate'),
                high=Max('buy_rate'),
                low=Min('buy_rate'),
                close=Avg('buy_rate'),
                volume=Count('id')
            ).order_by('period')
        
        # Format for chart library
        for item in grouped:
            if item['period']:
                ohlc_data.append({
                    'time': item['period'].isoformat(),
                    'open': float(item['open'] or 0),
                    'high': float(item['high'] or 0),
                    'low': float(item['low'] or 0),
                    'close': float(item['close'] or 0),
                    'volume': item['volume']
                })
        
        result = {
            'currency_pair': currency_pair,
            'timeframe': timeframe,
            'bank': bank,
            'interval': interval,
            'data': ohlc_data,
            'count': len(ohlc_data)
        }
        
        # Cache for 5 minutes
        cache.set(cache_key, result, 300)
        
        return Response(result)
    
    @action(detail=False, methods=['get'], url_path='line/(?P<currency_pair>[^/]+)/(?P<timeframe>[^/]+)')
    def line_chart_data(self, request, currency_pair=None, timeframe=None):
        """
        Get line chart data for simple price visualization
        """
        import pytz
        
        # Validate parameters
        valid_timeframes = ['1H', '4H', '1D', '1W', '1M', '3M', '6M', '1Y', 'ALL']
        if timeframe not in valid_timeframes:
            return Response(
                {'error': f'Invalid timeframe. Valid options: {", ".join(valid_timeframes)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        valid_pairs = ['USDTRY', 'EURTRY', 'XAUTRY', 'GBPTRY', 'CHFTRY', 'JPYTRY']
        if currency_pair not in valid_pairs:
            return Response(
                {'error': f'Invalid currency pair. Valid options: {", ".join(valid_pairs)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get parameters
        bank = request.query_params.get('bank')
        rate_type = request.query_params.get('type', 'buy')  # buy or sell
        
        # Cache key
        cache_key = f'chart:line:{currency_pair}:{timeframe}:{bank or "all"}:{rate_type}'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)
        
        # Determine date range
        end_date = timezone.now()
        
        timeframe_map = {
            '1H': timedelta(hours=24),
            '4H': timedelta(hours=96),
            '1D': timedelta(days=30),
            '1W': timedelta(weeks=12),
            '1M': timedelta(days=30),
            '3M': timedelta(days=90),
            '6M': timedelta(days=180),
            '1Y': timedelta(days=365),
        }
        
        if timeframe != 'ALL':
            start_date = end_date - timeframe_map[timeframe]
        else:
            start_date = BankExchangeRate.objects.filter(
                currency_pair=currency_pair
            ).earliest('timestamp').timestamp
        
        # Query data
        queryset = BankExchangeRate.objects.filter(
            currency_pair=currency_pair,
            timestamp__gte=start_date,
            timestamp__lte=end_date
        )
        
        if bank:
            queryset = queryset.filter(bank=bank)
        
        # Get data points
        data_points = []
        rate_field = 'buy_rate' if rate_type == 'buy' else 'sell_rate'
        
        for item in queryset.order_by('timestamp'):
            data_points.append({
                'time': item.timestamp.isoformat(),
                'value': float(getattr(item, rate_field)),
                'bank': item.bank
            })
        
        result = {
            'currency_pair': currency_pair,
            'timeframe': timeframe,
            'bank': bank,
            'rate_type': rate_type,
            'data': data_points,
            'count': len(data_points)
        }
        
        # Cache for 5 minutes
        cache.set(cache_key, result, 300)
        
        return Response(result)
    
    @action(detail=False, methods=['get'], url_path='comparison/(?P<currency_pair>[^/]+)')
    def bank_comparison(self, request, currency_pair=None):
        """
        Compare rates across different banks
        """
        valid_pairs = ['USDTRY', 'EURTRY', 'XAUTRY', 'GBPTRY', 'CHFTRY', 'JPYTRY']
        if currency_pair not in valid_pairs:
            return Response(
                {'error': f'Invalid currency pair. Valid options: {", ".join(valid_pairs)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get date range
        days = int(request.query_params.get('days', 7))
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # Cache key
        cache_key = f'chart:comparison:{currency_pair}:{days}'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)
        
        # Get all banks
        banks = BankExchangeRate.objects.filter(
            currency_pair=currency_pair,
            timestamp__gte=start_date
        ).values_list('bank', flat=True).distinct()
        
        comparison_data = {}
        
        for bank in banks:
            rates = BankExchangeRate.objects.filter(
                bank=bank,
                currency_pair=currency_pair,
                timestamp__gte=start_date,
                timestamp__lte=end_date
            ).order_by('timestamp')
            
            comparison_data[bank] = {
                'buy_rates': [],
                'sell_rates': [],
                'spreads': []
            }
            
            for rate in rates:
                time_str = rate.timestamp.isoformat()
                comparison_data[bank]['buy_rates'].append({
                    'time': time_str,
                    'value': float(rate.buy_rate)
                })
                comparison_data[bank]['sell_rates'].append({
                    'time': time_str,
                    'value': float(rate.sell_rate)
                })
                if rate.spread:
                    comparison_data[bank]['spreads'].append({
                        'time': time_str,
                        'value': float(rate.spread)
                    })
        
        result = {
            'currency_pair': currency_pair,
            'days': days,
            'banks': list(banks),
            'data': comparison_data
        }
        
        # Cache for 5 minutes
        cache.set(cache_key, result, 300)
        
        return Response(result)
    
    @action(detail=False, methods=['get'], url_path='indicators/(?P<currency_pair>[^/]+)')
    def technical_indicators(self, request, currency_pair=None):
        """
        Calculate technical indicators (SMA, EMA, RSI, etc.)
        """
        import numpy as np
        from decimal import Decimal
        
        valid_pairs = ['USDTRY', 'EURTRY', 'XAUTRY', 'GBPTRY', 'CHFTRY', 'JPYTRY']
        if currency_pair not in valid_pairs:
            return Response(
                {'error': f'Invalid currency pair. Valid options: {", ".join(valid_pairs)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Parameters
        bank = request.query_params.get('bank')
        period = int(request.query_params.get('period', 14))
        indicator = request.query_params.get('indicator', 'sma')  # sma, ema, rsi
        
        # Get data
        end_date = timezone.now()
        start_date = end_date - timedelta(days=period * 3)  # Get extra data for calculations
        
        queryset = BankExchangeRate.objects.filter(
            currency_pair=currency_pair,
            timestamp__gte=start_date,
            timestamp__lte=end_date
        )
        
        if bank:
            queryset = queryset.filter(bank=bank)
        
        # Get prices
        prices = []
        timestamps = []
        
        for item in queryset.order_by('timestamp'):
            prices.append(float(item.buy_rate))
            timestamps.append(item.timestamp.isoformat())
        
        if len(prices) < period:
            return Response(
                {'error': f'Insufficient data for {period} period calculation'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calculate indicators
        result_data = []
        
        if indicator == 'sma':
            # Simple Moving Average
            sma_values = []
            for i in range(period - 1, len(prices)):
                sma = np.mean(prices[i - period + 1:i + 1])
                sma_values.append({
                    'time': timestamps[i],
                    'value': float(sma),
                    'price': prices[i]
                })
            result_data = sma_values
            
        elif indicator == 'ema':
            # Exponential Moving Average
            multiplier = 2 / (period + 1)
            ema_values = []
            
            # Start with SMA for first EMA value
            ema = np.mean(prices[:period])
            ema_values.append({
                'time': timestamps[period - 1],
                'value': float(ema),
                'price': prices[period - 1]
            })
            
            # Calculate EMA for remaining values
            for i in range(period, len(prices)):
                ema = (prices[i] * multiplier) + (ema * (1 - multiplier))
                ema_values.append({
                    'time': timestamps[i],
                    'value': float(ema),
                    'price': prices[i]
                })
            result_data = ema_values
            
        elif indicator == 'rsi':
            # Relative Strength Index
            deltas = np.diff(prices)
            seed = deltas[:period]
            up = seed[seed >= 0].sum() / period
            down = -seed[seed < 0].sum() / period
            rs = up / down if down != 0 else 100
            rsi_values = [{'time': timestamps[period], 'value': 100 - (100 / (1 + rs)), 'price': prices[period]}]
            
            for i in range(period, len(prices) - 1):
                delta = deltas[i]
                if delta > 0:
                    upval = delta
                    downval = 0
                else:
                    upval = 0
                    downval = -delta
                
                up = (up * (period - 1) + upval) / period
                down = (down * (period - 1) + downval) / period
                rs = up / down if down != 0 else 100
                rsi = 100 - (100 / (1 + rs))
                
                rsi_values.append({
                    'time': timestamps[i + 1],
                    'value': float(rsi),
                    'price': prices[i + 1]
                })
            result_data = rsi_values
        
        result = {
            'currency_pair': currency_pair,
            'bank': bank,
            'indicator': indicator,
            'period': period,
            'data': result_data
        }
        
        return Response(result)


class BankExchangeRateViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Bank exchange rates API with comparison and analysis features
    """
    queryset = BankExchangeRate.objects.all()
    serializer_class = BankExchangeRateSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination
    throttle_classes = [CurrencyRateThrottle]
    
    def get_queryset(self):
        """Filter bank rates with advanced querying"""
        queryset = super().get_queryset()
        
        # Filter by bank
        bank = self.request.query_params.get('bank')
        if bank:
            queryset = queryset.filter(bank=bank)
        
        # Filter by currency pair
        currency_pair = self.request.query_params.get('currency_pair')
        if currency_pair:
            queryset = queryset.filter(currency_pair=currency_pair.upper())
        
        # Filter by date
        date = self.request.query_params.get('date')
        if date:
            queryset = queryset.filter(date=date)
        
        # Date range filters
        start_date = self.request.query_params.get('start_date')
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        
        end_date = self.request.query_params.get('end_date')
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        # Filter for only latest rates per bank/currency
        latest_only = self.request.query_params.get('latest_only', '').lower() == 'true'
        if latest_only:
            # Get latest timestamp
            latest_timestamp = queryset.aggregate(Max('timestamp'))['timestamp__max']
            if latest_timestamp:
                queryset = queryset.filter(timestamp=latest_timestamp)
        
        return queryset.select_related().order_by('-timestamp', 'bank', 'currency_pair')
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
        """
        Get latest rates for all banks and currencies
        """
        cache_key = 'bank_rates:latest'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)
        
        try:
            # Get latest timestamp
            latest_timestamp = BankExchangeRate.objects.aggregate(
                Max('timestamp')
            )['timestamp__max']
            
            if not latest_timestamp:
                return Response({
                    'timestamp': None,
                    'rates': [],
                    'summary': {}
                })
            
            # Get all rates at latest timestamp
            latest_rates = BankExchangeRate.objects.filter(
                timestamp=latest_timestamp
            ).select_related()
            
            # Calculate summary statistics
            summary = {}
            for currency in ['USDTRY', 'EURTRY', 'XAUTRY', 'GBPTRY']:
                currency_rates = latest_rates.filter(currency_pair=currency)
                if currency_rates.exists():
                    summary[currency] = {
                        'avg_buy': float(currency_rates.aggregate(Avg('buy_rate'))['buy_rate__avg']),
                        'avg_sell': float(currency_rates.aggregate(Avg('sell_rate'))['sell_rate__avg']),
                        'min_buy': float(currency_rates.aggregate(Min('buy_rate'))['buy_rate__min']),
                        'max_sell': float(currency_rates.aggregate(Max('sell_rate'))['sell_rate__max']),
                        'best_buy_bank': currency_rates.order_by('buy_rate').first().bank,
                        'best_sell_bank': currency_rates.order_by('-sell_rate').first().bank,
                    }
            
            response_data = {
                'timestamp': latest_timestamp,
                'rates': BankExchangeRateSerializer(latest_rates, many=True).data,
                'summary': summary
            }
            
            # Cache for 1 minute
            cache.set(cache_key, response_data, 60)
            
            return Response(response_data)
            
        except Exception as e:
            logger.error(f"Error fetching latest bank rates: {str(e)}")
            return Response(
                {'error': 'Failed to fetch latest rates'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def compare(self, request):
        """
        Compare rates between banks for a specific date and currency
        """
        currency_pair = request.query_params.get('currency_pair', 'USDTRY').upper()
        date_str = request.query_params.get('date')
        
        if date_str:
            try:
                comparison_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'error': 'Invalid date format. Use YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            comparison_date = timezone.now().date()
        
        # Get rates for comparison
        rates = BankExchangeRate.objects.filter(
            currency_pair=currency_pair,
            date=comparison_date
        ).order_by('-timestamp', 'bank')
        
        if not rates.exists():
            return Response(
                {'error': f'No rates found for {currency_pair} on {comparison_date}'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get latest rates for each bank on that date
        bank_rates = {}
        for rate in rates:
            if rate.bank not in bank_rates:
                bank_rates[rate.bank] = rate
        
        # Calculate statistics
        buy_rates = [r.buy_rate for r in bank_rates.values()]
        sell_rates = [r.sell_rate for r in bank_rates.values()]
        
        comparison_data = {
            'currency_pair': currency_pair,
            'date': comparison_date,
            'banks': [
                {
                    'bank': bank,
                    'buy_rate': float(rate.buy_rate),
                    'sell_rate': float(rate.sell_rate),
                    'spread': float(rate.spread) if rate.spread else None,
                    'spread_percentage': float(rate.spread_percentage) if rate.spread_percentage else None,
                    'timestamp': rate.timestamp
                }
                for bank, rate in bank_rates.items()
            ],
            'best_buy': {
                'rate': float(min(buy_rates)),
                'bank': next(b for b, r in bank_rates.items() if r.buy_rate == min(buy_rates))
            },
            'best_sell': {
                'rate': float(max(sell_rates)),
                'bank': next(b for b, r in bank_rates.items() if r.sell_rate == max(sell_rates))
            },
            'average_buy': float(sum(buy_rates) / len(buy_rates)),
            'average_sell': float(sum(sell_rates) / len(sell_rates)),
            'spread_analysis': {
                'min_spread': float(min(r.spread for r in bank_rates.values() if r.spread)),
                'max_spread': float(max(r.spread for r in bank_rates.values() if r.spread)),
                'avg_spread': float(
                    sum(r.spread for r in bank_rates.values() if r.spread) / 
                    len([r for r in bank_rates.values() if r.spread])
                )
            }
        }
        
        return Response(comparison_data)
    
    @action(detail=False, methods=['get'])
    def history(self, request):
        """
        Get historical rates with aggregation options
        """
        # Required parameters
        currency_pair = request.query_params.get('currency_pair')
        if not currency_pair:
            return Response(
                {'error': 'currency_pair parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Optional parameters
        bank = request.query_params.get('bank')
        days = int(request.query_params.get('days', 30))
        aggregation = request.query_params.get('aggregation', 'daily')  # daily, hourly, none
        
        # Calculate date range
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Base query
        queryset = BankExchangeRate.objects.filter(
            currency_pair=currency_pair.upper(),
            date__range=[start_date, end_date]
        )
        
        if bank:
            queryset = queryset.filter(bank=bank)
        
        # Apply aggregation
        if aggregation == 'daily':
            # Get daily averages
            data_points = queryset.values('date', 'bank').annotate(
                avg_buy=Avg('buy_rate'),
                avg_sell=Avg('sell_rate'),
                min_buy=Min('buy_rate'),
                max_buy=Max('buy_rate'),
                min_sell=Min('sell_rate'),
                max_sell=Max('sell_rate'),
                count=Count('id')
            ).order_by('date', 'bank')
        elif aggregation == 'hourly':
            # Get hourly data
            from django.db.models import Func, DateTimeField
            
            class TruncHour(Func):
                function = 'date_trunc'
                template = "%(function)s('hour', %(expressions)s)"
                output_field = DateTimeField()
            
            data_points = queryset.annotate(
                hour=TruncHour('timestamp')
            ).values('hour', 'bank').annotate(
                avg_buy=Avg('buy_rate'),
                avg_sell=Avg('sell_rate'),
                min_buy=Min('buy_rate'),
                max_buy=Max('buy_rate'),
                min_sell=Min('sell_rate'),
                max_sell=Max('sell_rate'),
                count=Count('id')
            ).order_by('hour', 'bank')
        else:
            # No aggregation - raw data
            data_points = queryset.values(
                'timestamp', 'date', 'bank', 'buy_rate', 'sell_rate',
                'spread', 'spread_percentage', 'buy_change', 'sell_change',
                'buy_change_percentage', 'sell_change_percentage'
            ).order_by('timestamp', 'bank')
        
        # Calculate statistics
        statistics = {
            'period': f'{days} days',
            'start_date': start_date,
            'end_date': end_date,
            'total_records': queryset.count(),
            'avg_buy_rate': queryset.aggregate(Avg('buy_rate'))['buy_rate__avg'],
            'avg_sell_rate': queryset.aggregate(Avg('sell_rate'))['sell_rate__avg'],
            'min_buy_rate': queryset.aggregate(Min('buy_rate'))['buy_rate__min'],
            'max_buy_rate': queryset.aggregate(Max('buy_rate'))['buy_rate__max'],
            'min_sell_rate': queryset.aggregate(Min('sell_rate'))['sell_rate__min'],
            'max_sell_rate': queryset.aggregate(Max('sell_rate'))['sell_rate__max'],
        }
        
        response_data = {
            'bank': bank,
            'currency_pair': currency_pair.upper(),
            'start_date': start_date,
            'end_date': end_date,
            'data_points': list(data_points),
            'statistics': statistics
        }
        
        return Response(response_data)
    
    @action(detail=False, methods=['post'])
    def export(self, request):
        """
        Export bank rates to CSV or Excel
        """
        serializer = BankRateExportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        export_format = serializer.validated_data['format']
        start_date = serializer.validated_data.get('start_date')
        end_date = serializer.validated_data.get('end_date')
        banks = serializer.validated_data.get('banks', [])
        currency_pairs = serializer.validated_data.get('currency_pairs', [])
        include_statistics = serializer.validated_data.get('include_statistics', False)
        
        # Build query
        queryset = BankExchangeRate.objects.all()
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        if banks:
            queryset = queryset.filter(bank__in=banks)
        if currency_pairs:
            queryset = queryset.filter(currency_pair__in=currency_pairs)
        
        queryset = queryset.order_by('date', 'timestamp', 'bank', 'currency_pair')
        
        if export_format == 'json':
            # Return JSON response
            data = list(queryset.values(
                'date', 'timestamp', 'bank', 'currency_pair',
                'buy_rate', 'sell_rate', 'spread', 'spread_percentage'
            ))
            
            response_data = {
                'data': data,
                'count': len(data)
            }
            
            if include_statistics:
                response_data['statistics'] = {
                    'avg_buy': queryset.aggregate(Avg('buy_rate'))['buy_rate__avg'],
                    'avg_sell': queryset.aggregate(Avg('sell_rate'))['sell_rate__avg'],
                    'min_buy': queryset.aggregate(Min('buy_rate'))['buy_rate__min'],
                    'max_sell': queryset.aggregate(Max('sell_rate'))['sell_rate__max'],
                }
            
            return Response(response_data)
        
        elif export_format == 'csv':
            # Generate CSV
            import csv
            from django.http import HttpResponse
            
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="bank_rates_{timezone.now().date()}.csv"'
            
            writer = csv.writer(response)
            writer.writerow([
                'Date', 'Timestamp', 'Bank', 'Currency Pair',
                'Buy Rate', 'Sell Rate', 'Spread', 'Spread %'
            ])
            
            for rate in queryset:
                writer.writerow([
                    rate.date,
                    rate.timestamp,
                    rate.bank,
                    rate.currency_pair,
                    rate.buy_rate,
                    rate.sell_rate,
                    rate.spread,
                    rate.spread_percentage
                ])
            
            if include_statistics:
                writer.writerow([])
                writer.writerow(['Statistics'])
                writer.writerow(['Average Buy Rate', queryset.aggregate(Avg('buy_rate'))['buy_rate__avg']])
                writer.writerow(['Average Sell Rate', queryset.aggregate(Avg('sell_rate'))['sell_rate__avg']])
                writer.writerow(['Min Buy Rate', queryset.aggregate(Min('buy_rate'))['buy_rate__min']])
                writer.writerow(['Max Sell Rate', queryset.aggregate(Max('sell_rate'))['sell_rate__max']])
            
            return response
        
        elif export_format == 'excel':
            # Generate Excel file
            try:
                import openpyxl
                from openpyxl import Workbook
                from django.http import HttpResponse
                
                wb = Workbook()
                ws = wb.active
                ws.title = 'Bank Rates'
                
                # Headers
                headers = [
                    'Date', 'Timestamp', 'Bank', 'Currency Pair',
                    'Buy Rate', 'Sell Rate', 'Spread', 'Spread %'
                ]
                ws.append(headers)
                
                # Data
                for rate in queryset:
                    ws.append([
                        rate.date,
                        rate.timestamp,
                        rate.bank,
                        rate.currency_pair,
                        float(rate.buy_rate),
                        float(rate.sell_rate),
                        float(rate.spread) if rate.spread else None,
                        float(rate.spread_percentage) if rate.spread_percentage else None
                    ])
                
                # Statistics sheet
                if include_statistics:
                    stats_ws = wb.create_sheet('Statistics')
                    stats_ws.append(['Metric', 'Value'])
                    stats_ws.append(['Average Buy Rate', float(queryset.aggregate(Avg('buy_rate'))['buy_rate__avg'])])
                    stats_ws.append(['Average Sell Rate', float(queryset.aggregate(Avg('sell_rate'))['sell_rate__avg'])])
                    stats_ws.append(['Min Buy Rate', float(queryset.aggregate(Min('buy_rate'))['buy_rate__min'])])
                    stats_ws.append(['Max Sell Rate', float(queryset.aggregate(Max('sell_rate'))['sell_rate__max'])])
                
                # Save to response
                response = HttpResponse(
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                response['Content-Disposition'] = f'attachment; filename="bank_rates_{timezone.now().date()}.xlsx"'
                wb.save(response)
                
                return response
                
            except ImportError:
                return Response(
                    {'error': 'Excel export requires openpyxl package'},
                    status=status.HTTP_501_NOT_IMPLEMENTED
                )
    
    @action(detail=False, methods=['get'])
    def import_logs(self, request):
        """
        Get import logs (admin only)
        """
        if not request.user.is_staff:
            return Response(
                {'error': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        logs = BankRateImportLog.objects.all().order_by('-started_at')[:20]
        serializer = BankRateImportLogSerializer(logs, many=True)
        
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def banks(self, request):
        """
        Get list of available banks
        """
        cache_key = 'bank_rates:banks_list'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)
        
        try:
            # Get unique banks from the database
            banks = BankExchangeRate.objects.values_list('bank', flat=True).distinct()
            
            # Get bank info with latest rates count
            bank_info = []
            for bank in banks:
                latest_count = BankExchangeRate.objects.filter(
                    bank=bank,
                    timestamp__gte=timezone.now() - timedelta(hours=24)
                ).count()
                
                bank_info.append({
                    'name': bank,
                    'display_name': dict(BankExchangeRate.BANK_CHOICES).get(bank, bank),
                    'is_active': latest_count > 0,
                    'rates_24h': latest_count
                })
            
            response_data = {
                'banks': bank_info,
                'total': len(bank_info),
                'timestamp': timezone.now().isoformat()
            }
            
            # Cache for 5 minutes
            cache.set(cache_key, response_data, 300)
            
            return Response(response_data)
            
        except Exception as e:
            logger.error(f"Error fetching banks list: {str(e)}")
            return Response(
                {'error': 'Failed to fetch banks list'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def best_rates(self, request):
        """
        Get best buy/sell rates for all currency pairs
        """
        cache_key = 'bank_rates:best_rates'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)
        
        try:
            currency_pairs = request.query_params.getlist('pairs') or ['USDTRY', 'EURTRY', 'XAUTRY']
            best_rates = {}
            
            for pair in currency_pairs:
                # Get today's rates
                today = timezone.now().date()
                rates = BankExchangeRate.objects.filter(
                    currency_pair=pair,
                    date=today
                )
                
                if rates.exists():
                    # Find best rates
                    buy_rates = rates.order_by('buy_rate')
                    sell_rates = rates.order_by('-sell_rate')
                    
                    best_buy = buy_rates.first()
                    best_sell = sell_rates.first()
                    
                    best_rates[pair] = {
                        'best_buy': {
                            'bank': best_buy.bank,
                            'rate': float(best_buy.buy_rate),
                            'timestamp': best_buy.timestamp
                        } if best_buy else None,
                        'best_sell': {
                            'bank': best_sell.bank,
                            'rate': float(best_sell.sell_rate),
                            'timestamp': best_sell.timestamp
                        } if best_sell else None,
                        'average': {
                            'buy': float(rates.aggregate(Avg('buy_rate'))['buy_rate__avg']),
                            'sell': float(rates.aggregate(Avg('sell_rate'))['sell_rate__avg'])
                        },
                        'spread_analysis': {
                            'min': float(rates.aggregate(Min('spread_percentage'))['spread_percentage__min'] or 0),
                            'max': float(rates.aggregate(Max('spread_percentage'))['spread_percentage__max'] or 0),
                            'avg': float(rates.aggregate(Avg('spread_percentage'))['spread_percentage__avg'] or 0)
                        }
                    }
            
            response_data = {
                'pairs': best_rates,
                'timestamp': timezone.now().isoformat()
            }
            
            # Cache for 1 minute
            cache.set(cache_key, response_data, 60)
            
            return Response(response_data)
            
        except Exception as e:
            logger.error(f"Error fetching best rates: {str(e)}")
            return Response(
                {'error': 'Failed to fetch best rates'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def realtime_updates(self, request):
        """
        Get real-time rate updates (for websocket simulation)
        """
        try:
            # Get rates from last 5 minutes
            recent_time = timezone.now() - timedelta(minutes=5)
            recent_rates = BankExchangeRate.objects.filter(
                timestamp__gte=recent_time
            ).order_by('-timestamp')[:20]
            
            updates = []
            for rate in recent_rates:
                updates.append({
                    'bank': rate.bank,
                    'currency_pair': rate.currency_pair,
                    'buy_rate': float(rate.buy_rate),
                    'sell_rate': float(rate.sell_rate),
                    'buy_change': float(rate.buy_change) if rate.buy_change else 0,
                    'sell_change': float(rate.sell_change) if rate.sell_change else 0,
                    'timestamp': rate.timestamp.isoformat(),
                    'is_increase': (rate.buy_change and rate.buy_change > 0) if rate.buy_change else False
                })
            
            return Response({
                'updates': updates,
                'count': len(updates),
                'timestamp': timezone.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error fetching realtime updates: {str(e)}")
            return Response(
                {'error': 'Failed to fetch updates'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )