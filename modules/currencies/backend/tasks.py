"""
Celery tasks for Currencies module
Handles periodic updates and background processing
"""

from celery import shared_task
from celery.utils.log import get_task_logger
from django.utils import timezone
from django.core.cache import cache
from django.db.models import Q
from decimal import Decimal
from datetime import timedelta

from .services import CurrencyService
from .models import CurrencyAlert, ExchangeRate

logger = get_task_logger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def update_exchange_rates(self):
    """
    Periodic task to update exchange rates
    Should be run every 5-15 minutes depending on requirements
    """
    try:
        logger.info("Starting exchange rate update task")
        
        service = CurrencyService()
        
        # Update TCMB rates (less frequent)
        cache_key = 'last_tcmb_update'
        last_tcmb = cache.get(cache_key)
        
        if not last_tcmb or (timezone.now() - last_tcmb).seconds > 1800:  # 30 minutes
            try:
                tcmb_count = service.update_tcmb_rates()
                logger.info(f"Updated {tcmb_count} TCMB rates")
                cache.set(cache_key, timezone.now(), 3600)
            except Exception as e:
                logger.error(f"TCMB update failed: {e}")
                # Don't fail the entire task if TCMB fails
        
        # Update crypto rates (more frequent)
        try:
            crypto_count = service.update_crypto_rates()
            logger.info(f"Updated {crypto_count} crypto rates")
        except Exception as e:
            logger.error(f"Crypto update failed: {e}")
            raise self.retry(exc=e)
        
        return {
            'status': 'success',
            'timestamp': timezone.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Rate update task failed: {e}", exc_info=True)
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=3)
def check_currency_alerts(self):
    """
    Check all active currency alerts and trigger notifications
    Should be run every 1-5 minutes
    """
    try:
        logger.info("Checking currency alerts")
        
        triggered_alerts = []
        active_alerts = CurrencyAlert.objects.filter(is_active=True)
        
        for alert in active_alerts:
            try:
                # Get latest exchange rate
                latest_rate = ExchangeRate.objects.filter(
                    base_currency=alert.base_currency,
                    target_currency=alert.target_currency
                ).latest('timestamp')
                
                # Check if alert should trigger
                should_trigger = False
                
                if alert.alert_type == 'above':
                    should_trigger = latest_rate.rate > alert.threshold_value
                elif alert.alert_type == 'below':
                    should_trigger = latest_rate.rate < alert.threshold_value
                elif alert.alert_type == 'change_percent':
                    # Get rate from 24 hours ago
                    yesterday = timezone.now() - timedelta(days=1)
                    try:
                        old_rate = ExchangeRate.objects.filter(
                            base_currency=alert.base_currency,
                            target_currency=alert.target_currency,
                            timestamp__lte=yesterday
                        ).latest('timestamp')
                        
                        change_pct = ((latest_rate.rate - old_rate.rate) / old_rate.rate) * 100
                        should_trigger = abs(change_pct) >= abs(alert.threshold_value)
                    except ExchangeRate.DoesNotExist:
                        continue
                
                if should_trigger:
                    # Check cooldown period (don't trigger too frequently)
                    if alert.last_triggered:
                        time_since_last = timezone.now() - alert.last_triggered
                        if time_since_last.seconds < 3600:  # 1 hour cooldown
                            continue
                    
                    # Trigger alert
                    alert.last_triggered = timezone.now()
                    alert.trigger_count += 1
                    alert.save()
                    
                    triggered_alerts.append({
                        'alert_id': str(alert.id),
                        'user_id': alert.user.id,
                        'pair': f"{alert.base_currency.code}/{alert.target_currency.code}",
                        'rate': float(latest_rate.rate),
                        'threshold': float(alert.threshold_value),
                        'type': alert.alert_type
                    })
                    
                    # Send notifications
                    send_alert_notifications.delay(alert.id)
                    
            except ExchangeRate.DoesNotExist:
                logger.warning(f"No rate found for alert {alert.id}")
                continue
            except Exception as e:
                logger.error(f"Error checking alert {alert.id}: {e}")
                continue
        
        logger.info(f"Triggered {len(triggered_alerts)} alerts")
        
        return {
            'status': 'success',
            'triggered_count': len(triggered_alerts),
            'triggered_alerts': triggered_alerts,
            'timestamp': timezone.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Alert check task failed: {e}", exc_info=True)
        raise self.retry(exc=e)


@shared_task
def send_alert_notifications(alert_id):
    """
    Send notifications for a triggered alert
    """
    try:
        alert = CurrencyAlert.objects.get(id=alert_id)
        
        # Get current rate
        latest_rate = ExchangeRate.objects.filter(
            base_currency=alert.base_currency,
            target_currency=alert.target_currency
        ).latest('timestamp')
        
        message = (
            f"Currency Alert: {alert.base_currency.code}/{alert.target_currency.code} "
            f"is now {latest_rate.rate:.4f} "
            f"(threshold: {alert.threshold_value:.4f})"
        )
        
        # Send email notification
        if alert.notify_email and alert.user.email:
            send_alert_email.delay(alert.user.email, message)
        
        # Send push notification (implement based on your push service)
        if alert.notify_push:
            # send_push_notification(alert.user, message)
            pass
        
        # Create in-app notification (implement based on your notification model)
        if alert.notify_in_app:
            # create_in_app_notification(alert.user, message)
            pass
        
        logger.info(f"Sent notifications for alert {alert_id}")
        
    except CurrencyAlert.DoesNotExist:
        logger.error(f"Alert {alert_id} not found")
    except Exception as e:
        logger.error(f"Failed to send notifications for alert {alert_id}: {e}")


@shared_task
def send_alert_email(email, message):
    """
    Send email notification for currency alert
    """
    from django.core.mail import send_mail
    from django.conf import settings
    
    try:
        send_mail(
            subject='UNIBOS Currency Alert',
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        logger.info(f"Sent alert email to {email}")
    except Exception as e:
        logger.error(f"Failed to send email to {email}: {e}")


@shared_task
def cleanup_old_rates():
    """
    Clean up old exchange rates to manage database size
    Run daily
    """
    try:
        service = CurrencyService()
        deleted_count = service.cleanup_old_rates(days=30)
        
        logger.info(f"Cleaned up {deleted_count} old exchange rates")
        
        return {
            'status': 'success',
            'deleted_count': deleted_count,
            'timestamp': timezone.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Cleanup task failed: {e}", exc_info=True)


@shared_task
def generate_market_data():
    """
    Generate market data for charts from exchange rates
    Run hourly
    """
    try:
        from .models import MarketData
        
        # Get unique currency pairs
        pairs = ExchangeRate.objects.values_list(
            'base_currency__code', 'target_currency__code'
        ).distinct()
        
        created_count = 0
        
        for base_code, target_code in pairs:
            pair_str = f"{base_code}/{target_code}"
            
            # Get rates from last hour
            hour_ago = timezone.now() - timedelta(hours=1)
            rates = ExchangeRate.objects.filter(
                base_currency__code=base_code,
                target_currency__code=target_code,
                timestamp__gte=hour_ago
            ).order_by('timestamp')
            
            if rates.count() < 2:
                continue
            
            # Calculate OHLCV
            open_price = rates.first().rate
            close_price = rates.last().rate
            high_price = rates.aggregate(max_rate=Max('rate'))['max_rate']
            low_price = rates.aggregate(min_rate=Min('rate'))['min_rate']
            volume = rates.aggregate(total_vol=Sum('volume_24h'))['total_vol'] or Decimal('0')
            
            # Create market data entry
            market_data, created = MarketData.objects.get_or_create(
                currency_pair=pair_str,
                period_start=hour_ago,
                interval='1h',
                source='AGGREGATED',
                defaults={
                    'open_price': open_price,
                    'high_price': high_price,
                    'low_price': low_price,
                    'close_price': close_price,
                    'volume': volume,
                    'period_end': timezone.now()
                }
            )
            
            if created:
                created_count += 1
        
        logger.info(f"Generated {created_count} market data entries")
        
        return {
            'status': 'success',
            'created_count': created_count,
            'timestamp': timezone.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Market data generation failed: {e}", exc_info=True)


@shared_task
def calculate_portfolio_performance():
    """
    Calculate and cache portfolio performance metrics
    Run every 15 minutes
    """
    try:
        from .models import Portfolio
        
        portfolios = Portfolio.objects.filter(
            holdings__isnull=False
        ).distinct()
        
        updated_count = 0
        
        for portfolio in portfolios:
            try:
                # Calculate metrics
                total_value_try = portfolio.calculate_total_value('TRY')
                total_value_usd = portfolio.calculate_total_value('USD')
                
                # Cache the results
                cache_key = f"portfolio_performance_{portfolio.id}"
                cache_data = {
                    'total_value_try': float(total_value_try),
                    'total_value_usd': float(total_value_usd),
                    'calculated_at': timezone.now().isoformat()
                }
                
                cache.set(cache_key, cache_data, 900)  # Cache for 15 minutes
                updated_count += 1
                
            except Exception as e:
                logger.error(f"Failed to calculate performance for portfolio {portfolio.id}: {e}")
                continue
        
        logger.info(f"Updated performance for {updated_count} portfolios")
        
        return {
            'status': 'success',
            'updated_count': updated_count,
            'timestamp': timezone.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Portfolio performance calculation failed: {e}", exc_info=True)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def import_firebase_rates_incremental(self):
    """
    Import new bank exchange rates from Firebase
    Runs every 5 minutes to check for new data
    Only imports records that don't exist in database
    """
    import requests
    from datetime import datetime
    from decimal import Decimal, InvalidOperation
    from django.db import transaction
    import pytz
    from .models import BankExchangeRate, BankRateImportLog
    
    FIREBASE_URL = 'https://findmeonphotos-default-rtdb.europe-west1.firebasedatabase.app/kurlar.json'
    
    # Bank and currency mappings
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
    
    CURRENCY_MAPPING = {
        'USDTRY': 'USDTRY',
        'EURTRY': 'EURTRY',
        'XAUTRY': 'XAUTRY',
        'GBPTRY': 'GBPTRY',
        'CHFTRY': 'CHFTRY',
        'JPYTRY': 'JPYTRY',
    }
    
    # Create import log
    import_log = BankRateImportLog.objects.create(
        import_type='scheduled',
        source_url=FIREBASE_URL,
        status='in_progress'
    )
    
    try:
        logger.info("Starting incremental Firebase rates import")
        
        # Fetch data from Firebase
        response = requests.get(FIREBASE_URL, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if not data:
            raise ValueError('No data received from Firebase')
        
        # Get all existing entry IDs in a single query for performance
        existing_ids = set(BankExchangeRate.objects.values_list('entry_id', flat=True))
        logger.info(f"Found {len(existing_ids)} existing entries in database")
        
        # Get latest timestamp for reference
        latest_entry = BankExchangeRate.objects.order_by('-timestamp').first()
        latest_timestamp = latest_entry.timestamp if latest_entry else None
        
        stats = {
            'total': 0,
            'new': 0,
            'updated': 0,
            'failed': 0,
            'skipped': 0
        }
        
        # Batch for bulk insert
        batch = []
        batch_size = 100
        istanbul_tz = pytz.timezone('Europe/Istanbul')
        
        # Process entries
        for entry_id, entry_data in data.items():
            try:
                # Validate entry
                if not isinstance(entry_data, dict) or 'zaman' not in entry_data:
                    stats['skipped'] += 1
                    continue
                
                # Parse timestamp
                timestamp_ms = entry_data['zaman']
                timestamp = datetime.fromtimestamp(timestamp_ms / 1000, tz=istanbul_tz)
                
                # Skip very old entries for performance (only check last 7 days in scheduled task)
                if latest_timestamp and (latest_timestamp - timestamp).days > 7:
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
                    bank_name = BANK_MAPPING.get(bank_name_raw)
                    
                    if not bank_name:
                        continue
                    
                    # Process each currency rate
                    for rate_data in bank_data.get('banka_kuru', []):
                        if not isinstance(rate_data, dict):
                            continue
                        
                        currency_pair_raw = rate_data.get('kur', '')
                        currency_pair = CURRENCY_MAPPING.get(currency_pair_raw)
                        
                        if not currency_pair:
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
                        
                        # Skip if already exists
                        if unique_entry_id in existing_ids:
                            stats['skipped'] += 1
                            continue
                        
                        # Get previous rates for change calculation
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
                        if len(batch) >= batch_size:
                            with transaction.atomic():
                                BankExchangeRate.objects.bulk_create(batch, batch_size=50)
                            batch = []
                
            except Exception as e:
                logger.error(f'Error processing entry {entry_id}: {str(e)}')
                stats['failed'] += 1
        
        # Save remaining batch
        if batch:
            with transaction.atomic():
                BankExchangeRate.objects.bulk_create(batch, batch_size=50)
        
        # Update import log
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
        
        logger.info(
            f"Firebase incremental import completed: {stats['new']} new, "
            f"{stats['skipped']} skipped, {stats['failed']} failed"
        )
        
        # Clear cache for latest rates if new data was imported
        if stats['new'] > 0:
            cache.delete('bank_rates:latest')
            cache.delete_pattern('bank_rates:chart:*')
            
            # Send notification
            notify_new_bank_rates.delay(stats['new'])
        
        return {
            'status': 'success',
            'stats': stats,
            'timestamp': timezone.now().isoformat()
        }
        
    except Exception as e:
        import_log.status = 'failed'
        import_log.error_message = str(e)
        import_log.completed_at = timezone.now()
        import_log.save()
        
        logger.error(f"Firebase incremental import failed: {str(e)}", exc_info=True)
        raise self.retry(exc=e)


@shared_task
def notify_new_bank_rates(count):
    """
    Send notification when new bank rates are available
    """
    try:
        from django.contrib.auth import get_user_model
        from django.core.mail import send_mass_mail
        from django.conf import settings
        
        User = get_user_model()
        
        # Get users who want bank rate notifications (implement based on your user preferences)
        # For now, just log it
        logger.info(f"New bank rates available: {count} new entries")
        
        # You can implement email notifications here
        # users = User.objects.filter(preferences__bank_rate_notifications=True)
        # ...
        
    except Exception as e:
        logger.error(f"Failed to send bank rate notifications: {e}")


@shared_task
def cleanup_old_bank_rates():
    """
    Clean up old bank rates keeping only recent data
    Run weekly
    """
    try:
        from .models import BankExchangeRate
        from datetime import timedelta
        
        # Keep last 90 days of data
        cutoff_date = timezone.now() - timedelta(days=90)
        
        # Delete old rates
        deleted_count = BankExchangeRate.objects.filter(
            timestamp__lt=cutoff_date
        ).delete()[0]
        
        logger.info(f"Cleaned up {deleted_count} old bank rates")
        
        return {
            'status': 'success',
            'deleted_count': deleted_count,
            'timestamp': timezone.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Bank rate cleanup failed: {e}", exc_info=True)