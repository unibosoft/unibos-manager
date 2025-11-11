"""
Daphne configuration for UNIBOS backend
ASGI server configuration for WebSocket support
"""

import multiprocessing
import os

# Server socket
bind = "0.0.0.0:8000"

# Worker processes - Daphne uses different process model than Gunicorn
# For production, typically use 1-2x CPU cores
workers = multiprocessing.cpu_count() * 2

# Connection settings
# Maximum number of concurrent connections per worker
max_requests = 10000

# Timeout settings (in seconds)
# Daphne handles long-lived WebSocket connections
timeout = 300  # 5 minutes for WebSocket connections
keepalive_timeout = 60

# Logging configuration
# Enable stdout/stderr logging
verbosity = 1  # 0=quiet, 1=normal, 2=verbose, 3=very verbose

# Access log format - similar to Gunicorn
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Error log - using backend logs directory
base_dir = os.path.dirname(os.path.abspath(__file__))
error_log = os.path.join(base_dir, "logs", "daphne-error.log")

# Access log
access_log = os.path.join(base_dir, "logs", "daphne-access.log")

# Process naming
process_name = "unibos_daphne"

# WebSocket specific settings
websocket_timeout = 86400  # 24 hours for long-lived WebSocket connections
websocket_connect_timeout = 5  # 5 seconds to establish WebSocket connection

# Application path
application = "unibos_backend.asgi:application"

# Proxy headers - trust X-Forwarded-* headers from nginx
proxy_headers = True

# Buffer size for WebSocket messages (in bytes)
ws_max_message_size = 1048576  # 1MB

# Channel layer settings (uses Redis)
# These are configured in Django settings, not here
# But Daphne needs to know about them for proper operation

# Security settings
# Allowed hosts should be configured in Django settings
# This is just for reference
# allowed_hosts = ["recaria.org", "localhost", "127.0.0.1"]

# Performance tuning
# Maximum backlog for the socket
backlog = 2048

# Root path for static files (served by nginx in production)
# static_root = os.path.join(base_dir, "staticfiles")

# Note: Unlike Gunicorn, Daphne is designed specifically for ASGI
# and handles WebSocket connections natively without special worker classes
