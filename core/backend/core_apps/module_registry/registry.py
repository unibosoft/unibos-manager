"""
UNIBOS Module Registry

Central registry for module discovery, loading, and management.
Singleton pattern for system-wide access.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


class ModuleRegistry:
    """
    Singleton registry for UNIBOS modules

    Handles:
    - Module discovery (scanning modules/ directory)
    - Manifest loading and validation
    - Module state tracking
    - URL route registration
    - Sidebar/navigation integration
    """

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._modules: Dict[str, Dict] = {}
            self._enabled_modules: Dict[str, Dict] = {}
            self._module_instances: Dict[str, Any] = {}
            self._initialized = True
            logger.info("ModuleRegistry initialized")

    def discover_modules(self, force_refresh: bool = False) -> Dict[str, Dict]:
        """
        Discover all modules in modules/ directory

        Scans for module.json files and loads module manifests.

        Args:
            force_refresh: Force re-discovery even if cached

        Returns:
            Dict of module_id -> manifest data
        """
        # Check cache first
        if not force_refresh and self._modules:
            return self._modules

        cache_key = 'unibos:module_registry:modules'
        if not force_refresh:
            cached = cache.get(cache_key)
            if cached:
                self._modules = cached
                self._update_enabled_modules()
                return self._modules

        logger.info("Discovering UNIBOS modules...")

        # Get modules directory
        modules_dir = self._get_modules_dir()

        if not modules_dir.exists():
            logger.warning(f"Modules directory not found: {modules_dir}")
            return {}

        discovered_modules = {}

        # Scan for module.json files
        for module_path in modules_dir.iterdir():
            if not module_path.is_dir():
                continue

            manifest_path = module_path / 'module.json'

            if not manifest_path.exists():
                logger.debug(f"No module.json found in {module_path.name}, skipping")
                continue

            try:
                # Load and parse manifest
                manifest = self._load_manifest(manifest_path)

                if not manifest:
                    continue

                module_id = manifest.get('id')

                if not module_id:
                    logger.warning(f"Module in {module_path} has no 'id' field")
                    continue

                # Store module data
                manifest['_manifest_path'] = str(manifest_path)
                manifest['_module_path'] = str(module_path)

                discovered_modules[module_id] = manifest

                logger.info(f"✓ Discovered module: {module_id} v{manifest.get('version', '0.0.0')}")

            except Exception as e:
                logger.error(f"Error loading module from {module_path}: {e}")
                continue

        self._modules = discovered_modules

        # Cache results
        cache.set(cache_key, discovered_modules, 3600)  # 1 hour

        # Update enabled modules
        self._update_enabled_modules()

        logger.info(f"Module discovery complete. Found {len(discovered_modules)} modules")

        return discovered_modules

    def _load_manifest(self, manifest_path: Path) -> Optional[Dict]:
        """
        Load and validate module manifest

        Args:
            manifest_path: Path to module.json

        Returns:
            Manifest dict or None if invalid
        """
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)

            # Basic validation
            required_fields = ['id', 'name', 'version', 'description', 'icon']
            for field in required_fields:
                if field not in manifest:
                    logger.error(f"Manifest {manifest_path} missing required field: {field}")
                    return None

            return manifest

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {manifest_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error reading {manifest_path}: {e}")
            return None

    def _update_enabled_modules(self):
        """Update cache of enabled modules from database"""
        try:
            # Import here to avoid circular dependency
            from .models import ModuleConfig

            enabled_configs = ModuleConfig.objects.filter(enabled=True)

            self._enabled_modules = {}

            for config in enabled_configs:
                if config.module_id in self._modules:
                    self._enabled_modules[config.module_id] = self._modules[config.module_id]

            logger.debug(f"Enabled modules: {len(self._enabled_modules)}")

        except Exception as e:
            logger.error(f"Error updating enabled modules: {e}")
            # If DB not ready, assume all discovered modules are enabled
            self._enabled_modules = self._modules.copy()

    def get_all_modules(self) -> Dict[str, Dict]:
        """
        Get all discovered modules

        Returns:
            Dict of module_id -> manifest
        """
        if not self._modules:
            self.discover_modules()

        return self._modules

    def get_enabled_modules(self) -> Dict[str, Dict]:
        """
        Get only enabled modules

        Returns:
            Dict of module_id -> manifest
        """
        if not self._modules:
            self.discover_modules()

        return self._enabled_modules

    def get_module(self, module_id: str) -> Optional[Dict]:
        """
        Get specific module manifest

        Args:
            module_id: Module identifier

        Returns:
            Module manifest or None
        """
        if not self._modules:
            self.discover_modules()

        return self._modules.get(module_id)

    def is_module_enabled(self, module_id: str) -> bool:
        """
        Check if module is enabled

        Args:
            module_id: Module identifier

        Returns:
            True if module is enabled
        """
        if not self._modules:
            self.discover_modules()

        return module_id in self._enabled_modules

    def get_sidebar_modules(self, user=None) -> List[Dict]:
        """
        Get modules for sidebar navigation

        Args:
            user: Optional user for permission checking

        Returns:
            List of module info dicts sorted by position
        """
        sidebar_modules = []

        for module_id, manifest in self.get_enabled_modules().items():
            integration = manifest.get('integration', {})
            sidebar_config = integration.get('sidebar', {})

            if not sidebar_config.get('enabled', True):
                continue

            # Check permissions if user provided
            if user:
                permissions = manifest.get('permissions', [])
                if permissions:
                    # Check if user has any of the required permissions
                    if not any(user.has_perm(perm) for perm in permissions):
                        continue

            sidebar_modules.append({
                'id': module_id,
                'name': manifest.get('name'),
                'icon': manifest.get('icon', '📦'),
                'position': sidebar_config.get('position', 999),
                'category': sidebar_config.get('category', 'general'),
                'url': f'/{module_id}/',
            })

        # Sort by position
        sidebar_modules.sort(key=lambda m: m['position'])

        return sidebar_modules

    def get_module_api_routes(self) -> Dict[str, str]:
        """
        Get API routes for all enabled modules

        Returns:
            Dict of module_id -> base_path
        """
        api_routes = {}

        for module_id, manifest in self.get_enabled_modules().items():
            api_config = manifest.get('api', {})
            base_path = api_config.get('base_path')

            if base_path:
                api_routes[module_id] = base_path

        return api_routes

    def sync_to_database(self):
        """
        Sync discovered modules to database

        Creates/updates ModuleConfig entries for all discovered modules.
        """
        try:
            from .models import ModuleConfig

            if not self._modules:
                self.discover_modules()

            for module_id, manifest in self._modules.items():
                config, created = ModuleConfig.objects.get_or_create(
                    module_id=module_id,
                    defaults={
                        'name': manifest.get('name'),
                        'version': manifest.get('version'),
                        'description': manifest.get('description', ''),
                        'icon': manifest.get('icon', ''),
                        'enabled': True,
                        'installed': True,
                        'config_json': manifest,
                        'manifest_path': manifest.get('_manifest_path', ''),
                        'module_path': manifest.get('_module_path', ''),
                    }
                )

                if not created:
                    # Update existing
                    config.update_from_manifest(manifest)
                    logger.debug(f"Updated module config: {module_id}")
                else:
                    config.mark_installed()
                    logger.info(f"Created module config: {module_id}")

            logger.info("Module database sync complete")

        except Exception as e:
            logger.error(f"Error syncing modules to database: {e}")

    def reload(self):
        """Force reload all modules from disk"""
        logger.info("Reloading module registry...")
        cache.delete('unibos:module_registry:modules')
        self._modules = {}
        self._enabled_modules = {}
        self._module_instances = {}
        self.discover_modules(force_refresh=True)
        self.sync_to_database()
        logger.info("Module registry reloaded")

    def _get_modules_dir(self) -> Path:
        """
        Get modules directory path

        Returns:
            Path to modules/ directory
        """
        # Try to get from settings
        if hasattr(settings, 'MODULES_DIR'):
            return Path(settings.MODULES_DIR)

        # Default: navigate from BASE_DIR
        base_dir = Path(settings.BASE_DIR)

        # From apps/web/backend -> go up to root, then modules/
        # BASE_DIR is apps/web/backend
        root_dir = base_dir.parent.parent.parent
        return root_dir / 'modules'

    def get_module_statistics(self) -> Dict:
        """
        Get module statistics

        Returns:
            Statistics dict
        """
        if not self._modules:
            self.discover_modules()

        total = len(self._modules)
        enabled = len(self._enabled_modules)
        disabled = total - enabled

        categories = {}
        for manifest in self._modules.values():
            integration = manifest.get('integration', {})
            sidebar = integration.get('sidebar', {})
            category = sidebar.get('category', 'general')
            categories[category] = categories.get(category, 0) + 1

        return {
            'total': total,
            'enabled': enabled,
            'disabled': disabled,
            'categories': categories,
        }


# Singleton instance
module_registry = ModuleRegistry()
