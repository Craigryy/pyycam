import os
import multiprocessing

# Bind to the port specified by Render
bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"

# Use the WEB_CONCURRENCY environment variable to determine
# the number of workers, or default to CPU count * 2 + 1
workers = int(os.environ.get("WEB_CONCURRENCY", multiprocessing.cpu_count() * 2 + 1))

# Use Gevent worker type for better performance with async operations
worker_class = "gevent"

# Set the number of threads per worker (optional)
threads = int(os.environ.get("THREADS_PER_WORKER", 4))

# Max number of simultaneous clients
worker_connections = 1000

# Timeout in seconds
timeout = 60

# Restart workers after this many requests
max_requests = 1000

# Jitter to add to max_requests
max_requests_jitter = 50

# Process name
proc_name = "pycam_gunicorn"

# Access log settings
accesslog = "-"  # stdout
errorlog = "-"   # stderr
loglevel = os.environ.get("GUNICORN_LOG_LEVEL", "info")

# Recommended settings for Render
forwarded_allow_ips = "*"
secure_scheme_headers = {"X-Forwarded-Proto": "https"}
