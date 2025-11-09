"""
Management command for module operations

Usage:
    python manage.py modules list              # List all modules
    python manage.py modules sync              # Sync modules from disk
    python manage.py modules enable <id>       # Enable module
    python manage.py modules disable <id>      # Disable module
    python manage.py modules info <id>         # Show module info
    python manage.py modules stats             # Show statistics
"""

from django.core.management.base import BaseCommand
from core.backend.core_apps.module_registry.registry import module_registry
from core.backend.core_apps.module_registry.models import ModuleConfig


class Command(BaseCommand):
    help = 'Manage UNIBOS modules'

    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            choices=['list', 'sync', 'enable', 'disable', 'info', 'stats'],
            help='Action to perform'
        )
        parser.add_argument(
            'module_id',
            nargs='?',
            help='Module ID (for enable/disable/info actions)'
        )

    def handle(self, *args, **options):
        action = options['action']
        module_id = options.get('module_id')

        if action == 'list':
            self.list_modules()
        elif action == 'sync':
            self.sync_modules()
        elif action == 'enable':
            if not module_id:
                self.stderr.write('Error: module_id required for enable action')
                return
            self.enable_module(module_id)
        elif action == 'disable':
            if not module_id:
                self.stderr.write('Error: module_id required for disable action')
                return
            self.disable_module(module_id)
        elif action == 'info':
            if not module_id:
                self.stderr.write('Error: module_id required for info action')
                return
            self.show_module_info(module_id)
        elif action == 'stats':
            self.show_stats()

    def list_modules(self):
        """List all discovered modules"""
        self.stdout.write('\nUNIBOS Modules\n' + '=' * 80)

        modules = module_registry.get_all_modules()

        if not modules:
            self.stdout.write(self.style.WARNING('\nNo modules found.'))
            self.stdout.write('Run "python manage.py modules sync" to discover modules.\n')
            return

        enabled_modules = module_registry.get_enabled_modules()

        for module_id, manifest in sorted(modules.items()):
            enabled = module_id in enabled_modules
            status = self.style.SUCCESS('ENABLED ') if enabled else self.style.ERROR('DISABLED')

            icon = manifest.get('icon', '📦')
            name = manifest.get('name', module_id)
            version = manifest.get('version', '0.0.0')
            description = manifest.get('description', '')

            self.stdout.write(f'\n{status} {icon} {name} (ID: {module_id})')
            self.stdout.write(f'  Version: {version}')
            self.stdout.write(f'  Description: {description}')

        self.stdout.write(f'\n{"─" * 80}')
        self.stdout.write(f'Total: {len(modules)} modules '
                          f'({len(enabled_modules)} enabled, '
                          f'{len(modules) - len(enabled_modules)} disabled)\n')

    def sync_modules(self):
        """Sync modules from disk to database"""
        self.stdout.write('\nSyncing modules from disk...\n')

        module_registry.reload()
        module_registry.sync_to_database()

        modules = module_registry.get_all_modules()

        self.stdout.write(self.style.SUCCESS(f'\n✓ Successfully synced {len(modules)} modules\n'))

    def enable_module(self, module_id):
        """Enable a module"""
        try:
            config = ModuleConfig.objects.get(module_id=module_id)
            if config.enabled:
                self.stdout.write(self.style.WARNING(f'Module {module_id} is already enabled'))
                return

            config.enable()
            self.stdout.write(self.style.SUCCESS(f'✓ Enabled module: {module_id}'))

        except ModuleConfig.DoesNotExist:
            self.stderr.write(self.style.ERROR(f'Module not found: {module_id}'))
            self.stdout.write('Run "python manage.py modules sync" first.')

    def disable_module(self, module_id):
        """Disable a module"""
        try:
            config = ModuleConfig.objects.get(module_id=module_id)
            if not config.enabled:
                self.stdout.write(self.style.WARNING(f'Module {module_id} is already disabled'))
                return

            config.disable()
            self.stdout.write(self.style.SUCCESS(f'✓ Disabled module: {module_id}'))

        except ModuleConfig.DoesNotExist:
            self.stderr.write(self.style.ERROR(f'Module not found: {module_id}'))
            self.stdout.write('Run "python manage.py modules sync" first.')

    def show_module_info(self, module_id):
        """Show detailed module information"""
        manifest = module_registry.get_module(module_id)

        if not manifest:
            self.stderr.write(self.style.ERROR(f'Module not found: {module_id}'))
            return

        self.stdout.write(f'\n{manifest.get("icon", "📦")} {manifest.get("name")}\n')
        self.stdout.write('=' * 80)

        # Basic info
        self.stdout.write(f'\nID: {module_id}')
        self.stdout.write(f'Version: {manifest.get("version")}')
        self.stdout.write(f'Description: {manifest.get("description")}')
        if manifest.get('author'):
            self.stdout.write(f'Author: {manifest.get("author")}')

        # Capabilities
        caps = manifest.get('capabilities', {})
        if caps:
            self.stdout.write('\nCapabilities:')
            for cap, enabled in caps.items():
                status = '✓' if enabled else '✗'
                self.stdout.write(f'  {status} {cap}')

        # Dependencies
        deps = manifest.get('dependencies', {})
        if deps:
            self.stdout.write('\nDependencies:')
            for dep_type, dep_list in deps.items():
                if dep_list:
                    self.stdout.write(f'  {dep_type}: {", ".join(dep_list)}')

        # API
        api = manifest.get('api', {})
        if api:
            self.stdout.write('\nAPI:')
            self.stdout.write(f'  Base Path: {api.get("base_path", "N/A")}')
            endpoints = api.get('endpoints', [])
            if endpoints:
                self.stdout.write(f'  Endpoints: {len(endpoints)}')

        # Integration
        integration = manifest.get('integration', {})
        sidebar = integration.get('sidebar', {})
        if sidebar:
            self.stdout.write('\nSidebar Integration:')
            self.stdout.write(f'  Enabled: {sidebar.get("enabled", True)}')
            self.stdout.write(f'  Position: {sidebar.get("position", "N/A")}')
            self.stdout.write(f'  Category: {sidebar.get("category", "general")}')

        # Paths
        self.stdout.write(f'\nModule Path: {manifest.get("_module_path")}')
        self.stdout.write(f'Manifest Path: {manifest.get("_manifest_path")}')

        self.stdout.write('')

    def show_stats(self):
        """Show module statistics"""
        stats = module_registry.get_module_statistics()

        self.stdout.write('\nModule Statistics\n' + '=' * 80)

        self.stdout.write(f'\nTotal Modules: {stats["total"]}')
        self.stdout.write(f'Enabled: {self.style.SUCCESS(str(stats["enabled"]))}')
        self.stdout.write(f'Disabled: {self.style.ERROR(str(stats["disabled"]))}')

        if stats['categories']:
            self.stdout.write('\nBy Category:')
            for category, count in sorted(stats['categories'].items()):
                self.stdout.write(f'  {category}: {count}')

        self.stdout.write('')
