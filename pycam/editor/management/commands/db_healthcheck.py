from django.core.management.base import BaseCommand
from django.db import connection, close_old_connections
import time
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Check database connection health and restart if needed'

    def add_arguments(self, parser):
        parser.add_argument(
            '--interval',
            type=int,
            default=60,
            help='Check interval in seconds',
        )
        parser.add_argument(
            '--timeout',
            type=int,
            default=0,
            help='Run for specified seconds, or 0 for indefinite',
        )

    def handle(self, *args, **options):
        interval = options['interval']
        timeout = options['timeout']
        start_time = time.time()
        self.stdout.write(self.style.SUCCESS(
            f'Starting database health check (interval={interval}s)'))

        try:
            while True:
                try:
                    # Close any stale connections
                    close_old_connections()

                    # Try to execute a simple query
                    with connection.cursor() as cursor:
                        cursor.execute("SELECT 1")
                        cursor.fetchone()

                    self.stdout.write(
                        self.style.SUCCESS(f'[{time.strftime("%H:%M:%S")}] Database connection OK'))
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'[{time.strftime("%H:%M:%S")}] Database error: {str(e)}'))
                    self.stdout.write(
                        self.style.WARNING('Attempting to close and reestablish all connections...'))

                    try:
                        # More aggressive connection reset
                        close_old_connections()
                        connection.close()
                        time.sleep(1)  # Small delay to allow connections to fully close

                        # Force new connection
                        connection.ensure_connection()

                        self.stdout.write(
                            self.style.SUCCESS('Connection reestablished successfully'))
                    except Exception as reconnect_error:
                        self.stdout.write(
                            self.style.ERROR(f'Failed to reconnect: {str(reconnect_error)}'))

                # Check if we should exit based on timeout
                if timeout > 0 and (time.time() - start_time) > timeout:
                    self.stdout.write(self.style.SUCCESS(f'Timeout reached ({timeout}s). Exiting.'))
                    break

                time.sleep(interval)

        except KeyboardInterrupt:
            self.stdout.write(self.style.SUCCESS('Database health check stopped by user'))
            return
