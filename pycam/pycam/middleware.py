import logging

class DatabaseConnectionMiddleware:
    """
    Middleware that ensures database connections are properly managed.

    This middleware no longer closes database connections.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger(__name__)

    def __call__(self, request):
        # Process the request without touching the database connections
        response = self.get_response(request)

        return response
