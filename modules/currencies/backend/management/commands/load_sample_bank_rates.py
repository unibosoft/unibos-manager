"""
Load sample bank exchange rates for testing
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from datetime import datetime, timedelta
import random
import uuid

from modules.currencies.backend.models import BankExchangeRate, Currency


class Command(BaseCommand):
    help = 'Load sample bank exchange rates for testing'

    def handle(self, *args, **options):
        self.stdout.write('Loading sample bank exchange rates...')
        
        # Ensure base currencies exist
        currencies_to_create = [
            ('TRY', 'Turkish Lira', '₺', 'fiat'),
            ('USD', 'US Dollar', '$', 'fiat'),
            ('EUR', 'Euro', '€', 'fiat'),
            ('GBP', 'British Pound', '£', 'fiat'),
            ('XAU', 'Gold (Ounce)', '🏅', 'commodity'),
        ]
        
        for code, name, symbol, currency_type in currencies_to_create:
            Currency.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'symbol': symbol,
                    'currency_type': currency_type,
                    'decimal_places': 2 if currency_type == 'fiat' else 4,
                    'is_active': True
                }
            )
        
        # Bank configurations
        banks = ['Akbank', 'Garanti', 'YKB']
        
        # Currency pairs with base rates and volatility
        pairs = {
            'USDTRY': {'base_buy': 32.45, 'base_sell': 32.55, 'volatility': 0.02},
            'EURTRY': {'base_buy': 35.12, 'base_sell': 35.25, 'volatility': 0.03},
            'GBPTRY': {'base_buy': 41.23, 'base_sell': 41.40, 'volatility': 0.025},
            'XAUTRY': {'base_buy': 2150.00, 'base_sell': 2170.00, 'volatility': 0.01},
        }
        
        # Generate rates for the last 7 days
        now = timezone.now()
        rates_created = 0
        
        for days_ago in range(7, -1, -1):
            current_date = now - timedelta(days=days_ago)
            
            # Generate multiple rates per day (simulating updates every 4 hours)
            for hour in [0, 4, 8, 12, 16, 20]:
                timestamp = current_date.replace(hour=hour, minute=0, second=0, microsecond=0)
                
                for bank in banks:
                    for pair, config in pairs.items():
                        # Add some randomness to rates
                        bank_adjustment = random.uniform(-0.01, 0.01)  # Bank-specific adjustment
                        time_adjustment = random.uniform(-config['volatility'], config['volatility'])
                        
                        buy_rate = Decimal(str(config['base_buy'] * (1 + bank_adjustment + time_adjustment)))
                        sell_rate = Decimal(str(config['base_sell'] * (1 + bank_adjustment + time_adjustment)))
                        
                        # Ensure sell > buy
                        if sell_rate <= buy_rate:
                            sell_rate = buy_rate + Decimal('0.05')
                        
                        # Generate unique entry_id
                        entry_id = f"{bank}_{pair}_{timestamp.strftime('%Y%m%d%H%M%S')}"
                        
                        # Check if rate already exists
                        existing = BankExchangeRate.objects.filter(
                            bank=bank,
                            currency_pair=pair,
                            timestamp=timestamp
                        ).first()
                        
                        if not existing:
                            # Get previous rate for change calculation
                            previous = BankExchangeRate.objects.filter(
                                bank=bank,
                                currency_pair=pair,
                                timestamp__lt=timestamp
                            ).order_by('-timestamp').first()
                            
                            rate = BankExchangeRate.objects.create(
                                entry_id=entry_id,
                                bank=bank,
                                currency_pair=pair,
                                buy_rate=buy_rate,
                                sell_rate=sell_rate,
                                date=current_date.date(),
                                timestamp=timestamp,
                                previous_buy_rate=previous.buy_rate if previous else None,
                                previous_sell_rate=previous.sell_rate if previous else None
                            )
                            rates_created += 1
                            
                            # The model's save method will calculate spread and changes
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {rates_created} bank exchange rates')
        )
        
        # Print summary
        total_rates = BankExchangeRate.objects.count()
        latest_rates = BankExchangeRate.objects.order_by('-timestamp').first()
        
        self.stdout.write(f'Total rates in database: {total_rates}')
        if latest_rates:
            self.stdout.write(f'Latest rate timestamp: {latest_rates.timestamp}')
            self.stdout.write(f'Latest rate: {latest_rates.bank} - {latest_rates.currency_pair} - Buy: {latest_rates.buy_rate} / Sell: {latest_rates.sell_rate}')