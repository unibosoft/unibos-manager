"""
Background OCR processing management command
Continuously processes documents with 'processing' status ONE AT A TIME
"""

import time
import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.cache import cache
from modules.documents.backend.models import Document
from modules.documents.backend.ocr_service import OCRProcessor

logger = logging.getLogger('documents.ocr_processor')


class Command(BaseCommand):
    help = 'Continuously process documents with pending OCR in background (one at a time)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--interval',
            type=int,
            default=3,
            help='Seconds to wait between checking for new documents (default: 3)'
        )

    def handle(self, *args, **options):
        interval = options['interval']

        self.stdout.write(self.style.SUCCESS(
            f'🚀 starting background ocr processor (one document at a time, interval: {interval}s)'
        ))

        ocr_processor = OCRProcessor()

        while True:
            try:
                # Check if processing is paused
                if cache.get('ocr_processing_paused', False):
                    self.stdout.write(self.style.WARNING(
                        '⏸️  OCR processing is PAUSED. Waiting...'
                    ))
                    time.sleep(interval * 2)
                    continue

                # Get ONE document at a time (safer for pause/resume)
                pending_document = Document.objects.filter(
                    processing_status='processing',
                    is_deleted=False
                ).order_by('uploaded_at').first()

                if pending_document:
                    self.stdout.write(
                        f'📄 processing: {pending_document.original_filename} (id: {pending_document.id})'
                    )

                    try:
                        # Check pause again before starting heavy processing
                        if cache.get('ocr_processing_paused', False):
                            self.stdout.write(self.style.WARNING(
                                '⏸️  OCR paused before starting document. Skipping.'
                            ))
                            time.sleep(interval * 2)
                            continue

                        # Process with OCR
                        result = ocr_processor.process_document(
                            pending_document.file_path.path,
                            document_type=pending_document.document_type,
                            force_ocr=True,
                            document_instance=pending_document
                        )

                        if result and result.get('success'):
                            # OCR processor already saved the document with dual results
                            # Just refresh from DB to get updated values
                            pending_document.refresh_from_db()

                            # Check if document was deleted during processing
                            if pending_document.is_deleted:
                                self.stdout.write(self.style.WARNING(
                                    f'  ⚠ document was deleted during processing, skipping'
                                ))
                            else:
                                self.stdout.write(self.style.SUCCESS(
                                    f'  ✓ completed (confidence: {pending_document.ocr_confidence}%) - '
                                    f'Tesseract: {len(pending_document.tesseract_text or "")} chars, '
                                    f'Ollama: {len(pending_document.ollama_text or "")} chars'
                                ))
                        else:
                            # Mark as failed
                            error_msg = result.get('error', 'Unknown error') if result else 'No result returned'

                            pending_document.processing_status = 'failed'
                            pending_document.save(update_fields=['processing_status'])

                            self.stdout.write(self.style.ERROR(
                                f'  ✗ failed: {error_msg}'
                            ))

                    except Exception as e:
                        logger.error(f'error processing document {pending_document.id}: {e}')
                        self.stdout.write(self.style.ERROR(
                            f'  ✗ error: {str(e)}'
                        ))

                        # Mark as failed
                        try:
                            pending_document.processing_status = 'failed'
                            pending_document.save(update_fields=['processing_status'])
                        except Exception:
                            pass

                # Wait before next cycle (shorter wait since we process one at a time)
                time.sleep(interval)

            except KeyboardInterrupt:
                self.stdout.write(self.style.WARNING(
                    '\n⚠️  stopping background ocr processor...'
                ))
                break

            except Exception as e:
                logger.error(f'error in ocr processing loop: {e}')
                self.stdout.write(self.style.ERROR(
                    f'❌ error: {str(e)}'
                ))
                # Continue after error, with longer wait
                time.sleep(interval * 2)

        self.stdout.write(self.style.SUCCESS(
            '👋 background ocr processor stopped'
        ))
