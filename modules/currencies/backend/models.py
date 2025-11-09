"""
Currency models for UNIBOS
Handles real-time currency tracking and portfolio management
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import uuid

User = get_user_model()


class Currency(models.Model):
    """Currency definition and metadata"""
    code = models.CharField(max_length=10, primary_key=True)  # USD, EUR, BTC, etc.
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10)
    currency_type = models.CharField(
        max_length=20,
        choices=[
            ('fiat', 'Fiat Currency'),
            ('crypto', 'Cryptocurrency'),
            ('commodity', 'Commodity'),
        ]
    )
    
    # Metadata
    decimal_places = models.PositiveSmallIntegerField(default=2)
    is_active = models.BooleanField(default=True)
    
    # Additional info
    country_code = models.CharField(max_length=2, blank=True)  # For fiat currencies
    icon_url = models.URLField(blank=True)
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'currencies'
        verbose_name_plural = 'Currencies'
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class ExchangeRate(models.Model):
    """Exchange rates between currencies"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    base_currency = models.ForeignKey(
        Currency,
        on_delete=models.CASCADE,
        related_name='base_rates'
    )
    target_currency = models.ForeignKey(
        Currency,
        on_delete=models.CASCADE,
        related_name='target_rates'
    )
    
    # Rate information
    rate = models.DecimalField(max_digits=20, decimal_places=10)
    bid = models.DecimalField(max_digits=20, decimal_places=10, null=True, blank=True)
    ask = models.DecimalField(max_digits=20, decimal_places=10, null=True, blank=True)
    
    # Market data
    volume_24h = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    change_24h = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    change_percentage_24h = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    
    # Source information
    source = models.CharField(max_length=50)  # TCMB, CoinGecko, etc.
    
    # Timestamps
    timestamp = models.DateTimeField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'exchange_rates'
        indexes = [
            models.Index(fields=['base_currency', 'target_currency', 'timestamp']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['source', 'timestamp']),
        ]
        unique_together = ['base_currency', 'target_currency', 'timestamp', 'source']
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.base_currency}/{self.target_currency} @ {self.timestamp}"


