"""
UNIBOS Web UI WebSocket Consumers
Real-time updates for the terminal-style web interface
"""

import json
import asyncio
from datetime import datetime
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone


class StatusConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time status updates"""
    
    async def connect(self):
        """Accept WebSocket connection"""
        self.room_name = 'status'
        self.room_group_name = f'unibos_{self.room_name}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Start sending periodic updates
        asyncio.create_task(self.send_periodic_updates())
        
        # Send initial status
        await self.send_status_update()
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': datetime.now().isoformat()
                }))
            elif message_type == 'get_status':
                await self.send_status_update()
            elif message_type == 'get_module_status':
                module_id = data.get('module_id')
                await self.send_module_status(module_id)
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))
    
    async def send_periodic_updates(self):
        """Send periodic status updates every second"""
        while True:
            try:
                await asyncio.sleep(1)
                await self.send_time_update()
            except Exception:
                break
    
    async def send_time_update(self):
        """Send current time update"""
        now = datetime.now()
        await self.send(text_data=json.dumps({
            'type': 'time_update',
            'time': now.strftime('%H:%M:%S'),
            'date': now.strftime('%Y-%m-%d'),
            'timestamp': now.isoformat()
        }))
    
    async def send_status_update(self):
        """Send full system status update"""
        status = await self.get_system_status()
        await self.send(text_data=json.dumps({
            'type': 'status_update',
            'status': status
        }))
    
    async def send_module_status(self, module_id):
        """Send specific module status"""
        module_status = await self.get_module_status(module_id)
        await self.send(text_data=json.dumps({
            'type': 'module_status',
            'module_id': module_id,
            'status': module_status
        }))
    
    @database_sync_to_async
    def get_system_status(self):
        """Get current system status from database"""
        # Check online status
        online = self.check_online_status()
        
        # Get module statuses
        modules = {
            'recaria': {
                'status': 'active',
                'health': 'good',
                'users': 0,
                'last_update': datetime.now().isoformat()
            },
            'birlikteyiz': {
                'status': 'active',
                'health': 'good',
                'alerts': 0,
                'last_update': datetime.now().isoformat()
            },
            'kisisel_enflasyon': {
                'status': 'active',
                'health': 'good',
                'items': 0,
                'last_update': datetime.now().isoformat()
            },
            'currencies': {
                'status': 'active',
                'health': 'good',
                'pairs': 0,
                'last_update': datetime.now().isoformat()
            }
        }
        
        return {
            'online': online,
            'modules': modules,
            'timestamp': datetime.now().isoformat()
        }
    
    @database_sync_to_async
    def get_module_status(self, module_id):
        """Get specific module status"""
        # This would fetch real data from the database
        # For now, return mock data
        statuses = {
            'recaria': {
                'active_users': 0,
                'guilds': 0,
                'quests': 0,
                'trades': 0
            },
            'birlikteyiz': {
                'active_alerts': 0,
                'helpers_online': 0,
                'resolved_today': 0
            },
            'kisisel_enflasyon': {
                'tracked_items': 0,
                'categories': 0,
                'inflation_rate': '0%',
                'last_calculation': 'Never'
            },
            'currencies': {
                'usd_try': 32.45,
                'eur_try': 35.12,
                'gbp_try': 41.23,
                'last_update': datetime.now().isoformat()
            }
        }
        
        return statuses.get(module_id, {})
    
    def check_online_status(self):
        """Check if system is online"""
        try:
            import socket
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except:
            return False
    
    # Handle room group messages
    async def status_message(self, event):
        """Handle status messages from room group"""
        message = event['message']
        await self.send(text_data=json.dumps(message))


class ModuleConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for module-specific updates"""
    
    async def connect(self):
        """Accept WebSocket connection for module updates"""
        self.module_id = self.scope['url_route']['kwargs']['module_id']
        self.room_group_name = f'module_{self.module_id}'
        
        # Join module-specific room
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send initial module data
        await self.send_module_data()
    
    async def disconnect(self, close_code):
        """Handle disconnection"""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Handle incoming messages"""
        try:
            data = json.loads(text_data)
            action = data.get('action')
            
            if action == 'refresh':
                await self.send_module_data()
            elif action == 'execute':
                command = data.get('command')
                await self.execute_module_command(command)
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))
    
    async def send_module_data(self):
        """Send module-specific data"""
        data = await self.get_module_data()
        await self.send(text_data=json.dumps({
            'type': 'module_data',
            'module_id': self.module_id,
            'data': data
        }))
    
    @database_sync_to_async
    def get_module_data(self):
        """Get module data from database"""
        # Fetch real module data based on module_id
        # This is mock data for demonstration
        if self.module_id == 'recaria':
            return {
                'characters': [],
                'guilds': [],
                'active_quests': [],
                'online_players': 0
            }
        elif self.module_id == 'birlikteyiz':
            return {
                'alerts': [],
                'helpers': [],
                'requests': []
            }
        elif self.module_id == 'kisisel_enflasyon':
            return {
                'products': [],
                'categories': [],
                'inflation_data': []
            }
        elif self.module_id == 'currencies':
            return {
                'rates': {
                    'USD/TRY': 32.45,
                    'EUR/TRY': 35.12,
                    'GBP/TRY': 41.23
                },
                'last_update': datetime.now().isoformat()
            }
        
        return {}
    
    async def execute_module_command(self, command):
        """Execute module-specific command"""
        result = await self.process_command(command)
        await self.send(text_data=json.dumps({
            'type': 'command_result',
            'command': command,
            'result': result
        }))
    
    @database_sync_to_async
    def process_command(self, command):
        """Process module command"""
        # Process commands based on module
        return {
            'success': True,
            'message': f'Command "{command}" executed successfully'
        }
    
    # Handle room group messages
    async def module_update(self, event):
        """Handle module update messages"""
        await self.send(text_data=json.dumps(event['data']))