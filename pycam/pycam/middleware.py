from django.db import close_old_connections

class DatabaseConnectionMiddleware:
    """
    Middleware that ensures database connections are properly closed.

    This helps avoid the "DatabaseWrapper objects created in a thread can only be used in that same thread" error
    by ensuring connections are closed at the beginning and end of each request.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Close connections before processing the request
        close_old_connections()

        # Process the request
        response = self.get_response(request)

        # Close connections after processing the request
        close_old_connections()

        return response
