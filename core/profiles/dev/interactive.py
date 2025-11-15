"""
UNIBOS-DEV Interactive Mode
Interactive TUI mode for development CLI

Implements development-specific menu structure and actions
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.clients.cli.framework.interactive import InteractiveMode
from core.clients.cli.framework.ui import MenuItem, Colors
from core.version import __version__


class UnibosDevInteractive(InteractiveMode):
    """
    Interactive mode for unibos-dev CLI

    Provides TUI interface for development operations:
    - Development server management
    - Git workflows and deployment
    - Database operations
    - Platform management
    """

    def __init__(self):
        super().__init__(
            title="unibos development",
            version=__version__
        )

    def get_sections(self):
        """
        Get menu sections for unibos-dev

        Returns:
            List of section dicts with menu items
        """
        return [
            {
                'id': 'dev',
                'label': 'development',
                'icon': '🔧',
                'items': [
                    MenuItem(
                        id='dev_run',
                        label='start development server',
                        icon='▶️',
                        description='start django development server with hot reload\n\nRuns: python manage.py runserver 0.0.0.0:8000'
                    ),
                    MenuItem(
                        id='dev_stop',
                        label='stop development server',
                        icon='⏹️',
                        description='stop running development server'
                    ),
                    MenuItem(
                        id='dev_status',
                        label='show status',
                        icon='📊',
                        description='display system status, services, and module information'
                    ),
                    MenuItem(
                        id='dev_shell',
                        label='django shell',
                        icon='🐚',
                        description='open django interactive shell for debugging'
                    ),
                ]
            },
            {
                'id': 'git',
                'label': 'git & deploy',
                'icon': '🚀',
                'items': [
                    MenuItem(
                        id='git_status',
                        label='git status',
                        icon='📋',
                        description='show current git repository status'
                    ),
                    MenuItem(
                        id='git_setup',
                        label='setup git remotes',
                        icon='🔧',
                        description='configure git remotes for 3-repo architecture\n\ndev, server, prod repositories'
                    ),
                    MenuItem(
                        id='git_push_all',
                        label='push to all repos',
                        icon='🌐',
                        description='push to all 3 repositories\n\nautomatically switches .gitignore templates\ndev → server → prod'
                    ),
                    MenuItem(
                        id='git_push_dev',
                        label='push to dev',
                        icon='⬆️',
                        description='push to development repository only\n\nRepo: github.com/unibosoft/unibos-dev'
                    ),
                    MenuItem(
                        id='git_push_server',
                        label='push to server',
                        icon='🖥️',
                        description='push to server repository only\n\nRepo: github.com/unibosoft/unibos-server'
                    ),
                    MenuItem(
                        id='git_push_prod',
                        label='push to prod',
                        icon='📦',
                        description='push to production repository only\n\nRepo: github.com/unibosoft/unibos'
                    ),
                    MenuItem(
                        id='deploy_rocksteady',
                        label='deploy to rocksteady',
                        icon='🎯',
                        description='deploy to rocksteady production server\n\nfull deployment with migrations, static files, and service restart'
                    ),
                ]
            },
            {
                'id': 'database',
                'label': 'database',
                'icon': '🗄️',
                'items': [
                    MenuItem(
                        id='db_backup',
                        label='create backup',
                        icon='💾',
                        description='create database backup to archive/database_backups/'
                    ),
                    MenuItem(
                        id='db_restore',
                        label='restore backup',
                        icon='📥',
                        description='restore database from backup file'
                    ),
                    MenuItem(
                        id='db_migrate',
                        label='run migrations',
                        icon='🔄',
                        description='apply pending database migrations'
                    ),
                    MenuItem(
                        id='db_makemigrations',
                        label='make migrations',
                        icon='📝',
                        description='generate new migration files from model changes'
                    ),
                ]
            },
            {
                'id': 'platform',
                'label': 'platform',
                'icon': '🌐',
                'items': [
                    MenuItem(
                        id='platform_modules',
                        label='list modules',
                        icon='📦',
                        description='show all registered modules and their status'
                    ),
                    MenuItem(
                        id='platform_config',
                        label='show configuration',
                        icon='⚙️',
                        description='display current platform configuration'
                    ),
                    MenuItem(
                        id='platform_identity',
                        label='node identity',
                        icon='🔐',
                        description='show node identity and persistence information'
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
        print(f"{Colors.ORANGE}{Colors.BOLD}▶ {item.label}{Colors.RESET}\n")

        try:
            if item.id == 'dev_run':
                print(f"{Colors.DIM}Starting development server...{Colors.RESET}\n")
                subprocess.run(['unibos-dev', 'dev', 'run'], check=True)

            elif item.id == 'dev_stop':
                print(f"{Colors.DIM}Stopping development server...{Colors.RESET}\n")
                subprocess.run(['unibos-dev', 'dev', 'stop'], check=True)

            elif item.id == 'dev_status':
                subprocess.run(['unibos-dev', 'status'], check=True)

            elif item.id == 'dev_shell':
                print(f"{Colors.DIM}Opening Django shell...{Colors.RESET}\n")
                # Change to web directory and run shell
                web_dir = project_root / 'core' / 'web'
                os.chdir(web_dir)
                subprocess.run([
                    'python',
                    'manage.py',
                    'shell'
                ], check=True)

            elif item.id == 'git_status':
                subprocess.run(['git', 'status'], check=True)

            elif item.id == 'git_setup':
                print(f"{Colors.DIM}Setting up git remotes for 3-repo architecture...{Colors.RESET}\n")
                subprocess.run(['unibos-dev', 'git', 'setup'], check=True)

            elif item.id == 'git_push_all':
                print(f"{Colors.YELLOW}Enter commit message:{Colors.RESET} ", end='')
                message = input().strip()
                if message:
                    print(f"\n{Colors.DIM}Pushing to all 3 repositories...{Colors.RESET}\n")
                    subprocess.run(['unibos-dev', 'git', 'push-all', message], check=True)
                else:
                    print(f"{Colors.RED}❌ Commit message required{Colors.RESET}")

            elif item.id == 'git_push_dev':
                print(f"{Colors.YELLOW}Enter commit message:{Colors.RESET} ", end='')
                message = input().strip()
                if message:
                    print(f"\n{Colors.DIM}Pushing to dev repository...{Colors.RESET}\n")
                    subprocess.run(['unibos-dev', 'git', 'push-all', message, '--repos', 'dev'], check=True)
                else:
                    print(f"{Colors.RED}❌ Commit message required{Colors.RESET}")

            elif item.id == 'git_push_server':
                print(f"{Colors.YELLOW}Enter commit message:{Colors.RESET} ", end='')
                message = input().strip()
                if message:
                    print(f"\n{Colors.DIM}Pushing to server repository...{Colors.RESET}\n")
                    subprocess.run(['unibos-dev', 'git', 'push-all', message, '--repos', 'server'], check=True)
                else:
                    print(f"{Colors.RED}❌ Commit message required{Colors.RESET}")

            elif item.id == 'git_push_prod':
                print(f"{Colors.YELLOW}Enter commit message:{Colors.RESET} ", end='')
                message = input().strip()
                if message:
                    print(f"\n{Colors.DIM}Pushing to prod repository...{Colors.RESET}\n")
                    subprocess.run(['unibos-dev', 'git', 'push-all', message, '--repos', 'prod'], check=True)
                else:
                    print(f"{Colors.RED}❌ Commit message required{Colors.RESET}")

            elif item.id == 'deploy_rocksteady':
                subprocess.run(['unibos-dev', 'deploy', 'rocksteady'], check=True)

            elif item.id == 'db_backup':
                subprocess.run(['unibos-dev', 'db', 'backup'], check=True)

            elif item.id == 'db_restore':
                print(f"{Colors.YELLOW}Enter backup file path:{Colors.RESET} ", end='')
                backup_file = input().strip()
                if backup_file:
                    subprocess.run(['unibos-dev', 'db', 'restore', backup_file], check=True)

            elif item.id == 'db_migrate':
                subprocess.run(['unibos-dev', 'db', 'migrate'], check=True)

            elif item.id == 'db_makemigrations':
                subprocess.run(['unibos-dev', 'db', 'makemigrations'], check=True)

            elif item.id == 'platform_modules':
                subprocess.run(['unibos-dev', 'platform', 'modules'], check=True)

            elif item.id == 'platform_config':
                subprocess.run(['unibos-dev', 'platform', 'config'], check=True)

            elif item.id == 'platform_identity':
                subprocess.run(['unibos-dev', 'platform', 'identity'], check=True)

            else:
                print(f"{Colors.YELLOW}⚠ Action not yet implemented: {item.id}{Colors.RESET}")

        except subprocess.CalledProcessError as e:
            print(f"\n{Colors.RED}❌ Command failed with exit code {e.returncode}{Colors.RESET}")
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}⚠ Interrupted{Colors.RESET}")
        except Exception as e:
            print(f"\n{Colors.RED}❌ Error: {e}{Colors.RESET}")

        # Pause before returning to menu
        print(f"\n{Colors.DIM}Press Enter to continue...{Colors.RESET}")
        input()

        return True  # Continue menu loop


def run_interactive():
    """Run unibos-dev in interactive mode"""
    interactive = UnibosDevInteractive()
    interactive.run(show_splash=True)
