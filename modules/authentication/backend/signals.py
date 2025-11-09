"""
Authentication signals for UNIBOS
"""

from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
from django.utils import timezone
import logging

logger = logging.getLogger('authentication')


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Log successful user login"""
    logger.info(f"User {user.username} logged in from {request.META.get('REMOTE_ADDR', 'unknown')}")
    # Update last login and increment login count
    user.last_login = timezone.now()
    if hasattr(user, 'login_count'):
        user.login_count += 1
        user.save(update_fields=['last_login', 'login_count'])
    else:
        user.save(update_fields=['last_login'])


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """Log user logout"""
    if user:
        logger.info(f"User {user.username} logged out")


@receiver(user_login_failed)
def log_login_failed(sender, credentials, request, **kwargs):
    """Log failed login attempts"""
    username = credentials.get('username', 'unknown')
    logger.warning(f"Failed login attempt for username {username} from {request.META.get('REMOTE_ADDR', 'unknown')}")