# Gunicorn configuration file for PyCam

import multiprocessing
from django.db import connections

# Server socket
bind = "0.0.0.0:8000"

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1

# Use sync worker type to avoid gevent threading issues
worker_class = "sync"

# Set threads to 1 to avoid threading issues entirely
threads = 1

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# Logging settings
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# Process naming
proc_name = 'gunicorn_pycam'

# Restart workers after this many requests to clear memory
max_requests = 1000
max_requests_jitter = 50

# Preload app to avoid loading the app multiple times in each worker
preload_app = True

# Timeout settings
timeout = 60
graceful_timeout = 30
keepalive = 5

# Worker connections
worker_connections = 1000

# Important settings for handling database connections
def worker_exit(server, worker):
    """Handle worker exit - clean up resources"""
    connections.close_all()
    server.log.info("Worker exited, cleaned up connections")

def worker_abort(worker):
    """Handle worker abort - clean up resources"""
    connections.close_all()
    worker.log.info("Worker aborted, cleaned up connections")

# Recommended settings for Render
forwarded_allow_ips = "*"
secure_scheme_headers = {"X-Forwarded-Proto": "https"}

class StandaloneApplication(object):
    """Standalone Gunicorn WSGI application."""

    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app


    def run(self):
        """Run the WSGI application with Gunicorn."""
        import gunicorn.app.base

        class WSGIApplication(gunicorn.app.base.BaseApplication):
            def __init__(self, app, options=None):
                self.application = app
                self.options = options or {}
                super(WSGIApplication, self).__init__()

            def load_config(self):
                for key, value in self.options.items():
                    if key in self.cfg.settings and value is not None:
                        self.cfg.set(key.lower(), value)

            def load(self):
                return self.application

        return WSGIApplication(self.application, self.options).run()


if __name__ == '__main__':
    print("This configuration file is meant to be imported by Gunicorn.")
