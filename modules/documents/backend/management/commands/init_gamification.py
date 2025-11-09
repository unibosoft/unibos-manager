"""
Management command to initialize gamification system
Creates default challenges, achievements, and sets up leaderboards
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()
from datetime import timedelta
from modules.documents.backend.gamification_models import (
    UserProfile, Challenge, Achievement, Leaderboard
)


class Command(BaseCommand):
    help = 'Initialize gamification system with default data'
    
    def handle(self, *args, **options):
        self.stdout.write('Initializing gamification system...')
        
        # Create user profiles for existing users
        self.create_user_profiles()
        
        # Create default challenges
        self.create_default_challenges()
        
        # Initialize leaderboards
        self.initialize_leaderboards()
        
        self.stdout.write(self.style.SUCCESS('Gamification system initialized successfully!'))
    
    def create_user_profiles(self):
        """Create gamification profiles for all existing users"""
        users = User.objects.all()
        created_count = 0
        
        for user in users:
            profile, created = UserProfile.objects.get_or_create(user=user)
            if created:
                created_count += 1
                self.stdout.write(f'Created profile for {user.username}')
        
        self.stdout.write(f'Created {created_count} new user profiles')
    
    def create_default_challenges(self):
        """Create default daily, weekly, and monthly challenges"""
        now = timezone.now()
        
        # Daily challenges
        daily_challenges = [
            {
                'title': 'Daily Scanner',
                'description': 'Process 3 receipts today',
                'challenge_type': 'daily',
                'target_count': 3,
                'target_type': 'receipts_processed',
                'points_reward': 50,
                'start_date': now,
                'end_date': now + timedelta(days=1)
            },
            {
                'title': 'Accuracy Expert',
                'description': 'Achieve 90% accuracy on validations today',
                'challenge_type': 'daily',
                'target_count': 90,
                'target_type': 'accuracy_target',
                'points_reward': 75,
                'start_date': now,
                'end_date': now + timedelta(days=1)
            },
            {
                'title': 'Community Helper',
                'description': 'Validate 5 receipts from other users',
                'challenge_type': 'daily',
                'target_count': 5,
                'target_type': 'receipts_validated',
                'points_reward': 60,
                'start_date': now,
                'end_date': now + timedelta(days=1)
            }
        ]
        
        # Weekly challenges
        weekly_challenges = [
            {
                'title': 'Week Warrior',
                'description': 'Process 20 receipts this week',
                'challenge_type': 'weekly',
                'target_count': 20,
                'target_type': 'receipts_processed',
                'points_reward': 300,
                'badge_reward': 'Week Warrior Badge',
                'start_date': now,
                'end_date': now + timedelta(weeks=1)
            },
            {
                'title': 'Streak Master',
                'description': 'Maintain a 7-day streak',
                'challenge_type': 'weekly',
                'target_count': 7,
                'target_type': 'streak_days',
                'points_reward': 500,
                'badge_reward': 'Streak Master Badge',
                'start_date': now,
                'end_date': now + timedelta(weeks=1)
            },
            {
                'title': 'Point Collector',
                'description': 'Earn 1000 points this week',
                'challenge_type': 'weekly',
                'target_count': 1000,
                'target_type': 'points_earned',
                'points_reward': 200,
                'start_date': now,
                'end_date': now + timedelta(weeks=1)
            }
        ]
        
        # Monthly challenges
        monthly_challenges = [
            {
                'title': 'Monthly Marathon',
                'description': 'Process 100 receipts this month',
                'challenge_type': 'monthly',
                'target_count': 100,
                'target_type': 'receipts_processed',
                'points_reward': 1500,
                'badge_reward': 'Monthly Marathon Badge',
                'start_date': now,
                'end_date': now + timedelta(days=30)
            },
            {
                'title': 'Validation Veteran',
                'description': 'Validate 50 receipts this month',
                'challenge_type': 'monthly',
                'target_count': 50,
                'target_type': 'receipts_validated',
                'points_reward': 1000,
                'badge_reward': 'Validation Veteran Badge',
                'start_date': now,
                'end_date': now + timedelta(days=30)
            }
        ]
        
        # Create all challenges
        all_challenges = daily_challenges + weekly_challenges + monthly_challenges
        created_count = 0
        
        for challenge_data in all_challenges:
            challenge, created = Challenge.objects.get_or_create(
                title=challenge_data['title'],
                defaults=challenge_data
            )
            if created:
                created_count += 1
                self.stdout.write(f'Created challenge: {challenge.title}')
        
        self.stdout.write(f'Created {created_count} new challenges')
    
    def initialize_leaderboards(self):
        """Initialize leaderboard entries for active users"""
        now = timezone.now()
        
        # Get users with profiles
        profiles = UserProfile.objects.all()
        
        # Daily leaderboard
        daily_start = now.date()
        for profile in profiles:
            Leaderboard.objects.get_or_create(
                user=profile.user,
                period_type='daily',
                period_start=daily_start,
                defaults={
                    'period_end': daily_start,
                    'points_earned': 0,
                    'receipts_processed': 0,
                    'accuracy_score': 0.0
                }
            )
        
        # Weekly leaderboard
        weekly_start = now.date() - timedelta(days=now.weekday())
        weekly_end = weekly_start + timedelta(days=6)
        for profile in profiles:
            Leaderboard.objects.get_or_create(
                user=profile.user,
                period_type='weekly',
                period_start=weekly_start,
                defaults={
                    'period_end': weekly_end,
                    'points_earned': 0,
                    'receipts_processed': 0,
                    'accuracy_score': 0.0
                }
            )
        
        # Monthly leaderboard
        monthly_start = now.date().replace(day=1)
        # Calculate last day of month
        if now.month == 12:
            monthly_end = monthly_start.replace(year=now.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            monthly_end = monthly_start.replace(month=now.month + 1, day=1) - timedelta(days=1)
        
        for profile in profiles:
            Leaderboard.objects.get_or_create(
                user=profile.user,
                period_type='monthly',
                period_start=monthly_start,
                defaults={
                    'period_end': monthly_end,
                    'points_earned': 0,
                    'receipts_processed': 0,
                    'accuracy_score': 0.0
                }
            )
        
        # All-time leaderboard
        for profile in profiles:
            Leaderboard.objects.get_or_create(
                user=profile.user,
                period_type='all_time',
                period_start=profile.created_at.date(),
                defaults={
                    'period_end': None,
                    'points_earned': profile.total_points,
                    'receipts_processed': profile.receipts_processed,
                    'accuracy_score': profile.accuracy_score
                }
            )
        
        # Update ranks
        self.update_leaderboard_ranks()
        
        self.stdout.write('Leaderboards initialized')
    
    def update_leaderboard_ranks(self):
        """Update ranks for all leaderboard entries"""
        period_types = ['daily', 'weekly', 'monthly', 'all_time']
        
        for period_type in period_types:
            # Get latest period for each type
            latest_entry = Leaderboard.objects.filter(
                period_type=period_type
            ).order_by('-period_start').first()
            
            if latest_entry:
                # Get all entries for this period
                entries = Leaderboard.objects.filter(
                    period_type=period_type,
                    period_start=latest_entry.period_start
                ).order_by('-points_earned')
                
                # Update ranks
                for rank, entry in enumerate(entries, 1):
                    entry.rank = rank
                    entry.save()
                
                self.stdout.write(f'Updated {period_type} leaderboard ranks')