"""
Django management command to run EMSC WebSocket listener
Usage: python manage.py emsc_listener
"""

import asyncio
import signal
import logging
from django.core.management.base import BaseCommand
from modules.birlikteyiz.backend.services import start_emsc_listener, stop_emsc_listener

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Start EMSC WebSocket listener for real-time earthquake data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose logging',
        )

    def handle(self, *args, **options):
        # Setup logging
        log_level = logging.DEBUG if options['verbose'] else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        self.stdout.write(self.style.SUCCESS('Starting EMSC WebSocket listener...'))
        self.stdout.write('Press Ctrl+C to stop')

        # Handle graceful shutdown
        loop = asyncio.get_event_loop()

        def signal_handler():
            self.stdout.write(self.style.WARNING('\nShutting down EMSC listener...'))
            asyncio.create_task(stop_emsc_listener())
            loop.stop()

        # Register signal handlers
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, signal_handler)

        try:
            # Run the listener
            loop.run_until_complete(start_emsc_listener())
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('\nInterrupted by user'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))
            logger.error(f"EMSC listener error: {e}", exc_info=True)
        finally:
            self.stdout.write(self.style.SUCCESS('EMSC listener stopped'))
