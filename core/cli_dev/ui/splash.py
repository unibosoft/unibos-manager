"""
UNIBOS CLI Splash Screen
Animated welcome screen with ASCII art logo
"""

import time
import json
from pathlib import Path
from .colors import Colors
from .layout import clear_screen, get_terminal_size, move_cursor, print_centered


def load_version_info() -> dict:
    """
    Load version information from VERSION.json

    Returns:
        Version info dict
    """
    try:
        # Navigate from core/cli/ui/ to root
        root_dir = Path(__file__).parent.parent.parent.parent
        version_file = root_dir / 'VERSION.json'

        if version_file.exists():
            with open(version_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {
                    'version': data.get('version', 'v533'),
                    'build': data.get('build', 'unknown'),
                    'build_date': data.get('build_date', 'unknown'),
                    'author': data.get('author', 'berk hatırlı'),
                    'location': data.get('location', 'bitez, bodrum, muğla, türkiye')
                }
    except Exception:
        pass

    # Fallback version info
    return {
        'version': 'v533+',
        'build': 'development',
        'build_date': 'unknown',
        'author': 'berk hatırlı',
        'location': 'bitez, bodrum, muğla, türkiye, dünya, güneş sistemi, samanyolu, evren'
    }


def show_splash_screen(quick: bool = False):
    """
    Show animated splash screen with UNIBOS logo

    Args:
        quick: If True, skip animation delays
    """
    clear_screen()
    cols, lines = get_terminal_size()

    # Get version info
    version_info = load_version_info()
    version = version_info['version']

    # Welcome box
    welcome_box = [
        f"{Colors.ORANGE}╭{'─' * 24}╮{Colors.RESET}",
        f"{Colors.ORANGE}│{Colors.RESET} {Colors.BOLD}* welcome to unibos! *{Colors.RESET} {Colors.ORANGE}│{Colors.RESET}",
        f"{Colors.ORANGE}╰{'─' * 24}╯{Colors.RESET}"
    ]

    # ASCII art - Large UNIBOS logo (3D shadow effect)
    logo_art = [
        f"",
        f"{Colors.ORANGE}██╗   ██╗███╗   ██╗██╗██████╗  ██████╗ ███████╗{Colors.RESET}",
        f"{Colors.ORANGE}██║   ██║████╗  ██║██║██╔══██╗██╔═══██╗██╔════╝{Colors.RESET}",
        f"{Colors.ORANGE}██║   ██║██╔██╗ ██║██║██████╔╝██║   ██║███████╗{Colors.RESET}",
        f"{Colors.ORANGE}██║   ██║██║╚██╗██║██║██╔══██╗██║   ██║╚════██║{Colors.RESET}",
        f"{Colors.ORANGE}╚██████╔╝██║ ╚████║██║██████╔╝╚██████╔╝███████║{Colors.RESET}",
        f"{Colors.ORANGE} ╚═════╝ ╚═╝  ╚═══╝╚═╝╚═════╝  ╚═════╝ ╚══════╝{Colors.RESET} {Colors.YELLOW}{version}{Colors.RESET}",
        f""
    ]

    # Calculate centering
    box_width = 26
    logo_width = 48

    # Center welcome box at top
    box_y = 4
    box_x = max(1, (cols - box_width) // 2)

    # Draw welcome box
    for i, line in enumerate(welcome_box):
        move_cursor(box_x, box_y + i)
        print(line, end='', flush=True)
        if not quick:
            time.sleep(0.02)

    # Center the logo art
    logo_y = box_y + 6
    logo_x = max(1, (cols - logo_width) // 2)

    # Animate logo appearance
    animation_delay = 0 if quick else 0.05
    for i, line in enumerate(logo_art):
        move_cursor(logo_x, logo_y + i)
        print(line, end='', flush=True)
        time.sleep(animation_delay)

    # Show additional info below
    info_y = logo_y + len(logo_art) + 2
    location = version_info['location']

    info_lines = [
        f"{Colors.DIM}unicorn bodrum operating system{Colors.RESET}",
        f"{Colors.DIM}build {version_info['build']}{Colors.RESET}",
        f"",
        f"{Colors.DIM}by {version_info['author']}{Colors.RESET}",
        f"{Colors.DIM}{location}{Colors.RESET}"
    ]

    for i, line in enumerate(info_lines):
        # Adjust centering for longer location line
        if i == 4:  # Location line
            text_x = max(1, (cols - len(Colors.strip(location))) // 2)
        else:
            text_x = max(1, (cols - 45) // 2)
        move_cursor(text_x, info_y + i)
        print(line, end='', flush=True)
        if not quick:
            time.sleep(0.03)

    if not quick:
        time.sleep(0.3)

    # Loading animation
    loading_y = info_y + len(info_lines) + 2
    loading_text = "initializing system components..."
    loading_x = max(1, (cols - len(loading_text)) // 2)

    # Show loading text
    move_cursor(loading_x, loading_y)
    print(f"{Colors.DIM}{loading_text}{Colors.RESET}", flush=True)

    if not quick:
        # Animated dots
        dot_x = loading_x + len(loading_text)
        for _ in range(3):
            for i in range(4):
                move_cursor(dot_x, loading_y)
                print(f"{Colors.DIM}{'.' * i}{' ' * (3-i)}{Colors.RESET}", end='', flush=True)
                time.sleep(0.1)

    # Final pause
    if not quick:
        time.sleep(0.5)
    else:
        time.sleep(0.1)


def show_compact_header():
    """Show compact version of header (no animation)"""
    cols, _ = get_terminal_size()
    version_info = load_version_info()

    # Single line header
    header = f"{Colors.ORANGE}🪐 unibos{Colors.RESET} {Colors.YELLOW}{version_info['version']}{Colors.RESET} {Colors.DIM}| unicorn bodrum operating system{Colors.RESET}"

    print_centered(header, 2)
    print()  # Add spacing
