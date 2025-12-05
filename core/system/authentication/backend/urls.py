"""
Authentication URL configuration
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    LoginView,
    RegisterView,
    LogoutView,
    LogoutAllView,
    ChangePasswordView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    SessionViewSet,
    TwoFactorSetupView,
    TwoFactorVerifyView,
    RefreshTokenView,
    OfflineLoginView,
)

router = DefaultRouter()
router.register('sessions', SessionViewSet, basename='session')

app_name = 'authentication'

urlpatterns = [
    # Token endpoints
    path('login/', LoginView.as_view(), name='login'),
    path('login/offline/', OfflineLoginView.as_view(), name='offline-login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('logout-all/', LogoutAllView.as_view(), name='logout-all'),
    path('refresh/', RefreshTokenView.as_view(), name='token-refresh'),
    
    # Password management
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('reset-password/', PasswordResetRequestView.as_view(), name='reset-password'),
    path('reset-password/confirm/', PasswordResetConfirmView.as_view(), name='reset-password-confirm'),
    
    # Two-factor authentication
    path('2fa/setup/', TwoFactorSetupView.as_view(), name='2fa-setup'),
    path('2fa/verify/', TwoFactorVerifyView.as_view(), name='2fa-verify'),
    
    # Session management
    path('', include(router.urls)),
]