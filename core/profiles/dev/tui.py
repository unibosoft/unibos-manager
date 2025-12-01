"""
UNIBOS-DEV TUI - v527 Structure
Development TUI with 3-section layout: modules, tools, dev tools
"""

import subprocess
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

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
            version=get_short_version_string(),  # Dynamic: "v1.0.0 @22:25"
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

    def load_module_metadata(self, module_path: Path) -> Optional[Dict[str, Any]]:
        """
        Load module metadata from module.json file

        Args:
            module_path: Path to the module directory

        Returns:
            Dictionary containing module metadata, or None if not found/invalid
        """
        module_json_path = module_path / 'module.json'

        if not module_json_path.exists():
            return None

        try:
            with open(module_json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            # Log error but continue - module can still be discovered
            return None

    def discover_modules(self) -> List[MenuItem]:
        """
        Discover installed modules dynamically

        Modules are identified by:
        - .enabled file (indicates module is enabled)
        - backend/ directory (contains Django app)
        - module.json file (optional, contains metadata)

        Returns:
            List of MenuItem objects for each discovered module
        """
        modules_dir = Path("/Users/berkhatirli/Desktop/unibos-dev/modules")
        modules = []

        if modules_dir.exists():
            for module_path in sorted(modules_dir.iterdir()):
                if module_path.is_dir() and not module_path.name.startswith('_'):
                    # Check if module has .enabled file to be valid
                    if (module_path / '.enabled').exists():
                        # Try to load module metadata from module.json
                        metadata = self.load_module_metadata(module_path)

                        # Extract metadata or use defaults
                        if metadata:
                            module_name = metadata.get('name', module_path.name)
                            module_icon = metadata.get('icon', '📦')
                            module_desc = metadata.get('description', f'Launch {module_name} module')
                            module_version = metadata.get('version', 'unknown')

                            # Get display name (use English if available)
                            display_name_data = metadata.get('display_name')
                            if isinstance(display_name_data, dict):
                                display_name = display_name_data.get('en', module_name)
                            else:
                                display_name = module_name

                            # Build feature list
                            features = metadata.get('features', [])
                            feature_list = ''
                            if isinstance(features, list) and features:
                                feature_list = '\n'.join([f'  • {f}' for f in features[:5]])  # Limit to 5 features
                                if len(features) > 5:
                                    feature_list += f'\n  • ... and {len(features) - 5} more'

                            # Build description
                            description_parts = [
                                f'{module_desc.lower()}\n',
                            ]

                            if feature_list:
                                description_parts.append('key features:')
                                description_parts.append(feature_list.lower())

                            description = '\n'.join(description_parts)

                            # Use short module name (just the ID) for sidebar
                            # This keeps labels concise and fits in 25 char width
                            label = module_name.lower()
                        else:
                            # Fallback to basic info if no metadata
                            label = module_path.name
                            module_icon = '📦'
                            description = (
                                f'launch {module_path.name} module\n\n'
                                f'no metadata file found'
                            )

                        modules.append(MenuItem(
                            id=f"module_{module_path.name}",
                            label=label,
                            icon=module_icon,
                            description=description,
                            enabled=True
                        ))

        # If no modules found, add placeholder
        if not modules:
            modules.append(MenuItem(
                id='no_modules',
                label='📦 no modules found',
                icon='',
                description='No enabled modules are currently installed.\n\n'
                           'Modules should be placed in:\n'
                           '/modules/\n\n'
                           'Each module must have:\n'
                           '  • .enabled file (marks module as enabled)\n'
                           '  • backend/ directory (Django app)\n'
                           '  • module.json file (optional metadata)',
                enabled=False
            ))

        return modules

    def get_menu_sections(self) -> List[MenuSection]:
        """Get development menu sections - v527 structure"""
        return [
            # Section 1: Modules (dynamically discovered)
            MenuSection(
                id='modules',
                label='modules',
                icon='📦',
                items=self.discover_modules()
            ),

            # Section 2: Tools (7 items)
            MenuSection(
                id='tools',
                label='tools',
                icon='🔧',
                items=[
                    MenuItem(
                        id='system_scrolls',
                        label=self.i18n.translate('menu.scrolls'),
                        icon='📜',
                        description='forge status & info\n\n'
                                   '→ system information\n'
                                   '→ version details\n'
                                   '→ service status\n'
                                   '→ resource usage\n\n'
                                   'complete system overview',
                        enabled=True
                    ),
                    MenuItem(
                        id='castle_guard',
                        label='🛡️  ' + self.i18n.translate('menu.guard'),
                        icon='',
                        description='fortress security\n\n'
                                   '→ security status\n'
                                   '→ access controls\n'
                                   '→ authentication logs\n'
                                   '→ firewall settings\n\n'
                                   'security management interface',
                        enabled=True
                    ),
                    MenuItem(
                        id='forge_smithy',
                        label='🔨 ' + self.i18n.translate('menu.smithy'),
                        icon='',
                        description='setup forge tools\n\n'
                                   '→ install dependencies\n'
                                   '→ configure environment\n'
                                   '→ setup database\n'
                                   '→ initialize services\n\n'
                                   'complete system setup wizard',
                        enabled=True
                    ),
                    MenuItem(
                        id='anvil_repair',
                        label='⚒️  ' + self.i18n.translate('menu.repair'),
                        icon='',
                        description='mend & fix issues\n\n'
                                   '→ diagnostic tools\n'
                                   '→ repair utilities\n'
                                   '→ log analysis\n'
                                   '→ recovery options\n\n'
                                   'system repair and maintenance',
                        enabled=True
                    ),
                    MenuItem(
                        id='code_forge',
                        label='⚙️  ' + self.i18n.translate('menu.git'),
                        icon='',
                        description='version chronicles\n\n'
                                   '→ git operations\n'
                                   '→ version control\n'
                                   '→ commit history\n'
                                   '→ branch management\n\n'
                                   'source code management',
                        enabled=True
                    ),
                    CommonItems.web_ui(self.i18n),
                    CommonItems.administration(self.i18n),
                ]
            ),

            # Section 3: Dev Tools (5 items)
            MenuSection(
                id='dev_tools',
                label='dev tools',
                icon='🛠️',
                items=[
                    MenuItem(
                        id='ai_builder',
                        label='🤖 ' + self.i18n.translate('menu.ai_builder'),
                        icon='',
                        description='ai-powered development\n\n'
                                   '→ code generation\n'
                                   '→ ai assistance\n'
                                   '→ smart refactoring\n'
                                   '→ documentation generation\n\n'
                                   'ai development tools',
                        enabled=True
                    ),
                    CommonItems.database_setup(self.i18n, profile_type='dev'),
                    MenuItem(
                        id='public_server',
                        label='🌍 ' + self.i18n.translate('menu.deployment'),
                        icon='',
                        description='deploy to ubuntu/oracle vm\n\n'
                                   '→ deploy to rocksteady\n'
                                   '→ ssh to server\n'
                                   '→ server management\n'
                                   '→ production deployment\n\n'
                                   'public server deployment',
                        enabled=True
                    ),
                    MenuItem(
                        id='sd_card',
                        label=self.i18n.translate('menu.sd_card'),
                        icon='💾',
                        description='sd operations\n\n'
                                   '→ format sd card\n'
                                   '→ create bootable image\n'
                                   '→ backup/restore\n'
                                   '→ partition management\n\n'
                                   'sd card utilities',
                        enabled=True
                    ),
                    MenuItem(
                        id='version_manager',
                        label=self.i18n.translate('menu.versions'),
                        icon='📋',
                        description='archive & git tools\n\n'
                                   '→ create version archives\n'
                                   '→ browse archive history\n'
                                   '→ restore versions\n'
                                   '→ git integration\n\n'
                                   'version control and archiving',
                        enabled=True
                    ),
                ]
            ),
        ]

    def register_dev_handlers(self):
        """Register all development action handlers"""
        # Tools section handlers
        self.register_action('system_scrolls', self.handle_system_scrolls)
        self.register_action('castle_guard', self.handle_castle_guard)
        self.register_action('forge_smithy', self.handle_forge_smithy)
        self.register_action('anvil_repair', self.handle_anvil_repair)
        self.register_action('code_forge', self.handle_code_forge)
        self.register_action('web_ui', self.handle_web_ui)
        self.register_action('administration', self.handle_administration)

        # Dev tools section handlers
        self.register_action('ai_builder', self.handle_ai_builder)
        self.register_action('database_setup', self.handle_database_setup)
        self.register_action('public_server', self.handle_public_server)
        self.register_action('sd_card', self.handle_sd_card)
        self.register_action('version_manager', self.handle_version_manager)

    # ===== TOOLS SECTION HANDLERS =====

    def handle_system_scrolls(self, item: MenuItem) -> bool:
        """show system status and information"""
        self.update_content(
            title="system scrolls",
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
                title="system scrolls - error",
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

    def handle_castle_guard(self, item: MenuItem) -> bool:
        """Security management"""
        self.update_content(
            title="castle guard - security tools",
            lines=[
                "🛡️ security management",
                "",
                "available security tools:",
                "",
                "→ firewall status",
                "→ ssh configuration",
                "→ ssl certificates",
                "→ access logs",
                "→ failed login attempts",
                "",
                "🚧 this feature is under development.",
                "",
                "security tools will include:",
                "  • system firewall management",
                "  • ssh key management",
                "  • ssl/tls certificate monitoring",
                "  • security audit logging",
                "  • intrusion detection",
                "",
                "press esc to return to menu"
            ],
            color=Colors.YELLOW
        )
        self.render()
        return True

    def handle_forge_smithy(self, item: MenuItem) -> bool:
        """System setup wizard"""
        self.update_content(
            title="forge smithy - setup wizard",
            lines=[
                "🔨 System Setup Wizard",
                "",
                "this wizard helps you set up UNIBOS from scratch.",
                "",
                "setup steps:",
                "",
                "1. Environment Check",
                "   → Python version",
                "   → Required packages",
                "   → System dependencies",
                "",
                "2. Database Setup",
                "   → PostgreSQL installation",
                "   → Database creation",
                "   → Run migrations",
                "",
                "3. Configuration",
                "   → Environment variables",
                "   → Settings files",
                "   → Secret keys",
                "",
                "4. Services",
                "   → Redis setup",
                "   → Background workers",
                "   → Django server",
                "",
                "🚧 Full wizard coming soon!",
                "",
                "for now, use:",
                "  • database setup (in dev tools)",
                "  • unibos-dev status (for checks)",
                "",
                "press esc to return to menu"
            ],
            color=Colors.CYAN
        )
        self.render()
        return True

    def handle_anvil_repair(self, item: MenuItem) -> bool:
        """System repair and maintenance"""
        self.update_content(
            title="anvil repair - diagnostics & repair",
            lines=[
                "⚒️ System Diagnostics & Repair Tools",
                "",
                "diagnostic tools:",
                "",
                "→ check system health",
                "→ verify database integrity",
                "→ test network connectivity",
                "→ validate file permissions",
                "→ analyze log files",
                "",
                "repair tools:",
                "",
                "→ fix database issues",
                "→ repair corrupted files",
                "→ reset configurations",
                "→ clear cache",
                "→ rebuild indexes",
                "",
                "🚧 This feature is under development.",
                "",
                "available now:",
                "  • unibos-dev status (health check)",
                "  • django management commands",
                "  • database migrations",
                "",
                "press esc to return to menu"
            ],
            color=Colors.YELLOW
        )
        self.render()
        return True

    def handle_code_forge(self, item: MenuItem) -> bool:
        """Git and version control"""
        self.update_content(
            title="code forge - git operations",
            lines=["📊 Loading git status...", ""],
            color=Colors.CYAN
        )
        self.render()

        try:
            # Show git status
            result = self.execute_command(['unibos-dev', 'git', 'status'])

            # Build content with git commands
            lines = ["⚙️ Git Status", "", ""]

            # Add command output
            if result.returncode == 0:
                lines.extend(result.stdout.strip().split('\n'))
            else:
                lines.append("❌ Failed to get git status")
                if result.stderr:
                    lines.extend(result.stderr.strip().split('\n'))

            lines.extend([
                "",
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                "",
                "available Git Commands:",
                "",
                "  unibos-dev git status        - Show git status",
                "  unibos-dev git push-dev      - Push to dev repo",
                "  unibos-dev git sync-prod     - Sync to prod directory",
                "  unibos-dev git commit        - Create commit",
                "",
                "run these commands from terminal for full git control.",
                "",
                "press esc to return to menu"
            ])

            self.update_content(
                title="code forge - git operations",
                lines=lines,
                color=Colors.CYAN
            )
            self.render()

        except Exception as e:
            self.update_content(
                title="code forge - error",
                lines=[
                    "❌ Failed to execute git command",
                    "",
                    f"Error: {str(e)}",
                    "",
                    "Try running: unibos-dev git status"
                ],
                color=Colors.RED
            )
            self.render()

        return True

    def handle_web_ui(self, item: MenuItem) -> bool:
        """Web interface management - Interactive submenu"""
        return self._show_web_ui_submenu()

    def _show_web_ui_submenu(self) -> bool:
        """show interactive Web UI submenu"""
        import time

        # Menu options
        options = [
            ("start", "🚀 Start Django Server", "Start the development server"),
            ("stop", "⏹️ Stop Django Server", "Stop the running server"),
            ("status", "📊 Server Status", "check if server is running"),
            ("logs", "📝 View Server Logs", "show recent server logs"),
            ("migrate", "🔄 Run Migrations", "Apply database migrations"),
            ("back", "← Back to Tools", "return to main menu"),
        ]

        selected = 0

        while True:
            # Build menu display
            lines = [
                "🌐 Web UI Management",
                "",
                "Select an option:",
                ""
            ]

            for i, (key, label, desc) in enumerate(options):
                if i == selected:
                    lines.append(f"  → {label}")
                    lines.append(f"    {desc}")
                else:
                    lines.append(f"    {label}")
                lines.append("")

            lines.extend([
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                "",
                "navigation: ↑↓ to move, Enter to select, ESC to go back"
            ])

            self.update_content(
                title="web ui management",
                lines=lines,
                color=Colors.CYAN
            )
            self.render()

            # Get input
            key = self.get_key()

            if key == 'UP':
                selected = (selected - 1) % len(options)
            elif key == 'DOWN':
                selected = (selected + 1) % len(options)
            elif key == 'ENTER':
                option_key = options[selected][0]

                if option_key == 'back':
                    return True
                elif option_key == 'start':
                    self._web_ui_start_server()
                elif option_key == 'stop':
                    self._web_ui_stop_server()
                elif option_key == 'status':
                    self._web_ui_show_status()
                elif option_key == 'logs':
                    self._web_ui_show_logs()
                elif option_key == 'migrate':
                    self._web_ui_run_migrations()

                # Wait for user to read output
                time.sleep(0.5)
            elif key == 'ESC':
                return True

        return True

    def _web_ui_start_server(self):
        """start django development server"""
        self.update_content(
            title="starting django server",
            lines=["🚀 Starting development server...", ""],
            color=Colors.CYAN
        )
        self.render()

        result = self.execute_command(['unibos-dev', 'dev', 'run'])
        self.show_command_output(result)

    def _web_ui_stop_server(self):
        """stop django development server"""
        self.update_content(
            title="stopping django server",
            lines=["⏹️ Stopping development server...", ""],
            color=Colors.CYAN
        )
        self.render()

        result = self.execute_command(['unibos-dev', 'dev', 'stop'])
        self.show_command_output(result)

    def _web_ui_show_status(self):
        """show Django server status"""
        self.update_content(
            title="django server status",
            lines=["📊 Checking server status...", ""],
            color=Colors.CYAN
        )
        self.render()

        result = self.execute_command(['unibos-dev', 'dev', 'status'])
        self.show_command_output(result)

    def _web_ui_show_logs(self):
        """show Django server logs"""
        self.update_content(
            title="django server logs",
            lines=["📝 Loading server logs...", ""],
            color=Colors.CYAN
        )
        self.render()

        result = self.execute_command(['unibos-dev', 'dev', 'logs'])
        self.show_command_output(result)

    def _web_ui_run_migrations(self):
        """Run Django migrations"""
        self.update_content(
            title="running migrations",
            lines=["🔄 Running database migrations...", ""],
            color=Colors.CYAN
        )
        self.render()

        result = self.execute_command(['unibos-dev', 'dev', 'migrate'])
        self.show_command_output(result)

    def handle_administration(self, item: MenuItem) -> bool:
        """System administration"""
        self.update_content(
            title="administration - system management",
            lines=[
                "👑 System Administration",
                "",
                "administration tools:",
                "",
                "→ user management",
                "  • create/delete users",
                "  • manage permissions",
                "  • reset passwords",
                "",
                "→ system settings",
                "  • environment configuration",
                "  • feature flags",
                "  • api settings",
                "",
                "→ module management",
                "  • enable/disable modules",
                "  • module configuration",
                "  • module permissions",
                "",
                "→ monitoring",
                "  • system logs",
                "  • performance metrics",
                "  • error tracking",
                "",
                "🚧 This feature is under development.",
                "",
                "for now, use Django admin:",
                "  1. Start server: unibos-dev dev run",
                "  2. Visit: http://localhost:8000/admin",
                "",
                "press esc to return to menu"
            ],
            color=Colors.YELLOW
        )
        self.render()
        return True

    # ===== DEV TOOLS SECTION HANDLERS =====

    def handle_ai_builder(self, item: MenuItem) -> bool:
        """AI-powered development tools"""
        self.update_content(
            title="ai builder - ai development tools",
            lines=[
                "🤖 AI-Powered Development",
                "",
                "the ai builder provides intelligent code assistance and generation.",
                "",
                "Features:",
                "",
                "→ code generation",
                "  • generate boilerplate code",
                "  • create test cases",
                "  • generate documentation",
                "",
                "→ ai assistance",
                "  • code completion",
                "  • bug detection",
                "  • code review suggestions",
                "",
                "→ smart refactoring",
                "  • optimize code structure",
                "  • improve performance",
                "  • apply best practices",
                "",
                "→ documentation",
                "  • auto-generate docstrings",
                "  • create readme files",
                "  • api documentation",
                "",
                "🚧 This feature is under development.",
                "",
                "for now, you can use:",
                "  • claude code cli (if installed)",
                "  • github copilot",
                "  • chatgpt for code assistance",
                "",
                "press esc to return to menu"
            ],
            color=Colors.MAGENTA
        )
        self.render()
        return True

    def handle_database_setup(self, item: MenuItem) -> bool:
        """PostgreSQL installation wizard"""
        return self._show_database_setup_submenu()

    def _show_database_setup_submenu(self) -> bool:
        """show interactive Database Setup submenu"""
        import time

        # Menu options
        options = [
            ("check", "🔍 Check Database Status", "check if PostgreSQL is installed and running"),
            ("install", "📥 Install PostgreSQL", "install postgresql using Homebrew (macOS)"),
            ("create", "🗄️ Create Database", "create UNIBOS database"),
            ("migrate", "🔄 Run Migrations", "apply django migrations"),
            ("backup", "💾 Backup Database", "create database backup"),
            ("restore", "♻️ Restore Database", "restore from backup"),
            ("back", "← Back to Dev Tools", "return to main menu"),
        ]

        selected = 0

        while True:
            # Build menu display
            lines = [
                "🗄️ Database Setup Wizard",
                "",
                "PostgreSQL Database Management:",
                ""
            ]

            for i, (key, label, desc) in enumerate(options):
                if i == selected:
                    lines.append(f"  → {label}")
                    lines.append(f"    {desc}")
                else:
                    lines.append(f"    {label}")
                lines.append("")

            lines.extend([
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                "",
                "navigation: ↑↓ to move, Enter to select, ESC to go back"
            ])

            self.update_content(
                title="database setup wizard",
                lines=lines,
                color=Colors.CYAN
            )
            self.render()

            # Get input
            key = self.get_key()

            if key == 'UP':
                selected = (selected - 1) % len(options)
            elif key == 'DOWN':
                selected = (selected + 1) % len(options)
            elif key == 'ENTER':
                option_key = options[selected][0]

                if option_key == 'back':
                    return True
                elif option_key == 'check':
                    self._db_check_status()
                elif option_key == 'install':
                    self._db_install_postgresql()
                elif option_key == 'create':
                    self._db_create_database()
                elif option_key == 'migrate':
                    self._db_run_migrations()
                elif option_key == 'backup':
                    self._db_backup()
                elif option_key == 'restore':
                    self._db_restore()

                # Wait for user to read output
                time.sleep(0.5)
            elif key == 'ESC':
                return True

        return True

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

    def handle_public_server(self, item: MenuItem) -> bool:
        """deploy to public server"""
        return self._show_public_server_submenu()

    def _show_public_server_submenu(self) -> bool:
        """show interactive Public Server submenu"""
        import time

        # Menu options
        options = [
            ("status", "📊 Server Status", "check rocksteady server status"),
            ("deploy", "🚀 Deploy to Rocksteady", "deploy unibos to production server"),
            ("ssh", "🔐 SSH to Server", "open ssh connection to rocksteady"),
            ("logs", "📝 View Server Logs", "show production server logs"),
            ("backup", "💾 Backup Server", "create server backup"),
            ("back", "← Back to Dev Tools", "return to main menu"),
        ]

        selected = 0

        while True:
            # Build menu display
            lines = [
                "🌍 Public Server Management",
                "",
                "Ubuntu/Oracle VM (rocksteady) Deployment:",
                ""
            ]

            for i, (key, label, desc) in enumerate(options):
                if i == selected:
                    lines.append(f"  → {label}")
                    lines.append(f"    {desc}")
                else:
                    lines.append(f"    {label}")
                lines.append("")

            lines.extend([
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                "",
                "navigation: ↑↓ to move, Enter to select, ESC to go back"
            ])

            self.update_content(
                title="public server management",
                lines=lines,
                color=Colors.CYAN
            )
            self.render()

            # Get input
            key = self.get_key()

            if key == 'UP':
                selected = (selected - 1) % len(options)
            elif key == 'DOWN':
                selected = (selected + 1) % len(options)
            elif key == 'ENTER':
                option_key = options[selected][0]

                if option_key == 'back':
                    return True
                elif option_key == 'status':
                    self._server_check_status()
                elif option_key == 'deploy':
                    self._server_deploy()
                elif option_key == 'ssh':
                    self._server_ssh()
                elif option_key == 'logs':
                    self._server_logs()
                elif option_key == 'backup':
                    self._server_backup()

                # Wait for user to read output
                time.sleep(0.5)
            elif key == 'ESC':
                return True

        return True

    def _server_check_status(self):
        """Check server status"""
        self.update_content(
            title="server status",
            lines=["📊 Checking rocksteady server status...", ""],
            color=Colors.CYAN
        )
        self.render()

        result = self.execute_command(['unibos-dev', 'deploy', 'status', 'rocksteady'])
        self.show_command_output(result)

    def _server_deploy(self):
        """deploy to server"""
        self.update_content(
            title="deploying to rocksteady",
            lines=["🚀 Deploying UNIBOS to production server...", ""],
            color=Colors.CYAN
        )
        self.render()

        result = self.execute_command(['unibos-dev', 'deploy', 'rocksteady'])
        self.show_command_output(result)

    def _server_ssh(self):
        """ssh to server"""
        self.update_content(
            title="ssh connection",
            lines=[
                "🔐 Opening SSH connection to rocksteady...",
                "",
                "run this command in your terminal:",
                "",
                "  ssh rocksteady",
                "",
                "or use the deploy command for full options.",
                "",
                "press esc to continue"
            ],
            color=Colors.YELLOW
        )
        self.render()

    def _server_logs(self):
        """View server logs"""
        self.update_content(
            title="server logs",
            lines=["📝 Fetching server logs...", ""],
            color=Colors.CYAN
        )
        self.render()

        result = self.execute_command(['unibos-dev', 'deploy', 'logs', 'rocksteady'])
        self.show_command_output(result)

    def _server_backup(self):
        """Backup server"""
        self.update_content(
            title="server backup",
            lines=["💾 Creating server backup...", ""],
            color=Colors.CYAN
        )
        self.render()

        result = self.execute_command(['unibos-dev', 'deploy', 'backup', 'rocksteady'])
        self.show_command_output(result)

    def handle_sd_card(self, item: MenuItem) -> bool:
        """SD card operations"""
        self.update_content(
            title="sd card operations",
            lines=[
                "💾 SD Card Utilities",
                "",
                "SD card management for Raspberry Pi and other devices.",
                "",
                "available Operations:",
                "",
                "→ format sd card",
                "  • format for raspberry pi",
                "  • create boot partition",
                "  • set up file system",
                "",
                "→ create bootable image",
                "  • flash raspberry pi os",
                "  • flash custom images",
                "  • verify image integrity",
                "",
                "→ backup/restore",
                "  • create sd card backup",
                "  • restore from backup",
                "  • clone sd cards",
                "",
                "→ partition management",
                "  • view partitions",
                "  • resize partitions",
                "  • create new partitions",
                "",
                "🚧 This feature is under development.",
                "",
                "for now, use:",
                "  • raspberry pi imager (gui tool)",
                "  • dd command (advanced users)",
                "  • balenaEtcher",
                "",
                "press esc to return to menu"
            ],
            color=Colors.YELLOW
        )
        self.render()
        return True

    def handle_version_manager(self, item: MenuItem) -> bool:
        """Version control and archiving"""
        return self._show_version_manager_submenu()

    def _show_version_manager_submenu(self) -> bool:
        """show interactive Version Manager submenu"""
        import time
        from pathlib import Path
        from core.version import (
            __version__, __build__, get_full_version,
            parse_build_timestamp, get_archive_name, RELEASE_TYPE, VERSION_CODENAME
        )

        # Check if archive directory exists
        archive_dir = Path("/Users/berkhatirli/Desktop/unibos-dev/archive/versions")
        archive_exists = archive_dir.exists()

        # Menu options
        options = [
            ("info", "📊 Current Version Info", "show detailed version information"),
            ("browse", "📋 Browse Archives", "view version archive history"),
            ("create", "📦 Quick Release", "create new version archive with wizard"),
            ("increment", "🔼 Increment Version", "bump version number"),
            ("analyze", "📈 Archive Analyzer", "analyze archive statistics"),
            ("git_status", "🔀 Git Status", "show git repository status"),
            ("git_tag", "🏷️  Create Git Tag", "create and push git tag"),
            ("back", "← Back to Dev Tools", "return to main menu"),
        ]

        selected = 0

        while True:
            # Get current version info
            build_info = parse_build_timestamp(__build__)
            build_display = build_info['short'] if build_info else __build__

            # Build menu display
            lines = [
                "📋 Version Manager",
                "",
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                f"  current: v{__version__} {build_display}",
                f"  codename: {VERSION_CODENAME}",
                f"  type: {RELEASE_TYPE}",
            ]

            if build_info:
                lines.append(f"  built: {build_info['date']} {build_info['time']}")

            lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            lines.append("")

            for i, (key, label, desc) in enumerate(options):
                if i == selected:
                    lines.append(f"  → {label}")
                    lines.append(f"    {desc}")
                else:
                    lines.append(f"    {label}")
                lines.append("")

            lines.extend([
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                "",
                "navigation: ↑↓ to move, Enter to select, ESC to go back"
            ])

            self.update_content(
                title="version manager",
                lines=lines,
                color=Colors.CYAN
            )
            self.render()

            # Get input
            key = self.get_key()

            if key == 'UP':
                selected = (selected - 1) % len(options)
            elif key == 'DOWN':
                selected = (selected + 1) % len(options)
            elif key == 'ENTER':
                option_key = options[selected][0]

                if option_key == 'back':
                    return True
                elif option_key == 'info':
                    self._version_show_info()
                elif option_key == 'browse':
                    self._version_browse_archives()
                elif option_key == 'create':
                    self._version_quick_release()
                elif option_key == 'increment':
                    self._version_increment()
                elif option_key == 'analyze':
                    self._version_analyze()
                elif option_key == 'git_status':
                    self._version_git_status()
                elif option_key == 'git_tag':
                    self._version_create_tag()

                # Wait for user to read output
                time.sleep(0.5)
            elif key == 'ESC':
                return True

        return True

    def _version_show_info(self):
        """Show detailed version information"""
        from core.version import (
            __version__, __build__, get_full_version, get_version_string,
            parse_build_timestamp, get_archive_name, FEATURES, DEVELOPMENT_HISTORY,
            VERSION_NAME, VERSION_CODENAME, RELEASE_DATE, RELEASE_TYPE,
            NEXT_VERSION, NEXT_RELEASE_NAME
        )

        build_info = parse_build_timestamp(__build__)

        lines = [
            "📊 Current Version Information",
            "",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            "",
            "  version details:",
            f"    semantic:  v{__version__}",
            f"    build:     {__build__}",
            f"    full:      v{__version__}+build.{__build__}",
            "",
            f"    name:      {VERSION_NAME}",
            f"    codename:  {VERSION_CODENAME}",
            f"    type:      {RELEASE_TYPE}",
            f"    date:      {RELEASE_DATE}",
            "",
        ]

        if build_info:
            lines.extend([
                "  build timestamp:",
                f"    date:      {build_info['date']}",
                f"    time:      {build_info['time']}",
                f"    readable:  {build_info['readable']}",
                "",
            ])

        lines.extend([
            "  archive:",
            f"    name:      {get_archive_name()}",
            "",
            "  development history:",
            f"    total iterations: {DEVELOPMENT_HISTORY.get('total_iterations', 'N/A')}",
            f"    version range:    {DEVELOPMENT_HISTORY.get('version_range', 'N/A')}",
            "",
            "  next milestone:",
            f"    version:   {NEXT_VERSION}",
            f"    name:      {NEXT_RELEASE_NAME}",
            "",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            "",
            "  enabled features:",
        ])

        for feature, enabled in FEATURES.items():
            status = "+" if enabled else "-"
            lines.append(f"    {status} {feature}")

        lines.extend([
            "",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            "",
            "press esc to continue"
        ])

        self.update_content(
            title="version information",
            lines=lines,
            color=Colors.CYAN
        )
        self.render()

    def _version_quick_release(self):
        """Quick release wizard"""
        import time
        from core.version import __version__, __build__, get_archive_name, get_new_build

        # Release type options
        options = [
            ("build", "📦 Build Only", "new build, same version (daily work)"),
            ("patch", "🔧 Patch Release", "bug fix (v1.0.0 → v1.0.1)"),
            ("minor", "✨ Minor Release", "new feature (v1.0.0 → v1.1.0)"),
            ("major", "🚀 Major Release", "breaking change (v1.0.0 → v2.0.0)"),
            ("back", "← Cancel", "return without changes"),
        ]

        selected = 0

        while True:
            new_build = get_new_build()

            lines = [
                "📦 Quick Release Wizard",
                "",
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                f"  current version: v{__version__}",
                f"  current build:   {__build__}",
                f"  new build:       {new_build}",
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                "",
                "  select release type:",
                ""
            ]

            for i, (key, label, desc) in enumerate(options):
                if i == selected:
                    lines.append(f"  → {label}")
                    lines.append(f"    {desc}")
                else:
                    lines.append(f"    {label}")
                lines.append("")

            lines.extend([
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                "",
                "navigation: ↑↓ to move, Enter to select, ESC to cancel"
            ])

            self.update_content(
                title="quick release",
                lines=lines,
                color=Colors.CYAN
            )
            self.render()

            key = self.get_key()

            if key == 'UP':
                selected = (selected - 1) % len(options)
            elif key == 'DOWN':
                selected = (selected + 1) % len(options)
            elif key == 'ENTER':
                option_key = options[selected][0]

                if option_key == 'back':
                    return
                else:
                    self._execute_release(option_key)
                    return
            elif key == 'ESC':
                return

    def _execute_release(self, release_type: str):
        """Execute the release process"""
        from core.version import __version__, get_new_build

        new_build = get_new_build()

        # Calculate new version
        parts = [int(x) for x in __version__.split('.')]
        if release_type == 'build':
            new_version = __version__
        elif release_type == 'patch':
            parts[2] += 1
            new_version = '.'.join(map(str, parts))
        elif release_type == 'minor':
            parts[1] += 1
            parts[2] = 0
            new_version = '.'.join(map(str, parts))
        elif release_type == 'major':
            parts[0] += 1
            parts[1] = 0
            parts[2] = 0
            new_version = '.'.join(map(str, parts))
        else:
            new_version = __version__

        archive_name = f"unibos_v{new_version}_b{new_build}"

        lines = [
            "🚀 Release Process",
            "",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"  release type: {release_type}",
            f"  new version:  v{new_version}",
            f"  new build:    {new_build}",
            f"  archive:      {archive_name}/",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            "",
            "  steps to complete:",
            "",
            "  1. update VERSION.json and core/version.py",
            "  2. create archive directory",
            "  3. git commit changes",
            "  4. create git tag",
            "  5. push to repositories",
            "",
            "  🚧 automatic release coming soon!",
            "",
            "  for now, manually update:",
            f"    VERSION.json: build = \"{new_build}\"",
            f"    core/version.py: __build__ = \"{new_build}\"",
            "",
            "press esc to continue"
        ]

        self.update_content(
            title="release process",
            lines=lines,
            color=Colors.YELLOW
        )
        self.render()

    def _version_increment(self):
        """Version increment wizard"""
        import time
        from core.version import __version__, __build__

        parts = [int(x) for x in __version__.split('.')]

        options = [
            ("patch", f"🔧 Patch: v{parts[0]}.{parts[1]}.{parts[2]+1}", "bug fixes, small improvements"),
            ("minor", f"✨ Minor: v{parts[0]}.{parts[1]+1}.0", "new features"),
            ("major", f"🚀 Major: v{parts[0]+1}.0.0", "breaking changes"),
            ("back", "← Cancel", "return without changes"),
        ]

        selected = 0

        while True:
            lines = [
                "🔼 Version Increment",
                "",
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                f"  current version: v{__version__}",
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                "",
                "  select increment type:",
                ""
            ]

            for i, (key, label, desc) in enumerate(options):
                if i == selected:
                    lines.append(f"  → {label}")
                    lines.append(f"    {desc}")
                else:
                    lines.append(f"    {label}")
                lines.append("")

            lines.extend([
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                "",
                "  when to use:",
                "    patch: bug fix, security patch",
                "    minor: new feature, enhancement",
                "    major: breaking API change, rewrite",
                "",
                "navigation: ↑↓ to move, Enter to select, ESC to cancel"
            ])

            self.update_content(
                title="increment version",
                lines=lines,
                color=Colors.CYAN
            )
            self.render()

            key = self.get_key()

            if key == 'UP':
                selected = (selected - 1) % len(options)
            elif key == 'DOWN':
                selected = (selected + 1) % len(options)
            elif key == 'ENTER':
                option_key = options[selected][0]

                if option_key == 'back':
                    return
                else:
                    self._execute_release(option_key)
                    return
            elif key == 'ESC':
                return

    def _version_create_tag(self):
        """Create git tag"""
        from core.version import __version__, __build__, VERSION_CODENAME

        lines = [
            "🏷️  Create Git Tag",
            "",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"  tag name:    v{__version__}",
            f"  build:       {__build__}",
            f"  codename:    {VERSION_CODENAME}",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            "",
            "  commands to run:",
            "",
            f"  git tag -a v{__version__} -m \"UNIBOS v{__version__}\"",
            f"  git push dev v{__version__}",
            f"  git push server v{__version__}",
            f"  git push manager v{__version__}",
            f"  git push prod v{__version__}",
            "",
            "  or use:",
            "    unibos-dev git push-dev --tags",
            "",
            "press esc to continue"
        ]

        self.update_content(
            title="create git tag",
            lines=lines,
            color=Colors.CYAN
        )
        self.render()

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

        # Build display
        lines = [
            "📋 Version Archive History",
            "",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        ]

        if archives:
            # Count by format
            new_count = sum(1 for a in archives if a['format'] == 'new')
            old_count = sum(1 for a in archives if a['format'] == 'old')

            lines.append(f"  total: {len(archives)} archives")
            if new_count > 0:
                lines.append(f"  new format (v1.0.0+): {new_count}")
            if old_count > 0:
                lines.append(f"  old format (pre-1.0): {old_count}")

            lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            lines.append("")
            lines.append("  recent archives:")
            lines.append("")

            for i, archive in enumerate(archives[:12]):  # Show last 12
                # Format display based on archive type
                if archive['format'] == 'new' and archive['build']:
                    # Parse timestamp for display
                    b = archive['build']
                    if len(b) == 14:
                        time_str = f"{b[8:10]}:{b[10:12]}"
                        date_str = f"{b[0:4]}-{b[4:6]}-{b[6:8]}"
                        lines.append(f"  {i+1:2}. v{archive['version']} @{time_str} ({date_str})")
                    else:
                        lines.append(f"  {i+1:2}. v{archive['version']} b{archive['build']}")
                else:
                    date_str = archive['date'] or ''
                    lines.append(f"  {i+1:2}. v{archive['version']} {date_str}")

            if len(archives) > 12:
                lines.append("")
                lines.append(f"  ... and {len(archives) - 12} more")

            lines.append("")
        else:
            lines.append("  no archives found")
            lines.append("")

        lines.extend([
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            "",
            "  archive location:",
            f"  {archive_dir}",
            "",
            "press esc to continue"
        ])

        self.update_content(
            title="browse archives",
            lines=lines,
            color=Colors.CYAN
        )
        self.render()

    def _version_analyze(self):
        """Analyze archives with statistics"""
        from pathlib import Path
        import os

        archive_dir = Path("/Users/berkhatirli/Desktop/unibos-dev/archive/versions")

        lines = [
            "📈 Archive Analyzer",
            "",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        ]

        if archive_dir.exists():
            # Calculate sizes
            total_size = 0
            archive_count = 0
            sizes = []

            for item in archive_dir.iterdir():
                if item.is_dir():
                    # Calculate directory size
                    dir_size = sum(
                        f.stat().st_size for f in item.rglob('*') if f.is_file()
                    )
                    total_size += dir_size
                    sizes.append((item.name, dir_size))
                    archive_count += 1

            # Format sizes
            def format_size(size):
                if size >= 1024 * 1024 * 1024:
                    return f"{size / (1024*1024*1024):.1f} GB"
                elif size >= 1024 * 1024:
                    return f"{size / (1024*1024):.1f} MB"
                elif size >= 1024:
                    return f"{size / 1024:.1f} KB"
                return f"{size} B"

            lines.extend([
                f"  total archives:  {archive_count}",
                f"  total size:      {format_size(total_size)}",
                "",
            ])

            if sizes:
                avg_size = total_size / len(sizes)
                lines.append(f"  average size:    {format_size(int(avg_size))}")

                # Find largest
                sizes.sort(key=lambda x: x[1], reverse=True)
                lines.extend([
                    "",
                    "  largest archives:",
                ])
                for name, size in sizes[:5]:
                    lines.append(f"    {format_size(size):>10}  {name[:40]}")

                # Check for anomalies (>2x average)
                anomalies = [s for s in sizes if s[1] > avg_size * 2]
                if anomalies:
                    lines.extend([
                        "",
                        f"  ⚠️  {len(anomalies)} size anomalies detected (>2x avg)",
                    ])

            lines.append("")
        else:
            lines.append("  archive directory not found")
            lines.append("")

        lines.extend([
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            "",
            "  for detailed analysis, run:",
            "    ./tools/archive_daily_check.sh",
            "",
            "press esc to continue"
        ])

        self.update_content(
            title="archive analyzer",
            lines=lines,
            color=Colors.CYAN
        )
        self.render()

    def _version_git_status(self):
        """show git status"""
        self.update_content(
            title="git status",
            lines=["🔀 Loading git status...", ""],
            color=Colors.CYAN
        )
        self.render()

        result = self.execute_command(['unibos-dev', 'git', 'status'])
        self.show_command_output(result)

def run_interactive():
    """Run the dev TUI"""
    tui = UnibosDevTUI()
    tui.run()


if __name__ == "__main__":
    run_interactive()
