"""
WebSocket consumers for Recaria module
Medieval consciousness exploration game real-time features
"""

import json
import asyncio
import random
from datetime import datetime, timedelta
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.cache import cache
from django.utils import timezone
from .models import (
    Character, Realm, ConsciousnessNode, MeditationSession,
    Creature, CreatureSpawn, CombatLog, Guild, Quest, Item
)


class GameConsumer(AsyncJsonWebsocketConsumer):
    """Main game WebSocket consumer"""
    
    async def connect(self):
        """Accept WebSocket connection"""
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            await self.close()
            return
        
        # Get or create character
        self.character = await self.get_or_create_character()
        if not self.character:
            await self.close()
            return
        
        self.character_id = str(self.character.user_id)
        self.room_group_name = f"game_{self.character_id}"
        
        # Join personal game channel
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        # Mark character as online
        await self.set_character_online(True)
        
        await self.accept()
        
        # Send initial game state
        await self.send_game_state()
        
        # Start periodic updates
        self.update_task = asyncio.create_task(self.periodic_updates())
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnect"""
        # Cancel periodic updates
        if hasattr(self, 'update_task'):
            self.update_task.cancel()
        
        # Mark character as offline
        await self.set_character_online(False)
        
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive_json(self, content):
        """Handle incoming WebSocket messages"""
        message_type = content.get('type')
        data = content.get('data', {})
        
        handlers = {
            'move': self.handle_move,
            'use_skill': self.handle_skill_use,
            'start_meditation': self.handle_start_meditation,
            'end_meditation': self.handle_end_meditation,
            'interact_node': self.handle_node_interaction,
            'chat': self.handle_chat,
            'get_inventory': self.send_inventory,
            'get_quests': self.send_quests,
            'get_skills': self.send_skills,
        }
        
        handler = handlers.get(message_type)
        if handler:
            await handler(data)
        else:
            await self.send_error(f"Unknown message type: {message_type}")
    
    async def send_game_state(self):
        """Send complete game state to client"""
        character_data = await self.get_character_data()
        realm_data = await self.get_realm_data()
        
        await self.send_json({
            'type': 'game_state',
            'data': {
                'character': character_data,
                'realm': realm_data,
                'server_time': timezone.now().isoformat()
            }
        })
    
    async def handle_move(self, data):
        """Handle character movement"""
        new_x = data.get('x')
        new_y = data.get('y')
        new_z = data.get('z', 0)
        
        if new_x is None or new_y is None:
            await self.send_error("Invalid movement coordinates")
            return
        
        # Validate movement (check obstacles, distance, etc.)
        if not await self.validate_movement(new_x, new_y, new_z):
            await self.send_error("Invalid movement")
            return
        
        # Update character position
        await self.update_character_position(new_x, new_y, new_z)
        
        # Notify nearby players
        await self.broadcast_movement(new_x, new_y, new_z)
        
        # Check for encounters
        await self.check_encounters(new_x, new_y, new_z)
    
    async def handle_skill_use(self, data):
        """Handle skill usage"""
        skill_id = data.get('skill_id')
        target_id = data.get('target_id')
        target_type = data.get('target_type', 'self')
        
        # Validate skill
        skill_result = await self.use_skill(skill_id, target_id, target_type)
        
        if skill_result['success']:
            await self.send_json({
                'type': 'skill_used',
                'data': skill_result
            })
            
            # Broadcast skill effect to nearby players
            await self.broadcast_skill_effect(skill_result)
        else:
            await self.send_error(skill_result.get('error', 'Skill failed'))
    
    async def handle_start_meditation(self, data):
        """Handle meditation start"""
        meditation_type = data.get('type', 'focus')
        node_id = data.get('node_id')
        
        # Check if already meditating
        if await self.is_meditating():
            await self.send_error("Already meditating")
            return
        
        # Start meditation session
        session = await self.start_meditation(meditation_type, node_id)
        
        if session:
            await self.send_json({
                'type': 'meditation_started',
                'data': {
                    'session_id': str(session['id']),
                    'type': meditation_type,
                    'expected_duration': 300  # 5 minutes
                }
            })
            
            # Schedule meditation rewards
            asyncio.create_task(self.meditation_timer(session['id']))
        else:
            await self.send_error("Cannot start meditation")
    
    async def handle_end_meditation(self, data):
        """Handle meditation end"""
        session_id = data.get('session_id')
        
        result = await self.end_meditation(session_id)
        
        if result:
            await self.send_json({
                'type': 'meditation_ended',
                'data': result
            })
        else:
            await self.send_error("Not meditating")
    
    async def handle_node_interaction(self, data):
        """Handle consciousness node interaction"""
        node_id = data.get('node_id')
        
        result = await self.interact_with_node(node_id)
        
        if result['success']:
            await self.send_json({
                'type': 'node_activated',
                'data': result
            })
        else:
            await self.send_error(result.get('error', 'Cannot interact with node'))
    
    async def handle_chat(self, data):
        """Handle chat messages"""
        message = data.get('message', '').strip()
        channel = data.get('channel', 'local')
        
        if not message or len(message) > 500:
            await self.send_error("Invalid message")
            return
        
        # Process chat message
        await self.broadcast_chat(message, channel)
    
    async def send_inventory(self, data=None):
        """Send character inventory"""
        inventory = await self.get_character_inventory()
        await self.send_json({
            'type': 'inventory',
            'data': inventory
        })
    
    async def send_quests(self, data=None):
        """Send character quests"""
        quests = await self.get_character_quests()
        await self.send_json({
            'type': 'quests',
            'data': quests
        })
    
    async def send_skills(self, data=None):
        """Send character skills"""
        skills = await self.get_character_skills()
        await self.send_json({
            'type': 'skills',
            'data': skills
        })
    
    async def periodic_updates(self):
        """Send periodic updates to client"""
        while True:
            try:
                await asyncio.sleep(5)  # Update every 5 seconds
                
                # Update character stats (regen, etc.)
                await self.update_character_stats()
                
                # Send nearby entities
                await self.send_nearby_entities()
                
                # Check for timed events
                await self.check_timed_events()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in periodic updates: {e}")
                await asyncio.sleep(10)
    
    async def broadcast_movement(self, x, y, z):
        """Broadcast character movement to nearby players"""
        realm_id = await self.get_character_realm()
        if realm_id:
            await self.channel_layer.group_send(
                f"realm_{realm_id}",
                {
                    'type': 'character_moved',
                    'character_id': self.character_id,
                    'character_name': self.character.name,
                    'x': x,
                    'y': y,
                    'z': z,
                    'timestamp': timezone.now().isoformat()
                }
            )
    
    async def broadcast_skill_effect(self, skill_result):
        """Broadcast skill effect to nearby players"""
        realm_id = await self.get_character_realm()
        if realm_id:
            await self.channel_layer.group_send(
                f"realm_{realm_id}",
                {
                    'type': 'skill_effect',
                    'caster_id': self.character_id,
                    'caster_name': self.character.name,
                    'skill': skill_result['skill'],
                    'target': skill_result.get('target'),
                    'effects': skill_result.get('effects', []),
                    'timestamp': timezone.now().isoformat()
                }
            )
    
    async def broadcast_chat(self, message, channel):
        """Broadcast chat message"""
        chat_data = {
            'type': 'chat_message',
            'sender_id': self.character_id,
            'sender_name': self.character.name,
            'message': message,
            'channel': channel,
            'timestamp': timezone.now().isoformat()
        }
        
        if channel == 'local':
            # Send to realm
            realm_id = await self.get_character_realm()
            if realm_id:
                await self.channel_layer.group_send(
                    f"realm_{realm_id}",
                    chat_data
                )
        elif channel == 'guild':
            # Send to guild
            guild_id = await self.get_character_guild()
            if guild_id:
                await self.channel_layer.group_send(
                    f"guild_{guild_id}",
                    chat_data
                )
        elif channel == 'global':
            # Send to all online players
            await self.channel_layer.group_send(
                "global_chat",
                chat_data
            )
    
    async def send_error(self, error_message):
        """Send error message to client"""
        await self.send_json({
            'type': 'error',
            'message': error_message,
            'timestamp': timezone.now().isoformat()
        })
    
    # Database operations
    @database_sync_to_async
    def get_or_create_character(self):
        """Get or create character for user"""
        try:
            return Character.objects.select_related('current_realm').get(user=self.user)
        except Character.DoesNotExist:
            # Create new character with default values
            default_realm = Realm.objects.filter(
                realm_type='material',
                is_accessible=True
            ).first()
            
            if not default_realm:
                return None
            
            return Character.objects.create(
                user=self.user,
                name=self.user.username,
                character_class='mystic',
                current_realm=default_realm
            )
    
    @database_sync_to_async
    def set_character_online(self, is_online):
        """Set character online status"""
        Character.objects.filter(user=self.user).update(
            is_online=is_online,
            last_played=timezone.now()
        )
    
    @database_sync_to_async
    def get_character_data(self):
        """Get character data"""
        char = Character.objects.select_related(
            'current_realm', 'guild'
        ).get(user=self.user)
        
        return {
            'name': char.name,
            'title': char.title,
            'class': char.character_class,
            'level': char.consciousness_level,
            'exp': char.consciousness_exp,
            'stats': {
                'health': char.health,
                'max_health': char.max_health,
                'mana': char.mana,
                'max_mana': char.max_mana,
                'stamina': char.stamina,
                'max_stamina': char.max_stamina,
            },
            'attributes': {
                'strength': char.strength,
                'dexterity': char.dexterity,
                'intelligence': char.intelligence,
                'wisdom': char.wisdom,
                'consciousness': char.consciousness,
            },
            'position': {
                'x': char.x_coordinate,
                'y': char.y_coordinate,
                'z': char.z_coordinate,
            },
            'guild': {
                'id': str(char.guild.id),
                'name': char.guild.name,
                'tag': char.guild.tag,
            } if char.guild else None,
            'karma': char.karma,
            'gold': char.gold,
            'soul_fragments': char.soul_fragments,
            'void_essence': char.void_essence,
        }
    
    @database_sync_to_async
    def get_realm_data(self):
        """Get current realm data"""
        char = Character.objects.select_related('current_realm').get(user=self.user)
        realm = char.current_realm
        
        if not realm:
            return None
        
        # Get nearby nodes
        nodes = ConsciousnessNode.objects.filter(
            realm=realm,
            is_active=True
        ).values('id', 'name', 'node_type', 'x_coordinate', 'y_coordinate', 'power_level')
        
        return {
            'id': str(realm.id),
            'name': realm.name,
            'type': realm.realm_type,
            'difficulty': realm.difficulty,
            'mana_density': float(realm.mana_density),
            'chaos_level': realm.chaos_level,
            'nodes': list(nodes),
        }
    
    @database_sync_to_async
    def validate_movement(self, x, y, z):
        """Validate character movement"""
        # Check movement speed, obstacles, etc.
        # Simplified for now
        return True
    
    @database_sync_to_async
    def update_character_position(self, x, y, z):
        """Update character position"""
        Character.objects.filter(user=self.user).update(
            x_coordinate=x,
            y_coordinate=y,
            z_coordinate=z
        )
    
    @database_sync_to_async
    def check_encounters(self, x, y, z):
        """Check for creature encounters"""
        char = Character.objects.get(user=self.user)
        
        # Find nearby creature spawns
        nearby_spawns = CreatureSpawn.objects.filter(
            realm=char.current_realm,
            is_active=True,
            x_coordinate__range=(x - 50, x + 50),
            y_coordinate__range=(y - 50, y + 50)
        ).select_related('creature')
        
        for spawn in nearby_spawns:
            # Random encounter chance
            if random.random() < 0.1:  # 10% chance
                # Trigger encounter
                return {
                    'encounter': True,
                    'creature': {
                        'id': spawn.creature.id,
                        'name': spawn.creature.name,
                        'level': spawn.creature.level,
                        'type': spawn.creature.creature_type,
                    }
                }
        
        return {'encounter': False}
    
    @database_sync_to_async
    def get_character_realm(self):
        """Get character's current realm ID"""
        char = Character.objects.get(user=self.user)
        return str(char.current_realm_id) if char.current_realm_id else None
    
    @database_sync_to_async
    def get_character_guild(self):
        """Get character's guild ID"""
        char = Character.objects.get(user=self.user)
        return str(char.guild_id) if char.guild_id else None
    
    @database_sync_to_async
    def is_meditating(self):
        """Check if character is meditating"""
        return Character.objects.get(user=self.user).is_meditating
    
    @database_sync_to_async
    def start_meditation(self, meditation_type, node_id=None):
        """Start meditation session"""
        char = Character.objects.get(user=self.user)
        
        if char.is_meditating:
            return None
        
        # Create meditation session
        session = MeditationSession.objects.create(
            character=char,
            realm=char.current_realm,
            node_id=node_id,
            meditation_type=meditation_type
        )
        
        # Mark character as meditating
        char.is_meditating = True
        char.save()
        
        return {
            'id': str(session.id),
            'type': meditation_type,
            'started_at': session.started_at.isoformat()
        }
    
    async def meditation_timer(self, session_id):
        """Timer for meditation rewards"""
        await asyncio.sleep(300)  # 5 minutes
        
        # Give meditation rewards
        result = await self.complete_meditation(session_id)
        if result:
            await self.send_json({
                'type': 'meditation_completed',
                'data': result
            })


