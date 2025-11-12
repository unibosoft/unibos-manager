"""
Management command to initialize UNIBOS Web UI
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from core.system.web_ui.backend.models import SystemStatus


class Command(BaseCommand):
    help = 'Initialize UNIBOS Web UI system status'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Initializing UNIBOS Web UI...'))
        
        # Initialize system status for each module
        modules = [
            ('recaria', 'Recaria Game Module'),
            ('birlikteyiz', 'Emergency Response System'),
            ('kisisel_enflasyon', 'Personal Inflation Tracker'),
            ('currencies', 'Currency Exchange System'),
            ('web_ui', 'Web Interface'),
            ('database', 'PostgreSQL Database'),
            ('websocket', 'WebSocket Server'),
        ]
        
        for module_id, description in modules:
            status, created = SystemStatus.objects.get_or_create(
                module=module_id,
                defaults={
                    'status': 'online',
                    'health_score': 100,
                    'error_count': 0,
                    'warning_count': 0,
                    'metadata': {
                        'description': description,
                        'initialized': timezone.now().isoformat()
                    }
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created status for {module_id}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠ Status for {module_id} already exists')
                )
        
        self.stdout.write(
            self.style.SUCCESS('\n✨ UNIBOS Web UI initialized successfully!')
        )
        self.stdout.write(
            self.style.SUCCESS('You can now access the web interface at http://localhost:8000/')
        )