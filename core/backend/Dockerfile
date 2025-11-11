# Build stage
FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    libgeos-dev \
    libproj-dev \
    gdal-bin \
    libgdal-dev \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libgeos-c1v5 \
    libproj19 \
    libgdal28 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r django && useradd -r -g django django

# Copy Python dependencies from builder
COPY --from=builder /root/.local /home/django/.local

# Set environment variables
ENV PATH=/home/django/.local/bin:$PATH
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=unibos_backend.settings.production

# Set work directory
WORKDIR /app

# Copy application code
COPY --chown=django:django . .

# Create necessary directories
RUN mkdir -p /app/static /app/media /app/logs && \
    chown -R django:django /app

# Switch to non-root user
USER django

# Collect static files
RUN python manage.py collectstatic --noinput

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health/quick/ || exit 1

# Expose port
EXPOSE 8000

# Run gunicorn
CMD ["gunicorn", "unibos_backend.asgi:application", "--config", "gunicorn.conf.py"]