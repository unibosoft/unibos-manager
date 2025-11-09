"""
Management command to import bank exchange rates from Firebase
"""

import requests
import logging
from datetime import datetime
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from modules.currencies.backend.models import BankExchangeRate, BankRateImportLog

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Import bank exchange rates from Firebase database'
    
    FIREBASE_URL = 'https://findmeonphotos-default-rtdb.europe-west1.firebasedatabase.app/kurlar.json'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--update-only',
            action='store_true',
            help='Only import new entries (skip existing ones)',
        )
        parser.add_argument(
            '--from-date',
            type=str,
            help='Import entries from this date (YYYY-MM-DD)',
        )
        parser.add_argument(
            '--to-date',
            type=str,
            help='Import entries up to this date (YYYY-MM-DD)',
        )
        parser.add_argument(
            '--bank',
            type=str,
            choices=['Akbank', 'Garanti', 'YKB'],
            help='Import only for specific bank',
        )
        parser.add_argument(
            '--currency',
            type=str,
            choices=['USDTRY', 'EURTRY', 'XAUTRY'],
            help='Import only for specific currency pair',
        )
    
    def handle(self, *args, **options):
        """Main command execution"""
        self.stdout.write(self.style.SUCCESS('Starting bank rates import...'))
        
        # Create import log
        import_log = BankRateImportLog.objects.create(
            import_type='manual',
            source_url=self.FIREBASE_URL,
            status='in_progress'
        )
        
        try:
            # Fetch data from Firebase
            self.stdout.write('Fetching data from Firebase...')
            response = requests.get(self.FIREBASE_URL, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if not data:
                raise ValueError('No data received from Firebase')
            
            self.stdout.write(f'Found {len(data)} entries to process')
            
            # Process the data
            stats = self.process_data(data, options, import_log)
            
            # Update import log with statistics
            import_log.total_entries = stats['total']
            import_log.new_entries = stats['new']
            import_log.updated_entries = stats['updated']
            import_log.failed_entries = stats['failed']
            import_log.status = 'completed'
            import_log.completed_at = timezone.now()
            
            # Calculate duration
            duration = (import_log.completed_at - import_log.started_at).total_seconds()
            import_log.duration_seconds = int(duration)
            import_log.save()
            
            # Print summary
            self.stdout.write(self.style.SUCCESS('\n' + '='*50))
            self.stdout.write(self.style.SUCCESS('Import completed successfully!'))
            self.stdout.write(f'Total entries processed: {stats["total"]}')
            self.stdout.write(f'New entries: {stats["new"]}')
            self.stdout.write(f'Updated entries: {stats["updated"]}')
            self.stdout.write(f'Failed entries: {stats["failed"]}')
            self.stdout.write(f'Skipped entries: {stats["skipped"]}')
            self.stdout.write(f'Duration: {duration:.2f} seconds')
            
        except Exception as e:
            import_log.status = 'failed'
            import_log.error_message = str(e)
            import_log.completed_at = timezone.now()
            import_log.save()
            
            self.stdout.write(self.style.ERROR(f'Import failed: {str(e)}'))
            logger.exception('Bank rates import failed')
            raise
    
    def process_data(self, data, options, import_log):
        """Process the Firebase data and import to database"""
        stats = {
            'total': 0,
            'new': 0,
            'updated': 0,
            'failed': 0,
            'skipped': 0
        }
        
        # Parse date filters if provided
        from_date = None
        to_date = None
        if options['from_date']:
            from_date = datetime.strptime(options['from_date'], '%Y-%m-%d').date()
        if options['to_date']:
            to_date = datetime.strptime(options['to_date'], '%Y-%m-%d').date()
        
        # Process each entry
        total_entries = len(data)
        processed = 0
        
        for entry_id, entry_data in data.items():
            processed += 1
            
            # Show progress every 100 entries
            if processed % 100 == 0:
                self.stdout.write(f'Processing: {processed}/{total_entries} ({processed*100/total_entries:.1f}%)')
            
            try:
                # Skip if no timestamp
                if 'zaman' not in entry_data:
                    stats['skipped'] += 1
                    continue
                
                # Parse timestamp
                timestamp_ms = entry_data['zaman']
                timestamp = datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)
                date = timestamp.date()
                
                # Apply date filters
                if from_date and date < from_date:
                    stats['skipped'] += 1
                    continue
                if to_date and date > to_date:
                    stats['skipped'] += 1
                    continue
                
                # Process bank data
                if 'data' in entry_data:
                    for bank_data in entry_data['data']:
                        result = self.process_bank_entry(
                            entry_id,
                            bank_data,
                            timestamp,
                            date,
                            options
                        )
                        stats[result] += 1
                        stats['total'] += 1
                
            except Exception as e:
                logger.error(f'Error processing entry {entry_id}: {str(e)}')
                stats['failed'] += 1
                
                # Store error details
                if not import_log.error_details:
                    import_log.error_details = {}
                import_log.error_details[entry_id] = str(e)
                import_log.save()
        
        return stats
    
    def process_bank_entry(self, firebase_id, bank_data, timestamp, date, options):
        """Process a single bank entry"""
        try:
            bank_name = bank_data.get('banka')
            
            # Apply bank filter if specified
            if options['bank'] and bank_name != options['bank']:
                return 'skipped'
            
            if not bank_name or bank_name not in ['Akbank', 'Garanti', 'YKB']:
                logger.warning(f'Unknown bank: {bank_name}')
                return 'failed'
            
            # Process each currency rate
            for rate_data in bank_data.get('banka_kuru', []):
                currency_pair = rate_data.get('kur')
                
                # Apply currency filter if specified
                if options['currency'] and currency_pair != options['currency']:
                    continue
                
                if not currency_pair or currency_pair not in ['USDTRY', 'EURTRY', 'XAUTRY']:
                    logger.warning(f'Unknown currency pair: {currency_pair}')
                    continue
                
                # Parse rates (handle both string and float formats)
                buy_rate = Decimal(str(rate_data.get('alis', 0)))
                sell_rate = Decimal(str(rate_data.get('satis', 0)))
                
                # Create unique entry ID
                entry_id = f"{firebase_id}_{bank_name}_{currency_pair}"
                
                # Check if entry exists
                existing_entry = BankExchangeRate.objects.filter(entry_id=entry_id).first()
                
                if existing_entry:
                    if options['update_only']:
                        return 'skipped'
                    
                    # Update existing entry if rates changed
                    if (existing_entry.buy_rate != buy_rate or 
                        existing_entry.sell_rate != sell_rate):
                        
                        existing_entry.buy_rate = buy_rate
                        existing_entry.sell_rate = sell_rate
                        existing_entry.save()
                        return 'updated'
                    return 'skipped'
                
                # Get previous rates for change calculation
                previous = BankExchangeRate.objects.filter(
                    bank=bank_name,
                    currency_pair=currency_pair,
                    timestamp__lt=timestamp
                ).order_by('-timestamp').first()
                
                # Create new entry
                with transaction.atomic():
                    BankExchangeRate.objects.create(
                        entry_id=entry_id,
                        bank=bank_name,
                        currency_pair=currency_pair,
                        buy_rate=buy_rate,
                        sell_rate=sell_rate,
                        date=date,
                        timestamp=timestamp,
                        previous_buy_rate=previous.buy_rate if previous else None,
                        previous_sell_rate=previous.sell_rate if previous else None
                    )
                
                return 'new'
            
            return 'skipped'
            
        except Exception as e:
            logger.error(f'Error processing bank entry: {str(e)}')
            return 'failed'