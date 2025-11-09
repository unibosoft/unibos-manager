"""
Management command to set API keys for AI services
"""

from django.core.management.base import BaseCommand
from django.conf import settings
import json
import os
from pathlib import Path

class Command(BaseCommand):
    help = 'Set API keys for AI services (Hugging Face, Mistral, etc.)'
    
    # API keys file location
    KEYS_FILE = Path(settings.BASE_DIR) / '.api_keys.json'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--huggingface',
            type=str,
            help='Set Hugging Face API key'
        )
        parser.add_argument(
            '--mistral',
            type=str,
            help='Set Mistral API key'
        )
        parser.add_argument(
            '--show',
            action='store_true',
            help='Show current API keys (masked)'
        )
        parser.add_argument(
            '--test',
            action='store_true',
            help='Test API keys'
        )
    
    def handle(self, *args, **options):
        # Load existing keys
        keys = self.load_keys()
        
        # Show current keys
        if options['show']:
            self.show_keys(keys)
            return
        
        # Set Hugging Face key
        if options['huggingface']:
            keys['HUGGINGFACE_API_KEY'] = options['huggingface']
            self.stdout.write(self.style.SUCCESS('✅ Hugging Face API key set'))
            
            # Also set as environment variable for current session
            os.environ['HUGGINGFACE_API_KEY'] = options['huggingface']
        
        # Set Mistral key
        if options['mistral']:
            keys['MISTRAL_API_KEY'] = options['mistral']
            self.stdout.write(self.style.SUCCESS('✅ Mistral API key set'))
            os.environ['MISTRAL_API_KEY'] = options['mistral']
        
        # Save keys
        if options['huggingface'] or options['mistral']:
            self.save_keys(keys)
            self.stdout.write(self.style.SUCCESS(f'\n📁 Keys saved to: {self.KEYS_FILE}'))
            self.stdout.write(self.style.WARNING('⚠️  Added .api_keys.json to .gitignore'))
        
        # Test keys
        if options['test']:
            self.test_keys(keys)
    
    def load_keys(self):
        """Load API keys from file"""
        if self.KEYS_FILE.exists():
            try:
                with open(self.KEYS_FILE, 'r') as f:
                    keys = json.load(f)
                    # Set as environment variables
                    for key, value in keys.items():
                        os.environ[key] = value
                    return keys
            except:
                return {}
        return {}
    
    def save_keys(self, keys):
        """Save API keys to file"""
        with open(self.KEYS_FILE, 'w') as f:
            json.dump(keys, f, indent=2)
        
        # Ensure it's in .gitignore
        gitignore_path = Path(settings.BASE_DIR).parent / '.gitignore'
        if gitignore_path.exists():
            with open(gitignore_path, 'r') as f:
                content = f.read()
            if '.api_keys.json' not in content:
                with open(gitignore_path, 'a') as f:
                    f.write('\n# API Keys\n.api_keys.json\n')
    
    def show_keys(self, keys):
        """Show current API keys (masked)"""
        self.stdout.write('\n=== Current API Keys ===\n')
        
        if not keys:
            self.stdout.write(self.style.WARNING('No API keys configured'))
            return
        
        for key_name, key_value in keys.items():
            if key_value:
                # Mask the key (show first 7 and last 4 characters)
                if len(key_value) > 15:
                    masked = f"{key_value[:7]}...{key_value[-4:]}"
                else:
                    masked = "***"
                self.stdout.write(f"{key_name}: {masked}")
            else:
                self.stdout.write(f"{key_name}: Not set")
    
    def test_keys(self, keys):
        """Test API keys"""
        self.stdout.write('\n=== Testing API Keys ===\n')
        
        # Test Hugging Face
        if keys.get('HUGGINGFACE_API_KEY'):
            try:
                import requests
                headers = {"Authorization": f"Bearer {keys['HUGGINGFACE_API_KEY']}"}
                response = requests.get(
                    "https://huggingface.co/api/whoami",
                    headers=headers,
                    timeout=5
                )
                if response.status_code == 200:
                    data = response.json()
                    self.stdout.write(self.style.SUCCESS(
                        f"✅ Hugging Face: Valid (User: {data.get('name', 'Unknown')})"
                    ))
                else:
                    self.stdout.write(self.style.ERROR(
                        f"❌ Hugging Face: Invalid key"
                    ))
            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f"❌ Hugging Face test failed: {str(e)}"
                ))
        else:
            self.stdout.write("⚠️  Hugging Face: No key configured")
        
        # Test Mistral
        if keys.get('MISTRAL_API_KEY'):
            self.stdout.write("ℹ️  Mistral: Key set (requires paid account to test)")
        else:
            self.stdout.write("⚠️  Mistral: No key configured")