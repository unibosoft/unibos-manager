# Currencies Module Documentation

## Overview
Advanced currency tracking and portfolio management system for UNIBOS with real-time exchange rates, portfolio management, and price alerts.

## Features

### Core Features
- **Real-time Currency Conversion**: Support for 30+ fiat currencies and 15+ cryptocurrencies
- **TCMB Integration**: Official Turkish Central Bank exchange rates
- **CoinGecko Integration**: Cryptocurrency market data
- **Portfolio Management**: Track multiple currency portfolios
- **Price Alerts**: Customizable alerts for rate changes
- **Historical Data**: Charts and analytics for historical rates
- **WebSocket Support**: Real-time updates via WebSocket connections

### Security Features
- **Rate Limiting**: API call throttling to prevent abuse
- **Input Validation**: Comprehensive validation for all inputs
- **SQL Injection Prevention**: Parameterized queries throughout
- **XSS Protection**: Output encoding and CSP headers
- **Authentication**: JWT-based authentication
- **Authorization**: Role-based access control
- **Encryption**: Sensitive data encrypted at rest

## API Endpoints

### Currency Endpoints
```
GET /api/v1/currencies/                    # List all currencies
GET /api/v1/currencies/rates/              # Get current exchange rates
POST /api/v1/currencies/convert/           # Convert between currencies
POST /api/v1/currencies/update-rates/      # Update rates (admin only)
GET /api/v1/currencies/{code}/history/     # Get historical rates
```

### Portfolio Endpoints
```
GET /api/v1/currencies/portfolios/                     # List user portfolios
POST /api/v1/currencies/portfolios/                    # Create portfolio
GET /api/v1/currencies/portfolios/{id}/                # Get portfolio details
PUT /api/v1/currencies/portfolios/{id}/                # Update portfolio
DELETE /api/v1/currencies/portfolios/{id}/             # Delete portfolio
GET /api/v1/currencies/portfolios/{id}/performance/    # Get performance metrics
POST /api/v1/currencies/portfolios/{id}/add-holding/   # Add holding
GET /api/v1/currencies/portfolios/{id}/transactions/   # Get transactions
```

### Alert Endpoints
```
GET /api/v1/currencies/alerts/             # List user alerts
POST /api/v1/currencies/alerts/            # Create alert
PUT /api/v1/currencies/alerts/{id}/        # Update alert
DELETE /api/v1/currencies/alerts/{id}/     # Delete alert
POST /api/v1/currencies/alerts/check/      # Check alerts (admin only)
```

### Market Data Endpoints
```
GET /api/v1/currencies/market-data/        # Get market data
GET /api/v1/currencies/market-data/chart/  # Get chart data
```

## WebSocket Connections

### Real-time Currency Rates
```javascript
// Connect to currency rates WebSocket
const ws = new WebSocket('ws://localhost:8000/ws/currencies/rates/');

// Subscribe to specific currency pair
ws.send(JSON.stringify({
    type: 'subscribe_pair',
    data: {
        base_currency: 'USD',
        target_currency: 'TRY'
    }
}));

// Receive rate updates
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Rate update:', data);
};
```

### Portfolio Updates
```javascript
// Connect to portfolio WebSocket
const portfolioId = 'your-portfolio-id';
const ws = new WebSocket(`ws://localhost:8000/ws/currencies/portfolio/${portfolioId}/`);

// Receive portfolio updates
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Portfolio update:', data);
};
```

### Price Alerts
```javascript
// Connect to alerts WebSocket
const ws = new WebSocket('ws://localhost:8000/ws/currencies/alerts/');

