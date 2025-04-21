import os
import multiprocessing

# Bind to the port specified by Render
bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"

# Number of worker processes - using sync worker
workers = int(os.environ.get("WEB_CONCURRENCY", 4))

# Use sync worker type to avoid gevent threading issues
worker_class = "sync"

# Set threads to 1 to avoid threading issues entirely
threads = 1

# Process name
proc_name = "pycam_gunicorn"

# Restart workers after this many requests to clear memory
max_requests = 1000
max_requests_jitter = 50

# Preload app to avoid loading the app multiple times in each worker
preload_app = True

# Timeout settings
timeout = 120
graceful_timeout = 30
keepalive = 5

# Access log settings
accesslog = "-"  # stdout
errorlog = "-"   # stderr
loglevel = os.environ.get("GUNICORN_LOG_LEVEL", "info")

# Worker connections
worker_connections = 1000

# Important settings for handling database connections
def post_fork(server, worker):
    """Close any database connections to avoid thread/process issues"""
    from django.db import connections
    for conn in connections.all():
        conn.close()

    server.log.info("Worker synced no connections")

def worker_exit(server, worker):
    """Close database connections when worker exits"""
    from django.db import connections
    connections.close_all()
    server.log.info("Worker exited, closed all connections")

def worker_abort(worker):
    """Close database connections when worker aborted"""
    from django.db import connections
    connections.close_all()
    worker.log.info("Worker aborted, closed all connections")

# Recommended settings for Render
forwarded_allow_ips = "*"
secure_scheme_headers = {"X-Forwarded-Proto": "https"}
