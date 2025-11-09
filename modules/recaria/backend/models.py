"""
Recaria models for UNIBOS
Medieval-themed consciousness exploration game inspired by Ultima Online
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField, JSONField
from django.contrib.postgres.indexes import GinIndex
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import uuid
import random
import math

User = get_user_model()


class Realm(models.Model):
    """Mystical realms representing different consciousness layers"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    
    # Realm properties
    realm_type = models.CharField(
        max_length=30,
        choices=[
            ('material', 'Material Plane'),
            ('ethereal', 'Ethereal Plane'),
            ('astral', 'Astral Plane'),
            ('shadow', 'Shadow Realm'),
            ('dream', 'Dream Realm'),
            ('void', 'The Void'),
        ]
    )
    difficulty = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    
    # Environmental properties
    mana_density = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(0.1), MaxValueValidator(10.0)]
    )
    chaos_level = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Access requirements
    min_consciousness_level = models.IntegerField(default=1)
    required_artifacts = ArrayField(
        models.CharField(max_length=50),
        default=list,
        blank=True
    )
    
    # Realm status
    is_accessible = models.BooleanField(default=True)
    special_events = models.JSONField(default=dict)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    lore_text = models.TextField(blank=True)
    
    class Meta:
        db_table = 'recaria_realms'
        ordering = ['difficulty', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_realm_type_display()})"


