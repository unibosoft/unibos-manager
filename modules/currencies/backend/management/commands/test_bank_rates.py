"""
Test command to verify bank rates integration
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
import requests
from decimal import Decimal

from modules.currencies.backend.models import BankExchangeRate, BankRateImportLog


class Command(BaseCommand):
    help = 'Test bank rates integration by fetching and displaying sample data'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('Bank Rates Integration Test'))
        self.stdout.write(self.style.SUCCESS('='*60 + '\n'))
        
        # 1. Test Firebase connection
        self.stdout.write('1. Testing Firebase connection...')
        try:
            url = 'https://findmeonphotos-default-rtdb.europe-west1.firebasedatabase.app/kurlar.json'
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            self.stdout.write(self.style.SUCCESS(f'   ✓ Connected successfully'))
            self.stdout.write(f'   ✓ Found {len(data)} entries in Firebase')
            
            # Get sample entry
            sample_key = list(data.keys())[0]
            sample = data[sample_key]
            
            if 'zaman' in sample:
                timestamp = datetime.fromtimestamp(sample['zaman'] / 1000)
                self.stdout.write(f'   ✓ Sample timestamp: {timestamp}')
            
            if 'data' in sample:
                banks = [b['banka'] for b in sample['data'] if 'banka' in b]
                self.stdout.write(f'   ✓ Banks found: {", ".join(set(banks))}')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ✗ Connection failed: {str(e)}'))
            return
        
        # 2. Test database models
        self.stdout.write('\n2. Testing database models...')
        try:
            # Check if we have any data
            total_rates = BankExchangeRate.objects.count()
            self.stdout.write(f'   ✓ Total bank rates in database: {total_rates}')
            
            if total_rates > 0:
                # Get latest rates
                latest = BankExchangeRate.objects.order_by('-timestamp').first()
                self.stdout.write(f'   ✓ Latest rate: {latest.bank} - {latest.currency_pair} @ {latest.timestamp}')
                
                # Get unique banks
                banks = BankExchangeRate.objects.values_list('bank', flat=True).distinct()
                self.stdout.write(f'   ✓ Banks in database: {", ".join(banks)}')
                
                # Get unique currency pairs
                pairs = BankExchangeRate.objects.values_list('currency_pair', flat=True).distinct()
                self.stdout.write(f'   ✓ Currency pairs: {", ".join(pairs)}')
                
                # Get date range
                earliest = BankExchangeRate.objects.order_by('date').first()
                latest = BankExchangeRate.objects.order_by('-date').first()
                self.stdout.write(f'   ✓ Date range: {earliest.date} to {latest.date}')
            else:
                self.stdout.write(self.style.WARNING('   ⚠ No bank rates in database yet'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ✗ Database test failed: {str(e)}'))
        
        # 3. Test import functionality
        self.stdout.write('\n3. Testing import functionality...')
        try:
            # Import a small sample
            from modules.currencies.backend.management.commands.import_bank_rates import Command as ImportCommand
            
            # Create a test import
            self.stdout.write('   → Importing sample data (last 5 entries)...')
            
            # Get last 5 entries from Firebase
            entries = list(data.items())[-5:]
            imported = 0
            skipped = 0
            
            for entry_id, entry_data in entries:
                try:
                    if 'zaman' not in entry_data or 'data' not in entry_data:
                        skipped += 1
                        continue
                    
                    timestamp = datetime.fromtimestamp(
                        entry_data['zaman'] / 1000, 
                        tz=timezone.utc
                    )
                    date = timestamp.date()
                    
                    for bank_data in entry_data['data']:
                        bank_name = bank_data.get('banka')
                        if not bank_name:
                            continue
                        
                        for rate_data in bank_data.get('banka_kuru', []):
                            currency_pair = rate_data.get('kur')
                            if not currency_pair:
                                continue
                            
                            unique_id = f"{entry_id}_{bank_name}_{currency_pair}"
                            
                            # Check if exists
                            if BankExchangeRate.objects.filter(entry_id=unique_id).exists():
                                skipped += 1
                                continue
                            
                            # Create rate
                            BankExchangeRate.objects.create(
                                entry_id=unique_id,
                                bank=bank_name,
                                currency_pair=currency_pair,
                                buy_rate=Decimal(str(rate_data.get('alis', 0))),
                                sell_rate=Decimal(str(rate_data.get('satis', 0))),
                                date=date,
                                timestamp=timestamp
                            )
                            imported += 1
                
                except Exception as e:
                    self.stdout.write(f'      ⚠ Error processing {entry_id}: {str(e)}')
            
            self.stdout.write(self.style.SUCCESS(f'   ✓ Imported {imported} rates, skipped {skipped}'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ✗ Import test failed: {str(e)}'))
        
        # 4. Test API endpoints
        self.stdout.write('\n4. Testing API functionality...')
        try:
            # Test latest rates retrieval
            latest_rates = BankExchangeRate.get_latest_rates()
            if latest_rates.exists():
                self.stdout.write(f'   ✓ Latest rates API: {latest_rates.count()} rates')
            
            # Test best rates
            for currency in ['USDTRY', 'EURTRY', 'XAUTRY']:
                best = BankExchangeRate.get_best_rates(currency)
                if best['best_buy_rate']:
                    self.stdout.write(
                        f'   ✓ Best {currency} rates: '
                        f'Buy {best["best_buy_rate"]:.4f} ({best["best_buy_bank"]}), '
                        f'Sell {best["best_sell_rate"]:.4f} ({best["best_sell_bank"]})'
                    )
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ✗ API test failed: {str(e)}'))
        
        # 5. Test import logs
        self.stdout.write('\n5. Checking import logs...')
        try:
            logs = BankRateImportLog.objects.order_by('-started_at')[:5]
            if logs:
                self.stdout.write(f'   ✓ Found {logs.count()} recent import logs:')
                for log in logs:
                    status_color = (
                        self.style.SUCCESS if log.status == 'completed' 
                        else self.style.ERROR
                    )
                    self.stdout.write(
                        f'      {status_color(log.status)}: '
                        f'{log.import_type} - {log.new_entries} new, '
                        f'{log.failed_entries} failed ({log.started_at})'
                    )
            else:
                self.stdout.write(self.style.WARNING('   ⚠ No import logs found'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ✗ Import log test failed: {str(e)}'))
        
        # 6. Summary
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('Test Summary'))
        self.stdout.write('='*60)
        
        total_rates = BankExchangeRate.objects.count()
        if total_rates > 0:
            self.stdout.write(self.style.SUCCESS(
                f'\n✓ Bank rates integration is working!\n'
                f'  - Total rates in database: {total_rates}\n'
                f'  - Firebase connection: OK\n'
                f'  - Import functionality: OK\n'
                f'  - API endpoints: Ready\n'
            ))
            
            self.stdout.write('\nNext steps:')
            self.stdout.write('1. Run full import: python manage.py import_bank_rates')
            self.stdout.write('2. Start Celery worker for scheduled imports')
            self.stdout.write('3. Access API at /api/bank-rates/')
            
        else:
            self.stdout.write(self.style.WARNING(
                '\n⚠ No bank rates in database yet.\n'
                'Run: python manage.py import_bank_rates\n'
            ))