class CurrencyAlert(models.Model):
    """User alerts for currency rate changes"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='currency_alerts')
    
    # Alert configuration
    base_currency = models.ForeignKey(
        Currency,
        on_delete=models.CASCADE,
        related_name='alert_base'
    )
    target_currency = models.ForeignKey(
        Currency,
        on_delete=models.CASCADE,
        related_name='alert_target'
    )
    
    # Alert conditions
    alert_type = models.CharField(
        max_length=20,
        choices=[
            ('above', 'Above'),
            ('below', 'Below'),
            ('change_percent', 'Change Percentage'),
        ]
    )
    threshold_value = models.DecimalField(max_digits=20, decimal_places=10)
    
    # Alert status
    is_active = models.BooleanField(default=True)
    last_triggered = models.DateTimeField(null=True, blank=True)
    trigger_count = models.PositiveIntegerField(default=0)
    
    # Notification preferences
    notify_email = models.BooleanField(default=True)
    notify_push = models.BooleanField(default=True)
    notify_in_app = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'currency_alerts'
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['base_currency', 'target_currency', 'is_active']),
        ]
    
    def __str__(self):
        return f"Alert: {self.base_currency}/{self.target_currency} {self.alert_type} {self.threshold_value}"
    
    def check_condition(self, current_rate):
        """Check if alert condition is met"""
        if self.alert_type == 'above':
            return current_rate > self.threshold_value
        elif self.alert_type == 'below':
            return current_rate < self.threshold_value
        elif self.alert_type == 'change_percent':
            # Need to calculate percentage change
            # This would require historical data
            pass
        return False


class Portfolio(models.Model):
    """User currency portfolio"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='portfolio')
    name = models.CharField(max_length=100, default='My Portfolio')
    description = models.TextField(blank=True)
    
    # Portfolio settings
    is_default = models.BooleanField(default=True)
    is_public = models.BooleanField(default=False)
    
    # Portfolio statistics (cached)
    total_value_usd = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    total_value_try = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    daily_pnl = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    daily_pnl_percentage = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_calculated = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'portfolios'
        indexes = [
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        return f"{self.user.username}'s {self.name}"
    
    def calculate_total_value(self, base_currency='TRY'):
        """Calculate total portfolio value in base currency using real prices"""
        from .real_crypto_service import crypto_service
        
        holdings_data = []
        for holding in self.holdings.all():
            holdings_data.append({
                'symbol': holding.currency.code,
                'amount': float(holding.amount)
            })
        
        if holdings_data:
            portfolio_value = crypto_service.calculate_portfolio_value(holdings_data, base_currency)
            return Decimal(str(portfolio_value['total_value']))
        return Decimal('0')


class PortfolioHolding(models.Model):
    """Individual currency holdings in a portfolio"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='holdings')
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    
    # Asset type
    ASSET_TYPE_CHOICES = [
        ('fiat', 'Fiat Currency'),
        ('crypto', 'Cryptocurrency'),
        ('commodity', 'Commodity'),
    ]
    asset_type = models.CharField(max_length=20, choices=ASSET_TYPE_CHOICES, default='fiat')
    
    # Holding details
    amount = models.DecimalField(max_digits=20, decimal_places=10)
    average_buy_price = models.DecimalField(max_digits=20, decimal_places=10)
    total_invested = models.DecimalField(max_digits=20, decimal_places=10, default=0)
    
    # P&L tracking
    realized_pnl = models.DecimalField(max_digits=20, decimal_places=10, default=0)
    unrealized_pnl = models.DecimalField(max_digits=20, decimal_places=10, default=0)
    
    # Metadata
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'portfolio_holdings'
        unique_together = ['portfolio', 'currency']
        indexes = [
            models.Index(fields=['portfolio', 'asset_type']),
        ]
    
    def __str__(self):
        return f"{self.amount} {self.currency.code} in {self.portfolio.name}"
    
    def get_current_value(self, base_currency='TRY'):
        """Get current value in base currency"""
        if self.currency.code == base_currency:
            return self.amount
        
        # Check crypto rates first if it's a crypto asset
        if self.asset_type == 'crypto':
            try:
                # Try to get crypto exchange rate
                crypto_rate = CryptoExchangeRate.objects.filter(
                    base_asset=self.currency.code,
                    quote_asset=base_currency
                ).latest('timestamp')
                return self.amount * crypto_rate.last_price
            except CryptoExchangeRate.DoesNotExist:
                pass
        
        # Fall back to regular exchange rates
        try:
            rate = ExchangeRate.objects.filter(
                base_currency=self.currency,
                target_currency__code=base_currency
            ).latest('timestamp')
            return self.amount * rate.rate
        except ExchangeRate.DoesNotExist:
            return None
    
    def calculate_unrealized_pnl(self, base_currency='TRY'):
        """Calculate unrealized P&L"""
        current_value = self.get_current_value(base_currency)
        if current_value and self.total_invested:
            self.unrealized_pnl = current_value - self.total_invested
            return self.unrealized_pnl
        return Decimal('0')
    
    def get_pnl_percentage(self):
        """Calculate P&L percentage"""
        if self.total_invested and self.total_invested > 0:
            total_pnl = self.realized_pnl + self.unrealized_pnl
            return (total_pnl / self.total_invested) * 100
        return Decimal('0')


class PortfolioTransaction(models.Model):
    """Track all portfolio transactions for P&L calculation"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='portfolio_transactions')
    
    # Transaction details
    transaction_type = models.CharField(
        max_length=10,
        choices=[
            ('buy', 'Buy'),
            ('sell', 'Sell'),
            ('deposit', 'Deposit'),
            ('withdraw', 'Withdraw'),
        ]
    )
    
    # Asset information
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=20, decimal_places=10)
    
    # Price information (in base currency at time of transaction)
    price = models.DecimalField(max_digits=20, decimal_places=10)
    price_currency = models.CharField(max_length=10, default='USD')  # USD, TRY, EUR
    total_value = models.DecimalField(max_digits=20, decimal_places=10)
    
    # Additional transaction costs
    fee_amount = models.DecimalField(max_digits=20, decimal_places=10, default=0)
    fee_currency = models.CharField(max_length=10, default='USD')
    
    # Exchange/source information
    exchange = models.CharField(max_length=50, blank=True)  # Binance, BTCTurk, etc.
    external_id = models.CharField(max_length=100, blank=True, unique=True, null=True)
    
    # P&L tracking
    realized_pnl = models.DecimalField(max_digits=20, decimal_places=10, default=0, null=True, blank=True)
    cost_basis = models.DecimalField(max_digits=20, decimal_places=10, null=True, blank=True)
    
    # Metadata
    notes = models.TextField(blank=True)
    executed_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'portfolio_transactions'
        indexes = [
            models.Index(fields=['portfolio', '-executed_at']),
            models.Index(fields=['currency', '-executed_at']),
            models.Index(fields=['-executed_at']),
            models.Index(fields=['external_id']),
        ]
        ordering = ['-executed_at']
    
    def __str__(self):
        return f"{self.transaction_type} {self.amount} {self.currency.code} @ {self.price}"
    
    def save(self, *args, **kwargs):
        """Calculate total value and update portfolio holding"""
        if not self.total_value:
            self.total_value = self.amount * self.price
        
        super().save(*args, **kwargs)
        
        # Update portfolio holding
        self.update_portfolio_holding()
    
    def update_portfolio_holding(self):
        """Update or create portfolio holding based on transaction"""
        holding, created = PortfolioHolding.objects.get_or_create(
            portfolio=self.portfolio,
            currency=self.currency,
            defaults={
                'amount': Decimal('0'),
                'average_buy_price': Decimal('0'),
                'total_invested': Decimal('0'),
                'asset_type': self.currency.currency_type
            }
        )
        
        if self.transaction_type == 'buy':
            # Update holding amount and average price
            new_total = holding.amount + self.amount
            if new_total > 0:
                new_invested = holding.total_invested + self.total_value
                holding.average_buy_price = new_invested / new_total
                holding.total_invested = new_invested
            holding.amount = new_total
            
        elif self.transaction_type == 'sell':
            # Calculate realized P&L
            if holding.amount > 0 and self.amount <= holding.amount:
                cost_basis = self.amount * holding.average_buy_price
                self.realized_pnl = self.total_value - cost_basis
                self.cost_basis = cost_basis
                
                # Update holding
                holding.amount -= self.amount
                holding.realized_pnl += self.realized_pnl
                
                if holding.amount > 0:
                    holding.total_invested = holding.amount * holding.average_buy_price
                else:
                    holding.total_invested = Decimal('0')
                    holding.average_buy_price = Decimal('0')
        
        holding.save()
        
        # Save realized P&L if calculated
        if self.realized_pnl is not None:
            super().save(update_fields=['realized_pnl', 'cost_basis'])


