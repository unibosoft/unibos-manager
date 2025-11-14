"""
UNIBOS CLI Layout Utilities
Terminal size detection, cursor movement, screen clearing
"""

import os
import sys
import shutil


def get_terminal_size() -> tuple[int, int]:
    """
    Get current terminal size

    Returns:
        Tuple of (columns, lines)
    """
    try:
        size = shutil.get_terminal_size()
        return size.columns, size.lines
    except (AttributeError, ValueError):
        # Fallback to default size
        return 80, 24


def clear_screen():
    """Clear the terminal screen"""
    if sys.platform == 'win32':
        os.system('cls')
    else:
        os.system('clear')
        # Also send ANSI clear code
        print('\033[2J\033[H', end='', flush=True)


def move_cursor(x: int, y: int):
    """
    Move cursor to specific position

    Args:
        x: Column (0-indexed)
        y: Row (0-indexed)
    """
    print(f'\033[{y};{x}H', end='', flush=True)


def hide_cursor():
    """Hide the terminal cursor"""
    print('\033[?25l', end='', flush=True)


def show_cursor():
    """Show the terminal cursor"""
    print('\033[?25h', end='', flush=True)


def save_cursor():
    """Save current cursor position"""
    print('\033[s', end='', flush=True)


def restore_cursor():
    """Restore saved cursor position"""
    print('\033[u', end='', flush=True)


def clear_line():
    """Clear the current line"""
    print('\033[2K', end='', flush=True)


def draw_box(x: int, y: int, width: int, height: int, title: str = "", color: str = ""):
    """
    Draw a box at specified position

    Args:
        x: Starting column
        y: Starting row
        width: Box width
        height: Box height
        title: Optional title for the box
        color: Optional color code
    """
    from .colors import Colors

    # Top border
    move_cursor(x, y)
    if title:
        title_text = f" {title} "
        remaining = width - len(title_text) - 2
        left_border = remaining // 2
        right_border = remaining - left_border
        print(f"{color}╭{'─' * left_border}{title_text}{'─' * right_border}╮{Colors.RESET}")
    else:
        print(f"{color}╭{'─' * width}╮{Colors.RESET}")

    # Side borders
    for i in range(1, height):
        move_cursor(x, y + i)
        print(f"{color}│{' ' * width}│{Colors.RESET}")

    # Bottom border
    move_cursor(x, y + height)
    print(f"{color}╰{'─' * width}╯{Colors.RESET}")


def center_text(text: str, width: int) -> int:
    """
    Calculate x position to center text

    Args:
        text: Text to center
        width: Available width

    Returns:
        X position for centering
    """
    from .colors import Colors
    plain_text = Colors.strip(text)
    return max(0, (width - len(plain_text)) // 2)


def print_centered(text: str, y: int):
    """
    Print text centered horizontally at given y position

    Args:
        text: Text to print
        y: Row position
    """
    cols, _ = get_terminal_size()
    x = center_text(text, cols)
    move_cursor(x, y)
    print(text, end='', flush=True)
