"""
Management command to clean up old solitaire sessions

NOTE: This is OPTIONAL. By default, games remain active until the player
explicitly starts a new game or wins. This command can be used for 
maintenance if needed to clean up very old abandoned sessions.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from modules.solitaire.backend.models import SolitaireGameSession


class Command(BaseCommand):
    help = 'Clean up old in-progress solitaire sessions and mark them as abandoned'

    def add_arguments(self, parser):
        parser.add_argument(
            '--hours',
            type=int,
            default=24,
            help='Mark sessions older than this many hours as abandoned (default: 24)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes'
        )

    def handle(self, *args, **options):
        hours = options['hours']
        dry_run = options['dry_run']
        
        # Find old in-progress sessions
        cutoff_time = timezone.now() - timedelta(hours=hours)
        
        old_sessions = SolitaireGameSession.objects.filter(
            is_completed=False,
            is_won=False,
            is_abandoned=False,
            started_at__lt=cutoff_time
        )
        
        count = old_sessions.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('No old sessions to clean up'))
            return
        
        self.stdout.write(f'Found {count} old in-progress sessions older than {hours} hours')
        
        if not dry_run:
            # Mark them as abandoned
            old_sessions.update(
                is_abandoned=True,
                ended_at=timezone.now()
            )
            self.stdout.write(self.style.SUCCESS(f'Marked {count} sessions as abandoned'))
        else:
            self.stdout.write(self.style.WARNING(f'DRY RUN: Would mark {count} sessions as abandoned'))
            
            # Show some details
            for session in old_sessions[:10]:  # Show first 10
                self.stdout.write(
                    f'  - Session {session.session_id[:8]}... by {session.player.display_name} '
                    f'started {session.started_at}'
                )