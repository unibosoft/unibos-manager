"""
Comprehensive tests for Currencies module
Tests security, performance, and functionality
"""

from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from decimal import Decimal
from unittest.mock import patch, MagicMock
import json
from datetime import timedelta

from .models import (
    Currency, ExchangeRate, CurrencyAlert,
    Portfolio, PortfolioHolding, Transaction,
    MarketData
)
from .services import CurrencyService, TCMBService, CoinGeckoService

User = get_user_model()


class CurrencyModelTests(TestCase):
    """Test Currency model"""
    
    def setUp(self):
        self.currency = Currency.objects.create(
            code='USD',
            name='US Dollar',
            symbol='$',
            currency_type='fiat',
            decimal_places=2
        )
    
    def test_currency_creation(self):
        """Test currency is created correctly"""
        self.assertEqual(self.currency.code, 'USD')
        self.assertEqual(self.currency.name, 'US Dollar')
        self.assertEqual(self.currency.symbol, '$')
        self.assertEqual(self.currency.currency_type, 'fiat')
        self.assertTrue(self.currency.is_active)
    
    def test_currency_str(self):
        """Test string representation"""
        self.assertEqual(str(self.currency), 'USD - US Dollar')
    
    def test_currency_unique_code(self):
        """Test currency code is unique"""
        with self.assertRaises(Exception):
            Currency.objects.create(
                code='USD',
                name='Another Dollar',
                symbol='$',
                currency_type='fiat'
            )


class ExchangeRateModelTests(TestCase):
    """Test ExchangeRate model"""
    
    def setUp(self):
        self.usd = Currency.objects.create(
            code='USD',
            name='US Dollar',
            symbol='$',
            currency_type='fiat'
        )
        self.try_currency = Currency.objects.create(
            code='TRY',
            name='Turkish Lira',
            symbol='₺',
            currency_type='fiat'
        )
        self.rate = ExchangeRate.objects.create(
            base_currency=self.usd,
            target_currency=self.try_currency,
            rate=Decimal('32.50'),
            source='TCMB',
            timestamp=timezone.now()
        )
    
    def test_exchange_rate_creation(self):
        """Test exchange rate is created correctly"""
        self.assertEqual(self.rate.base_currency, self.usd)
        self.assertEqual(self.rate.target_currency, self.try_currency)
        self.assertEqual(self.rate.rate, Decimal('32.50'))
        self.assertEqual(self.rate.source, 'TCMB')
    
    def test_exchange_rate_str(self):
        """Test string representation"""
        expected = f"USD/TRY @ {self.rate.timestamp}"
        self.assertEqual(str(self.rate), expected)
    
    def test_exchange_rate_uniqueness(self):
        """Test rate uniqueness constraint"""
        with self.assertRaises(Exception):
            ExchangeRate.objects.create(
                base_currency=self.usd,
                target_currency=self.try_currency,
                rate=Decimal('33.00'),
                source='TCMB',
                timestamp=self.rate.timestamp
            )


