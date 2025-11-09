"""
Gamification Models for Receipt Processing System
Tracks user achievements, points, levels, and rewards
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import json
from datetime import timedelta


class UserProfile(models.Model):
    """Extended user profile with gamification stats"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='gamification_profile')
    
    # Carrots (points) and levels
    total_points = models.IntegerField(default=0)  # Total carrots earned
    current_level = models.IntegerField(default=1)
    experience_points = models.IntegerField(default=0)  # Current level carrots
    
    # Stats
    receipts_processed = models.IntegerField(default=0)
    receipts_validated = models.IntegerField(default=0)
    accuracy_score = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(100.0)])
    streak_days = models.IntegerField(default=0)
    last_activity_date = models.DateField(null=True, blank=True)
    
    # Rankings
    weekly_rank = models.IntegerField(null=True, blank=True)
    monthly_rank = models.IntegerField(null=True, blank=True)
    all_time_rank = models.IntegerField(null=True, blank=True)
    
    # Preferences
    preferred_language = models.CharField(max_length=10, default='tr')
    notification_enabled = models.BooleanField(default=True)
    tutorial_completed = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-total_points']
    
    def __str__(self):
        return f"{self.user.username} - Level {self.current_level} (🥕 {self.total_points} carrots)"
    
    def add_points(self, points, reason=""):
        """Add carrots and check for level up"""
        self.total_points += points  # Add to total carrots
        self.experience_points += points  # Add to current level carrots
        
        # Check for level up
        next_level_points = self.get_next_level_requirement()
        if self.experience_points >= next_level_points:
            self.level_up()
        
        self.save()
        
        # Log the carrot transaction
        PointTransaction.objects.create(
            user=self.user,
            points=points,  # Actually carrots
            reason=reason,
            transaction_type='earned'
        )
        
        return self.current_level
    
    def level_up(self):
        """Level up the user"""
        self.current_level += 1
        self.experience_points = 0
        
        # Create achievement for level up
        Achievement.objects.get_or_create(
            user=self.user,
            achievement_type='level_up',
            defaults={
                'name': f'Level {self.current_level} Achieved!',
                'description': f'Reached level {self.current_level}',
                'points_awarded': self.current_level * 100,
                'icon': 'trophy'
            }
        )
    
    def get_next_level_requirement(self):
        """Calculate carrots needed for next level"""
        # Exponential growth: 100, 250, 500, 1000, 2000...
        return int(100 * (1.5 ** (self.current_level - 1)))
    
    def update_streak(self):
        """Update daily streak"""
        today = timezone.now().date()
        
        if not self.last_activity_date:
            self.streak_days = 1
        elif self.last_activity_date == today:
            return  # Already updated today
        elif self.last_activity_date == today - timedelta(days=1):
            self.streak_days += 1
        else:
            self.streak_days = 1
        
        self.last_activity_date = today
        self.save()
        
        # Check for streak achievements
        if self.streak_days in [7, 30, 100]:
            Achievement.objects.get_or_create(
                user=self.user,
                achievement_type='streak',
                name=f'{self.streak_days} Day Streak!',
                defaults={
                    'description': f'Maintained a {self.streak_days} day streak',
                    'points_awarded': self.streak_days * 10,
                    'icon': 'fire'
                }
            )


class Achievement(models.Model):
    """User achievements and badges"""
    
    ACHIEVEMENT_TYPES = [
        ('first_receipt', 'First Receipt'),
        ('accuracy_master', 'Accuracy Master'),
        ('speed_demon', 'Speed Demon'),
        ('validator', 'Validator'),
        ('contributor', 'Contributor'),
        ('streak', 'Streak Keeper'),
        ('level_up', 'Level Up'),
        ('milestone', 'Milestone'),
        ('special', 'Special Event'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='achievements')
    achievement_type = models.CharField(max_length=30, choices=ACHIEVEMENT_TYPES)
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50, default='star')
    color = models.CharField(max_length=7, default='#FFD700')
    
    points_awarded = models.IntegerField(default=0)
    rarity = models.CharField(max_length=20, choices=[
        ('common', 'Common'),
        ('rare', 'Rare'),
        ('epic', 'Epic'),
        ('legendary', 'Legendary'),
    ], default='common')
    
    unlocked_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-unlocked_at']
        unique_together = ['user', 'achievement_type', 'name']
    
    def __str__(self):
        return f"{self.user.username} - {self.name}"