class Character(models.Model):
    """Player character in the medieval consciousness exploration"""
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        primary_key=True,
        related_name='recaria_character'
    )
    
    # Character identity
    name = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=100, blank=True)
    
    # Character class and stats
    character_class = models.CharField(
        max_length=20,
        choices=[
            ('mystic', 'Mystic'),
            ('sage', 'Sage'),
            ('dreamwalker', 'Dreamwalker'),
            ('voidseeker', 'Voidseeker'),
            ('mindbender', 'Mindbender'),
            ('soulweaver', 'Soulweaver'),
        ]
    )
    
    # Core attributes
    strength = models.IntegerField(default=10)
    dexterity = models.IntegerField(default=10)
    intelligence = models.IntegerField(default=10)
    wisdom = models.IntegerField(default=10)
    consciousness = models.IntegerField(default=10)
    
    # Derived stats
    health = models.IntegerField(default=100)
    max_health = models.IntegerField(default=100)
    mana = models.IntegerField(default=50)
    max_mana = models.IntegerField(default=50)
    stamina = models.IntegerField(default=100)
    max_stamina = models.IntegerField(default=100)
    
    # Consciousness exploration stats
    consciousness_level = models.IntegerField(default=1)
    consciousness_exp = models.BigIntegerField(default=0)
    enlightenment_points = models.IntegerField(default=0)
    karma = models.IntegerField(default=0)  # -1000 to 1000
    
    # Currency and resources
    gold = models.BigIntegerField(default=100)
    soul_fragments = models.IntegerField(default=0)
    void_essence = models.IntegerField(default=0)
    
    # Location
    current_realm = models.ForeignKey(
        Realm,
        on_delete=models.SET_NULL,
        null=True,
        related_name='present_characters'
    )
    x_coordinate = models.IntegerField(default=0)
    y_coordinate = models.IntegerField(default=0)
    z_coordinate = models.IntegerField(default=0)  # For multi-dimensional realms
    
    # Skills (stored as JSON for flexibility)
    skills = models.JSONField(default=dict)
    # {"meditation": 75, "astral_projection": 50, "telepathy": 30, etc.}
    
    # Status flags
    is_meditating = models.BooleanField(default=False)
    is_in_combat = models.BooleanField(default=False)
    is_dead = models.BooleanField(default=False)
    is_online = models.BooleanField(default=False)
    
    # Death and respawn
    death_count = models.IntegerField(default=0)
    last_death = models.DateTimeField(null=True, blank=True)
    respawn_realm = models.ForeignKey(
        Realm,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='respawn_point_for'
    )
    
    # Guild membership
    guild = models.ForeignKey(
        'Guild',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='members'
    )
    guild_rank = models.CharField(max_length=50, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    last_played = models.DateTimeField(auto_now=True)
    total_playtime = models.BigIntegerField(default=0)  # In seconds
    
    class Meta:
        db_table = 'recaria_characters'
        indexes = [
            models.Index(fields=['consciousness_level']),
            models.Index(fields=['current_realm', 'x_coordinate', 'y_coordinate']),
            models.Index(fields=['guild', 'guild_rank']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_character_class_display()}) Lv.{self.consciousness_level}"
    
    def calculate_skill_cap(self, skill_name):
        """Calculate maximum skill level based on consciousness"""
        base_cap = 100
        consciousness_bonus = self.consciousness_level * 5
        return min(base_cap + consciousness_bonus, 200)


class Skill(models.Model):
    """Skill definitions for the consciousness exploration system"""
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=100)
    category = models.CharField(
        max_length=30,
        choices=[
            ('combat', 'Combat'),
            ('magic', 'Magic'),
            ('consciousness', 'Consciousness'),
            ('crafting', 'Crafting'),
            ('gathering', 'Gathering'),
            ('social', 'Social'),
        ]
    )
    
    # Skill properties
    description = models.TextField()
    base_difficulty = models.IntegerField(default=1)
    mana_cost = models.IntegerField(default=0)
    stamina_cost = models.IntegerField(default=0)
    
    # Requirements
    required_stats = models.JSONField(default=dict)
    # {"intelligence": 15, "wisdom": 10, etc.}
    required_skills = models.JSONField(default=dict)
    # {"meditation": 50, "focus": 30, etc.}
    
    # Effects and bonuses
    effects = models.JSONField(default=dict)
    
    class Meta:
        db_table = 'recaria_skills'
        ordering = ['category', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class Item(models.Model):
    """Items in the medieval consciousness world"""
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=100)
    item_type = models.CharField(
        max_length=20,
        choices=[
            ('weapon', 'Weapon'),
            ('armor', 'Armor'),
            ('consumable', 'Consumable'),
            ('artifact', 'Artifact'),
            ('reagent', 'Reagent'),
            ('tool', 'Tool'),
            ('book', 'Book'),
            ('key', 'Key'),
        ]
    )
    
    # Item properties
    rarity = models.CharField(
        max_length=20,
        choices=[
            ('common', 'Common'),
            ('uncommon', 'Uncommon'),
            ('rare', 'Rare'),
            ('epic', 'Epic'),
            ('legendary', 'Legendary'),
            ('mythic', 'Mythic'),
        ],
        default='common'
    )
    
    # Physical properties
    weight = models.DecimalField(max_digits=6, decimal_places=2, default=0.1)
    durability = models.IntegerField(null=True, blank=True)
    stack_size = models.IntegerField(default=1)
    
    # Requirements
    level_requirement = models.IntegerField(default=1)
    stat_requirements = models.JSONField(default=dict)
    
    # Effects and bonuses
    stats_modifier = models.JSONField(default=dict)
    # {"strength": 5, "mana_regen": 2, etc.}
    special_effects = models.JSONField(default=dict)
    
    # Value
    base_value = models.IntegerField(default=1)
    
    # Visuals and lore
    description = models.TextField()
    lore_text = models.TextField(blank=True)
    icon_url = models.URLField(blank=True)
    
    class Meta:
        db_table = 'recaria_items'
        ordering = ['item_type', 'rarity', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_rarity_display()})"


