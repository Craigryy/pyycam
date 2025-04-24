"""
Custom database backends with retry logic for better error handling
"""
import time
import logging
from django.db.backends.sqlite3.base import DatabaseWrapper as SQLite3DatabaseWrapper
from django.db.utils import OperationalError, InterfaceError, ProgrammingError

logger = logging.getLogger(__name__)


class DatabaseWrapper(SQLite3DatabaseWrapper):
    """
    Database wrapper for SQLite3 that automatically retries operations
    that fail due to connection issues
    """

    def _execute_with_retry(self, cursor, query, params, max_retries=3, retry_delay=0.5):
        """Execute a query with retry logic for better resilience"""
        retry_count = 0
        last_error = None

        while retry_count < max_retries:
            try:
                return super()._execute_wrapper(cursor, query, params)
            except (OperationalError, InterfaceError, ProgrammingError) as e:
                last_error = e
                error_str = str(e)

                # Only retry if it's a connection error
                if "closed database" in error_str or "database is locked" in error_str:
                    retry_count += 1
                    logger.warning(
                        f"Database operation failed (attempt {retry_count}/{max_retries}): {error_str}. "
                        f"Retrying in {retry_delay} seconds..."
                    )

                    # Close the connection and wait
                    self.close()
                    time.sleep(retry_delay)

                    # Try to reconnect
                    try:
                        self.connect()
                        # Get a fresh cursor for the retry
                        cursor = self.create_cursor()
                    except Exception as reconnect_err:
                        logger.error(f"Failed to reconnect: {reconnect_err}")
                else:
                    # If it's not a connection error, don't retry
                    raise

        # If we got here, all retries failed
        logger.error(f"All {max_retries} retry attempts failed. Last error: {last_error}")
        raise last_error

    def _execute_wrapper(self, cursor, query, params):
        """Override the execute wrapper to add retry logic"""
        return self._execute_with_retry(cursor, query, params)
