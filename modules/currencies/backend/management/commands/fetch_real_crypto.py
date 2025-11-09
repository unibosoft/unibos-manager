"""
Management command to fetch real-time cryptocurrency data
Runs periodically to update database with latest prices
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from decimal import Decimal
import logging
import pytz

from modules.currencies.backend.models import (
    Currency, CryptoExchangeRate, Portfolio, PortfolioPerformance
)
from modules.currencies.backend.real_crypto_service import crypto_service

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Fetch real-time cryptocurrency prices from multiple exchanges'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--symbols',
            nargs='+',
            default=['BTC', 'ETH', 'AVAX'],
            help='Cryptocurrency symbols to fetch'
        )
        parser.add_argument(
            '--update-portfolios',
            action='store_true',
            help='Update all portfolio performance snapshots'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Verbose output'
        )
    
    def handle(self, *args, **options):
        symbols = options['symbols']
        update_portfolios = options['update_portfolios']
        verbose = options['verbose']
        
        istanbul_tz = pytz.timezone('Europe/Istanbul')
        current_time = timezone.now()
        
        self.stdout.write(f"Starting crypto price fetch at {current_time}")
        
        # Ensure currencies exist
        self._ensure_currencies_exist(symbols)
        
        # Fetch prices from all sources
        all_prices = crypto_service.get_all_prices(symbols)
        
        saved_count = 0
        error_count = 0
        
        for symbol, price_data in all_prices.items():
            # Save Binance data
            if price_data.get('binance_usdt'):
                saved = self._save_exchange_rate(symbol, price_data['binance_usdt'], 'USDT')
                if saved:
                    saved_count += 1
                    if verbose:
                        self.stdout.write(f"✓ Saved Binance {symbol}/USDT")
                else:
                    error_count += 1
            
            # Save CoinGecko USD data
            if price_data.get('coingecko_usd'):
                saved = self._save_exchange_rate(symbol, price_data['coingecko_usd'], 'USD')
                if saved:
                    saved_count += 1
                    if verbose:
                        self.stdout.write(f"✓ Saved CoinGecko {symbol}/USD")
                else:
                    error_count += 1
            
            # Save CoinGecko TRY data
            if price_data.get('coingecko_try'):
                saved = self._save_exchange_rate(symbol, price_data['coingecko_try'], 'TRY')
                if saved:
                    saved_count += 1
                    if verbose:
                        self.stdout.write(f"✓ Saved CoinGecko {symbol}/TRY")
                else:
                    error_count += 1
            
            # Save BTCTurk TRY data
            if price_data.get('btcturk_try'):
                saved = self._save_exchange_rate(symbol, price_data['btcturk_try'], 'TRY')
                if saved:
                    saved_count += 1
                    if verbose:
                        self.stdout.write(f"✓ Saved BTCTurk {symbol}/TRY")
                else:
                    error_count += 1
            
            # Log aggregated prices
            if verbose and price_data.get('aggregated'):
                agg = price_data['aggregated']
                self.stdout.write(
                    f"{symbol} Aggregated: "
                    f"USD ${agg.get('usd_price', 'N/A')}, "
                    f"TRY ₺{agg.get('try_price', 'N/A')}"
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Completed: {saved_count} prices saved, {error_count} errors"
            )
        )
        
        # Update portfolio snapshots if requested
        if update_portfolios:
            self._update_portfolio_snapshots(verbose)
    
    def _ensure_currencies_exist(self, symbols):
        """Ensure cryptocurrency entries exist in database"""
        currency_info = {
            'BTC': {'name': 'Bitcoin', 'symbol': '₿'},
            'ETH': {'name': 'Ethereum', 'symbol': 'Ξ'},
            'AVAX': {'name': 'Avalanche', 'symbol': 'AVAX'},
        }
        
        for symbol in symbols:
            info = currency_info.get(symbol, {'name': symbol, 'symbol': symbol})
            Currency.objects.get_or_create(
                code=symbol,
                defaults={
                    'name': info['name'],
                    'symbol': info['symbol'],
                    'currency_type': 'crypto',
                    'decimal_places': 8,
                    'is_active': True
                }
            )
    
    def _save_exchange_rate(self, symbol, price_data, quote_currency):
        """Save exchange rate to database"""
        if not price_data or 'price' not in price_data:
            return False
        
        try:
            with transaction.atomic():
                # Create exchange rate record
                rate = CryptoExchangeRate.objects.create(
                    exchange=price_data.get('exchange', 'Unknown'),
                    symbol=f"{symbol}/{quote_currency}",
                    base_asset=symbol,
                    quote_asset=quote_currency,
                    last_price=Decimal(str(price_data['price'])),
                    bid_price=Decimal(str(price_data.get('bid', 0))) if price_data.get('bid') else None,
                    ask_price=Decimal(str(price_data.get('ask', 0))) if price_data.get('ask') else None,
                    high_24h=Decimal(str(price_data.get('high_24h', 0))) if price_data.get('high_24h') else None,
                    low_24h=Decimal(str(price_data.get('low_24h', 0))) if price_data.get('low_24h') else None,
                    volume_24h=Decimal(str(price_data.get('volume_24h', 0))) if price_data.get('volume_24h') else None,
                    change_24h=Decimal(str(price_data.get('change_24h', 0))) if price_data.get('change_24h') else None,
                    change_percentage_24h=Decimal(str(price_data.get('change_percentage_24h', 0))) if price_data.get('change_percentage_24h') else None,
                    timestamp=price_data.get('timestamp', timezone.now())
                )
                return True
        except Exception as e:
            logger.error(f"Error saving exchange rate for {symbol}/{quote_currency}: {str(e)}")
            return False
    
    def _update_portfolio_snapshots(self, verbose):
        """Update performance snapshots for all active portfolios"""
        portfolios = Portfolio.objects.filter(
            holdings__amount__gt=0
        ).distinct()
        
        updated_count = 0
        
        for portfolio in portfolios:
            try:
                PortfolioPerformance.capture_snapshot(portfolio)
                updated_count += 1
                if verbose:
                    self.stdout.write(f"✓ Updated snapshot for {portfolio.user.username}'s portfolio")
            except Exception as e:
                logger.error(f"Error updating portfolio {portfolio.id}: {str(e)}")
                if verbose:
                    self.stdout.write(
                        self.style.ERROR(f"✗ Failed to update {portfolio.user.username}'s portfolio")
                    )
        
        self.stdout.write(
            self.style.SUCCESS(f"Updated {updated_count} portfolio snapshots")
        )