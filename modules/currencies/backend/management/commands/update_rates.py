"""
Management command to update exchange rates from external APIs
Can be run periodically via cron job or Celery beat
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from modules.currencies.backend.services import CurrencyService
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Update exchange rates from external APIs (TCMB and CoinGecko)'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--source',
            type=str,
            choices=['tcmb', 'coingecko', 'all'],
            default='all',
            help='Source to update from',
        )
        parser.add_argument(
            '--cleanup',
            action='store_true',
            help='Clean up old rates after update',
        )
        parser.add_argument(
            '--cleanup-days',
            type=int,
            default=30,
            help='Number of days to keep when cleaning up',
        )
    
    def handle(self, *args, **options):
        source = options['source']
        cleanup = options['cleanup']
        cleanup_days = options['cleanup_days']
        
        service = CurrencyService()
        
        self.stdout.write(f'Starting rate update at {timezone.now()}')
        
        tcmb_count = 0
        crypto_count = 0
        
        # Update TCMB rates
        if source in ['tcmb', 'all']:
            self.stdout.write('Updating TCMB rates...')
            try:
                tcmb_count = service.update_tcmb_rates()
                self.stdout.write(
                    self.style.SUCCESS(f'Updated {tcmb_count} TCMB rates')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Failed to update TCMB rates: {e}')
                )
                logger.error(f'TCMB update failed: {e}', exc_info=True)
        
        # Update CoinGecko rates
        if source in ['coingecko', 'all']:
            self.stdout.write('Updating CoinGecko rates...')
            try:
                crypto_count = service.update_crypto_rates()
                self.stdout.write(
                    self.style.SUCCESS(f'Updated {crypto_count} crypto rates')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Failed to update crypto rates: {e}')
                )
                logger.error(f'CoinGecko update failed: {e}', exc_info=True)
        
        # Clean up old rates if requested
        if cleanup:
            self.stdout.write(f'Cleaning up rates older than {cleanup_days} days...')
            try:
                deleted_count = service.cleanup_old_rates(cleanup_days)
                self.stdout.write(
                    self.style.SUCCESS(f'Deleted {deleted_count} old rates')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Failed to clean up old rates: {e}')
                )
                logger.error(f'Cleanup failed: {e}', exc_info=True)
        
        total_updated = tcmb_count + crypto_count
        self.stdout.write(
            self.style.SUCCESS(
                f'Rate update completed. Total rates updated: {total_updated}'
            )
        )