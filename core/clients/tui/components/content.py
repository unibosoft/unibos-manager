"""
UNIBOS TUI Content Area Component
Right side content area with scrolling support
"""

import sys
from typing import List, Optional, Any

from core.clients.cli.framework.ui import Colors, get_terminal_size, move_cursor, wrap_text


class ContentArea:
    """Content area component for TUI"""

    def __init__(self, config):
        """Initialize content area with config"""
        self.config = config
        self.scroll_position = 0
        self.content_lines = []  # Store lines for scrolling

    def draw(self, title: str, content: str = "", item: Optional[Any] = None):
        """
        Draw content area

        Args:
            title: Content title
            content: Content text (can be multiline)
            item: Optional menu item for additional context
        """
        cols, lines = get_terminal_size()

        # Calculate content area dimensions
        content_x = self.config.sidebar_width + 2
        content_width = cols - content_x - 2
        content_y_start = 3
        content_height = lines - content_y_start - 3  # Leave room for footer

        # Clear content area first
        self.clear(content_x, content_y_start, content_width, content_height + 1)

        # Apply lowercase if configured (except for actual command output)
        display_title = title.lower() if self.config.lowercase_ui and not title.startswith("Command") else title

        # Draw title with dynamic color based on content type
        move_cursor(content_x, content_y_start)
        if "Error" in title or "Failed" in title:
            title_color = Colors.RED
        elif "Success" in title or "Started" in title or "Completed" in title:
            title_color = Colors.GREEN
        elif "Warning" in title or "Status" in title:
            title_color = Colors.YELLOW
        else:
            title_color = Colors.CYAN

        sys.stdout.write(f"{title_color}{Colors.BOLD}{display_title}{Colors.RESET}")

        # Draw separator line
        y = content_y_start + 1
        move_cursor(content_x, y)
        sys.stdout.write(f"{Colors.DIM}{'─' * min(len(display_title) + 10, content_width)}{Colors.RESET}")

        # Process content
        y = content_y_start + 3
        if content:
            # Split content into lines
            lines_list = content.split('\n')

            # Wrap long lines
            wrapped_lines = []
            for line in lines_list:
                if len(line) > content_width - 2:
                    # Wrap long lines but preserve some structure
                    wrapped = wrap_text(line, content_width - 2)
                    wrapped_lines.extend(wrapped.split('\n'))
                else:
                    wrapped_lines.append(line)

            # Store for potential scrolling
            self.content_lines = wrapped_lines

            # Calculate visible lines with scroll position
            visible_lines = wrapped_lines[self.scroll_position:]
            lines_shown = 0
            total_lines = len(wrapped_lines)

            # Draw content lines
            for line in visible_lines:
                if lines_shown >= content_height - 2:
                    # Show scroll indicator at bottom
                    remaining = total_lines - (self.scroll_position + lines_shown)
                    if remaining > 0:
                        move_cursor(content_x, content_y_start + content_height)
                        sys.stdout.write(f"{Colors.DIM}↓ {remaining} more lines (use arrow keys to scroll){Colors.RESET}")
                    break

                move_cursor(content_x, y)

                # Special formatting for certain patterns
                if line.startswith('✓') or line.startswith('✅'):
                    sys.stdout.write(f"{Colors.GREEN}{line}{Colors.RESET}")
                elif line.startswith('✗') or line.startswith('❌'):
                    sys.stdout.write(f"{Colors.RED}{line}{Colors.RESET}")
                elif line.startswith('⚠') or line.startswith('ℹ️'):
                    sys.stdout.write(f"{Colors.YELLOW}{line}{Colors.RESET}")
                elif line.startswith('→') or line.startswith('▶') or line.startswith('🌐'):
                    sys.stdout.write(f"{Colors.ORANGE}{line}{Colors.RESET}")
                elif line.startswith('#') or line.startswith('='):
                    # Headers
                    sys.stdout.write(f"{Colors.BOLD}{line}{Colors.RESET}")
                elif line.startswith('Command:') or line.startswith('File:'):
                    # Command or file references
                    sys.stdout.write(f"{Colors.CYAN}{line}{Colors.RESET}")
                elif line.startswith('─') or line.startswith('━'):
                    # Separators
                    sys.stdout.write(f"{Colors.DIM}{line}{Colors.RESET}")
                elif line.startswith('  ') or line.startswith('\t'):
                    # Indented (likely code or command)
                    sys.stdout.write(f"{Colors.DIM}{line}{Colors.RESET}")
                elif "Error" in line or "error" in line or "failed" in line:
                    # Error messages
                    sys.stdout.write(f"{Colors.RED}{line}{Colors.RESET}")
                elif "success" in line or "Success" in line or "completed" in line:
                    # Success messages
                    sys.stdout.write(f"{Colors.GREEN}{line}{Colors.RESET}")
                else:
                    sys.stdout.write(f"{Colors.WHITE}{line}{Colors.RESET}")

                y += 1
                lines_shown += 1

            # Show scroll indicator at top if scrolled
            if self.scroll_position > 0:
                move_cursor(content_x, content_y_start + 2)
                sys.stdout.write(f"{Colors.DIM}↑ {self.scroll_position} lines above{Colors.RESET}")

        # Draw item metadata if available
        if item and hasattr(item, 'metadata'):
            y += 1
            if y < lines - 2:
                move_cursor(content_x, y)
                sys.stdout.write(f"{Colors.DIM}───────────{Colors.RESET}")
                y += 1

            metadata = item.metadata
            if isinstance(metadata, dict):
                for key, value in metadata.items():
                    if y >= lines - 2:
                        break
                    move_cursor(content_x, y)
                    text = f"{key}: {value}"
                    if self.config.lowercase_ui:
                        text = text.lower()
                    sys.stdout.write(f"{Colors.DIM}{text}{Colors.RESET}")
                    y += 1

        sys.stdout.flush()

    def clear(self, x: int, y: int, width: int, height: int):
        """Clear content area"""
        for i in range(height):
            move_cursor(x, y + i)
            sys.stdout.write(' ' * width)