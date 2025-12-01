"""
UNIBOS TUI Header Component
V527-style header with orange background and system info
"""

import sys
from datetime import datetime
from typing import Optional

from core.clients.cli.framework.ui import Colors, get_terminal_size, move_cursor
from core.version import __build__


class Header:
    """Header component for TUI"""

    def __init__(self, config, i18n=None):
        """Initialize header with config and i18n manager"""
        self.config = config
        self.i18n = i18n

    def draw(self, breadcrumb: str = "", username: str = "", language: str = "🇹🇷 Türkçe"):
        """
        Draw v527-style header with orange background

        Format: 🦄 unibos v1.0.0+20251202003028 › [breadcrumb] | 🇹🇷 Türkçe | berkhatirli
        NO CLOCK IN HEADER (clock is in footer)

        Args:
            breadcrumb: Navigation breadcrumb
            username: Current username
            language: Language display (default: Turkish)
        """
        cols, _ = get_terminal_size()

        # V527: Hide cursor during draw
        sys.stdout.write('\033[?25l')
        sys.stdout.flush()

        # Clear header line
        sys.stdout.write('\033[1;1H\033[2K')
        sys.stdout.flush()

        # Full orange background
        move_cursor(1, 1)
        sys.stdout.write(f"{Colors.BG_ORANGE}{' ' * cols}{Colors.RESET}")
        sys.stdout.flush()

        # Left side: Icon + Title + Version + Build + Breadcrumb
        # Format: v1.0.0+20251202003028
        title_text = f"  🦄 {self.config.title}"
        if self.config.version:
            title_text += f" {self.config.version}+{__build__}"

        if breadcrumb and self.config.show_breadcrumbs:
            # Make breadcrumb lowercase if config says so
            if self.config.lowercase_ui:
                breadcrumb = breadcrumb.lower()
            title_text += f" › {breadcrumb}"

        # Apply lowercase if configured
        if self.config.lowercase_ui:
            title_text = title_text.lower()

        move_cursor(1, 1)
        sys.stdout.write(f"{Colors.BG_ORANGE}{Colors.BLACK}{Colors.BOLD}{title_text}{Colors.RESET}")
        sys.stdout.flush()

        # Right side: Language | Username
        # NO TIME/CLOCK - that goes in footer
        right_elements = []

        # Language
        if language:
            right_elements.append(language)

        # Username
        if username:
            right_elements.append(username)

        # Draw right side
        if right_elements:
            right_text = " | ".join(right_elements)
            # Add spacing before the text
            right_text = f" {right_text} "
            right_pos = cols - len(right_text)
            if right_pos > len(title_text):  # Ensure no overlap
                move_cursor(right_pos, 1)
                sys.stdout.write(f"{Colors.BG_ORANGE}{Colors.BLACK}{right_text}{Colors.RESET}")
                sys.stdout.flush()

        # V527: Final flush and show cursor
        sys.stdout.flush()
        sys.stdout.write('\033[?25h')
        sys.stdout.flush()