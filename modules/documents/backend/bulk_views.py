"""
Bulk operations and recycle bin views for documents
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.db import transaction
from django.contrib import messages
from datetime import timedelta
import json
import csv
import logging

from .models import Document
from core.system.web_ui.backend.views import BaseUIView

logger = logging.getLogger('documents.bulk')


class BulkDeleteView(LoginRequiredMixin, View):
    """Handle bulk soft delete of documents"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            document_ids = data.get('document_ids', [])
            
            if not document_ids:
                return JsonResponse({'success': False, 'error': 'No documents selected'})
            
            # Soft delete documents
            with transaction.atomic():
                deleted_count = Document.objects.filter(
                    id__in=document_ids,
                    user=request.user,
                    is_deleted=False
                ).update(
                    is_deleted=True,
                    deleted_at=timezone.now(),
                    deleted_by=request.user
                )
            
            logger.info(f"User {request.user.id} soft deleted {deleted_count} documents")

            return JsonResponse({
                'success': True,
                'deleted': deleted_count
            })
            
        except Exception as e:
            logger.error(f"Bulk delete error: {e}")
            return JsonResponse({'success': False, 'error': str(e)})


class BulkReprocessView(LoginRequiredMixin, View):
    """Handle bulk OCR reprocessing"""

    def post(self, request):
        try:
            data = json.loads(request.body)
            document_ids = data.get('document_ids', [])

            if not document_ids:
                return JsonResponse({'success': False, 'error': 'no documents selected'})

            # Get documents to process
            documents = Document.objects.filter(
                id__in=document_ids,
                user=request.user,
                is_deleted=False
            )

            processed = 0
            failed = 0

            # Import OCR processor
            from .ocr_service import OCRProcessor
            ocr_processor = OCRProcessor()

            # Process each document
            for doc in documents:
                try:
                    # Process with OCR
                    result = ocr_processor.process_document(
                        doc.file_path.path,
                        document_type=doc.document_type,
                        force_ocr=True,
                        document_instance=doc
                    )

                    if result and result.get('success'):
                        # OCR processor already saved the document with dual results
                        # Just refresh from DB to get updated values
                        doc.refresh_from_db()

                        # Check if document was deleted during processing
                        if doc.is_deleted:
                            logger.info(f"document {doc.id} was deleted during processing, skipping")
                            continue

                        processed += 1
                    else:
                        doc.processing_status = 'failed'
                        doc.save()
                        failed += 1

                except Exception as e:
                    logger.error(f"error processing document {doc.id}: {e}")
                    doc.processing_status = 'failed'
                    doc.save()
                    failed += 1

            logger.info(f"user {request.user.id} processed {processed} documents, {failed} failed")

            return JsonResponse({
                'success': True,
                'processed': processed,
                'failed': failed
            })

        except Exception as e:
            logger.error(f"bulk reprocess error: {e}")
            return JsonResponse({'success': False, 'error': str(e)})


class BulkReprocessPendingView(LoginRequiredMixin, View):
    """Handle bulk OCR reprocessing for all pending documents"""

    def post(self, request):
        try:
            # Get all pending documents for user
            documents = Document.objects.filter(
                user=request.user,
                is_deleted=False,
                processing_status='pending'
            )

            processed = 0
            failed = 0

            # Import OCR processor
            from .ocr_service import OCRProcessor
            ocr_processor = OCRProcessor()

            # Process each document
            for doc in documents:
                try:
                    # Process with OCR
                    result = ocr_processor.process_document(
                        doc.file_path.path,
                        document_type=doc.document_type,
                        force_ocr=True,
                        document_instance=doc
                    )

                    if result and result.get('success'):
                        # OCR processor already saved the document with dual results
                        # Just refresh from DB to get updated values
                        doc.refresh_from_db()

                        # Check if document was deleted during processing
                        if doc.is_deleted:
                            logger.info(f"document {doc.id} was deleted during processing, skipping")
                            continue

                        processed += 1
                    else:
                        doc.processing_status = 'failed'
                        doc.save()
                        failed += 1

                except Exception as e:
                    logger.error(f"error processing document {doc.id}: {e}")
                    doc.processing_status = 'failed'
                    doc.save()
                    failed += 1

            logger.info(f"user {request.user.id} processed {processed} pending documents, {failed} failed")

            return JsonResponse({
                'success': True,
                'processed': processed,
                'failed': failed
            })

        except Exception as e:
            logger.error(f"bulk reprocess pending error: {e}")
            return JsonResponse({'success': False, 'error': str(e)})


class RecycleBinView(LoginRequiredMixin, BaseUIView):
    """View for recycle bin (soft deleted documents)"""
    template_name = 'documents/recycle_bin.html'
    
    def get(self, request):
        context = self.get_context_data()
        
        # Get deleted documents
        deleted_documents = Document.objects.filter(
            user=request.user,
            is_deleted=True
        ).order_by('-deleted_at')
        
        # Calculate days until permanent deletion
        for doc in deleted_documents:
            if doc.deleted_at:
                days_old = (timezone.now() - doc.deleted_at).days
                doc.days_until_deletion = max(0, 30 - days_old)
                doc.will_be_deleted_at = doc.deleted_at + timedelta(days=30)
        
        context['documents'] = deleted_documents
        context['total_count'] = deleted_documents.count()
        
        # Group by deletion date
        deletion_groups = {}
        for doc in deleted_documents:
            if doc.deleted_at:
                date_key = doc.deleted_at.date()
                if date_key not in deletion_groups:
                    deletion_groups[date_key] = []
                deletion_groups[date_key].append(doc)
        
        context['deletion_groups'] = dict(sorted(deletion_groups.items(), reverse=True))
        
        return render(request, self.template_name, context)


