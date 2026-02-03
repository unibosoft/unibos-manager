"""
Documents Module - DRF REST API URL Configuration
Registered at /api/v1/documents/
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .api_viewsets import (
    DocumentViewSet,
    ParsedReceiptViewSet,
    DocumentBatchViewSet,
    OCRTemplateViewSet,
    CreditCardViewSet,
    SubscriptionViewSet,
    GamificationViewSet,
)

# DRF Router
router = DefaultRouter()
router.register(r'documents', DocumentViewSet, basename='document')
router.register(r'receipts', ParsedReceiptViewSet, basename='receipt')
router.register(r'batches', DocumentBatchViewSet, basename='batch')
router.register(r'templates', OCRTemplateViewSet, basename='template')
router.register(r'credit-cards', CreditCardViewSet, basename='creditcard')
router.register(r'subscriptions', SubscriptionViewSet, basename='subscription')
router.register(r'gamification', GamificationViewSet, basename='gamification')

urlpatterns = [
    path('', include(router.urls)),
]
