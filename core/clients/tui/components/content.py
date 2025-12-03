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
        cols, term_lines = get_terminal_size()

        # V527: Hide cursor during draw
        sys.stdout.write('\033[?25l')

        # Calculate content area dimensions
        # V527 spec: Sidebar=25 chars (cols 1-25), Separator=1 char (col 26), Content starts at col 27
        # Layout: [Sidebar 1-25][│ 26][Content 27+]
        content_x = 27  # Content starts IMMEDIATELY after separator (no gap)
        content_width = cols - content_x - 2
        content_y_start = 3
        # BUGFIX: Footer is at line 'term_lines', so fillable area is from line 2 to line 'term_lines - 1'
        # Content height = (term_lines - 1) - content_y_start = term_lines - content_y_start - 1
        content_height = term_lines - content_y_start - 1  # Fill to line before footer

        # Build entire output in a single buffer to prevent flickering
        output_buffer = []

        # Clear content area and draw separator in one pass
        separator_col = 26
        for y in range(3, term_lines):
            # Clear line
            output_buffer.append(f"\033[{y};{content_x}H{' ' * content_width}")
            # Draw separator
            output_buffer.append(f"\033[{y};{separator_col}H{Colors.DIM}│{Colors.RESET}")

        # Apply lowercase if configured (except for actual command output)
        display_title = title.lower() if self.config.lowercase_ui and not title.startswith("Command") else title

        # Determine title color based on content type
        title_lower = title.lower()
        if "error" in title_lower or "failed" in title_lower:
            title_color = Colors.RED
        elif "success" in title_lower or "started" in title_lower or "completed" in title_lower:
            title_color = Colors.GREEN
        elif "warning" in title_lower or "status" in title_lower:
            title_color = Colors.YELLOW
        else:
            title_color = Colors.CYAN

        # Add title to buffer
        output_buffer.append(f"\033[{content_y_start};{content_x}H{title_color}{Colors.BOLD}{display_title}{Colors.RESET}")

        # Add separator line to buffer
        output_buffer.append(f"\033[{content_y_start + 1};{content_x}H{Colors.DIM}{'─' * min(len(display_title) + 10, content_width)}{Colors.RESET}")

        # Process content
        y = content_y_start + 3
        if content:
            # Split content into lines - handle both string and list types
            if isinstance(content, list):
                lines_list = content
            elif isinstance(content, str):
                lines_list = content.split('\n')
            else:
                lines_list = str(content).split('\n')

            # Wrap long lines
            wrapped_lines = []
            for line in lines_list:
                if len(line) > content_width - 2:
                    wrapped = wrap_text(line, content_width - 2)
                    if isinstance(wrapped, list):
                        wrapped_lines.extend(wrapped)
                    else:
                        wrapped_lines.append(str(wrapped))
                else:
                    wrapped_lines.append(line)

            # Store for potential scrolling
            self.content_lines = wrapped_lines

            # Calculate visible lines with scroll position
            visible_lines = wrapped_lines[self.scroll_position:]
            lines_shown = 0
            total_lines = len(wrapped_lines)

            # Calculate max visible lines
            max_content_lines = content_height - 4

            # Helper function to get line color
            def get_line_color(line: str) -> str:
                if line.startswith('✓') or line.startswith('✅'):
                    return Colors.GREEN
                elif line.startswith('✗') or line.startswith('❌'):
                    return Colors.RED
                elif line.startswith('⚠') or line.startswith('ℹ️'):
                    return Colors.YELLOW
                elif line.startswith('→') or line.startswith('▶') or line.startswith('🌐'):
                    return Colors.ORANGE
                elif line.startswith('#') or line.startswith('='):
                    return Colors.BOLD
                elif line.lower().startswith('command:') or line.lower().startswith('file:'):
                    return Colors.CYAN
                elif line.startswith('─') or line.startswith('━'):
                    return Colors.DIM
                elif line.startswith('  ') or line.startswith('\t'):
                    return Colors.DIM
                elif "error" in line.lower() or "failed" in line.lower():
                    return Colors.RED
                elif "success" in line.lower() or "completed" in line.lower():
                    return Colors.GREEN
                else:
                    return Colors.WHITE

            # Add content lines to buffer
            for line in visible_lines:
                if lines_shown >= max_content_lines:
                    # Show scroll indicator at bottom
                    remaining = total_lines - (self.scroll_position + lines_shown)
                    if remaining > 0:
                        if self.i18n:
                            msg = self.i18n.translate('more_lines', count=remaining)
                        else:
                            msg = f"↓ {remaining} more lines (use arrow keys to scroll)"
                        output_buffer.append(f"\033[{content_y_start + content_height - 1};{content_x}H{Colors.DIM}{msg}{Colors.RESET}")
                    break

                color = get_line_color(line)
                output_buffer.append(f"\033[{y};{content_x}H{color}{line}{Colors.RESET}")
                y += 1
                lines_shown += 1

            # Show scroll indicator at top if scrolled
            if self.scroll_position > 0:
                if self.i18n:
                    msg = self.i18n.translate('lines_above', count=self.scroll_position)
                else:
                    msg = f"↑ {self.scroll_position} lines above"
                output_buffer.append(f"\033[{content_y_start + 2};{content_x}H{Colors.DIM}{msg}{Colors.RESET}")

        # Draw item metadata if available
        if item and hasattr(item, 'metadata'):
            y += 1
            if y < term_lines - 2:
                output_buffer.append(f"\033[{y};{content_x}H{Colors.DIM}───────────{Colors.RESET}")
                y += 1

            metadata = item.metadata
            if isinstance(metadata, dict):
                for key, value in metadata.items():
                    if y >= term_lines - 2:
                        break
                    text = f"{key}: {value}"
                    if self.config.lowercase_ui:
                        text = text.lower()
                    output_buffer.append(f"\033[{y};{content_x}H{Colors.DIM}{text}{Colors.RESET}")
                    y += 1

        # Write entire buffer in one operation to prevent flickering
        sys.stdout.write(''.join(output_buffer))

        # V527: Final flush (keep cursor hidden)
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