class Inventory(models.Model):
    """Character inventory"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    character = models.ForeignKey(Character, on_delete=models.CASCADE, related_name='inventory')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    
    # Item state
    quantity = models.IntegerField(default=1)
    equipped = models.BooleanField(default=False)
    equipment_slot = models.CharField(
        max_length=20,
        blank=True,
        choices=[
            ('head', 'Head'),
            ('neck', 'Neck'),
            ('chest', 'Chest'),
            ('legs', 'Legs'),
            ('feet', 'Feet'),
            ('hands', 'Hands'),
            ('ring1', 'Ring 1'),
            ('ring2', 'Ring 2'),
            ('mainhand', 'Main Hand'),
            ('offhand', 'Off Hand'),
        ]
    )
    
    # Item condition
    current_durability = models.IntegerField(null=True, blank=True)
    is_blessed = models.BooleanField(default=False)
    is_cursed = models.BooleanField(default=False)
    enchantments = models.JSONField(default=list)
    
    # Metadata
    acquired_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'recaria_inventory'
        unique_together = ['character', 'item', 'equipment_slot']
        indexes = [
            models.Index(fields=['character', 'equipped']),
            models.Index(fields=['character', 'item']),
        ]
    
    def __str__(self):
        return f"{self.character.name}'s {self.item.name} x{self.quantity}"


class ConsciousnessNode(models.Model):
    """Special locations in realms that enhance consciousness"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    realm = models.ForeignKey(Realm, on_delete=models.CASCADE, related_name='consciousness_nodes')
    name = models.CharField(max_length=100)
    
    # Location
    x_coordinate = models.IntegerField()
    y_coordinate = models.IntegerField()
    z_coordinate = models.IntegerField(default=0)
    
    # Node properties
    node_type = models.CharField(
        max_length=30,
        choices=[
            ('meditation', 'Meditation Circle'),
            ('portal', 'Realm Portal'),
            ('wisdom', 'Wisdom Stone'),
            ('void', 'Void Anchor'),
            ('dream', 'Dream Nexus'),
            ('memory', 'Memory Pool'),
        ]
    )
    power_level = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    
    # Activation requirements
    activation_cost = models.JSONField(default=dict)
    # {"mana": 100, "soul_fragments": 5, etc.}
    cooldown_hours = models.IntegerField(default=24)
    
    # Current state
    is_active = models.BooleanField(default=True)
    last_activated_by = models.ForeignKey(
        Character,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='activated_nodes'
    )
    last_activated_at = models.DateTimeField(null=True, blank=True)
    
    # Effects
    consciousness_exp_bonus = models.IntegerField(default=100)
    special_rewards = models.JSONField(default=dict)
    
    class Meta:
        db_table = 'recaria_consciousness_nodes'
        unique_together = ['realm', 'x_coordinate', 'y_coordinate', 'z_coordinate']
        indexes = [
            models.Index(fields=['realm', 'node_type']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} in {self.realm.name}"


class Quest(models.Model):
    """Consciousness exploration quests"""
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=200)
    quest_type = models.CharField(
        max_length=30,
        choices=[
            ('main', 'Main Quest'),
            ('consciousness', 'Consciousness Journey'),
            ('guild', 'Guild Quest'),
            ('daily', 'Daily Quest'),
            ('event', 'Event Quest'),
        ]
    )
    
    # Quest details
    description = models.TextField()
    lore_text = models.TextField(blank=True)
    
    # Requirements
    min_level = models.IntegerField(default=1)
    required_quests = ArrayField(
        models.CharField(max_length=50),
        default=list,
        blank=True
    )
    required_items = models.JSONField(default=dict)
    
    # Objectives
    objectives = models.JSONField(default=list)
    # [{"type": "meditation", "target": "void_node", "count": 3}, ...]
    
    # Rewards
    exp_reward = models.IntegerField(default=0)
    gold_reward = models.IntegerField(default=0)
    item_rewards = models.JSONField(default=dict)
    skill_rewards = models.JSONField(default=dict)
    
    # Quest availability
    is_repeatable = models.BooleanField(default=False)
    cooldown_hours = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'recaria_quests'
        ordering = ['quest_type', 'min_level']
    
    def __str__(self):
        return f"{self.name} ({self.get_quest_type_display()})"


