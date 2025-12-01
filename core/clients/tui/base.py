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
    flush_input_buffer,
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

from .i18n import get_translation_manager, t


@dataclass
class TUIConfig:
    """Configuration for TUI appearance and behavior"""
    title: str = "unibos"
    version: str = "v0.534.0"
    location: str = "bitez, bodrum"
    sidebar_width: int = 25  # V527 spec: exactly 25 characters
    show_splash: bool = True
    quick_splash: bool = False
    enable_animations: bool = True
    enable_sounds: bool = False
    color_scheme: str = "v527"  # v527, modern, dark, light

    # V527 specific settings
    lowercase_ui: bool = True  # v527 uses all lowercase
    show_breadcrumbs: bool = True
    show_time: bool = True  # Time shows in FOOTER, not header
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

        # Translation manager
        self.i18n = get_translation_manager()

        # Components
        self.header = Header(self.config, self.i18n)
        self.footer = Footer(self.config, self.i18n)
        self.sidebar = Sidebar(self.config)
        self.content_area = ContentArea(self.config, self.i18n)
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

        # V527: Keypress debouncing to prevent rapid navigation corruption
        self.last_keypress_time = 0
        self.min_keypress_interval = 0.08  # 80ms debounce (increased from 50ms for stability)

        # V527: Navigation lock to prevent concurrent rendering (Protection 1)
        self._rendering = False

        # V527: Render completion flag (Protection 8)
        self._last_render_complete = False

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
        """Render complete UI with v527 hide-cursor pattern and ALL 8 protections"""
        # V527: Hide cursor at start of draw sequence
        sys.stdout.write('\033[?25l')
        sys.stdout.flush()

        try:
            # V527 Protection 4: Enhanced clear with triple clear
            sys.stdout.write('\033[2J')  # Clear screen
            sys.stdout.write('\033[H')   # Move to home
            sys.stdout.write('\033[3J')  # Clear scrollback
            sys.stdout.flush()

            # V527 Protection 4: Increase delay to 30ms (from 20ms)
            time.sleep(0.03)

            # Double clear for safety
            clear_screen()
            sys.stdout.flush()

            # V527 Protection 7: Clear stale input (5 flushes)
            flush_input_buffer(times=5)

            # Get terminal size for responsive layout
            cols, lines = get_terminal_size()

            # Update components with current state
            sections = self.get_menu_sections()
            current_section = sections[self.state.current_section] if sections else None
            selected_item = self.state.get_selected_item() if current_section else None

            # V527 Protection 5: Draw components in STRICT ORDER with Protection 6 (flush + delay)
            # Get current language display
            lang_code = self.i18n.get_language()
            lang_flag = self.i18n.get_language_flag(lang_code)
            lang_name = self.i18n.get_language_display_name(lang_code)
            language_display = f"{lang_flag} {lang_name}"

            # PROTECTION 5 & 6: Header FIRST with flush and delay
            self.header.draw(
                breadcrumb=self.get_breadcrumb(),
                username=self.get_username(),
                language=language_display  # V527 spec: language in header
            )
            sys.stdout.flush()
            time.sleep(0.01)  # Protection 6: Small delay after component

            # PROTECTION 5 & 6: Sidebar SECOND with flush and delay
            self.sidebar.draw(
                sections=sections,
                current_section=self.state.current_section,
                selected_index=self.state.selected_index
            )
            sys.stdout.flush()
            time.sleep(0.01)  # Protection 6: Small delay after component

            # PROTECTION 5 & 6: Content THIRD with flush and delay
            # Render content area with persistent buffer or selected item description
            if self.content_buffer['lines']:
                # Show buffered content from last command
                # Handle both list and string types defensively
                lines = self.content_buffer['lines']
                if isinstance(lines, str):
                    content = lines
                elif isinstance(lines, list):
                    content = '\n'.join(lines)
                else:
                    content = str(lines)

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
            sys.stdout.flush()
            time.sleep(0.01)  # Protection 6: Small delay after component

            # PROTECTION 5 & 6: Footer LAST with flush and delay
            self.footer.draw(
                hints=self.get_navigation_hints(),
                status=self.get_system_status()
            )
            sys.stdout.flush()
            time.sleep(0.01)  # Protection 6: Small delay after component

        finally:
            # V527: Always show cursor after draw (even on error)
            sys.stdout.write('\033[?25h')
            sys.stdout.flush()

            # V527 Protection 8: Mark render as complete
            self._last_render_complete = True

    def _navigation_redraw(self, sections):
        """Atomic redraw for navigation - prevents flicker and escape sequence leaks"""
        # Prevent concurrent rendering
        if self._rendering:
            return
        self._rendering = True

        try:
            cols, lines = get_terminal_size()

            # Hide cursor and disable line wrap
            sys.stdout.write('\033[?25l\033[?7l')
            sys.stdout.flush()

            # Aggressive input flush
            flush_input_buffer(times=5)
            try:
                import select
                while select.select([sys.stdin], [], [], 0)[0]:
                    sys.stdin.read(1)
            except:
                pass

            # Draw sidebar
            self.sidebar.draw(
                sections, self.state.current_section,
                self.state.selected_index, bool(self.state.in_submenu)
            )

            # Update content
            self.update_content_for_selection()

            # Get language display
            lang_code = self.i18n.get_language()
            lang_flag = self.i18n.get_language_flag(lang_code)
            lang_name = self.i18n.get_language_display_name(lang_code)
            language_display = f"{lang_flag} {lang_name}"

            # Redraw header at line 1 (explicit position)
            sys.stdout.write('\033[1;1H')
            self.header.draw(
                breadcrumb=self.get_breadcrumb(),
                username=self.get_username(),
                language=language_display
            )

            # Redraw footer at last line (explicit position)
            sys.stdout.write(f'\033[{lines};1H')
            self.footer.draw(
                hints=self.get_navigation_hints(),
                status=self.get_system_status()
            )

            # Final flush
            sys.stdout.flush()
        finally:
            # Re-enable line wrap and show cursor
            sys.stdout.write('\033[?7h\033[?25h')
            sys.stdout.flush()
            self._rendering = False

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
            return self.i18n.translate('navigate_hint_submenu')
        return self.i18n.translate('navigate_hint_main')

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
        # V527: Debounce rapid keypresses to prevent screen corruption
        current_time = time.time()
        if current_time - self.last_keypress_time < self.min_keypress_interval:
            return True  # Skip this keypress, too fast
        self.last_keypress_time = current_time

        sections = self.get_menu_sections()

        if key == Keys.UP:
            if self.state.navigate_up():
                self._navigation_redraw(sections)

        elif key == Keys.DOWN:
            current_section = sections[self.state.current_section] if sections else None
            max_items = len(current_section.items) if current_section else 0
            if self.state.navigate_down(max_items):
                self._navigation_redraw(sections)

        elif key == Keys.LEFT:
            if self.state.navigate_left():
                self.render()
            elif not self.state.in_submenu:
                return False  # Exit on left at top level

        elif key == Keys.RIGHT:
            # v527: Right arrow acts like Enter - selects current item
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

        elif key and key.lower() == 'l':
            # V527: Language selection menu
            self.show_language_menu()
            self.render()

        # V527 CHANGE: Numeric quick selection disabled (no numbers in sidebar)
        # elif key and key.isdigit():
        #     # Quick select by number
        #     num = int(key)
        #     current_section = sections[self.state.current_section] if sections else None
        #     if current_section and 0 <= num < len(current_section.items):
        #         item = current_section.items[num]
        #         if item.enabled:
        #             show_cursor()
        #             result = self.handle_action(item)
        #             hide_cursor()
        #             if not result:
        #                 return False
        #             self.render()

        return True

    def run(self):
        """Run the TUI main loop (v527 with resize and clock)"""
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

            # V527: Initialize terminal size for resize detection
            cols, lines = get_terminal_size()
            self.state.last_cols = cols
            self.state.last_lines = lines

            # V527: Track last footer update time for live clock
            last_footer_update = time.time()

            # Main event loop
            while self.running:
                # Get key with timeout for responsive updates
                key = get_single_key(timeout=0.1)
                if key:
                    if not self.handle_key(key):
                        break

                # V527: Check for terminal resize (polling-based)
                cols, lines = get_terminal_size()
                if cols != self.state.last_cols or lines != self.state.last_lines:
                    self.state.last_cols = cols
                    self.state.last_lines = lines
                    # Full redraw on resize
                    self.render()

                # V527: Update footer time every second (polling, not threading)
                current_time = time.time()
                if current_time - last_footer_update >= 1.0 and not self.state.in_submenu:
                    # Update only footer (not entire screen)
                    self.footer.draw(
                        hints=self.get_navigation_hints(),
                        status=self.get_system_status()
                    )
                    last_footer_update = current_time
                    hide_cursor()

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

    def get_key(self) -> str:
        """
        Get a single keypress from user

        Returns:
            Key code string ('UP', 'DOWN', 'LEFT', 'RIGHT', 'ENTER', 'ESC', or character)
        """
        import time
        while True:
            key = get_single_key(timeout=0.1)
            if key:
                # Map Keys constants to simple strings
                if key == Keys.UP:
                    return 'UP'
                elif key == Keys.DOWN:
                    return 'DOWN'
                elif key == Keys.LEFT:
                    return 'LEFT'
                elif key == Keys.RIGHT:
                    return 'RIGHT'
                elif key == Keys.ENTER or key == '\r' or key == '\n':
                    return 'ENTER'
                elif key == Keys.ESC or key == '\x1b':
                    return 'ESC'
                elif key == Keys.TAB:
                    return 'TAB'
                else:
                    return key
            time.sleep(0.01)

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
        self.update_content(self.i18n.translate('message'), lines, color)
        self.render()

    def show_error(self, message: str):
        """Show an error message"""
        self.update_content(self.i18n.translate('error'), [f"❌ {message}"], Colors.RED)
        self.render()

    def show_help_screen(self):
        """Show help screen"""
        help_lines = [
            self.i18n.translate('help_screen_title'),
            "",
            self.i18n.translate('navigation') + ":",
            "  " + self.i18n.translate('navigation_up_down'),
            "  " + self.i18n.translate('navigation_left_right'),
            "  " + self.i18n.translate('navigation_tab'),
            "  " + self.i18n.translate('navigation_enter'),
            "  " + self.i18n.translate('navigation_esc'),
            "  " + self.i18n.translate('navigation_q'),
            "",
            self.i18n.translate('shortcuts') + ":",
            "  " + self.i18n.translate('shortcut_ctrl_r'),
            "  " + self.i18n.translate('shortcut_ctrl_l'),
            "  " + self.i18n.translate('shortcut_f1'),
            "  " + self.i18n.translate('shortcut_l')
        ]
        self.update_content(self.i18n.translate('help'), help_lines, Colors.CYAN)
        self.render()

    def show_about_screen(self):
        """Show about screen"""
        about_lines = [
            f"{self.config.title} {self.config.version}",
            self.i18n.translate('unicorn_bodrum_os'),
            "",
            self.i18n.translate('about_created_by'),
            self.i18n.translate('about_location'),
            "",
            self.i18n.translate('about_profile', profile=self.get_profile_name()),
            self.i18n.translate('about_build', build='534')
        ]
        self.update_content(self.i18n.translate('about'), about_lines, Colors.ORANGE)
        self.render()

    def update_content_for_selection(self):
        """
        Update content area when sidebar selection changes (v527 spec)

        This method updates only the content area without full screen redraw
        """
        sections = self.get_menu_sections()
        current_section = sections[self.state.current_section] if sections else None
        if current_section and 0 <= self.state.selected_index < len(current_section.items):
            selected_item = current_section.items[self.state.selected_index]
            # Draw content for selected item
            self.content_area.draw(
                title=selected_item.label,
                content=selected_item.description,
                item=selected_item
            )
            sys.stdout.flush()

    def show_language_menu(self):
        """
        Show language selection popup (v527 spec)

        V527 SPEC:
        - 40x15 character popup, centered on screen
        - Arrow key navigation
        - Enter to confirm, ESC to cancel
        - Updates header language when selected
        """
        from core.clients.cli.framework.ui import draw_box

        cols, lines = get_terminal_size()

        # Language menu dimensions (v527 spec)
        lang_width = 40
        lang_height = 15
        lang_x = (cols - lang_width) // 2
        lang_y = (lines - lang_height) // 2

        # Get available languages from i18n system
        languages = self.i18n.get_available_languages()

        # Find current language in list
        current_lang = self.i18n.get_language()
        selected = 0
        for i, (code, name, flag) in enumerate(languages):
            if code == current_lang:
                selected = i
                break

        while True:
            # Draw popup box
            draw_box(lang_x, lang_y, lang_width, lang_height,
                    self.i18n.translate('select_language'),
                    Colors.YELLOW)

            # Display languages with selection highlight
            for i, (code, name, flag) in enumerate(languages[:10]):  # Max 10
                y_pos = lang_y + 2 + i

                if i == selected:
                    # Selected item with orange background
                    move_cursor(lang_x + 3, y_pos)
                    sys.stdout.write(f"{Colors.BG_ORANGE}{Colors.WHITE} ➤ {flag} {name} {' ' * (lang_width - len(name) - 10)}{Colors.RESET}")
                else:
                    # Normal item
                    move_cursor(lang_x + 3, y_pos)
                    sys.stdout.write(f"   {flag} {name}")

            sys.stdout.flush()
            hide_cursor()

            # Handle input
            key = get_single_key(timeout=0.1)
            if key == Keys.UP:
                selected = (selected - 1) % len(languages)
            elif key == Keys.DOWN:
                selected = (selected + 1) % len(languages)
            elif key == Keys.ENTER or key == '\r' or key == '\n':
                # Language selected - actually change the language
                code, name, flag = languages[selected]
                # Set the language in translation manager
                self.i18n.set_language(code)
                # Show confirmation message
                self.show_message(
                    self.i18n.translate('language_changed', flag=flag, name=name),
                    Colors.GREEN
                )
                break
            elif key == Keys.ESC or key == '\x1b' or (key and key.lower() == 'l'):
                # Cancel
                break

            time.sleep(0.01)

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
            lines.append(f"{self.i18n.translate('command')}: {cmd}")
            lines.append("─" * 40)
            lines.append("")

        # Show output
        if result.stdout:
            # Handle both string and list types defensively
            if isinstance(result.stdout, str):
                stdout_lines = result.stdout.split('\n')
            elif isinstance(result.stdout, list):
                stdout_lines = result.stdout
            else:
                stdout_lines = [str(result.stdout)]
            lines.extend(stdout_lines)

        # Show errors if any
        if result.stderr:
            lines.append("")
            lines.append(self.i18n.translate('errors') + ":")
            # Handle both string and list types defensively
            if isinstance(result.stderr, str):
                stderr_lines = result.stderr.split('\n')
            elif isinstance(result.stderr, list):
                stderr_lines = result.stderr
            else:
                stderr_lines = [str(result.stderr)]
            lines.extend(stderr_lines)

        # Show exit status if non-zero
        if result.returncode != 0:
            lines.append("")
            lines.append(self.i18n.translate('exit_code', code=result.returncode))
        else:
            lines.append("")
            lines.append(self.i18n.translate('command_completed'))

        self.update_content(self.i18n.translate('command_output'), lines)
        self.render()