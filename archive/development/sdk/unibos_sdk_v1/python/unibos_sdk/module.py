"""
UNIBOS Module Wrapper

Main wrapper class that modules should use to integrate with UNIBOS.
"""

import json
from pathlib import Path
from typing import Dict, Optional
from .base import UnibosSdkBase


class UnibosModule(UnibosSdkBase):
    """
    UNIBOS Module wrapper class

    This is the main class that modules should inherit from.
    It provides all the necessary functionality to integrate with UNIBOS.

    Usage:
        from unibos_sdk import UnibosModule

        class BirlikteyizModule(UnibosModule):
            def __init__(self):
                super().__init__('birlikteyiz')
    """

    def __init__(self, module_id: str):
        """
        Initialize UNIBOS module

        Args:
            module_id: Unique module identifier (e.g., 'birlikteyiz', 'currencies')
        """
        self.module_id = module_id
        self.manifest = self.load_manifest()
        self.config = self.load_config()
        self._initialized = False

    def load_manifest(self) -> Dict:
        """
        Load module.json manifest file

        Returns:
            Dict containing module manifest

        Raises:
            FileNotFoundError: If module.json not found
            json.JSONDecodeError: If module.json is invalid JSON
        """
        module_dir = self._get_module_directory()
        manifest_path = module_dir / 'module.json'

        if not manifest_path.exists():
            raise FileNotFoundError(
                f"module.json not found for module '{self.module_id}' at {manifest_path}"
            )

        with open(manifest_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def load_config(self) -> Dict:
        """
        Load module configuration from database

        Returns:
            Dict containing module configuration
        """
        # This will be implemented later when ModuleRegistry is ready
        return {}

    def _get_module_directory(self) -> Path:
        """
        Get module's root directory

        Returns:
            Path to module directory
        """
        # Assume we're being called from within the module
        # modules/<module_id>/
        current_file = Path(__file__).resolve()
        # Navigate up to find modules directory
        unibos_root = current_file.parent.parent.parent.parent
        module_dir = unibos_root / 'modules' / self.module_id

        if not module_dir.exists():
            raise FileNotFoundError(
                f"Module directory not found: {module_dir}"
            )

        return module_dir

    def get_storage_path(self, subpath: str = '') -> Path:
        """
        Get module-specific storage path in Universal Data Directory

        Args:
            subpath: Optional subdirectory within module storage

        Returns:
            Path to module storage directory

        Example:
            storage = module.get_storage_path('earthquakes')
            # Returns: /data/runtime/media/modules/birlikteyiz/earthquakes/
        """
        unibos_root = self._get_unibos_root()
        data_dir = unibos_root / 'data'
        module_storage = data_dir / 'runtime' / 'media' / 'modules' / self.module_id

        # Create directory if it doesn't exist
        module_storage.mkdir(parents=True, exist_ok=True)

        if subpath:
            full_path = module_storage / subpath
            full_path.mkdir(parents=True, exist_ok=True)
            return full_path

        return module_storage

    def get_cache_path(self) -> Path:
        """
        Get module-specific cache path

        Returns:
            Path to module cache directory

        Example:
            cache = module.get_cache_path()
            # Returns: /data/runtime/cache/birlikteyiz/
        """
        unibos_root = self._get_unibos_root()
        data_dir = unibos_root / 'data'
        cache_path = data_dir / 'runtime' / 'cache' / self.module_id

        # Create directory if it doesn't exist
        cache_path.mkdir(parents=True, exist_ok=True)

        return cache_path

    def get_logs_path(self) -> Path:
        """
        Get module-specific logs path

        Returns:
            Path to module logs directory

        Example:
            logs = module.get_logs_path()
            # Returns: /data/runtime/logs/modules/birlikteyiz/
        """
        unibos_root = self._get_unibos_root()
        data_dir = unibos_root / 'data'
        logs_path = data_dir / 'runtime' / 'logs' / 'modules' / self.module_id

        # Create directory if it doesn't exist
        logs_path.mkdir(parents=True, exist_ok=True)

        return logs_path

    def _get_unibos_root(self) -> Path:
        """
        Get UNIBOS root directory

        Returns:
            Path to UNIBOS root
        """
        current_file = Path(__file__).resolve()
        # shared/python/unibos_sdk/module.py -> go up 4 levels to root
        return current_file.parent.parent.parent.parent

    # Implement abstract methods from UnibosSdkBase

    def get_manifest(self) -> Dict:
        """Return loaded manifest"""
        return self.manifest

    def initialize(self):
        """
        Initialize module

        Override this in your module class to add custom initialization.
        """
        if self._initialized:
            return

        # Default initialization
        self._initialized = True

    def get_api_routes(self) -> list:
        """
        Get module API routes from manifest

        Returns:
            List of route configurations
        """
        api_config = self.manifest.get('api', {})
        base_path = api_config.get('base_path', f'/api/v1/{self.module_id}/')

        return [{
            'path': base_path,
            'view': f'modules.{self.module_id}.backend.urls',
            'name': f'{self.module_id}-api'
        }]

    def get_required_permissions(self) -> list:
        """Get required permissions from manifest"""
        return self.manifest.get('permissions', [])

    def __repr__(self):
        return f"<UnibosModule: {self.module_id} v{self.manifest.get('version', 'unknown')}>"
