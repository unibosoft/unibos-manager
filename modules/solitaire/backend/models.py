"""
Solitaire Game Session Models
Stores game state for persistence across sessions
"""

from django.db import models
from django.conf import settings
import json
from datetime import datetime
from django.utils import timezone

class SolitaireSession(models.Model):
    """Stores the complete state of a solitaire game"""
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='solitaire_sessions')
    session_id = models.CharField(max_length=100, unique=True)
    
    # Game state as JSON
    stock_pile = models.JSONField(default=list)  # Cards in stock pile
    waste_pile = models.JSONField(default=list)  # Cards in waste pile
    foundation_piles = models.JSONField(default=dict)  # 4 foundation piles (by suit)
    tableau_piles = models.JSONField(default=list)  # 7 tableau piles
    
    # Game statistics
    moves_count = models.IntegerField(default=0)
    score = models.IntegerField(default=0)
    game_time = models.IntegerField(default=0)  # Seconds played
    
    # Game status
    is_active = models.BooleanField(default=True)
    is_won = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    last_played = models.DateTimeField(auto_now=True)
    
    # Security
    last_minimize = models.DateTimeField(null=True, blank=True)
    lock_password = models.CharField(max_length=128, null=True, blank=True)  # Hashed
    
    class Meta:
        ordering = ['-last_played']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['session_id']),
        ]
    
    def __str__(self):
        return f"Solitaire #{self.id} - {self.user.username} - Score: {self.score}"
    
    def save_game_state(self, game_state):
        """Save the current game state"""
        self.stock_pile = game_state.get('stock', [])
        self.waste_pile = game_state.get('waste', [])
        self.foundation_piles = game_state.get('foundations', {})
        self.tableau_piles = game_state.get('tableau', [])
        self.moves_count = game_state.get('moves', 0)
        self.score = game_state.get('score', 0)
        self.game_time = game_state.get('time', 0)
        self.save()
    
    def get_game_state(self):
        """Retrieve the current game state"""
        return {
            'stock': self.stock_pile,
            'waste': self.waste_pile,
            'foundations': self.foundation_piles,
            'tableau': self.tableau_piles,
            'moves': self.moves_count,
            'score': self.score,
            'time': self.game_time,
            'is_won': self.is_won
        }
    
    def set_minimize_lock(self, password_hash):
        """Set lock password when minimizing"""
        self.last_minimize = datetime.now()
        self.lock_password = password_hash
        self.save()
    
    def verify_lock(self, password_hash):
        """Verify the lock password"""
        return self.lock_password == password_hash


class SolitaireMove(models.Model):
    """Track individual moves for undo functionality"""
    
    session = models.ForeignKey(SolitaireSession, on_delete=models.CASCADE, related_name='moves')
    move_number = models.IntegerField()
    
    # Move details
    from_pile = models.CharField(max_length=20)  # stock, waste, foundation_X, tableau_X
    to_pile = models.CharField(max_length=20)
    cards_moved = models.JSONField()  # List of cards moved
    cards_revealed = models.JSONField(default=list)  # Any cards revealed as result
    
    # For undo
    previous_state = models.JSONField()
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['session', 'move_number']
        unique_together = ['session', 'move_number']
    
    def __str__(self):
        return f"Move #{self.move_number} in Session {self.session_id}"


class SolitaireStatistics(models.Model):
    """Track overall solitaire statistics for a user"""
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='solitaire_stats')
    
    # Game statistics
    games_played = models.IntegerField(default=0)
    games_won = models.IntegerField(default=0)
    total_score = models.IntegerField(default=0)
    highest_score = models.IntegerField(default=0)
    total_time_played = models.IntegerField(default=0)  # Total seconds
    
    # Streaks
    current_win_streak = models.IntegerField(default=0)
    best_win_streak = models.IntegerField(default=0)
    
    # Records
    fastest_win = models.IntegerField(null=True, blank=True)  # Seconds
    fewest_moves_win = models.IntegerField(null=True, blank=True)
    
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Solitaire statistics"
    
    def __str__(self):
        return f"{self.user.username} - Win Rate: {self.win_rate}%"
    
    @property
    def win_rate(self):
        """Calculate win percentage"""
        if self.games_played == 0:
            return 0
        return round((self.games_won / self.games_played) * 100, 1)


