"""
Serializers for Currencies module
"""

from rest_framework import serializers
from decimal import Decimal
from django.db.models import Avg, Min, Max
from .models import (
    Currency, ExchangeRate, CurrencyAlert, Portfolio, 
    PortfolioHolding, Transaction, MarketData, BankExchangeRate,
    BankRateImportLog, CryptoExchangeRate
)


class CurrencySerializer(serializers.ModelSerializer):
    """Currency serializer"""
    
    class Meta:
        model = Currency
        fields = [
            'code', 'name', 'symbol', 'currency_type',
            'decimal_places', 'is_active', 'country_code',
            'icon_url', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ExchangeRateSerializer(serializers.ModelSerializer):
    """Exchange rate serializer"""
    base_currency = CurrencySerializer(read_only=True)
    target_currency = CurrencySerializer(read_only=True)
    base_currency_code = serializers.CharField(
        write_only=True, source='base_currency.code'
    )
    target_currency_code = serializers.CharField(
        write_only=True, source='target_currency.code'
    )
    
    class Meta:
        model = ExchangeRate
        fields = [
            'id', 'base_currency', 'target_currency',
            'base_currency_code', 'target_currency_code',
            'rate', 'bid', 'ask', 'volume_24h',
            'change_24h', 'change_percentage_24h',
            'source', 'timestamp', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def validate_rate(self, value):
        """Validate exchange rate"""
        if value <= 0:
            raise serializers.ValidationError("Rate must be positive")
        return value


class CurrencyAlertSerializer(serializers.ModelSerializer):
    """Currency alert serializer"""
    base_currency = CurrencySerializer(read_only=True)
    target_currency = CurrencySerializer(read_only=True)
    base_currency_code = serializers.CharField(
        write_only=True, source='base_currency.code'
    )
    target_currency_code = serializers.CharField(
        write_only=True, source='target_currency.code'
    )
    
    class Meta:
        model = CurrencyAlert
        fields = [
            'id', 'base_currency', 'target_currency',
            'base_currency_code', 'target_currency_code',
            'alert_type', 'threshold_value', 'is_active',
            'last_triggered', 'trigger_count',
            'notify_email', 'notify_push', 'notify_in_app',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'last_triggered', 'trigger_count',
            'created_at', 'updated_at'
        ]
    
    def validate(self, data):
        """Validate alert configuration"""
        if data.get('alert_type') == 'change_percent':
            threshold = data.get('threshold_value')
            if threshold is not None and (threshold < -100 or threshold > 1000):
                raise serializers.ValidationError(
                    "Percentage change must be between -100 and 1000"
                )
        return data


class PortfolioSerializer(serializers.ModelSerializer):
    """Portfolio serializer"""
    total_value = serializers.SerializerMethodField()
    holdings_count = serializers.IntegerField(
        source='holdings.count', read_only=True
    )
    
    class Meta:
        model = Portfolio
        fields = [
            'id', 'name', 'description', 'is_default',
            'is_public', 'total_value', 'holdings_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_total_value(self, obj):
        """Calculate total portfolio value"""
        return float(obj.calculate_total_value())
    
    def validate_name(self, value):
        """Validate portfolio name"""
        user = self.context['request'].user
        qs = Portfolio.objects.filter(user=user, name=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                "You already have a portfolio with this name"
            )
        return value


class PortfolioHoldingSerializer(serializers.ModelSerializer):
    """Portfolio holding serializer"""
    currency = CurrencySerializer(read_only=True)
    currency_code = serializers.CharField(
        write_only=True, source='currency.code'
    )
    current_value = serializers.SerializerMethodField()
    profit_loss = serializers.SerializerMethodField()
    profit_loss_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = PortfolioHolding
        fields = [
            'id', 'portfolio', 'currency', 'currency_code',
            'amount', 'average_buy_price', 'current_value',
            'profit_loss', 'profit_loss_percentage', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_current_value(self, obj):
        """Get current value of holding"""
        value = obj.get_current_value()
        return float(value) if value else None
    
    def get_profit_loss(self, obj):
        """Calculate profit/loss"""
        current_value = obj.get_current_value()
        if current_value:
            cost_basis = obj.amount * obj.average_buy_price
            return float(current_value - cost_basis)
        return None
    
    def get_profit_loss_percentage(self, obj):
        """Calculate profit/loss percentage"""
        current_value = obj.get_current_value()
        if current_value:
            cost_basis = obj.amount * obj.average_buy_price
            if cost_basis > 0:
                return float(((current_value - cost_basis) / cost_basis) * 100)
        return None
    
    def validate_amount(self, value):
        """Validate holding amount"""
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive")
        return value


class TransactionSerializer(serializers.ModelSerializer):
    """Transaction serializer"""
    currency = CurrencySerializer(read_only=True)
    currency_code = serializers.CharField(
        write_only=True, source='currency.code'
    )
    fee_currency = CurrencySerializer(read_only=True)
    fee_currency_code = serializers.CharField(
        write_only=True, source='fee_currency.code',
        required=False, allow_null=True
    )
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'portfolio', 'transaction_type',
            'currency', 'currency_code', 'amount',
            'price', 'total_value', 'fee_amount',
            'fee_currency', 'fee_currency_code',
            'notes', 'exchange', 'external_id',
            'executed_at', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def validate(self, data):
        """Validate transaction data"""
        if data.get('amount', 0) <= 0:
            raise serializers.ValidationError("Amount must be positive")
        if data.get('price', 0) <= 0:
            raise serializers.ValidationError("Price must be positive")
        
        # Calculate total value if not provided
        if 'total_value' not in data:
            data['total_value'] = data['amount'] * data['price']
        
        return data
    
    def create(self, validated_data):
        """Create transaction and update portfolio holdings"""
        transaction = super().create(validated_data)
        
        # Update portfolio holdings based on transaction type
        portfolio = transaction.portfolio
        currency = transaction.currency
        
        try:
            holding = PortfolioHolding.objects.get(
                portfolio=portfolio,
                currency=currency
            )
        except PortfolioHolding.DoesNotExist:
            holding = PortfolioHolding.objects.create(
                portfolio=portfolio,
                currency=currency,
                amount=Decimal('0'),
                average_buy_price=Decimal('0')
            )
        
        if transaction.transaction_type == 'buy':
            # Update holding amount and average price
            total_cost = holding.amount * holding.average_buy_price
            total_cost += transaction.total_value
            holding.amount += transaction.amount
            holding.average_buy_price = total_cost / holding.amount
            holding.save()
        elif transaction.transaction_type == 'sell':
            # Reduce holding amount
            holding.amount -= transaction.amount
            if holding.amount <= 0:
                holding.delete()
            else:
                holding.save()
        
        return transaction


class MarketDataSerializer(serializers.ModelSerializer):
    """Market data serializer"""
    
    class Meta:
        model = MarketData
        fields = [
            'id', 'currency_pair', 'open_price', 'high_price',
            'low_price', 'close_price', 'volume',
            'period_start', 'period_end', 'interval', 'source'
        ]
        read_only_fields = ['id']
    
    def validate(self, data):
        """Validate OHLCV data"""
        high = data.get('high_price')
        low = data.get('low_price')
        open_price = data.get('open_price')
        close = data.get('close_price')
        
        if high < low:
            raise serializers.ValidationError(
                "High price cannot be less than low price"
            )
        if high < open_price or high < close:
            raise serializers.ValidationError(
                "High price must be >= open and close prices"
            )
        if low > open_price or low > close:
            raise serializers.ValidationError(
                "Low price must be <= open and close prices"
            )
        
        return data


class PortfolioDetailSerializer(PortfolioSerializer):
    """Detailed portfolio serializer with holdings"""
    holdings = PortfolioHoldingSerializer(many=True, read_only=True)
    recent_transactions = serializers.SerializerMethodField()
    performance_24h = serializers.SerializerMethodField()
    performance_7d = serializers.SerializerMethodField()
    performance_30d = serializers.SerializerMethodField()
    
    class Meta(PortfolioSerializer.Meta):
        fields = PortfolioSerializer.Meta.fields + [
            'holdings', 'recent_transactions',
            'performance_24h', 'performance_7d', 'performance_30d'
        ]
    
    def get_recent_transactions(self, obj):
        """Get recent transactions"""
        transactions = obj.transactions.order_by('-executed_at')[:10]
        return TransactionSerializer(transactions, many=True).data
    
    def get_performance_24h(self, obj):
        """Calculate 24h performance"""
        # This would calculate actual performance based on historical data
        return {
            'value_change': 0.0,
            'percentage_change': 0.0
        }
    
    def get_performance_7d(self, obj):
        """Calculate 7d performance"""
        return {
            'value_change': 0.0,
            'percentage_change': 0.0
        }
    
    def get_performance_30d(self, obj):
        """Calculate 30d performance"""
        return {
            'value_change': 0.0,
            'percentage_change': 0.0
        }


class BankExchangeRateSerializer(serializers.ModelSerializer):
    """Bank exchange rate serializer"""
    bank_display = serializers.CharField(source='get_bank_display', read_only=True)
    currency_pair_display = serializers.CharField(source='get_currency_pair_display', read_only=True)
    
    class Meta:
        model = BankExchangeRate
        fields = [
            'id', 'entry_id', 'bank', 'bank_display', 
            'currency_pair', 'currency_pair_display',
            'buy_rate', 'sell_rate', 'spread', 'spread_percentage',
            'date', 'timestamp',
            'buy_change', 'sell_change', 
            'buy_change_percentage', 'sell_change_percentage',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'entry_id', 'spread', 'spread_percentage',
            'buy_change', 'sell_change',
            'buy_change_percentage', 'sell_change_percentage',
            'created_at', 'updated_at'
        ]


class BankRateComparisonSerializer(serializers.Serializer):
    """Serializer for comparing bank rates"""
    currency_pair = serializers.CharField()
    date = serializers.DateField()
    banks = serializers.ListField(
        child=serializers.DictField()
    )
    best_buy = serializers.DictField()
    best_sell = serializers.DictField()
    average_buy = serializers.DecimalField(max_digits=20, decimal_places=6)
    average_sell = serializers.DecimalField(max_digits=20, decimal_places=6)
    spread_analysis = serializers.DictField()


class BankRateHistorySerializer(serializers.Serializer):
    """Serializer for historical bank rates"""
    bank = serializers.CharField(required=False)
    currency_pair = serializers.CharField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    data_points = serializers.ListField(
        child=serializers.DictField()
    )
    statistics = serializers.DictField()


class BankRateLatestSerializer(serializers.Serializer):
    """Serializer for latest bank rates"""
    timestamp = serializers.DateTimeField()
    rates = serializers.ListField(
        child=BankExchangeRateSerializer()
    )
    summary = serializers.DictField()


class BankRateImportLogSerializer(serializers.ModelSerializer):
    """Bank rate import log serializer"""
    duration_formatted = serializers.SerializerMethodField()
    success_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = BankRateImportLog
        fields = [
            'id', 'import_type', 'total_entries', 'new_entries',
            'updated_entries', 'failed_entries', 'status',
            'error_message', 'error_details', 'started_at',
            'completed_at', 'duration_seconds', 'duration_formatted',
            'success_rate', 'source_url'
        ]
        read_only_fields = '__all__'
    
    def get_duration_formatted(self, obj):
        """Format duration in human-readable format"""
        if not obj.duration_seconds:
            return None
        
        seconds = obj.duration_seconds
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            minutes = seconds // 60
            secs = seconds % 60
            return f"{minutes}m {secs}s"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}h {minutes}m"
    
    def get_success_rate(self, obj):
        """Calculate success rate percentage"""
        if obj.total_entries == 0:
            return 0
        
        successful = obj.new_entries + obj.updated_entries
        return round((successful / obj.total_entries) * 100, 2)


class BankRateExportSerializer(serializers.Serializer):
    """Serializer for exporting bank rates"""
    format = serializers.ChoiceField(choices=['csv', 'excel', 'json'])
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    banks = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    currency_pairs = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    include_statistics = serializers.BooleanField(default=False)


class CryptoExchangeRateSerializer(serializers.ModelSerializer):
    """Serializer for cryptocurrency exchange rates"""
    spread = serializers.SerializerMethodField()
    spread_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = CryptoExchangeRate
        fields = [
            'id', 'exchange', 'symbol', 'base_asset', 'quote_asset',
            'last_price', 'bid_price', 'ask_price',
            'open_24h', 'high_24h', 'low_24h',
            'volume_24h', 'volume_24h_quote',
            'change_24h', 'change_percentage_24h',
            'market_cap', 'circulating_supply',
            'spread', 'spread_percentage',
            'timestamp', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'spread', 'spread_percentage']
    
    def get_spread(self, obj):
        """Calculate spread"""
        spread = obj.calculate_spread()
        return str(spread) if spread else None
    
    def get_spread_percentage(self, obj):
        """Calculate spread percentage"""
        spread_pct = obj.calculate_spread_percentage()
        return str(spread_pct) if spread_pct else None


class CryptoExchangeRateListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for crypto rate listings"""
    
    class Meta:
        model = CryptoExchangeRate
        fields = [
            'exchange', 'symbol', 'last_price',
            'change_percentage_24h', 'volume_24h_quote', 'timestamp'
        ]


class CryptoComparisonSerializer(serializers.Serializer):
    """Serializer for crypto exchange comparison"""
    symbol = serializers.CharField()
    exchanges = serializers.ListField(
        child=serializers.DictField()
    )
    best_bid = serializers.DecimalField(max_digits=20, decimal_places=8)
    best_bid_exchange = serializers.CharField()
    best_ask = serializers.DecimalField(max_digits=20, decimal_places=8)
    best_ask_exchange = serializers.CharField()
    average_price = serializers.DecimalField(max_digits=20, decimal_places=8)
    max_spread = serializers.DecimalField(max_digits=20, decimal_places=8)
    min_spread = serializers.DecimalField(max_digits=20, decimal_places=8)


class PortfolioDetailSerializerV2(serializers.ModelSerializer):
    """Enhanced portfolio serializer with crypto support"""
    holdings = serializers.SerializerMethodField()
    total_value = serializers.SerializerMethodField()
    total_pnl = serializers.SerializerMethodField()
    allocation = serializers.SerializerMethodField()
    performance_24h = serializers.SerializerMethodField()
    
    class Meta:
        model = Portfolio
        fields = [
            'id', 'name', 'description', 'is_default', 'is_public',
            'holdings', 'total_value', 'total_pnl', 'allocation',
            'performance_24h', 'created_at', 'updated_at'
        ]
    
    def get_holdings(self, obj):
        """Get detailed holdings with current values"""
        holdings_data = []
        for holding in obj.holdings.all():
            current_value = holding.get_current_value('TRY')
            holding_data = {
                'id': holding.id,
                'currency': holding.currency.code,
                'asset_type': holding.asset_type,
                'amount': str(holding.amount),
                'average_buy_price': str(holding.average_buy_price),
                'total_invested': str(holding.total_invested),
                'current_value': str(current_value) if current_value else None,
                'realized_pnl': str(holding.realized_pnl),
                'unrealized_pnl': str(holding.unrealized_pnl),
                'pnl_percentage': str(holding.get_pnl_percentage()),
            }
            holdings_data.append(holding_data)
        return holdings_data
    
    def get_total_value(self, obj):
        """Get total portfolio value"""
        return str(obj.calculate_total_value('TRY'))
    
    def get_total_pnl(self, obj):
        """Calculate total P&L"""
        total_realized = Decimal('0')
        total_unrealized = Decimal('0')
        
        for holding in obj.holdings.all():
            total_realized += holding.realized_pnl
            holding.calculate_unrealized_pnl('TRY')
            total_unrealized += holding.unrealized_pnl
        
        return {
            'realized': str(total_realized),
            'unrealized': str(total_unrealized),
            'total': str(total_realized + total_unrealized)
        }
    
    def get_allocation(self, obj):
        """Calculate portfolio allocation percentages"""
        allocations = {}
        total_value = obj.calculate_total_value('TRY')
        
        if total_value and total_value > 0:
            for holding in obj.holdings.all():
                current_value = holding.get_current_value('TRY')
                if current_value:
                    percentage = (current_value / total_value) * 100
                    allocations[holding.currency.code] = {
                        'value': str(current_value),
                        'percentage': str(round(percentage, 2))
                    }
        
        return allocations
    
    def get_performance_24h(self, obj):
        """Calculate 24h performance"""
        # This would need historical data to calculate properly
        # For now, return mock data
        return {
            'value_change': '0',
            'percentage_change': '0'
        }