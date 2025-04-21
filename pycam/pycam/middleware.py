from django.db import close_old_connections, connection
from django.db.utils import OperationalError, ProgrammingError, InterfaceError
import logging
import time

class DatabaseConnectionMiddleware:
    """
    Enhanced middleware that aggressively manages database connections
    to prevent "Cannot operate on a closed database" errors.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger(__name__)

    def ensure_connection(self):
        """Try to establish a database connection with retries."""
        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                # First close any existing connections
                connection.close()

                # Then try to establish a new one
                connection.ensure_connection()

                # Test if it works
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")

                return True  # Connection successful
            except (OperationalError, ProgrammingError, InterfaceError) as e:
                retry_count += 1
                self.logger.warning(f"Database connection error (attempt {retry_count}/{max_retries}): {e}")

                if retry_count >= max_retries:
                    self.logger.error(f"Failed to establish database connection after {max_retries} attempts")
                    return False

                # Wait a bit before retrying
                time.sleep(0.5)

        return False

    def __call__(self, request):
        # First close any stale connections
        close_old_connections()

        # Ensure we have a working connection before processing
        self.ensure_connection()

        try:
            # Process the request
            response = self.get_response(request)
            return response
        except (OperationalError, ProgrammingError, InterfaceError) as e:
            # If we encounter database errors during request processing
            self.logger.error(f"Database error during request: {e}")
            self.ensure_connection()  # Try to reconnect
            raise  # Re-raise the exception
        finally:
            # Always close connections at the end
            close_old_connections()
