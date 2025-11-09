"""
Management command to regenerate thumbnails for all documents
This is useful after changing the thumbnail generation logic
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from modules.documents.backend.models import Document
from modules.documents.backend.utils import ThumbnailGenerator
import logging

logger = logging.getLogger('documents.commands')


class Command(BaseCommand):
    help = 'Regenerate thumbnails for all documents with the new top-cropping logic'

    def add_arguments(self, parser):
        parser.add_argument(
            '--document-type',
            type=str,
            choices=['receipt', 'invoice', 'all'],
            default='all',
            help='Type of documents to regenerate thumbnails for'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=10,
            help='Number of documents to process in each batch'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without actually doing it'
        )

    def handle(self, *args, **options):
        document_type = options['document_type']
        batch_size = options['batch_size']
        dry_run = options['dry_run']
        
        # Build query
        queryset = Document.objects.filter(file_path__isnull=False)
        
        if document_type != 'all':
            queryset = queryset.filter(document_type=document_type)
        
        total_count = queryset.count()
        
        if total_count == 0:
            self.stdout.write(self.style.WARNING('No documents found to process'))
            return
        
        self.stdout.write(
            self.style.SUCCESS(f'Found {total_count} documents to process')
        )
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - No changes will be made'))
        
        # Initialize thumbnail generator
        thumbnail_generator = ThumbnailGenerator()
        
        successful = 0
        failed = 0
        skipped = 0
        
        # Process in batches
        for i in range(0, total_count, batch_size):
            batch = queryset[i:i+batch_size]
            
            for document in batch:
                try:
                    # Check if document has a file
                    if not document.file_path:
                        self.stdout.write(
                            self.style.WARNING(f'Skipping {document.id}: No file attached')
                        )
                        skipped += 1
                        continue
                    
                    if dry_run:
                        self.stdout.write(
                            f'Would regenerate thumbnail for: {document.original_filename}'
                        )
                        successful += 1
                        continue
                    
                    # Generate new thumbnail
                    with transaction.atomic():
                        # Open the file and generate thumbnail
                        document.file_path.open('rb')
                        thumb_file = thumbnail_generator.generate_thumbnail_from_django_file(
                            document.file_path,
                            str(document.id)
                        )
                        document.file_path.close()
                        
                        if thumb_file:
                            # Delete old thumbnail if exists
                            if document.thumbnail_path:
                                document.thumbnail_path.delete(save=False)
                            
                            # Save new thumbnail
                            document.thumbnail_path.save(
                                f'thumb_{document.id}.jpg',
                                thumb_file,
                                save=True
                            )
                            
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'✓ Regenerated thumbnail for: {document.original_filename}'
                                )
                            )
                            successful += 1
                        else:
                            self.stdout.write(
                                self.style.WARNING(
                                    f'⚠ Could not generate thumbnail for: {document.original_filename}'
                                )
                            )
                            failed += 1
                            
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f'✗ Error processing {document.original_filename}: {str(e)}'
                        )
                    )
                    failed += 1
                    logger.error(f'Error regenerating thumbnail for document {document.id}: {str(e)}')
            
            # Progress update
            processed = min(i + batch_size, total_count)
            self.stdout.write(
                f'Progress: {processed}/{total_count} ({processed*100//total_count}%)'
            )
        
        # Final summary
        self.stdout.write(
            self.style.SUCCESS(
                f'\nSummary:\n'
                f'  Successful: {successful}\n'
                f'  Failed: {failed}\n'
                f'  Skipped: {skipped}\n'
                f'  Total: {total_count}'
            )
        )