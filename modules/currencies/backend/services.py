"""
Currency services for external API integrations with security and reliability
"""

import requests
import xml.etree.ElementTree as ET
from decimal import Decimal
from django.utils import timezone
from django.core.cache import cache
from django.conf import settings
from django.db import transaction
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import hashlib
import hmac

from .models import Currency, ExchangeRate, MarketData

logger = logging.getLogger(__name__)


class RateLimiter:
    """Rate limiting for API calls"""
    
    def __init__(self, max_calls: int, period: int):
        self.max_calls = max_calls
        self.period = period  # in seconds
    
    def is_allowed(self, key: str) -> bool:
        """Check if API call is allowed"""
        cache_key = f"rate_limit:{key}"
        current_count = cache.get(cache_key, 0)
        
        if current_count >= self.max_calls:
            return False
        
        cache.set(cache_key, current_count + 1, self.period)
        return True


class APISecurityManager:
    """Manage API security and validation"""
    
    @staticmethod
    def validate_response(response: requests.Response) -> bool:
        """Validate API response for security issues"""
        # Check status code
        if response.status_code != 200:
            logger.warning(f"API returned status {response.status_code}")
            return False
        
        # Check content type
        content_type = response.headers.get('content-type', '')
        if 'json' not in content_type and 'xml' not in content_type:
            logger.warning(f"Unexpected content type: {content_type}")
            return False
        
        # Check response size (prevent DOS)
        if len(response.content) > 10 * 1024 * 1024:  # 10MB limit
            logger.warning("Response too large")
            return False
        
        return True
    
    @staticmethod
    def sanitize_data(data: Dict) -> Dict:
        """Sanitize data from external APIs"""
        # Remove any potential script injections
        sanitized = {}
        for key, value in data.items():
            if isinstance(value, str):
                # Remove potential XSS
                value = value.replace('<', '').replace('>', '')
                value = value.replace('javascript:', '')
                value = value.strip()
            sanitized[key] = value
        return sanitized


class TCMBService:
    """
    Turkish Central Bank (TCMB) API integration
    Fetches official exchange rates for fiat currencies
    """
    
    BASE_URL = "https://www.tcmb.gov.tr/kurlar/today.xml"
    RATE_LIMITER = RateLimiter(max_calls=10, period=3600)  # 10 calls per hour
    
    def __init__(self):
        self.security_manager = APISecurityManager()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'UNIBOS/1.0 Currency Module',
            'Accept': 'application/xml'
        })
        # Set timeout for all requests
        self.session.timeout = 10
    
    def fetch_rates(self) -> Optional[Dict]:
        """
        Fetch current exchange rates from TCMB
        Returns dict with currency codes as keys
        """
        cache_key = "tcmb_rates"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            logger.info("Returning cached TCMB rates")
            return cached_data
        
        if not self.RATE_LIMITER.is_allowed('tcmb'):
            logger.warning("TCMB rate limit exceeded")
            return self._get_fallback_rates()
        
        try:
            response = self.session.get(
                self.BASE_URL,
                timeout=10,
                verify=True  # Ensure SSL verification
            )
            
            if not self.security_manager.validate_response(response):
                return self._get_fallback_rates()
            
            # Parse XML
            root = ET.fromstring(response.content)
            rates = {}
            
            for currency in root.findall('.//Currency'):
                code = currency.get('CurrencyCode')
                if code:
                    try:
                        # Get buying and selling rates
                        forex_buying = currency.find('ForexBuying')
                        forex_selling = currency.find('ForexSelling')
                        
                        if forex_buying is not None and forex_buying.text:
                            buying_rate = Decimal(forex_buying.text)
                            selling_rate = Decimal(forex_selling.text) if forex_selling is not None else buying_rate
                            
                            rates[code] = {
                                'bid': buying_rate,
                                'ask': selling_rate,
                                'rate': (buying_rate + selling_rate) / 2,
                                'source': 'TCMB',
                                'timestamp': timezone.now()
                            }
                    except (ValueError, TypeError) as e:
                        logger.warning(f"Error parsing rate for {code}: {e}")
                        continue
            
            # Add TRY as base
            rates['TRY'] = {
                'bid': Decimal('1'),
                'ask': Decimal('1'),
                'rate': Decimal('1'),
                'source': 'TCMB',
                'timestamp': timezone.now()
            }
            
            # Cache for 5 minutes
            cache.set(cache_key, rates, 300)
            
            logger.info(f"Fetched {len(rates)} rates from TCMB")
            return rates
            
        except requests.RequestException as e:
            logger.error(f"TCMB API request failed: {e}")
            return self._get_fallback_rates()
        except ET.ParseError as e:
            logger.error(f"Failed to parse TCMB XML: {e}")
            return self._get_fallback_rates()
        except Exception as e:
            logger.error(f"Unexpected error fetching TCMB rates: {e}")
            return self._get_fallback_rates()
    
    def _get_fallback_rates(self) -> Dict:
        """
        Return fallback rates when API is unavailable
        Uses last known good rates or predefined defaults
        """
        # Try to get last known rates from database
        try:
            recent_rates = ExchangeRate.objects.filter(
                source='TCMB',
                timestamp__gte=timezone.now() - timedelta(days=1)
            ).select_related('base_currency', 'target_currency')
            
            if recent_rates.exists():
                rates = {}
                for rate in recent_rates:
                    if rate.base_currency.code not in rates:
                        rates[rate.base_currency.code] = {
                            'bid': rate.bid or rate.rate,
                            'ask': rate.ask or rate.rate,
                            'rate': rate.rate,
                            'source': 'TCMB_CACHED',
                            'timestamp': rate.timestamp
                        }
                logger.info("Using cached rates from database")
                return rates
        except Exception as e:
            logger.error(f"Failed to get cached rates: {e}")
        
        # Return hardcoded fallback rates
        logger.warning("Using hardcoded fallback rates")
        return {
            'USD': {'rate': Decimal('32.50'), 'bid': Decimal('32.45'), 'ask': Decimal('32.55'), 'source': 'FALLBACK'},
            'EUR': {'rate': Decimal('35.50'), 'bid': Decimal('35.45'), 'ask': Decimal('35.55'), 'source': 'FALLBACK'},
            'GBP': {'rate': Decimal('41.00'), 'bid': Decimal('40.95'), 'ask': Decimal('41.05'), 'source': 'FALLBACK'},
            'JPY': {'rate': Decimal('0.22'), 'bid': Decimal('0.219'), 'ask': Decimal('0.221'), 'source': 'FALLBACK'},
            'CHF': {'rate': Decimal('36.50'), 'bid': Decimal('36.45'), 'ask': Decimal('36.55'), 'source': 'FALLBACK'},
            'TRY': {'rate': Decimal('1'), 'bid': Decimal('1'), 'ask': Decimal('1'), 'source': 'FALLBACK'}
        }


