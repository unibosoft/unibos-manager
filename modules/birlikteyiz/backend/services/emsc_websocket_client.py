"""
EMSC (European-Mediterranean Seismological Centre) WebSocket Client
Real-time earthquake data stream from SeismicPortal
"""

import asyncio
import websockets
import json
import logging
from datetime import datetime
from django.utils import timezone
from django.db import transaction
from decimal import Decimal
from asgiref.sync import sync_to_async

logger = logging.getLogger(__name__)


class EMSCWebSocketClient:
    """
    WebSocket client for real-time earthquake data from EMSC SeismicPortal
    Endpoint: wss://www.seismicportal.eu/standing_order/websocket
    """

    WEBSOCKET_URI = 'wss://www.seismicportal.eu/standing_order/websocket'
    PING_INTERVAL = 15  # seconds
    RECONNECT_DELAY = 5  # seconds

    def __init__(self):
        self.websocket = None
        self.is_running = False
        self.data_source = None

    async def ensure_data_source(self):
        """Ensure EMSC data source exists in database"""
        from modules.birlikteyiz.backend.models import EarthquakeDataSource

        @sync_to_async
        def get_or_create_source():
            source, created = EarthquakeDataSource.objects.get_or_create(
                name='EMSC',
                defaults={
                    'url': self.WEBSOCKET_URI,
                    'description': 'European-Mediterranean Seismological Centre - Real-time WebSocket feed',
                    'is_active': True,
                    'fetch_interval_minutes': 0,  # Real-time, no interval
                    'min_magnitude': 0.0,  # Get all magnitudes
                    'max_results': 0,  # Unlimited
                    'use_geographic_filter': False,
                    'filter_region_name': 'Global'
                }
            )
            if created:
                logger.info(f"Created EMSC data source: {source.name}")
            return source

        self.data_source = await get_or_create_source()

    async def process_earthquake_message(self, message_data):
        """
        Process incoming earthquake message and save to database

        Expected format:
        {
            "action": "create" | "update" | "delete",
            "data": {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [longitude, latitude, depth]
                },
                "properties": {
                    "unid": "unique_id",
                    "time": "2024-11-03T12:34:56.000Z",
                    "mag": 4.5,
                    "magtype": "ml",
                    "auth": "EMSC",
                    "flynn_region": "Region Name",
                    "depth": 10.0,
                    ...
                }
            }
        }
        """
        from modules.birlikteyiz.backend.models import Earthquake

        try:
            action = message_data.get('action')
            data = message_data.get('data', {})

            # Only process create and update actions
            if action not in ['create', 'update']:
                return

            properties = data.get('properties', {})
            geometry = data.get('geometry', {})
            coordinates = geometry.get('coordinates', [])

            if len(coordinates) < 3:
                logger.warning(f"Invalid coordinates in EMSC message: {coordinates}")
                return

            # Extract earthquake data
            longitude = Decimal(str(coordinates[0]))
            latitude = Decimal(str(coordinates[1]))
            depth = Decimal(str(coordinates[2]))
            magnitude = Decimal(str(properties.get('mag', 0)))
            unid = properties.get('unid', '')
            time_str = properties.get('time', '')
            auth = properties.get('auth', 'EMSC')
            flynn_region = properties.get('flynn_region', 'Unknown Region')

            # Parse time
            try:
                occurred_at = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                occurred_at = timezone.make_aware(occurred_at) if timezone.is_naive(occurred_at) else occurred_at
            except Exception as e:
                logger.error(f"Failed to parse time '{time_str}': {e}")
                occurred_at = timezone.now()

            # Create unique ID
            unique_id = f"EMSC_{unid}" if unid else f"EMSC_{time_str}_{latitude}_{longitude}"

            # Save to database
            @sync_to_async
            @transaction.atomic
            def save_earthquake():
                earthquake, created = Earthquake.objects.update_or_create(
                    unique_id=unique_id,
                    defaults={
                        'source': 'EMSC',
                        'source_id': unid,
                        'magnitude': magnitude,
                        'depth': depth,
                        'latitude': latitude,
                        'longitude': longitude,
                        'location': flynn_region,
                        'occurred_at': occurred_at,
                        'fetched_at': timezone.now(),
                        'raw_data': message_data
                    }
                )

                # Update data source statistics
                if created:
                    self.data_source.success_count += 1
                    self.data_source.total_earthquakes_fetched += 1
                    self.data_source.last_success = timezone.now()
                    self.data_source.save(update_fields=['success_count', 'total_earthquakes_fetched', 'last_success'])

                    logger.info(f"{'Created' if created else 'Updated'} EMSC earthquake: M{magnitude} - {flynn_region}")

                return earthquake, created

            await save_earthquake()

        except Exception as e:
            logger.error(f"Error processing EMSC earthquake message: {e}", exc_info=True)

            # Update error statistics
            @sync_to_async
            def update_error_stats():
                self.data_source.error_count += 1
                self.data_source.last_error = str(e)
                self.data_source.last_error_time = timezone.now()
                self.data_source.save(update_fields=['error_count', 'last_error', 'last_error_time'])

            await update_error_stats()

    async def listen(self):
        """Listen to WebSocket messages"""
        try:
            async for message in self.websocket:
                try:
                    message_data = json.loads(message)
                    logger.debug(f"Received EMSC message: {message_data.get('action', 'unknown')}")

                    # Update last fetch time
                    @sync_to_async
                    def update_fetch_time():
                        self.data_source.last_fetch = timezone.now()
                        self.data_source.fetch_count += 1
                        self.data_source.save(update_fields=['last_fetch', 'fetch_count'])

                    await update_fetch_time()

                    # Process earthquake data
                    await self.process_earthquake_message(message_data)

                except json.JSONDecodeError as e:
                    logger.error(f"Failed to decode EMSC message: {e}")
                except Exception as e:
                    logger.error(f"Error processing EMSC message: {e}", exc_info=True)

        except websockets.exceptions.ConnectionClosed:
            logger.warning("EMSC WebSocket connection closed")
        except Exception as e:
            logger.error(f"Error in EMSC listen loop: {e}", exc_info=True)

    async def keep_alive(self):
        """Send ping messages to keep connection alive"""
        while self.is_running and self.websocket:
            try:
                await asyncio.sleep(self.PING_INTERVAL)
                if self.websocket and not self.websocket.closed:
                    await self.websocket.ping()
                    logger.debug("Sent ping to EMSC WebSocket")
            except Exception as e:
                logger.error(f"Error sending ping: {e}")
                break

    async def connect(self):
        """Connect to EMSC WebSocket and start listening"""
        await self.ensure_data_source()

        while self.is_running:
            try:
                logger.info(f"Connecting to EMSC WebSocket: {self.WEBSOCKET_URI}")

                async with websockets.connect(
                    self.WEBSOCKET_URI,
                    ping_interval=None,  # We handle pings manually
                    close_timeout=10
                ) as websocket:
                    self.websocket = websocket
                    logger.info("Connected to EMSC WebSocket successfully")

                    # Update data source status
                    @sync_to_async
                    def mark_active():
                        self.data_source.is_active = True
                        self.data_source.save(update_fields=['is_active'])

                    await mark_active()

                    # Start keep-alive task
                    keep_alive_task = asyncio.create_task(self.keep_alive())

                    # Listen for messages
                    try:
                        await self.listen()
                    finally:
                        keep_alive_task.cancel()

            except websockets.exceptions.WebSocketException as e:
                logger.error(f"WebSocket error: {e}")
            except Exception as e:
                logger.error(f"Connection error: {e}", exc_info=True)

            if self.is_running:
                logger.info(f"Reconnecting to EMSC WebSocket in {self.RECONNECT_DELAY} seconds...")
                await asyncio.sleep(self.RECONNECT_DELAY)

    async def start(self):
        """Start the WebSocket client"""
        self.is_running = True
        await self.connect()

    async def stop(self):
        """Stop the WebSocket client"""
        self.is_running = False
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
        logger.info("EMSC WebSocket client stopped")


# Singleton instance
_emsc_client = None


def get_emsc_client():
    """Get or create EMSC WebSocket client instance"""
    global _emsc_client
    if _emsc_client is None:
        _emsc_client = EMSCWebSocketClient()
    return _emsc_client


async def start_emsc_listener():
    """Start EMSC WebSocket listener"""
    client = get_emsc_client()
    await client.start()


async def stop_emsc_listener():
    """Stop EMSC WebSocket listener"""
    client = get_emsc_client()
    await client.stop()
