from django.db import close_old_connections
from django.db.utils import OperationalError, ProgrammingError, InterfaceError
import logging


class DatabaseConnectionMiddleware:
    """
    Middleware that manages database connections to prevent
    "Cannot operate on a closed database" errors.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger(__name__)

    def __call__(self, request):
        # Close any stale connections at the start of the request
        close_old_connections()

        # Process the request
        response = self.get_response(request)

        # Close all connections at the end of the request
        close_old_connections()

        return response
