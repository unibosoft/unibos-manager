# UNIBOS Backend

Secure, scalable Django backend system for the UNIBOS platform, designed to handle millions of users.

## Features

- **JWT Authentication**: Secure authentication with refresh tokens and 2FA support
- **Modular Architecture**: Clean separation of concerns with Django apps
- **Real-time Support**: WebSocket integration for live updates
- **PostgreSQL + PostGIS**: Advanced database features with spatial data support
- **Redis Caching**: High-performance caching and session management
- **Celery Integration**: Asynchronous task processing
- **API Documentation**: Auto-generated OpenAPI/Swagger documentation
- **Security First**: OWASP compliant with extensive security measures
- **Monitoring**: Prometheus metrics and health checks
- **Docker Ready**: Complete containerization support

## Modules

### Authentication (`apps.authentication`)
- JWT-based authentication with refresh tokens
- Two-factor authentication (2FA)
- Session management and device tracking
- Password reset functionality
- Login attempt monitoring

### Users (`apps.users`)
- Extended user model with profiles
- Device management for push notifications
- Notification system
- User preferences and settings

### Currencies (`apps.currencies`)
- Real-time currency exchange rates
- Portfolio management
- Price alerts
- Historical data tracking
- WebSocket support for live updates

### Personal Inflation (`apps.personal_inflation`)
- Personal consumption basket tracking
- Custom inflation calculation
- Product price monitoring
- Store management
- Inflation reports and analysis

### Recaria (`apps.recaria`)
- Space exploration game backend
- Galaxy and solar system management
- Player progression system
- Real-time battles
- Alliance system
- WebSocket support for multiplayer

### Birlikteyiz (`apps.birlikteyiz`)
- Emergency mesh network communication
- LoRa device management
- Disaster zone monitoring
- Resource point tracking
- Network topology analysis
- WebSocket support for real-time updates

## Requirements

- Python 3.11+
- PostgreSQL 15+ with PostGIS
- Redis 7+
- Node.js 18+ (for frontend assets)

## Quick Start

### Using Docker

```bash
# Clone the repository
git clone https://github.com/yourusername/unibos-backend.git
cd unibos-backend

# Copy environment variables
cp .env.example .env
# Edit .env with your configuration

# Start all services
docker-compose up -d

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Access the application
# API: http://localhost:8000/api/v1/
# Admin: http://localhost:8000/admin/
# Swagger: http://localhost:8000/api/v1/schema/swagger/
```

### Manual Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up PostgreSQL database
createdb unibos_db
psql unibos_db -c "CREATE EXTENSION postgis;"

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Run development server
python manage.py runserver
```

## Configuration

### Environment Variables

Key environment variables (see `.env.example` for full list):

- `SECRET_KEY`: Django secret key (generate a strong one)
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `CORS_ALLOWED_ORIGINS`: Comma-separated list of allowed CORS origins

### Database Setup

```sql
-- Create database and user
CREATE USER unibos WITH PASSWORD 'secure_password';
CREATE DATABASE unibos_db OWNER unibos;
\c unibos_db;
CREATE EXTENSION postgis;
CREATE EXTENSION pg_trgm;
CREATE EXTENSION btree_gin;
```

## Development

### Running Tests

```bash
# Run all tests
python manage.py test

# Run with coverage
coverage run --source='.' manage.py test
coverage report

# Run specific app tests
python manage.py test apps.authentication
```

### Code Quality

```bash
# Linting
flake8 .

# Type checking
mypy .

# Format code
black .
```

### Making Migrations

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migration SQL
python manage.py sqlmigrate app_name migration_number
```

## API Documentation

- **OpenAPI Schema**: `/api/v1/schema/`
- **Swagger UI**: `/api/v1/schema/swagger/`
- **ReDoc**: `/api/v1/schema/redoc/`

### Authentication

All API endpoints require JWT authentication:

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "pass"}'

# Use token
curl http://localhost:8000/api/v1/users/me/ \
  -H "Authorization: Bearer <access_token>"
```

## WebSocket Connections

```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:8000/ws/currencies/?token=<jwt_token>');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
};
```

## Production Deployment

### Using the Deployment Script

```bash
chmod +x deploy.sh
./deploy.sh
```

### Manual Deployment

1. Set up server environment
2. Configure PostgreSQL and Redis
3. Set up Nginx reverse proxy
4. Configure SSL with Let's Encrypt
5. Set up systemd services
6. Configure monitoring

### Security Checklist

- [ ] Change default passwords
- [ ] Configure SSL/TLS
- [ ] Set up firewall rules
- [ ] Enable rate limiting
- [ ] Configure CORS properly
- [ ] Set up monitoring alerts
- [ ] Enable audit logging
- [ ] Configure backup strategy

## Monitoring

- **Health Check**: `/health/`
- **Prometheus Metrics**: `/metrics/`
- **Django Admin**: `/admin/`

## Performance Optimization

- Database connection pooling
- Redis caching for frequently accessed data
- Async views for I/O operations
- Celery for background tasks
- Query optimization with select_related/prefetch_related
- Database indexing strategy

## Troubleshooting

### Common Issues

1. **Database connection errors**
   ```bash
   # Check PostgreSQL is running
   sudo systemctl status postgresql
   
   # Check connection
   psql -U unibos -d unibos_db -h localhost
   ```

2. **Redis connection errors**
   ```bash
   # Check Redis is running
   redis-cli ping
   ```

3. **Static files not loading**
   ```bash
   python manage.py collectstatic --noinput
   ```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

This project is part of the UNIBOS platform. All rights reserved.