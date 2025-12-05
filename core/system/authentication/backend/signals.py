"""
Authentication signals for UNIBOS

Handles authentication events and sends WebSocket notifications.
"""

from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import logging

logger = logging.getLogger('authentication')


def _send_ws_notification(user_id, notification_type, data):
    """Send WebSocket notification (non-blocking)"""
    try:
        from .consumers import send_auth_notification_sync
        send_auth_notification_sync(user_id, notification_type, data)
    except Exception as e:
        logger.debug(f"WebSocket notification failed (non-critical): {e}")


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Log successful user login and send WebSocket notification"""
    ip_address = request.META.get('REMOTE_ADDR', 'unknown')
    user_agent = request.META.get('HTTP_USER_AGENT', '')

    logger.info(f"User {user.username} logged in from {ip_address}")

    # Update last login and increment login count
    user.last_login = timezone.now()
    if hasattr(user, 'login_count'):
        user.login_count += 1
        user.save(update_fields=['last_login', 'login_count'])
    else:
        user.save(update_fields=['last_login'])

    # Send WebSocket notification for new session
    _send_ws_notification(user.id, 'auth_session_created', {
        'ip_address': ip_address,
        'device_info': {'user_agent': user_agent},
        'timestamp': timezone.now().isoformat(),
    })


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """Log user logout and send WebSocket notification"""
    if user:
        logger.info(f"User {user.username} logged out")

        # Send WebSocket notification
        _send_ws_notification(user.id, 'auth_session_revoked', {
            'reason': 'logout',
            'timestamp': timezone.now().isoformat(),
        })


@receiver(user_login_failed)
def log_login_failed(sender, credentials, request, **kwargs):
    """Log failed login attempts and send security alert"""
    username = credentials.get('username', 'unknown')
    ip_address = request.META.get('REMOTE_ADDR', 'unknown')

    logger.warning(f"Failed login attempt for username {username} from {ip_address}")

    # Try to find user and send security alert
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.filter(username=username).first()

        if user:
            _send_ws_notification(user.id, 'auth_security_alert', {
                'alert_type': 'failed_login',
                'message': f'Failed login attempt from {ip_address}',
                'severity': 'warning',
                'timestamp': timezone.now().isoformat(),
            })
    except Exception:
        pass


# ========== Model Signals for Identity Enhancement ==========

@receiver(post_save, sender='authentication.AccountLink')
def account_link_changed(sender, instance, created, **kwargs):
    """Send notification when account link status changes"""
    if not created:  # Only for updates, not creation
        _send_ws_notification(instance.local_user_id, 'auth_link_status_changed', {
            'link_id': str(instance.id),
            'status': instance.status,
            'hub_username': instance.hub_username,
            'timestamp': timezone.now().isoformat(),
        })