class CoinGeckoService:
    """
    CoinGecko API integration for cryptocurrency rates
    Free tier: 10-30 calls/minute depending on endpoint
    """
    
    BASE_URL = "https://api.coingecko.com/api/v3"
    RATE_LIMITER = RateLimiter(max_calls=25, period=60)  # Conservative limit
    
    # Top cryptocurrencies to track
    CRYPTO_IDS = {
        'BTC': 'bitcoin',
        'ETH': 'ethereum',
        'BNB': 'binancecoin',
        'XRP': 'ripple',
        'ADA': 'cardano',
        'SOL': 'solana',
        'DOGE': 'dogecoin',
        'DOT': 'polkadot',
        'MATIC': 'matic-network',
        'AVAX': 'avalanche-2',
        'LINK': 'chainlink',
        'UNI': 'uniswap',
        'ATOM': 'cosmos',
        'LTC': 'litecoin',
        'FTM': 'fantom'
    }
    
    def __init__(self):
        self.security_manager = APISecurityManager()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'UNIBOS/1.0 Currency Module',
            'Accept': 'application/json'
        })
    
    def fetch_rates(self, vs_currency: str = 'try') -> Optional[Dict]:
        """
        Fetch cryptocurrency rates against specified currency
        """
        cache_key = f"coingecko_rates_{vs_currency}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            logger.info("Returning cached CoinGecko rates")
            return cached_data
        
        if not self.RATE_LIMITER.is_allowed('coingecko'):
            logger.warning("CoinGecko rate limit exceeded")
            return self._get_fallback_rates()
        
        try:
            # Build request parameters
            ids = ','.join(self.CRYPTO_IDS.values())
            params = {
                'ids': ids,
                'vs_currencies': vs_currency.lower(),
                'include_24hr_change': 'true',
                'include_24hr_vol': 'true',
                'include_last_updated_at': 'true'
            }
            
            response = self.session.get(
                f"{self.BASE_URL}/simple/price",
                params=params,
                timeout=10,
                verify=True
            )
            
            if not self.security_manager.validate_response(response):
                return self._get_fallback_rates()
            
            data = response.json()
            rates = {}
            
            # Map CoinGecko IDs back to currency codes
            id_to_code = {v: k for k, v in self.CRYPTO_IDS.items()}
            
            for coin_id, coin_data in data.items():
                code = id_to_code.get(coin_id)
                if code:
                    vs_curr = vs_currency.lower()
                    rates[code] = {
                        'rate': Decimal(str(coin_data.get(vs_curr, 0))),
                        'change_24h': Decimal(str(coin_data.get(f'{vs_curr}_24h_change', 0))),
                        'volume_24h': Decimal(str(coin_data.get(f'{vs_curr}_24h_vol', 0))),
                        'source': 'CoinGecko',
                        'timestamp': timezone.now()
                    }
            
            # Cache for 5 minutes
            cache.set(cache_key, rates, 300)
            
            logger.info(f"Fetched {len(rates)} crypto rates from CoinGecko")
            return rates
            
        except requests.RequestException as e:
            logger.error(f"CoinGecko API request failed: {e}")
            return self._get_fallback_rates()
        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"Error parsing CoinGecko response: {e}")
            return self._get_fallback_rates()
        except Exception as e:
            logger.error(f"Unexpected error fetching CoinGecko rates: {e}")
            return self._get_fallback_rates()
    
    def fetch_market_data(self, coin_id: str, days: int = 30) -> Optional[List]:
        """
        Fetch historical market data for charts
        """
        cache_key = f"coingecko_market_{coin_id}_{days}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        if not self.RATE_LIMITER.is_allowed('coingecko_market'):
            logger.warning("CoinGecko rate limit exceeded for market data")
            return None
        
        try:
            params = {
                'vs_currency': 'try',
                'days': days,
                'interval': 'daily' if days > 1 else 'hourly'
            }
            
            response = self.session.get(
                f"{self.BASE_URL}/coins/{coin_id}/market_chart",
                params=params,
                timeout=10,
                verify=True
            )
            
            if not self.security_manager.validate_response(response):
                return None
            
            data = response.json()
            
            # Process market data
            market_data = []
            prices = data.get('prices', [])
            volumes = data.get('total_volumes', [])
            
            for i, (timestamp, price) in enumerate(prices):
                volume = volumes[i][1] if i < len(volumes) else 0
                market_data.append({
                    'timestamp': datetime.fromtimestamp(timestamp / 1000, tz=timezone.utc),
                    'price': Decimal(str(price)),
                    'volume': Decimal(str(volume))
                })
            
            # Cache for 1 hour
            cache.set(cache_key, market_data, 3600)
            
            return market_data
            
        except Exception as e:
            logger.error(f"Error fetching market data: {e}")
            return None
    
    def _get_fallback_rates(self) -> Dict:
        """
        Return fallback cryptocurrency rates
        """
        logger.warning("Using fallback crypto rates")
        return {
            'BTC': {'rate': Decimal('1850000'), 'change_24h': Decimal('0'), 'source': 'FALLBACK'},
            'ETH': {'rate': Decimal('115000'), 'change_24h': Decimal('0'), 'source': 'FALLBACK'},
            'BNB': {'rate': Decimal('20000'), 'change_24h': Decimal('0'), 'source': 'FALLBACK'},
            'XRP': {'rate': Decimal('20'), 'change_24h': Decimal('0'), 'source': 'FALLBACK'},
            'ADA': {'rate': Decimal('15'), 'change_24h': Decimal('0'), 'source': 'FALLBACK'}
        }


