"""
Common MenuItem Factory
Centralized MenuItem definitions to eliminate code duplication across profiles

This module provides factory functions for MenuItem objects that are used across
multiple UNIBOS profiles (dev, server, manager, client/prod).

Benefits:
- DRY principle: Define once, use everywhere
- Consistency: Ensures consistent emoji spacing and descriptions
- i18n ready: Supports internationalization
- Easy maintenance: Update in one place
"""

from typing import Optional
from core.clients.cli.framework.ui import MenuItem


class CommonItems:
    """Factory class for creating common MenuItem objects"""

    @staticmethod
    def system_status(i18n=None, profile_type: str = 'generic') -> MenuItem:
        """
        System status menu item (used in all 4 profiles)

        Args:
            i18n: Internationalization object
            profile_type: Type of profile ('dev', 'server', 'manager', 'client')

        Returns:
            MenuItem for system status
        """
        # Profile-specific descriptions
        descriptions = {
            'dev': 'forge status & info\n\n'
                   '→ system information\n'
                   '→ version details\n'
                   '→ service status\n'
                   '→ resource usage\n\n'
                   'complete system overview',
            'server': 'cpu, memory, disk, uptime\n\n'
                      '→ CPU usage and load\n'
                      '→ Memory consumption\n'
                      '→ Disk space usage\n'
                      '→ System uptime\n\n'
                      'Complete system status',
            'manager': 'complete system status\n\n'
                       '→ Overall health\n'
                       '→ Service states\n'
                       '→ Resource usage\n'
                       '→ Recent activity\n\n'
                       'View complete system status',
            'client': 'device information\n\n'
                     '→ System health\n'
                     '→ Resource usage\n'
                     '→ Service status\n'
                     '→ Hardware info\n\n'
                     'View system status',
            'generic': 'system status and information\n\n'
                      '→ System health\n'
                      '→ Resource usage\n'
                      '→ Service status\n\n'
                      'View system status'
        }

        return MenuItem(
            id='system_status',
            label='💚 system status',
            icon='',
            description=descriptions.get(profile_type, descriptions['generic']),
            enabled=True
        )

    @staticmethod
    def database_setup(i18n=None, profile_type: str = 'dev') -> MenuItem:
        """
        Database setup menu item (primarily dev, but adaptable)

        Args:
            i18n: Internationalization object
            profile_type: Type of profile

        Returns:
            MenuItem for database setup
        """
        label = i18n.translate('menu.database') if i18n else '🗄️  database'

        if profile_type == 'dev':
            description = 'postgresql installer\n\n' \
                         '→ install postgresql\n' \
                         '→ create database\n' \
                         '→ run migrations\n' \
                         '→ configure access\n\n' \
                         'database installation wizard'
        elif profile_type == 'server':
            description = 'postgresql database service\n\n' \
                         '→ Database service status\n' \
                         '→ Connection monitoring\n' \
                         '→ Performance tuning\n' \
                         '→ Vacuum operations\n\n' \
                         'Manage PostgreSQL database'
        else:
            description = 'database management\n\n' \
                         '→ Database operations\n' \
                         '→ Configuration\n' \
                         '→ Monitoring\n\n' \
                         'Database tools'

        return MenuItem(
            id='database_setup' if profile_type == 'dev' else 'postgresql_service',
            label=label,
            icon='🗄️',
            description=description,
            enabled=True
        )

    @staticmethod
    def web_ui(i18n=None) -> MenuItem:
        """
        Web UI management menu item (dev profile)

        Args:
            i18n: Internationalization object

        Returns:
            MenuItem for web UI management
        """
        label = i18n.translate('menu.web_ui') if i18n else '🌐 web ui'

        return MenuItem(
            id='web_ui',
            label=label,
            icon='🌐',
            description='web interface manager\n\n'
                       '→ start django server\n'
                       '→ stop django server\n'
                       '→ view server logs\n'
                       '→ server configuration\n\n'
                       'web interface control',
            enabled=True
        )

    @staticmethod
    def administration(i18n=None) -> MenuItem:
        """
        Administration menu item (dev profile)

        Args:
            i18n: Internationalization object

        Returns:
            MenuItem for administration
        """
        label = i18n.translate('menu.admin') if i18n else '👑 admin'

        return MenuItem(
            id='administration',
            label=label,
            icon='👑',
            description='system administration\n\n'
                       '→ user management\n'
                       '→ permissions\n'
                       '→ system settings\n'
                       '→ configuration\n\n'
                       'administrative tools',
            enabled=True
        )

    @staticmethod
    def git_operations(i18n=None, menu_id: str = 'code_forge') -> MenuItem:
        """
        Git operations menu item (dev and manager profiles)

        Args:
            i18n: Internationalization object
            menu_id: ID for the menu item ('code_forge' for dev, 'git_status' for manager)

        Returns:
            MenuItem for git operations
        """
        if menu_id == 'code_forge':
            label = i18n.translate('menu.git') if i18n else '⚙️  git'
            description = 'version chronicles\n\n' \
                         '→ git operations\n' \
                         '→ version control\n' \
                         '→ commit history\n' \
                         '→ branch management\n\n' \
                         'source code management'
        else:  # git_status for manager
            label = '📦 git status'
            description = 'git repository status\n\n' \
                         '→ Current branch\n' \
                         '→ Uncommitted changes\n' \
                         '→ Remote sync status\n' \
                         '→ Recent commits\n\n' \
                         'View git repository status'

        return MenuItem(
            id=menu_id,
            label=label,
            icon='',
            description=description,
            enabled=True
        )

    @staticmethod
    def view_logs(profile_type: str = 'generic') -> MenuItem:
        """
        View logs menu item (server and manager profiles)

        Args:
            profile_type: Type of profile ('server', 'manager')

        Returns:
            MenuItem for viewing logs
        """
        if profile_type == 'server':
            description = 'application and system logs\n\n' \
                         '→ Django application logs\n' \
                         '→ Nginx access/error logs\n' \
                         '→ PostgreSQL logs\n' \
                         '→ System journal logs\n\n' \
                         'View server logs'
        elif profile_type == 'manager':
            description = 'view target logs\n\n' \
                         '→ Application logs\n' \
                         '→ Error logs\n' \
                         '→ Access logs\n' \
                         '→ System logs\n\n' \
                         'View logs from target server'
        else:
            description = 'system logs\n\n' \
                         '→ Application logs\n' \
                         '→ System logs\n' \
                         '→ Error logs\n\n' \
                         'View logs'

        return MenuItem(
            id='view_logs',
            label='📝 view logs',
            icon='',
            description=description,
            enabled=True
        )

    @staticmethod
    def backup_database(profile_type: str = 'generic') -> MenuItem:
        """
        Database backup menu item (server and manager profiles)

        Args:
            profile_type: Type of profile ('server', 'manager')

        Returns:
            MenuItem for database backup
        """
        if profile_type == 'server':
            description = 'backup database\n\n' \
                         '→ Create PostgreSQL dump\n' \
                         '→ Verify backup integrity\n' \
                         '→ Store backup file\n' \
                         '→ Backup rotation\n\n' \
                         'Create database backup'
        elif profile_type == 'manager':
            description = 'backup target database\n\n' \
                         '→ Create database backup\n' \
                         '→ Download to local\n' \
                         '→ Verify backup integrity\n' \
                         '→ Store backup info\n\n' \
                         'Create database backup'
        else:
            description = 'database backup\n\n' \
                         '→ Create backup\n' \
                         '→ Verify integrity\n\n' \
                         'Backup database'

        return MenuItem(
            id='backup_database',
            label='💾 database backup',
            icon='',
            description=description,
            enabled=True
        )

    @staticmethod
    def restart_services(profile_type: str = 'generic') -> MenuItem:
        """
        Restart services menu item (server and manager profiles)

        Args:
            profile_type: Type of profile ('server', 'manager')

        Returns:
            MenuItem for restarting services
        """
        if profile_type == 'server':
            description = 'full server restart\n\n' \
                         '→ Restart all services\n' \
                         '→ Graceful shutdown\n' \
                         '→ Service verification\n' \
                         '→ Health check\n\n' \
                         'Restart all server services'
            label = '🔄 restart all'
            item_id = 'restart_all'
        elif profile_type == 'manager':
            description = 'restart target services\n\n' \
                         '→ Restart web server\n' \
                         '→ Restart background workers\n' \
                         '→ Reload configurations\n' \
                         '→ Check service status\n\n' \
                         'Restart all services on target'
            label = '🔄 restart services'
            item_id = 'restart_services'
        else:
            description = 'restart services\n\n' \
                         '→ Restart all services\n\n' \
                         'Restart services'
            label = '🔄 restart'
            item_id = 'restart'

        return MenuItem(
            id=item_id,
            label=label,
            icon='',
            description=description,
            enabled=True
        )