class PortfolioPerformance(models.Model):
    """Track portfolio performance over time"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='performance_history')
    
    # Snapshot date/time
    snapshot_date = models.DateField(db_index=True)
    snapshot_time = models.DateTimeField(db_index=True)
    
    # Portfolio value in different currencies
    total_value_usd = models.DecimalField(max_digits=20, decimal_places=2)
    total_value_try = models.DecimalField(max_digits=20, decimal_places=2)
    total_value_eur = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    
    # Cost basis
    total_invested_usd = models.DecimalField(max_digits=20, decimal_places=2)
    total_invested_try = models.DecimalField(max_digits=20, decimal_places=2)
    
    # P&L calculations
    daily_pnl = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    daily_pnl_percentage = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    
    weekly_pnl = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    weekly_pnl_percentage = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    
    monthly_pnl = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    monthly_pnl_percentage = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    
    yearly_pnl = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    yearly_pnl_percentage = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    
    total_pnl = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    total_pnl_percentage = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    
    # Holdings snapshot (JSON)
    holdings_snapshot = models.JSONField(default=dict)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'portfolio_performance'
        indexes = [
            models.Index(fields=['portfolio', '-snapshot_date']),
            models.Index(fields=['-snapshot_date']),
            models.Index(fields=['portfolio', '-snapshot_time']),
        ]
        unique_together = ['portfolio', 'snapshot_date']
        ordering = ['-snapshot_date']
    
    def __str__(self):
        return f"{self.portfolio.name} performance on {self.snapshot_date}"
    
    @classmethod
    def capture_snapshot(cls, portfolio):
        """Capture current portfolio performance snapshot"""
        from .real_crypto_service import crypto_service, portfolio_analytics
        
        # Get current holdings
        holdings_data = []
        for holding in portfolio.holdings.all():
            holdings_data.append({
                'symbol': holding.currency.code,
                'amount': float(holding.amount),
                'buy_price': float(holding.average_buy_price),
                'currency': 'USD'  # TODO: Get actual currency
            })
        
        # Calculate current values
        portfolio_value_usd = crypto_service.calculate_portfolio_value(holdings_data, 'USD')
        portfolio_value_try = crypto_service.calculate_portfolio_value(holdings_data, 'TRY')
        
        # Calculate P&L
        pnl_data = portfolio_analytics.calculate_pnl(holdings_data)
        
        # Get historical performance for comparisons
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        year_ago = today - timedelta(days=365)
        
        # Get previous snapshots
        yesterday_snapshot = cls.objects.filter(portfolio=portfolio, snapshot_date=yesterday).first()
        week_ago_snapshot = cls.objects.filter(portfolio=portfolio, snapshot_date=week_ago).first()
        month_ago_snapshot = cls.objects.filter(portfolio=portfolio, snapshot_date=month_ago).first()
        year_ago_snapshot = cls.objects.filter(portfolio=portfolio, snapshot_date=year_ago).first()
        
        # Calculate period P&L
        daily_pnl = daily_pnl_pct = weekly_pnl = weekly_pnl_pct = monthly_pnl = monthly_pnl_pct = yearly_pnl = yearly_pnl_pct = Decimal('0')
        
        current_value_usd = Decimal(str(portfolio_value_usd['total_value']))
        current_value_try = Decimal(str(portfolio_value_try['total_value']))
        
        if yesterday_snapshot:
            daily_pnl = current_value_usd - yesterday_snapshot.total_value_usd
            if yesterday_snapshot.total_value_usd > 0:
                daily_pnl_pct = (daily_pnl / yesterday_snapshot.total_value_usd) * 100
        
        if week_ago_snapshot:
            weekly_pnl = current_value_usd - week_ago_snapshot.total_value_usd
            if week_ago_snapshot.total_value_usd > 0:
                weekly_pnl_pct = (weekly_pnl / week_ago_snapshot.total_value_usd) * 100
        
        if month_ago_snapshot:
            monthly_pnl = current_value_usd - month_ago_snapshot.total_value_usd
            if month_ago_snapshot.total_value_usd > 0:
                monthly_pnl_pct = (monthly_pnl / month_ago_snapshot.total_value_usd) * 100
        
        if year_ago_snapshot:
            yearly_pnl = current_value_usd - year_ago_snapshot.total_value_usd
            if year_ago_snapshot.total_value_usd > 0:
                yearly_pnl_pct = (yearly_pnl / year_ago_snapshot.total_value_usd) * 100
        
        # Create or update today's snapshot
        snapshot, created = cls.objects.update_or_create(
            portfolio=portfolio,
            snapshot_date=today,
            defaults={
                'snapshot_time': timezone.now(),
                'total_value_usd': current_value_usd,
                'total_value_try': current_value_try,
                'total_invested_usd': Decimal(str(pnl_data['total_cost'])),
                'total_invested_try': Decimal(str(pnl_data['total_cost'])) * Decimal('30'),  # TODO: Use real exchange rate
                'daily_pnl': daily_pnl,
                'daily_pnl_percentage': daily_pnl_pct,
                'weekly_pnl': weekly_pnl,
                'weekly_pnl_percentage': weekly_pnl_pct,
                'monthly_pnl': monthly_pnl,
                'monthly_pnl_percentage': monthly_pnl_pct,
                'yearly_pnl': yearly_pnl,
                'yearly_pnl_percentage': yearly_pnl_pct,
                'total_pnl': Decimal(str(pnl_data['total_pnl'])),
                'total_pnl_percentage': Decimal(str(pnl_data['total_pnl_percentage'])),
                'holdings_snapshot': portfolio_value_usd['holdings']
            }
        )
        
        # Update portfolio cached values
        portfolio.total_value_usd = current_value_usd
        portfolio.total_value_try = current_value_try
        portfolio.daily_pnl = daily_pnl
        portfolio.daily_pnl_percentage = daily_pnl_pct
        portfolio.last_calculated = timezone.now()
        portfolio.save()
        
        return snapshot


class Transaction(models.Model):
    """Currency transactions (buy/sell)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='transactions')
    
    # Transaction details
    transaction_type = models.CharField(
        max_length=10,
        choices=[
            ('buy', 'Buy'),
            ('sell', 'Sell'),
            ('transfer', 'Transfer'),
        ]
    )
    
    # Currency information
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=20, decimal_places=10)
    price = models.DecimalField(max_digits=20, decimal_places=10)
    total_value = models.DecimalField(max_digits=20, decimal_places=10)
    
    # Fee information
    fee_amount = models.DecimalField(max_digits=20, decimal_places=10, default=0)
    fee_currency = models.ForeignKey(
        Currency,
        on_delete=models.CASCADE,
        related_name='fee_transactions',
        null=True,
        blank=True
    )
    
    # Metadata
    notes = models.TextField(blank=True)
    exchange = models.CharField(max_length=50, blank=True)  # Exchange name
    external_id = models.CharField(max_length=100, blank=True)  # External transaction ID
    
    # Timestamps
    executed_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'transactions'
        indexes = [
            models.Index(fields=['portfolio', 'executed_at']),
            models.Index(fields=['currency', 'executed_at']),
            models.Index(fields=['executed_at']),
        ]
        ordering = ['-executed_at']
    
    def __str__(self):
        return f"{self.transaction_type} {self.amount} {self.currency.code}"


