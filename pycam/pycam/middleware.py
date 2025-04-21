from django.db import close_old_connections, connections
import logging

class DatabaseConnectionMiddleware:
    """
    Middleware that ensures database connections are properly managed.

    This helps manage database connections without closing them too aggressively.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger(__name__)

    def __call__(self, request):
        # Only close old/stale connections, not all connections
        close_old_connections()

        # Process the request
        response = self.get_response(request)

        # Don't close connections after every request, only at the end of the process
        # close_old_connections()  # Removed this line

        return response
