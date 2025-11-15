"""
UNIBOS CLI Layout Engine
Full v527 UI/UX layout with header, sidebar, content, and footer

Extracted from v527 main.py - Complete visual design
Reference: docs/development/cli_v527_reference.md
"""

import sys
import time
from datetime import datetime
from typing import List, Dict, Any, Optional

from .colors import Colors
from .terminal import get_terminal_size, move_cursor


def draw_header(title: str, version: str, breadcrumb: str = "", username: str = ""):
    """
    Draw v527-style header - single line with orange background

    Args:
        title: Application title (e.g., "unibos")
        version: Version string (e.g., "v0.534.0")
        breadcrumb: Navigation breadcrumb (e.g., "Development › Run Server")
        username: Current user
    """
    cols, _ = get_terminal_size()

    # Clear header line
    sys.stdout.write('\033[1;1H\033[2K')

    # Full orange background
    move_cursor(1, 1)
    sys.stdout.write(f"{Colors.BG_ORANGE}{' ' * cols}{Colors.RESET}")
    sys.stdout.flush()

    # Left side: Title + version + breadcrumb
    title_text = f"  🦄 {title} {version}"
    if breadcrumb:
        title_text += f"  ›  {breadcrumb}"

    move_cursor(1, 1)
    sys.stdout.write(f"{Colors.BG_ORANGE}{Colors.BLACK}{Colors.BOLD}{title_text}{Colors.RESET}")

    # Window controls (right side before username)
    controls_text = "[_] [□] [X]"
    controls_pos = cols - len(controls_text) - 2
    move_cursor(controls_pos, 1)
    sys.stdout.write(f"{Colors.BG_ORANGE}{Colors.BLACK}{controls_text}{Colors.RESET}")

    # Username (if provided)
    if username:
        user_text = f"| {username}"
        user_pos = controls_pos - len(user_text) - 2
        move_cursor(user_pos, 1)
        sys.stdout.write(f"{Colors.BG_ORANGE}{Colors.BLACK}{user_text}{Colors.RESET}")

    sys.stdout.flush()


def draw_sidebar_section(
    y_start: int,
    title: str,
    items: List[tuple],  # [(key, label), ...]
    selected_index: int = -1,
    is_dimmed: bool = False,
    sidebar_width: int = 25
):
    """
    Draw a sidebar section with items (v527 exact style)

    Args:
        y_start: Starting Y position
        title: Section title (will be lowercased)
        items: List of (key, label) tuples
        selected_index: Currently selected item index (-1 for none)
        is_dimmed: Whether section should be dimmed
        sidebar_width: Width of sidebar

    Returns:
        int: Next Y position after this section
    """
    cols, lines = get_terminal_size()

    # Section header (lowercase, v527 style)
    move_cursor(1, y_start)
    title_lower = title.lower()
    sys.stdout.write(f"{Colors.BG_DARK}{Colors.ORANGE}{Colors.BOLD} {title_lower:<{sidebar_width-2}} {Colors.RESET}")

    # Items
    y = y_start + 1
    for i, (key, label) in enumerate(items):
        if y >= lines - 1:  # Leave room for footer
            break

        # Ensure label is lowercase
        label_lower = label.lower()

        # Truncate label if too long
        max_label_len = sidebar_width - 3
        if len(label_lower) > max_label_len:
            label_lower = label_lower[:max_label_len - 3] + "..."

        # Determine colors (v527 exact)
        if i == selected_index and not is_dimmed:
            bg = Colors.BG_ORANGE
            fg = Colors.WHITE + Colors.BOLD
        else:
            bg = Colors.BG_DARK
            fg = Colors.DIM if is_dimmed else Colors.WHITE

        # Draw item (v527 exact: full width background, then text at x=2)
        move_cursor(1, y)
        sys.stdout.write(f"{bg}{' ' * sidebar_width}{Colors.RESET}")
        move_cursor(2, y)
        sys.stdout.write(f"{bg}{fg} {label_lower}{Colors.RESET}")

        y += 1

    sys.stdout.flush()
    return y


def draw_sidebar_sections(
    sections: List[Dict[str, Any]],
    current_section: int,
    selected_index: int,
    in_submenu: bool = False,
    sidebar_width: int = 25
):
    """
    Draw all sidebar sections (v527 style)

    Args:
        sections: List of section dicts with 'label' and 'items'
        current_section: Currently active section index
        selected_index: Selected item within current section
        in_submenu: Whether in submenu (dims sidebar)
        sidebar_width: Width of sidebar
    """
    y = 3  # Start after header (line 1) and a blank line (line 2)

    for i, section in enumerate(sections):
        is_current = (i == current_section)
        is_dimmed = in_submenu or not is_current

        # Get items for this section
        items = [(item.id, item.label) for item in section.get('items', [])]

        # Selected index only applies to current section
        sel_idx = selected_index if is_current else -1

        y = draw_sidebar_section(
            y_start=y,
            title=section.get('label', ''),
            items=items,
            selected_index=sel_idx,
            is_dimmed=is_dimmed,
            sidebar_width=sidebar_width
        )

        # Add spacing between sections
        y += 1


