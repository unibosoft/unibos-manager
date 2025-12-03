"""
UNIBOS-DEV TUI - Simplified Structure
Development TUI with single dev-tools section
"""

import subprocess
from pathlib import Path
from typing import List

from core.clients.tui import BaseTUI
from core.clients.tui.components import MenuSection
from core.clients.cli.framework.ui import MenuItem, Colors
from core.clients.tui.common_items import CommonItems


class UnibosDevTUI(BaseTUI):
    """Development TUI with v527 structure"""

    def __init__(self):
        """Initialize dev TUI with proper config"""
        from core.clients.tui.base import TUIConfig
        from core.version import __version__, __build__, get_short_version_string

        config = TUIConfig(
            title="unibos-dev",
            version=get_short_version_string(),  # Dynamic: "v1.0.0 22:25"
            location="dev environment",
            sidebar_width=25,  # V527 spec: exactly 25 characters
            show_splash=True,
            quick_splash=False,
            lowercase_ui=True,  # v527 style
            show_breadcrumbs=True,
            show_time=True,  # Time in footer, not header
            show_hostname=True,
            show_status_led=True
        )

        super().__init__(config)

        # Register dev-specific handlers
        self.register_dev_handlers()

    def get_profile_name(self) -> str:
        """Get profile name"""
        return "development"

    def get_menu_sections(self) -> List[MenuSection]:
        """Get development menu sections - simplified single section"""
        return [
            # Single unified dev-tools section
            MenuSection(
                id='dev_tools',
                label='dev-tools',
                icon='🛠️',
                items=[
                    # System & Status
                    MenuItem(
                        id='system_status',
                        label=self.i18n.translate('menu.system_status'),
                        icon='📊',
                        description='system status & info\n\n'
                                   '→ system information\n'
                                   '→ version details\n'
                                   '→ service status\n'
                                   '→ resource usage\n\n'
                                   'complete system overview',
                        enabled=True
                    ),
                    CommonItems.web_ui(self.i18n),
                    CommonItems.database_setup(self.i18n, profile_type='dev'),
                    MenuItem(
                        id='code_forge',
                        label=self.i18n.translate('menu.git'),
                        icon='⚙️',
                        description='git operations\n\n'
                                   '→ git status\n'
                                   '→ commit history\n'
                                   '→ branch management\n\n'
                                   'source code management',
                        enabled=True
                    ),
                    MenuItem(
                        id='version_manager',
                        label=self.i18n.translate('menu.versions'),
                        icon='📋',
                        description='version archives\n\n'
                                   '→ create archives\n'
                                   '→ browse history\n'
                                   '→ release pipeline\n\n'
                                   'version control and archiving',
                        enabled=True
                    ),
                    MenuItem(
                        id='deploy_servers',
                        label=self.i18n.translate('menu.deploy'),
                        icon='🌍',
                        description='server deployment\n\n'
                                   '→ rocksteady (production)\n'
                                   '→ bebop (staging)\n'
                                   '→ deploy & manage\n\n'
                                   'multi-server deploy',
                        enabled=True
                    ),
                    MenuItem(
                        id='ai_builder',
                        label=self.i18n.translate('menu.ai_builder'),
                        icon='🤖',
                        description='ai development\n\n'
                                   '→ code generation\n'
                                   '→ ai assistance\n'
                                   '→ smart refactoring\n\n'
                                   'ai-powered tools',
                        enabled=True
                    ),
                    CommonItems.administration(self.i18n),
                ]
            ),
        ]

    def register_dev_handlers(self):
        """Register all development action handlers"""
        # Dev tools handlers
        self.register_action('system_status', self.handle_system_status)
        self.register_action('web_ui', self.handle_web_ui)
        self.register_action('database_setup', self.handle_database_setup)
        self.register_action('code_forge', self.handle_code_forge)
        self.register_action('version_manager', self.handle_version_manager)
        self.register_action('deploy_servers', self.handle_deploy_servers)
        self.register_action('ai_builder', self.handle_ai_builder)
        self.register_action('administration', self.handle_administration)

    # ===== DEV TOOLS HANDLERS =====

    def handle_system_status(self, item: MenuItem) -> bool:
        """show system status and information"""
        self.update_content(
            title="system status",
            lines=["⏳ gathering system information...", ""],
            color=Colors.CYAN
        )
        self.render()

        try:
            # Execute status command
            result = self.execute_command(['unibos-dev', 'status'])

            # Show results
            self.show_command_output(result)

        except Exception as e:
            self.update_content(
                title="system status - error",
                lines=[
                    "❌ failed to load system information",
                    "",
                    f"error: {str(e)}",
                    "",
                    "try running: unibos-dev status"
                ],
                color=Colors.RED
            )
            self.render()

        return True

    def handle_code_forge(self, item: MenuItem) -> bool:
        """Git and version control"""
        options = [
            ("status", "📊 git status", "show current repository status"),
            ("commit", "💾 commit changes", "create a new commit"),
            ("push", "⬆️  push to remote", "push commits to remote repository"),
            ("pull", "⬇️  pull from remote", "pull latest changes"),
            ("branch", "🌿 branch info", "show branch information"),
            ("log", "📜 commit log", "show recent commits"),
            ("back", "← back", "return to dev tools"),
        ]

        handlers = {
            "status": self._git_show_status,
            "commit": self._git_commit,
            "push": self._git_push,
            "pull": self._git_pull,
            "branch": self._git_branch_info,
            "log": self._git_show_log,
        }

        return self.show_submenu(
            title="git",
            subtitle="source code management",
            options=options,
            handlers=handlers
        )

    def _git_show_status(self):
        """Show git status"""
        self.update_content(title="git status", lines=["⏳ loading..."], color=Colors.CYAN)
        self.render()
        result = self.execute_command(['unibos-dev', 'git', 'status'])
        self.show_command_output(result)

    def _git_commit(self):
        """Create git commit"""
        self.update_content(title="git commit", lines=["⏳ preparing commit..."], color=Colors.CYAN)
        self.render()
        result = self.execute_command(['unibos-dev', 'git', 'commit'])
        self.show_command_output(result)

    def _git_push(self):
        """Push to remote"""
        self.update_content(title="git push", lines=["⏳ pushing..."], color=Colors.CYAN)
        self.render()
        result = self.execute_command(['unibos-dev', 'git', 'push-dev'])
        self.show_command_output(result)

    def _git_pull(self):
        """Pull from remote"""
        self.update_content(title="git pull", lines=["⏳ pulling..."], color=Colors.CYAN)
        self.render()
        result = self.execute_command(['git', 'pull'])
        self.show_command_output(result)

    def _git_branch_info(self):
        """Show branch info"""
        self.update_content(title="git branches", lines=["⏳ loading..."], color=Colors.CYAN)
        self.render()
        result = self.execute_command(['git', 'branch', '-vv'])
        self.show_command_output(result)

    def _git_show_log(self):
        """Show commit log"""
        self.update_content(title="git log", lines=["⏳ loading..."], color=Colors.CYAN)
        self.render()
        result = self.execute_command(['git', 'log', '--oneline', '-20'])
        self.show_command_output(result)

    def handle_web_ui(self, item: MenuItem) -> bool:
        """Web interface management"""
        options = [
            ("start", "🚀 start server", "start uvicorn in background"),
            ("stop", "⏹️  stop server", "stop the running server"),
            ("restart", "🔄 restart server", "stop and start server"),
            ("status", "📊 server status", "check if server is running"),
            ("logs", "📝 view logs", "show recent server logs"),
            ("migrate", "🔃 run migrations", "apply database migrations"),
            ("back", "← back", "return to dev tools"),
        ]

        handlers = {
            "start": self._web_ui_start_server,
            "stop": self._web_ui_stop_server,
            "restart": self._web_ui_restart_server,
            "status": self._web_ui_show_status,
            "logs": self._web_ui_show_logs,
            "migrate": self._web_ui_run_migrations,
        }

        return self.show_submenu(
            title="web ui",
            subtitle="uvicorn asgi server",
            options=options,
            handlers=handlers
        )

    def _web_ui_start_server(self):
        """start uvicorn development server in background"""
        self.update_content(
            title="starting uvicorn server",
            lines=["🚀 starting server in background...", ""],
            color=Colors.CYAN
        )
        self.render()

        # Start in background mode (-b flag)
        result = self.execute_command(['unibos-dev', 'dev', 'run', '-b'])
        self.show_command_output(result)

    def _web_ui_stop_server(self):
        """stop development server"""
        self.update_content(
            title="stopping server",
            lines=["⏹️ stopping development server...", ""],
            color=Colors.CYAN
        )
        self.render()

        result = self.execute_command(['unibos-dev', 'dev', 'stop'])
        self.show_command_output(result)

    def _web_ui_restart_server(self):
        """restart development server"""
        import time

        self.update_content(
            title="restarting server",
            lines=["🔄 stopping server...", ""],
            color=Colors.CYAN
        )
        self.render()

        # Stop first
        stop_result = self.execute_command(['unibos-dev', 'dev', 'stop'])

        # Show stop result and wait
        stop_output = stop_result.stdout.strip() if stop_result.stdout else ""
        self.update_content(
            title="restarting server",
            lines=[
                stop_output or "⏹️  stopping...",
                "",
                "🚀 starting server...",
            ],
            color=Colors.CYAN
        )
        self.render()

        # Wait for port to be released
        time.sleep(1.0)

        # Then start in background
        result = self.execute_command(['unibos-dev', 'dev', 'run', '-b'])
        self.show_command_output(result)

    def _web_ui_show_status(self):
        """show server status"""
        self.update_content(
            title="server status",
            lines=["📊 checking server status...", ""],
            color=Colors.CYAN
        )
        self.render()

        result = self.execute_command(['unibos-dev', 'dev', 'status'])
        self.show_command_output(result)

    def _web_ui_show_logs(self):
        """show server logs"""
        self.update_content(
            title="server logs",
            lines=["📝 loading server logs...", ""],
            color=Colors.CYAN
        )
        self.render()

        result = self.execute_command(['unibos-dev', 'dev', 'logs'])
        self.show_command_output(result)

    def _web_ui_run_migrations(self):
        """run django migrations"""
        self.update_content(
            title="running migrations",
            lines=["🔄 running database migrations...", ""],
            color=Colors.CYAN
        )
        self.render()

        result = self.execute_command(['unibos-dev', 'dev', 'migrate'])
        self.show_command_output(result)

    def handle_administration(self, item: MenuItem) -> bool:
        """System administration"""
        options = [
            ("users", "👤 user management", "manage users and permissions"),
            ("settings", "⚙️  system settings", "configure system settings"),
            ("modules", "📦 module management", "enable/disable modules"),
            ("logs", "📝 system logs", "view system logs"),
            ("django_admin", "🌐 django admin", "open django admin interface"),
            ("back", "← back", "return to dev tools"),
        ]

        handlers = {
            "users": self._admin_users,
            "settings": self._admin_settings,
            "modules": self._admin_modules,
            "logs": self._admin_logs,
            "django_admin": self._admin_django,
        }

        return self.show_submenu(
            title="admin",
            subtitle="system administration",
            options=options,
            handlers=handlers
        )

    def _admin_users(self):
        """User management placeholder"""
        self.update_content(title="user management", lines=[
            "🚧 coming soon",
            "",
            "for now, use django admin:",
            "  http://localhost:8000/admin/auth/user/"
        ], color=Colors.YELLOW)
        self.render()

    def _admin_settings(self):
        """System settings placeholder"""
        self.update_content(title="system settings", lines=[
            "🚧 coming soon",
            "",
            "for now, edit settings files directly:",
            "  core/clients/web/unibos_backend/settings/"
        ], color=Colors.YELLOW)
        self.render()

    def _admin_modules(self):
        """Module management placeholder"""
        self.update_content(title="module management", lines=[
            "🚧 coming soon",
            "",
            "modules are managed via .enabled files:",
            "  modules/<module_name>/.enabled"
        ], color=Colors.YELLOW)
        self.render()

    def _admin_logs(self):
        """View system logs"""
        self.update_content(title="system logs", lines=["⏳ loading..."], color=Colors.CYAN)
        self.render()
        result = self.execute_command(['tail', '-50', '/Users/berkhatirli/Desktop/unibos-dev/core/clients/web/logs/django.log'])
        self.show_command_output(result)

    def _admin_django(self):
        """Open Django admin info"""
        self.update_content(title="django admin", lines=[
            "django admin interface",
            "",
            "1. start server: unibos-dev dev run",
            "2. visit: http://localhost:8000/admin",
            "",
            "default credentials:",
            "  username: admin",
            "  password: (set during setup)"
        ], color=Colors.CYAN)
        self.render()

    def handle_ai_builder(self, item: MenuItem) -> bool:
        """AI-powered development tools"""
        options = [
            ("claude", "🤖 claude code", "ai-powered coding assistant"),
            ("generate", "✨ generate code", "generate boilerplate code"),
            ("review", "🔍 code review", "ai code review suggestions"),
            ("docs", "📝 generate docs", "auto-generate documentation"),
            ("back", "← back", "return to dev tools"),
        ]

        handlers = {
            "claude": self._ai_claude,
            "generate": self._ai_generate,
            "review": self._ai_review,
            "docs": self._ai_docs,
        }

        return self.show_submenu(
            title="ai builder",
            subtitle="ai-powered development",
            options=options,
            handlers=handlers
        )

    def _ai_claude(self):
        """Claude Code info"""
        self.update_content(title="claude code", lines=[
            "claude code - ai coding assistant",
            "",
            "currently active: you're using claude code right now!",
            "",
            "features:",
            "  • code generation",
            "  • debugging assistance",
            "  • code review",
            "  • documentation",
            "",
            "just ask me anything about your code."
        ], color=Colors.MAGENTA)
        self.render()

    def _ai_generate(self):
        """Code generation placeholder"""
        self.update_content(title="generate code", lines=[
            "🚧 coming soon",
            "",
            "for now, use claude code to generate code:",
            "  just describe what you need!"
        ], color=Colors.YELLOW)
        self.render()

    def _ai_review(self):
        """Code review placeholder"""
        self.update_content(title="code review", lines=[
            "🚧 coming soon",
            "",
            "for now, ask claude code to review your code:",
            "  share your code and ask for review"
        ], color=Colors.YELLOW)
        self.render()

    def _ai_docs(self):
        """Documentation generation placeholder"""
        self.update_content(title="generate docs", lines=[
            "🚧 coming soon",
            "",
            "for now, ask claude code to generate docs:",
            "  share your code and ask for documentation"
        ], color=Colors.YELLOW)
        self.render()

    def handle_database_setup(self, item: MenuItem) -> bool:
        """PostgreSQL installation wizard"""
        options = [
            ("check", "🔍 check status", "check if postgresql is installed and running"),
            ("install", "📥 install postgresql", "install using homebrew (macos)"),
            ("create", "🗄️  create database", "create unibos database"),
            ("migrate", "🔄 run migrations", "apply django migrations"),
            ("backup", "💾 backup database", "create database backup"),
            ("restore", "♻️  restore database", "restore from backup"),
            ("back", "← back", "return to dev tools"),
        ]

        handlers = {
            "check": self._db_check_status,
            "install": self._db_install_postgresql,
            "create": self._db_create_database,
            "migrate": self._db_run_migrations,
            "backup": self._db_backup,
            "restore": self._db_restore,
        }

        return self.show_submenu(
            title="database",
            subtitle="postgresql database management",
            options=options,
            handlers=handlers
        )

    def _db_check_status(self):
        """Check database status"""
        self.update_content(
            title="database status",
            lines=["🔍 Checking database status...", ""],
            color=Colors.CYAN
        )
        self.render()

        result = self.execute_command(['unibos-dev', 'db', 'status'])
        self.show_command_output(result)

    def _db_install_postgresql(self):
        """install postgresql"""
        self.update_content(
            title="installing postgresql",
            lines=[
                "📥 PostgreSQL Installation",
                "",
                "this will install PostgreSQL using Homebrew.",
                "",
                "run this command in terminal:",
                "",
                "  brew install postgresql@14",
                "  brew services start postgresql@14",
                "",
                "then create database:",
                "",
                "  createdb unibos_dev",
                "",
                "press esc to continue"
            ],
            color=Colors.YELLOW
        )
        self.render()

    def _db_create_database(self):
        """create database"""
        self.update_content(
            title="creating database",
            lines=["🗄️ Creating UNIBOS database...", ""],
            color=Colors.CYAN
        )
        self.render()

        result = self.execute_command(['unibos-dev', 'db', 'create'])
        self.show_command_output(result)

    def _db_run_migrations(self):
        """Run migrations"""
        self.update_content(
            title="running migrations",
            lines=["🔄 Running database migrations...", ""],
            color=Colors.CYAN
        )
        self.render()

        result = self.execute_command(['unibos-dev', 'db', 'migrate'])
        self.show_command_output(result)

    def _db_backup(self):
        """Backup database"""
        self.update_content(
            title="database backup",
            lines=["💾 Creating database backup...", ""],
            color=Colors.CYAN
        )
        self.render()

        result = self.execute_command(['unibos-dev', 'db', 'backup'])
        self.show_command_output(result)

    def _db_restore(self):
        """Restore database"""
        self.update_content(
            title="database restore",
            lines=["♻️ Restoring database...", ""],
            color=Colors.CYAN
        )
        self.render()

        result = self.execute_command(['unibos-dev', 'db', 'restore'])
        self.show_command_output(result)

    # ===== DEPLOY SERVERS =====

    # Server configurations
    SERVERS = {
        'rocksteady': {
            'name': 'rocksteady',
            'label': '🖥️  rocksteady',
            'description': 'production server',
            'env': 'production',
            'icon': '🖥️',
        },
        'bebop': {
            'name': 'bebop',
            'label': '🧪 bebop',
            'description': 'staging server',
            'env': 'staging',
            'icon': '🧪',
        },
    }

    def handle_deploy_servers(self, item: MenuItem) -> bool:
        """Server selection menu"""
        options = [
            ("rocksteady", "🖥️  rocksteady", "production server"),
            ("bebop", "🧪 bebop", "staging server"),
            ("back", "← back", "return to dev tools"),
        ]

        handlers = {
            "rocksteady": lambda: self._show_server_menu('rocksteady'),
            "bebop": lambda: self._show_server_menu('bebop'),
        }

        return self.show_submenu(
            title="deploy",
            subtitle="select target server",
            options=options,
            handlers=handlers
        )

    def _show_server_menu(self, server_name: str):
        """Show operations menu for a specific server"""
        server = self.SERVERS.get(server_name, {})
        server_label = server.get('label', server_name)
        server_env = server.get('env', 'unknown')

        options = [
            ("status", "📊 status", f"check {server_name} service status"),
            ("deploy", "🚀 deploy", f"deploy to {server_name}"),
            ("start", "▶️  start", f"start service on {server_name}"),
            ("stop", "⏹️  stop", f"stop service on {server_name}"),
            ("restart", "🔄 restart", f"restart service on {server_name}"),
            ("logs", "📝 logs", f"view {server_name} logs"),
            ("backup", "💾 backup", f"backup {server_name} database"),
            ("backups", "📋 backups", f"list {server_name} backups"),
            ("ssh", "🔐 ssh", f"ssh info for {server_name}"),
            ("back", "← back", "return to server selection"),
        ]

        handlers = {
            "status": lambda: self._server_status(server_name),
            "deploy": lambda: self._server_deploy(server_name),
            "start": lambda: self._server_start(server_name),
            "stop": lambda: self._server_stop(server_name),
            "restart": lambda: self._server_restart(server_name),
            "logs": lambda: self._server_logs(server_name),
            "backup": lambda: self._server_backup(server_name),
            "backups": lambda: self._server_list_backups(server_name),
            "ssh": lambda: self._server_ssh(server_name),
        }

        return self.show_submenu(
            title=f"{server_label}",
            subtitle=f"{server_env} environment",
            options=options,
            handlers=handlers
        )

    def _server_status(self, server: str):
        """Check server status"""
        result = self.execute_command_streaming(
            ['unibos-dev', 'deploy', 'status', server],
            title=f"checking {server} status"
        )
        self.show_command_output(result)

    def _server_deploy(self, server: str):
        """Deploy to server with live streaming output"""
        result = self.execute_command_streaming(
            ['unibos-dev', 'deploy', 'run', server],
            title=f"deploying to {server}"
        )
        self.show_command_output(result)

    def _server_start(self, server: str):
        """Start server service"""
        result = self.execute_command_streaming(
            ['unibos-dev', 'deploy', 'start', server],
            title=f"starting {server}"
        )
        self.show_command_output(result)

    def _server_stop(self, server: str):
        """Stop server service"""
        result = self.execute_command_streaming(
            ['unibos-dev', 'deploy', 'stop', server],
            title=f"stopping {server}"
        )
        self.show_command_output(result)

    def _server_restart(self, server: str):
        """Restart server service"""
        result = self.execute_command_streaming(
            ['unibos-dev', 'deploy', 'restart', server],
            title=f"restarting {server}"
        )
        self.show_command_output(result)

    def _server_logs(self, server: str):
        """View server logs"""
        result = self.execute_command_streaming(
            ['unibos-dev', 'deploy', 'logs', server],
            title=f"{server} logs"
        )
        self.show_command_output(result)

    def _server_backup(self, server: str):
        """Create database backup"""
        result = self.execute_command_streaming(
            ['unibos-dev', 'deploy', 'backup', server],
            title=f"backing up {server}"
        )
        self.show_command_output(result)

    def _server_list_backups(self, server: str):
        """List available backups"""
        result = self.execute_command_streaming(
            ['unibos-dev', 'deploy', 'backups', server],
            title=f"{server} backups"
        )
        self.show_command_output(result)

    def _server_ssh(self, server: str):
        """SSH connection info"""
        self.update_content(
            title=f"ssh to {server}",
            lines=[
                f"🔐 ssh connection to {server}",
                "",
                "run this command in your terminal:",
                "",
                f"  ssh {server}",
                "",
                f"or use: unibos-dev deploy ssh {server}",
                "",
                "press esc to go back"
            ],
            color=Colors.YELLOW
        )

        sections = self.get_menu_sections()
        self._navigation_redraw(sections)

        while True:
            key = self.get_key()
            if key == 'ESC':
                break

    def handle_version_manager(self, item: MenuItem) -> bool:
        """Version control and archiving"""
        from core.version import __version__, __build__, VERSION_CODENAME

        options = [
            ("info", "📊 version info", "show detailed version information"),
            ("browse", "📋 browse archives", "view version archive history"),
            ("create", "📦 quick release", "create new version archive"),
            ("increment", "🔼 increment version", "bump version number"),
            ("analyze", "📈 archive analyzer", "analyze archive statistics"),
            ("git_status", "🔀 git status", "show git repository status"),
            ("git_tag", "🏷️  create git tag", "create and push git tag"),
            ("back", "← back", "return to dev tools"),
        ]

        handlers = {
            "info": self._version_show_info,
            "browse": self._version_browse_archives,
            "create": self._version_quick_release,
            "increment": self._version_increment,
            "analyze": self._version_analyze,
            "git_status": self._version_git_status,
            "git_tag": self._version_create_tag,
        }

        return self.show_submenu(
            title="versions",
            subtitle=f"v{__version__}+{__build__} · {VERSION_CODENAME.lower()}",
            options=options,
            handlers=handlers
        )

    def _version_show_info(self):
        """Show detailed version information - clean format"""
        from core.version import (
            __version__, __build__, parse_build_timestamp, get_archive_name,
            FEATURES, VERSION_CODENAME, RELEASE_DATE, RELEASE_TYPE
        )

        build_info = parse_build_timestamp(__build__)

        lines = [
            f"v{__version__}+build.{__build__}",
            f"{VERSION_CODENAME.lower()} · {RELEASE_TYPE.lower()} · {RELEASE_DATE}",
            "",
        ]

        if build_info:
            lines.append(f"built: {build_info['date']} {build_info['time']}")
            lines.append("")

        lines.extend([
            f"archive: {get_archive_name()}",
            "",
            "features:",
        ])

        for feature, enabled in FEATURES.items():
            status = "✓" if enabled else "·"
            lines.append(f"  {status} {feature}")

        self.update_content(title="version info", lines=lines, color=Colors.CYAN)
        self.render()

        while True:
            key = self.get_key()
            if key == 'ESC':
                break

    def _version_quick_release(self):
        """Quick release wizard - simplified"""
        from core.version import __version__, get_new_build

        parts = [int(x) for x in __version__.split('.')]
        options = [
            ("build", "📦 build", f"v{__version__} (new timestamp)"),
            ("patch", "🔧 patch", f"v{parts[0]}.{parts[1]}.{parts[2]+1}"),
            ("minor", "✨ minor", f"v{parts[0]}.{parts[1]+1}.0"),
            ("major", "🚀 major", f"v{parts[0]+1}.0.0"),
        ]

        selected = 0

        while True:
            lines = [
                f"current: v{__version__}",
                "",
            ]

            for i, (key, label, preview) in enumerate(options):
                if i == selected:
                    lines.append(f" → {label}  ·  {preview}")
                else:
                    lines.append(f"   {label}")

            self.update_content(title="quick release", lines=lines, color=Colors.CYAN)
            self.render()

            key = self.get_key()

            if key == 'UP':
                selected = (selected - 1) % len(options)
            elif key == 'DOWN':
                selected = (selected + 1) % len(options)
            elif key == 'ENTER' or key == 'RIGHT':
                self._execute_release(options[selected][0])
                return
            elif key == 'ESC' or key == 'LEFT':
                return

    def _execute_release(self, release_type: str):
        """Execute the release process using ReleasePipeline"""
        from core.profiles.dev.release_pipeline import ReleasePipeline, PipelineStep

        # Map 'build' to 'daily' for pipeline
        pipeline_type = 'daily' if release_type == 'build' else release_type

        pipeline = ReleasePipeline()
        new_version = pipeline.calculate_new_version(pipeline_type)
        new_build = pipeline.get_new_build()

        # Progress tracking
        progress_lines = []
        current_step_name = ""

        def on_step_start(step: PipelineStep):
            nonlocal current_step_name
            current_step_name = step.name

        def on_step_complete(step: PipelineStep):
            if step.status == "success":
                progress_lines.append(f"  ✓ {step.name}")
            elif step.status == "failed":
                progress_lines.append(f"  ✗ {step.name}: {step.message}")
            elif step.status == "skipped":
                progress_lines.append(f"  ○ {step.name} (skipped)")

        def on_progress(msg: str):
            nonlocal progress_lines
            # Update display
            lines = [
                f"releasing v{new_version}+build.{new_build}",
                "",
                f"  ◦ {current_step_name}..." if current_step_name else "",
            ] + progress_lines[-8:]  # Show last 8 completed steps

            self.update_content(title="release pipeline", lines=lines, color=Colors.CYAN)
            self.render()

        # Set callbacks
        pipeline.on_step_start = on_step_start
        pipeline.on_step_complete = on_step_complete
        pipeline.on_progress = on_progress

        # Show initial state
        lines = [
            f"releasing v{new_version}+build.{new_build}",
            "",
            "  preparing pipeline...",
        ]
        self.update_content(title="release pipeline", lines=lines, color=Colors.CYAN)
        self.render()

        # Run pipeline
        result = pipeline.run(
            release_type=pipeline_type,
            message=f"chore: release v{new_version}",
            repos=['dev', 'server', 'manager', 'prod'],
            dry_run=False
        )

        # Show result
        if result.success:
            lines = [
                f"✓ v{result.version}+build.{result.build}",
                "",
            ] + progress_lines + [
                "",
                f"completed in {result.duration:.1f}s",
            ]
            if result.archive_path:
                lines.append(f"archive: {result.archive_path.split('/')[-1]}")
            color = Colors.GREEN
        else:
            lines = [
                f"✗ release failed",
                "",
            ] + progress_lines + [
                "",
                f"error: {result.error}",
            ]
            color = Colors.RED

        self.update_content(title="release complete" if result.success else "release failed", lines=lines, color=color)
        self.render()

        while True:
            key = self.get_key()
            if key == 'ESC':
                if result.success:
                    # Restart TUI to reflect new version
                    self._restart_tui()
                break

    def _restart_tui(self):
        """Restart TUI to reflect updated version"""
        import os
        import sys

        # Show restart message
        self.update_content(
            title="restarting",
            lines=["", "  tui yeniden başlatılıyor...", ""],
            color=Colors.CYAN
        )
        self.render()

        # Clean up terminal
        self.cleanup()

        # Re-execute the TUI
        os.execv(sys.executable, [sys.executable] + sys.argv)

    def _version_increment(self):
        """Version increment wizard - simplified"""
        from core.version import __version__

        parts = [int(x) for x in __version__.split('.')]
        options = [
            ("patch", "🔧 patch", f"v{parts[0]}.{parts[1]}.{parts[2]+1} (bugfix)"),
            ("minor", "✨ minor", f"v{parts[0]}.{parts[1]+1}.0 (feature)"),
            ("major", "🚀 major", f"v{parts[0]+1}.0.0 (breaking)"),
        ]

        selected = 0

        while True:
            lines = [f"current: v{__version__}", ""]

            for i, (key, label, preview) in enumerate(options):
                if i == selected:
                    lines.append(f" → {label}  ·  {preview}")
                else:
                    lines.append(f"   {label}")

            self.update_content(title="increment", lines=lines, color=Colors.CYAN)
            self.render()

            key = self.get_key()

            if key == 'UP':
                selected = (selected - 1) % len(options)
            elif key == 'DOWN':
                selected = (selected + 1) % len(options)
            elif key == 'ENTER' or key == 'RIGHT':
                self._execute_release(options[selected][0])
                return
            elif key == 'ESC' or key == 'LEFT':
                return

    def _version_create_tag(self):
        """Create git tag - simplified"""
        from core.version import __version__

        lines = [
            f"tag: v{__version__}",
            "",
            "commands:",
            f"  git tag -a v{__version__} -m \"v{__version__}\"",
            f"  git push --tags",
            "",
            "or: unibos-dev git push-dev --tags"
        ]

        self.update_content(title="git tag", lines=lines, color=Colors.CYAN)
        self.render()

        while True:
            key = self.get_key()
            if key == 'ESC':
                break

    def _version_browse_archives(self):
        """Browse version archives with new format support"""
        from pathlib import Path
        import json
        import re

        archive_dir = Path("/Users/berkhatirli/Desktop/unibos-dev/archive/versions")

        if not archive_dir.exists():
            self.update_content(
                title="browse archives",
                lines=[
                    "   archive directory not found",
                    "",
                    f"expected location: {archive_dir}",
                    "",
                    "press esc to continue"
                ],
                color=Colors.YELLOW
            )
            self.render()
            return

        # Find all archives - both old and new format
        archives = []

        # Scan archive directory
        for item in sorted(archive_dir.iterdir(), reverse=True):
            if item.is_dir():
                archive_info = {
                    'path': item,
                    'name': item.name,
                    'version': 'unknown',
                    'build': None,
                    'date': None,
                    'format': 'unknown'
                }

                # Try to read VERSION.json
                version_file = item / 'VERSION.json'
                if version_file.exists():
                    try:
                        with open(version_file) as f:
                            data = json.load(f)

                            # New format (v1.0.0+)
                            if 'version' in data and isinstance(data['version'], dict):
                                v = data['version']
                                archive_info['version'] = f"{v.get('major', 0)}.{v.get('minor', 0)}.{v.get('patch', 0)}"
                                archive_info['build'] = v.get('build')
                                archive_info['format'] = 'new'
                                if 'build_info' in data:
                                    archive_info['date'] = data['build_info'].get('date')
                            # Old format
                            else:
                                archive_info['version'] = data.get('version', 'unknown')
                                archive_info['build'] = data.get('build_number') or data.get('build')
                                archive_info['date'] = data.get('release_date', '')[:10] if data.get('release_date') else None
                                archive_info['format'] = 'old'
                    except:
                        pass

                # Parse version from directory name if not found in VERSION.json
                if archive_info['version'] == 'unknown':
                    # New format: unibos_v1.0.0_b20251201222554
                    new_match = re.match(r'unibos_v(\d+\.\d+\.\d+)_b(\d{14})', item.name)
                    if new_match:
                        archive_info['version'] = new_match.group(1)
                        archive_info['build'] = new_match.group(2)
                        archive_info['format'] = 'new'
                    else:
                        # Old format: unibos_v534_20251116_...
                        old_match = re.match(r'unibos_v(\d+)_(\d{8})', item.name)
                        if old_match:
                            archive_info['version'] = f"0.{old_match.group(1)}.0"
                            archive_info['date'] = f"{old_match.group(2)[:4]}-{old_match.group(2)[4:6]}-{old_match.group(2)[6:8]}"
                            archive_info['format'] = 'old'

                archives.append(archive_info)

        # Build display - simplified
        lines = [f"{len(archives)} archives", ""]

        if archives:
            for i, archive in enumerate(archives[:15]):  # Show last 15
                if archive['format'] == 'new' and archive['build']:
                    b = archive['build']
                    if len(b) == 14:
                        lines.append(f"  v{archive['version']} · {b[0:4]}-{b[4:6]}-{b[6:8]} {b[8:10]}:{b[10:12]}")
                    else:
                        lines.append(f"  v{archive['version']} · b{archive['build']}")
                else:
                    date_str = archive['date'] or ''
                    lines.append(f"  v{archive['version']} · {date_str}")

            if len(archives) > 15:
                lines.extend(["", f"  +{len(archives) - 15} more"])
        else:
            lines.append("  no archives found")

        self.update_content(title="archives", lines=lines, color=Colors.CYAN)
        self.render()

        while True:
            key = self.get_key()
            if key == 'ESC':
                break

    def _version_analyze(self):
        """Analyze archives with statistics - simplified"""
        from pathlib import Path

        archive_dir = Path("/Users/berkhatirli/Desktop/unibos-dev/archive/versions")

        def format_size(size):
            if size >= 1024 * 1024 * 1024:
                return f"{size / (1024*1024*1024):.1f}gb"
            elif size >= 1024 * 1024:
                return f"{size / (1024*1024):.1f}mb"
            elif size >= 1024:
                return f"{size / 1024:.1f}kb"
            return f"{size}b"

        if not archive_dir.exists():
            lines = ["archive directory not found"]
        else:
            total_size = 0
            sizes = []

            for item in archive_dir.iterdir():
                if item.is_dir():
                    dir_size = sum(f.stat().st_size for f in item.rglob('*') if f.is_file())
                    total_size += dir_size
                    sizes.append((item.name, dir_size))

            lines = [
                f"{len(sizes)} archives · {format_size(total_size)} total",
                "",
            ]

            if sizes:
                avg_size = total_size / len(sizes)
                lines.append(f"avg: {format_size(int(avg_size))}")
                lines.append("")

                sizes.sort(key=lambda x: x[1], reverse=True)
                lines.append("largest:")
                for name, size in sizes[:5]:
                    short_name = name[:35] + "..." if len(name) > 38 else name
                    lines.append(f"  {format_size(size):>8} {short_name}")

                anomalies = [s for s in sizes if s[1] > avg_size * 2]
                if anomalies:
                    lines.extend(["", f"⚠ {len(anomalies)} anomalies (>2x avg)"])

        self.update_content(title="analyzer", lines=lines, color=Colors.CYAN)
        self.render()

        while True:
            key = self.get_key()
            if key == 'ESC':
                break

    def _version_git_status(self):
        """show git status - simplified"""
        import subprocess
        from pathlib import Path

        project_root = Path(__file__).parent.parent.parent.parent

        self.update_content(title="git status", lines=["loading..."], color=Colors.CYAN)
        self.render()

        try:
            # Get git status
            result = subprocess.run(
                ['git', 'status', '--short', '--branch'],
                capture_output=True, text=True, cwd=project_root
            )

            lines = []

            # Parse branch info
            status_lines = result.stdout.strip().split('\n') if result.stdout.strip() else []

            if status_lines:
                branch_line = status_lines[0]
                lines.append(f"branch: {branch_line.replace('## ', '')}")
                lines.append("")

                # File changes
                changes = status_lines[1:] if len(status_lines) > 1 else []
                if changes:
                    lines.append(f"changes ({len(changes)}):")
                    for change in changes[:15]:  # Limit to 15 lines
                        lines.append(f"  {change}")
                    if len(changes) > 15:
                        lines.append(f"  ... and {len(changes) - 15} more")
                else:
                    lines.append("✓ working tree clean")

            # Get recent commits
            commits_result = subprocess.run(
                ['git', 'log', '--oneline', '-5'],
                capture_output=True, text=True, cwd=project_root
            )

            if commits_result.stdout.strip():
                lines.append("")
                lines.append("recent commits:")
                for commit in commits_result.stdout.strip().split('\n'):
                    lines.append(f"  {commit}")

            self.update_content(title="git status", lines=lines, color=Colors.CYAN)
            self.render()

        except Exception as e:
            self.update_content(
                title="git status",
                lines=[f"error: {e}"],
                color=Colors.RED
            )
            self.render()

        # Wait for key
        while True:
            key = self.get_key()
            if key == 'ESC':
                break

def run_interactive():
    """Run the dev TUI"""
    tui = UnibosDevTUI()
    tui.run()


if __name__ == "__main__":
    run_interactive()