class CurrencyService:
    """
    Main service for managing currency data and updates
    Orchestrates different API services
    """
    
    def __init__(self):
        self.tcmb_service = TCMBService()
        self.coingecko_service = CoinGeckoService()
    
    @transaction.atomic
    def update_tcmb_rates(self) -> int:
        """
        Update fiat currency rates from TCMB
        Returns number of rates updated
        """
        rates = self.tcmb_service.fetch_rates()
        if not rates:
            logger.error("Failed to fetch TCMB rates")
            return 0
        
        updated_count = 0
        
        for code, rate_data in rates.items():
            if code == 'TRY':
                continue
            
            try:
                # Get or create currency
                currency, _ = Currency.objects.get_or_create(
                    code=code,
                    defaults={
                        'name': code,  # Will be updated separately
                        'symbol': code,
                        'currency_type': 'fiat',
                        'decimal_places': 2,
                        'is_active': True
                    }
                )
                
                # Create exchange rate to TRY
                target_currency = Currency.objects.get(code='TRY')
                
                ExchangeRate.objects.create(
                    base_currency=currency,
                    target_currency=target_currency,
                    rate=rate_data['rate'],
                    bid=rate_data.get('bid'),
                    ask=rate_data.get('ask'),
                    source=rate_data.get('source', 'TCMB'),
                    timestamp=rate_data.get('timestamp', timezone.now())
                )
                
                updated_count += 1
                
            except Exception as e:
                logger.error(f"Error updating rate for {code}: {e}")
                continue
        
        logger.info(f"Updated {updated_count} TCMB rates")
        return updated_count
    
    @transaction.atomic
    def update_crypto_rates(self) -> int:
        """
        Update cryptocurrency rates from CoinGecko
        Returns number of rates updated
        """
        rates = self.coingecko_service.fetch_rates('try')
        if not rates:
            logger.error("Failed to fetch crypto rates")
            return 0
        
        updated_count = 0
        
        for code, rate_data in rates.items():
            try:
                # Get or create currency
                currency, _ = Currency.objects.get_or_create(
                    code=code,
                    defaults={
                        'name': self._get_crypto_name(code),
                        'symbol': code,
                        'currency_type': 'crypto',
                        'decimal_places': 8,
                        'is_active': True
                    }
                )
                
                # Create exchange rate to TRY
                target_currency = Currency.objects.get(code='TRY')
                
                ExchangeRate.objects.create(
                    base_currency=currency,
                    target_currency=target_currency,
                    rate=rate_data['rate'],
                    change_24h=rate_data.get('change_24h'),
                    change_percentage_24h=rate_data.get('change_24h'),
                    volume_24h=rate_data.get('volume_24h'),
                    source=rate_data.get('source', 'CoinGecko'),
                    timestamp=rate_data.get('timestamp', timezone.now())
                )
                
                updated_count += 1
                
            except Exception as e:
                logger.error(f"Error updating rate for {code}: {e}")
                continue
        
        logger.info(f"Updated {updated_count} crypto rates")
        return updated_count
    
    def _get_crypto_name(self, code: str) -> str:
        """Get full name for cryptocurrency"""
        names = {
            'BTC': 'Bitcoin',
            'ETH': 'Ethereum',
            'BNB': 'Binance Coin',
            'XRP': 'Ripple',
            'ADA': 'Cardano',
            'SOL': 'Solana',
            'DOGE': 'Dogecoin',
            'DOT': 'Polkadot',
            'MATIC': 'Polygon',
            'AVAX': 'Avalanche',
            'LINK': 'Chainlink',
            'UNI': 'Uniswap',
            'ATOM': 'Cosmos',
            'LTC': 'Litecoin',
            'FTM': 'Fantom'
        }
        return names.get(code, code)
    
    def get_conversion_rate(
        self,
        from_currency: str,
        to_currency: str,
        use_cache: bool = True
    ) -> Optional[Decimal]:
        """
        Get conversion rate between two currencies
        Handles cross rates through TRY if needed
        """
        if from_currency == to_currency:
            return Decimal('1')
        
        cache_key = f"conversion_{from_currency}_{to_currency}"
        
        if use_cache:
            cached_rate = cache.get(cache_key)
            if cached_rate:
                return Decimal(str(cached_rate))
        
        try:
            # Try direct rate
            rate = ExchangeRate.objects.filter(
                base_currency__code=from_currency,
                target_currency__code=to_currency
            ).latest('timestamp')
            
            cache.set(cache_key, str(rate.rate), 300)
            return rate.rate
            
        except ExchangeRate.DoesNotExist:
            # Try reverse rate
            try:
                reverse_rate = ExchangeRate.objects.filter(
                    base_currency__code=to_currency,
                    target_currency__code=from_currency
                ).latest('timestamp')
                
                rate = Decimal('1') / reverse_rate.rate
                cache.set(cache_key, str(rate), 300)
                return rate
                
            except ExchangeRate.DoesNotExist:
                # Try through TRY
                try:
                    from_try = ExchangeRate.objects.filter(
                        base_currency__code=from_currency,
                        target_currency__code='TRY'
                    ).latest('timestamp')
                    
                    to_try = ExchangeRate.objects.filter(
                        base_currency__code=to_currency,
                        target_currency__code='TRY'
                    ).latest('timestamp')
                    
                    rate = from_try.rate / to_try.rate
                    cache.set(cache_key, str(rate), 300)
                    return rate
                    
                except ExchangeRate.DoesNotExist:
                    logger.warning(f"No rate found for {from_currency}/{to_currency}")
                    return None
        
        except Exception as e:
            logger.error(f"Error getting conversion rate: {e}")
            return None
    
    def cleanup_old_rates(self, days: int = 30) -> int:
        """
        Clean up old exchange rates to manage database size
        Keep only latest rate per day for historical data
        """
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # Delete old rates except daily snapshots
        deleted_count = ExchangeRate.objects.filter(
            timestamp__lt=cutoff_date
        ).exclude(
            timestamp__hour=12  # Keep noon rates as daily snapshot
        ).delete()[0]
        
        logger.info(f"Cleaned up {deleted_count} old exchange rates")
        return deleted_count