"""
Cryptocurrency Exchange Service
Fetches real-time crypto prices from multiple exchanges
"""

import logging
import json
from decimal import Decimal
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from django.utils import timezone
from django.core.cache import cache
import random  # For mock data generation

logger = logging.getLogger(__name__)


class CryptoExchangeService:
    """Service for fetching cryptocurrency exchange rates"""
    
    # Common trading pairs to track
    TRACKED_PAIRS = {
        'international': [
            'BTC/USD', 'ETH/USD', 'BNB/USD', 'XRP/USD', 'ADA/USD',
            'SOL/USD', 'DOGE/USD', 'DOT/USD', 'MATIC/USD', 'AVAX/USD',
            'BTC/EUR', 'ETH/EUR', 'BTC/USDT', 'ETH/USDT'
        ],
        'turkish': [
            'BTC/TRY', 'ETH/TRY', 'BNB/TRY', 'XRP/TRY', 'ADA/TRY',
            'SOL/TRY', 'DOGE/TRY', 'USDT/TRY', 'AVAX/TRY', 'MATIC/TRY'
        ]
    }
    
    # Exchange API configurations (mock for now)
    EXCHANGES = {
        'Binance': {
            'api_url': 'https://api.binance.com/api/v3',
            'rate_limit': 1200,  # requests per minute
            'supported_pairs': ['BTC/USD', 'ETH/USD', 'BNB/USD', 'XRP/USD'],
        },
        'Coinbase': {
            'api_url': 'https://api.pro.coinbase.com',
            'rate_limit': 10,  # requests per second
            'supported_pairs': ['BTC/USD', 'ETH/USD', 'ADA/USD', 'SOL/USD'],
        },
        'Kraken': {
            'api_url': 'https://api.kraken.com/0',
            'rate_limit': 1,  # requests per second
            'supported_pairs': ['BTC/USD', 'ETH/USD', 'DOT/USD', 'MATIC/USD'],
        },
        'BTCTurk': {
            'api_url': 'https://api.btcturk.com/api/v2',
            'rate_limit': 100,  # requests per minute
            'supported_pairs': ['BTC/TRY', 'ETH/TRY', 'XRP/TRY', 'USDT/TRY'],
        },
        'Paribu': {
            'api_url': 'https://www.paribu.com/ticker',
            'rate_limit': 60,  # requests per minute
            'supported_pairs': ['BTC/TRY', 'ETH/TRY', 'DOGE/TRY', 'AVAX/TRY'],
        },
        'BinanceTR': {
            'api_url': 'https://www.trbinance.com/api/v3',
            'rate_limit': 1200,  # requests per minute
            'supported_pairs': ['BTC/TRY', 'ETH/TRY', 'BNB/TRY', 'SOL/TRY'],
        }
    }
    
    @classmethod
    def fetch_exchange_rates(cls, exchange: str, symbol: Optional[str] = None) -> List[Dict]:
        """
        Fetch exchange rates from a specific exchange
        Returns mock data for now - implement actual API calls later
        """
        cache_key = f"crypto_rates:{exchange}:{symbol or 'all'}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        try:
            if exchange in ['Binance', 'BinanceUS', 'BinanceTR']:
                data = cls._fetch_binance_data(exchange, symbol)
            elif exchange == 'Coinbase':
                data = cls._fetch_coinbase_data(symbol)
            elif exchange == 'Kraken':
                data = cls._fetch_kraken_data(symbol)
            elif exchange == 'BTCTurk':
                data = cls._fetch_btcturk_data(symbol)
            elif exchange == 'Paribu':
                data = cls._fetch_paribu_data(symbol)
            else:
                # Generate mock data for other exchanges
                data = cls._generate_mock_data(exchange, symbol)
            
            # Cache for 30 seconds
            cache.set(cache_key, data, 30)
            return data
            
        except Exception as e:
            logger.error(f"Error fetching rates from {exchange}: {e}")
            return []
    
    @classmethod
    def _generate_mock_data(cls, exchange: str, symbol: Optional[str] = None) -> List[Dict]:
        """Generate realistic mock cryptocurrency data"""
        mock_prices = {
            'BTC/USD': (65000, 69000),
            'BTC/EUR': (60000, 64000),
            'BTC/TRY': (2100000, 2250000),
            'ETH/USD': (3200, 3500),
            'ETH/EUR': (2950, 3250),
            'ETH/TRY': (103000, 113000),
            'BNB/USD': (580, 620),
            'BNB/TRY': (18700, 20000),
            'XRP/USD': (0.50, 0.65),
            'XRP/TRY': (16.0, 21.0),
            'ADA/USD': (0.45, 0.60),
            'ADA/TRY': (14.5, 19.5),
            'SOL/USD': (140, 165),
            'SOL/TRY': (4500, 5350),
            'DOGE/USD': (0.075, 0.095),
            'DOGE/TRY': (2.4, 3.1),
            'DOT/USD': (7.0, 8.5),
            'DOT/TRY': (225, 275),
            'MATIC/USD': (0.85, 1.10),
            'MATIC/TRY': (27.5, 35.5),
            'AVAX/USD': (35, 42),
            'AVAX/TRY': (1130, 1360),
            'USDT/TRY': (32.20, 32.45),
        }
        
        pairs_to_fetch = [symbol] if symbol else cls.EXCHANGES.get(exchange, {}).get('supported_pairs', [])
        if not pairs_to_fetch:
            # Default pairs if exchange not configured
            pairs_to_fetch = ['BTC/USD', 'ETH/USD'] if 'TRY' not in exchange else ['BTC/TRY', 'ETH/TRY']
        
        data = []
        for pair in pairs_to_fetch:
            if pair not in mock_prices:
                continue
                
            base, quote = pair.split('/')
            min_price, max_price = mock_prices[pair]
            
            # Generate realistic price with small variations
            last_price = random.uniform(min_price, max_price)
            spread_percentage = random.uniform(0.05, 0.25) / 100  # 0.05% to 0.25% spread
            
            bid_price = last_price * (1 - spread_percentage)
            ask_price = last_price * (1 + spread_percentage)
            
            # Generate 24h changes
            change_percentage = random.uniform(-5, 5)
            open_24h = last_price / (1 + change_percentage / 100)
            high_24h = max(last_price, open_24h) * random.uniform(1.01, 1.05)
            low_24h = min(last_price, open_24h) * random.uniform(0.95, 0.99)
            
            # Volume based on pair popularity
            base_volume = {
                'BTC': random.uniform(10000, 25000),
                'ETH': random.uniform(50000, 150000),
                'BNB': random.uniform(30000, 80000),
                'XRP': random.uniform(1000000, 5000000),
                'ADA': random.uniform(500000, 2000000),
                'SOL': random.uniform(50000, 200000),
                'DOGE': random.uniform(5000000, 20000000),
                'DOT': random.uniform(100000, 500000),
                'MATIC': random.uniform(500000, 2000000),
                'AVAX': random.uniform(50000, 200000),
                'USDT': random.uniform(1000000, 5000000),
            }.get(base, random.uniform(10000, 100000))
            
            volume_24h_quote = base_volume * last_price
            
            data.append({
                'exchange': exchange,
                'symbol': pair,
                'base_asset': base,
                'quote_asset': quote,
                'last_price': Decimal(str(round(last_price, 8))),
                'bid_price': Decimal(str(round(bid_price, 8))),
                'ask_price': Decimal(str(round(ask_price, 8))),
                'open_24h': Decimal(str(round(open_24h, 8))),
                'high_24h': Decimal(str(round(high_24h, 8))),
                'low_24h': Decimal(str(round(low_24h, 8))),
                'volume_24h': Decimal(str(round(base_volume, 2))),
                'volume_24h_quote': Decimal(str(round(volume_24h_quote, 2))),
                'change_24h': Decimal(str(round(last_price - open_24h, 8))),
                'change_percentage_24h': Decimal(str(round(change_percentage, 2))),
                'timestamp': timezone.now(),
            })
        
        return data
    
    @classmethod
    def _fetch_binance_data(cls, exchange: str, symbol: Optional[str] = None) -> List[Dict]:
        """Fetch data from Binance API (mock for now)"""
        return cls._generate_mock_data(exchange, symbol)
    
    @classmethod
    def _fetch_coinbase_data(cls, symbol: Optional[str] = None) -> List[Dict]:
        """Fetch data from Coinbase API (mock for now)"""
        return cls._generate_mock_data('Coinbase', symbol)
    
    @classmethod
    def _fetch_kraken_data(cls, symbol: Optional[str] = None) -> List[Dict]:
        """Fetch data from Kraken API (mock for now)"""
        return cls._generate_mock_data('Kraken', symbol)
    
    @classmethod
    def _fetch_btcturk_data(cls, symbol: Optional[str] = None) -> List[Dict]:
        """Fetch data from BTCTurk API (mock for now)"""
        return cls._generate_mock_data('BTCTurk', symbol)
    
    @classmethod
    def _fetch_paribu_data(cls, symbol: Optional[str] = None) -> List[Dict]:
        """Fetch data from Paribu API (mock for now)"""
        return cls._generate_mock_data('Paribu', symbol)
    
    @classmethod
    def get_best_prices(cls, symbol: str) -> Dict:
        """
        Get best bid and ask prices across all exchanges for a symbol
        """
        cache_key = f"best_prices:{symbol}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        best_bid = None
        best_bid_exchange = None
        best_ask = None
        best_ask_exchange = None
        
        # Check which exchanges support this pair
        quote_currency = symbol.split('/')[1]
        exchanges_to_check = []
        
        if quote_currency == 'TRY':
            exchanges_to_check = ['BTCTurk', 'Paribu', 'BinanceTR']
        else:
            exchanges_to_check = ['Binance', 'Coinbase', 'Kraken']
        
        for exchange in exchanges_to_check:
            try:
                rates = cls.fetch_exchange_rates(exchange, symbol)
                for rate in rates:
                    if rate['symbol'] == symbol:
                        # Best bid is highest bid (best price to sell at)
                        if best_bid is None or rate['bid_price'] > best_bid:
                            best_bid = rate['bid_price']
                            best_bid_exchange = exchange
                        
                        # Best ask is lowest ask (best price to buy at)
                        if best_ask is None or rate['ask_price'] < best_ask:
                            best_ask = rate['ask_price']
                            best_ask_exchange = exchange
            except Exception as e:
                logger.error(f"Error fetching {symbol} from {exchange}: {e}")
        
        result = {
            'symbol': symbol,
            'best_bid': best_bid,
            'best_bid_exchange': best_bid_exchange,
            'best_ask': best_ask,
            'best_ask_exchange': best_ask_exchange,
            'spread': best_ask - best_bid if best_ask and best_bid else None,
            'timestamp': timezone.now()
        }
        
        # Cache for 10 seconds
        cache.set(cache_key, result, 10)
        return result
    
    @classmethod
    def get_aggregated_market_data(cls, symbol: str) -> Dict:
        """
        Get aggregated market data across all exchanges
        """
        quote_currency = symbol.split('/')[1]
        exchanges = ['BTCTurk', 'Paribu', 'BinanceTR'] if quote_currency == 'TRY' else ['Binance', 'Coinbase', 'Kraken']
        
        total_volume = Decimal('0')
        price_sum = Decimal('0')
        price_count = 0
        high_24h = None
        low_24h = None
        
        for exchange in exchanges:
            try:
                rates = cls.fetch_exchange_rates(exchange, symbol)
                for rate in rates:
                    if rate['symbol'] == symbol:
                        total_volume += rate.get('volume_24h_quote', 0)
                        price_sum += rate['last_price']
                        price_count += 1
                        
                        if high_24h is None or rate['high_24h'] > high_24h:
                            high_24h = rate['high_24h']
                        if low_24h is None or rate['low_24h'] < low_24h:
                            low_24h = rate['low_24h']
            except Exception as e:
                logger.error(f"Error aggregating {symbol} from {exchange}: {e}")
        
        avg_price = price_sum / price_count if price_count > 0 else None
        
        return {
            'symbol': symbol,
            'average_price': avg_price,
            'total_volume_24h': total_volume,
            'high_24h': high_24h,
            'low_24h': low_24h,
            'exchanges_count': price_count,
            'timestamp': timezone.now()
        }


