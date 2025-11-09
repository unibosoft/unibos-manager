"""
Management command to purge documents that have been in recycle bin for more than 30 days
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import logging

from modules.documents.backend.models import Document

logger = logging.getLogger('documents.purge')


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
        
        # Find documents to purge
        documents_to_purge = Document.objects.filter(
            is_deleted=True,
            deleted_at__lt=cutoff_date
        )
        
        count = documents_to_purge.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS(
                f'No documents found older than {days} days in recycle bin'
            ))
            return
        
        self.stdout.write(
            f'Found {count} document(s) deleted more than {days} days ago'
        )
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - No documents will be deleted'))
            
            # Show details of what would be deleted
            for doc in documents_to_purge[:10]:  # Show first 10
                days_old = (timezone.now() - doc.deleted_at).days
                self.stdout.write(
                    f'  - {doc.original_filename} (deleted {days_old} days ago by {doc.deleted_by})'
                )
            
            if count > 10:
                self.stdout.write(f'  ... and {count - 10} more')
        else:
            # Actually delete the documents
            deleted_count = 0
            failed_count = 0
            
            for doc in documents_to_purge:
                try:
                    # Delete associated files
                    if doc.file_path:
                        doc.file_path.delete(save=False)
                    if doc.thumbnail_path:
                        doc.thumbnail_path.delete(save=False)
                    
                    # Delete the document
                    doc.delete()
                    deleted_count += 1
                    
                except Exception as e:
                    failed_count += 1
                    logger.error(f'Failed to delete document {doc.id}: {e}')
                    self.stdout.write(
                        self.style.ERROR(f'Failed to delete {doc.original_filename}: {e}')
                    )
            
            self.stdout.write(self.style.SUCCESS(
                f'Successfully purged {deleted_count} document(s)'
            ))
            
            if failed_count > 0:
                self.stdout.write(self.style.WARNING(
                    f'Failed to delete {failed_count} document(s)'
                ))
            
            logger.info(f'Purged {deleted_count} old documents from recycle bin')