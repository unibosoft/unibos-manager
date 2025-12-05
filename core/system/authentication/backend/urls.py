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
    # Identity Enhancement views
    AccountLinkInitView,
    AccountLinkVerifyView,
    AccountLinkStatusView,
    EmailVerificationRequestView,
    EmailVerificationConfirmView,
    HubKeyPairListView,
    HubKeyPairCreateView,
    HubPrimaryKeyView,
    PermissionSyncView,
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

    # Account Linking (Identity Enhancement)
    path('link/init/', AccountLinkInitView.as_view(), name='link-init'),
    path('link/verify/', AccountLinkVerifyView.as_view(), name='link-verify'),
    path('link/status/', AccountLinkStatusView.as_view(), name='link-status'),

    # Email Verification
    path('email/verify/request/', EmailVerificationRequestView.as_view(), name='email-verify-request'),
    path('email/verify/confirm/', EmailVerificationConfirmView.as_view(), name='email-verify-confirm'),

    # Hub Key Management
    path('keys/', HubKeyPairListView.as_view(), name='keys-list'),
    path('keys/create/', HubKeyPairCreateView.as_view(), name='keys-create'),
    path('keys/primary/', HubPrimaryKeyView.as_view(), name='keys-primary'),

    # Permission Sync
    path('permissions/sync/', PermissionSyncView.as_view(), name='permissions-sync'),

    # Session management
    path('', include(router.urls)),
]