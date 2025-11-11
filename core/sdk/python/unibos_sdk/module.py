"""
UNIBOS Module Base Class
Provides standardized module initialization and metadata management
"""

import logging
from pathlib import Path
import json
from typing import Optional, Dict, Any


class UnibosModule:
    """
    Base class for UNIBOS modules
    Handles module registration, initialization, and lifecycle management
    """

    def __init__(self, module_id: str):
        """
        Initialize UNIBOS module

        Args:
            module_id: Unique identifier for the module (e.g., 'core', 'wimm', 'birlikteyiz')
        """
        self.module_id = module_id
        self.logger = logging.getLogger(f"unibos.modules.{module_id}")
        self.manifest = self._load_manifest()

    def _load_manifest(self) -> Dict[str, Any]:
        """
        Load module manifest from module.json file

        Returns:
            Dictionary containing module metadata
        """
        try:
            # Try to find module.json in the module directory
            # Assuming module structure: modules/{module_id}/module.json
            possible_paths = [
                Path(f"modules/{self.module_id}/module.json"),
                Path(f"../../../modules/{self.module_id}/module.json"),
            ]

            for manifest_path in possible_paths:
                if manifest_path.exists():
                    with open(manifest_path, 'r') as f:
                        return json.load(f)

            # If no manifest found, return minimal default
            self.logger.debug(f"No manifest found for module '{self.module_id}', using defaults")
            return {
                "id": self.module_id,
                "version": "0.0.0",
                "name": self.module_id.title()
            }

        except Exception as e:
            self.logger.warning(f"Error loading manifest for module '{self.module_id}': {e}")
            return {
                "id": self.module_id,
                "version": "0.0.0",
                "name": self.module_id.title()
            }

    def initialize(self) -> None:
        """
        Initialize module resources
        Override this method in subclasses for custom initialization logic
        """
        pass

    def shutdown(self) -> None:
        """
        Cleanup module resources
        Override this method in subclasses for custom cleanup logic
        """
        pass

    def get_metadata(self) -> Dict[str, Any]:
        """
        Get module metadata

        Returns:
            Dictionary containing module metadata from manifest
        """
        return self.manifest

    def get_storage_path(self, subpath: str = '') -> Path:
        """
        Get module-specific storage path

        Args:
            subpath: Optional subdirectory within module storage

        Returns:
            Path object for module storage location
        """
        from pathlib import Path
        from django.conf import settings

        # Module storage: data/modules/{module_id}/{subpath}
        module_storage = Path(settings.DATA_DIR) / 'modules' / self.module_id / subpath
        module_storage.mkdir(parents=True, exist_ok=True)
        return module_storage

    def get_cache_path(self) -> Path:
        """
        Get module-specific cache directory

        Returns:
            Path object for module cache location
        """
        return self.get_storage_path('cache')

    def get_logs_path(self) -> Path:
        """
        Get module-specific logs directory

        Returns:
            Path object for module logs location
        """
        return self.get_storage_path('logs')

    def __repr__(self) -> str:
        return f"UnibosModule(id={self.module_id}, version={self.manifest.get('version', 'unknown')})"
