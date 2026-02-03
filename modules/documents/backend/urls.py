"""
Documents module URL configuration
"""

from django.urls import path, include
from .views import (
    DocumentsDashboardView,
    DocumentListView,
    DocumentUploadView,
    DocumentDetailView,
    DocumentViewerView,
    CreditCardManagementView,
    SubscriptionManagementView,
    select_ocr_method,
    DocumentAnalysisView
)
from .api_views import (
    trigger_ocr,
    get_document_status,
    batch_trigger_ocr,
    regenerate_thumbnail,
    batch_regenerate_thumbnails,
    search_documents,
    test_structured_data,
    ai_batch_process,
    get_processing_status,
    ocr_pause,
    ocr_resume,
    ocr_status,
    analysis_retry_method,
    analysis_select_method,
    analysis_refresh,
    analysis_run_all,
    run_analysis_methods,
    get_analysis_status
)
from .bulk_views import (
    BulkDeleteView,
    BulkReprocessView,
    BulkReprocessPendingView,
    RecycleBinView,
    RestoreDocumentView,
    PermanentDeleteView,
    EmptyRecycleBinView,
    DocumentExportView
)
from . import receipt_processing_views
from . import simple_receipt_view
from .document_sharing_views import (
    share_document,
    view_shared_document,
    my_shared_documents,
    revoke_share,
    public_document_view,
)

app_name = 'documents'

# Import receipt URLs if available
try:
    from .receipt_urls import urlpatterns as receipt_patterns
except ImportError:
    receipt_patterns = []

urlpatterns = [
    # Main dashboard
    path('', DocumentsDashboardView.as_view(), name='dashboard'),

    # Document management
    path('list/', DocumentListView.as_view(), name='document_list'),
    path('upload/', DocumentUploadView.as_view(), name='upload'),
    path('document/<uuid:document_id>/', DocumentDetailView.as_view(), name='document_detail'),
    path('document/<uuid:document_id>/view/', DocumentViewerView.as_view(), name='document_view'),
    path('document/<uuid:document_id>/select-ocr/', select_ocr_method, name='select_ocr_method'),
    path('document/<uuid:document_id>/analysis/', DocumentAnalysisView.as_view(), name='document_analysis'),

    # Financial tools
    path('credit-cards/', CreditCardManagementView.as_view(), name='credit_cards'),
    path('subscriptions/', SubscriptionManagementView.as_view(), name='subscriptions'),
    
    # API endpoints for AJAX functionality
    path('api/document/<uuid:document_id>/trigger-ocr/', trigger_ocr, name='api_trigger_ocr'),
    path('api/document/<uuid:document_id>/status/', get_document_status, name='api_document_status'),
    path('api/document/<uuid:document_id>/regenerate-thumbnail/', regenerate_thumbnail, name='api_regenerate_thumbnail'),
    path('api/document/<uuid:document_id>/test-structured-data/', test_structured_data, name='api_test_structured_data'),
    path('api/batch-ocr/', batch_trigger_ocr, name='api_batch_ocr'),
    path('api/batch-thumbnails/', batch_regenerate_thumbnails, name='api_batch_thumbnails'),
    path('api/search/', search_documents, name='api_search'),
    path('api/ai-batch-process/', ai_batch_process, name='ai_batch_process'),
    path('api/receipt/<uuid:receipt_id>/', receipt_processing_views.get_receipt_detail, name='api_receipt_detail'),
    path('api/processing-status/', get_processing_status, name='api_processing_status'),
    path('api/ocr-pause/', ocr_pause, name='api_ocr_pause'),
    path('api/ocr-resume/', ocr_resume, name='api_ocr_resume'),
    path('api/ocr-status/', ocr_status, name='api_ocr_status'),

    # Analysis comparison endpoints
    path('api/analysis/<uuid:document_id>/', get_analysis_status, name='api_analysis_status'),
    path('api/analysis/<uuid:document_id>/retry/<str:method>/', analysis_retry_method, name='api_analysis_retry'),
    path('api/analysis/<uuid:document_id>/select/<str:method>/', analysis_select_method, name='api_analysis_select'),
    path('api/analysis/<uuid:document_id>/refresh/', analysis_refresh, name='api_analysis_refresh'),
    path('api/analysis/<uuid:document_id>/run-all/', analysis_run_all, name='api_analysis_run_all'),
    path('api/analysis/<uuid:document_id>/run-methods/', run_analysis_methods, name='api_analysis_run_methods'),

    # Bulk operations
    path('bulk/delete/', BulkDeleteView.as_view(), name='bulk_delete'),
    path('bulk/reprocess/', BulkReprocessView.as_view(), name='bulk_reprocess'),
    path('bulk/reprocess-pending/', BulkReprocessPendingView.as_view(), name='bulk_reprocess_pending'),
    path('bulk/export/', DocumentExportView.as_view(), name='export'),
    
    # Recycle bin
    path('recycle-bin/', RecycleBinView.as_view(), name='recycle_bin'),
    path('restore/', RestoreDocumentView.as_view(), name='restore'),
    path('permanent-delete/', PermanentDeleteView.as_view(), name='permanent_delete'),
    path('empty-recycle-bin/', EmptyRecycleBinView.as_view(), name='empty_recycle_bin'),
    
    # Receipt Processing with Gamification
    path('receipts/', include('modules.documents.backend.receipt_urls')),
    
    # Simple receipt hub for testing
    path('simple-receipt-hub/', simple_receipt_view.simple_receipt_hub, name='simple_receipt_hub'),
    path('process-receipt-ollama/', simple_receipt_view.process_receipt_ollama, name='process_receipt_ollama'),
    
    # Document sharing
    path('document/<uuid:document_id>/share/', share_document, name='share_document'),
    path('shared/<uuid:share_id>/', view_shared_document, name='view_shared_document'),
    path('shared/', my_shared_documents, name='my_shared_documents'),
    path('share/<uuid:share_id>/revoke/', revoke_share, name='revoke_share'),
    path('public/<str:share_link>/', public_document_view, name='public_document_view'),

    # Convenience redirects for receipt processing
    path('receipt-hub/', receipt_processing_views.receipt_dashboard, name='receipt_hub'),
    path('upload-receipt/', receipt_processing_views.upload_receipt, name='upload_receipt'),
    path('validate-receipt/<uuid:document_id>/', receipt_processing_views.validate_receipt, name='validate_receipt'),
    path('leaderboard/', receipt_processing_views.leaderboard, name='leaderboard'),
    path('achievements/', receipt_processing_views.achievements, name='achievements'),
    path('challenges/', receipt_processing_views.challenges, name='challenges'),
    path('document-validation/', receipt_processing_views.document_validation, name='document_validation'),
]