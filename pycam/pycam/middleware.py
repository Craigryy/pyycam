from django.db import close_old_connections, connections, connection
from django.db.utils import OperationalError, ProgrammingError, InterfaceError
import logging

class DatabaseConnectionMiddleware:
    """
    Middleware that ensures database connections are properly managed.

    This middleware handles database reconnection as needed to prevent
    "Cannot operate on a closed database" errors.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger(__name__)

    def __call__(self, request):
        # Close any stale connections
        close_old_connections()

        # Ensure database connection is working
        try:
            # Try a simple query to test the connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
        except (OperationalError, ProgrammingError, InterfaceError) as e:
            self.logger.warning(f"Database connection error: {e}. Reconnecting...")
            # Force close and reopen connection
            connection.close()
            connection.connect()

        try:
            # Process the request
            response = self.get_response(request)
            return response
        finally:
            # Always close connections in finally block to ensure it runs
            close_old_connections()
