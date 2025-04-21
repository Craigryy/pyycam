from django.db import close_old_connections
import logging

class DatabaseConnectionMiddleware:
    """
    Middleware that ensures database connections are properly managed.

    This middleware only closes stale connections at the beginning of requests,
    which is a balanced approach to prevent errors.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger(__name__)

    def __call__(self, request):
        # Only close stale connections, not all active ones
        close_old_connections()

        # Process the request
        response = self.get_response(request)

        # Let Django manage the connection lifecycle naturally
        # No need to close connections here

        return response
