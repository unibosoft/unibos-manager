"""
WebSocket consumers for real-time OCR analysis updates
"""
import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)


class OCRAnalysisConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time OCR analysis updates

    Frontend connects to: ws://localhost:8000/ws/ocr/analysis/<document_id>/

    Messages sent to frontend:
    - log: {"type": "log", "message": "...", "level": "info"}
    - status: {"type": "status", "method": "paddleocr", "status": "running"}
    - result: {"type": "result", "method": "paddleocr", "data": {...}}
    - complete: {"type": "complete", "message": "All methods completed"}
    """

    async def connect(self):
        """Accept WebSocket connection and join document-specific group"""
        self.document_id = self.scope['url_route']['kwargs']['document_id']
        self.room_group_name = f'ocr_analysis_{self.document_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        logger.info(f"WebSocket connected for document {self.document_id}")

    async def disconnect(self, close_code):
        """Leave document group on disconnect"""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info(f"WebSocket disconnected for document {self.document_id} (code: {close_code})")

    async def receive(self, text_data):
        """Handle messages from WebSocket (not used in this implementation)"""
        pass

    # Handlers for different message types from backend

    async def analysis_log(self, event):
        """Send log message to WebSocket"""
        logger.info(f"📤 Consumer sending log to frontend: {event.get('message')}")
        await self.send(text_data=json.dumps({
            'type': 'log',
            'message': event['message'],
            'level': event.get('level', 'info'),
            'timestamp': event.get('timestamp')
        }))

    async def analysis_status(self, event):
        """Send status update to WebSocket"""
        logger.info(f"📤 Consumer sending status to frontend: {event.get('method')} - {event.get('status')}")
        await self.send(text_data=json.dumps({
            'type': 'status',
            'method': event['method'],
            'status': event['status']
        }))

    async def analysis_result(self, event):
        """Send analysis result to WebSocket"""
        logger.info(f"📤 Consumer sending result to frontend: {event.get('method')}")
        await self.send(text_data=json.dumps({
            'type': 'result',
            'method': event['method'],
            'data': event['data']
        }))

    async def analysis_complete(self, event):
        """Send completion message to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'complete',
            'message': event.get('message', 'Analysis completed')
        }))