class RestoreDocumentView(LoginRequiredMixin, View):
    """Restore documents from recycle bin"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            document_ids = data.get('document_ids', [])
            
            if not document_ids:
                return JsonResponse({'success': False, 'error': 'No documents selected'})
            
            # Restore documents
            with transaction.atomic():
                restored_count = Document.objects.filter(
                    id__in=document_ids,
                    user=request.user,
                    is_deleted=True
                ).update(
                    is_deleted=False,
                    deleted_at=None,
                    deleted_by=None
                )
            
            logger.info(f"User {request.user.id} restored {restored_count} documents")
            
            return JsonResponse({
                'success': True,
                'restored_count': restored_count
            })
            
        except Exception as e:
            logger.error(f"Restore error: {e}")
            return JsonResponse({'success': False, 'error': str(e)})


class PermanentDeleteView(LoginRequiredMixin, View):
    """Permanently delete documents from recycle bin"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            document_ids = data.get('document_ids', [])
            
            if not document_ids:
                return JsonResponse({'success': False, 'error': 'No documents selected'})
            
            # Permanently delete documents
            deleted_count = 0
            with transaction.atomic():
                documents = Document.objects.filter(
                    id__in=document_ids,
                    user=request.user,
                    is_deleted=True
                )
                
                # Delete associated files
                for doc in documents:
                    try:
                        if doc.file_path:
                            doc.file_path.delete(save=False)
                        if doc.thumbnail_path:
                            doc.thumbnail_path.delete(save=False)
                    except Exception as e:
                        logger.error(f"Error deleting files for document {doc.id}: {e}")
                
                deleted_count = documents.count()
                documents.delete()
            
            logger.info(f"User {request.user.id} permanently deleted {deleted_count} documents")
            
            return JsonResponse({
                'success': True,
                'deleted_count': deleted_count
            })
            
        except Exception as e:
            logger.error(f"Permanent delete error: {e}")
            return JsonResponse({'success': False, 'error': str(e)})


class EmptyRecycleBinView(LoginRequiredMixin, View):
    """Empty entire recycle bin"""
    
    def post(self, request):
        try:
            # Get all deleted documents for user
            documents = Document.objects.filter(
                user=request.user,
                is_deleted=True
            )
            
            deleted_count = 0
            with transaction.atomic():
                # Delete associated files
                for doc in documents:
                    try:
                        if doc.file_path:
                            doc.file_path.delete(save=False)
                        if doc.thumbnail_path:
                            doc.thumbnail_path.delete(save=False)
                    except Exception as e:
                        logger.error(f"Error deleting files for document {doc.id}: {e}")
                
                deleted_count = documents.count()
                documents.delete()
            
            logger.info(f"User {request.user.id} emptied recycle bin ({deleted_count} documents)")
            
            messages.success(request, f'{deleted_count} documents permanently deleted')
            return redirect('documents:recycle_bin')
            
        except Exception as e:
            logger.error(f"Empty recycle bin error: {e}")
            messages.error(request, f'Error emptying recycle bin: {e}')
            return redirect('documents:recycle_bin')


class DocumentExportView(LoginRequiredMixin, View):
    """Export documents to CSV or JSON"""
    
    def get(self, request):
        format_type = request.GET.get('format', 'csv')
        
        # Get documents for user
        documents = Document.objects.filter(
            user=request.user,
            is_deleted=False
        ).order_by('-created_at')
        
        if format_type == 'json':
            # Export as JSON
            data = []
            for doc in documents:
                data.append({
                    'id': str(doc.id),
                    'filename': doc.original_filename,
                    'type': doc.document_type,
                    'created': doc.created_at.isoformat(),
                    'ocr_text': doc.ocr_text or '',
                    'ocr_confidence': doc.ocr_confidence,
                    'status': doc.processing_status
                })
            
            response = HttpResponse(
                json.dumps(data, indent=2),
                content_type='application/json'
            )
            response['Content-Disposition'] = 'attachment; filename="documents_export.json"'
            
        else:
            # Export as CSV
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="documents_export.csv"'
            
            writer = csv.writer(response)
            writer.writerow(['ID', 'Filename', 'Type', 'Created', 'Status', 'OCR Confidence', 'OCR Text'])
            
            for doc in documents:
                writer.writerow([
                    str(doc.id),
                    doc.original_filename,
                    doc.document_type,
                    doc.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    doc.processing_status,
                    doc.ocr_confidence or '',
                    (doc.ocr_text or '')[:100]  # First 100 chars of OCR text
                ])
        
        logger.info(f"User {request.user.id} exported {documents.count()} documents as {format_type}")
        return response