class RealmConsumer(AsyncJsonWebsocketConsumer):
    """Realm-specific WebSocket consumer"""
    
    async def connect(self):
        """Accept WebSocket connection"""
        self.user = self.scope["user"]
        self.realm_id = self.scope['url_route']['kwargs']['realm_id']
        self.room_group_name = f"realm_{self.realm_id}"
        
        # Verify character is in this realm
        if not await self.verify_realm_access():
            await self.close()
            return
        
        # Join realm group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send realm state
        await self.send_realm_state()
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnect"""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive_json(self, content):
        """Handle incoming WebSocket messages"""
        # Realm-specific messages
        pass
    
    async def send_realm_state(self):
        """Send current realm state"""
        realm_data = await self.get_realm_state()
        await self.send_json({
            'type': 'realm_state',
            'data': realm_data
        })
    
    # Group message handlers
    async def character_moved(self, event):
        """Handle character movement broadcast"""
        await self.send_json({
            'type': 'character_moved',
            'character': {
                'id': event['character_id'],
                'name': event['character_name'],
                'position': {
                    'x': event['x'],
                    'y': event['y'],
                    'z': event['z']
                }
            },
            'timestamp': event['timestamp']
        })
    
    async def skill_effect(self, event):
        """Handle skill effect broadcast"""
        await self.send_json({
            'type': 'skill_effect',
            'data': event
        })
    
    async def chat_message(self, event):
        """Handle chat message broadcast"""
        await self.send_json({
            'type': 'chat_message',
            'sender': {
                'id': event['sender_id'],
                'name': event['sender_name']
            },
            'message': event['message'],
            'channel': event['channel'],
            'timestamp': event['timestamp']
        })
    
    @database_sync_to_async
    def verify_realm_access(self):
        """Verify character has access to realm"""
        try:
            char = Character.objects.get(user=self.user)
            return str(char.current_realm_id) == self.realm_id
        except Character.DoesNotExist:
            return False
    
    @database_sync_to_async
    def get_realm_state(self):
        """Get current realm state"""
        realm = Realm.objects.get(id=self.realm_id)
        
        # Get online characters in realm
        online_chars = Character.objects.filter(
            current_realm=realm,
            is_online=True
        ).values('user_id', 'name', 'consciousness_level', 'x_coordinate', 'y_coordinate')
        
        return {
            'realm': {
                'id': str(realm.id),
                'name': realm.name,
                'type': realm.realm_type,
                'special_events': realm.special_events,
            },
            'online_characters': list(online_chars),
            'active_nodes': ConsciousnessNode.objects.filter(
                realm=realm,
                is_active=True
            ).count()
        }


class CombatConsumer(AsyncJsonWebsocketConsumer):
    """Combat WebSocket consumer"""
    
    async def connect(self):
        """Accept WebSocket connection"""
        self.user = self.scope["user"]
        self.combat_id = None
        
        await self.accept()
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnect"""
        if self.combat_id:
            await self.leave_combat()
    
    async def receive_json(self, content):
        """Handle incoming WebSocket messages"""
        message_type = content.get('type')
        data = content.get('data', {})
        
        handlers = {
            'attack': self.handle_attack,
            'defend': self.handle_defend,
            'use_item': self.handle_use_item,
            'flee': self.handle_flee,
        }
        
        handler = handlers.get(message_type)
        if handler:
            await handler(data)
    
    async def handle_attack(self, data):
        """Handle attack action"""
        target_id = data.get('target_id')
        skill_id = data.get('skill_id')
        
        result = await self.perform_attack(target_id, skill_id)
        
        await self.send_json({
            'type': 'combat_action',
            'action': 'attack',
            'result': result
        })
    
    async def handle_defend(self, data):
        """Handle defend action"""
        result = await self.perform_defend()
        
        await self.send_json({
            'type': 'combat_action',
            'action': 'defend',
            'result': result
        })
    
    async def handle_use_item(self, data):
        """Handle item use in combat"""
        item_id = data.get('item_id')
        target_id = data.get('target_id')
        
        result = await self.use_combat_item(item_id, target_id)
        
        await self.send_json({
            'type': 'combat_action',
            'action': 'use_item',
            'result': result
        })
    
    async def handle_flee(self, data):
        """Handle flee attempt"""
        result = await self.attempt_flee()
        
        await self.send_json({
            'type': 'combat_action',
            'action': 'flee',
            'result': result
        })
        
        if result['success']:
            await self.leave_combat()
    
    @database_sync_to_async
    def perform_attack(self, target_id, skill_id=None):
        """Perform attack calculation"""
        # Combat calculation logic
        return {
            'success': True,
            'damage': random.randint(10, 50),
            'critical': random.random() < 0.1,
            'target_health': 80
        }
    
    @database_sync_to_async
    def perform_defend(self):
        """Perform defend action"""
        return {
            'success': True,
            'defense_bonus': 50,
            'duration': 1  # turns
        }
    
    @database_sync_to_async
    def use_combat_item(self, item_id, target_id):
        """Use item in combat"""
        return {
            'success': True,
            'effect': 'healing',
            'value': 30
        }
    
    @database_sync_to_async
    def attempt_flee(self):
        """Attempt to flee from combat"""
        flee_chance = random.random()
        return {
            'success': flee_chance > 0.5,
            'message': 'Escaped successfully!' if flee_chance > 0.5 else 'Cannot escape!'
        }
    
    async def leave_combat(self):
        """Leave combat session"""
        if self.combat_id:
            await self.channel_layer.group_discard(
                f"combat_{self.combat_id}",
                self.channel_name
            )
            self.combat_id = None


