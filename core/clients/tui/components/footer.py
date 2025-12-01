"""
UNIBOS TUI Footer Component
V527-style footer with navigation hints and system status
"""

import sys
import socket
from datetime import datetime
from typing import Dict, Any, Optional

from core.clients.cli.framework.ui import Colors, get_terminal_size, move_cursor


class Footer:
    """Footer component for TUI"""

    def __init__(self, config, i18n=None):
        """Initialize footer with config and i18n manager"""
        self.config = config
        self.i18n = i18n

    def draw(self, hints: str = "", status: Optional[Dict[str, Any]] = None):
        """
        Draw v527-style footer with hints and status

        Args:
            hints: Navigation hints text
            status: System status dict with hostname, time, date, online
        """
        cols, lines = get_terminal_size()
        footer_y = lines

        # V527: Hide cursor during draw
        sys.stdout.write('\033[?25l')
        sys.stdout.flush()

        # CRITICAL: Aggressive flush - both termios and reading any pending bytes
        try:
            import termios
            termios.tcflush(sys.stdin, termios.TCIFLUSH)
        except Exception:
            pass

        # Also try to drain stdin non-blocking
        try:
            import select
            while select.select([sys.stdin], [], [], 0)[0]:
                sys.stdin.read(1)
        except Exception:
            pass

        # V527 CRITICAL: Clear footer line completely
        sys.stdout.write(f"\033[{footer_y};1H\033[2K")
        sys.stdout.write(f"\033[{footer_y};1H{Colors.BG_DARK}{' ' * cols}{Colors.RESET}")
        sys.stdout.flush()

        # Left side: Navigation hints
        if not hints:
            hints = "↑↓ navigate | enter/→ select | esc/← back | tab switch | q quit"

        # Apply lowercase if configured
        if self.config.lowercase_ui:
            hints = hints.lower()

        # V527: Use precise cursor positioning (Column 2 for left-aligned)
        sys.stdout.write(f"\033[{footer_y};2H")
        sys.stdout.write(f"{Colors.BG_DARK}{Colors.DIM}{hints}{Colors.RESET}")
        sys.stdout.flush()

        # Right side: Status information
        right_elements = []

        if status:
            # Hostname
            if self.config.show_hostname and 'hostname' in status:
                hostname = status['hostname']
                if self.config.lowercase_ui:
                    hostname = hostname.lower()
                right_elements.append(hostname)

            # Location
            if self.config.location:
                location = self.config.location
                if self.config.lowercase_ui:
                    location = location.lower()
                right_elements.append(location)

            # Date
            if 'date' in status:
                right_elements.append(status['date'])

            # Time
            if 'time' in status:
                right_elements.append(status['time'])

            # Online status
            if self.config.show_status_led and 'online' in status:
                if status['online']:
                    status_text = self.i18n.translate('online') if self.i18n else "online"
                    status_led = "●"  # Green LED
                    led_color = Colors.GREEN
                else:
                    status_text = self.i18n.translate('offline') if self.i18n else "offline"
                    status_led = "●"  # Red LED
                    led_color = Colors.RED
        else:
            # Default status
            hostname = socket.gethostname()
            if self.config.lowercase_ui:
                hostname = hostname.lower()
            right_elements.append(hostname)

            location = self.config.location
            if self.config.lowercase_ui:
                location = location.lower()
            right_elements.append(location)

            right_elements.append(datetime.now().strftime("%Y-%m-%d"))
            right_elements.append(datetime.now().strftime("%H:%M:%S"))

            status_text = self.i18n.translate('online') if self.i18n else "online"
            status_led = "●"
            led_color = Colors.GREEN

        # Build right side text
        if right_elements:
            right_text = " | ".join(right_elements)
            if self.config.show_status_led:
                right_text += f" | {status_text} "

            # Calculate position
            right_len = len(right_text) + 1  # +1 for LED
            right_pos = cols - right_len - 2
            right_pos = max(2, right_pos)

            # Draw right side
            # V527: Use footer_y not lines!
            move_cursor(right_pos, footer_y)
            sys.stdout.write(f"{Colors.BG_DARK}{Colors.WHITE}{right_text}")
            if self.config.show_status_led:
                sys.stdout.write(f"{led_color}{status_led}{Colors.RESET}")
            else:
                sys.stdout.write(Colors.RESET)
            sys.stdout.flush()

        # V527: Final flush and show cursor
        sys.stdout.flush()
        sys.stdout.write('\033[?25h')
        sys.stdout.flush()