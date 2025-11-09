"""
Management command to setup OMDB API key
"""

from django.core.management.base import BaseCommand
from django.conf import settings
from cryptography.fernet import Fernet
import os
import getpass

from modules.movies.backend.omdb_models import APIKeyManager


class Command(BaseCommand):
    help = 'Setup OMDB API key for movies module'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--key',
            type=str,
            help='OMDB API key (will prompt if not provided)'
        )
        parser.add_argument(
            '--daily-limit',
            type=int,
            default=1000,
            help='Daily API request limit (default: 1000)'
        )
    
    def handle(self, *args, **options):
        # Get API key
        api_key = options['key']
        if not api_key:
            api_key = getpass.getpass('Enter OMDB API key: ')
        
        if not api_key:
            self.stdout.write(self.style.ERROR('API key is required'))
            return
        
        # Setup encryption key
        encryption_key_path = os.path.join(settings.BASE_DIR, '.movies_encryption_key')
        if not os.path.exists(encryption_key_path):
            self.stdout.write('Generating encryption key...')
            key = Fernet.generate_key()
            with open(encryption_key_path, 'wb') as f:
                f.write(key)
            os.chmod(encryption_key_path, 0o600)  # Secure the file
            settings.MOVIES_ENCRYPTION_KEY = key
        else:
            with open(encryption_key_path, 'rb') as f:
                settings.MOVIES_ENCRYPTION_KEY = f.read()
        
        # Create or update API key manager
        api_manager, created = APIKeyManager.objects.get_or_create(
            is_active=True,
            defaults={
                'key_name': 'OMDB API',
                'daily_limit': options['daily_limit']
            }
        )
        
        # Set the API key
        api_manager.set_api_key(api_key)
        api_manager.daily_limit = options['daily_limit']
        api_manager.save()
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'✅ API key created successfully'))
        else:
            self.stdout.write(self.style.SUCCESS(f'✅ API key updated successfully'))
        
        self.stdout.write(f'Daily limit: {api_manager.daily_limit} requests')
        self.stdout.write(f'Remaining today: {api_manager.remaining_requests} requests')
        
        # Test the API key
        self.stdout.write('\nTesting API key...')
        from modules.movies.backend.omdb_service import OMDBService
        
        try:
            service = OMDBService()
            result = service.search_movies('The Matrix')
            
            if result.get('Response') == 'True':
                self.stdout.write(self.style.SUCCESS('✅ API key is working!'))
                self.stdout.write(f"Found {result.get('totalResults', 0)} results for 'The Matrix'")
            else:
                self.stdout.write(self.style.WARNING('⚠️ API returned an error:'))
                self.stdout.write(result.get('Error', 'Unknown error'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error testing API: {e}'))