class CharacterQuest(models.Model):
    """Track character quest progress"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    character = models.ForeignKey(Character, on_delete=models.CASCADE, related_name='quests')
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE)
    
    # Progress tracking
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
            ('abandoned', 'Abandoned'),
        ],
        default='active'
    )
    progress = models.JSONField(default=dict)
    # {"meditation_count": 2, "items_collected": {"soul_fragment": 3}, etc.}
    
    # Timestamps
    accepted_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_progress = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'recaria_character_quests'
        unique_together = ['character', 'quest']
        indexes = [
            models.Index(fields=['character', 'status']),
        ]
    
    def __str__(self):
        return f"{self.character.name} - {self.quest.name} ({self.status})"


class Guild(models.Model):
    """Player guilds for group consciousness exploration"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    tag = models.CharField(max_length=10, unique=True)
    
    # Leadership
    founder = models.ForeignKey(
        Character,
        on_delete=models.PROTECT,
        related_name='founded_guild'
    )
    leader = models.ForeignKey(
        Character,
        on_delete=models.PROTECT,
        related_name='led_guild'
    )
    
    # Guild properties
    motto = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    banner_pattern = models.JSONField(default=dict)
    
    # Guild stats
    level = models.IntegerField(default=1)
    experience = models.BigIntegerField(default=0)
    collective_consciousness = models.IntegerField(default=0)
    
    # Guild resources
    guild_bank_gold = models.BigIntegerField(default=0)
    guild_bank_items = models.JSONField(default=dict)
    
    # Guild features
    guild_hall_realm = models.ForeignKey(
        Realm,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='guild_halls'
    )
    unlocked_perks = models.JSONField(default=list)
    
    # Settings
    is_recruiting = models.BooleanField(default=True)
    min_level_requirement = models.IntegerField(default=1)
    application_message = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'recaria_guilds'
        ordering = ['-level', 'name']
    
    def __str__(self):
        return f"[{self.tag}] {self.name}"


class Creature(models.Model):
    """NPCs and monsters in the consciousness realms"""
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=100)
    creature_type = models.CharField(
        max_length=30,
        choices=[
            ('beast', 'Beast'),
            ('elemental', 'Elemental'),
            ('undead', 'Undead'),
            ('demon', 'Demon'),
            ('construct', 'Construct'),
            ('humanoid', 'Humanoid'),
            ('aberration', 'Aberration'),
            ('dragon', 'Dragon'),
        ]
    )
    
    # Creature stats
    level = models.IntegerField(default=1)
    health = models.IntegerField()
    mana = models.IntegerField(default=0)
    
    # Combat stats
    attack = models.IntegerField()
    defense = models.IntegerField()
    magic_resistance = models.IntegerField(default=0)
    
    # AI behavior
    aggression = models.CharField(
        max_length=20,
        choices=[
            ('passive', 'Passive'),
            ('neutral', 'Neutral'),
            ('aggressive', 'Aggressive'),
            ('territorial', 'Territorial'),
        ],
        default='neutral'
    )
    
    # Loot
    loot_table = models.JSONField(default=dict)
    # {"gold": {"min": 10, "max": 50}, "items": [...], "drop_rates": {...}}
    experience_value = models.IntegerField()
    
    # Special abilities
    abilities = models.JSONField(default=list)
    
    # Appearance and lore
    description = models.TextField()
    lore_text = models.TextField(blank=True)
    
    class Meta:
        db_table = 'recaria_creatures'
        ordering = ['level', 'name']
    
    def __str__(self):
        return f"{self.name} (Lv.{self.level})"


