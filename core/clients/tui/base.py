"""
UNIBOS TUI Base Class
Base class for all UNIBOS TUI implementations

Provides complete v527-style UI with modern enhancements
"""

import sys
import time
import subprocess
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Callable
from pathlib import Path
from dataclasses import dataclass, field

# Import existing UI components
from core.clients.cli.framework.ui import (
    Colors,
    clear_screen,
    get_terminal_size,
    move_cursor,
    hide_cursor,
    show_cursor,
    wrap_text,
    print_centered,
    show_splash_screen,
    get_single_key,
    Keys,
    MenuItem,
    MenuState,
)

from .components import (
    Header,
    Footer,
    Sidebar,
    ContentArea,
    StatusBar,
    MenuSection,
)


@dataclass
class TUIConfig:
    """Configuration for TUI appearance and behavior"""
    title: str = "unibos"
    version: str = "v0.534.0"
    location: str = "bitez, bodrum"
    sidebar_width: int = 30
    show_splash: bool = True
    quick_splash: bool = False
    enable_animations: bool = True
    enable_sounds: bool = False
    color_scheme: str = "v527"  # v527, modern, dark, light

    # V527 specific settings
    lowercase_ui: bool = True  # v527 uses all lowercase
    show_breadcrumbs: bool = True
    show_time: bool = True
    show_hostname: bool = True
    show_status_led: bool = True


