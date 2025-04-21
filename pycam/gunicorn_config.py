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
    """Initialize worker environment after fork"""
    server.log.info("Worker initialized")

def worker_exit(server, worker):
    """Handle worker exit"""
    server.log.info("Worker exited")

def worker_abort(worker):
    """Handle worker abort"""
    worker.log.info("Worker aborted")

# Recommended settings for Render
forwarded_allow_ips = "*"
secure_scheme_headers = {"X-Forwarded-Proto": "https"}
