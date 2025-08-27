# Multi-stage build for UNIBOS
# Works on AMD64, ARM64 (including Raspberry Pi)

FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY backend/requirements*.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt || \
    pip install --no-cache-dir --user -r requirements_minimal.txt

# Final stage
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    libjpeg62-turbo \
    nginx \
    supervisor \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Set environment variables
ENV PATH=/root/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=unibos_backend.settings.production \
    DB_HOST=db \
    DB_PORT=5432

# Create app user
RUN useradd -m -u 1000 unibos && \
    mkdir -p /app /var/log/unibos /var/run/unibos && \
    chown -R unibos:unibos /app /var/log/unibos /var/run/unibos

# Set working directory
WORKDIR /app

# Copy application
COPY --chown=unibos:unibos backend/ ./backend/
COPY --chown=unibos:unibos src/ ./src/

# Copy configuration files
COPY --chown=unibos:unibos deploy/docker/nginx.conf /etc/nginx/nginx.conf
COPY --chown=unibos:unibos deploy/docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY --chown=unibos:unibos deploy/docker/entrypoint.sh /entrypoint.sh

# Make entrypoint executable
RUN chmod +x /entrypoint.sh

# Create directories
RUN mkdir -p backend/staticfiles backend/media backend/logs

# Switch to app user
USER unibos

# Expose ports
EXPOSE 8000 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/status/ || exit 1

# Entry point
ENTRYPOINT ["/entrypoint.sh"]
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]