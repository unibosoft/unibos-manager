"""
UNIBOS TUI Content Area Component
Right side content area with scrolling support
"""

import sys
from typing import List, Optional, Any

from core.clients.cli.framework.ui import Colors, get_terminal_size, move_cursor, wrap_text


class ContentArea:
    """Content area component for TUI"""

    def __init__(self, config, i18n=None):
        """Initialize content area with config and i18n manager"""
        self.config = config
        self.i18n = i18n
        self.scroll_position = 0
        self.content_lines = []  # Store lines for scrolling

    def draw(self, title: str, content: str = "", item: Optional[Any] = None):
        """
        Draw content area

        V527 SPEC:
        - Content starts at column 27 (sidebar is 25 chars + 2 spacing)
        - Background is transparent/default (NOT dark gray)
        - Content area has no background color

        Args:
            title: Content title
            content: Content text (can be multiline)
            item: Optional menu item for additional context
        """
        cols, lines = get_terminal_size()

        # V527: Hide cursor during draw
        sys.stdout.write('\033[?25l')
        sys.stdout.flush()

        # Calculate content area dimensions
        # V527 spec: Sidebar=25 chars (cols 1-25), Separator=1 char (col 26), Content starts at col 27
        # Layout: [Sidebar 1-25][│ 26][Content 27+]
        content_x = 27  # Content starts IMMEDIATELY after separator (no gap)
        content_width = cols - content_x - 2
        content_y_start = 3
        # BUGFIX: Footer is at line 'lines', so fillable area is from line 2 to line 'lines - 1'
        # Content height = (lines - 1) - content_y_start = lines - content_y_start - 1
        content_height = lines - content_y_start - 1  # Fill to line before footer

        # PERMANENT FIX: Clear content area with proper buffering
        # V527 CRITICAL: Clear from line 3 to line 'lines - 1' (footer is at line 'lines')
        # Line 1 = header, Line 2 = header separator, preserve both
        # Build clear buffer first, then write all at once
        clear_buffer = []
        for y in range(3, lines):  # Clear lines 3 to lines-1, preserve header (lines 1-2)
            clear_buffer.append(f"\033[{y};{content_x}H{' ' * content_width}")

        # Write all clear operations in one buffer
        sys.stdout.write(''.join(clear_buffer))

        # Force flush to ensure clear completes before drawing
        sys.stdout.flush()

        # Redraw separator AFTER clear completes
        self._redraw_separator()

        # Another flush to ensure separator is drawn before content
        sys.stdout.flush()

        # Apply lowercase if configured (except for actual command output)
        display_title = title.lower() if self.config.lowercase_ui and not title.startswith("Command") else title

        # Draw title with dynamic color based on content type
        move_cursor(content_x, content_y_start)
        title_lower = title.lower()
        if "error" in title_lower or "failed" in title_lower:
            title_color = Colors.RED
        elif "success" in title_lower or "started" in title_lower or "completed" in title_lower:
            title_color = Colors.GREEN
        elif "warning" in title_lower or "status" in title_lower:
            title_color = Colors.YELLOW
        else:
            title_color = Colors.CYAN

        sys.stdout.write(f"{title_color}{Colors.BOLD}{display_title}{Colors.RESET}")
        sys.stdout.flush()

        # Draw separator line
        y = content_y_start + 1
        move_cursor(content_x, y)
        sys.stdout.write(f"{Colors.DIM}{'─' * min(len(display_title) + 10, content_width)}{Colors.RESET}")
        sys.stdout.flush()

        # Process content
        y = content_y_start + 3
        if content:
            # Split content into lines - handle both string and list types
            if isinstance(content, list):
                # If content is already a list, use it directly
                lines_list = content
            elif isinstance(content, str):
                # If content is a string, split it
                lines_list = content.split('\n')
            else:
                # Fallback: convert to string and split
                lines_list = str(content).split('\n')

            # Wrap long lines
            wrapped_lines = []
            for line in lines_list:
                if len(line) > content_width - 2:
                    # Wrap long lines but preserve some structure
                    wrapped = wrap_text(line, content_width - 2)
                    # wrap_text() already returns a list, so extend directly
                    if isinstance(wrapped, list):
                        wrapped_lines.extend(wrapped)
                    else:
                        # Fallback for unexpected types
                        wrapped_lines.append(str(wrapped))
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
                        if self.i18n:
                            msg = self.i18n.translate('more_lines', count=remaining)
                        else:
                            msg = f"↓ {remaining} more lines (use arrow keys to scroll)"
                        sys.stdout.write(f"{Colors.DIM}{msg}{Colors.RESET}")
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
                elif line.lower().startswith('command:') or line.lower().startswith('file:'):
                    # Command or file references
                    sys.stdout.write(f"{Colors.CYAN}{line}{Colors.RESET}")
                elif line.startswith('─') or line.startswith('━'):
                    # Separators
                    sys.stdout.write(f"{Colors.DIM}{line}{Colors.RESET}")
                elif line.startswith('  ') or line.startswith('\t'):
                    # Indented (likely code or command)
                    sys.stdout.write(f"{Colors.DIM}{line}{Colors.RESET}")
                elif "error" in line.lower() or "failed" in line.lower():
                    # Error messages
                    sys.stdout.write(f"{Colors.RED}{line}{Colors.RESET}")
                elif "success" in line.lower() or "completed" in line.lower():
                    # Success messages
                    sys.stdout.write(f"{Colors.GREEN}{line}{Colors.RESET}")
                else:
                    sys.stdout.write(f"{Colors.WHITE}{line}{Colors.RESET}")

                y += 1
                lines_shown += 1

            # Show scroll indicator at top if scrolled
            if self.scroll_position > 0:
                move_cursor(content_x, content_y_start + 2)
                if self.i18n:
                    msg = self.i18n.translate('lines_above', count=self.scroll_position)
                else:
                    msg = f"↑ {self.scroll_position} lines above"
                sys.stdout.write(f"{Colors.DIM}{msg}{Colors.RESET}")

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

        # V527: Final flush and show cursor
        sys.stdout.flush()
        sys.stdout.write('\033[?25h')
        sys.stdout.flush()

    def clear(self, x: int, y: int, width: int, height: int):
        """Clear content area"""
        for i in range(height):
            move_cursor(x, y + i)
            sys.stdout.write(' ' * width)

        # Force flush to ensure clearing happens immediately
        sys.stdout.flush()

        # Redraw separator line after clearing (v527 spec)
        self._redraw_separator()

    def _redraw_separator(self):
        """
        Redraw vertical separator line (v527 spec)

        After clearing content area, separator must be redrawn to maintain persistence
        """
        cols, lines = get_terminal_size()
        separator_col = 26  # V527 spec: exactly column 26

        # BUGFIX: Use range(2, lines) to draw separator to line 'lines - 1' (footer is at line 'lines')
        for y in range(2, lines):
            move_cursor(separator_col, y)
            sys.stdout.write(f"{Colors.DIM}│{Colors.RESET}")

        sys.stdout.flush()