class SolitairePlayer(models.Model):
    """Track both registered and anonymous players"""
    
    # Player identification
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='solitaire_players')
    session_key = models.CharField(max_length=100, db_index=True)  # Django session key
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    
    # Player info
    display_name = models.CharField(max_length=100, blank=True)
    is_anonymous = models.BooleanField(default=True)
    
    # Activity tracking
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)
    total_sessions = models.IntegerField(default=0)
    
    # Location info (optional, from IP)
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_banned = models.BooleanField(default=False)
    ban_reason = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-last_seen']
        indexes = [
            models.Index(fields=['session_key', 'ip_address']),
            models.Index(fields=['last_seen']),
        ]
    
    def __str__(self):
        if self.user:
            return f"Player: {self.user.username} ({self.ip_address})"
        return f"Anonymous Player: {self.ip_address}"


class SolitaireGameSession(models.Model):
    """Track individual game sessions"""
    
    player = models.ForeignKey(SolitairePlayer, on_delete=models.CASCADE, related_name='game_sessions')
    
    # Session info
    session_id = models.CharField(max_length=100, unique=True, db_index=True)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    # Game state
    game_state = models.JSONField(default=dict)  # Complete game state
    moves_count = models.IntegerField(default=0)
    score = models.IntegerField(default=0)
    time_played = models.IntegerField(default=0)  # Seconds
    
    # Game result
    is_completed = models.BooleanField(default=False)
    is_won = models.BooleanField(default=False)
    is_abandoned = models.BooleanField(default=False)
    
    # Browser info
    browser_info = models.JSONField(default=dict)  # Screen size, etc.
    
    class Meta:
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['player', 'started_at']),
            models.Index(fields=['is_won', 'is_completed']),
        ]
    
    def __str__(self):
        return f"Game #{self.id} - {self.player} - Score: {self.score}"
    
    def end_session(self, won=False):
        """Mark session as ended"""
        if not self.ended_at:
            self.ended_at = timezone.now()
        self.is_completed = True
        self.is_won = won
        self.is_abandoned = False  # Not abandoned if properly ended
        self.save()
    
    def abandon_session(self):
        """Mark session as abandoned"""
        if not self.ended_at:
            self.ended_at = timezone.now()
        self.is_abandoned = True
        self.is_completed = False  # Not completed if abandoned
        self.is_won = False  # Can't win if abandoned
        self.save()


class SolitaireGameDeck(models.Model):
    """Store unique deck configurations for multiplayer games"""
    
    deck_id = models.CharField(max_length=50, unique=True, db_index=True)
    deck_seed = models.CharField(max_length=100)  # Seed for deck generation
    deck_configuration = models.JSONField()  # Full deck configuration
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['deck_id']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Deck #{self.deck_id}"


class SolitaireMultiplayerGame(models.Model):
    """Multiplayer game sessions"""
    
    game_code = models.CharField(max_length=10, unique=True, db_index=True)
    deck = models.ForeignKey(SolitaireGameDeck, on_delete=models.CASCADE, related_name='multiplayer_games')
    
    # Players (max 2 for now)
    player1 = models.ForeignKey(SolitairePlayer, on_delete=models.CASCADE, related_name='multiplayer_games_as_player1', null=True)
    player2 = models.ForeignKey(SolitairePlayer, on_delete=models.CASCADE, related_name='multiplayer_games_as_player2', null=True, blank=True)
    
    # Game sessions for each player
    player1_session = models.ForeignKey(SolitaireGameSession, on_delete=models.CASCADE, related_name='multiplayer_as_player1', null=True)
    player2_session = models.ForeignKey(SolitaireGameSession, on_delete=models.CASCADE, related_name='multiplayer_as_player2', null=True, blank=True)
    
    # Game status
    is_active = models.BooleanField(default=True)
    winner = models.ForeignKey(SolitairePlayer, on_delete=models.SET_NULL, null=True, blank=True, related_name='won_multiplayer_games')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Multiplayer Game {self.game_code}"
    
    def is_full(self):
        """Check if game has 2 players"""
        return self.player1 and self.player2
    
    def get_opponent(self, player):
        """Get the opponent of a given player"""
        if self.player1 == player:
            return self.player2
        elif self.player2 == player:
            return self.player1
        return None


