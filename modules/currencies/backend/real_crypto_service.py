"""
Real-time cryptocurrency service with multiple exchange API integrations
Handles real price fetching from Binance, CoinGecko, and BTCTurk
"""

import logging
import requests
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
from django.core.cache import cache
from django.utils import timezone
from datetime import datetime, timedelta
import hashlib
import json
import time
import pytz

logger = logging.getLogger(__name__)


class CryptoAPIService:
    """Main service for fetching real-time cryptocurrency data"""
    
    # API Endpoints (no authentication needed for public data)
    BINANCE_API = "https://api.binance.com/api/v3"
    BINANCE_US_API = "https://api.binance.us/api/v3"
    COINGECKO_API = "https://api.coingecko.com/api/v3"
    BTCTURK_API = "https://api.btcturk.com/api/v2"
    
    # Supported cryptocurrencies
    SUPPORTED_CRYPTOS = ['BTC', 'ETH', 'AVAX']
    
    # Cache settings
    CACHE_TTL = 60  # 1 minute cache for real-time data
    RATE_LIMIT_CACHE_TTL = 3600  # 1 hour for rate limit tracking
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'UNIBOS/1.0 (Cryptocurrency Portfolio Manager)'
        })
        
    def _make_request(self, url: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make HTTP request with error handling and caching"""
        # Generate cache key
        cache_key = hashlib.md5(f"{url}:{json.dumps(params or {})}".encode()).hexdigest()
        
        # Check cache first
        cached_data = cache.get(f"crypto_api:{cache_key}")
        if cached_data:
            logger.debug(f"Returning cached data for {url}")
            return cached_data
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Cache successful response
            cache.set(f"crypto_api:{cache_key}", data, self.CACHE_TTL)
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed for {url}: {str(e)}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response from {url}: {str(e)}")
            return None
    
    def get_binance_price(self, symbol: str, quote: str = 'USDT') -> Optional[Dict]:
        """
        Get real-time price from Binance
        
        Args:
            symbol: Crypto symbol (BTC, ETH, AVAX)
            quote: Quote currency (USDT, BUSD, etc.)
        
        Returns:
            Dict with price information or None if failed
        """
        trading_pair = f"{symbol}{quote}"
        
        # Try main Binance first
        url = f"{self.BINANCE_API}/ticker/24hr"
        data = self._make_request(url, {'symbol': trading_pair})
        
        if not data:
            # Fallback to Binance US
            url = f"{self.BINANCE_US_API}/ticker/24hr"
            data = self._make_request(url, {'symbol': trading_pair})
        
        if data:
            return {
                'exchange': 'Binance',
                'symbol': symbol,
                'quote': quote,
                'price': float(data.get('lastPrice', 0)),
                'bid': float(data.get('bidPrice', 0)),
                'ask': float(data.get('askPrice', 0)),
                'volume_24h': float(data.get('volume', 0)),
                'volume_24h_quote': float(data.get('quoteVolume', 0)),
                'change_24h': float(data.get('priceChange', 0)),
                'change_percentage_24h': float(data.get('priceChangePercent', 0)),
                'high_24h': float(data.get('highPrice', 0)),
                'low_24h': float(data.get('lowPrice', 0)),
                'timestamp': timezone.make_aware(datetime.fromtimestamp(data.get('closeTime', 0) / 1000), pytz.utc)
            }
        
        return None
    
    def get_coingecko_price(self, coin_id: str, vs_currency: str = 'usd') -> Optional[Dict]:
        """
        Get price data from CoinGecko
        
        Args:
            coin_id: CoinGecko coin ID (bitcoin, ethereum, avalanche-2)
            vs_currency: Target currency (usd, try, eur, etc.)
        
        Returns:
            Dict with price information or None if failed
        """
        # Map symbols to CoinGecko IDs
        coin_id_map = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'AVAX': 'avalanche-2'
        }
        
        if coin_id in coin_id_map:
            coin_id = coin_id_map[coin_id]
        
        url = f"{self.COINGECKO_API}/simple/price"
        params = {
            'ids': coin_id,
            'vs_currencies': vs_currency,
            'include_market_cap': 'true',
            'include_24hr_vol': 'true',
            'include_24hr_change': 'true',
            'include_last_updated_at': 'true'
        }
        
        data = self._make_request(url, params)
        
        if data and coin_id in data:
            coin_data = data[coin_id]
            return {
                'exchange': 'CoinGecko',
                'symbol': coin_id.upper(),
                'quote': vs_currency.upper(),
                'price': coin_data.get(vs_currency, 0),
                'market_cap': coin_data.get(f'{vs_currency}_market_cap', 0),
                'volume_24h': coin_data.get(f'{vs_currency}_24h_vol', 0),
                'change_percentage_24h': coin_data.get(f'{vs_currency}_24h_change', 0),
                'timestamp': timezone.make_aware(datetime.fromtimestamp(coin_data.get('last_updated_at', 0)), pytz.utc)
            }
        
        return None
    
    def get_btcturk_price(self, symbol: str) -> Optional[Dict]:
        """
        Get real-time TRY prices from BTCTurk
        
        Args:
            symbol: Crypto symbol (BTC, ETH, AVAX)
        
        Returns:
            Dict with TRY price information or None if failed
        """
        pair_symbol = f"{symbol}TRY"
        
        # Get ticker data
        url = f"{self.BTCTURK_API}/ticker"
        params = {'pairSymbol': pair_symbol}
        data = self._make_request(url, params)
        
        if data and 'data' in data and len(data['data']) > 0:
            ticker = data['data'][0]
            return {
                'exchange': 'BTCTurk',
                'symbol': symbol,
                'quote': 'TRY',
                'price': float(ticker.get('last', 0)),
                'bid': float(ticker.get('bid', 0)),
                'ask': float(ticker.get('ask', 0)),
                'volume_24h': float(ticker.get('volume', 0)),
                'change_24h': float(ticker.get('dailyChange', 0)),
                'change_percentage_24h': float(ticker.get('dailyPercent', 0)),
                'high_24h': float(ticker.get('high', 0)),
                'low_24h': float(ticker.get('low', 0)),
                'timestamp': timezone.make_aware(datetime.fromtimestamp(ticker.get('timestamp', 0) / 1000), pytz.utc) if isinstance(ticker.get('timestamp'), (int, float)) else timezone.now()
            }
        
        return None
    
    def get_all_prices(self, symbols: Optional[List[str]] = None) -> Dict[str, Dict]:
        """
        Get prices for multiple cryptocurrencies from all available sources
        
        Args:
            symbols: List of crypto symbols (defaults to SUPPORTED_CRYPTOS)
        
        Returns:
            Dict with prices from all sources
        """
        if not symbols:
            symbols = self.SUPPORTED_CRYPTOS
        
        prices = {}
        
        for symbol in symbols:
            prices[symbol] = {
                'binance_usdt': None,
                'coingecko_usd': None,
                'coingecko_try': None,
                'btcturk_try': None,
                'aggregated': {}
            }
            
            # Fetch from Binance
            binance_data = self.get_binance_price(symbol, 'USDT')
            if binance_data:
                prices[symbol]['binance_usdt'] = binance_data
            
            # Fetch from CoinGecko (USD and TRY)
            coingecko_usd = self.get_coingecko_price(symbol, 'usd')
            if coingecko_usd:
                prices[symbol]['coingecko_usd'] = coingecko_usd
            
            coingecko_try = self.get_coingecko_price(symbol, 'try')
            if coingecko_try:
                prices[symbol]['coingecko_try'] = coingecko_try
            
            # Fetch from BTCTurk
            btcturk_data = self.get_btcturk_price(symbol)
            if btcturk_data:
                prices[symbol]['btcturk_try'] = btcturk_data
            
            # Calculate aggregated prices
            prices[symbol]['aggregated'] = self._aggregate_prices(prices[symbol])
        
        return prices
    
    def _aggregate_prices(self, price_data: Dict) -> Dict:
        """
        Aggregate prices from multiple sources
        
        Args:
            price_data: Dict with prices from different sources
        
        Returns:
            Dict with aggregated price information
        """
        usd_prices = []
        try_prices = []
        
        # Collect USD prices
        if price_data['binance_usdt'] and price_data['binance_usdt']['price']:
            usd_prices.append(price_data['binance_usdt']['price'])
        if price_data['coingecko_usd'] and price_data['coingecko_usd']['price']:
            usd_prices.append(price_data['coingecko_usd']['price'])
        
        # Collect TRY prices
        if price_data['coingecko_try'] and price_data['coingecko_try']['price']:
            try_prices.append(price_data['coingecko_try']['price'])
        if price_data['btcturk_try'] and price_data['btcturk_try']['price']:
            try_prices.append(price_data['btcturk_try']['price'])
        
        aggregated = {
            'usd_price': sum(usd_prices) / len(usd_prices) if usd_prices else None,
            'try_price': sum(try_prices) / len(try_prices) if try_prices else None,
            'sources_count': len([p for p in price_data.values() if p and isinstance(p, dict) and 'price' in p]),
            'last_updated': timezone.now()
        }
        
        # Calculate implied USD/TRY rate if both prices available
        if aggregated['usd_price'] and aggregated['try_price']:
            aggregated['implied_usdtry'] = aggregated['try_price'] / aggregated['usd_price']
        
        return aggregated
    
    def get_historical_data(self, symbol: str, days: int = 30, interval: str = 'daily') -> Optional[List[Dict]]:
        """
        Get historical price data from CoinGecko
        
        Args:
            symbol: Crypto symbol
            days: Number of days of history
            interval: Data interval (daily, hourly)
        
        Returns:
            List of historical data points or None if failed
        """
        coin_id_map = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'AVAX': 'avalanche-2'
        }
        
        coin_id = coin_id_map.get(symbol)
        if not coin_id:
            return None
        
        url = f"{self.COINGECKO_API}/coins/{coin_id}/market_chart"
        params = {
            'vs_currency': 'usd',
            'days': days,
            'interval': interval
        }
        
        data = self._make_request(url, params)
        
        if data and 'prices' in data:
            historical = []
            for timestamp, price in data['prices']:
                historical.append({
                    'timestamp': timezone.make_aware(datetime.fromtimestamp(timestamp / 1000), pytz.utc),
                    'price': price,
                    'symbol': symbol
                })
            return historical
        
        return None
    
    def calculate_portfolio_value(self, holdings: List[Dict], base_currency: str = 'USD') -> Dict:
        """
        Calculate total portfolio value with real-time prices
        
        Args:
            holdings: List of holdings with 'symbol' and 'amount' keys
            base_currency: Target currency for valuation
        
        Returns:
            Dict with portfolio valuation details
        """
        symbols = list(set([h['symbol'] for h in holdings]))
        prices = self.get_all_prices(symbols)
        
        total_value = Decimal('0')
        portfolio_details = []
        
        for holding in holdings:
            symbol = holding['symbol']
            amount = Decimal(str(holding['amount']))
            
            # Get appropriate price based on base currency
            if base_currency == 'USD':
                price = prices[symbol]['aggregated'].get('usd_price', 0)
            elif base_currency == 'TRY':
                price = prices[symbol]['aggregated'].get('try_price', 0)
            else:
                price = 0
            
            if price:
                value = amount * Decimal(str(price))
                total_value += value
                
                portfolio_details.append({
                    'symbol': symbol,
                    'amount': float(amount),
                    'price': float(price),
                    'value': float(value),
                    'percentage': 0  # Will be calculated after total
                })
        
        # Calculate percentages
        if total_value > 0:
            for detail in portfolio_details:
                detail['percentage'] = (Decimal(str(detail['value'])) / total_value * 100).quantize(Decimal('0.01'))
        
        return {
            'total_value': float(total_value),
            'base_currency': base_currency,
            'holdings': portfolio_details,
            'timestamp': timezone.now(),
            'prices': prices
        }


class PortfolioAnalytics:
    """Advanced portfolio analytics and P&L calculations"""
    
    @staticmethod
    def calculate_pnl(holdings: List[Dict], period: str = 'daily') -> Dict:
        """
        Calculate profit and loss for different time periods
        
        Args:
            holdings: List of holdings with purchase info
            period: Time period (daily, weekly, monthly, yearly)
        
        Returns:
            Dict with P&L calculations
        """
        service = CryptoAPIService()
        current_prices = service.get_all_prices()
        
        total_cost = Decimal('0')
        total_current_value = Decimal('0')
        holdings_pnl = []
        
        for holding in holdings:
            symbol = holding['symbol']
            amount = Decimal(str(holding['amount']))
            buy_price = Decimal(str(holding['buy_price']))
            
            # Get current price in same currency as buy price
            if holding.get('currency', 'USD') == 'TRY':
                current_price = current_prices[symbol]['aggregated'].get('try_price', 0)
            else:
                current_price = current_prices[symbol]['aggregated'].get('usd_price', 0)
            
            if current_price:
                current_price = Decimal(str(current_price))
                cost = amount * buy_price
                current_value = amount * current_price
                pnl = current_value - cost
                pnl_percentage = (pnl / cost * 100) if cost > 0 else Decimal('0')
                
                total_cost += cost
                total_current_value += current_value
                
                holdings_pnl.append({
                    'symbol': symbol,
                    'amount': float(amount),
                    'buy_price': float(buy_price),
                    'current_price': float(current_price),
                    'cost': float(cost),
                    'current_value': float(current_value),
                    'pnl': float(pnl),
                    'pnl_percentage': float(pnl_percentage),
                    'status': 'profit' if pnl > 0 else 'loss' if pnl < 0 else 'neutral'
                })
        
        total_pnl = total_current_value - total_cost
        total_pnl_percentage = (total_pnl / total_cost * 100) if total_cost > 0 else Decimal('0')
        
        return {
            'period': period,
            'total_cost': float(total_cost),
            'total_current_value': float(total_current_value),
            'total_pnl': float(total_pnl),
            'total_pnl_percentage': float(total_pnl_percentage),
            'holdings': holdings_pnl,
            'timestamp': timezone.now(),
            'status': 'profit' if total_pnl > 0 else 'loss' if total_pnl < 0 else 'neutral'
        }
    
    @staticmethod
    def calculate_performance_metrics(transactions: List[Dict]) -> Dict:
        """
        Calculate advanced performance metrics
        
        Args:
            transactions: List of transaction history
        
        Returns:
            Dict with performance metrics
        """
        if not transactions:
            return {}
        
        # Sort transactions by date
        sorted_txns = sorted(transactions, key=lambda x: x['date'])
        
        # Calculate metrics
        total_invested = sum([t['amount'] * t['price'] for t in sorted_txns if t['type'] == 'buy'])
        total_sold = sum([t['amount'] * t['price'] for t in sorted_txns if t['type'] == 'sell'])
        
        # Calculate time-weighted return (simplified)
        first_date = sorted_txns[0]['date']
        last_date = sorted_txns[-1]['date']
        days_held = (last_date - first_date).days or 1
        
        # Get current holdings value
        service = CryptoAPIService()
        current_holdings = {}
        
        for txn in sorted_txns:
            symbol = txn['symbol']
            if txn['type'] == 'buy':
                current_holdings[symbol] = current_holdings.get(symbol, 0) + txn['amount']
            elif txn['type'] == 'sell':
                current_holdings[symbol] = current_holdings.get(symbol, 0) - txn['amount']
        
        holdings_list = [{'symbol': k, 'amount': v} for k, v in current_holdings.items() if v > 0]
        portfolio_value = service.calculate_portfolio_value(holdings_list)
        
        current_value = portfolio_value['total_value']
        total_return = current_value + total_sold - total_invested
        return_percentage = (total_return / total_invested * 100) if total_invested > 0 else 0
        
        # Annualized return
        years = days_held / 365
        if years > 0 and total_invested > 0:
            annualized_return = ((current_value / total_invested) ** (1 / years) - 1) * 100
        else:
            annualized_return = 0
        
        return {
            'total_invested': total_invested,
            'total_sold': total_sold,
            'current_value': current_value,
            'total_return': total_return,
            'return_percentage': return_percentage,
            'annualized_return': annualized_return,
            'days_held': days_held,
            'transaction_count': len(sorted_txns),
            'first_transaction': first_date,
            'last_transaction': last_date
        }


# Singleton instance
crypto_service = CryptoAPIService()
portfolio_analytics = PortfolioAnalytics()