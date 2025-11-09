"""
Push Notification Service for Birlikteyiz
Sends earthquake alerts via Firebase Cloud Messaging (FCM)
"""

import logging
from typing import List, Optional
from decimal import Decimal

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Service for sending push notifications about earthquakes

    Note: This is a lightweight implementation that works without Firebase Admin SDK.
    For production, install firebase-admin and uncomment the FCM code.
    """

    def __init__(self):
        self.enabled = False
        try:
            # Try to import firebase_admin
            # Uncomment when firebase-admin is installed:
            # import firebase_admin
            # from firebase_admin import messaging, credentials
            # self.enabled = True
            logger.info("NotificationService initialized (demo mode - no FCM)")
        except ImportError:
            logger.warning("firebase-admin not installed. Notifications disabled.")

    def send_earthquake_alert(
        self,
        earthquake_data: dict,
        device_tokens: Optional[List[str]] = None
    ) -> dict:
        """
        Send earthquake alert to registered devices

        Args:
            earthquake_data: Dictionary with earthquake details
            device_tokens: List of FCM device tokens (optional for testing)

        Returns:
            dict with success status and message count
        """

        magnitude = earthquake_data.get('magnitude', 0)
        location = earthquake_data.get('location', 'Bilinmeyen')
        depth = earthquake_data.get('depth', 0)

        # Create notification based on magnitude
        if magnitude >= 5.0:
            title = f"🚨 büyük deprem! {magnitude}"
            priority = 'high'
            color = '#ff0000'  # Red
        elif magnitude >= 4.0:
            title = f"⚠️ orta şiddetli deprem {magnitude}"
            priority = 'high'
            color = '#ff6600'  # Orange
        elif magnitude >= 3.0:
            title = f"📊 deprem {magnitude}"
            priority = 'normal'
            color = '#ffcc00'  # Yellow
        else:
            title = f"ℹ️ küçük deprem {magnitude}"
            priority = 'low'
            color = '#00ff00'  # Green

        body = f"{location}\nderinlik: {depth} km"

        # Log the notification (for testing without FCM)
        logger.info(f"Earthquake Alert: {title} - {body}")

        if not self.enabled:
            return {
                'success': True,
                'sent': 0,
                'failed': 0,
                'message': 'Demo mode - notification logged but not sent'
            }

        # Production FCM implementation (uncomment when firebase-admin is installed):
        """
        try:
            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data={
                    'type': 'earthquake',
                    'magnitude': str(magnitude),
                    'location': location,
                    'depth': str(depth),
                    'latitude': str(earthquake_data.get('latitude', 0)),
                    'longitude': str(earthquake_data.get('longitude', 0)),
                    'occurred_at': earthquake_data.get('occurred_at', ''),
                    'source': earthquake_data.get('source', ''),
                },
                android=messaging.AndroidConfig(
                    priority=priority,
                    notification=messaging.AndroidNotification(
                        color=color,
                        sound='default',
                        channel_id='earthquake_alerts'
                    )
                ),
                apns=messaging.APNSConfig(
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(
                            alert=messaging.ApsAlert(
                                title=title,
                                body=body
                            ),
                            sound='default',
                            badge=1
                        )
                    )
                ),
                tokens=device_tokens or []
            )

            response = messaging.send_multicast(message)

            return {
                'success': True,
                'sent': response.success_count,
                'failed': response.failure_count,
                'message': f'Sent {response.success_count} notifications'
            }

        except Exception as e:
            logger.error(f"Failed to send notification: {str(e)}")
            return {
                'success': False,
                'sent': 0,
                'failed': len(device_tokens or []),
                'error': str(e)
            }
        """

        return {
            'success': True,
            'sent': 0,
            'failed': 0,
            'message': 'Firebase Admin SDK not configured'
        }

    def should_notify(self, magnitude: float, min_magnitude: float = 3.0) -> bool:
        """
        Determine if notification should be sent based on magnitude

        Args:
            magnitude: Earthquake magnitude
            min_magnitude: Minimum magnitude to trigger notification (default: 3.0)

        Returns:
            bool: True if notification should be sent
        """
        return magnitude >= min_magnitude


# Global notification service instance
notification_service = NotificationService()
