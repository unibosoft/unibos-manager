"""
Authentication views for UNIBOS
Implements secure JWT-based authentication with rate limiting
"""

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone
from rest_framework import status, generics
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.signals import user_logged_in, user_logged_out

from .serializers import (
    CustomTokenObtainPairSerializer,
    RegisterSerializer,
    ChangePasswordSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    UserSessionSerializer,
    TwoFactorSetupSerializer,
    TwoFactorVerifySerializer,
)
from .models import (
    RefreshTokenBlacklist,
    UserSession,
    LoginAttempt,
    PasswordResetToken,
    TwoFactorAuth,
)
from .utils import (
    get_client_ip,
    send_password_reset_email,
    generate_otp_secret,
    verify_otp,
    generate_backup_codes,
)
from core.system.common.backend.throttles import AuthRateThrottle

User = get_user_model()


class LoginView(TokenObtainPairView):
    """Custom login view with additional security features"""
    serializer_class = CustomTokenObtainPairSerializer
    throttle_classes = [AuthRateThrottle]
    
    def post(self, request, *args, **kwargs):
        # Check for too many failed login attempts
        ip_address = get_client_ip(request)
        username = request.data.get('username', '')
        
        # Check IP-based rate limiting
        ip_failures = LoginAttempt.get_recent_failures(ip_address=ip_address, minutes=30)
        if ip_failures >= 5:
            return Response(
                {"detail": "Too many failed login attempts. Please try again later."},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        
        # Check username-based rate limiting
        user_failures = LoginAttempt.get_recent_failures(username=username, minutes=30)
        if user_failures >= 3:
            return Response(
                {"detail": "Too many failed login attempts for this account. Please try again later."},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        
        # Attempt login
        response = super().post(request, *args, **kwargs)
        
        # Track login attempt
        is_successful = response.status_code == 200
        user = None
        failure_reason = ''
        
        if is_successful:
            try:
                user = User.objects.get(username=username)
                # Send login signal
                user_logged_in.send(sender=User, request=request, user=user)
            except User.DoesNotExist:
                pass
        else:
            failure_reason = 'Invalid credentials'
        
        LoginAttempt.objects.create(
            username=username,
            ip_address=ip_address,
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            is_successful=is_successful,
            failure_reason=failure_reason,
            user=user
        )
        
        return response


class RegisterView(generics.CreateAPIView):
    """User registration view"""
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    throttle_classes = [AuthRateThrottle]
    
    @transaction.atomic
    def perform_create(self, serializer):
        user = serializer.save()
        # Generate tokens for immediate login
        refresh = RefreshToken.for_user(user)
        
        # Track session
        request = self.request
        UserSession.objects.create(
            user=user,
            session_key=refresh.payload['jti'],
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            expires_at=refresh['exp']
        )
        
        # Add tokens to response
        self.tokens = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        if hasattr(self, 'tokens'):
            response.data['tokens'] = self.tokens
        return response


class LogoutView(APIView):
    """Logout view with token blacklisting"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            # Get refresh token from request
            refresh_token = request.data.get('refresh')
            if refresh_token:
                # Blacklist the refresh token
                token = RefreshToken(refresh_token)
                RefreshTokenBlacklist.objects.create(
                    token=refresh_token,
                    user=request.user,
                    expires_at=timezone.datetime.fromtimestamp(token['exp'])
                )
                
                # Invalidate session
                UserSession.objects.filter(
                    user=request.user,
                    session_key=token['jti']
                ).update(is_active=False)
            
            # Send logout signal
            user_logged_out.send(sender=User, request=request, user=request.user)
            
            return Response(
                {"detail": "Successfully logged out."},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"detail": "Invalid token."},
                status=status.HTTP_400_BAD_REQUEST
            )


class LogoutAllView(APIView):
    """Logout from all devices"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # Invalidate all active sessions
        UserSession.objects.filter(
            user=request.user,
            is_active=True
        ).update(is_active=False)
        
        # Note: We can't blacklist all tokens without storing them
        # In production, you might want to change the user's JWT secret
        
        return Response(
            {"detail": "Successfully logged out from all devices."},
            status=status.HTTP_200_OK
        )


class ChangePasswordView(APIView):
    """Change password view"""
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer
    
    def post(self, request):
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # Invalidate all sessions except current
        current_session = request.auth.payload.get('jti') if request.auth else None
        UserSession.objects.filter(
            user=request.user,
            is_active=True
        ).exclude(
            session_key=current_session
        ).update(is_active=False)
        
        return Response(
            {"detail": "Password changed successfully."},
            status=status.HTTP_200_OK
        )


class PasswordResetRequestView(APIView):
    """Request password reset view"""
    permission_classes = [AllowAny]
    serializer_class = PasswordResetRequestSerializer
    throttle_classes = [AuthRateThrottle]
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        user = User.objects.get(email=email)
        
        # Generate reset token
        import secrets
        token = secrets.token_urlsafe(32)
        
        # Create password reset token
        reset_token = PasswordResetToken.objects.create(
            user=user,
            token=token,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            expires_at=timezone.now() + timezone.timedelta(hours=1)
        )
        
        # Send reset email
        send_password_reset_email(user, token)
        
        return Response(
            {"detail": "Password reset email sent."},
            status=status.HTTP_200_OK
        )


class PasswordResetConfirmView(APIView):
    """Confirm password reset view"""
    permission_classes = [AllowAny]
    serializer_class = PasswordResetConfirmSerializer
    
    @transaction.atomic
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']
        
        # Verify token
        try:
            reset_token = PasswordResetToken.objects.get(
                token=token,
                is_used=False
            )
            
            if not reset_token.is_valid():
                return Response(
                    {"detail": "Invalid or expired token."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Reset password
            user = reset_token.user
            user.set_password(new_password)
            user.save()
            
            # Mark token as used
            reset_token.mark_used()
            
            # Invalidate all user sessions
            UserSession.objects.filter(
                user=user,
                is_active=True
            ).update(is_active=False)
            
            return Response(
                {"detail": "Password reset successfully."},
                status=status.HTTP_200_OK
            )
            
        except PasswordResetToken.DoesNotExist:
            return Response(
                {"detail": "Invalid token."},
                status=status.HTTP_400_BAD_REQUEST
            )


class SessionViewSet(ViewSet):
    """Manage user sessions"""
    permission_classes = [IsAuthenticated]
    serializer_class = UserSessionSerializer
    
    def list(self, request):
        """List all active sessions"""
        sessions = UserSession.objects.filter(
            user=request.user,
            is_active=True
        )
        serializer = self.serializer_class(sessions, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def revoke(self, request, pk=None):
        """Revoke a specific session"""
        try:
            session = UserSession.objects.get(
                pk=pk,
                user=request.user
            )
            session.is_active = False
            session.save()
            
            return Response(
                {"detail": "Session revoked successfully."},
                status=status.HTTP_200_OK
            )
        except UserSession.DoesNotExist:
            return Response(
                {"detail": "Session not found."},
                status=status.HTTP_404_NOT_FOUND
            )


class TwoFactorSetupView(APIView):
    """Setup two-factor authentication"""
    permission_classes = [IsAuthenticated]
    serializer_class = TwoFactorSetupSerializer
    
    def post(self, request):
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        # Generate secret and backup codes
        secret = generate_otp_secret()
        backup_codes = generate_backup_codes()
        
        # Create or update 2FA settings
        two_factor, created = TwoFactorAuth.objects.update_or_create(
            user=request.user,
            defaults={
                'secret': secret,
                'backup_codes': backup_codes,
                'is_enabled': False
            }
        )
        
        # Generate QR code URL
        import pyotp
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name=request.user.email,
            issuer_name='UNIBOS'
        )
        
        return Response({
            'secret': secret,
            'qr_code': provisioning_uri,
            'backup_codes': backup_codes
        })


class TwoFactorVerifyView(APIView):
    """Verify and enable two-factor authentication"""
    permission_classes = [IsAuthenticated]
    serializer_class = TwoFactorVerifySerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        code = serializer.validated_data['code']
        
        try:
            two_factor = TwoFactorAuth.objects.get(user=request.user)
            
            if verify_otp(two_factor.secret, code):
                two_factor.is_enabled = True
                two_factor.save()
                
                return Response(
                    {"detail": "Two-factor authentication enabled successfully."},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"detail": "Invalid verification code."},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except TwoFactorAuth.DoesNotExist:
            return Response(
                {"detail": "Two-factor authentication not set up."},
                status=status.HTTP_400_BAD_REQUEST
            )


class RefreshTokenView(TokenRefreshView):
    """Custom token refresh view"""
    
    def post(self, request, *args, **kwargs):
        # Check if refresh token is blacklisted
        refresh_token = request.data.get('refresh')
        
        if RefreshTokenBlacklist.objects.filter(token=refresh_token).exists():
            return Response(
                {"detail": "Token is blacklisted."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        return super().post(request, *args, **kwargs)