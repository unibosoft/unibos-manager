"""
URL configuration for Currencies module
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CurrencyViewSet,
    PortfolioViewSet,
    CurrencyAlertViewSet,
    MarketDataViewSet,
    BankExchangeRateViewSet,
    ChartDataViewSet
)

app_name = 'currencies'

# Create router for viewsets
router = DefaultRouter()
router.register(r'currencies', CurrencyViewSet, basename='currency')
router.register(r'portfolios', PortfolioViewSet, basename='portfolio')
router.register(r'alerts', CurrencyAlertViewSet, basename='alert')
router.register(r'market-data', MarketDataViewSet, basename='marketdata')
router.register(r'bank-rates', BankExchangeRateViewSet, basename='bankrate')
router.register(r'chart-data', ChartDataViewSet, basename='chartdata')

urlpatterns = [
    path('', include(router.urls)),
]

# Additional URL patterns for custom endpoints
urlpatterns += [
    # Currency endpoints
    path('currencies/rates/', CurrencyViewSet.as_view({'get': 'rates'}), name='currency-rates'),
    path('currencies/convert/', CurrencyViewSet.as_view({'post': 'convert'}), name='currency-convert'),
    path('currencies/update-rates/', CurrencyViewSet.as_view({'post': 'update_rates'}), name='currency-update-rates'),
    path('currencies/<str:pk>/history/', CurrencyViewSet.as_view({'get': 'history'}), name='currency-history'),
    
    # Portfolio endpoints (user-centric, no UUID needed)
    path('portfolio/', PortfolioViewSet.as_view({'get': 'my_portfolio'}), name='my-portfolio'),
    path('portfolio/add-asset/', PortfolioViewSet.as_view({'post': 'add_asset'}), name='portfolio-add-asset'),
    path('portfolio/remove-asset/', PortfolioViewSet.as_view({'post': 'remove_asset'}), name='portfolio-remove-asset'),
    path('portfolio/stats/', PortfolioViewSet.as_view({'get': 'stats'}), name='portfolio-stats'),
    path('portfolio/history/', PortfolioViewSet.as_view({'get': 'history'}), name='portfolio-history'),
    
    # Legacy portfolio endpoints (for backward compatibility)
    path('portfolios/<uuid:pk>/performance/', PortfolioViewSet.as_view({'get': 'performance'}), name='portfolio-performance'),
    path('portfolios/<uuid:pk>/add-holding/', PortfolioViewSet.as_view({'post': 'add_holding'}), name='portfolio-add-holding'),
    path('portfolios/<uuid:pk>/transactions/', PortfolioViewSet.as_view({'get': 'transactions'}), name='portfolio-transactions'),
    
    # Alert endpoints
    path('alerts/check/', CurrencyAlertViewSet.as_view({'post': 'check_alerts'}), name='alert-check'),
    
    # Market data endpoints
    path('market-data/chart/', MarketDataViewSet.as_view({'get': 'chart_data'}), name='marketdata-chart'),
    
    # Bank rate endpoints
    path('bank-rates/latest/', BankExchangeRateViewSet.as_view({'get': 'latest'}), name='bankrate-latest'),
    path('bank-rates/compare/', BankExchangeRateViewSet.as_view({'get': 'compare'}), name='bankrate-compare'),
    path('bank-rates/history/', BankExchangeRateViewSet.as_view({'get': 'history'}), name='bankrate-history'),
    path('bank-rates/export/', BankExchangeRateViewSet.as_view({'post': 'export'}), name='bankrate-export'),
    path('bank-rates/import-logs/', BankExchangeRateViewSet.as_view({'get': 'import_logs'}), name='bankrate-import-logs'),
    path('bank-rates/banks/', BankExchangeRateViewSet.as_view({'get': 'banks'}), name='bankrate-banks'),
    path('bank-rates/best-rates/', BankExchangeRateViewSet.as_view({'get': 'best_rates'}), name='bankrate-best-rates'),
    path('bank-rates/realtime-updates/', BankExchangeRateViewSet.as_view({'get': 'realtime_updates'}), name='bankrate-realtime'),
]