class MarketData(models.Model):
    """Historical market data for analysis"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    currency_pair = models.CharField(max_length=20, db_index=True)  # e.g., "USD/TRY"
    
    # OHLCV data
    open_price = models.DecimalField(max_digits=20, decimal_places=10)
    high_price = models.DecimalField(max_digits=20, decimal_places=10)
    low_price = models.DecimalField(max_digits=20, decimal_places=10)
    close_price = models.DecimalField(max_digits=20, decimal_places=10)
    volume = models.DecimalField(max_digits=20, decimal_places=2)
    
    # Time period
    period_start = models.DateTimeField(db_index=True)
    period_end = models.DateTimeField()
    interval = models.CharField(
        max_length=10,
        choices=[
            ('1m', '1 Minute'),
            ('5m', '5 Minutes'),
            ('15m', '15 Minutes'),
            ('1h', '1 Hour'),
            ('4h', '4 Hours'),
            ('1d', '1 Day'),
            ('1w', '1 Week'),
        ]
    )
    
    # Source
    source = models.CharField(max_length=50)
    
    class Meta:
        db_table = 'market_data'
        indexes = [
            models.Index(fields=['currency_pair', 'interval', 'period_start']),
            models.Index(fields=['period_start']),
        ]
        unique_together = ['currency_pair', 'period_start', 'interval', 'source']
        ordering = ['-period_start']


class CryptoExchangeRate(models.Model):
    """Cryptocurrency exchange rates from multiple exchanges"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Exchange information
    EXCHANGE_CHOICES = [
        # International Crypto Exchanges
        ('Binance', 'Binance'),
        ('BinanceUS', 'Binance US'),
        ('Coinbase', 'Coinbase Pro'),
        ('Kraken', 'Kraken'),
        ('Bitfinex', 'Bitfinex'),
        ('Huobi', 'Huobi Global'),
        ('OKX', 'OKX'),
        ('KuCoin', 'KuCoin'),
        ('Bybit', 'Bybit'),
        
        # Turkish Crypto Exchanges
        ('BTCTurk', 'BTCTurk'),
        ('Paribu', 'Paribu'),
        ('BinanceTR', 'Binance TR'),
        ('Bitexen', 'Bitexen'),
        ('Thodex', 'Thodex'),
    ]
    exchange = models.CharField(max_length=50, choices=EXCHANGE_CHOICES, db_index=True)
    
    # Trading pair information
    symbol = models.CharField(max_length=20, db_index=True)  # BTC/USD, ETH/USD, BTC/TRY
    base_asset = models.CharField(max_length=10)  # BTC, ETH, etc.
    quote_asset = models.CharField(max_length=10)  # USD, TRY, EUR, etc.
    
    # Price information
    last_price = models.DecimalField(max_digits=20, decimal_places=8)
    bid_price = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    ask_price = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    
    # 24h statistics
    open_24h = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    high_24h = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    low_24h = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    volume_24h = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    volume_24h_quote = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    change_24h = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    change_percentage_24h = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Market cap for crypto (if available)
    market_cap = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    circulating_supply = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    
    # Timestamps
    timestamp = models.DateTimeField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'crypto_exchange_rates'
        indexes = [
            models.Index(fields=['exchange', 'symbol', '-timestamp']),
            models.Index(fields=['symbol', '-timestamp']),
            models.Index(fields=['base_asset', 'quote_asset', '-timestamp']),
            models.Index(fields=['-timestamp']),
        ]
        unique_together = ['exchange', 'symbol', 'timestamp']
        ordering = ['-timestamp', 'exchange', 'symbol']
    
    def __str__(self):
        return f"{self.exchange} - {self.symbol} @ {self.last_price}"
    
    def calculate_spread(self):
        """Calculate spread between bid and ask"""
        if self.bid_price and self.ask_price:
            return self.ask_price - self.bid_price
        return None
    
    def calculate_spread_percentage(self):
        """Calculate spread percentage"""
        spread = self.calculate_spread()
        if spread and self.bid_price and self.bid_price > 0:
            return (spread / self.bid_price) * 100
        return None


