"""
Django Admin configuration for Gamification models
"""

from django.contrib import admin
from .gamification_models import (
    UserProfile, Achievement, PointTransaction, Challenge, 
    UserChallenge, Leaderboard, ValidationFeedback, LearningModel
)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_points', 'current_level', 'receipts_processed', 
                   'accuracy_score', 'streak_days', 'last_activity_date']
    list_filter = ['current_level', 'tutorial_completed', 'last_activity_date']
    search_fields = ['user__username', 'user__email']
    ordering = ['-total_points']
    
    fieldsets = (
        ('User Info', {
            'fields': ('user', 'preferred_language', 'notification_enabled', 'tutorial_completed')
        }),
        ('Points & Level', {
            'fields': ('total_points', 'current_level', 'experience_points')
        }),
        ('Statistics', {
            'fields': ('receipts_processed', 'receipts_validated', 'accuracy_score', 
                      'streak_days', 'last_activity_date')
        }),
        ('Rankings', {
            'fields': ('weekly_rank', 'monthly_rank', 'all_time_rank')
        }),
    )


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'achievement_type', 'rarity', 'points_awarded', 'unlocked_at']
    list_filter = ['achievement_type', 'rarity', 'unlocked_at']
    search_fields = ['user__username', 'name', 'description']
    ordering = ['-unlocked_at']


@admin.register(PointTransaction)
class PointTransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'points', 'transaction_type', 'reason', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['user__username', 'reason']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'


@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ['title', 'challenge_type', 'target_type', 'target_count', 
                   'points_reward', 'start_date', 'end_date', 'is_active']
    list_filter = ['challenge_type', 'target_type', 'is_active']
    search_fields = ['title', 'description']
    ordering = ['-start_date']
    
    fieldsets = (
        ('Challenge Info', {
            'fields': ('title', 'description', 'challenge_type')
        }),
        ('Requirements', {
            'fields': ('target_type', 'target_count')
        }),
        ('Rewards', {
            'fields': ('points_reward', 'badge_reward')
        }),
        ('Timing', {
            'fields': ('start_date', 'end_date', 'is_active')
        }),
    )


@admin.register(UserChallenge)
class UserChallengeAdmin(admin.ModelAdmin):
    list_display = ['user', 'challenge', 'current_progress', 'completed', 
                   'completed_at', 'claimed_reward']
    list_filter = ['completed', 'claimed_reward', 'completed_at']
    search_fields = ['user__username', 'challenge__title']
    ordering = ['-started_at']


@admin.register(Leaderboard)
class LeaderboardAdmin(admin.ModelAdmin):
    list_display = ['user', 'period_type', 'period_start', 'points_earned', 
                   'receipts_processed', 'accuracy_score', 'rank']
    list_filter = ['period_type', 'period_start']
    search_fields = ['user__username']
    ordering = ['period_type', 'rank']
    date_hierarchy = 'period_start'


@admin.register(ValidationFeedback)
class ValidationFeedbackAdmin(admin.ModelAdmin):
    list_display = ['user', 'field_name', 'confidence_score', 'is_correct', 
                   'votes_up', 'votes_down', 'points_awarded', 'created_at']
    list_filter = ['field_name', 'is_correct', 'created_at']
    search_fields = ['user__username', 'field_name', 'original_value', 'corrected_value']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'


@admin.register(LearningModel)
class LearningModelAdmin(admin.ModelAdmin):
    list_display = ['pattern_type', 'confidence_score', 'usage_count', 
                   'success_count', 'store_name', 'updated_at']
    list_filter = ['pattern_type', 'store_name']
    search_fields = ['pattern_value', 'store_name', 'sample_text']
    ordering = ['-confidence_score', '-usage_count']