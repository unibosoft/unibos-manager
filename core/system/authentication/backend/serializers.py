"""
Authentication serializers for UNIBOS
"""

from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from .models import UserSession, TwoFactorAuth
from .utils import get_client_ip, get_device_info

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT token serializer with additional claims"""

    def validate(self, attrs):
        data = super().validate(attrs)

        # Add custom claims
        refresh = self.get_token(self.user)
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'is_staff': self.user.is_staff,
            'is_superuser': self.user.is_superuser,
            'roles': list(self.user.groups.values_list('name', flat=True)),
            'permissions': list(self.user.user_permissions.values_list('codename', flat=True)),
        }

        # Add offline_hash for offline authentication on nodes
        # This is the bcrypt hash that nodes can use to verify password when Hub is unreachable
        data['offline_hash'] = self.user.password  # Django stores bcrypt hash

        # Track session
        request = self.context.get('request')
        if request:
            # refresh['exp'] Unix timestamp, datetime'a cevir
            from datetime import datetime, timezone as dt_timezone
            expires_dt = datetime.fromtimestamp(refresh['exp'], tz=dt_timezone.utc)
            UserSession.objects.create(
                user=self.user,
                session_key=refresh.payload['jti'],
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                device_info=get_device_info(request),
                expires_at=expires_dt
            )

        return data
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Add custom claims
        token['email'] = user.email
        token['username'] = user.username
        token['is_staff'] = user.is_staff
        
        return token


class RegisterSerializer(serializers.ModelSerializer):
    """User registration serializer"""
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    email = serializers.EmailField(
        required=True,
        validators=[
            UniqueValidator(queryset=User.objects.all())
        ]
    )
    
    class Meta:
        model = User
        fields = (
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name'
        )
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class ChangePasswordSerializer(serializers.Serializer):
    """Change password serializer"""
    old_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError(
                {"new_password": "Password fields didn't match."}
            )
        return attrs
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                "Old password is not correct"
            )
        return value
    
    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class PasswordResetRequestSerializer(serializers.Serializer):
    """Request password reset serializer"""
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "No user is associated with this email address."
            )
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Confirm password reset serializer"""
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError(
                {"new_password": "Password fields didn't match."}
            )
        return attrs


class UserSessionSerializer(serializers.ModelSerializer):
    """User session serializer"""
    
    class Meta:
        model = UserSession
        fields = (
            'id', 'ip_address', 'user_agent', 'device_info',
            'country', 'city', 'created_at', 'last_activity',
            'is_active', 'is_suspicious'
        )
        read_only_fields = fields


class TwoFactorSetupSerializer(serializers.Serializer):
    """Two-factor authentication setup serializer"""
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                "Password is not correct"
            )
        return value


class TwoFactorVerifySerializer(serializers.Serializer):
    """Two-factor authentication verification serializer"""
    code = serializers.CharField(
        required=True,
        min_length=6,
        max_length=6
    )


class RefreshTokenSerializer(serializers.Serializer):
    """Refresh token serializer"""
    refresh = serializers.CharField(required=True)
    
    def validate(self, attrs):
        refresh = attrs['refresh']
        
        try:
            RefreshToken(refresh)
        except Exception:
            raise serializers.ValidationError(
                "Invalid refresh token"
            )
        
        return attrs