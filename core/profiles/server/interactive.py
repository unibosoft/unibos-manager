"""
UNIBOS-SERVER Interactive Mode
Interactive TUI mode for server CLI

Implements server-specific menu structure and actions for:
- Production server management (rocksteady)
- Service monitoring and health checks
- Distributed node coordination
- Central API management
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.clients.cli.framework.interactive import InteractiveMode
from core.clients.cli.framework.ui import MenuItem, Colors
from core.version import __version__


class UnibosServerInteractive(InteractiveMode):
    """
    Interactive mode for unibos-server CLI

    Provides TUI interface for production server operations:
    - Service management (django, postgresql, redis, celery)
    - Health monitoring
    - Node registry and coordination
    - Backup and maintenance
    """

    def __init__(self):
        super().__init__(
            title="unibos server",
            version=__version__
        )

    def get_sections(self):
        """
        Get menu sections for unibos-server

        Returns:
            List of section dicts with menu items
        """
        return [
            {
                'id': 'services',
                'label': 'services',
                'icon': '�',
                'items': [
                    MenuItem(
                        id='service_status',
                        label='service status',
                        icon='=�',
                        description='show status of all services (django, postgres, redis, celery)'
                    ),
                    MenuItem(
                        id='service_restart',
                        label='restart services',
                        icon='=',
                        description='restart all or specific services'
                    ),
                    MenuItem(
                        id='service_logs',
                        label='view logs',
                        icon='=�',
                        description='view service logs (django, gunicorn, celery)'
                    ),
                    MenuItem(
                        id='service_health',
                        label='health check',
                        icon='<�',
                        description='comprehensive health check (database, redis, disk, memory)'
                    ),
                ]
            },
            {
                'id': 'nodes',
                'label': 'node registry',
                'icon': '<',
                'items': [
                    MenuItem(
                        id='nodes_list',
                        label='list nodes',
                        icon='=�',
                        description='show all registered nodes in the network'
                    ),
                    MenuItem(
                        id='nodes_health',
                        label='node health',
                        icon='=�',
                        description='health status of all connected nodes'
                    ),
                    MenuItem(
                        id='nodes_sync',
                        label='sync status',
                        icon='=',
                        description='synchronization status with each node'
                    ),
                ]
            },
            {
                'id': 'database',
                'label': 'database',
                'icon': '=�',
                'items': [
                    MenuItem(
                        id='db_backup',
                        label='create backup',
                        icon='=�',
                        description='create postgresql backup'
                    ),
                    MenuItem(
                        id='db_restore',
                        label='restore backup',
                        icon='=�',
                        description='restore from backup file'
                    ),
                    MenuItem(
                        id='db_migrate',
                        label='run migrations',
                        icon='=',
                        description='apply pending database migrations'
                    ),
                    MenuItem(
                        id='db_vacuum',
                        label='vacuum database',
                        icon='>�',
                        description='optimize postgresql performance'
                    ),
                ]
            },
            {
                'id': 'monitoring',
                'label': 'monitoring',
                'icon': '=�',
                'items': [
                    MenuItem(
                        id='mon_stats',
                        label='system stats',
                        icon='=�',
                        description='cpu, memory, disk usage'
                    ),
                    MenuItem(
                        id='mon_connections',
                        label='active connections',
                        icon='=',
                        description='active database and network connections'
                    ),
                    MenuItem(
                        id='mon_performance',
                        label='performance metrics',
                        icon='�',
                        description='request rate, response time, cache hits'
                    ),
                ]
            }
        ]

    def handle_action(self, item: MenuItem) -> bool:
        """
        Handle menu item action

        Args:
            item: Selected menu item

        Returns:
            True to continue menu loop, False to exit
        """
        import subprocess
        import os
        from core.clients.cli.framework.ui import clear_screen, Colors

        clear_screen()
        print(f"{Colors.ORANGE}{Colors.BOLD}� {item.label}{Colors.RESET}\n")

        try:
            # Service management
            if item.id == 'service_status':
                print(f"{Colors.DIM}checking service status...{Colors.RESET}\n")
                subprocess.run(['systemctl', 'status', 'gunicorn', 'redis', 'celery', 'postgresql'], check=False)

            elif item.id == 'service_restart':
                print(f"{Colors.YELLOW}restart which service? (all/django/redis/celery):{Colors.RESET} ", end='')
                service = input().strip().lower()
                if service in ['all', 'django', 'redis', 'celery']:
                    if service == 'all':
                        subprocess.run(['sudo', 'systemctl', 'restart', 'gunicorn', 'redis', 'celery'], check=True)
                    elif service == 'django':
                        subprocess.run(['sudo', 'systemctl', 'restart', 'gunicorn'], check=True)
                    else:
                        subprocess.run(['sudo', 'systemctl', 'restart', service], check=True)

            elif item.id == 'service_logs':
                print(f"{Colors.YELLOW}which logs? (django/gunicorn/celery/all):{Colors.RESET} ", end='')
                log_type = input().strip().lower()
                if log_type == 'django':
                    subprocess.run(['tail', '-f', '/var/log/django/django.log'], check=False)
                elif log_type == 'gunicorn':
                    subprocess.run(['sudo', 'journalctl', '-u', 'gunicorn', '-f'], check=False)
                elif log_type == 'celery':
                    subprocess.run(['sudo', 'journalctl', '-u', 'celery', '-f'], check=False)

            elif item.id == 'service_health':
                subprocess.run(['unibos-server', 'health'], check=True)

            # Node management
            elif item.id == 'nodes_list':
                print(f"{Colors.CYAN}registered nodes:{Colors.RESET}\n")
                # TODO: Implement node registry query
                print(f"{Colors.DIM}node registry not yet implemented{Colors.RESET}")

            # Database management
            elif item.id == 'db_backup':
                subprocess.run(['unibos-server', 'db', 'backup'], check=True)

            elif item.id == 'db_migrate':
                subprocess.run(['unibos-server', 'db', 'migrate'], check=True)

            # Monitoring
            elif item.id == 'mon_stats':
                subprocess.run(['unibos-server', 'stats'], check=True)

            else:
                print(f"{Colors.YELLOW}� action not yet implemented: {item.id}{Colors.RESET}")

        except subprocess.CalledProcessError as e:
            print(f"\n{Colors.RED}L command failed with exit code {e.returncode}{Colors.RESET}")
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}� interrupted{Colors.RESET}")
        except Exception as e:
            print(f"\n{Colors.RED}L error: {e}{Colors.RESET}")

        # Pause before returning to menu
        print(f"\n{Colors.DIM}press enter to continue...{Colors.RESET}")
        input()

        return True  # Continue menu loop


def run_interactive():
    """Run unibos-server in interactive mode"""
    interactive = UnibosServerInteractive()
    interactive.run(show_splash=True)
