"""WIMM Django App Configuration - UNIBOS Module Integration"""
from django.apps import AppConfig
from pathlib import Path
import sys

class WimmConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'modules.wimm.backend'
    label = 'wimm'
    verbose_name = 'WIMM - Where Is My Money'
    
    def ready(self):
        self._add_sdk_to_path()
        self._initialize_module()
    
    def _add_sdk_to_path(self):
        try:
            module_dir = Path(__file__).resolve().parent.parent.parent.parent
            sdk_path = module_dir / 'shared' / 'python'
            if sdk_path.exists() and str(sdk_path) not in sys.path:
                sys.path.insert(0, str(sdk_path))
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Could not add SDK to path: {e}")
    
    def _initialize_module(self):
        try:
            from unibos_sdk import UnibosModule
            self.unibos_module = UnibosModule('wimm')
            import logging
            logging.getLogger(__name__).info(f"✓ Initialized UNIBOS module: wimm v{self.unibos_module.manifest.get('version')}")
            self.unibos_module.get_storage_path('invoices/')
            self.unibos_module.get_cache_path()
            self.unibos_module.get_logs_path()
        except ImportError as e:
            import logging
            logging.getLogger(__name__).warning(f"UNIBOS SDK not available: {e}")
