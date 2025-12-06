"""
Authentication utility functions
"""

import secrets
import pyotp
import user_agents
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from typing import List, Dict, Any


def get_client_ip(request) -> str:
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_device_info(request) -> Dict[str, Any]:
    """Extract device information from user agent"""
    user_agent_string = request.META.get('HTTP_USER_AGENT', '')
    user_agent = user_agents.parse(user_agent_string)
    
    return {
        'browser': {
            'family': user_agent.browser.family,
            'version': user_agent.browser.version_string,
        },
        'os': {
            'family': user_agent.os.family,
            'version': user_agent.os.version_string,
        },
        'device': {
            'family': user_agent.device.family,
            'brand': user_agent.device.brand,
            'model': user_agent.device.model,
            'is_mobile': user_agent.is_mobile,
            'is_tablet': user_agent.is_tablet,
            'is_pc': user_agent.is_pc,
            'is_bot': user_agent.is_bot,
        }
    }


def generate_otp_secret() -> str:
    """Generate a random OTP secret"""
    return pyotp.random_base32()


def verify_otp(secret: str, code: str, window: int = 1) -> bool:
    """Verify OTP code"""
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=window)


def generate_backup_codes(count: int = 8) -> List[str]:
    """Generate backup codes for 2FA"""
    return [secrets.token_hex(4) for _ in range(count)]


def send_password_reset_email(user, token: str) -> None:
    """Send password reset email"""
    reset_url = f"{settings.FRONTEND_URL}/auth/reset-password?token={token}"
    
    context = {
        'user': user,
        'reset_url': reset_url,
        'site_name': 'UNIBOS',
    }
    
    subject = 'Password Reset Request - UNIBOS'
    html_message = render_to_string('emails/password_reset.html', context)
    plain_message = render_to_string('emails/password_reset.txt', context)
    
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False,
    )


def send_login_alert_email(user, session_info: Dict[str, Any]) -> None:
    """Send email alert for new login"""
    context = {
        'user': user,
        'ip_address': session_info.get('ip_address'),
        'location': f"{session_info.get('city', 'Unknown')}, {session_info.get('country', 'Unknown')}",
        'device': session_info.get('device_info', {}),
        'time': session_info.get('created_at'),
        'site_name': 'UNIBOS',
    }
    
    subject = 'New Login to Your UNIBOS Account'
    html_message = render_to_string('emails/login_alert.html', context)
    plain_message = render_to_string('emails/login_alert.txt', context)
    
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=True,  # Don't fail login if email fails
    )


def is_suspicious_login(user, request) -> bool:
    """Check if login attempt is suspicious"""
    # Get current request info
    current_ip = get_client_ip(request)
    current_device = get_device_info(request)
    
    # Get user's recent sessions
    from .models import UserSession
    recent_sessions = UserSession.objects.filter(
        user=user,
        is_active=True
    ).order_by('-created_at')[:5]
    
    # Check for suspicious patterns
    for session in recent_sessions:
        # Different country
        if session.country and session.country != request.META.get('HTTP_CF_IPCOUNTRY'):
            return True
        
        # Very different device
        if session.device_info:
            old_device = session.device_info
            if (old_device.get('device', {}).get('is_mobile') != current_device['device']['is_mobile'] or
                old_device.get('os', {}).get('family') != current_device['os']['family']):
                return True
    
    return False


def get_location_from_ip(ip_address: str) -> Dict[str, str]:
    """Get location information from IP address"""
    # This is a placeholder - in production, use a service like MaxMind GeoIP2
    # or Cloudflare's CF-IPCountry header
    return {
        'country': 'TR',
        'city': 'Istanbul',
    }


def send_email_verification(user, token: str, verification_type: str = 'registration') -> None:
    """
    Send email verification link to user.

    Args:
        user: User instance
        token: Verification token string
        verification_type: 'registration', 'change', or 'recovery'
    """
    verify_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"

    # Subject based on type
    subjects = {
        'registration': 'Welcome to UNIBOS - Verify Your Email',
        'change': 'UNIBOS - Confirm Your New Email',
        'recovery': 'UNIBOS - Account Recovery',
    }
    subject = subjects.get(verification_type, 'UNIBOS - Email Verification')

    context = {
        'user': user,
        'verify_url': verify_url,
        'site_name': 'UNIBOS',
        'verification_type': verification_type,
    }

    # Try to use template, fallback to simple text
    try:
        html_message = render_to_string('emails/email_verification.html', context)
        plain_message = render_to_string('emails/email_verification.txt', context)
    except Exception:
        # Fallback plain text email
        plain_message = f"""Hello {user.username},

Please verify your email address by clicking the link below:

{verify_url}

This link will expire in 24 hours.

If you didn't create an account with UNIBOS, please ignore this email.

Best regards,
UNIBOS Team
"""
        html_message = f"""
<html>
<body style="font-family: 'Courier New', monospace; background-color: #0a0a0a; color: #f0f0f0; padding: 40px;">
    <div style="max-width: 500px; margin: 0 auto; background: rgba(20, 20, 20, 0.95); border: 1px solid #ff8c00; border-radius: 8px; padding: 30px;">
        <h1 style="color: #ff8c00; text-align: center;">UNIBOS</h1>
        <p>Hello {user.username},</p>
        <p>Please verify your email address by clicking the button below:</p>
        <div style="text-align: center; margin: 30px 0;">
            <a href="{verify_url}" style="background: #ff8c00; color: #000; padding: 15px 30px; text-decoration: none; font-weight: bold; border-radius: 4px;">Verify Email</a>
        </div>
        <p style="color: #808080; font-size: 12px;">This link will expire in 24 hours.</p>
        <p style="color: #808080; font-size: 12px;">If you didn't create an account with UNIBOS, please ignore this email.</p>
        <hr style="border-color: #303030; margin: 20px 0;">
        <p style="color: #606060; font-size: 11px; text-align: center;">UNIBOS - Universal Basic Operating System</p>
    </div>
</body>
</html>
"""

    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=True,  # Don't fail registration if email fails
    )