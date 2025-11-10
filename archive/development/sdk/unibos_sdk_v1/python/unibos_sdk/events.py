"""
UNIBOS Event System

Event-driven communication between modules using Django signals.
"""

from typing import Dict, Any, Callable
from django.dispatch import Signal, receiver
import logging

logger = logging.getLogger(__name__)


# System-wide event signals
earthquake_detected = Signal()  # providing_args=['earthquake', 'magnitude', 'location']
user_location_changed = Signal()  # providing_args=['user', 'old_location', 'new_location']
payment_completed = Signal()  # providing_args=['user', 'amount', 'currency', 'transaction_id']
document_uploaded = Signal()  # providing_args=['user', 'document', 'file_type']
currency_rate_updated = Signal()  # providing_args=['currency_pair', 'old_rate', 'new_rate']
user_registered = Signal()  # providing_args=['user']
module_enabled = Signal()  # providing_args=['module_id']
module_disabled = Signal()  # providing_args=['module_id']


class UnibosEvents:
    """
    Event system for inter-module communication

    Modules can emit events and listen to events from other modules
    without direct coupling.
    """

    @staticmethod
    def emit(signal: Signal, sender: Any = None, **kwargs):
        """
        Emit an event to all listeners

        Args:
            signal: Signal to emit
            sender: Sender object (usually module instance or class)
            **kwargs: Event data

        Example:
            UnibosEvents.emit(
                earthquake_detected,
                sender=self.__class__,
                earthquake=eq_object,
                magnitude=6.5,
                location={'lat': 38.0, 'lon': 28.0}
            )
        """
        try:
            signal.send(sender=sender, **kwargs)
            logger.debug(f"Event emitted: {signal} from {sender}")
        except Exception as e:
            logger.error(f"Error emitting event {signal}: {e}")

    @staticmethod
    def listen(signal: Signal, handler: Callable):
        """
        Register event listener

        Args:
            signal: Signal to listen to
            handler: Handler function

        Example:
            def handle_earthquake(sender, earthquake, magnitude, **kwargs):
                print(f"Earthquake detected: M{magnitude}")

            UnibosEvents.listen(earthquake_detected, handle_earthquake)
        """
        try:
            signal.connect(handler)
            logger.debug(f"Listener registered for {signal}: {handler.__name__}")
        except Exception as e:
            logger.error(f"Error registering listener for {signal}: {e}")

    @staticmethod
    def unlisten(signal: Signal, handler: Callable):
        """
        Unregister event listener

        Args:
            signal: Signal to stop listening to
            handler: Handler function to remove
        """
        try:
            signal.disconnect(handler)
            logger.debug(f"Listener unregistered for {signal}: {handler.__name__}")
        except Exception as e:
            logger.error(f"Error unregistering listener for {signal}: {e}")

    @staticmethod
    def emit_earthquake_detected(sender, earthquake, magnitude: float, location: Dict):
        """
        Convenience method to emit earthquake_detected event

        Args:
            sender: Sender (birlikteyiz module)
            earthquake: Earthquake model instance
            magnitude: Earthquake magnitude
            location: Location dict with lat/lon
        """
        UnibosEvents.emit(
            earthquake_detected,
            sender=sender,
            earthquake=earthquake,
            magnitude=magnitude,
            location=location
        )

    @staticmethod
    def emit_user_location_changed(sender, user, old_location: Dict, new_location: Dict):
        """
        Convenience method to emit user_location_changed event

        Args:
            sender: Sender module
            user: User instance
            old_location: Previous location dict
            new_location: New location dict
        """
        UnibosEvents.emit(
            user_location_changed,
            sender=sender,
            user=user,
            old_location=old_location,
            new_location=new_location
        )

    @staticmethod
    def emit_payment_completed(sender, user, amount: float, currency: str, transaction_id: str):
        """
        Convenience method to emit payment_completed event

        Args:
            sender: Sender module
            user: User instance
            amount: Payment amount
            currency: Currency code
            transaction_id: Transaction ID
        """
        UnibosEvents.emit(
            payment_completed,
            sender=sender,
            user=user,
            amount=amount,
            currency=currency,
            transaction_id=transaction_id
        )

    @staticmethod
    def emit_document_uploaded(sender, user, document, file_type: str):
        """
        Convenience method to emit document_uploaded event

        Args:
            sender: Sender module
            user: User instance
            document: Document model instance
            file_type: File type (pdf, image, etc.)
        """
        UnibosEvents.emit(
            document_uploaded,
            sender=sender,
            user=user,
            document=document,
            file_type=file_type
        )

    @staticmethod
    def emit_currency_rate_updated(sender, currency_pair: str, old_rate: float, new_rate: float):
        """
        Convenience method to emit currency_rate_updated event

        Args:
            sender: Sender module (currencies)
            currency_pair: Currency pair (e.g., 'USD/TRY')
            old_rate: Previous rate
            new_rate: New rate
        """
        UnibosEvents.emit(
            currency_rate_updated,
            sender=sender,
            currency_pair=currency_pair,
            old_rate=old_rate,
            new_rate=new_rate
        )


# Decorator for event handlers
def event_handler(signal: Signal):
    """
    Decorator to mark function as event handler

    Usage:
        @event_handler(earthquake_detected)
        def handle_earthquake(sender, earthquake, magnitude, **kwargs):
            print(f"Earthquake: M{magnitude}")
    """
    def decorator(func):
        signal.connect(func)
        return func
    return decorator
