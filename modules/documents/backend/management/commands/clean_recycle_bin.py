"""
Management command to clean old documents from recycle bin
Run this as a daily cron job
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import logging

from modules.documents.backend.models import Document

logger = logging.getLogger('documents.cron')


class Command(BaseCommand):
    help = 'Permanently delete documents that have been in recycle bin for more than 30 days'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days to keep deleted documents (default: 30)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting'
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        
        # Calculate cutoff date
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # Find old deleted documents
        old_documents = Document.objects.filter(
            is_deleted=True,
            deleted_at__lt=cutoff_date
        )
        
        count = old_documents.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('No documents to clean up'))
            return
        
        if dry_run:
            self.stdout.write(f'DRY RUN: Would delete {count} documents:')
            for doc in old_documents[:10]:  # Show first 10
                self.stdout.write(f'  - {doc.original_filename} (deleted {doc.deleted_at})')
            if count > 10:
                self.stdout.write(f'  ... and {count - 10} more')
        else:
            # Delete associated files
            deleted_count = 0
            failed_count = 0
            
            for doc in old_documents:
                try:
                    # Delete physical files
                    if doc.file_path:
                        try:
                            doc.file_path.delete(save=False)
                        except Exception as e:
                            logger.warning(f'Could not delete file for document {doc.id}: {e}')
                    
                    if doc.thumbnail_path:
                        try:
                            doc.thumbnail_path.delete(save=False)
                        except Exception as e:
                            logger.warning(f'Could not delete thumbnail for document {doc.id}: {e}')
                    
                    # Delete database record
                    doc.delete()
                    deleted_count += 1
                    
                except Exception as e:
                    logger.error(f'Failed to delete document {doc.id}: {e}')
                    failed_count += 1
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully deleted {deleted_count} documents from recycle bin'
                )
            )
            
            if failed_count > 0:
                self.stdout.write(
                    self.style.WARNING(f'Failed to delete {failed_count} documents')
                )
            
            logger.info(f'Recycle bin cleanup: deleted {deleted_count} documents, failed {failed_count}')