// Receive alert notifications
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'alert_triggered') {
        console.log('Alert triggered:', data);
    }
};
```

## Management Commands

### Initialize Currencies
```bash
python manage.py init_currencies --type all
# Options: --type [fiat|crypto|commodity|all]
#          --force (update existing currencies)
```

### Update Exchange Rates
```bash
python manage.py update_rates --source all
# Options: --source [tcmb|coingecko|all]
#          --cleanup (clean old rates)
#          --cleanup-days 30
```

## Celery Tasks

### Periodic Tasks
Configure in your Celery beat schedule:

```python
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'update-exchange-rates': {
        'task': 'apps.currencies.tasks.update_exchange_rates',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
    },
    'check-currency-alerts': {
        'task': 'apps.currencies.tasks.check_currency_alerts',
        'schedule': crontab(minute='*/1'),  # Every minute
    },
    'cleanup-old-rates': {
        'task': 'apps.currencies.tasks.cleanup_old_rates',
        'schedule': crontab(hour=3, minute=0),  # Daily at 3 AM
    },
    'generate-market-data': {
        'task': 'apps.currencies.tasks.generate_market_data',
        'schedule': crontab(minute=0),  # Every hour
    },
    'calculate-portfolio-performance': {
        'task': 'apps.currencies.tasks.calculate_portfolio_performance',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
    },
}
```

## Database Models

### Currency
- **code**: Primary key (USD, EUR, BTC, etc.)
- **name**: Full currency name
- **symbol**: Currency symbol (₺, $, €, ₿)
- **currency_type**: fiat, crypto, or commodity
- **decimal_places**: Number of decimal places
- **is_active**: Whether currency is active

### ExchangeRate
- **base_currency**: Source currency
- **target_currency**: Target currency
- **rate**: Exchange rate
- **bid/ask**: Bid and ask prices
- **change_24h**: 24-hour change
- **source**: Data source (TCMB, CoinGecko)
- **timestamp**: Rate timestamp

### Portfolio
- **user**: Portfolio owner
- **name**: Portfolio name
- **description**: Optional description
- **is_default**: Default portfolio flag
- **is_public**: Public visibility flag

### PortfolioHolding
- **portfolio**: Parent portfolio
- **currency**: Held currency
- **amount**: Amount held
- **average_buy_price**: Average purchase price

### Transaction
- **portfolio**: Parent portfolio
- **transaction_type**: buy, sell, or transfer
- **currency**: Transaction currency
- **amount**: Transaction amount
- **price**: Transaction price
- **total_value**: Total transaction value
- **fee_amount**: Transaction fee
- **executed_at**: Execution timestamp

### CurrencyAlert
- **user**: Alert owner
- **base_currency**: Base currency to monitor
- **target_currency**: Target currency
- **alert_type**: above, below, or change_percent
- **threshold_value**: Trigger threshold
- **is_active**: Active status
- **notify_email/push/in_app**: Notification preferences

## Configuration

### Environment Variables
```bash
# External APIs
TCMB_API_URL=https://www.tcmb.gov.tr/kurlar/today.xml
COINGECKO_API_URL=https://api.coingecko.com/api/v3
COINGECKO_API_KEY=your_api_key  # Optional for free tier

# Cache Settings
CURRENCY_CACHE_TTL=300  # 5 minutes
PORTFOLIO_CACHE_TTL=900  # 15 minutes

# Rate Limiting
CURRENCY_API_RATE_LIMIT=100/hour
CONVERSION_API_RATE_LIMIT=500/hour

# WebSocket Settings
WS_HEARTBEAT_INTERVAL=30  # seconds
WS_MAX_CONNECTIONS_PER_USER=5
```

### Django Settings
```python
# Add to INSTALLED_APPS
INSTALLED_APPS = [
    ...
    'apps.currencies',
    ...
]

# Celery Configuration
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

# Cache Configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'currencies'
    }
}
```

## Testing

Run tests:
```bash
# Run all tests
python manage.py test apps.currencies

# Run specific test class
python manage.py test apps.currencies.tests.CurrencyAPITests

# Run with coverage
coverage run --source='apps.currencies' manage.py test apps.currencies
coverage report
```

## Performance Optimization

### Database Indexes
- Currency code (primary key)
- ExchangeRate: (base_currency, target_currency, timestamp)
- Portfolio: (user, is_default)
- Transaction: (portfolio, executed_at)

### Caching Strategy
- Exchange rates: 5-minute cache
- Portfolio values: 15-minute cache
- Currency list: 1-hour cache
- Market data: 1-hour cache

### Query Optimization
- Use `select_related()` for foreign keys
- Use `prefetch_related()` for many-to-many
- Batch updates where possible
- Use database views for complex queries

## Security Best Practices

1. **Input Validation**: All inputs validated using Django serializers
2. **Rate Limiting**: Prevent API abuse with throttling
3. **Authentication**: JWT tokens with refresh mechanism
4. **Authorization**: Check portfolio ownership before access
5. **Encryption**: Sensitive data encrypted using Django's encryption
6. **Audit Logging**: All transactions logged for audit trail
7. **Error Handling**: Generic error messages to prevent information leakage
8. **HTTPS Only**: Enforce HTTPS in production
9. **CORS Configuration**: Whitelist allowed origins
10. **SQL Injection Prevention**: Use ORM and parameterized queries

## Monitoring

### Key Metrics
- API response times
- Exchange rate update frequency
- Alert trigger rate
- WebSocket connection count
- Cache hit ratio
- Database query performance

### Logging
```python
import logging

logger = logging.getLogger('currencies')

# Log levels
logger.debug('Debug information')
logger.info('General information')
logger.warning('Warning messages')
logger.error('Error messages')
logger.critical('Critical issues')
```

### Health Checks
- Database connectivity
- Redis connectivity
- External API availability
- WebSocket server status

## Troubleshooting

### Common Issues

#### Exchange rates not updating
1. Check Celery worker is running
2. Verify external API connectivity
3. Check rate limiting hasn't been exceeded
4. Review error logs

#### WebSocket connection issues
1. Verify ASGI server is running
2. Check WebSocket URL is correct
3. Ensure authentication token is valid
4. Review browser console for errors

#### Portfolio calculations incorrect
1. Verify exchange rates are current
2. Check holding amounts are correct
3. Review transaction history
4. Clear cache and recalculate

## Support

For issues or questions:
1. Check the documentation
2. Review error logs
3. Contact the development team

## License

This module is part of the UNIBOS project and follows the project's licensing terms.