class BankExchangeRate(models.Model):
    """Bank exchange rates for currencies"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Firebase entry ID for tracking updates
    entry_id = models.CharField(max_length=100, unique=True, db_index=True)
    
    # Bank information
    BANK_CHOICES = [
        ('TCMB', 'T.C. Merkez Bankası'),
        ('Akbank', 'Akbank'),
        ('Garanti', 'Garanti'),
        ('YKB', 'Yapı Kredi'),
        ('Ziraat', 'Ziraat Bankası'),
        ('Halkbank', 'Halkbank'),
        ('Vakıfbank', 'Vakıfbank'),
        ('İşbank', 'İş Bankası'),
        ('ING', 'ING Bank'),
        ('QNB', 'QNB Finansbank'),
        ('Denizbank', 'Denizbank'),
        ('TEB', 'TEB'),
    ]
    bank = models.CharField(max_length=20, choices=BANK_CHOICES, db_index=True)
    
    # Currency pair
    CURRENCY_PAIR_CHOICES = [
        ('USDTRY', 'USD/TRY'),
        ('EURTRY', 'EUR/TRY'),
        ('XAUTRY', 'Gold/TRY'),
        ('GBPTRY', 'GBP/TRY'),
        ('CHFTRY', 'CHF/TRY'),
        ('JPYTRY', 'JPY/TRY'),
    ]
    currency_pair = models.CharField(max_length=10, choices=CURRENCY_PAIR_CHOICES, db_index=True)
    
    # Exchange rates
    buy_rate = models.DecimalField(max_digits=20, decimal_places=6)
    sell_rate = models.DecimalField(max_digits=20, decimal_places=6)
    
    # Spread calculation
    spread = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True)
    spread_percentage = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    
    # Date and time
    date = models.DateField(db_index=True)
    timestamp = models.DateTimeField(db_index=True)
    
    # Change tracking
    previous_buy_rate = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True)
    previous_sell_rate = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True)
    buy_change = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True)
    sell_change = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True)
    buy_change_percentage = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    sell_change_percentage = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'bank_exchange_rates'
        indexes = [
            models.Index(fields=['bank', 'currency_pair', 'date']),
            models.Index(fields=['currency_pair', 'date']),
            models.Index(fields=['date', 'bank']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['bank', 'currency_pair', '-timestamp']),
            models.Index(fields=['entry_id']),
        ]
        unique_together = ['bank', 'currency_pair', 'timestamp']
        ordering = ['-timestamp', 'bank', 'currency_pair']
    
    def __str__(self):
        return f"{self.bank} - {self.currency_pair} @ {self.timestamp}"
    
    def save(self, *args, **kwargs):
        """Calculate spread and change values before saving"""
        # Calculate spread
        if self.buy_rate and self.sell_rate:
            self.spread = self.sell_rate - self.buy_rate
            if self.buy_rate > 0:
                self.spread_percentage = (self.spread / self.buy_rate) * 100
        
        # Calculate changes if previous rates exist
        if self.previous_buy_rate and self.buy_rate:
            self.buy_change = self.buy_rate - self.previous_buy_rate
            if self.previous_buy_rate > 0:
                self.buy_change_percentage = (self.buy_change / self.previous_buy_rate) * 100
        
        if self.previous_sell_rate and self.sell_rate:
            self.sell_change = self.sell_rate - self.previous_sell_rate
            if self.previous_sell_rate > 0:
                self.sell_change_percentage = (self.sell_change / self.previous_sell_rate) * 100
        
        super().save(*args, **kwargs)
    
    @classmethod
    def get_latest_rates(cls, bank=None, currency_pair=None):
        """Get latest rates filtered by bank and/or currency pair"""
        queryset = cls.objects.all()
        if bank:
            queryset = queryset.filter(bank=bank)
        if currency_pair:
            queryset = queryset.filter(currency_pair=currency_pair)
        
        # Get latest timestamp
        latest = queryset.order_by('-timestamp').first()
        if latest:
            return queryset.filter(timestamp=latest.timestamp)
        return queryset.none()
    
    @classmethod
    def get_best_rates(cls, currency_pair, date=None):
        """Get best buy (lowest) and sell (highest) rates for a currency pair"""
        from django.db.models import Min, Max
        
        if date is None:
            date = timezone.now().date()
        
        rates = cls.objects.filter(
            currency_pair=currency_pair,
            date=date
        ).aggregate(
            best_buy=Min('buy_rate'),
            best_sell=Max('sell_rate')
        )
        
        best_buy_bank = None
        best_sell_bank = None
        
        if rates['best_buy']:
            best_buy_obj = cls.objects.filter(
                currency_pair=currency_pair,
                date=date,
                buy_rate=rates['best_buy']
            ).first()
            if best_buy_obj:
                best_buy_bank = best_buy_obj.bank
        
        if rates['best_sell']:
            best_sell_obj = cls.objects.filter(
                currency_pair=currency_pair,
                date=date,
                sell_rate=rates['best_sell']
            ).first()
            if best_sell_obj:
                best_sell_bank = best_sell_obj.bank
        
        return {
            'best_buy_rate': rates['best_buy'],
            'best_buy_bank': best_buy_bank,
            'best_sell_rate': rates['best_sell'],
            'best_sell_bank': best_sell_bank,
        }


class BankRateImportLog(models.Model):
    """Log for tracking bank rate imports"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Import details
    import_type = models.CharField(
        max_length=20,
        choices=[
            ('manual', 'Manual Import'),
            ('scheduled', 'Scheduled Task'),
            ('api', 'API Import'),
        ]
    )
    
    # Statistics
    total_entries = models.PositiveIntegerField(default=0)
    new_entries = models.PositiveIntegerField(default=0)
    updated_entries = models.PositiveIntegerField(default=0)
    failed_entries = models.PositiveIntegerField(default=0)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        default='pending'
    )
    
    # Error tracking
    error_message = models.TextField(blank=True)
    error_details = models.JSONField(default=dict, blank=True)
    
    # Timing
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.PositiveIntegerField(null=True, blank=True)
    
    # Source information
    source_url = models.URLField(blank=True)
    
    class Meta:
        db_table = 'bank_rate_import_logs'
        indexes = [
            models.Index(fields=['-started_at']),
            models.Index(fields=['status', '-started_at']),
        ]
        ordering = ['-started_at']
    
    def __str__(self):
        return f"Import {self.import_type} - {self.started_at}"