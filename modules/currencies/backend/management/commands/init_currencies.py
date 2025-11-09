"""
Management command to initialize currency data
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from modules.currencies.backend.models import Currency
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Initialize currency database with default currencies'
    
    # Default fiat currencies
    FIAT_CURRENCIES = [
        {'code': 'TRY', 'name': 'Turkish Lira', 'symbol': '₺', 'country_code': 'TR', 'decimal_places': 2},
        {'code': 'USD', 'name': 'US Dollar', 'symbol': '$', 'country_code': 'US', 'decimal_places': 2},
        {'code': 'EUR', 'name': 'Euro', 'symbol': '€', 'country_code': 'EU', 'decimal_places': 2},
        {'code': 'GBP', 'name': 'British Pound', 'symbol': '£', 'country_code': 'GB', 'decimal_places': 2},
        {'code': 'JPY', 'name': 'Japanese Yen', 'symbol': '¥', 'country_code': 'JP', 'decimal_places': 0},
        {'code': 'CHF', 'name': 'Swiss Franc', 'symbol': 'CHF', 'country_code': 'CH', 'decimal_places': 2},
        {'code': 'CAD', 'name': 'Canadian Dollar', 'symbol': 'C$', 'country_code': 'CA', 'decimal_places': 2},
        {'code': 'AUD', 'name': 'Australian Dollar', 'symbol': 'A$', 'country_code': 'AU', 'decimal_places': 2},
        {'code': 'CNY', 'name': 'Chinese Yuan', 'symbol': '¥', 'country_code': 'CN', 'decimal_places': 2},
        {'code': 'RUB', 'name': 'Russian Ruble', 'symbol': '₽', 'country_code': 'RU', 'decimal_places': 2},
        {'code': 'INR', 'name': 'Indian Rupee', 'symbol': '₹', 'country_code': 'IN', 'decimal_places': 2},
        {'code': 'KRW', 'name': 'South Korean Won', 'symbol': '₩', 'country_code': 'KR', 'decimal_places': 0},
        {'code': 'BRL', 'name': 'Brazilian Real', 'symbol': 'R$', 'country_code': 'BR', 'decimal_places': 2},
        {'code': 'ZAR', 'name': 'South African Rand', 'symbol': 'R', 'country_code': 'ZA', 'decimal_places': 2},
        {'code': 'SGD', 'name': 'Singapore Dollar', 'symbol': 'S$', 'country_code': 'SG', 'decimal_places': 2},
        {'code': 'HKD', 'name': 'Hong Kong Dollar', 'symbol': 'HK$', 'country_code': 'HK', 'decimal_places': 2},
        {'code': 'NZD', 'name': 'New Zealand Dollar', 'symbol': 'NZ$', 'country_code': 'NZ', 'decimal_places': 2},
        {'code': 'MXN', 'name': 'Mexican Peso', 'symbol': '$', 'country_code': 'MX', 'decimal_places': 2},
        {'code': 'NOK', 'name': 'Norwegian Krone', 'symbol': 'kr', 'country_code': 'NO', 'decimal_places': 2},
        {'code': 'SEK', 'name': 'Swedish Krona', 'symbol': 'kr', 'country_code': 'SE', 'decimal_places': 2},
        {'code': 'DKK', 'name': 'Danish Krone', 'symbol': 'kr', 'country_code': 'DK', 'decimal_places': 2},
        {'code': 'PLN', 'name': 'Polish Zloty', 'symbol': 'zł', 'country_code': 'PL', 'decimal_places': 2},
        {'code': 'THB', 'name': 'Thai Baht', 'symbol': '฿', 'country_code': 'TH', 'decimal_places': 2},
        {'code': 'IDR', 'name': 'Indonesian Rupiah', 'symbol': 'Rp', 'country_code': 'ID', 'decimal_places': 0},
        {'code': 'MYR', 'name': 'Malaysian Ringgit', 'symbol': 'RM', 'country_code': 'MY', 'decimal_places': 2},
        {'code': 'PHP', 'name': 'Philippine Peso', 'symbol': '₱', 'country_code': 'PH', 'decimal_places': 2},
        {'code': 'CZK', 'name': 'Czech Koruna', 'symbol': 'Kč', 'country_code': 'CZ', 'decimal_places': 2},
        {'code': 'HUF', 'name': 'Hungarian Forint', 'symbol': 'Ft', 'country_code': 'HU', 'decimal_places': 0},
        {'code': 'ILS', 'name': 'Israeli Shekel', 'symbol': '₪', 'country_code': 'IL', 'decimal_places': 2},
        {'code': 'AED', 'name': 'UAE Dirham', 'symbol': 'د.إ', 'country_code': 'AE', 'decimal_places': 2},
        {'code': 'SAR', 'name': 'Saudi Riyal', 'symbol': 'ر.س', 'country_code': 'SA', 'decimal_places': 2},
        {'code': 'KWD', 'name': 'Kuwaiti Dinar', 'symbol': 'د.ك', 'country_code': 'KW', 'decimal_places': 3},
        {'code': 'QAR', 'name': 'Qatari Riyal', 'symbol': 'ر.ق', 'country_code': 'QA', 'decimal_places': 2},
    ]
    
    # Default cryptocurrencies
    CRYPTO_CURRENCIES = [
        {'code': 'BTC', 'name': 'Bitcoin', 'symbol': '₿', 'decimal_places': 8},
        {'code': 'ETH', 'name': 'Ethereum', 'symbol': 'Ξ', 'decimal_places': 8},
        {'code': 'BNB', 'name': 'Binance Coin', 'symbol': 'BNB', 'decimal_places': 8},
        {'code': 'XRP', 'name': 'Ripple', 'symbol': 'XRP', 'decimal_places': 6},
        {'code': 'ADA', 'name': 'Cardano', 'symbol': 'ADA', 'decimal_places': 6},
        {'code': 'SOL', 'name': 'Solana', 'symbol': 'SOL', 'decimal_places': 9},
        {'code': 'DOGE', 'name': 'Dogecoin', 'symbol': 'DOGE', 'decimal_places': 8},
        {'code': 'DOT', 'name': 'Polkadot', 'symbol': 'DOT', 'decimal_places': 10},
        {'code': 'MATIC', 'name': 'Polygon', 'symbol': 'MATIC', 'decimal_places': 18},
        {'code': 'AVAX', 'name': 'Avalanche', 'symbol': 'AVAX', 'decimal_places': 18},
        {'code': 'LINK', 'name': 'Chainlink', 'symbol': 'LINK', 'decimal_places': 18},
        {'code': 'UNI', 'name': 'Uniswap', 'symbol': 'UNI', 'decimal_places': 18},
        {'code': 'ATOM', 'name': 'Cosmos', 'symbol': 'ATOM', 'decimal_places': 6},
        {'code': 'LTC', 'name': 'Litecoin', 'symbol': 'Ł', 'decimal_places': 8},
        {'code': 'FTM', 'name': 'Fantom', 'symbol': 'FTM', 'decimal_places': 18},
        {'code': 'ALGO', 'name': 'Algorand', 'symbol': 'ALGO', 'decimal_places': 6},
        {'code': 'XLM', 'name': 'Stellar', 'symbol': 'XLM', 'decimal_places': 7},
        {'code': 'VET', 'name': 'VeChain', 'symbol': 'VET', 'decimal_places': 18},
        {'code': 'TRX', 'name': 'TRON', 'symbol': 'TRX', 'decimal_places': 6},
        {'code': 'SHIB', 'name': 'Shiba Inu', 'symbol': 'SHIB', 'decimal_places': 18},
        {'code': 'APT', 'name': 'Aptos', 'symbol': 'APT', 'decimal_places': 8},
        {'code': 'ARB', 'name': 'Arbitrum', 'symbol': 'ARB', 'decimal_places': 18},
        {'code': 'OP', 'name': 'Optimism', 'symbol': 'OP', 'decimal_places': 18},
        {'code': 'NEAR', 'name': 'NEAR Protocol', 'symbol': 'NEAR', 'decimal_places': 24},
        {'code': 'FIL', 'name': 'Filecoin', 'symbol': 'FIL', 'decimal_places': 18},
    ]
    
    # Commodities
    COMMODITY_CURRENCIES = [
        {'code': 'XAU', 'name': 'Gold (per oz)', 'symbol': 'XAU', 'decimal_places': 2},
        {'code': 'XAG', 'name': 'Silver (per oz)', 'symbol': 'XAG', 'decimal_places': 2},
        {'code': 'XPT', 'name': 'Platinum (per oz)', 'symbol': 'XPT', 'decimal_places': 2},
        {'code': 'XPD', 'name': 'Palladium (per oz)', 'symbol': 'XPD', 'decimal_places': 2},
    ]
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update existing currencies',
        )
        parser.add_argument(
            '--type',
            type=str,
            choices=['fiat', 'crypto', 'commodity', 'all'],
            default='all',
            help='Type of currencies to initialize',
        )
    
    @transaction.atomic
    def handle(self, *args, **options):
        force_update = options['force']
        currency_type = options['type']
        
        created_count = 0
        updated_count = 0
        
        # Process fiat currencies
        if currency_type in ['fiat', 'all']:
            self.stdout.write('Initializing fiat currencies...')
            for curr_data in self.FIAT_CURRENCIES:
                created, updated = self._create_or_update_currency(
                    curr_data, 'fiat', force_update
                )
                created_count += created
                updated_count += updated
        
        # Process cryptocurrencies
        if currency_type in ['crypto', 'all']:
            self.stdout.write('Initializing cryptocurrencies...')
            for curr_data in self.CRYPTO_CURRENCIES:
                created, updated = self._create_or_update_currency(
                    curr_data, 'crypto', force_update
                )
                created_count += created
                updated_count += updated
        
        # Process commodities
        if currency_type in ['commodity', 'all']:
            self.stdout.write('Initializing commodity currencies...')
            for curr_data in self.COMMODITY_CURRENCIES:
                created, updated = self._create_or_update_currency(
                    curr_data, 'commodity', force_update
                )
                created_count += created
                updated_count += updated
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully initialized currencies: '
                f'{created_count} created, {updated_count} updated'
            )
        )
    
    def _create_or_update_currency(self, data, currency_type, force_update):
        """Create or update a currency"""
        code = data['code']
        
        try:
            currency = Currency.objects.get(code=code)
            if force_update:
                # Update existing currency
                currency.name = data['name']
                currency.symbol = data['symbol']
                currency.currency_type = currency_type
                currency.decimal_places = data.get('decimal_places', 2)
                currency.country_code = data.get('country_code', '')
                currency.is_active = True
                currency.save()
                self.stdout.write(f'  Updated: {code} - {data["name"]}')
                return 0, 1
            else:
                self.stdout.write(f'  Exists: {code} - {data["name"]}')
                return 0, 0
        except Currency.DoesNotExist:
            # Create new currency
            Currency.objects.create(
                code=code,
                name=data['name'],
                symbol=data['symbol'],
                currency_type=currency_type,
                decimal_places=data.get('decimal_places', 2),
                country_code=data.get('country_code', ''),
                is_active=True
            )
            self.stdout.write(
                self.style.SUCCESS(f'  Created: {code} - {data["name"]}')
            )
            return 1, 0