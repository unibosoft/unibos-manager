"""
Management command to import bank exchange rates from Firebase
Supports full import and recent-only options with progress tracking
"""

import requests
import json
import sys
from datetime import datetime, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from django.db.models import Q
from tqdm import tqdm
import pytz

from modules.currencies.backend.models import BankExchangeRate, BankRateImportLog


class Command(BaseCommand):
    help = 'Import bank exchange rates from Firebase database'
    
    FIREBASE_URL = 'https://findmeonphotos-default-rtdb.europe-west1.firebasedatabase.app/kurlar.json'
    
    # Bank mapping - Firebase to Django model
    BANK_MAPPING = {
        'TCMB': 'TCMB',
        'Akbank': 'Akbank',
        'Garanti': 'Garanti',
        'Garanti BBVA': 'Garanti',
        'YKB': 'YKB',
        'Yapı Kredi': 'YKB',
        'Ziraat': 'Ziraat',
        'Halkbank': 'Halkbank',
        'Vakıfbank': 'Vakıfbank',
        'İş Bankası': 'İşbank',
        'ING': 'ING',
        'QNB': 'QNB',
        'Denizbank': 'Denizbank',
        'TEB': 'TEB',
    }
    
    # Currency pair mapping
    CURRENCY_MAPPING = {
        'USDTRY': 'USDTRY',
        'EURTRY': 'EURTRY',
        'XAUTRY': 'XAUTRY',
        'GBPTRY': 'GBPTRY',
        'CHFTRY': 'CHFTRY',
        'JPYTRY': 'JPYTRY',
    }
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--full',
            action='store_true',
            help='Import all data from Firebase (default: last 30 days)'
        )
        parser.add_argument(
            '--recent',
            type=int,
            default=30,
            help='Number of days to import (default: 30)'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Batch size for database inserts (default: 100)'
        )
        parser.add_argument(
            '--update-existing',
            action='store_true',
            help='Update existing records if they differ'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run without actually saving to database'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed progress information'
        )
    
    def handle(self, *args, **options):
        """Main command handler"""
        self.stdout.write(self.style.SUCCESS('Starting Firebase import...'))
        
        # Parse options
        full_import = options['full']
        recent_days = options['recent']
        batch_size = options['batch_size']
        update_existing = options['update_existing']
        dry_run = options['dry_run']
        verbose = options['verbose']
        
        # Create import log
        import_log = None
        if not dry_run:
            import_log = BankRateImportLog.objects.create(
                import_type='manual',
                source_url=self.FIREBASE_URL,
                status='in_progress'
            )
        
        try:
            # Fetch data from Firebase
            self.stdout.write('Fetching data from Firebase...')
            response = requests.get(self.FIREBASE_URL, timeout=60)
            response.raise_for_status()
            data = response.json()
            
            if not data:
                raise CommandError('No data received from Firebase')
            
            self.stdout.write(f'Received {len(data)} entries from Firebase')
            
            # Determine cutoff date
            cutoff_date = None
            if not full_import:
                istanbul_tz = pytz.timezone('Europe/Istanbul')
                cutoff_date = datetime.now(istanbul_tz) - timedelta(days=recent_days)
                self.stdout.write(f'Importing data from last {recent_days} days (since {cutoff_date})')
            else:
                self.stdout.write('Importing all data (full import)')
            
            # Get existing entry IDs for duplicate checking
            existing_ids = set(BankExchangeRate.objects.values_list('entry_id', flat=True))
            self.stdout.write(f'Found {len(existing_ids)} existing entries in database')
            
            # Process data
            stats = {
                'total': 0,
                'new': 0,
                'updated': 0,
                'skipped': 0,
                'failed': 0,
                'errors': []
            }
            
            # Prepare batch for bulk insert
            batch = []
            updates = []
            
            # Sort entries by timestamp for chronological processing
            sorted_entries = sorted(
                data.items(),
                key=lambda x: x[1].get('zaman', 0) if isinstance(x[1], dict) else 0
            )
            
            # Use tqdm for progress bar
            with tqdm(total=len(sorted_entries), desc='Processing entries') as pbar:
                for entry_id, entry_data in sorted_entries:
                    pbar.update(1)
                    
                    try:
                        # Validate entry data
                        if not isinstance(entry_data, dict) or 'zaman' not in entry_data:
                            stats['skipped'] += 1
                            if verbose:
                                self.stdout.write(f'Skipping invalid entry: {entry_id}')
                            continue
                        
                        # Parse timestamp
                        timestamp_ms = entry_data['zaman']
                        istanbul_tz = pytz.timezone('Europe/Istanbul')
                        timestamp = datetime.fromtimestamp(
                            timestamp_ms / 1000,
                            tz=istanbul_tz
                        )
                        
                        # Check cutoff date
                        if cutoff_date and timestamp < cutoff_date:
                            stats['skipped'] += 1
                            continue
                        
                        date = timestamp.date()
                        
                        # Process bank data
                        if 'data' not in entry_data or not isinstance(entry_data['data'], list):
                            stats['skipped'] += 1
                            continue
                        
                        for bank_data in entry_data['data']:
                            if not isinstance(bank_data, dict):
                                continue
                            
                            bank_name_raw = bank_data.get('banka', '')
                            bank_name = self.BANK_MAPPING.get(bank_name_raw)
                            
                            if not bank_name:
                                if verbose:
                                    self.stdout.write(
                                        self.style.WARNING(f'Unknown bank: {bank_name_raw}')
                                    )
                                continue
                            
                            # Process each currency rate
                            for rate_data in bank_data.get('banka_kuru', []):
                                if not isinstance(rate_data, dict):
                                    continue
                                
                                currency_pair_raw = rate_data.get('kur', '')
                                currency_pair = self.CURRENCY_MAPPING.get(currency_pair_raw)
                                
                                if not currency_pair:
                                    if verbose:
                                        self.stdout.write(
                                            self.style.WARNING(f'Unknown currency: {currency_pair_raw}')
                                        )
                                    continue
                                
                                # Parse rates
                                try:
                                    buy_rate = Decimal(str(rate_data.get('alis', 0)))
                                    sell_rate = Decimal(str(rate_data.get('satis', 0)))
                                    
                                    # Skip invalid rates
                                    if buy_rate <= 0 or sell_rate <= 0:
                                        stats['skipped'] += 1
                                        continue
                                    
                                except (ValueError, TypeError, InvalidOperation):
                                    stats['failed'] += 1
                                    continue
                                
                                # Create unique entry ID
                                unique_entry_id = f"{entry_id}_{bank_name}_{currency_pair}"
                                
                                # Check if exists
                                if unique_entry_id in existing_ids:
                                    if update_existing:
                                        # Check if needs update
                                        existing = BankExchangeRate.objects.filter(
                                            entry_id=unique_entry_id
                                        ).first()
                                        
                                        if existing and (
                                            existing.buy_rate != buy_rate or
                                            existing.sell_rate != sell_rate
                                        ):
                                            updates.append({
                                                'entry': existing,
                                                'buy_rate': buy_rate,
                                                'sell_rate': sell_rate
                                            })
                                            stats['updated'] += 1
                                        else:
                                            stats['skipped'] += 1
                                    else:
                                        stats['skipped'] += 1
                                    continue
                                
                                # Get previous rates for change calculation
                                previous = None
                                if not dry_run:
                                    previous = BankExchangeRate.objects.filter(
                                        bank=bank_name,
                                        currency_pair=currency_pair,
                                        timestamp__lt=timestamp
                                    ).order_by('-timestamp').first()
                                
                                # Create new entry
                                new_entry = BankExchangeRate(
                                    entry_id=unique_entry_id,
                                    bank=bank_name,
                                    currency_pair=currency_pair,
                                    buy_rate=buy_rate,
                                    sell_rate=sell_rate,
                                    date=date,
                                    timestamp=timestamp,
                                    previous_buy_rate=previous.buy_rate if previous else None,
                                    previous_sell_rate=previous.sell_rate if previous else None
                                )
                                
                                batch.append(new_entry)
                                stats['new'] += 1
                                stats['total'] += 1
                                
                                # Save batch if reached batch size
                                if len(batch) >= batch_size and not dry_run:
                                    self._save_batch(batch)
                                    batch = []
                                    pbar.set_description(f'Saved {stats["new"]} new entries')
                    
                    except Exception as e:
                        stats['failed'] += 1
                        stats['errors'].append({
                            'entry_id': entry_id,
                            'error': str(e)
                        })
                        if verbose:
                            self.stdout.write(
                                self.style.ERROR(f'Error processing entry {entry_id}: {str(e)}')
                            )
            
            # Save remaining batch
            if batch and not dry_run:
                self._save_batch(batch)
            
            # Process updates
            if updates and not dry_run:
                self.stdout.write(f'Updating {len(updates)} existing entries...')
                for update_data in updates:
                    entry = update_data['entry']
                    entry.buy_rate = update_data['buy_rate']
                    entry.sell_rate = update_data['sell_rate']
                    entry.save()
            
            # Update import log
            if import_log:
                import_log.total_entries = stats['total']
                import_log.new_entries = stats['new']
                import_log.updated_entries = stats['updated']
                import_log.failed_entries = stats['failed']
                import_log.status = 'completed'
                import_log.completed_at = timezone.now()
                
                # Calculate duration
                duration = (import_log.completed_at - import_log.started_at).total_seconds()
                import_log.duration_seconds = int(duration)
                
                # Store error details
                if stats['errors']:
                    import_log.error_details = {
                        'errors': stats['errors'][:100]  # Store first 100 errors
                    }
                
                import_log.save()
            
            # Print summary
            self.stdout.write(self.style.SUCCESS('\n' + '='*50))
            self.stdout.write(self.style.SUCCESS('Import Summary:'))
            self.stdout.write(f'  Total processed: {stats["total"]}')
            self.stdout.write(self.style.SUCCESS(f'  New entries: {stats["new"]}'))
            if update_existing:
                self.stdout.write(self.style.WARNING(f'  Updated entries: {stats["updated"]}'))
            self.stdout.write(f'  Skipped entries: {stats["skipped"]}')
            if stats['failed'] > 0:
                self.stdout.write(self.style.ERROR(f'  Failed entries: {stats["failed"]}'))
            
            if dry_run:
                self.stdout.write(self.style.WARNING('\nDRY RUN - No data was saved to database'))
            
            self.stdout.write(self.style.SUCCESS('\nImport completed successfully!'))
            
        except requests.RequestException as e:
            error_msg = f'Failed to fetch data from Firebase: {str(e)}'
            self.stdout.write(self.style.ERROR(error_msg))
            
            if import_log:
                import_log.status = 'failed'
                import_log.error_message = error_msg
                import_log.completed_at = timezone.now()
                import_log.save()
            
            raise CommandError(error_msg)
        
        except Exception as e:
            error_msg = f'Import failed: {str(e)}'
            self.stdout.write(self.style.ERROR(error_msg))
            
            if import_log:
                import_log.status = 'failed'
                import_log.error_message = error_msg
                import_log.completed_at = timezone.now()
                import_log.save()
            
            raise CommandError(error_msg)
    
    def _save_batch(self, batch):
        """Save a batch of entries to database"""
        try:
            with transaction.atomic():
                BankExchangeRate.objects.bulk_create(batch, batch_size=100)
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to save batch: {str(e)}')
            )
            # Try saving individually
            for entry in batch:
                try:
                    entry.save()
                except Exception as individual_error:
                    self.stdout.write(
                        self.style.ERROR(
                            f'Failed to save entry {entry.entry_id}: {str(individual_error)}'
                        )
                    )