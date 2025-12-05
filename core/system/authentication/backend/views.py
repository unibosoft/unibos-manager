"""
Authentication views for UNIBOS
Implements secure JWT-based authentication with rate limiting
"""

from datetime import datetime, timezone as dt_timezone
from django.conf import settings
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
    # Identity Enhancement serializers
    AccountLinkSerializer,
    AccountLinkInitSerializer,
    AccountLinkVerifySerializer,
    EmailVerificationRequestSerializer,
    EmailVerificationConfirmSerializer,
    HubKeyPairSerializer,
    HubKeyPairCreateSerializer,
    PermissionSyncSerializer,
)
from .models import (
    RefreshTokenBlacklist,
    UserSession,
    LoginAttempt,
    PasswordResetToken,
    TwoFactorAuth,
    # Identity Enhancement models
    AccountLink,
    EmailVerificationToken,
    HubKeyPair,
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
        # refresh['exp'] Unix timestamp, datetime'a cevir
        expires_dt = datetime.fromtimestamp(refresh['exp'], tz=dt_timezone.utc)
        UserSession.objects.create(
            user=user,
            session_key=refresh.payload['jti'],
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            expires_at=expires_dt
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
                expires_dt = datetime.fromtimestamp(token['exp'], tz=dt_timezone.utc)
                RefreshTokenBlacklist.objects.create(
                    token=refresh_token,
                    user=request.user,
                    expires_at=expires_dt
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


class OfflineLoginView(APIView):
    """
    Offline login view for Node-only authentication

    This view allows users to login on a Node when the Hub is unreachable.
    It uses cached user credentials (offline_hash) that were stored during
    a previous successful Hub login.

    Flow:
    1. Client provides username/email and password
    2. Node checks local UserOfflineCache for the user
    3. If found and cache is valid, verify password against offline_hash
    4. Generate a local JWT token (signed with node's key)
    5. Return token with offline_mode=true flag
    """
    permission_classes = [AllowAny]
    throttle_classes = [AuthRateThrottle]

    def post(self, request):
        from django.contrib.auth.hashers import check_password
        import logging

        logger = logging.getLogger('authentication')

        username = request.data.get('username', '').strip()
        password = request.data.get('password', '')

        if not username or not password:
            return Response(
                {"detail": "Username and password are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check rate limiting
        ip_address = get_client_ip(request)
        ip_failures = LoginAttempt.get_recent_failures(ip_address=ip_address, minutes=30)
        if ip_failures >= 5:
            return Response(
                {"detail": "Too many failed login attempts. Please try again later."},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        # Try to find user locally (either by username or email)
        try:
            if '@' in username:
                user = User.objects.get(email=username)
            else:
                user = User.objects.get(username=username)
        except User.DoesNotExist:
            # Try offline cache if user doesn't exist locally
            try:
                from .models import UserOfflineCache
                if '@' in username:
                    cache_entry = UserOfflineCache.objects.get(email=username)
                else:
                    cache_entry = UserOfflineCache.objects.get(username=username)

                # Verify password against cached hash
                if not check_password(password, cache_entry.offline_hash):
                    LoginAttempt.objects.create(
                        username=username,
                        ip_address=ip_address,
                        user_agent=request.META.get('HTTP_USER_AGENT', ''),
                        is_successful=False,
                        failure_reason='invalid_password_offline'
                    )
                    return Response(
                        {"detail": "Invalid credentials."},
                        status=status.HTTP_401_UNAUTHORIZED
                    )

                # Check cache validity
                if not cache_entry.is_valid():
                    return Response(
                        {"detail": "Offline credentials expired. Please login online to refresh."},
                        status=status.HTTP_401_UNAUTHORIZED
                    )

                # Generate offline JWT
                response_data = self._generate_offline_token(cache_entry, request)
                return Response(response_data, status=status.HTTP_200_OK)

            except Exception:
                LoginAttempt.objects.create(
                    username=username,
                    ip_address=ip_address,
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    is_successful=False,
                    failure_reason='user_not_found'
                )
                return Response(
                    {"detail": "Invalid credentials."},
                    status=status.HTTP_401_UNAUTHORIZED
                )

        # User exists locally - verify password
        if not user.check_password(password):
            LoginAttempt.objects.create(
                username=username,
                ip_address=ip_address,
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                is_successful=False,
                failure_reason='invalid_password',
                user=user
            )
            return Response(
                {"detail": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Generate JWT for local user
        refresh = RefreshToken.for_user(user)

        # Add custom claims
        refresh['email'] = user.email
        refresh['username'] = user.username
        refresh['is_staff'] = user.is_staff
        refresh['offline_mode'] = True  # Mark as offline session

        # Track session
        expires_dt = datetime.fromtimestamp(refresh['exp'], tz=dt_timezone.utc)
        UserSession.objects.create(
            user=user,
            session_key=refresh.payload['jti'],
            ip_address=ip_address,
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            device_info={'offline_mode': True},
            expires_at=expires_dt
        )

        # Track successful login
        LoginAttempt.objects.create(
            username=username,
            ip_address=ip_address,
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            is_successful=True,
            user=user
        )

        logger.info(f"Offline login successful for user {user.username} from {ip_address}")

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': str(user.id),
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
            },
            'offline_mode': True,
            'offline_hash': user.password,  # For caching on client
        }, status=status.HTTP_200_OK)

    def _generate_offline_token(self, cache_entry, request):
        """Generate JWT token from offline cache entry"""
        from rest_framework_simplejwt.tokens import AccessToken
        import uuid

        # Create a minimal access token
        token = AccessToken()
        token['user_id'] = str(cache_entry.global_uuid)
        token['username'] = cache_entry.username
        token['email'] = cache_entry.email
        token['is_staff'] = cache_entry.is_staff
        token['offline_mode'] = True
        token['jti'] = str(uuid.uuid4())

        # Track login attempt
        ip_address = get_client_ip(request)
        LoginAttempt.objects.create(
            username=cache_entry.username,
            ip_address=ip_address,
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            is_successful=True,
            failure_reason='',
        )

        return {
            'access': str(token),
            'refresh': None,  # No refresh for pure offline mode
            'user': {
                'id': str(cache_entry.global_uuid),
                'username': cache_entry.username,
                'email': cache_entry.email,
                'first_name': cache_entry.first_name,
                'last_name': cache_entry.last_name,
                'is_staff': cache_entry.is_staff,
                'is_superuser': cache_entry.is_superuser,
            },
            'offline_mode': True,
            'cache_expires_at': cache_entry.cache_valid_until.isoformat() if cache_entry.cache_valid_until else None,
        }


# ========== Identity Enhancement Views ==========

class AccountLinkInitView(APIView):
    """
    Initialize account linking between local Node account and Hub account.

    Flow:
    1. User provides Hub credentials
    2. Node authenticates with Hub
    3. Hub sends verification code to user's email
    4. Verification code stored locally for later verification
    """
    permission_classes = [IsAuthenticated]
    serializer_class = AccountLinkInitSerializer

    def post(self, request):
        import requests
        import secrets
        import logging

        logger = logging.getLogger('authentication')
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        hub_url = serializer.validated_data['hub_url'].rstrip('/')
        hub_username = serializer.validated_data['hub_username']
        hub_password = serializer.validated_data['hub_password']

        # Check if user already has a link
        if hasattr(request.user, 'hub_link'):
            existing_link = request.user.hub_link
            if existing_link.status == 'active':
                return Response(
                    {"detail": "Account is already linked to a Hub account."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            # Delete pending/revoked link to allow re-linking
            existing_link.delete()

        try:
            # Authenticate with Hub
            auth_response = requests.post(
                f"{hub_url}/api/v1/auth/login/",
                json={'username': hub_username, 'password': hub_password},
                timeout=10
            )

            if auth_response.status_code != 200:
                return Response(
                    {"detail": "Invalid Hub credentials."},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            hub_data = auth_response.json()
            hub_user = hub_data.get('user', {})

            # Generate verification code
            verification_code = ''.join(secrets.choice('0123456789') for _ in range(6))

            # Create account link (pending)
            link = AccountLink.objects.create(
                local_user=request.user,
                hub_user_uuid=hub_user.get('id'),
                hub_username=hub_user.get('username'),
                hub_email=hub_user.get('email'),
                hub_url=hub_url,
                verification_code=verification_code,
                verification_expires=timezone.now() + timezone.timedelta(hours=1),
                status='pending'
            )

            # TODO: Send verification code to Hub user's email
            # For now, return the code in response (dev mode)
            logger.info(f"Account link initiated: {request.user.username} -> {hub_username}")

            return Response({
                'message': 'Verification code sent to your Hub email.',
                'link_id': str(link.id),
                'hub_username': hub_username,
                'hub_email': hub_user.get('email'),
                # DEV ONLY - remove in production
                'verification_code': verification_code if settings.DEBUG else None,
            }, status=status.HTTP_201_CREATED)

        except requests.RequestException as e:
            logger.error(f"Hub connection failed: {e}")
            return Response(
                {"detail": "Could not connect to Hub. Please try again later."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )


class AccountLinkVerifyView(APIView):
    """Verify account link with verification code"""
    permission_classes = [IsAuthenticated]
    serializer_class = AccountLinkVerifySerializer

    def post(self, request):
        import logging
        logger = logging.getLogger('authentication')

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        verification_code = serializer.validated_data['verification_code']

        try:
            link = AccountLink.objects.get(
                local_user=request.user,
                status='pending'
            )

            if link.verification_expires and link.verification_expires < timezone.now():
                return Response(
                    {"detail": "Verification code has expired. Please initiate linking again."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if link.verification_code != verification_code:
                return Response(
                    {"detail": "Invalid verification code."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Verify the link
            link.verify()
            logger.info(f"Account link verified: {request.user.username} -> {link.hub_username}")

            return Response({
                'message': 'Account successfully linked to Hub.',
                'link': AccountLinkSerializer(link).data
            }, status=status.HTTP_200_OK)

        except AccountLink.DoesNotExist:
            return Response(
                {"detail": "No pending account link found."},
                status=status.HTTP_404_NOT_FOUND
            )


class AccountLinkStatusView(APIView):
    """Get current account link status"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            link = AccountLink.objects.get(local_user=request.user)
            return Response(AccountLinkSerializer(link).data)
        except AccountLink.DoesNotExist:
            return Response(
                {"detail": "No account link found.", "linked": False},
                status=status.HTTP_200_OK
            )

    def delete(self, request):
        """Revoke account link"""
        try:
            link = AccountLink.objects.get(local_user=request.user)
            link.status = 'revoked'
            link.save()
            return Response(
                {"detail": "Account link revoked successfully."},
                status=status.HTTP_200_OK
            )
        except AccountLink.DoesNotExist:
            return Response(
                {"detail": "No account link found."},
                status=status.HTTP_404_NOT_FOUND
            )


class EmailVerificationRequestView(APIView):
    """Request email verification token"""
    permission_classes = [IsAuthenticated]
    serializer_class = EmailVerificationRequestSerializer

    def post(self, request):
        import logging
        logger = logging.getLogger('authentication')

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        verification_type = serializer.validated_data.get('verification_type', 'registration')

        # Create verification token
        token = EmailVerificationToken.create_token(
            user=request.user,
            email=email,
            verification_type=verification_type,
            ip_address=get_client_ip(request)
        )

        # TODO: Send verification email
        logger.info(f"Email verification requested: {request.user.username} -> {email}")

        return Response({
            'message': 'Verification email sent.',
            'email': email,
            # DEV ONLY
            'token': token.token if settings.DEBUG else None,
        }, status=status.HTTP_201_CREATED)


class EmailVerificationConfirmView(APIView):
    """Confirm email verification"""
    permission_classes = [AllowAny]
    serializer_class = EmailVerificationConfirmSerializer

    def post(self, request):
        import logging
        logger = logging.getLogger('authentication')

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        token_value = serializer.validated_data['token']

        try:
            token = EmailVerificationToken.objects.get(
                token=token_value,
                is_used=False
            )

            if not token.is_valid():
                return Response(
                    {"detail": "Token has expired."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Mark token as used
            token.mark_used()

            # Update user email if it's a change verification
            if token.verification_type == 'change':
                token.user.email = token.email
                token.user.save()

            logger.info(f"Email verified: {token.user.username} -> {token.email}")

            return Response({
                'message': 'Email verified successfully.',
                'email': token.email,
                'verification_type': token.verification_type
            }, status=status.HTTP_200_OK)

        except EmailVerificationToken.DoesNotExist:
            return Response(
                {"detail": "Invalid or already used token."},
                status=status.HTTP_400_BAD_REQUEST
            )


class HubKeyPairListView(APIView):
    """List active Hub key pairs (public keys only for Nodes)"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        keys = HubKeyPair.objects.filter(is_active=True)
        serializer = HubKeyPairSerializer(keys, many=True)
        return Response(serializer.data)


class HubKeyPairCreateView(APIView):
    """Create new Hub key pair (Hub only)"""
    permission_classes = [IsAuthenticated]
    serializer_class = HubKeyPairCreateSerializer

    def post(self, request):
        # Only allow on Hub instances
        from core.instance.node_identity import get_node_identity
        identity = get_node_identity()

        if identity.get('node_type') != 'hub':
            return Response(
                {"detail": "Key pair creation is only allowed on Hub instances."},
                status=status.HTTP_403_FORBIDDEN
            )

        if not request.user.is_staff:
            return Response(
                {"detail": "Only staff members can create key pairs."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        key_pair = HubKeyPair.generate_key_pair(
            key_name=serializer.validated_data['key_name'],
            key_type=serializer.validated_data.get('key_type', 'jwt'),
            key_size=serializer.validated_data.get('key_size', 2048)
        )

        if serializer.validated_data.get('set_as_primary'):
            # Unset other primary keys
            HubKeyPair.objects.filter(is_primary=True).update(is_primary=False)
            key_pair.is_primary = True
            key_pair.save()

        return Response({
            'message': 'Key pair created successfully.',
            'key': HubKeyPairSerializer(key_pair).data
        }, status=status.HTTP_201_CREATED)


class HubPrimaryKeyView(APIView):
    """Get primary Hub public key for JWT verification"""
    permission_classes = [AllowAny]

    def get(self, request):
        key = HubKeyPair.get_primary_key()
        if not key:
            return Response(
                {"detail": "No primary key configured."},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response({
            'key_id': key.key_id,
            'public_key': key.public_key,
            'algorithm': key.algorithm,
        })


class PermissionSyncView(APIView):
    """
    Sync permissions from Hub to Node.
    Called by Hub to push permission updates to linked accounts.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = PermissionSyncSerializer

    def post(self, request):
        import logging
        logger = logging.getLogger('authentication')

        # Verify request is from Hub (check JWT issuer or use API key)
        # For now, require staff permission
        if not request.user.is_staff:
            return Response(
                {"detail": "Permission sync requires staff access."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        hub_user_uuid = serializer.validated_data['hub_user_uuid']
        permissions = serializer.validated_data.get('permissions', [])
        roles = serializer.validated_data.get('roles', [])

        try:
            link = AccountLink.objects.get(
                hub_user_uuid=hub_user_uuid,
                status='active'
            )

            # Update synced permissions
            link.synced_permissions = permissions
            link.synced_roles = roles
            link.last_permission_sync = timezone.now()
            link.save()

            logger.info(f"Permissions synced for {link.local_user.username}: {len(permissions)} permissions, {len(roles)} roles")

            return Response({
                'message': 'Permissions synced successfully.',
                'local_user': link.local_user.username,
                'permissions_count': len(permissions),
                'roles_count': len(roles)
            }, status=status.HTTP_200_OK)

        except AccountLink.DoesNotExist:
            return Response(
                {"detail": "No active account link found for this Hub user."},
                status=status.HTTP_404_NOT_FOUND
            )