class GuildConsumer(AsyncJsonWebsocketConsumer):
    """Guild WebSocket consumer"""
    
    async def connect(self):
        """Accept WebSocket connection"""
        self.user = self.scope["user"]
        self.guild_id = self.scope['url_route']['kwargs']['guild_id']
        self.room_group_name = f"guild_{self.guild_id}"
        
        # Verify guild membership
        if not await self.verify_guild_membership():
            await self.close()
            return
        
        # Join guild group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send guild state
        await self.send_guild_state()
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnect"""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive_json(self, content):
        """Handle incoming WebSocket messages"""
        message_type = content.get('type')
        data = content.get('data', {})
        
        if message_type == 'guild_chat':
            await self.handle_guild_chat(data)
        elif message_type == 'guild_event':
            await self.handle_guild_event(data)
    
    async def send_guild_state(self):
        """Send current guild state"""
        guild_data = await self.get_guild_data()
        await self.send_json({
            'type': 'guild_state',
            'data': guild_data
        })
    
    async def handle_guild_chat(self, data):
        """Handle guild chat message"""
        message = data.get('message', '').strip()
        
        if message:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'guild_chat_message',
                    'sender_id': str(self.user.id),
                    'sender_name': self.user.username,
                    'message': message,
                    'timestamp': timezone.now().isoformat()
                }
            )
    
    async def handle_guild_event(self, data):
        """Handle guild event (promotion, kick, etc.)"""
        event_type = data.get('event_type')
        # Handle various guild events
        pass
    
    # Group message handlers
    async def guild_chat_message(self, event):
        """Handle guild chat broadcast"""
        await self.send_json({
            'type': 'guild_chat',
            'sender': {
                'id': event['sender_id'],
                'name': event['sender_name']
            },
            'message': event['message'],
            'timestamp': event['timestamp']
        })
    
    async def chat_message(self, event):
        """Handle general chat broadcast"""
        if event['channel'] == 'guild':
            await self.guild_chat_message(event)
    
    @database_sync_to_async
    def verify_guild_membership(self):
        """Verify user is guild member"""
        try:
            char = Character.objects.get(user=self.user)
            return str(char.guild_id) == self.guild_id
        except Character.DoesNotExist:
            return False
    
    @database_sync_to_async
    def get_guild_data(self):
        """Get guild data"""
        guild = Guild.objects.prefetch_related('members').get(id=self.guild_id)
        
        online_members = Character.objects.filter(
            guild=guild,
            is_online=True
        ).values('user_id', 'name', 'consciousness_level', 'guild_rank')
        
        return {
            'guild': {
                'id': str(guild.id),
                'name': guild.name,
                'tag': guild.tag,
                'level': guild.level,
                'motto': guild.motto,
                'member_count': guild.members.count(),
            },
            'online_members': list(online_members),
            'collective_consciousness': guild.collective_consciousness,
            'guild_bank_gold': guild.guild_bank_gold,
        }