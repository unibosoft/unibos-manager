"""
UNIBOS CLI Interactive Mode Base
Base class for interactive CLI mode with menu navigation

This provides the foundation for the hybrid CLI approach:
- When arguments provided → Direct Click commands
- When no arguments → Interactive TUI mode

Extracted and adapted from v527 main.py
Reference: docs/development/cli_v527_reference.md
"""

import sys
import time
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Callable

from .ui import (
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
    draw_header,
    draw_sidebar_sections,
    draw_content_area,
    draw_footer,
    clear_content_area,
)


class InteractiveMode(ABC):
    """
    Base class for interactive CLI mode

    Subclasses (unibos, unibos-dev, unibos-server) should:
    1. Override get_sections() to define menu structure
    2. Override handle_action() to implement menu actions
    3. Optionally override render_header() and render_footer()
    """

    def __init__(self, title: str, version: str):
        """
        Initialize interactive mode

        Args:
            title: CLI title (e.g., "UNIBOS Development")
            version: Version string (e.g., "v1.0.0")
        """
        self.title = title
        self.version = version
        self.state = MenuState()
        self.running = False

    @abstractmethod
    def get_sections(self) -> List[Dict[str, Any]]:
        """
        Get menu sections for this CLI

        Returns:
            List of section dicts with structure:
            {
                'id': 'section_id',
                'label': 'Section Name',
                'icon': '📦',
                'items': [MenuItem(...), ...]
            }
        """
        pass

    @abstractmethod
    def handle_action(self, item: MenuItem) -> bool:
        """
        Handle menu item action

        Args:
            item: Selected menu item

        Returns:
            True to continue menu loop, False to exit
        """
        pass

    def render_header(self):
        """
        Render v527-style header (single line, orange background)

        Override in subclass for custom breadcrumb
        """
        import os
        username = os.environ.get('USER', 'user')[:15]
        breadcrumb = self.get_breadcrumb()

        draw_header(
            title=self.title.lower(),
            version=self.version,
            breadcrumb=breadcrumb,
            username=username
        )

    def render_footer(self):
        """
        Render v527-style footer with full details

        Override in subclass for custom location/hostname
        """
        # v527 exact format (lowercase)
        hints = "↑↓ navigate | enter/→ select | esc/← back | tab switch | q quit"
        draw_footer(hints=hints, location="dev environment", hostname="")

    def render_sidebar(self):
        """
        Render v527-style sidebar with all sections

        Uses new draw_sidebar_sections function
        """
        draw_sidebar_sections(
            sections=self.state.sections,
            current_section=self.state.current_section,
            selected_index=self.state.selected_index,
            in_submenu=self.state.in_submenu is not None,
            sidebar_width=25
        )

    def render_content(self):
        """
        Render content area (right side)

        Override in subclass for custom content
        """
        item = self.state.get_selected_item()
        if not item:
            return

        # Build content lines
        lines = []
        if item.description:
            lines = item.description.split('\n')

        draw_content_area(
            title=item.label,
            lines=lines,
            sidebar_width=25
        )

    def get_breadcrumb(self) -> str:
        """
        Get navigation breadcrumb

        Override in subclass for custom breadcrumb
        """
        current_section = self.state.get_current_section()
        if current_section:
            section_label = current_section.get('label', '')
            item = self.state.get_selected_item()
            if item:
                return f"{section_label} › {item.label}"
            return section_label
        return ""

    def render(self):
        """Render entire UI (v527 style)"""
        clear_screen()
        self.render_header()
        self.render_sidebar()
        self.render_content()
        self.render_footer()
        sys.stdout.flush()

    def handle_key(self, key: str) -> bool:
        """
        Handle keyboard input

        Args:
            key: Key code from get_single_key()

        Returns:
            True to continue, False to exit
        """
        if key == Keys.UP:
            current_section = self.state.get_current_section()
            if current_section:
                max_items = len(current_section.get('items', []))
                if self.state.navigate_up():
                    self.render()

        elif key == Keys.DOWN:
            current_section = self.state.get_current_section()
            if current_section:
                max_items = len(current_section.get('items', []))
                if self.state.navigate_down(max_items):
                    self.render()

        elif key == Keys.LEFT:
            if self.state.navigate_left():
                self.render()
            elif not self.state.in_submenu:
                # At top level, left means exit
                return False

        elif key == Keys.RIGHT:
            if self.state.navigate_right(len(self.state.sections)):
                self.render()

        elif key == Keys.ENTER or key == '\r':
            item = self.state.get_selected_item()
            if item and item.enabled:
                show_cursor()
                if not self.handle_action(item):
                    return False
                hide_cursor()
                self.render()

        elif key == Keys.ESC or key == '\x1b':
            if self.state.in_submenu:
                self.state.exit_submenu()
                self.render()
            else:
                return False

        elif key == '\t' or key == Keys.TAB:  # TAB to switch sections (v527 exact)
            if not self.state.in_submenu:
                # Cycle to next section
                self.state.current_section = (self.state.current_section + 1) % len(self.state.sections)
                self.state.selected_index = 0
                self.state.previous_index = None
                self.render()

        elif key and key.lower() == 'q':  # Q to quit (v527 exact)
            return False

        elif key and key.isdigit():
            # Quick select by number
            num = int(key)
            item = self.state.quick_select(num)
            if item and item.enabled:
                show_cursor()
                if not self.handle_action(item):
                    return False
                hide_cursor()
                self.render()

        # Check for terminal resize
        cols, lines = get_terminal_size()
        if self.state.terminal_resized(cols, lines):
            self.render()

        return True

    def run(self, show_splash: bool = True):
        """
        Run interactive mode

        Args:
            show_splash: Whether to show splash screen (default True)
        """
        try:
            # Show splash screen
            if show_splash:
                show_splash_screen(quick=False)

            # Initialize menu structure (v527 exact - sections manage their own items)
            self.state.sections = self.get_sections()

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
                time.sleep(0.01)  # Prevent CPU spinning

        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            pass
        finally:
            # Cleanup
            show_cursor()
            clear_screen()

    def exit(self):
        """Exit interactive mode"""
        self.running = False