def draw_content_area(
    title: str,
    lines: List[str],
    sidebar_width: int = 25,
    content_bg: str = ""
):
    """
    Draw content area (right side, v527 exact style)

    Args:
        title: Content area title (will be lowercased)
        lines: List of content lines to display (will be lowercased)
        sidebar_width: Width of sidebar (to calculate content position)
        content_bg: Optional background color
    """
    cols, term_lines = get_terminal_size()

    content_x = sidebar_width + 2
    content_width = cols - content_x - 2
    content_y_start = 3

    # Title bar (lowercase, v527 style - no border, just title)
    move_cursor(content_x, content_y_start)
    title_lower = title.lower()
    sys.stdout.write(f"{Colors.CYAN}{Colors.BOLD}{title_lower}{Colors.RESET}")

    # Content lines (lowercase)
    y = content_y_start + 2
    for line in lines:
        if y >= term_lines - 1:
            break

        # Ensure lowercase
        line_lower = line.lower()

        # Wrap line if too long
        if len(line_lower) > content_width:
            line_lower = line_lower[:content_width - 3] + "..."

        move_cursor(content_x, y)
        if content_bg:
            sys.stdout.write(f"{content_bg}{Colors.DIM}{line_lower}{Colors.RESET}")
        else:
            sys.stdout.write(f"{Colors.DIM}{line_lower}{Colors.RESET}")

        y += 1

    sys.stdout.flush()


def draw_footer(hints: str = "", location: str = "bitez, bodrum", hostname: str = ""):
    """
    Draw v527-style footer with full details

    Args:
        hints: Navigation hints text (lowercase)
        location: Location text (lowercase)
        hostname: Hostname (lowercase)
    """
    import socket

    cols, lines = get_terminal_size()

    # Full dark background
    move_cursor(1, lines)
    sys.stdout.write(f"{Colors.BG_DARK}{' ' * cols}{Colors.RESET}")

    # Left side: Navigation hints (lowercase, v527 exact format)
    if not hints:
        hints = "↑↓ navigate | enter/→ select | esc/← back | tab switch | q quit"

    move_cursor(2, lines)
    sys.stdout.write(f"{Colors.BG_DARK}{Colors.DIM}{hints}{Colors.RESET}")

    # Get hostname if not provided
    if not hostname:
        try:
            hostname = socket.gethostname().lower()
        except:
            hostname = "localhost"

    # Right side: hostname | location | date | time | status
    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    current_time = now.strftime("%H:%M:%S")
    status_text = "online"
    status_led = "●"  # Green LED

    # Build right side (lowercase)
    right_side = f"{hostname} | {location} | {current_date} | {current_time} | {status_text} "
    right_side_len = len(right_side) + 1  # +1 for LED

    # Calculate position
    right_pos = cols - right_side_len - 2
    right_pos = max(2, right_pos)

    # Draw right side
    move_cursor(right_pos, lines)
    sys.stdout.write(f"{Colors.BG_DARK}{Colors.WHITE}{right_side}{Colors.GREEN}{status_led}{Colors.RESET}")

    sys.stdout.flush()


def clear_content_area(sidebar_width: int = 25):
    """
    Clear the content area (right side)

    Args:
        sidebar_width: Width of sidebar
    """
    cols, lines = get_terminal_size()
    content_x = sidebar_width + 1

    for y in range(3, lines):
        move_cursor(content_x, y)
        sys.stdout.write(' ' * (cols - content_x))

    sys.stdout.flush()


def draw_box(x: int, y: int, width: int, height: int, title: str = "", color: str = Colors.CYAN):
    """
    Draw a box with optional title (v527 style)

    Args:
        x: X position
        y: Y position
        width: Box width
        height: Box height
        title: Optional title
        color: Box color
    """
    # Top border
    move_cursor(x, y)
    if title:
        title_text = f" {title} "
        border = "─" * ((width - len(title_text) - 2) // 2)
        sys.stdout.write(f"{color}┌{border}{title_text}{border}")
        if len(border) * 2 + len(title_text) < width - 2:
            sys.stdout.write("─")
        sys.stdout.write(f"┐{Colors.RESET}")
    else:
        sys.stdout.write(f"{color}┌{'─' * (width - 2)}┐{Colors.RESET}")

    # Sides
    for i in range(1, height - 1):
        move_cursor(x, y + i)
        sys.stdout.write(f"{color}│{' ' * (width - 2)}│{Colors.RESET}")

    # Bottom border
    move_cursor(x, y + height - 1)
    sys.stdout.write(f"{color}└{'─' * (width - 2)}┘{Colors.RESET}")

    sys.stdout.flush()
