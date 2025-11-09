"""
UNIBOS SDK Base Classes

Abstract base classes that all UNIBOS modules must implement.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional


class UnibosSdkBase(ABC):
    """
    Abstract base class for all UNIBOS modules

    All modules must inherit from this class and implement its abstract methods.
    This ensures a consistent interface across all modules.

    Example:
        class MyModule(UnibosSdkBase):
            def get_manifest(self) -> Dict:
                return self._load_manifest('my_module')

            def initialize(self):
                # Module initialization logic
                pass

            def get_api_routes(self) -> List:
                return [
                    {'path': '/api/v1/mymodule/', 'view': 'mymodule.api_views'}
                ]
    """

    @abstractmethod
    def get_manifest(self) -> Dict:
        """
        Return module manifest (from module.json)

        Returns:
            Dict containing module metadata:
            - id: Module unique identifier
            - name: Module display name
            - version: Semantic version (e.g., "1.0.0")
            - description: Short description
            - icon: Emoji icon
            - capabilities: Dict of module capabilities
            - dependencies: List of required modules
            - etc.
        """
        pass

    @abstractmethod
    def initialize(self):
        """
        Initialize module

        Called when the module is loaded by UNIBOS.
        Use this to set up any required resources, connections, etc.

        Example:
            def initialize(self):
                self.setup_database()
                self.register_event_listeners()
                self.start_background_tasks()
        """
        pass

    @abstractmethod
    def get_api_routes(self) -> List:
        """
        Return module API routes for URL routing

        Returns:
            List of dicts with route information:
            [
                {
                    'path': '/api/v1/mymodule/',
                    'view': 'mymodule.api_views',
                    'name': 'mymodule-api'
                }
            ]
        """
        pass

    def get_required_permissions(self) -> List[str]:
        """
        Return required permissions for this module

        Returns:
            List of permission strings (e.g., ['mymodule.view', 'mymodule.edit'])
        """
        return []

    def on_install(self):
        """
        Called when module is first installed

        Use this to create initial database tables, create default data, etc.
        This is called only once, during module installation.
        """
        pass

    def on_uninstall(self):
        """
        Called when module is uninstalled

        Use this to clean up resources, remove database tables, etc.
        WARNING: This will permanently remove module data!
        """
        pass

    def on_upgrade(self, old_version: str, new_version: str):
        """
        Called when module is upgraded

        Args:
            old_version: Previous module version
            new_version: New module version

        Use this to migrate data, update database schema, etc.
        """
        pass

    def on_enable(self):
        """
        Called when module is enabled

        Use this to start services, register event listeners, etc.
        """
        pass

    def on_disable(self):
        """
        Called when module is disabled

        Use this to stop services, unregister event listeners, etc.
        """
        pass

    def health_check(self) -> Dict:
        """
        Perform module health check

        Returns:
            Dict with health status:
            {
                'status': 'healthy' | 'degraded' | 'unhealthy',
                'checks': {
                    'database': 'ok',
                    'api': 'ok',
                    'cache': 'degraded'
                },
                'message': 'Optional status message'
            }
        """
        return {
            'status': 'healthy',
            'checks': {},
            'message': 'Health check not implemented'
        }
