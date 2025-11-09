"""
URL Configuration for Receipt Processing with Gamification
"""

from django.urls import path
from . import receipt_processing_views as views

app_name = 'receipt_processing'

urlpatterns = [
    # Main dashboard
    path('dashboard/', views.receipt_dashboard, name='dashboard'),
    
    # Receipt processing workflow
    path('upload/', views.upload_receipt, name='upload'),
    path('validate/<uuid:document_id>/', views.validate_receipt, name='validate'),
    path('complete/<uuid:document_id>/', views.complete_receipt, name='complete'),
    
    # Gamification features
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('achievements/', views.achievements, name='achievements'),
    path('challenges/', views.challenges, name='challenges'),
    path('document-validation/', views.document_validation, name='document_validation'),
    
    # API endpoints
    path('api/receipt-status/<uuid:document_id>/', views.api_receipt_status, name='api_receipt_status'),
    path('api/user-stats/', views.api_user_stats, name='api_user_stats'),
    
    # OCR endpoints
    path('rescan-ocr/<uuid:document_id>/', views.rescan_ocr, name='rescan_ocr'),
    path('update-ocr/<uuid:document_id>/', views.update_ocr, name='update_ocr'),
    path('ai-extract/', views.ai_extract_fields, name='ai_extract'),
    
    # Image processing endpoints
    path('crop-image/<uuid:document_id>/', views.crop_image, name='crop_image'),
    path('optimize-for-ocr/<uuid:document_id>/', views.optimize_for_ocr, name='optimize_for_ocr'),
    path('reset-image/<uuid:document_id>/', views.reset_image, name='reset_image'),
    
    # OpenStreetMap endpoints
    path('search-nearby-business/', views.search_nearby_business, name='search_nearby_business'),
]