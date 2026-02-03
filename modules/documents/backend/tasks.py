"""
Documents Module - Celery Tasks
Background task processing for OCR, thumbnails, and gamification
"""

from celery import shared_task
from django.utils import timezone
import logging

logger = logging.getLogger('documents.tasks')


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_document_ocr(self, document_id):
    """
    Process OCR for a single document (Tesseract + Ollama dual processing).
    Called after document upload to extract text in background.
    """
    from .models import Document
    from .ocr_service import OCRProcessor

    try:
        document = Document.objects.get(id=document_id)

        if document.is_deleted:
            logger.info(f"Document {document_id} was deleted, skipping OCR")
            return {'success': False, 'reason': 'deleted'}

        document.processing_status = 'processing'
        document.save(update_fields=['processing_status'])

        ocr_processor = OCRProcessor()
        result = ocr_processor.process_document(
            document.file_path.path,
            document_type=document.document_type,
            force_ocr=True,
            document_instance=document
        )

        if result.get('success') and result.get('ocr_text'):
            document.refresh_from_db()
            if document.processing_status == 'processing':
                document.processing_status = 'completed'
                document.ocr_processed_at = timezone.now()
                document.save(update_fields=['processing_status', 'ocr_processed_at'])

            # Auto-parse receipt if applicable
            if document.document_type == 'receipt' and result.get('parsed_data'):
                try:
                    from .views import DocumentUploadView
                    view = DocumentUploadView()
                    view.save_parsed_receipt(document, result['parsed_data'])
                except Exception as e:
                    logger.error(f"Receipt parsing failed for {document_id}: {e}")

            # Award gamification points
            update_user_points.delay(
                str(document.user_id),
                'receipt_ocr_complete',
                str(document_id)
            )

            logger.info(f"OCR completed for document {document_id}")
            return {
                'success': True,
                'document_id': str(document_id),
                'text_length': len(result['ocr_text']),
            }
        else:
            document.processing_status = 'failed'
            document.save(update_fields=['processing_status'])
            logger.warning(f"OCR failed for document {document_id}: {result.get('error')}")
            return {
                'success': False,
                'document_id': str(document_id),
                'error': result.get('error', 'No text extracted'),
            }

    except Document.DoesNotExist:
        logger.error(f"Document {document_id} not found")
        return {'success': False, 'error': 'Document not found'}
    except Exception as exc:
        logger.error(f"OCR task failed for {document_id}: {exc}")
        try:
            Document.objects.filter(id=document_id).update(
                processing_status='failed'
            )
        except Exception:
            pass
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=2, default_retry_delay=30)
def process_batch_documents(self, batch_id):
    """
    Process OCR for all documents in a batch.
    Triggers individual process_document_ocr tasks for each document.
    """
    from .models import Document, DocumentBatch

    try:
        batch = DocumentBatch.objects.get(id=batch_id)
        batch.status = 'processing'
        batch.save(update_fields=['status'])

        # Get all documents in this batch (uploaded after batch start)
        documents = Document.objects.filter(
            user=batch.user,
            processing_status__in=['pending', 'processing'],
            uploaded_at__gte=batch.started_at,
            is_deleted=False
        )

        # Trigger individual OCR tasks
        for doc in documents:
            process_document_ocr.delay(str(doc.id))

        logger.info(f"Batch {batch_id}: triggered OCR for {documents.count()} documents")
        return {
            'success': True,
            'batch_id': str(batch_id),
            'document_count': documents.count(),
        }

    except DocumentBatch.DoesNotExist:
        logger.error(f"Batch {batch_id} not found")
        return {'success': False, 'error': 'Batch not found'}
    except Exception as exc:
        logger.error(f"Batch processing failed for {batch_id}: {exc}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=2, default_retry_delay=30)
def generate_thumbnail(self, document_id):
    """
    Generate or regenerate thumbnail for a document.
    """
    from .models import Document
    from .utils import ThumbnailGenerator

    try:
        document = Document.objects.get(id=document_id)

        if not document.file_path:
            return {'success': False, 'error': 'No file path'}

        generator = ThumbnailGenerator()
        thumb_file = generator.generate_thumbnail_from_django_file(
            document.file_path,
            str(document.id)
        )

        if thumb_file:
            if document.thumbnail_path:
                try:
                    document.thumbnail_path.delete(save=False)
                except Exception:
                    pass

            document.thumbnail_path.save(
                f"thumb_{document.id}.jpg", thumb_file, save=True
            )
            logger.info(f"Thumbnail generated for document {document_id}")
            return {'success': True, 'document_id': str(document_id)}
        else:
            logger.warning(f"Thumbnail generation returned None for {document_id}")
            return {'success': False, 'error': 'Generation failed'}

    except Document.DoesNotExist:
        logger.error(f"Document {document_id} not found")
        return {'success': False, 'error': 'Document not found'}
    except Exception as exc:
        logger.error(f"Thumbnail task failed for {document_id}: {exc}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=2, default_retry_delay=120)
def ai_enhance_ocr(self, document_id, methods=None):
    """
    Run AI-enhanced OCR analysis on a document.
    Runs specified methods or all available methods.
    """
    from .models import Document

    try:
        document = Document.objects.get(id=document_id)

        if not document.file_path:
            return {'success': False, 'error': 'No file path'}

        if methods is None:
            methods = ['llama_vision', 'hybrid']

        from .analysis_service import OCRAnalysisService
        analyzer = OCRAnalysisService()
        results = analyzer.analyze_document(
            document,
            force_refresh=True,
            methods_to_run=methods,
        )

        logger.info(f"AI enhancement completed for document {document_id}")
        return {
            'success': True,
            'document_id': str(document_id),
            'methods_run': methods,
        }

    except Document.DoesNotExist:
        logger.error(f"Document {document_id} not found")
        return {'success': False, 'error': 'Document not found'}
    except Exception as exc:
        logger.error(f"AI enhancement failed for {document_id}: {exc}")
        raise self.retry(exc=exc)


@shared_task
def validate_receipt_data(document_id):
    """
    Validate parsed receipt data against known patterns.
    Checks store names, amounts, dates for consistency.
    """
    from .models import Document, ParsedReceipt

    try:
        document = Document.objects.get(id=document_id)

        try:
            receipt = document.parsed_receipt
        except ParsedReceipt.DoesNotExist:
            return {'success': False, 'error': 'No parsed receipt'}

        validation_results = {
            'store_valid': bool(receipt.store_name),
            'date_valid': receipt.transaction_date is not None,
            'total_valid': receipt.total_amount is not None and receipt.total_amount > 0,
            'items_valid': receipt.items.exists(),
            'items_count': receipt.items.count(),
        }

        # Check total matches sum of items
        if receipt.total_amount and receipt.items.exists():
            from django.db.models import Sum
            items_total = receipt.items.aggregate(
                total=Sum('total_price')
            )['total']
            if items_total:
                diff = abs(float(receipt.total_amount) - float(items_total))
                validation_results['total_matches_items'] = diff < 1.0
            else:
                validation_results['total_matches_items'] = False

        is_valid = all([
            validation_results['store_valid'],
            validation_results['date_valid'],
            validation_results['total_valid'],
        ])

        if is_valid:
            document.processing_status = 'completed'
        else:
            document.processing_status = 'manual_review'
        document.save(update_fields=['processing_status'])

        logger.info(f"Receipt validation for {document_id}: valid={is_valid}")
        return {
            'success': True,
            'document_id': str(document_id),
            'is_valid': is_valid,
            'details': validation_results,
        }

    except Document.DoesNotExist:
        logger.error(f"Document {document_id} not found")
        return {'success': False, 'error': 'Document not found'}
    except Exception as e:
        logger.error(f"Receipt validation failed for {document_id}: {e}")
        return {'success': False, 'error': str(e)}


@shared_task
def update_user_points(user_id, action_type, document_id=None):
    """
    Award gamification points to user for various actions.
    """
    try:
        from .gamification_models import UserProfile, POINT_REWARDS

        profile, _ = UserProfile.objects.get_or_create(
            user_id=user_id
        )

        points = POINT_REWARDS.get(action_type, 0)
        if callable(points):
            points = 0  # Skip callable rewards (need context)

        if points > 0:
            reason = f"{action_type}"
            if document_id:
                reason += f" (doc: {document_id})"

            profile.add_points(points, reason)
            profile.update_streak()

            logger.info(f"Awarded {points} points to user {user_id} for {action_type}")
            return {
                'success': True,
                'user_id': str(user_id),
                'points_awarded': points,
                'total_points': profile.total_points,
            }

        return {'success': True, 'points_awarded': 0}

    except Exception as e:
        logger.error(f"Points update failed for user {user_id}: {e}")
        return {'success': False, 'error': str(e)}


@shared_task
def process_challenge_completion(user_id):
    """
    Check and process challenge completions for a user.
    Called after points are awarded to check if any challenges are complete.
    """
    try:
        from .gamification_models import UserProfile, UserChallenge, Challenge

        profile = UserProfile.objects.get(user_id=user_id)

        # Get active challenges for this user
        active_challenges = UserChallenge.objects.filter(
            user_id=user_id,
            completed=False,
            challenge__is_active=True,
            challenge__end_date__gte=timezone.now()
        ).select_related('challenge')

        completed = []
        for uc in active_challenges:
            challenge = uc.challenge

            # Check progress based on challenge target type
            current = 0
            if challenge.target_type == 'receipts_processed':
                current = profile.receipts_processed
            elif challenge.target_type == 'receipts_validated':
                current = profile.receipts_validated
            elif challenge.target_type == 'accuracy_target':
                current = int(profile.accuracy_score)
            elif challenge.target_type == 'streak_days':
                current = profile.streak_days
            elif challenge.target_type == 'points_earned':
                current = profile.total_points

            if current != uc.current_progress:
                uc.current_progress = current
                if current >= challenge.target_count and not uc.completed:
                    uc.completed = True
                    uc.completed_at = timezone.now()
                    profile.add_points(
                        challenge.points_reward,
                        f"Challenge completed: {challenge.title}"
                    )
                    completed.append(challenge.title)
                uc.save()

        if completed:
            logger.info(f"User {user_id} completed challenges: {', '.join(completed)}")

        return {
            'success': True,
            'user_id': str(user_id),
            'challenges_completed': completed,
        }

    except UserProfile.DoesNotExist:
        return {'success': False, 'error': 'User profile not found'}
    except Exception as e:
        logger.error(f"Challenge processing failed for user {user_id}: {e}")
        return {'success': False, 'error': str(e)}