class PointTransaction(models.Model):
    """Track all carrot transactions"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='point_transactions')
    points = models.IntegerField()  # Number of carrots
    reason = models.CharField(max_length=255)
    transaction_type = models.CharField(max_length=20, choices=[
        ('earned', 'Earned'),
        ('spent', 'Spent'),
        ('bonus', 'Bonus'),
        ('penalty', 'Penalty'),
    ])
    
    related_document_id = models.UUIDField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - 🥕 {self.points} carrots ({self.transaction_type})"


class Challenge(models.Model):
    """Daily/Weekly challenges for users"""
    title = models.CharField(max_length=200)
    description = models.TextField()
    challenge_type = models.CharField(max_length=30, choices=[
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('special', 'Special Event'),
    ])
    
    # Requirements
    target_count = models.IntegerField(default=1)
    target_type = models.CharField(max_length=50, choices=[
        ('receipts_processed', 'Process Receipts'),
        ('receipts_validated', 'Validate Receipts'),
        ('accuracy_target', 'Accuracy Target'),
        ('streak_days', 'Maintain Streak'),
        ('points_earned', 'Earn Points'),
    ])
    
    # Rewards
    points_reward = models.IntegerField(default=100)
    badge_reward = models.CharField(max_length=100, blank=True)
    
    # Timing
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.title} ({self.challenge_type})"


class UserChallenge(models.Model):
    """Track user progress on challenges"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_challenges')
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='user_progress')
    
    current_progress = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    claimed_reward = models.BooleanField(default=False)
    
    started_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-started_at']
        unique_together = ['user', 'challenge']
    
    def __str__(self):
        return f"{self.user.username} - {self.challenge.title} ({self.current_progress}/{self.challenge.target_count})"
    
    def update_progress(self, increment=1):
        """Update challenge progress"""
        self.current_progress += increment
        
        if self.current_progress >= self.challenge.target_count and not self.completed:
            self.completed = True
            self.completed_at = timezone.now()
            
            # Award points
            profile = UserProfile.objects.get_or_create(user=self.user)[0]
            profile.add_points(self.challenge.points_reward, f"Completed challenge: {self.challenge.title}")
            
            # Create achievement if badge reward exists
            if self.challenge.badge_reward:
                Achievement.objects.get_or_create(
                    user=self.user,
                    achievement_type='special',
                    name=self.challenge.badge_reward,
                    defaults={
                        'description': f'Completed: {self.challenge.title}',
                        'points_awarded': self.challenge.points_reward,
                        'icon': 'medal'
                    }
                )
        
        self.save()


class Leaderboard(models.Model):
    """Leaderboard entries for different periods"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='leaderboard_entries')
    period_type = models.CharField(max_length=20, choices=[
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('all_time', 'All Time'),
    ])
    
    period_start = models.DateField()
    period_end = models.DateField(null=True, blank=True)
    
    points_earned = models.IntegerField(default=0)
    receipts_processed = models.IntegerField(default=0)
    accuracy_score = models.FloatField(default=0.0)
    
    rank = models.IntegerField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-points_earned']
        unique_together = ['user', 'period_type', 'period_start']
        indexes = [
            models.Index(fields=['period_type', '-points_earned']),
            models.Index(fields=['period_start', 'period_end']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.period_type} - Rank #{self.rank}"


class ValidationFeedback(models.Model):
    """Track user corrections and validations for learning"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='validation_feedback')
    document_id = models.UUIDField()
    
    field_name = models.CharField(max_length=50)
    original_value = models.TextField(blank=True)
    corrected_value = models.TextField()
    confidence_score = models.FloatField(default=0.0)
    
    # Learning metrics
    is_correct = models.BooleanField(null=True, blank=True)  # Verified by other users
    votes_up = models.IntegerField(default=0)
    votes_down = models.IntegerField(default=0)
    
    # Points awarded for this validation
    points_awarded = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['document_id', 'field_name']),
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.field_name} validation"