class BaseTUI(ABC):
    """
    Base class for all UNIBOS TUI implementations

    This provides the complete v527-style interface with:
    - Header with breadcrumbs and status
    - Multi-section sidebar with navigation
    - Content area with scrolling
    - Footer with hints and system info
    - Keyboard navigation and shortcuts
    """

    def __init__(self, config: Optional[TUIConfig] = None):
        """
        Initialize TUI with configuration

        Args:
            config: TUI configuration (uses defaults if None)
        """
        self.config = config or TUIConfig()
        self.state = MenuState()
        self.running = False

        # Components
        self.header = Header(self.config)
        self.footer = Footer(self.config)
        self.sidebar = Sidebar(self.config)
        self.content_area = ContentArea(self.config)
        self.status_bar = StatusBar(self.config)

        # Action handlers registry
        self.action_handlers = {}
        self.register_default_handlers()

        # Cache for expensive operations
        self.cache = {
            'modules': None,
            'git_status': None,
            'system_info': None
        }

        # Content storage for persistent display
        self.content_buffer = {
            'title': '',
            'lines': [],
            'color': Colors.RESET,
            'last_command': None,
            'last_result': None
        }

    @abstractmethod
    def get_menu_sections(self) -> List[MenuSection]:
        """
        Get menu sections for this TUI

        Returns:
            List of MenuSection objects
        """
        pass

    @abstractmethod
    def get_profile_name(self) -> str:
        """
        Get profile name (dev, server, prod)

        Returns:
            Profile name string
        """
        pass

    def register_default_handlers(self):
        """Register default action handlers"""
        # Common handlers all profiles can use
        self.register_action('quit', self.handle_quit)
        self.register_action('refresh', self.handle_refresh)
        self.register_action('help', self.handle_help)
        self.register_action('about', self.handle_about)

    def register_action(self, action_id: str, handler: Callable):
        """
        Register an action handler

        Args:
            action_id: Unique action identifier
            handler: Function to handle the action
        """
        self.action_handlers[action_id] = handler

    def handle_action(self, item: MenuItem) -> bool:
        """
        Handle menu item action

        Args:
            item: Selected menu item

        Returns:
            True to continue, False to exit
        """
        # Check for registered handler
        if item.id in self.action_handlers:
            try:
                return self.action_handlers[item.id](item)
            except Exception as e:
                self.show_error(f"Action failed: {e}")
                return True

        # Default: show not implemented
        self.show_message(
            f"Action not implemented: {item.id}",
            color=Colors.YELLOW
        )
        return True

    def handle_quit(self, item: MenuItem) -> bool:
        """Handle quit action"""
        return False

    def handle_refresh(self, item: MenuItem) -> bool:
        """Handle refresh action"""
        self.clear_cache()
        self.render()
        return True

    def handle_help(self, item: MenuItem) -> bool:
        """Handle help action"""
        self.show_help_screen()
        return True

    def handle_about(self, item: MenuItem) -> bool:
        """Handle about action"""
        self.show_about_screen()
        return True

    def render(self):
        """Render complete UI"""
        clear_screen()

        # Get terminal size for responsive layout
        cols, lines = get_terminal_size()

        # Update components with current state
        sections = self.get_menu_sections()
        current_section = sections[self.state.current_section] if sections else None
        selected_item = self.state.get_selected_item() if current_section else None

        # Draw components in order
        self.header.draw(
            breadcrumb=self.get_breadcrumb(),
            username=self.get_username()
        )

        self.sidebar.draw(
            sections=sections,
            current_section=self.state.current_section,
            selected_index=self.state.selected_index
        )

        # Render content area with persistent buffer or selected item description
        if self.content_buffer['lines']:
            # Show buffered content from last command
            content = '\n'.join(self.content_buffer['lines'])
            self.content_area.draw(
                title=self.content_buffer['title'],
                content=content,
                item=None
            )
        elif selected_item:
            # Show selected item description
            self.content_area.draw(
                title=selected_item.label,
                content=selected_item.description,
                item=selected_item
            )

        self.footer.draw(
            hints=self.get_navigation_hints(),
            status=self.get_system_status()
        )

        sys.stdout.flush()

    def get_breadcrumb(self) -> str:
        """Get current navigation breadcrumb"""
        sections = self.get_menu_sections()
        if not sections:
            return ""

        current_section = sections[self.state.current_section]
        item = self.state.get_selected_item()

        if item:
            return f"{current_section.label} › {item.label}"
        return current_section.label

    def get_username(self) -> str:
        """Get current username"""
        import os
        return os.environ.get('USER', 'user')[:15]

    def get_navigation_hints(self) -> str:
        """Get navigation hints for footer"""
        if self.state.in_submenu:
            return "↑↓ navigate | enter confirm | esc cancel"
        return "↑↓ navigate | enter/→ select | esc/← back | tab switch | q quit"

    def get_system_status(self) -> Dict[str, Any]:
        """Get system status for footer"""
        import socket
        from datetime import datetime

        return {
            'hostname': socket.gethostname().lower(),
            'time': datetime.now().strftime('%H:%M:%S'),
            'date': datetime.now().strftime('%Y-%m-%d'),
            'online': self.check_online_status()
        }

    def check_online_status(self) -> bool:
        """Check if system is online"""
        try:
            # Quick DNS check
            import socket
            socket.create_connection(("1.1.1.1", 53), timeout=1).close()
            return True
        except:
            return False

    def handle_key(self, key: str) -> bool:
        """
        Handle keyboard input

        Args:
            key: Key code from get_single_key()

        Returns:
            True to continue, False to exit
        """

        sections = self.get_menu_sections()

        if key == Keys.UP:
            if self.state.navigate_up():
                self.render()

        elif key == Keys.DOWN:
            current_section = sections[self.state.current_section] if sections else None
            max_items = len(current_section.items) if current_section else 0
            if self.state.navigate_down(max_items):
                self.render()

        elif key == Keys.LEFT:
            if self.state.navigate_left():
                self.render()
            elif not self.state.in_submenu:
                return False  # Exit on left at top level

        elif key == Keys.RIGHT:
            if self.state.navigate_right(len(sections)):
                self.render()

        elif key == Keys.TAB:
            # Switch sections
            if not self.state.in_submenu and sections:
                self.state.current_section = (self.state.current_section + 1) % len(sections)
                self.state.selected_index = 0
                self.render()

        elif key == Keys.ENTER or key == '\r' or key == '\n':
            # Get current section and item
            current_section = sections[self.state.current_section] if sections else None
            if current_section and 0 <= self.state.selected_index < len(current_section.items):
                item = current_section.items[self.state.selected_index]
                if item and item.enabled:
                    show_cursor()
                    result = self.handle_action(item)
                    hide_cursor()
                    if not result:
                        return False
                    self.render()

        elif key == Keys.ESC or key == '\x1b':
            if self.state.in_submenu:
                self.state.exit_submenu()
                self.render()
            else:
                return False

        elif key and key.lower() == 'q':
            return False

        elif key and key.isdigit():
            # Quick select by number
            num = int(key)
            current_section = sections[self.state.current_section] if sections else None
            if current_section and 0 <= num < len(current_section.items):
                item = current_section.items[num]
                if item.enabled:
                    show_cursor()
                    result = self.handle_action(item)
                    hide_cursor()
                    if not result:
                        return False
                    self.render()

        # Check for terminal resize
        cols, lines = get_terminal_size()
        if self.state.terminal_resized(cols, lines):
            self.render()

        return True

    def run(self):
        """Run the TUI main loop"""
        try:
            # Show splash screen
            if self.config.show_splash:
                show_splash_screen(quick=self.config.quick_splash)

            # Initialize menu structure
            sections = self.get_menu_sections()
            self.state.sections = [s.to_dict() for s in sections]

            # Hide cursor for cleaner UI
            hide_cursor()

            # Initial render
            self.running = True
            self.render()

            # Main event loop
            while self.running:
                key = get_single_key(timeout=0.1)
                if key:
                    if not self.handle_key(key):
                        break
                time.sleep(0.01)

        except KeyboardInterrupt:
            pass
        finally:
            # Cleanup
            show_cursor()
            clear_screen()
            self.cleanup()

    def cleanup(self):
        """Cleanup on exit"""
        pass

    def update_content(self, title: str, lines: List[str], color: str = Colors.RESET):
        """Update the content buffer with new information"""
        self.content_buffer['title'] = title
        self.content_buffer['lines'] = lines
        self.content_buffer['color'] = color
        # Content will be displayed on next render

    def show_message(self, message: str, color: str = Colors.GREEN):
        """Show a message in content area"""
        # Handle both string and list inputs
        if isinstance(message, list):
            lines = message
        else:
            lines = message.split('\n') if message else []
        self.update_content("Message", lines, color)
        self.render()

    def show_error(self, message: str):
        """Show an error message"""
        self.update_content("Error", [f"❌ {message}"], Colors.RED)
        self.render()

    def show_help_screen(self):
        """Show help screen"""
        help_lines = [
            "UNIBOS TUI Help",
            "",
            "NAVIGATION:",
            "  ↑/↓        Navigate items",
            "  ←/→        Navigate sections",
            "  TAB        Switch sections",
            "  Enter      Select item",
            "  ESC        Back/Cancel",
            "  Q          Quit",
            "",
            "QUICK SELECT:",
            "  0-9        Select item by number",
            "",
            "SHORTCUTS:",
            "  Ctrl+R     Refresh",
            "  Ctrl+L     Clear screen",
            "  F1         Help"
        ]
        self.update_content("Help", help_lines, Colors.CYAN)
        self.render()

    def show_about_screen(self):
        """Show about screen"""
        about_lines = [
            f"{self.config.title.upper()} {self.config.version}",
            "Unicorn Bodrum Operating System",
            "",
            "Created by Berk Hatırlı",
            "Bitez, Bodrum, Muğla, Turkey",
            "",
            f"Profile: {self.get_profile_name()}",
            "Build: 534"
        ]
        self.update_content("About", about_lines, Colors.ORANGE)
        self.render()

    def clear_cache(self):
        """Clear all cached data"""
        self.cache = {
            'modules': None,
            'git_status': None,
            'system_info': None
        }

    def execute_command(self, command: List[str], **kwargs) -> subprocess.CompletedProcess:
        """
        Execute a command and return result

        Args:
            command: Command to execute
            **kwargs: Additional arguments for subprocess.run

        Returns:
            CompletedProcess object
        """
        defaults = {
            'capture_output': True,
            'text': True,
            'check': False
        }
        defaults.update(kwargs)
        return subprocess.run(command, **defaults)

    def show_command_output(self, result: subprocess.CompletedProcess):
        """
        Display command output

        Args:
            result: CompletedProcess object from execute_command
        """
        lines = []

        # Show command
        if hasattr(result, 'args'):
            cmd = ' '.join(result.args if isinstance(result.args, list) else [str(result.args)])
            lines.append(f"Command: {cmd}")
            lines.append("─" * 40)
            lines.append("")

        # Show output
        if result.stdout:
            stdout_lines = result.stdout.split('\n')
            lines.extend(stdout_lines)

        # Show errors if any
        if result.stderr:
            lines.append("")
            lines.append("Errors:")
            stderr_lines = result.stderr.split('\n')
            lines.extend(stderr_lines)

        # Show exit status if non-zero
        if result.returncode != 0:
            lines.append("")
            lines.append(f"❌ Exit code: {result.returncode}")
        else:
            lines.append("")
            lines.append("✅ Command completed successfully")

        self.update_content("Command Output", lines)
        self.render()