class CreatureSpawn(models.Model):
    """Creature spawn points in realms"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    creature = models.ForeignKey(Creature, on_delete=models.CASCADE)
    realm = models.ForeignKey(Realm, on_delete=models.CASCADE, related_name='creature_spawns')
    
    # Spawn location
    x_coordinate = models.IntegerField()
    y_coordinate = models.IntegerField()
    z_coordinate = models.IntegerField(default=0)
    spawn_radius = models.IntegerField(default=10)
    
    # Spawn properties
    max_creatures = models.IntegerField(default=1)
    respawn_time = models.IntegerField(default=300)  # In seconds
    
    # Current state
    current_creatures = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'recaria_creature_spawns'
        indexes = [
            models.Index(fields=['realm', 'creature']),
            models.Index(fields=['realm', 'x_coordinate', 'y_coordinate']),
        ]
    
    def __str__(self):
        return f"{self.creature.name} spawn in {self.realm.name}"


class CombatLog(models.Model):
    """Combat encounters between characters and creatures"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Participants
    attacker = models.ForeignKey(
        Character,
        on_delete=models.CASCADE,
        related_name='attacks_made'
    )
    defender_character = models.ForeignKey(
        Character,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='attacks_received'
    )
    defender_creature = models.ForeignKey(
        Creature,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    
    # Combat details
    realm = models.ForeignKey(Realm, on_delete=models.CASCADE)
    damage_dealt = models.IntegerField()
    damage_type = models.CharField(
        max_length=20,
        choices=[
            ('physical', 'Physical'),
            ('magical', 'Magical'),
            ('psychic', 'Psychic'),
            ('void', 'Void'),
        ]
    )
    
    # Results
    is_critical = models.BooleanField(default=False)
    is_killing_blow = models.BooleanField(default=False)
    
    # Loot (if killing blow)
    loot_gained = models.JSONField(default=dict, blank=True)
    experience_gained = models.IntegerField(default=0)
    
    # Timestamp
    occurred_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'recaria_combat_logs'
        ordering = ['-occurred_at']
        indexes = [
            models.Index(fields=['attacker', 'occurred_at']),
            models.Index(fields=['realm', 'occurred_at']),
        ]
    
    def __str__(self):
        defender = self.defender_character or self.defender_creature
        return f"{self.attacker.name} vs {defender} - {self.damage_dealt} damage"


class MeditationSession(models.Model):
    """Track meditation sessions for consciousness advancement"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    character = models.ForeignKey(
        Character,
        on_delete=models.CASCADE,
        related_name='meditation_sessions'
    )
    
    # Session location and type
    realm = models.ForeignKey(Realm, on_delete=models.CASCADE)
    node = models.ForeignKey(
        ConsciousnessNode,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    meditation_type = models.CharField(
        max_length=30,
        choices=[
            ('focus', 'Focus Meditation'),
            ('void', 'Void Meditation'),
            ('astral', 'Astral Projection'),
            ('dream', 'Dream Walking'),
            ('group', 'Group Meditation'),
        ]
    )
    
    # Session progress
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    duration = models.IntegerField(default=0)  # In seconds
    
    # Results
    consciousness_exp_gained = models.IntegerField(default=0)
    insights_gained = models.JSONField(default=list)
    skill_improvements = models.JSONField(default=dict)
    
    # Special events during meditation
    visions = models.JSONField(default=list)
    void_encounters = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'recaria_meditation_sessions'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['character', 'started_at']),
            models.Index(fields=['realm', 'meditation_type']),
        ]
    
    def __str__(self):
        return f"{self.character.name}'s {self.get_meditation_type_display()} session"


class Achievement(models.Model):
    """Achievements for consciousness exploration milestones"""
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=100)
    category = models.CharField(
        max_length=30,
        choices=[
            ('exploration', 'Exploration'),
            ('combat', 'Combat'),
            ('consciousness', 'Consciousness'),
            ('social', 'Social'),
            ('crafting', 'Crafting'),
            ('special', 'Special'),
        ]
    )
    
    # Achievement details
    description = models.TextField()
    hidden = models.BooleanField(default=False)
    
    # Requirements
    criteria = models.JSONField(default=dict)
    # {"type": "meditation_count", "value": 100, "realm": "void", etc.}
    
    # Rewards
    title_reward = models.CharField(max_length=100, blank=True)
    consciousness_exp_reward = models.IntegerField(default=0)
    special_rewards = models.JSONField(default=dict)
    
    # Display
    icon_url = models.URLField(blank=True)
    rarity = models.CharField(
        max_length=20,
        choices=[
            ('common', 'Common'),
            ('rare', 'Rare'),
            ('epic', 'Epic'),
            ('legendary', 'Legendary'),
        ],
        default='common'
    )
    
    class Meta:
        db_table = 'recaria_achievements'
        ordering = ['category', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class CharacterAchievement(models.Model):
    """Track character achievements"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    character = models.ForeignKey(
        Character,
        on_delete=models.CASCADE,
        related_name='achievements'
    )
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    
    # Progress
    progress = models.JSONField(default=dict)
    completed = models.BooleanField(default=False)
    
    # Timestamps
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'recaria_character_achievements'
        unique_together = ['character', 'achievement']
        indexes = [
            models.Index(fields=['character', 'completed']),
        ]
    
    def __str__(self):
        status = "Completed" if self.completed else "In Progress"
        return f"{self.character.name} - {self.achievement.name} ({status})"