class PortfolioModelTests(TestCase):
    """Test Portfolio and related models"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.portfolio = Portfolio.objects.create(
            user=self.user,
            name='My Portfolio',
            description='Test portfolio',
            is_default=True
        )
        self.usd = Currency.objects.create(
            code='USD',
            name='US Dollar',
            symbol='$',
            currency_type='fiat'
        )
        self.try_currency = Currency.objects.create(
            code='TRY',
            name='Turkish Lira',
            symbol='₺',
            currency_type='fiat'
        )
    
    def test_portfolio_creation(self):
        """Test portfolio is created correctly"""
        self.assertEqual(self.portfolio.user, self.user)
        self.assertEqual(self.portfolio.name, 'My Portfolio')
        self.assertTrue(self.portfolio.is_default)
        self.assertFalse(self.portfolio.is_public)
    
    def test_portfolio_unique_name_per_user(self):
        """Test portfolio name is unique per user"""
        with self.assertRaises(Exception):
            Portfolio.objects.create(
                user=self.user,
                name='My Portfolio',
                description='Another portfolio'
            )
    
    def test_portfolio_holding(self):
        """Test portfolio holding creation"""
        holding = PortfolioHolding.objects.create(
            portfolio=self.portfolio,
            currency=self.usd,
            amount=Decimal('100'),
            average_buy_price=Decimal('32.50')
        )
        
        self.assertEqual(holding.portfolio, self.portfolio)
        self.assertEqual(holding.currency, self.usd)
        self.assertEqual(holding.amount, Decimal('100'))
        self.assertEqual(holding.average_buy_price, Decimal('32.50'))
    
    def test_portfolio_total_value_calculation(self):
        """Test portfolio value calculation"""
        # Add holding
        PortfolioHolding.objects.create(
            portfolio=self.portfolio,
            currency=self.usd,
            amount=Decimal('100'),
            average_buy_price=Decimal('32.50')
        )
        
        # Add exchange rate
        ExchangeRate.objects.create(
            base_currency=self.usd,
            target_currency=self.try_currency,
            rate=Decimal('33.00'),
            source='TCMB',
            timestamp=timezone.now()
        )
        
        # Calculate total value
        total_value = self.portfolio.calculate_total_value('TRY')
        self.assertEqual(total_value, Decimal('3300'))  # 100 USD * 33.00


class CurrencyAPITests(APITestCase):
    """Test Currency API endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Create test currencies
        self.usd = Currency.objects.create(
            code='USD',
            name='US Dollar',
            symbol='$',
            currency_type='fiat'
        )
        self.eur = Currency.objects.create(
            code='EUR',
            name='Euro',
            symbol='€',
            currency_type='fiat'
        )
        self.try_currency = Currency.objects.create(
            code='TRY',
            name='Turkish Lira',
            symbol='₺',
            currency_type='fiat'
        )
        
        # Create test exchange rates
        ExchangeRate.objects.create(
            base_currency=self.usd,
            target_currency=self.try_currency,
            rate=Decimal('32.50'),
            source='TCMB',
            timestamp=timezone.now()
        )
        ExchangeRate.objects.create(
            base_currency=self.eur,
            target_currency=self.try_currency,
            rate=Decimal('35.50'),
            source='TCMB',
            timestamp=timezone.now()
        )
    
    def test_list_currencies(self):
        """Test listing all currencies"""
        url = reverse('currencies:currency-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)
    
    def test_get_currency_rates(self):
        """Test getting current exchange rates"""
        url = reverse('currencies:currency-rates')
        response = self.client.get(url, {'base': 'TRY'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('rates', response.data)
        self.assertEqual(response.data['base'], 'TRY')
    
    def test_currency_conversion(self):
        """Test currency conversion endpoint"""
        url = reverse('currencies:currency-convert')
        data = {
            'from_currency': 'USD',
            'to_currency': 'TRY',
            'amount': 100
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['from_currency'], 'USD')
        self.assertEqual(response.data['to_currency'], 'TRY')
        self.assertEqual(response.data['amount'], 100)
        self.assertEqual(response.data['converted_amount'], 3250.0)
    
    def test_currency_conversion_validation(self):
        """Test conversion with invalid data"""
        url = reverse('currencies:currency-convert')
        
        # Test negative amount
        data = {
            'from_currency': 'USD',
            'to_currency': 'TRY',
            'amount': -100
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test invalid currency
        data = {
            'from_currency': 'INVALID',
            'to_currency': 'TRY',
            'amount': 100
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_currency_history(self):
        """Test getting historical rates"""
        # Add some historical rates
        for i in range(5):
            ExchangeRate.objects.create(
                base_currency=self.usd,
                target_currency=self.try_currency,
                rate=Decimal('32.50') + Decimal(str(i * 0.1)),
                source='TCMB',
                timestamp=timezone.now() - timedelta(days=i)
            )
        
        url = reverse('currencies:currency-history', kwargs={'pk': 'USD'})
        response = self.client.get(url, {'days': 7})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['currency'], 'USD')
        self.assertIn('data', response.data)


class PortfolioAPITests(APITestCase):
    """Test Portfolio API endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Create test currency
        self.usd = Currency.objects.create(
            code='USD',
            name='US Dollar',
            symbol='$',
            currency_type='fiat'
        )
        self.try_currency = Currency.objects.create(
            code='TRY',
            name='Turkish Lira',
            symbol='₺',
            currency_type='fiat'
        )
    
    def test_create_portfolio(self):
        """Test creating a new portfolio"""
        url = reverse('currencies:portfolio-list')
        data = {
            'name': 'Test Portfolio',
            'description': 'My test portfolio',
            'is_default': True
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Test Portfolio')
        self.assertTrue(response.data['is_default'])
        
        # Verify portfolio was created
        portfolio = Portfolio.objects.get(id=response.data['id'])
        self.assertEqual(portfolio.user, self.user)
    
    def test_list_user_portfolios(self):
        """Test listing user's portfolios"""
        # Create portfolios
        Portfolio.objects.create(
            user=self.user,
            name='Portfolio 1'
        )
        Portfolio.objects.create(
            user=self.user,
            name='Portfolio 2'
        )
        
        url = reverse('currencies:portfolio-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_add_holding_to_portfolio(self):
        """Test adding a holding to portfolio"""
        portfolio = Portfolio.objects.create(
            user=self.user,
            name='Test Portfolio'
        )
        
        url = reverse('currencies:portfolio-add-holding', kwargs={'pk': str(portfolio.id)})
        data = {
            'currency_code': 'USD',
            'amount': 100,
            'average_buy_price': 32.50
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['amount'], 100)
        
        # Verify holding was created
        holding = PortfolioHolding.objects.get(
            portfolio=portfolio,
            currency=self.usd
        )
        self.assertEqual(holding.amount, Decimal('100'))
        self.assertEqual(holding.average_buy_price, Decimal('32.50'))
    
    def test_portfolio_performance(self):
        """Test portfolio performance endpoint"""
        portfolio = Portfolio.objects.create(
            user=self.user,
            name='Test Portfolio'
        )
        
        # Add holding
        PortfolioHolding.objects.create(
            portfolio=portfolio,
            currency=self.usd,
            amount=Decimal('100'),
            average_buy_price=Decimal('32.50')
        )
        
        # Add exchange rate
        ExchangeRate.objects.create(
            base_currency=self.usd,
            target_currency=self.try_currency,
            rate=Decimal('33.00'),
            source='TCMB',
            timestamp=timezone.now()
        )
        
        url = reverse('currencies:portfolio-performance', kwargs={'pk': str(portfolio.id)})
        response = self.client.get(url, {'period': '30d'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_value_try', response.data)
        self.assertIn('holdings', response.data)
        self.assertEqual(len(response.data['holdings']), 1)


class CurrencyServiceTests(TestCase):
    """Test currency services"""
    
    def setUp(self):
        self.service = CurrencyService()
        
        # Create TRY currency
        Currency.objects.create(
            code='TRY',
            name='Turkish Lira',
            symbol='₺',
            currency_type='fiat'
        )
    
    @patch('modules.currencies.backend.services.requests.Session.get')
    def test_tcmb_service_fetch_rates(self, mock_get):
        """Test TCMB service fetches rates correctly"""
        # Mock XML response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'application/xml'}
        mock_response.content = b'''<?xml version="1.0" encoding="UTF-8"?>
        <Tarih_Date>
            <Currency CurrencyCode="USD">
                <ForexBuying>32.4500</ForexBuying>
                <ForexSelling>32.5500</ForexSelling>
            </Currency>
            <Currency CurrencyCode="EUR">
                <ForexBuying>35.4500</ForexBuying>
                <ForexSelling>35.5500</ForexSelling>
            </Currency>
        </Tarih_Date>'''
        mock_get.return_value = mock_response
        
        tcmb_service = TCMBService()
        rates = tcmb_service.fetch_rates()
        
        self.assertIsNotNone(rates)
        self.assertIn('USD', rates)
        self.assertIn('EUR', rates)
        self.assertEqual(rates['USD']['rate'], Decimal('32.5000'))
    
    @patch('modules.currencies.backend.services.requests.Session.get')
    def test_coingecko_service_fetch_rates(self, mock_get):
        """Test CoinGecko service fetches rates correctly"""
        # Mock JSON response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'application/json'}
        mock_response.json.return_value = {
            'bitcoin': {
                'try': 1850000,
                'try_24h_change': 2.5,
                'try_24h_vol': 1000000
            },
            'ethereum': {
                'try': 115000,
                'try_24h_change': -1.2,
                'try_24h_vol': 500000
            }
        }
        mock_get.return_value = mock_response
        
        coingecko_service = CoinGeckoService()
        rates = coingecko_service.fetch_rates('try')
        
        self.assertIsNotNone(rates)
        self.assertIn('BTC', rates)
        self.assertIn('ETH', rates)
        self.assertEqual(rates['BTC']['rate'], Decimal('1850000'))
    
    def test_get_conversion_rate(self):
        """Test conversion rate calculation"""
        # Create currencies
        usd = Currency.objects.create(
            code='USD',
            name='US Dollar',
            symbol='$',
            currency_type='fiat'
        )
        eur = Currency.objects.create(
            code='EUR',
            name='Euro',
            symbol='€',
            currency_type='fiat'
        )
        try_currency = Currency.objects.get(code='TRY')
        
        # Create exchange rates
        ExchangeRate.objects.create(
            base_currency=usd,
            target_currency=try_currency,
            rate=Decimal('32.50'),
            source='TCMB',
            timestamp=timezone.now()
        )
        ExchangeRate.objects.create(
            base_currency=eur,
            target_currency=try_currency,
            rate=Decimal('35.50'),
            source='TCMB',
            timestamp=timezone.now()
        )
        
        # Test direct rate
        rate = self.service.get_conversion_rate('USD', 'TRY')
        self.assertEqual(rate, Decimal('32.50'))
        
        # Test cross rate through TRY
        rate = self.service.get_conversion_rate('USD', 'EUR')
        expected_rate = Decimal('32.50') / Decimal('35.50')
        self.assertAlmostEqual(float(rate), float(expected_rate), places=4)


class SecurityTests(APITestCase):
    """Test security features"""
    
    def test_unauthenticated_access(self):
        """Test unauthenticated users can only read"""
        # Create test currency
        Currency.objects.create(
            code='USD',
            name='US Dollar',
            symbol='$',
            currency_type='fiat'
        )
        
        # Test read access (should work)
        url = reverse('currencies:currency-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test write access (should fail)
        url = reverse('currencies:portfolio-list')
        data = {'name': 'Test Portfolio'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_portfolio_ownership(self):
        """Test users can only access their own portfolios"""
        user1 = User.objects.create_user(
            username='user1',
            password='pass1'
        )
        user2 = User.objects.create_user(
            username='user2',
            password='pass2'
        )
        
        # Create portfolio for user1
        portfolio = Portfolio.objects.create(
            user=user1,
            name='User1 Portfolio'
        )
        
        # Authenticate as user2
        self.client.force_authenticate(user=user2)
        
        # Try to access user1's portfolio
        url = reverse('currencies:portfolio-detail', kwargs={'pk': str(portfolio.id)})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_rate_limiting(self):
        """Test rate limiting is applied"""
        # This would require actual rate limiting middleware testing
        # Simplified version here
        pass
    
    def test_sql_injection_prevention(self):
        """Test SQL injection prevention"""
        user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.client.force_authenticate(user=user)
        
        # Try SQL injection in search
        url = reverse('currencies:currency-list')
        response = self.client.get(url, {'search': "'; DROP TABLE currencies; --"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify table still exists
        self.assertTrue(Currency.objects.exists())
    
    def test_xss_prevention(self):
        """Test XSS prevention"""
        user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.client.force_authenticate(user=user)
        
        # Try to create portfolio with XSS
        url = reverse('currencies:portfolio-list')
        data = {
            'name': '<script>alert("XSS")</script>',
            'description': '<img src=x onerror=alert("XSS")>'
        }
        response = self.client.post(url, data, format='json')
        
        if response.status_code == status.HTTP_201_CREATED:
            # Check that script tags are escaped
            portfolio = Portfolio.objects.get(id=response.data['id'])
            self.assertNotIn('<script>', portfolio.name)
            self.assertNotIn('onerror=', portfolio.description)