"""
Web UI Django App Configuration
Terminal-style web interface for UNIBOS

UNIBOS Module Integration
"""

from django.apps import AppConfig
from pathlib import Path
import sys


class WebUiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'modules.web_ui.backend'
    label = 'web_ui'
    verbose_name = 'Web UI - Terminal Interface'

    def ready(self):
        """
        Initialize UNIBOS module
        """
        # Add shared SDK to Python path
        self._add_sdk_to_path()

        # Initialize UNIBOS module
        self._initialize_module()

    def _add_sdk_to_path(self):
        """Add UNIBOS SDK to Python path if not already there"""
        try:
            # Get project root (from modules/web_ui/backend -> go up 3 levels)
            module_dir = Path(__file__).resolve().parent.parent.parent.parent
            sdk_path = module_dir / 'platform' / 'sdk' / 'python'

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
            self.unibos_module = UnibosModule('web_ui')

            # Log initialization
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"✓ Initialized UNIBOS module: web_ui v{self.unibos_module.manifest.get('version')}")

        except ImportError as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"UNIBOS SDK not available, running in legacy mode: {e}")