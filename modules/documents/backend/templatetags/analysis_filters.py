"""
Custom template filters for OCR analysis
"""

from django import template
from django.utils import timezone
from datetime import datetime, timedelta
from dateutil import parser

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """
    Get item from dictionary using key

    Usage in template:
        {{ analysis|get_item:method.id }}
        {{ method_data|get_item:'status' }}

    Args:
        dictionary: The dictionary to access
        key: The key to look up

    Returns:
        Value from dictionary or empty dict if not found
    """
    if dictionary is None:
        return {}
    return dictionary.get(key, {})


@register.filter
def timeago(timestamp_str):
    """
    Convert ISO timestamp string to relative time format

    Examples:
        "2025-11-09T10:30:00" -> "5 minutes ago"
        "2025-11-08T10:30:00" -> "1 day ago"

    Args:
        timestamp_str: ISO format timestamp string

    Returns:
        Relative time string (e.g., "5 minutes ago", "1 day ago")
    """
    if not timestamp_str:
        return "never"

    try:
        # Parse ISO format timestamp
        if isinstance(timestamp_str, str):
            timestamp = parser.isoparse(timestamp_str)
        else:
            timestamp = timestamp_str

        # Make timezone-aware if needed
        if timezone.is_naive(timestamp):
            timestamp = timezone.make_aware(timestamp)

        now = timezone.now()
        diff = now - timestamp

        seconds = diff.total_seconds()

        if seconds < 60:
            return "just now"
        elif seconds < 3600:  # Less than 1 hour
            minutes = int(seconds / 60)
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        elif seconds < 86400:  # Less than 1 day
            hours = int(seconds / 3600)
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif seconds < 604800:  # Less than 1 week
            days = int(seconds / 86400)
            return f"{days} day{'s' if days != 1 else ''} ago"
        elif seconds < 2592000:  # Less than 30 days
            weeks = int(seconds / 604800)
            return f"{weeks} week{'s' if weeks != 1 else ''} ago"
        else:
            months = int(seconds / 2592000)
            return f"{months} month{'s' if months != 1 else ''} ago"
    except Exception as e:
        return "unknown"
