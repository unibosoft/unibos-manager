"""
Gunicorn configuration for UNIBOS backend with Uvicorn workers
Modern ASGI setup with WebSocket support and improved performance
"""

import multiprocessing
import os

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes - Uvicorn workers for ASGI support
workers = multiprocessing.cpu_count() * 2 + 1  # Recommended formula for CPU-bound apps
worker_class = "uvicorn.workers.UvicornWorker"  # Modern ASGI worker with WebSocket support
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 120
graceful_timeout = 30
keepalive = 5

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 100

# Preload application
preload_app = False

# Enable stdout/stderr logging
capture_output = True
enable_stdio_inheritance = True

# Access log format
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Error log - using backend logs directory
base_dir = os.path.dirname(os.path.abspath(__file__))
errorlog = os.path.join(base_dir, "logs", "gunicorn-error.log")
loglevel = "info"

# Access log
accesslog = os.path.join(base_dir, "logs", "gunicorn-access.log")

# Process naming
proc_name = "unibos_backend"

# Server mechanics
daemon = False
# Run as ubuntu user (not www-data)
user = None  # Will run as the user starting the process
group = None  # Will run as the group of the user starting the process

# Server hooks
def when_ready(server):
    server.log.info("Server is ready. Spawning workers")

def worker_int(worker):
    worker.log.info("worker received INT or QUIT signal")

def pre_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def pre_exec(server):
    server.log.info("Forked child, re-executing.")

def on_starting(server):
    server.log.info("Starting Gunicorn server")

def on_reload(server):
    server.log.info("Reloading Gunicorn server")

# Environment variables
raw_env = [
    "DJANGO_SETTINGS_MODULE=unibos_backend.settings.production",
    f"PYTHONPATH={os.path.dirname(os.path.abspath(__file__))}",
]