class SolitaireActivity(models.Model):
    """Track detailed activity within games"""
    
    ACTION_CHOICES = [
        ('start', 'Game Started'),
        ('move', 'Card Move'),
        ('undo', 'Undo Move'),
        ('hint', 'Hint Used'),
        ('auto', 'Auto Complete'),
        ('win', 'Game Won'),
        ('abandon', 'Game Abandoned'),
        ('pause', 'Game Paused'),
        ('resume', 'Game Resumed'),
    ]
    
    session = models.ForeignKey(SolitaireGameSession, on_delete=models.CASCADE, related_name='activities')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(default=dict)  # Additional action details
    
    class Meta:
        ordering = ['session', 'timestamp']
        indexes = [
            models.Index(fields=['session', 'action']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"{self.get_action_display()} at {self.timestamp}"


class SolitaireMoveHistory(models.Model):
    """Track every single card movement in detail"""
    
    PILE_TYPES = [
        ('stock', 'Stock'),
        ('waste', 'Waste'),
        ('tableau', 'Tableau'),
        ('foundation', 'Foundation'),
    ]
    
    session = models.ForeignKey(SolitaireGameSession, on_delete=models.CASCADE, related_name='move_history')
    move_number = models.IntegerField()  # Sequential move number
    
    # Move details
    from_pile_type = models.CharField(max_length=20, choices=PILE_TYPES)
    from_pile_index = models.IntegerField(null=True, blank=True)  # For tableau/foundation index
    to_pile_type = models.CharField(max_length=20, choices=PILE_TYPES)
    to_pile_index = models.IntegerField(null=True, blank=True)  # For tableau/foundation index
    
    # Card details
    cards = models.JSONField()  # List of cards moved [{suit, rank, face_up}]
    num_cards = models.IntegerField(default=1)  # Number of cards moved
    
    # State tracking
    score_before = models.IntegerField(default=0)
    score_after = models.IntegerField(default=0)
    score_change = models.IntegerField(default=0)
    
    # Timing
    timestamp = models.DateTimeField(auto_now_add=True)
    time_since_start = models.IntegerField(default=0)  # Seconds since game start
    time_since_last_move = models.IntegerField(default=0)  # Seconds since last move
    
    # Additional context
    is_undo = models.BooleanField(default=False)
    is_auto_move = models.BooleanField(default=False)
    revealed_card = models.JSONField(null=True, blank=True)  # Card revealed after move
    
    class Meta:
        ordering = ['session', 'move_number']
        unique_together = ['session', 'move_number']
        indexes = [
            models.Index(fields=['session', 'timestamp']),
            models.Index(fields=['session', 'move_number']),
        ]
    
    def __str__(self):
        card_info = self.cards[0] if self.cards else {}
        card_str = f"{card_info.get('rank', '?')}{card_info.get('suit', '?')}"
        from_str = f"{self.from_pile_type}"
        if self.from_pile_index is not None:
            from_str += f"[{self.from_pile_index}]"
        to_str = f"{self.to_pile_type}"
        if self.to_pile_index is not None:
            to_str += f"[{self.to_pile_index}]"
        return f"Move #{self.move_number}: {card_str} from {from_str} to {to_str}"
    
    def get_card_display(self):
        """Get formatted card display"""
        if not self.cards:
            return "No cards"
        
        suits = {'H': '♥', 'D': '♦', 'C': '♣', 'S': '♠'}
        result = []
        for card in self.cards:
            suit = suits.get(card.get('suit', ''), card.get('suit', '?'))
            rank = card.get('rank', '?')
            result.append(f"{rank}{suit}")
        return ", ".join(result)