class CryptoPortfolioAnalyzer:
    """Analyze crypto portfolio performance"""
    
    @staticmethod
    def calculate_portfolio_metrics(holdings: List[Dict]) -> Dict:
        """
        Calculate portfolio metrics like total value, allocation, risk score
        """
        total_value = Decimal('0')
        allocations = {}
        
        for holding in holdings:
            value = holding.get('current_value', 0)
            total_value += value
            asset = holding.get('asset')
            if asset:
                allocations[asset] = allocations.get(asset, 0) + value
        
        # Calculate percentages
        allocation_percentages = {}
        for asset, value in allocations.items():
            if total_value > 0:
                allocation_percentages[asset] = (value / total_value) * 100
        
        # Calculate risk score (simplified)
        risk_score = cls._calculate_risk_score(allocation_percentages)
        
        return {
            'total_value': total_value,
            'allocations': allocation_percentages,
            'risk_score': risk_score,
            'diversification_score': cls._calculate_diversification(allocation_percentages),
        }
    
    @staticmethod
    def _calculate_risk_score(allocations: Dict) -> float:
        """
        Calculate portfolio risk score (0-100)
        Higher concentration = higher risk
        """
        if not allocations:
            return 0
        
        # Simple risk calculation based on concentration
        max_allocation = max(allocations.values()) if allocations else 0
        
        if max_allocation > 50:
            return 80  # High risk
        elif max_allocation > 30:
            return 60  # Medium-high risk
        elif max_allocation > 20:
            return 40  # Medium risk
        else:
            return 20  # Low risk
    
    @staticmethod
    def _calculate_diversification(allocations: Dict) -> float:
        """
        Calculate diversification score (0-100)
        More assets with balanced allocation = better diversification
        """
        if not allocations or len(allocations) == 1:
            return 0
        
        # Calculate using Herfindahl-Hirschman Index (HHI)
        hhi = sum(pct ** 2 for pct in allocations.values())
        
        # Convert HHI to diversification score (inverse relationship)
        # HHI ranges from 1/n to 10000 (where n is number of assets)
        # We want score from 0 to 100
        min_hhi = 10000 / len(allocations)  # Perfect diversification
        max_hhi = 10000  # Complete concentration
        
        if hhi <= min_hhi:
            return 100
        elif hhi >= max_hhi:
            return 0
        else:
            # Linear interpolation
            return 100 * (max_hhi - hhi) / (max_hhi - min_hhi)