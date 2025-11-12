"""
Management command to clean up old logs based on retention policy
Run this daily via cron: python manage.py cleanup_logs
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from core.system.logging.backend.models import SystemLog, ActivityLog, LogRetentionPolicy
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Clean up old logs based on retention policies'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force cleanup even if no policy exists',
        )
    
    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        force = options.get('force', False)
        
        self.stdout.write('Starting log cleanup...')
        
        # Get or create default policies
        system_policy, _ = LogRetentionPolicy.objects.get_or_create(
            log_type='system',
            defaults={'retention_days': 30, 'is_active': True}
        )
        
        activity_policy, _ = LogRetentionPolicy.objects.get_or_create(
            log_type='activity',
            defaults={'retention_days': 90, 'is_active': True}
        )
        
        # Clean system logs
        if system_policy.is_active or force:
            cutoff_date = timezone.now() - timedelta(days=system_policy.retention_days)
            old_logs = SystemLog.objects.filter(timestamp__lt=cutoff_date)
            count = old_logs.count()
            
            if count > 0:
                self.stdout.write(f'Found {count} system logs older than {system_policy.retention_days} days')
                
                if not dry_run:
                    # Archive if enabled
                    if system_policy.archive_enabled and system_policy.archive_path:
                        self._archive_logs(old_logs, system_policy.archive_path)
                    
                    # Delete logs
                    old_logs.delete()
                    self.stdout.write(self.style.SUCCESS(f'Deleted {count} system logs'))
                else:
                    self.stdout.write(f'[DRY RUN] Would delete {count} system logs')
        
        # Clean activity logs
        if activity_policy.is_active or force:
            cutoff_date = timezone.now() - timedelta(days=activity_policy.retention_days)
            old_logs = ActivityLog.objects.filter(timestamp__lt=cutoff_date)
            count = old_logs.count()
            
            if count > 0:
                self.stdout.write(f'Found {count} activity logs older than {activity_policy.retention_days} days')
                
                if not dry_run:
                    # Archive if enabled
                    if activity_policy.archive_enabled and activity_policy.archive_path:
                        self._archive_logs(old_logs, activity_policy.archive_path)
                    
                    # Delete logs
                    old_logs.delete()
                    self.stdout.write(self.style.SUCCESS(f'Deleted {count} activity logs'))
                else:
                    self.stdout.write(f'[DRY RUN] Would delete {count} activity logs')
        
        # Clean up orphaned aggregations
        cutoff_date = timezone.now() - timedelta(days=180)  # Keep 6 months of aggregations
        from core.system.logging.backend.models import LogAggregation
        old_aggregations = LogAggregation.objects.filter(date_hour__lt=cutoff_date)
        agg_count = old_aggregations.count()
        
        if agg_count > 0:
            if not dry_run:
                old_aggregations.delete()
                self.stdout.write(self.style.SUCCESS(f'Deleted {agg_count} old aggregations'))
            else:
                self.stdout.write(f'[DRY RUN] Would delete {agg_count} old aggregations')
        
        self.stdout.write(self.style.SUCCESS('Log cleanup completed'))
    
    def _archive_logs(self, logs, archive_path):
        """Archive logs to file before deletion"""
        import json
        import os
        from django.core.serializers.json import DjangoJSONEncoder
        
        # Create archive directory if not exists
        os.makedirs(archive_path, exist_ok=True)
        
        # Generate archive filename
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        filename = os.path.join(archive_path, f'logs_archive_{timestamp}.jsonl')
        
        # Write logs to file (JSON Lines format)
        with open(filename, 'w') as f:
            for log in logs.iterator(chunk_size=1000):
                log_data = {
                    'timestamp': log.timestamp,
                    'level': getattr(log, 'level', None),
                    'category': getattr(log, 'category', None),
                    'message': getattr(log, 'message', ''),
                    'user': log.user.username if log.user else None,
                    'ip_address': getattr(log, 'ip_address', ''),
                    'extra_data': getattr(log, 'extra_data', {}) if hasattr(log, 'extra_data') else getattr(log, 'metadata', {})
                }
                f.write(json.dumps(log_data, cls=DjangoJSONEncoder) + '\n')
        
        self.stdout.write(f'Archived logs to {filename}')