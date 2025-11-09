"""
Test EMSC WebSocket connection
Usage: python manage.py test_emsc
"""

import asyncio
import logging
from django.core.management.base import BaseCommand
from modules.birlikteyiz.backend.services import EMSCWebSocketClient

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class Command(BaseCommand):
    help = 'Test EMSC WebSocket connection (runs for 60 seconds)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Testing EMSC WebSocket connection...'))
        self.stdout.write('Will listen for 60 seconds')
        self.stdout.write('Press Ctrl+C to stop earlier\n')

        client = EMSCWebSocketClient()

        async def test_connection():
            # Start listening in background
            listen_task = asyncio.create_task(client.start())

            # Wait for 60 seconds or until interrupted
            try:
                await asyncio.sleep(60)
            except KeyboardInterrupt:
                self.stdout.write(self.style.WARNING('\nTest interrupted by user'))
            finally:
                await client.stop()
                listen_task.cancel()
                try:
                    await listen_task
                except asyncio.CancelledError:
                    pass

        try:
            asyncio.run(test_connection())
            self.stdout.write(self.style.SUCCESS('\nTest completed successfully'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\nTest failed: {e}'))
