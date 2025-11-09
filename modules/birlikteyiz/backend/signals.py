"""
Django Signals for Birlikteyiz
Automatically trigger notifications when new earthquakes are added
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
import logging

from .models import Earthquake
from .notification_service import notification_service

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Earthquake)
def earthquake_created(sender, instance, created, **kwargs):
    """
    Signal handler for new earthquake creation
    Sends notification for significant earthquakes

    Args:
        sender: The model class (Earthquake)
        instance: The actual instance being saved
        created: Boolean; True if a new record was created
        **kwargs: Additional keyword arguments
    """

    # Only process newly created earthquakes
    if not created:
        return

    # Only notify for recent earthquakes (within last hour)
    one_hour_ago = timezone.now() - timedelta(hours=1)
    if instance.occurred_at < one_hour_ago:
        logger.info(f"Skipping notification for old earthquake: {instance.occurred_at}")
        return

    # Check if notification should be sent
    if notification_service.should_notify(float(instance.magnitude)):
        earthquake_data = {
            'id': str(instance.id),
            'magnitude': float(instance.magnitude),
            'depth': float(instance.depth),
            'latitude': float(instance.latitude),
            'longitude': float(instance.longitude),
            'location': instance.location,
            'city': instance.city or '',
            'source': instance.source,
            'occurred_at': instance.occurred_at.isoformat(),
        }

        # Send notification (this will log in demo mode)
        result = notification_service.send_earthquake_alert(earthquake_data)

        logger.info(
            f"Earthquake notification triggered: "
            f"M{instance.magnitude} - {instance.location} | "
            f"Result: {result['message']}"
        )
    else:
        logger.debug(
            f"Skipped notification for minor earthquake: "
            f"M{instance.magnitude} - {instance.location}"
        )