class LearningModel(models.Model):
    """Store learning patterns from user feedback"""
    pattern_type = models.CharField(max_length=50, choices=[
        ('store_name', 'Store Name Pattern'),
        ('date_format', 'Date Format Pattern'),
        ('amount_format', 'Amount Format Pattern'),
        ('item_pattern', 'Item Pattern'),
        ('field_location', 'Field Location Pattern'),
    ])
    
    pattern_value = models.TextField()
    confidence_score = models.FloatField(default=0.0)
    usage_count = models.IntegerField(default=0)
    success_count = models.IntegerField(default=0)
    
    # Store-specific patterns
    store_name = models.CharField(max_length=255, blank=True)
    
    # Metadata
    sample_text = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-confidence_score', '-usage_count']
        indexes = [
            models.Index(fields=['pattern_type', '-confidence_score']),
            models.Index(fields=['store_name', 'pattern_type']),
        ]
    
    def __str__(self):
        return f"{self.pattern_type} - {self.confidence_score:.2f}% confidence"
    
    def update_confidence(self, success=True):
        """Update confidence based on success/failure"""
        self.usage_count += 1
        if success:
            self.success_count += 1
        
        # Calculate new confidence
        self.confidence_score = (self.success_count / self.usage_count) * 100
        self.save()


# Carrot reward values (detailed system)
POINT_REWARDS = {
    # Basic actions
    'receipt_upload': 5,
    'receipt_ocr_complete': 10,
    'complete_extraction': 15,
    
    # Validation rewards
    'store_name_validation': 3,
    'date_validation': 3,
    'total_amount_validation': 5,
    'product_validation': 2,  # Per product
    'field_validation': 3,  # Generic field
    
    # Correction rewards
    'missing_info_addition': 5,
    'field_correction': 7,
    'error_correction': 7,
    
    # Community actions
    'community_validation': 3,
    'accurate_validation': 5,
    
    # Bonuses
    'perfect_receipt': 20,  # 100% accuracy
    'streak_5': 30,  # 5 correct receipts in a row
    'streak_10': 70,  # 10 correct receipts in a row
    'daily_bonus_10': 50,  # 10 receipts in a day
    'weekly_bonus_50': 200,  # 50 receipts in a week
    'monthly_bonus_100': 500,  # 100 receipts in a month
    
    # Dynamic bonuses
    'streak_bonus': lambda days: days * 5,
    'level_up': lambda level: level * 100,
    'challenge_complete': 50,
    'expert_multiplier': 2,  # Multiplier for expert validators
}

# Achievement definitions
ACHIEVEMENT_DEFINITIONS = {
    'first_receipt': {
        'name': 'First Steps',
        'description': 'Uploaded your first receipt',
        'points': 50,  # 50 carrots
        'icon': '🥕',  # Carrot emoji
        'rarity': 'common'
    },
    'speed_demon_10': {
        'name': 'Speed Demon',
        'description': 'Processed 10 receipts in one day',
        'points': 200,  # 200 carrots
        'icon': '⚡',  # Lightning emoji
        'rarity': 'rare'
    },
    'accuracy_95': {
        'name': 'Accuracy Master',
        'description': 'Maintained 95% accuracy over 50 receipts',
        'points': 500,  # 500 carrots
        'icon': '🎯',  # Target emoji
        'rarity': 'epic'
    },
    'validator_100': {
        'name': 'Community Helper',
        'description': 'Validated 100 receipts from other users',
        'points': 300,  # 300 carrots
        'icon': '🤝',  # Handshake emoji
        'rarity': 'rare'
    },
    'streak_30': {
        'name': 'Dedicated Scanner',
        'description': 'Maintained a 30-day streak',
        'points': 1000,  # 1000 carrots!
        'icon': '🔥',  # Fire emoji
        'rarity': 'legendary'
    },
}