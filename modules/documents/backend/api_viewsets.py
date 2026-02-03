"""
Documents Module - DRF REST API ViewSets
Provides /api/v1/documents/ endpoints for CRUD operations
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Q, Count
from django.utils import timezone
from django.shortcuts import get_object_or_404
import logging

from .models import (
    Document, ParsedReceipt, ReceiptItem,
    DocumentBatch, OCRTemplate,
    CreditCard, Subscription, ExpenseCategory, ExpenseGroup,
    ProcessingStatus
)
from .serializers import (
    DocumentSerializer, DocumentListSerializer, DocumentUploadSerializer,
    ParsedReceiptSerializer, ReceiptItemSerializer,
    DocumentBatchSerializer,
    OCRTemplateSerializer,
    CreditCardSerializer, SubscriptionSerializer,
    ExpenseCategorySerializer, ExpenseGroupSerializer,
    DocumentStatisticsSerializer
)

logger = logging.getLogger('documents.api')


class DocumentPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class IsOwner(permissions.BasePermission):
    """Only allow owners of an object to access it"""

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class DocumentViewSet(viewsets.ModelViewSet):
    """
    Document CRUD operations with filtering and search.

    list: GET /api/v1/documents/documents/
    create: POST /api/v1/documents/documents/
    retrieve: GET /api/v1/documents/documents/{id}/
    update: PUT /api/v1/documents/documents/{id}/
    partial_update: PATCH /api/v1/documents/documents/{id}/
    destroy: DELETE /api/v1/documents/documents/{id}/ (soft delete)
    """
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    pagination_class = DocumentPagination
    parser_classes = [MultiPartParser, FormParser]

    def get_serializer_class(self):
        if self.action == 'list':
            return DocumentListSerializer
        return DocumentSerializer

    def get_queryset(self):
        queryset = Document.objects.filter(
            user=self.request.user,
            is_deleted=False
        ).select_related('parsed_receipt')

        # Filter by document type
        doc_type = self.request.query_params.get('type')
        if doc_type:
            queryset = queryset.filter(document_type=doc_type)

        # Filter by processing status
        doc_status = self.request.query_params.get('status')
        if doc_status:
            queryset = queryset.filter(processing_status=doc_status)

        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(original_filename__icontains=search) |
                Q(ocr_text__icontains=search) |
                Q(parsed_receipt__store_name__icontains=search)
            )

        return queryset.order_by('-uploaded_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        """Soft delete instead of hard delete"""
        instance.is_deleted = True
        instance.deleted_at = timezone.now()
        instance.deleted_by = self.request.user
        instance.save()

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """GET /api/v1/documents/documents/statistics/ - Document stats"""
        docs = Document.objects.filter(user=request.user, is_deleted=False)
        stats = docs.aggregate(
            total=Count('id'),
            pending=Count('id', filter=Q(processing_status='pending')),
            processing=Count('id', filter=Q(processing_status='processing')),
            completed=Count('id', filter=Q(processing_status='completed')),
            failed=Count('id', filter=Q(processing_status='failed')),
        )
        deleted = Document.objects.filter(user=request.user, is_deleted=True).count()

        # Documents by type
        by_type = {}
        for item in docs.values('document_type').annotate(count=Count('id')):
            by_type[item['document_type']] = item['count']

        # Recent uploads
        recent = docs.order_by('-uploaded_at')[:5]
        recent_serializer = DocumentListSerializer(recent, many=True)

        return Response({
            'total_documents': stats['total'],
            'pending_documents': stats['pending'],
            'processing_documents': stats['processing'],
            'completed_documents': stats['completed'],
            'failed_documents': stats['failed'],
            'deleted_documents': deleted,
            'documents_by_type': by_type,
            'recent_uploads': recent_serializer.data,
        })

    @action(detail=True, methods=['post'])
    def trigger_ocr(self, request, pk=None):
        """POST /api/v1/documents/documents/{id}/trigger_ocr/ - Trigger OCR"""
        document = self.get_object()

        if document.processing_status == 'processing':
            return Response(
                {'error': 'Document is already being processed'},
                status=status.HTTP_400_BAD_REQUEST
            )

        document.processing_status = 'processing'
        document.save()

        try:
            from .ocr_service import OCRProcessor
            ocr_processor = OCRProcessor()
            result = ocr_processor.process_document(
                document.file_path.path,
                document_type=document.document_type,
                force_ocr=True,
                document_instance=document
            )

            if result['success'] and result.get('ocr_text'):
                document.ocr_text = result['ocr_text']
                document.ocr_confidence = result.get('confidence', 0)
                document.processing_status = 'completed'
                document.ocr_processed_at = timezone.now()
                document.save()

                return Response({
                    'success': True,
                    'text_length': len(result['ocr_text']),
                    'confidence': result.get('confidence', 0),
                })
            else:
                document.processing_status = 'failed'
                document.save()
                return Response(
                    {'error': result.get('error', 'OCR failed')},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            document.processing_status = 'failed'
            document.save()
            logger.error(f"OCR trigger failed: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def analyze(self, request, pk=None):
        """POST /api/v1/documents/documents/{id}/analyze/ - Run OCR analysis"""
        document = self.get_object()
        methods = request.data.get('methods', [])
        force_refresh = request.data.get('force_refresh', False)

        if not methods:
            return Response(
                {'error': 'methods parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        valid_methods = [
            'tesseract', 'paddleocr', 'llama_vision', 'hybrid',
            'trocr', 'donut', 'layoutlmv3', 'surya', 'doctr',
            'easyocr', 'ocrmypdf'
        ]
        invalid = [m for m in methods if m not in valid_methods]
        if invalid:
            return Response(
                {'error': f'Invalid methods: {", ".join(invalid)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            from .analysis_service import OCRAnalysisService
            import threading

            def run_analysis():
                import asyncio
                try:
                    try:
                        loop = asyncio.get_event_loop()
                    except RuntimeError:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)

                    analyzer = OCRAnalysisService()
                    analyzer.analyze_document(
                        document,
                        force_refresh=force_refresh,
                        methods_to_run=methods,
                    )
                except Exception as e:
                    logger.error(f"Background analysis failed: {e}")
                finally:
                    try:
                        if loop and not loop.is_closed():
                            loop.close()
                    except Exception:
                        pass

            thread = threading.Thread(target=run_analysis, daemon=True)
            thread.start()

            return Response({
                'success': True,
                'message': f'Analysis started for {len(methods)} methods',
                'methods': methods,
            })
        except Exception as e:
            logger.error(f"Analysis trigger failed: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def recycle_bin(self, request):
        """GET /api/v1/documents/documents/recycle_bin/ - List deleted docs"""
        deleted = Document.objects.filter(
            user=request.user,
            is_deleted=True
        ).order_by('-deleted_at')

        page = self.paginate_queryset(deleted)
        if page is not None:
            serializer = DocumentListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = DocumentListSerializer(deleted, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """POST /api/v1/documents/documents/{id}/restore/ - Restore from bin"""
        document = get_object_or_404(
            Document, id=pk, user=request.user, is_deleted=True
        )
        document.is_deleted = False
        document.deleted_at = None
        document.deleted_by = None
        document.save()

        return Response({'success': True, 'message': 'Document restored'})


class ParsedReceiptViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Parsed receipt read-only operations.

    list: GET /api/v1/documents/receipts/
    retrieve: GET /api/v1/documents/receipts/{id}/
    """
    serializer_class = ParsedReceiptSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = DocumentPagination

    def get_queryset(self):
        return ParsedReceipt.objects.filter(
            document__user=self.request.user,
            document__is_deleted=False
        ).select_related('document').prefetch_related('items').order_by('-transaction_date')

    @action(detail=True, methods=['get'])
    def items(self, request, pk=None):
        """GET /api/v1/documents/receipts/{id}/items/ - Receipt items"""
        receipt = self.get_object()
        items = receipt.items.all().order_by('id')
        serializer = ReceiptItemSerializer(items, many=True)
        return Response(serializer.data)


class DocumentBatchViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Document batch operations.

    list: GET /api/v1/documents/batches/
    retrieve: GET /api/v1/documents/batches/{id}/
    """
    serializer_class = DocumentBatchSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = DocumentPagination

    def get_queryset(self):
        return DocumentBatch.objects.filter(
            user=self.request.user
        ).order_by('-started_at')


class OCRTemplateViewSet(viewsets.ModelViewSet):
    """
    OCR template CRUD operations.

    list: GET /api/v1/documents/templates/
    create: POST /api/v1/documents/templates/
    retrieve: GET /api/v1/documents/templates/{id}/
    update: PUT /api/v1/documents/templates/{id}/
    destroy: DELETE /api/v1/documents/templates/{id}/
    """
    serializer_class = OCRTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = OCRTemplate.objects.all()


class CreditCardViewSet(viewsets.ModelViewSet):
    """
    Credit card CRUD operations.

    list: GET /api/v1/documents/credit-cards/
    create: POST /api/v1/documents/credit-cards/
    retrieve: GET /api/v1/documents/credit-cards/{id}/
    update: PUT /api/v1/documents/credit-cards/{id}/
    destroy: DELETE /api/v1/documents/credit-cards/{id}/
    """
    serializer_class = CreditCardSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return CreditCard.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SubscriptionViewSet(viewsets.ModelViewSet):
    """
    Subscription CRUD operations.

    list: GET /api/v1/documents/subscriptions/
    create: POST /api/v1/documents/subscriptions/
    retrieve: GET /api/v1/documents/subscriptions/{id}/
    update: PUT /api/v1/documents/subscriptions/{id}/
    destroy: DELETE /api/v1/documents/subscriptions/{id}/
    """
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        queryset = Subscription.objects.filter(user=self.request.user)

        # Filter by active status
        active = self.request.query_params.get('active')
        if active is not None:
            queryset = queryset.filter(is_active=active.lower() == 'true')

        return queryset.order_by('service_name')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class GamificationViewSet(viewsets.ViewSet):
    """
    Gamification read-only endpoints.

    profile: GET /api/v1/documents/gamification/profile/
    achievements: GET /api/v1/documents/gamification/achievements/
    leaderboard: GET /api/v1/documents/gamification/leaderboard/
    """
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def profile(self, request):
        """GET /api/v1/documents/gamification/profile/"""
        try:
            from .gamification_models import UserProfile
            profile, _ = UserProfile.objects.get_or_create(user=request.user)
            return Response({
                'total_points': profile.total_points,
                'current_level': profile.current_level,
                'experience_points': profile.experience_points,
                'next_level_requirement': profile.get_next_level_requirement(),
                'receipts_processed': profile.receipts_processed,
                'receipts_validated': profile.receipts_validated,
                'accuracy_score': profile.accuracy_score,
                'streak_days': profile.streak_days,
                'rank': UserProfile.objects.filter(
                    total_points__gt=profile.total_points
                ).count() + 1,
            })
        except Exception as e:
            logger.error(f"Gamification profile error: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def achievements(self, request):
        """GET /api/v1/documents/gamification/achievements/"""
        try:
            from .gamification_models import Achievement
            achievements = Achievement.objects.filter(user=request.user)
            data = [{
                'id': a.id,
                'type': a.achievement_type,
                'name': a.name,
                'description': a.description,
                'icon': a.icon,
                'rarity': a.rarity,
                'points_awarded': a.points_awarded,
                'unlocked_at': a.unlocked_at.isoformat(),
            } for a in achievements]
            return Response(data)
        except Exception as e:
            logger.error(f"Achievements error: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def leaderboard(self, request):
        """GET /api/v1/documents/gamification/leaderboard/"""
        try:
            from .gamification_models import UserProfile
            period = request.query_params.get('period', 'all_time')
            limit = min(int(request.query_params.get('limit', 20)), 100)

            profiles = UserProfile.objects.all().order_by('-total_points')[:limit]
            data = [{
                'rank': idx + 1,
                'username': p.user.username,
                'total_points': p.total_points,
                'current_level': p.current_level,
                'receipts_processed': p.receipts_processed,
                'is_current_user': p.user == request.user,
            } for idx, p in enumerate(profiles)]
            return Response(data)
        except Exception as e:
            logger.error(f"Leaderboard error: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