# Convenience functions for quick access
def get_system_status(i18n=None, profile_type: str = 'generic') -> MenuItem:
    """Quick access to system status item"""
    return CommonItems.system_status(i18n, profile_type)


def get_database_setup(i18n=None, profile_type: str = 'dev') -> MenuItem:
    """Quick access to database setup item"""
    return CommonItems.database_setup(i18n, profile_type)


def get_web_ui(i18n=None) -> MenuItem:
    """Quick access to web UI item"""
    return CommonItems.web_ui(i18n)


def get_administration(i18n=None) -> MenuItem:
    """Quick access to administration item"""
    return CommonItems.administration(i18n)


def get_git_operations(i18n=None, menu_id: str = 'code_forge') -> MenuItem:
    """Quick access to git operations item"""
    return CommonItems.git_operations(i18n, menu_id)


def get_view_logs(profile_type: str = 'generic') -> MenuItem:
    """Quick access to view logs item"""
    return CommonItems.view_logs(profile_type)


def get_backup_database(profile_type: str = 'generic') -> MenuItem:
    """Quick access to backup database item"""
    return CommonItems.backup_database(profile_type)


def get_restart_services(profile_type: str = 'generic') -> MenuItem:
    """Quick access to restart services item"""
    return CommonItems.restart_services(profile_type)
