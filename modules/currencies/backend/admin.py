"""
Admin configuration for Currencies module
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from decimal import Decimal

from .models import (
    Currency, ExchangeRate, CurrencyAlert,
    Portfolio, PortfolioHolding, Transaction,
    MarketData, BankExchangeRate, BankRateImportLog
)


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = [
        'code', 'name', 'symbol', 'currency_type',
        'is_active', 'decimal_places', 'country_code',
        'created_at'
    ]
    list_filter = ['currency_type', 'is_active', 'created_at']
    search_fields = ['code', 'name', 'country_code']
    ordering = ['code']
    
    fieldsets = (
        (None, {
            'fields': ('code', 'name', 'symbol', 'currency_type')
        }),
        ('Details', {
            'fields': ('decimal_places', 'country_code', 'icon_url', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
    
    def has_delete_permission(self, request, obj=None):
        # Prevent accidental deletion of currencies
        if obj and obj.code in ['TRY', 'USD', 'EUR', 'BTC', 'ETH']:
            return False
        return super().has_delete_permission(request, obj)


@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = [
        'currency_pair', 'rate', 'bid', 'ask',
        'change_24h_display', 'source', 'timestamp'
    ]
    list_filter = ['source', 'timestamp', 'base_currency', 'target_currency']
    search_fields = ['base_currency__code', 'target_currency__code']
    date_hierarchy = 'timestamp'
    ordering = ['-timestamp']
    
    def currency_pair(self, obj):
        return f"{obj.base_currency.code}/{obj.target_currency.code}"
    currency_pair.short_description = 'Pair'
    
    def change_24h_display(self, obj):
        if obj.change_percentage_24h:
            color = 'green' if obj.change_percentage_24h > 0 else 'red'
            return format_html(
                '<span style="color: {};">{:+.2f}%</span>',
                color, obj.change_percentage_24h
            )
        return '-'
    change_24h_display.short_description = '24h Change'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'base_currency', 'target_currency'
        )


@admin.register(CurrencyAlert)
class CurrencyAlertAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'currency_pair', 'alert_type',
        'threshold_value', 'is_active', 'trigger_count',
        'last_triggered'
    ]
    list_filter = [
        'is_active', 'alert_type', 'notify_email',
        'notify_push', 'last_triggered'
    ]
    search_fields = [
        'user__username', 'user__email',
        'base_currency__code', 'target_currency__code'
    ]
    ordering = ['-created_at']
    
    def currency_pair(self, obj):
        return f"{obj.base_currency.code}/{obj.target_currency.code}"
    currency_pair.short_description = 'Pair'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user', 'base_currency', 'target_currency'
        )
    
    actions = ['activate_alerts', 'deactivate_alerts', 'reset_triggers']
    
    def activate_alerts(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} alerts activated.')
    activate_alerts.short_description = 'Activate selected alerts'
    
    def deactivate_alerts(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} alerts deactivated.')
    deactivate_alerts.short_description = 'Deactivate selected alerts'
    
    def reset_triggers(self, request, queryset):
        updated = queryset.update(
            trigger_count=0,
            last_triggered=None
        )
        self.message_user(request, f'{updated} alerts reset.')
    reset_triggers.short_description = 'Reset trigger counts'


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'user', 'is_default', 'is_public',
        'holdings_count', 'total_value_display',
        'created_at'
    ]
    list_filter = ['is_default', 'is_public', 'created_at']
    search_fields = ['name', 'user__username', 'user__email']
    ordering = ['-created_at']
    
    def holdings_count(self, obj):
        return obj.holdings.count()
    holdings_count.short_description = 'Holdings'
    
    def total_value_display(self, obj):
        try:
            value = obj.calculate_total_value('TRY')
            return format_html('₺{:,.2f}', value)
        except:
            return '-'
    total_value_display.short_description = 'Total Value (TRY)'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


class PortfolioHoldingInline(admin.TabularInline):
    model = PortfolioHolding
    extra = 0
    fields = [
        'currency', 'amount', 'average_buy_price',
        'current_value_display', 'profit_loss_display'
    ]
    readonly_fields = ['current_value_display', 'profit_loss_display']
    
    def current_value_display(self, obj):
        if obj.pk:
            value = obj.get_current_value('TRY')
            if value:
                return format_html('₺{:,.2f}', value)
        return '-'
    current_value_display.short_description = 'Current Value'
    
    def profit_loss_display(self, obj):
        if obj.pk:
            current = obj.get_current_value('TRY')
            if current:
                cost = obj.amount * obj.average_buy_price
                pl = current - cost
                color = 'green' if pl > 0 else 'red'
                return format_html(
                    '<span style="color: {};">₺{:,.2f}</span>',
                    color, pl
                )
        return '-'
    profit_loss_display.short_description = 'P/L'


@admin.register(PortfolioHolding)
class PortfolioHoldingAdmin(admin.ModelAdmin):
    list_display = [
        'portfolio', 'currency', 'amount',
        'average_buy_price', 'current_value_display',
        'profit_loss_display', 'updated_at'
    ]
    list_filter = ['portfolio', 'currency__currency_type', 'updated_at']
    search_fields = [
        'portfolio__name', 'currency__code',
        'currency__name', 'portfolio__user__username'
    ]
    ordering = ['-updated_at']
    
    def current_value_display(self, obj):
        value = obj.get_current_value('TRY')
        if value:
            return format_html('₺{:,.2f}', value)
        return '-'
    current_value_display.short_description = 'Current Value (TRY)'
    
    def profit_loss_display(self, obj):
        current = obj.get_current_value('TRY')
        if current:
            cost = obj.amount * obj.average_buy_price
            pl = current - cost
            pct = (pl / cost * 100) if cost > 0 else 0
            color = 'green' if pl > 0 else 'red'
            return format_html(
                '<span style="color: {};">₺{:,.2f} ({:+.2f}%)</span>',
                color, pl, pct
            )
        return '-'
    profit_loss_display.short_description = 'Profit/Loss'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'portfolio', 'currency', 'portfolio__user'
        )


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        'transaction_type', 'portfolio', 'currency',
        'amount', 'price', 'total_value',
        'fee_amount', 'executed_at'
    ]
    list_filter = [
        'transaction_type', 'executed_at',
        'currency__currency_type', 'exchange'
    ]
    search_fields = [
        'portfolio__name', 'currency__code',
        'portfolio__user__username', 'external_id',
        'notes'
    ]
    date_hierarchy = 'executed_at'
    ordering = ['-executed_at']
    
    fieldsets = (
        (None, {
            'fields': (
                'portfolio', 'transaction_type',
                'currency', 'amount', 'price', 'total_value'
            )
        }),
        ('Fees', {
            'fields': ('fee_amount', 'fee_currency')
        }),
        ('Additional Info', {
            'fields': ('exchange', 'external_id', 'notes', 'executed_at')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'portfolio', 'currency', 'fee_currency',
            'portfolio__user'
        )


@admin.register(MarketData)
class MarketDataAdmin(admin.ModelAdmin):
    list_display = [
        'currency_pair', 'interval', 'open_price',
        'high_price', 'low_price', 'close_price',
        'volume', 'period_start', 'source'
    ]
    list_filter = ['interval', 'source', 'period_start']
    search_fields = ['currency_pair']
    date_hierarchy = 'period_start'
    ordering = ['-period_start']
    
    def get_readonly_fields(self, request, obj=None):
        # Make all fields readonly for existing objects
        if obj:
            return self.fields or [f.name for f in self.model._meta.fields]
        return super().get_readonly_fields(request, obj)


@admin.register(BankExchangeRate)
class BankExchangeRateAdmin(admin.ModelAdmin):
    list_display = [
        'bank', 'currency_pair', 'buy_rate', 'sell_rate',
        'spread_display', 'change_display', 'date', 'timestamp'
    ]
    list_filter = ['bank', 'currency_pair', 'date']
    search_fields = ['bank', 'currency_pair', 'entry_id']
    date_hierarchy = 'date'
    ordering = ['-timestamp', 'bank', 'currency_pair']
    
    fieldsets = (
        ('Identification', {
            'fields': ('entry_id', 'bank', 'currency_pair')
        }),
        ('Rates', {
            'fields': (
                'buy_rate', 'sell_rate', 
                'spread', 'spread_percentage'
            )
        }),
        ('Changes', {
            'fields': (
                'previous_buy_rate', 'previous_sell_rate',
                'buy_change', 'sell_change',
                'buy_change_percentage', 'sell_change_percentage'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('date', 'timestamp', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = (
        'entry_id', 'spread', 'spread_percentage',
        'buy_change', 'sell_change',
        'buy_change_percentage', 'sell_change_percentage',
        'created_at', 'updated_at'
    )
    
    def spread_display(self, obj):
        if obj.spread:
            color = 'orange' if obj.spread_percentage > 5 else 'green'
            return format_html(
                '<span style="color: {};">{:.4f} ({:.2f}%)</span>',
                color, obj.spread, obj.spread_percentage
            )
        return '-'
    spread_display.short_description = 'Spread'
    
    def change_display(self, obj):
        if obj.buy_change_percentage:
            color = 'green' if obj.buy_change_percentage > 0 else 'red'
            return format_html(
                '<span style="color: {};">Buy: {:+.2f}%</span>',
                color, obj.buy_change_percentage
            )
        return '-'
    change_display.short_description = 'Change'
    
    actions = ['import_latest_rates']
    
    def import_latest_rates(self, request, queryset):
        from .tasks import import_bank_rates
        import_bank_rates.delay(import_type='manual')
        self.message_user(
            request, 
            'Bank rates import task has been queued. Check import logs for status.'
        )
    import_latest_rates.short_description = 'Import latest rates from Firebase'


@admin.register(BankRateImportLog)
class BankRateImportLogAdmin(admin.ModelAdmin):
    list_display = [
        'import_type', 'status', 'total_entries', 'new_entries',
        'failed_entries', 'success_rate_display', 'duration_display',
        'started_at'
    ]
    list_filter = ['status', 'import_type', 'started_at']
    search_fields = ['error_message']
    date_hierarchy = 'started_at'
    ordering = ['-started_at']
    
    fieldsets = (
        ('Import Info', {
            'fields': ('import_type', 'status', 'source_url')
        }),
        ('Statistics', {
            'fields': (
                'total_entries', 'new_entries', 
                'updated_entries', 'failed_entries'
            )
        }),
        ('Timing', {
            'fields': (
                'started_at', 'completed_at', 'duration_seconds'
            )
        }),
        ('Errors', {
            'fields': ('error_message', 'error_details'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = (
        'import_type', 'status', 'source_url',
        'total_entries', 'new_entries', 'updated_entries', 
        'failed_entries', 'started_at', 'completed_at',
        'duration_seconds', 'error_message', 'error_details'
    )
    
    def success_rate_display(self, obj):
        if obj.total_entries == 0:
            return '-'
        
        successful = obj.new_entries + obj.updated_entries
        rate = (successful / obj.total_entries) * 100
        
        if rate >= 95:
            color = 'green'
        elif rate >= 80:
            color = 'orange'
        else:
            color = 'red'
        
        return format_html(
            '<span style="color: {};">{:.1f}%</span>',
            color, rate
        )
    success_rate_display.short_description = 'Success Rate'
    
    def duration_display(self, obj):
        if not obj.duration_seconds:
            return '-'
        
        seconds = obj.duration_seconds
        if seconds < 60:
            return f'{seconds}s'
        elif seconds < 3600:
            minutes = seconds // 60
            secs = seconds % 60
            return f'{minutes}m {secs}s'
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f'{hours}h {minutes}m'
    duration_display.short_description = 'Duration'
    
    def has_add_permission(self, request):
        # Prevent manual creation of import logs
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Only allow deletion of failed imports
        if obj and obj.status == 'failed':
            return True
        return False