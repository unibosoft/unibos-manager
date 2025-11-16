"""
UNIBOS-DEV Enhanced TUI
Development TUI with full v527 features and shared infrastructure
"""

import subprocess
from pathlib import Path
from typing import List

from core.clients.tui import BaseTUI
from core.clients.tui.components import MenuSection
from core.clients.cli.framework.ui import MenuItem, Colors, clear_screen


class UnibosDevTUI(BaseTUI):
    """Enhanced TUI for unibos-dev with complete functionality"""

    def get_profile_name(self) -> str:
        """Get profile name"""
        return "development"

    def get_menu_sections(self) -> List[MenuSection]:
        """Get development menu sections"""
        return [
            # Development Tools Section
            MenuSection(
                id='dev',
                label='development',
                icon='🔧',
                items=[
                    MenuItem(
                        id='dev_run',
                        label='start server',
                        icon='▶️',
                        description='Start Django development server\n\n'
                                   '→ Runs on http://127.0.0.1:8000\n'
                                   '→ Auto-reload enabled\n'
                                   '→ Debug mode active\n\n'
                                   'Command: python manage.py runserver',
                        enabled=True
                    ),
                    MenuItem(
                        id='dev_stop',
                        label='stop server',
                        icon='⏹️',
                        description='Stop running development server\n\n'
                                   '→ Kills all Django runserver processes\n'
                                   '→ Frees up port 8000\n\n'
                                   'Command: pkill -f "manage.py runserver"',
                        enabled=True
                    ),
                    MenuItem(
                        id='dev_shell',
                        label='django shell',
                        icon='🐚',
                        description='Open Django interactive shell\n\n'
                                   '→ Full Django environment loaded\n'
                                   '→ Access to all models and settings\n'
                                   '→ IPython enhanced if available\n\n'
                                   'Command: python manage.py shell',
                        enabled=True
                    ),
                    MenuItem(
                        id='dev_test',
                        label='run tests',
                        icon='🧪',
                        description='Run Django test suite\n\n'
                                   '→ Runs all app tests\n'
                                   '→ Shows coverage if available\n'
                                   '→ Uses test database\n\n'
                                   'Command: python manage.py test',
                        enabled=True
                    ),
                    MenuItem(
                        id='dev_logs',
                        label='view logs',
                        icon='📋',
                        description='View development logs\n\n'
                                   '→ Shows last 50 lines by default\n'
                                   '→ Can follow in real-time\n'
                                   '→ Includes Django debug logs\n\n'
                                   'Log file: data/core/logs/django/debug.log',
                        enabled=True
                    ),
                ]
            ),

            # Git & Deployment Section
            MenuSection(
                id='git',
                label='git & deploy',
                icon='🚀',
                items=[
                    MenuItem(
                        id='git_status',
                        label='git status',
                        icon='📊',
                        description='Show git repository status\n\n'
                                   '→ Current branch\n'
                                   '→ Modified files\n'
                                   '→ Staged changes\n'
                                   '→ Unpushed commits\n\n'
                                   'Command: git status',
                        enabled=True
                    ),
                    MenuItem(
                        id='git_pull',
                        label='pull changes',
                        icon='⬇️',
                        description='Pull latest changes from remote\n\n'
                                   '→ Fetches from origin\n'
                                   '→ Merges into current branch\n'
                                   '→ Shows conflicts if any\n\n'
                                   'Command: git pull',
                        enabled=True
                    ),
                    MenuItem(
                        id='git_commit',
                        label='commit changes',
                        icon='💾',
                        description='Commit current changes\n\n'
                                   '→ Stages all changes\n'
                                   '→ Prompts for commit message\n'
                                   '→ Creates local commit\n\n'
                                   'Commands: git add -A && git commit',
                        enabled=True
                    ),
                    MenuItem(
                        id='git_push_all',
                        label='push to all repos',
                        icon='🌐',
                        description='Push to all 3 repositories\n\n'
                                   '→ Dev repository (GitHub)\n'
                                   '→ Server repository (GitHub)\n'
                                   '→ Prod repository (GitHub)\n\n'
                                   'Automatically switches .gitignore',
                        enabled=True
                    ),
                    MenuItem(
                        id='deploy_rocksteady',
                        label='deploy to server',
                        icon='🎯',
                        description='Deploy to rocksteady server\n\n'
                                   '→ SSH to rocksteady.fun\n'
                                   '→ Pull latest changes\n'
                                   '→ Run migrations\n'
                                   '→ Collect static files\n'
                                   '→ Restart services\n\n'
                                   'Full production deployment',
                        enabled=True
                    ),
                ]
            ),

            # Database Section
            MenuSection(
                id='database',
                label='database',
                icon='🗄️',
                items=[
                    MenuItem(
                        id='db_migrate',
                        label='run migrations',
                        icon='🔄',
                        description='Apply pending database migrations\n\n'
                                   '→ Shows pending migrations\n'
                                   '→ Applies in order\n'
                                   '→ Updates schema\n\n'
                                   'Command: python manage.py migrate',
                        enabled=True
                    ),
                    MenuItem(
                        id='db_makemigrations',
                        label='make migrations',
                        icon='📝',
                        description='Create new migration files\n\n'
                                   '→ Detects model changes\n'
                                   '→ Generates migration files\n'
                                   '→ Shows SQL preview\n\n'
                                   'Command: python manage.py makemigrations',
                        enabled=True
                    ),
                    MenuItem(
                        id='db_backup',
                        label='backup database',
                        icon='💾',
                        description='Create database backup\n\n'
                                   '→ Full database dump\n'
                                   '→ Timestamped filename\n'
                                   '→ Compressed format\n\n'
                                   'Location: archive/database_backups/',
                        enabled=True
                    ),
                    MenuItem(
                        id='db_restore',
                        label='restore backup',
                        icon='📥',
                        description='Restore from backup\n\n'
                                   '→ Lists available backups\n'
                                   '→ Confirms before restore\n'
                                   '→ Full data replacement\n\n'
                                   'Warning: Destructive operation',
                        enabled=True
                    ),
                    MenuItem(
                        id='db_shell',
                        label='database shell',
                        icon='🐚',
                        description='Open database shell\n\n'
                                   '→ Direct SQL access\n'
                                   '→ PostgreSQL psql client\n'
                                   '→ Full query capabilities\n\n'
                                   'Command: python manage.py dbshell',
                        enabled=True
                    ),
                ]
            ),

            # Platform Section
            MenuSection(
                id='platform',
                label='platform',
                icon='🌐',
                items=[
                    MenuItem(
                        id='platform_status',
                        label='system status',
                        icon='📊',
                        description='Show complete system status\n\n'
                                   '→ Version information\n'
                                   '→ Directory structure\n'
                                   '→ Service status\n'
                                   '→ Database connectivity\n'
                                   '→ Module registry\n\n'
                                   'Full health check',
                        enabled=True
                    ),
                    MenuItem(
                        id='platform_modules',
                        label='manage modules',
                        icon='📦',
                        description='Module management interface\n\n'
                                   '→ List all modules\n'
                                   '→ Enable/disable modules\n'
                                   '→ View module details\n'
                                   '→ Check dependencies\n\n'
                                   'Module registry control',
                        enabled=True
                    ),
                    MenuItem(
                        id='platform_config',
                        label='configuration',
                        icon='⚙️',
                        description='Platform configuration\n\n'
                                   '→ Environment settings\n'
                                   '→ Django settings\n'
                                   '→ Service configs\n'
                                   '→ Path configurations\n\n'
                                   'View and edit configs',
                        enabled=True
                    ),
                    MenuItem(
                        id='platform_identity',
                        label='node identity',
                        icon='🔐',
                        description='Node identity information\n\n'
                                   '→ Node UUID\n'
                                   '→ Node type (dev/server/prod)\n'
                                   '→ Registration status\n'
                                   '→ Network identity\n\n'
                                   'Persistent node identity',
                        enabled=True
                    ),
                ]
            ),
        ]

    def __init__(self):
        """Initialize dev TUI with proper config"""
        from core.clients.tui.base import TUIConfig

        config = TUIConfig(
            title="unibos-dev",
            version="v0.534.0",
            location="dev environment",
            sidebar_width=30,
            show_splash=True,  # Re-enabled splash screen
            quick_splash=False,
            lowercase_ui=True,  # v527 style
            show_breadcrumbs=True,
            show_time=True,
            show_hostname=True,
            show_status_led=True
        )

        super().__init__(config)

        # Register dev-specific handlers
        self.register_dev_handlers()

    def register_dev_handlers(self):
        """Register all development action handlers"""
        # Development actions
        self.register_action('dev_run', self.handle_dev_run)
        self.register_action('dev_stop', self.handle_dev_stop)
        self.register_action('dev_shell', self.handle_dev_shell)
        self.register_action('dev_test', self.handle_dev_test)
        self.register_action('dev_logs', self.handle_dev_logs)

        # Git actions
        self.register_action('git_status', self.handle_git_status)
        self.register_action('git_pull', self.handle_git_pull)
        self.register_action('git_commit', self.handle_git_commit)
        self.register_action('git_push_all', self.handle_git_push_all)
        self.register_action('deploy_rocksteady', self.handle_deploy_rocksteady)

        # Database actions
        self.register_action('db_migrate', self.handle_db_migrate)
        self.register_action('db_makemigrations', self.handle_db_makemigrations)
        self.register_action('db_backup', self.handle_db_backup)
        self.register_action('db_restore', self.handle_db_restore)
        self.register_action('db_shell', self.handle_db_shell)

        # Platform actions
        self.register_action('platform_status', self.handle_platform_status)
        self.register_action('platform_modules', self.handle_platform_modules)
        self.register_action('platform_config', self.handle_platform_config)
        self.register_action('platform_identity', self.handle_platform_identity)

    # Development handlers
    def handle_dev_run(self, item):
        """Start development server"""
        import subprocess
        import os
        import time

        # Check if server is already running
        check_result = subprocess.run(
            ['pgrep', '-f', 'manage.py runserver'],
            capture_output=True
        )

        if check_result.returncode == 0:
            # Server already running
            self.update_content(
                title="Development Server Status",
                lines=[
                    "⚠️  Development server is already running!",
                    "",
                    "Server is accessible at: http://127.0.0.1:8000",
                    "Use 'Stop Server' to stop it first."
                ],
                color=Colors.YELLOW
            )
        else:
            # Start server in background, redirect output to log file
            log_file = '/tmp/unibos_django_server.log'

            try:
                with open(log_file, 'w') as f:
                    process = subprocess.Popen(
                        ['unibos-dev', 'dev', 'run'],
                        stdout=f,
                        stderr=subprocess.STDOUT,
                        preexec_fn=os.setsid  # Create new process group
                    )

                # Wait a moment to check if it started
                time.sleep(2)

                if process.poll() is None:
                    # Server started successfully
                    self.update_content(
                        title="Development Server Started",
                        lines=[
                            "✅ Development server started!",
                            "",
                            "🌐 Server running at: http://127.0.0.1:8000",
                            "📋 Logs: /tmp/unibos_django_server.log",
                            "⏹️  Use 'Stop Server' to stop it",
                            "",
                            "The server is running in the background."
                        ],
                        color=Colors.GREEN
                    )
                else:
                    # Server failed to start, show log
                    with open(log_file, 'r') as f:
                        log_content = f.read()[-500:]  # Last 500 chars

                    self.update_content(
                        title="Server Start Failed",
                        lines=[
                            "❌ Failed to start server!",
                            "",
                            "Error output:",
                            "─" * 40,
                            log_content
                        ],
                        color=Colors.RED
                    )
            except Exception as e:
                self.update_content(
                    title="Server Start Error",
                    lines=[
                        "❌ Failed to start server!",
                        "",
                        f"Error: {e}"
                    ],
                    color=Colors.RED
                )

        self.render()
        return True

    def handle_dev_stop(self, item):
        """Stop development server"""
        import subprocess

        # Kill all Django runserver processes
        result = subprocess.run(
            ['pkill', '-f', 'manage.py runserver'],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            self.update_content(
                title="Development Server Stopped",
                lines=[
                    "✅ Development server stopped!",
                    "",
                    "The Django development server has been terminated.",
                    "",
                    "Use 'Start Server' to start it again."
                ],
                color=Colors.GREEN
            )
        else:
            # Check if server was running
            check_result = subprocess.run(
                ['pgrep', '-f', 'manage.py runserver'],
                capture_output=True
            )

            if check_result.returncode != 0:
                self.update_content(
                    title="Server Status",
                    lines=[
                        "ℹ️  No development server is running.",
                        "",
                        "Use 'Start Server' to start it."
                    ],
                    color=Colors.CYAN
                )
            else:
                self.update_content(
                    title="Stop Server Failed",
                    lines=[
                        "❌ Failed to stop server!",
                        "",
                        "You may need to manually kill the process.",
                        "",
                        "Try: pkill -f 'manage.py runserver'"
                    ],
                    color=Colors.RED
                )

        self.render()
        return True

    def handle_dev_shell(self, item):
        """Open Django shell"""
        # Run a simple Django shell command to get context
        result = self.execute_command(['unibos-dev', 'dev', 'shell', '--help'])

        # Since shell is interactive, provide instructions
        self.update_content(
            title="Django Shell",
            lines=[
                "Django Shell requires interactive terminal access.",
                "",
                "To use Django shell:",
                "1. Exit the TUI (press 'q' or ESC)",
                "2. Run: unibos-dev dev shell",
                "",
                "The shell provides:",
                "→ Full Django environment loaded",
                "→ Access to all models and settings",
                "→ IPython enhanced if available",
                "",
                "Alternative: Use the command line outside TUI for interactive shells."
            ]
        )
        self.render()
        return True

    def handle_dev_test(self, item):
        """Run tests"""
        self.update_content(
            title="Running Tests...",
            lines=["⏳ Running Django test suite...", "", "This may take a moment..."]
        )
        self.render()

        result = self.execute_command(['unibos-dev', 'dev', 'test'])
        self.show_command_output(result)
        return True

    def handle_dev_logs(self, item):
        """View logs"""
        import os

        log_file = '/tmp/unibos_django_server.log'

        if os.path.exists(log_file):
            # Read last 50 lines of log for content area
            with open(log_file, 'r') as f:
                lines = f.readlines()
                last_lines = lines[-50:] if len(lines) > 50 else lines

            # Format lines for content area
            content = [
                f"Server logs (last {len(last_lines)} lines):",
                f"File: {log_file}",
                "",
                "─" * 40,
                ""
            ]

            for line in last_lines:
                # Keep full lines for scrolling support
                line = line.rstrip()
                if line:
                    content.append(line)

            self.update_content(
                title="Development Server Logs",
                lines=content,
                color=Colors.CYAN
            )
        else:
            self.update_content(
                title="No Logs Available",
                lines=[
                    "ℹ️  No log file found.",
                    "",
                    "The server may not have been started yet.",
                    "Use 'Start Server' to start it first."
                ],
                color=Colors.CYAN
            )

        self.render()
        return True

    # Git handlers
    def handle_git_status(self, item):
        """Show git status"""
        result = self.execute_command(['git', 'status'])

        if result.returncode == 0:
            lines = result.stdout.split('\n')
            self.update_content(
                title="Git Status",
                lines=lines,
                color=Colors.CYAN
            )
        else:
            self.update_content(
                title="Git Status Error",
                lines=[
                    "❌ Failed to get git status",
                    "",
                    "Error:",
                    result.stderr
                ],
                color=Colors.RED
            )

        self.render()
        return True

    def handle_git_pull(self, item):
        """Pull from remote"""
        self.update_content(
            title="Pulling from Remote...",
            lines=["⏳ Fetching latest changes...", "", "This may take a moment..."]
        )
        self.render()

        result = self.execute_command(['git', 'pull'])
        self.show_command_output(result)
        return True

    def handle_git_commit(self, item):
        """Commit changes"""
        # First show git status for context
        status_result = self.execute_command(['git', 'status', '--short'])

        if status_result.stdout.strip():
            lines = [
                "Current changes to be committed:",
                "",
                "─" * 40,
                ""
            ]
            lines.extend(status_result.stdout.split('\n'))
            lines.extend([
                "",
                "─" * 40,
                "",
                "ℹ️  To commit these changes:",
                "1. Exit TUI (press 'q')",
                "2. Run: git add -A && git commit -m 'your message'",
                "",
                "Or use 'Push to all repos' for automated commit and push."
            ])

            self.update_content(
                title="Git Commit",
                lines=lines
            )
        else:
            self.update_content(
                title="No Changes",
                lines=[
                    "ℹ️  No changes to commit.",
                    "",
                    "Working directory is clean."
                ],
                color=Colors.CYAN
            )

        self.render()
        return True

    def handle_git_push_all(self, item):
        """Push to all repositories"""
        # Show current status first
        status_result = self.execute_command(['git', 'status', '--short'])

        lines = [
            "Push to All Repositories",
            "",
            "This will:",
            "→ Commit all current changes",
            "→ Push to dev repository",
            "→ Push to server repository",
            "→ Push to prod repository",
            "",
            "Current changes:",
            "─" * 40,
            ""
        ]

        if status_result.stdout.strip():
            lines.extend(status_result.stdout.split('\n'))
        else:
            lines.append("No uncommitted changes")

        lines.extend([
            "",
            "─" * 40,
            "",
            "ℹ️  To push to all repos:",
            "1. Exit TUI (press 'q')",
            "2. Run: unibos-dev git push-all 'your commit message'"
        ])

        self.update_content(
            title="Push to All Repos",
            lines=lines
        )
        self.render()
        return True

    def handle_deploy_rocksteady(self, item):
        """Deploy to rocksteady"""
        lines = [
            "Deploy to Rocksteady Server",
            "",
            "This deployment will:",
            "→ SSH to rocksteady.fun",
            "→ Pull latest changes",
            "→ Run database migrations",
            "→ Collect static files",
            "→ Restart systemd services",
            "",
            "⚠️  This is a production deployment!",
            "",
            "Prerequisites:",
            "✓ SSH key configured for rocksteady.fun",
            "✓ Latest changes pushed to server repo",
            "✓ Database migrations tested locally",
            "",
            "─" * 40,
            "",
            "To deploy:",
            "1. Exit TUI (press 'q')",
            "2. Run: unibos-dev deploy rocksteady",
            "",
            "The deployment will show real-time progress."
        ]

        self.update_content(
            title="Production Deployment",
            lines=lines,
            color=Colors.YELLOW
        )
        self.render()
        return True

    # Database handlers
    def handle_db_migrate(self, item):
        """Run migrations"""
        self.update_content(
            title="Running Migrations...",
            lines=["⏳ Applying database migrations...", "", "This may take a moment..."]
        )
        self.render()

        result = self.execute_command(['unibos-dev', 'db', 'migrate'])
        self.show_command_output(result)
        return True

    def handle_db_makemigrations(self, item):
        """Make migrations"""
        self.update_content(
            title="Creating Migrations...",
            lines=["⏳ Detecting model changes...", "", "Creating migration files..."]
        )
        self.render()

        result = self.execute_command(['unibos-dev', 'db', 'makemigrations'])
        self.show_command_output(result)
        return True

    def handle_db_backup(self, item):
        """Backup database"""
        self.update_content(
            title="Creating Database Backup...",
            lines=["⏳ Backing up database...", "", "This may take a moment..."]
        )
        self.render()

        result = self.execute_command(['unibos-dev', 'db', 'backup'])
        self.show_command_output(result)
        return True

    def handle_db_restore(self, item):
        """Restore database"""
        # List available backups first
        import os
        backup_dir = "/Users/berkhatirli/Desktop/unibos-dev/archive/database_backups"

        lines = [
            "Database Restore",
            "",
            "Available backups:",
            "─" * 40,
            ""
        ]

        if os.path.exists(backup_dir):
            backups = sorted([f for f in os.listdir(backup_dir) if f.endswith(('.sql', '.dump', '.gz'))])[-10:]
            if backups:
                for backup in backups:
                    lines.append(f"  • {backup}")
            else:
                lines.append("  No backups found")
        else:
            lines.append("  Backup directory not found")

        lines.extend([
            "",
            "─" * 40,
            "",
            "⚠️  Restoring will replace all current data!",
            "",
            "To restore a backup:",
            "1. Exit TUI (press 'q')",
            "2. Run: unibos-dev db restore <backup_file>",
            "",
            "Example: unibos-dev db restore backup_2024-11-16.sql"
        ])

        self.update_content(
            title="Database Restore",
            lines=lines,
            color=Colors.YELLOW
        )
        self.render()
        return True

    def handle_db_shell(self, item):
        """Open database shell"""
        lines = [
            "Database Shell",
            "",
            "The database shell provides direct SQL access.",
            "",
            "Features:",
            "→ Direct PostgreSQL psql client",
            "→ Full SQL query capabilities",
            "→ Database administration",
            "",
            "To use database shell:",
            "1. Exit TUI (press 'q')",
            "2. Run: unibos-dev db shell",
            "",
            "You'll be connected to the configured database.",
            "",
            "Common commands:",
            "  \\dt     - List all tables",
            "  \\d table - Describe table structure",
            "  \\q      - Exit shell"
        ]

        self.update_content(
            title="Database Shell",
            lines=lines
        )
        self.render()
        return True

    # Platform handlers
    def handle_platform_status(self, item):
        """Show platform status"""
        self.update_content(
            title="Loading Platform Status...",
            lines=["⏳ Gathering system information...", "", "This may take a moment..."]
        )
        self.render()

        result = self.execute_command(['unibos-dev', 'status'])
        self.show_command_output(result)
        return True

    def handle_platform_modules(self, item):
        """Manage modules"""
        self.update_content(
            title="Loading Modules...",
            lines=["⏳ Scanning module registry...", "", "Checking dependencies..."]
        )
        self.render()

        result = self.execute_command(['unibos-dev', 'platform', '-v'])
        self.show_command_output(result)
        return True

    def handle_platform_config(self, item):
        """Show configuration"""
        self.update_content(
            title="Loading Configuration...",
            lines=["⏳ Reading configuration files...", "", "Processing settings..."]
        )
        self.render()

        result = self.execute_command(['unibos-dev', 'platform', '-v', '--json'])

        if result.returncode == 0:
            # Format JSON output for better readability
            try:
                import json
                config_data = json.loads(result.stdout)
                lines = [
                    "Platform Configuration",
                    "─" * 40,
                    ""
                ]

                def format_dict(d, indent=0):
                    result_lines = []
                    for key, value in d.items():
                        if isinstance(value, dict):
                            result_lines.append(" " * indent + f"{key}:")
                            result_lines.extend(format_dict(value, indent + 2))
                        elif isinstance(value, list):
                            result_lines.append(" " * indent + f"{key}:")
                            for item in value:
                                result_lines.append(" " * (indent + 2) + f"• {item}")
                        else:
                            result_lines.append(" " * indent + f"{key}: {value}")
                    return result_lines

                lines.extend(format_dict(config_data))
                self.update_content("Platform Configuration", lines)
            except json.JSONDecodeError:
                # Fall back to raw output
                self.show_command_output(result)
        else:
            self.show_command_output(result)

        self.render()
        return True

    def handle_platform_identity(self, item):
        """Show node identity"""
        lines = ["Node Identity Information", "", "─" * 40, ""]

        try:
            from core.base.identity import get_instance_identity
            instance = get_instance_identity()
            identity = instance.get_identity()

            lines.extend([
                f"Node UUID: {identity.uuid}",
                f"Node Type: {identity.node_type.value}",
                f"Hostname: {identity.hostname}",
                f"Platform: {identity.platform}",
                f"Created: {identity.created_at}",
                f"Last Seen: {identity.last_seen}"
            ])

            if identity.registered_to:
                lines.append(f"Registered To: {identity.registered_to}")

            lines.extend([
                "",
                "─" * 40,
                "",
                "This identity is persistent and unique to this node.",
                "It's used for:",
                "→ Node registration",
                "→ Inter-node communication",
                "→ Service discovery",
                "→ Access control"
            ])
        except Exception as e:
            lines.extend([
                f"❌ Error loading identity: {e}",
                "",
                "The identity system may not be initialized.",
                "Try running: unibos-dev platform init"
            ])

        self.update_content(
            title="Node Identity",
            lines=lines,
            color=Colors.CYAN
        )
        self.render()
        return True

    # Helper methods are inherited from BaseTUI


def run_interactive():
    """Run the enhanced dev TUI"""
    tui = UnibosDevTUI()
    tui.run()


if __name__ == "__main__":
    run_interactive()