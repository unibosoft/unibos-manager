"""
CCTV Django App Configuration
Professional security camera management system

UNIBOS Module Integration
"""

from django.apps import AppConfig
from pathlib import Path
import sys


class CctvConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'modules.cctv.backend'
    label = 'cctv'
    verbose_name = 'CCTV - Security Cameras'

    def ready(self):
        """
        Initialize UNIBOS module and register signals
        """
        # Add shared SDK to Python path
        self._add_sdk_to_path()

        # Initialize UNIBOS module
        self._initialize_module()

        # Import and register signals (if any)
        # from . import signals  # noqa

    def _add_sdk_to_path(self):
        """Add UNIBOS SDK to Python path if not already there"""
        try:
            # Get project root (from modules/cctv/backend -> go up 3 levels)
            module_dir = Path(__file__).resolve().parent.parent.parent.parent
            sdk_path = module_dir / 'shared' / 'python'

            if sdk_path.exists() and str(sdk_path) not in sys.path:
                sys.path.insert(0, str(sdk_path))
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Could not add SDK to path: {e}")

    def _initialize_module(self):
        """Initialize UNIBOS module wrapper"""
        try:
            from unibos_sdk import UnibosModule

            # Initialize module
            self.unibos_module = UnibosModule('cctv')

            # Log initialization
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"✓ Initialized UNIBOS module: cctv v{self.unibos_module.manifest.get('version')}")

            # Ensure storage paths exist
            self.unibos_module.get_storage_path('recordings/')
            self.unibos_module.get_storage_path('snapshots/')
            self.unibos_module.get_storage_path('alerts/')
            self.unibos_module.get_storage_path('thumbnails/')
            self.unibos_module.get_cache_path()
            self.unibos_module.get_logs_path()

        except ImportError as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"UNIBOS SDK not available, running in legacy mode: {e}")