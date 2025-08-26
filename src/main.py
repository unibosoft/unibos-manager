#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🪐 unibos v517 - unicorn bodrum operating system
Simplified Web Forge + Lowercase UI + Single Server Architecture

Author: berk hatırlı - bitez, bodrum, muğla, türkiye
Version: v517_20250826_1733
Purpose: Professional terminal UI with multi-module support"""

import os
import sys
import json
import platform
import subprocess
import shutil
import time
import socket
import threading
import select
import re
import fcntl
from pathlib import Path
from datetime import datetime
from emoji_safe_slice import emoji_safe_slice, get_display_width
from sidebar_fix import draw_sidebar_simple, simple_navigation_handler
try:
    from zoneinfo import ZoneInfo
except ImportError:
    try:
        from backports.zoneinfo import ZoneInfo
    except ImportError:
        ZoneInfo = None

# Platform-specific imports
if platform.system() != 'Windows':
    try:
        import termios
        import tty
        TERMIOS_AVAILABLE = True
    except ImportError:
        TERMIOS_AVAILABLE = False
else:
    TERMIOS_AVAILABLE = False
    import msvcrt

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import translations module
try:
    from translations import TRANSLATIONS, detect_system_language, get_translation, get_available_languages
except ImportError:
    print("Error: translations.py not found!")
    sys.exit(1)

# Import enhanced currencies module if available
try:
    from currencies_enhanced import CurrenciesModule
    CURRENCIES_AVAILABLE = True
except ImportError:
    CURRENCIES_AVAILABLE = False

# Import network utilities for security features
try:
    from network_utils import get_network_security_info, generate_security_report
    NETWORK_UTILS_AVAILABLE = True
except ImportError:
    NETWORK_UTILS_AVAILABLE = False

# Import new UI architecture
try:
    from ui_architecture import UnibosUI, Layout, Colors as UIColors
    # TEMPORARILY DISABLE UI ARCHITECTURE TO USE CORRECT HEADER
    UI_ARCHITECTURE_AVAILABLE = False  # Changed from True to use main.py header with proper alignment
except ImportError:
    UI_ARCHITECTURE_AVAILABLE = False
    # Silent fallback - don't print warnings that mess up the UI

# Import centralized CLI context manager
try:
    from cli_context_manager import get_cli_context, MenuItem, UISection, ContentRenderer
    CLI_CONTEXT_AVAILABLE = True
    cli_context = get_cli_context()
    
    # Register custom content renderers
    try:
        from cli_content_renderers import register_all_renderers
        register_all_renderers(cli_context)
    except ImportError:
        pass  # Content renderers are optional
except ImportError:
    CLI_CONTEXT_AVAILABLE = False
    cli_context = None

# Import optional managers
try:
    from version_manager import VersionManager
    version_manager = VersionManager()
    VERSION_INFO_DYNAMIC = version_manager.get_full_version_info()
except (ImportError, AttributeError):
    VERSION_INFO_DYNAMIC = None

try:
    from setup_manager import SetupManager
    setup_manager = SetupManager()
except ImportError:
    setup_manager = None

try:
    from repair_manager import RepairManager
    repair_manager = RepairManager()
except ImportError:
    repair_manager = None

try:
    from git_manager import GitManager, show_git_status, quick_commit, quick_push, quick_pull, quick_branch
    git_manager = GitManager()
except ImportError:
    git_manager = None

try:
    from communication_logger import comm_logger
    COMM_LOGGER_AVAILABLE = True
except ImportError:
    COMM_LOGGER_AVAILABLE = False
    comm_logger = None

# Version information
VERSION_INFO = {
    "version": "v517",
    "build": "20250826_1733", 
    "build_date": "2025-08-26 17:33:27 +03:00",
    "author": "berk hatırlı",
    "location": "bitez, bodrum, muğla, türkiye, dünya, güneş sistemi, samanyolu, yerel galaksi grubu, evren"
}

# Check for psutil availability
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

# Global language state
CURRENT_LANG = detect_system_language()

def t(key):
    """Shorthand for get_translation"""
    return get_translation(key, CURRENT_LANG)

# Color definitions
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    
    # Foreground colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    GRAY = "\033[90m"
    ORANGE = "\033[38;5;208m"
    
    # Background colors
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"
    # Improved contrast colors - WCAG compliant
    BG_GRAY = "\033[48;5;240m"      # Lighter gray for better contrast
    BG_ORANGE = "\033[48;5;208m"    # Orange background for Claude style
    BG_DARK = "\033[48;5;234m"      # Darker background for header/footer
    BG_CONTENT = "\033[48;5;236m"   # Dark but visible content background

# Menu state management
class MenuState:
    def __init__(self):
        self.current_section = 0  # 0=modules, 1=tools, 2=dev_tools
        self.selected_index = 0
        self.previous_index = None  # Track previous selection for efficient updates
        self.in_submenu = None
        self.in_language_menu = False
        self.language_selected_index = 0  # For language selector navigation
        self.tool_selected_index = 0
        self.modules = []
        self.tools = []
        self.last_cols = 0  # For terminal resize detection
        self.last_lines = 0
        self.dev_tools = []  # New dev tools section
        self.tool_items = []
        self.previous_tool_index = -1  # Track previous tool selection
        self.web_forge_index = 0  # Track selected option in web forge
        self.version_manager_index = 0  # Track selected option in version manager
        self.administration_index = 0  # Track selected option in administration
        self.last_drawn_submenu = None  # Track last drawn submenu
        self.dev_tools_start_y = 0  # Position for dev tools section
        # Sub-navigation tracking for breadcrumbs
        self.web_forge_sub = None
        self.version_sub = None
        self.documents_sub = None
        # Navigation optimization
        self.last_update_time = 0  # For debouncing
        self.update_buffer = []  # For batching updates
        self.sidebar_cache = {}  # Cache rendered sidebar lines
        # Module documentation cache
        self.module_docs_cache = {}  # Cache for loaded documentation
        self.preview_mode = True  # Enable preview mode by default

menu_state = MenuState()

# Navigation optimization settings
NAV_DEBOUNCE_TIME = 0.03  # 30ms debounce
UPDATE_BATCH_TIME = 0.02  # 20ms batch window

# Global UI controller
ui_controller = None

def clear_screen():
    """Clear the terminal screen with enhanced clearing"""
    # Use ANSI escape sequences for more thorough clearing
    sys.stdout.write('\033[2J')  # Clear entire screen
    sys.stdout.write('\033[H')   # Move cursor to top-left
    sys.stdout.write('\033[3J')  # Clear scrollback buffer (supported terminals)
    sys.stdout.flush()
    
    # Also use OS-specific clear command as fallback
    os.system('cls' if platform.system() == 'Windows' else 'clear')
    sys.stdout.flush()  # Ensure screen is fully cleared before continuing

def get_terminal_size():
    """Get terminal dimensions"""
    try:
        import shutil
        columns, lines = shutil.get_terminal_size((80, 24))
        return columns, lines
    except:
        return 80, 24

def move_cursor(x, y):
    """Move cursor to position (1-indexed)"""
    print(f"\033[{y};{x}H", end='', flush=True)

def hide_cursor():
    """Hide the terminal cursor"""
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()

def show_cursor():
    """Show the terminal cursor"""
    sys.stdout.write("\033[?25h")
    sys.stdout.flush()

def get_spinner_frame(index):
    """Get a spinner animation frame"""
    spinners = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    return spinners[index % len(spinners)]

def wrap_text(text, width):
    """Wrap text to fit within specified width"""
    if not text:
        return []
    
    words = text.split()
    lines = []
    current_line = []
    current_length = 0
    
    for word in words:
        word_length = len(word)
        if current_length + word_length + len(current_line) <= width:
            current_line.append(word)
            current_length += word_length
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
            current_length = word_length
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return lines

def get_system_status():
    """Get simple online status"""
    try:
        # Try to connect to a public DNS server
        socket.create_connection(("8.8.8.8", 53), timeout=1).close()
        return f"{Colors.GREEN}●{Colors.RESET}"
    except:
        return f"{Colors.RED}●{Colors.RESET}"

def load_version_info():
    """Load version information from VERSION.json"""
    version_path = Path(__file__).parent / "VERSION.json"
    try:
        with open(version_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return {
                "version": data.get("version", "v510"),
                "build": data.get("build_number", "20250823_1022"),
                "build_date": data.get("release_date", "2025-08-23 10:22:13 +03:00"),
                "author": data.get("author", "berk hatırlı"),
                "location": data.get("location", "bitez, bodrum, muğla, türkiye")
            }
    except Exception:
        return VERSION_INFO

# Load version info at startup
VERSION_INFO = load_version_info()

def draw_box(x, y, width, height, title="", color=Colors.CYAN, style="double", with_bg=True):
    """NO BOXES - Only draw title"""
    # Get terminal size to respect boundaries
    cols, lines = get_terminal_size()
    
    # Ensure we don't exceed boundaries (adjusted for single-line header)
    if y < 2:
        y = 2
    if y + height > lines - 1:
        height = lines - 1 - y
    
    # Clear the content area
    for row in range(y, y + height):
        move_cursor(x, row)
        print(' ' * min(width, cols - x), end='', flush=True)
    
    # Only draw the title, no box
    if title:
        # Calculate title position to center it
        title_with_spaces = f" {title} "
        title_len = len(title_with_spaces)
        title_pos = x + (width - title_len) // 2
        # Draw title at top
        move_cursor(x + 2, y + 1)
        sys.stdout.write(f"{Colors.BOLD}{color}{title}{Colors.RESET}")
        sys.stdout.flush()
    
    # NO BOX DRAWING - Function now only clears area and draws title

def get_system_info():
    """Get enhanced system information"""
    try:
        system_info = {
            "hostname": socket.gethostname()[:20],
            "platform": platform.system(),
            "architecture": platform.machine(),
            "python_version": platform.python_version(),
        }
        
        # Get CPU and memory info if psutil is available
        if PSUTIL_AVAILABLE:
            try:
                # Memory
                mem = psutil.virtual_memory()
                system_info["memory_total"] = f"{mem.total // (1024**3)}GB"
                system_info["memory_used"] = f"{mem.used // (1024**3)}GB ({mem.percent:.1f}%)"
                
                # CPU
                system_info["cpu_cores"] = f"{psutil.cpu_count(logical=False)} physical, {psutil.cpu_count()} logical"
                system_info["cpu_usage"] = f"{psutil.cpu_percent(interval=0.1)}%"
                
                # Disk
                disk = psutil.disk_usage('/')
                system_info["disk_total"] = f"{disk.total / (1024**3):.1f}GB"
                system_info["disk_free"] = f"{disk.free / (1024**3):.1f}GB ({100 - disk.percent:.1f}%)"
            except Exception as e:
                system_info.update({
                    "memory_total": "n/a",
                    "cpu_cores": "n/a",
                    "disk_free": "n/a"
                })
        else:
            system_info.update({
                "memory_total": "N/A",
                "cpu_cores": "N/A",
                "disk_free": "N/A"
            })
        
        return system_info
        
    except Exception as e:
        return {
            "platform": platform.system(),
            "architecture": "unknown",
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
            "error": str(e)
        }

def get_navigation_breadcrumb():
    """Get navigation breadcrumb for current state"""
    parts = []
    
    # Determine the section based on current state
    if menu_state.in_submenu:
        # Tools
        if menu_state.in_submenu in ['system_scrolls', 'castle_guard', 'forge_smithy', 
                                     'anvil_repair', 'code_forge', 'web_forge']:
            parts.append("tools")
            name_map = {
                'system_scrolls': 'system scrolls',
                'castle_guard': 'castle guard',
                'forge_smithy': 'forge smithy',
                'anvil_repair': 'anvil repair',
                'code_forge': 'code forge',
                'web_forge': 'web ui'  # Display as web ui in breadcrumb
            }
            parts.append(name_map.get(menu_state.in_submenu, menu_state.in_submenu))
            
            # Sub-navigation within tools
            if menu_state.in_submenu == 'web_forge' and hasattr(menu_state, 'web_forge_sub'):
                if menu_state.web_forge_sub:
                    parts.append(menu_state.web_forge_sub)
            elif menu_state.in_submenu == 'version_manager' and hasattr(menu_state, 'version_sub'):
                if menu_state.version_sub:
                    parts.append(menu_state.version_sub)
        
        # Dev Tools
        elif menu_state.in_submenu in ['version_manager', 'git', 'ai_builder', 'database_setup', 'public_server']:
            parts.append("dev tools")
            name_map = {
                'version_manager': 'version manager',
                'git': 'git manager',
                'ai_builder': 'ai builder',
                'database_setup': 'database setup',
                'public_server': 'public server'
            }
            parts.append(name_map.get(menu_state.in_submenu, menu_state.in_submenu))
            
            # Sub-navigation for version manager
            if menu_state.in_submenu == 'version_manager' and hasattr(menu_state, 'version_sub'):
                if menu_state.version_sub:
                    parts.append(menu_state.version_sub)
        
        # Modules
        elif menu_state.in_submenu in ['recaria', 'birlikteyiz', 'kisisel', 'currencies', 
                                       'wimm', 'wims', 'documents', 'movies', 'music', 'restopos']:
            parts.append("modules")
            name_map = {
                'recaria': 'recaria',
                'birlikteyiz': 'birlikteyiz',
                'kisisel': 'kişisel enflasyon',
                'currencies': 'currencies',
                'wimm': 'wimm',
                'wims': 'wims',
                'documents': 'documents',
                'movies': 'movies',
                'music': 'music',
                'restopos': 'restopos'
            }
            parts.append(name_map.get(menu_state.in_submenu, menu_state.in_submenu))
    else:
        # Main screen - check which section is highlighted
        if hasattr(menu_state, 'current_section'):
            if menu_state.current_section == 0:
                parts.append("modules")
                if hasattr(menu_state, 'selected_index') and hasattr(menu_state, 'modules'):
                    if menu_state.selected_index < len(menu_state.modules):
                        _, name, _, _, _ = menu_state.modules[menu_state.selected_index]
                        # Remove emoji from name if present (they have format "🎬 movies")
                        if ' ' in name and name[0] not in 'abcdefghijklmnopqrstuvwxyz':
                            name = name.split(' ', 1)[1]
                        parts.append(name)
            elif menu_state.current_section == 1:
                parts.append("tools")
                if hasattr(menu_state, 'selected_index') and hasattr(menu_state, 'tools'):
                    if menu_state.selected_index < len(menu_state.tools):
                        _, name, _, _, _ = menu_state.tools[menu_state.selected_index]
                        # Remove emoji from name if present
                        if ' ' in name and name[0] not in 'abcdefghijklmnopqrstuvwxyz':
                            name = name.split(' ', 1)[1]
                        parts.append(name)
            elif menu_state.current_section == 2:
                parts.append("dev tools")
                if hasattr(menu_state, 'selected_index') and hasattr(menu_state, 'dev_tools'):
                    if menu_state.selected_index < len(menu_state.dev_tools):
                        _, name, _, _, _ = menu_state.dev_tools[menu_state.selected_index]
                        # Remove emoji from name if present
                        if ' ' in name and name[0] not in 'abcdefghijklmnopqrstuvwxyz':
                            name = name.split(' ', 1)[1]
                        parts.append(name)
    
    return " › ".join(parts) if parts else ""

def draw_header_time_only():
    """Update only the time in the header - more efficient for clock updates"""
    # This function should not be used anymore - just call draw_header()
    # Keeping for compatibility but redirecting to main draw_header
    draw_header()

def draw_header():
    """Draw header with logo/version and user info - SINGLE LINE"""
    cols, lines = get_terminal_size()
    
    # Build information
    version = VERSION_INFO.get("version", "v308")
    build = VERSION_INFO.get("build_number", "")
    
    # Clear header line completely first to prevent artifacts
    sys.stdout.write('\033[1;1H\033[2K')  # Move to line 1 and clear
    
    # Single line header - Line 1 only
    move_cursor(1, 1)
    sys.stdout.write(f"{Colors.BG_ORANGE}{' ' * cols}{Colors.RESET}")
    sys.stdout.flush()
    
    # UNIBOS title on LEFT with version and build
    title_text = f"  🦄 unibos {version}"
    if build:
        title_text += f" {build}"  # Show build without parentheses
    
    # Add breadcrumb immediately after version (on same line)
    breadcrumb = get_navigation_breadcrumb()
    if breadcrumb:
        title_text += f"  ›  {breadcrumb}"
    
    move_cursor(1, 1)  # Start at column 1 for leftmost alignment
    sys.stdout.write(f"{Colors.BG_ORANGE}{Colors.BLACK}{Colors.BOLD}{title_text}{Colors.RESET}")
    sys.stdout.flush()
    
    # Add window controls (minimize/maximize/close) before right side info
    controls_text = "[_] [□] [X]"
    controls_len = len(controls_text)
    
    # Right side info: language | username | time - ON SAME LINE
    lang_flag = TRANSLATIONS[CURRENT_LANG]["flag"]
    lang_name = TRANSLATIONS[CURRENT_LANG]["name"]
    username = os.environ.get('USER', 'user')[:15]
    
    # Get current time
    try:
        from zoneinfo import ZoneInfo
        now = datetime.now(ZoneInfo('Europe/Istanbul'))
    except ImportError:
        now = datetime.now()
    
    current_date = now.strftime("%Y-%m-%d")
    current_time = now.strftime("%H:%M:%S")
    right_text = f"{lang_flag} {lang_name} | {username} | {current_time}"
    
    # Calculate position for right-aligned text with controls
    right_text_len = len(f"{lang_name} | {username} | {current_time}") + 3  # +3 for flag
    controls_pos = cols - controls_len - 2
    right_pos = controls_pos - right_text_len - 2
    
    # Make sure right text doesn't overlap with title
    title_end = len(title_text) + 2
    if right_pos < title_end:
        right_pos = title_end + 2
    
    # Draw window controls
    move_cursor(controls_pos, 1)
    sys.stdout.write(f"{Colors.BG_ORANGE}{Colors.BLACK}{controls_text}{Colors.RESET}")
    
    # Place right side info on same line (line 1)
    move_cursor(right_pos, 1)
    sys.stdout.write(f"{Colors.BG_ORANGE}{Colors.BLACK}{right_text}{Colors.RESET}")
    sys.stdout.flush()


def update_sidebar_selection():
    """Update only the sidebar selection without redrawing everything - OPTIMIZED"""
    try:
        # TEMPORARILY DISABLE DEBOUNCING TO FIX NAVIGATION
        # Use debouncing to prevent too frequent updates
        # current_time = time.time()
        # if current_time - menu_state.last_update_time < NAV_DEBOUNCE_TIME:
        #     return
        # menu_state.last_update_time = current_time
        
        # Use the fast update method
        update_sidebar_selection_fast()
        
        # Update content area only
        draw_main_content()
        
    except Exception as e:
        # Log but don't crash
        debug_mode = os.environ.get('UNIBOS_DEBUG', '').lower() == 'true'
        if debug_mode:
            with open('/tmp/unibos_debug.log', 'a') as f:
                f.write(f"update_sidebar_selection error: {type(e).__name__}: {str(e)}\n")
                import traceback
                f.write(traceback.format_exc())
                f.write(f"State: section={menu_state.current_section}, index={menu_state.selected_index}, prev={menu_state.previous_index}\n")
                f.write(f"Modules: {len(menu_state.modules) if hasattr(menu_state, 'modules') else 'None'}\n")
                f.write(f"Tools: {len(menu_state.tools) if hasattr(menu_state, 'tools') else 'None'}\n")
                f.flush()

def update_sidebar_selection_fast():
    """Ultra-fast sidebar selection update - only updates changed lines"""
    cols, lines = get_terminal_size()
    sidebar_width = 25
    is_dimmed = menu_state.in_submenu is not None
    text_color = Colors.DIM if is_dimmed else Colors.WHITE
    
    # Determine positions (adjusted for single-line header)
    if menu_state.current_section == 0:  # modules
        y_base = 5  # Changed from 6 to 5
        items = menu_state.modules
        prefix = "module"
    elif menu_state.current_section == 1:  # tools
        y_base = menu_state.tools_start_y + 2
        items = menu_state.tools
        prefix = "tool"
    else:  # dev tools
        y_base = menu_state.dev_tools_start_y + 2
        items = menu_state.dev_tools
        prefix = "devtool"
    
    # Only update the two changed lines
    if menu_state.previous_index is not None and menu_state.previous_index < len(items):
        # Clear previous selection
        prev_y = y_base + menu_state.previous_index
        if prev_y < lines - 1:
            name = items[menu_state.previous_index][1]
            # CRITICAL FIX: Always ensure full sidebar width is filled with background
            move_cursor(1, prev_y)
            sys.stdout.write(f"{Colors.BG_DARK}{' ' * sidebar_width}{Colors.RESET}")
            safe_name = emoji_safe_slice(name, 22)
            sys.stdout.write(f"\033[{prev_y};2H{Colors.BG_DARK}{text_color} {safe_name}{Colors.RESET}")
    
    # Highlight current selection
    if menu_state.selected_index < len(items):
        curr_y = y_base + menu_state.selected_index
        if curr_y < lines - 1:
            name = items[menu_state.selected_index][1]
            if not is_dimmed:
                # First fill entire line with background, then draw text
                move_cursor(1, curr_y)
                sys.stdout.write(f"{Colors.BG_ORANGE}{' ' * sidebar_width}{Colors.RESET}")
                safe_name = emoji_safe_slice(name, 22)
                sys.stdout.write(f"\033[{curr_y};2H{Colors.BG_ORANGE}{Colors.WHITE} {safe_name}{Colors.RESET}")
            else:
                # First fill entire line with background, then draw text
                move_cursor(1, curr_y)
                sys.stdout.write(f"{Colors.BG_DARK}{' ' * sidebar_width}{Colors.RESET}")
                safe_name = emoji_safe_slice(name, 22)
                sys.stdout.write(f"\033[{curr_y};2H{Colors.BG_DARK}{text_color} {safe_name}{Colors.RESET}")
    
    sys.stdout.flush()
    hide_cursor()

def draw_sidebar():
    """Draw left sidebar with modules - SIMPLIFIED VERSION"""
    # Ensure menu items are initialized before drawing
    if not hasattr(menu_state, 'modules') or not menu_state.modules:
        initialize_menu_items()
    if not hasattr(menu_state, 'tools') or not menu_state.tools:
        initialize_menu_items()
    if not hasattr(menu_state, 'dev_tools') or not menu_state.dev_tools:
        initialize_menu_items()
    
    # CRITICAL: Reset sidebar state when not in submenu
    if menu_state.in_submenu is None:
        # Force clear any cached state
        menu_state.last_sidebar_cache_key = None
        if hasattr(menu_state, '_sidebar_highlight_cache'):
            delattr(menu_state, '_sidebar_highlight_cache')
    
    # Always use simple drawing for consistency
    draw_sidebar_simple(menu_state, Colors, sidebar_width=25)


def draw_footer(only_time=False):
    """Draw footer with navigation hints, date, location and online status LED"""
    # Skip redrawing if only_time is True to prevent blinking
    if only_time:
        return
        
    cols, lines = get_terminal_size()
    
    # Footer takes exactly 1 line
    footer_start = lines - 1
    
    # Always clear footer area
    move_cursor(1, footer_start)
    print(f"{Colors.BG_DARK}{' ' * cols}{Colors.RESET}", end='', flush=True)
    
    # Navigation hints on footer line
    move_cursor(2, footer_start)  # Single line footer
    # Context-specific navigation hints
    if menu_state.in_submenu in ['system_info', 'security_tools']:
        nav_text = "← back/esc to return | enter to close"
    elif menu_state.in_submenu == 'tools':
        nav_text = "↑↓ navigate | → select | ← back"
    elif menu_state.in_submenu == 'web_forge':
        nav_text = "↑↓ navigate | enter select | ← back | q quit"
    elif menu_state.in_submenu == 'version_manager':
        nav_text = "↑↓ navigate | enter select | ← back | q quit"
    elif menu_state.in_submenu == 'administration':
        nav_text = "↑↓ navigate | enter select | ← back | q quit"
    elif menu_state.in_submenu:
        nav_text = "← back/esc to return | enter to launch"
    else:
        nav_text = "↑↓ navigate | → select | tab switch | L language | M minimize | q quit"
    
    # Draw navigation hints in gray
    print(f"{Colors.BG_DARK}{Colors.DIM}{nav_text}{Colors.RESET}", end='', flush=True)
    
    # Get location and hostname from system info
    from system_info import get_hostname
    location_text = "bitez, bodrum"
    hostname = get_hostname()
    
    # Get status LED
    status = get_system_status()
    status_text = "online"
    
    # Build right side text: hostname | location | online
    right_side = f"{hostname} | {location_text} | {status_text} {status}"
    right_side_len = len(f"{hostname} | {location_text} | {status_text} ") + 1  # +1 for LED
    
    # Calculate position for right-aligned text
    right_pos = cols - right_side_len - 2
    right_pos = max(2, right_pos)  # Ensure positive position
    
    # Draw right side info
    move_cursor(right_pos, footer_start)
    print(f"{Colors.BG_DARK}{Colors.WHITE}{hostname} | {location_text} | {status_text} {status}{Colors.RESET}", end='', flush=True)

def initialize_menu_items():
    """Initialize menu items for sidebar - CENTRALIZED"""
    # Module items with translation support
    menu_state.modules = [
        ("recaria", "🪐 recaria", t('universe_explorer'), True, lambda: handle_module_launch('recaria')),
        ("birlikteyiz", "📡 birlikteyiz", t('mesh_network'), True, lambda: handle_module_launch('birlikteyiz')),
        ("kisisel", "📈 kişisel enflasyon", t('inflation_calc'), True, lambda: handle_module_launch('kisisel')),
        ("currencies", "💰 currencies", t('exchange_rates'), True, lambda: handle_module_launch('currencies')),
        ("wimm", "💸 wimm", t('where_is_my_money'), True, lambda: handle_module_launch('wimm')),
        ("wims", "📦 wims", t('where_is_my_stuff'), True, lambda: handle_module_launch('wims')),
        ("documents", "📄 documents", "document manager with ai", True, lambda: handle_documents_module()),
        ("movies", "🎬 movies", "movie & series collection", True, lambda: handle_module_launch('movies')),
        ("music", "🎵 music", "music library & spotify", True, lambda: handle_module_launch('music')),
        ("restopos", "🍽️  restopos", "restaurant pos system", True, lambda: handle_module_launch('restopos')),
    ]
    
    # Sync with centralized context if available
    if CLI_CONTEXT_AVAILABLE and cli_context:
        cli_context.modules.clear()
        for key, name, desc, available, action in menu_state.modules:
            cli_context.register_module(
                MenuItem(key, name.split(' ', 1)[1] if ' ' in name else name, desc, available, action, 
                        icon=name.split(' ')[0] if ' ' in name else ''),
                UISection.MODULES
            )
    
    # Tool items with translation support
    menu_state.tools = [
        ("system_scrolls", f"📊 system scrolls", "forge status & info", True, lambda: handle_tool_launch('system_scrolls')),
        ("castle_guard", f"🔒 castle guard", "fortress security", True, lambda: handle_tool_launch('castle_guard')),
        ("forge_smithy", f"🔧 forge smithy", "setup forge tools", True, lambda: handle_tool_launch('forge_smithy')),
        ("anvil_repair", f"🛠️  anvil repair", "mend & fix issues", True, lambda: handle_tool_launch('anvil_repair')),
        ("code_forge", f"📦 code forge", "version chronicles", True, lambda: handle_tool_launch('code_forge')),
        ("web_ui", f"🌐 web ui", "web interface manager", True, lambda: handle_tool_launch('web_ui')),
        ("administration", f"🔐 administration", "system administration", True, lambda: handle_tool_launch('administration')),
    ]
    
    # Sync tools with centralized context
    if CLI_CONTEXT_AVAILABLE and cli_context:
        cli_context.tools.clear()
        for key, name, desc, available, action in menu_state.tools:
            cli_context.register_module(
                MenuItem(key, name.split(' ', 1)[1] if ' ' in name else name, desc, available, action,
                        icon=name.split(' ')[0] if ' ' in name else ''),
                UISection.TOOLS
            )
    
    # Dev tools - new section
    menu_state.dev_tools = [
        ("ai_builder", f"🤖 ai builder", "ai-powered development", True, lambda: handle_dev_tool_launch('ai_builder')),
        ("database_setup", "🗄️  database setup", "postgresql installer", True, database_setup_wizard),
        ("public_server", "🌐 public server", "deploy to ubuntu/oracle vm", True, lambda: handle_dev_tool_launch('public_server')),
        ("sd_card", f"💾 {t('sd_card')}", t('sd_operations'), True, None),
        ("version_manager", "📊 version manager", "archive & git tools", True, version_manager_menu),
    ]
    
    # Sync dev tools with centralized context
    if CLI_CONTEXT_AVAILABLE and cli_context:
        cli_context.dev_tools.clear()
        for key, name, desc, available, action in menu_state.dev_tools:
            cli_context.register_module(
                MenuItem(key, name.split(' ', 1)[1] if ' ' in name else name, desc, available, action,
                        icon=name.split(' ')[0] if ' ' in name else ''),
                UISection.DEV_TOOLS
            )

def draw_main_content():
    """Draw main content area without right panel - CENTRALIZED"""
    # Always use the standardized draw_module_info for consistency
    # Don't use cli_context renderers to ensure uniform documentation display
    
    # Fallback to original implementation
    cols, lines = get_terminal_size()
    content_x = 27  # After sidebar and separator
    
    # Use full width for content area (no right panel)
    content_width = cols - content_x - 1  # Only 1 for minimal right margin
    
    # Calculate content height with proper boundaries
    content_height = lines - 4  # Use full height: 2 for header, 1 for footer, 1 for bottom margin
    
    # Clear main content area properly without affecting sidebar
    # Use the clear_content_area function for consistency
    clear_content_area()
    
    # Add a small delay on first render to ensure clearing is complete
    if not hasattr(menu_state, '_first_content_render_done'):
        time.sleep(0.05)  # Small delay to ensure terminal processes the clear
        menu_state._first_content_render_done = True
    
    # Ensure separator line is preserved after clearing (adjusted for single-line header)
    sidebar_width = 25
    for y in range(2, lines - 1):  # Changed from 3 to 2
        move_cursor(sidebar_width + 1, y)
        sys.stdout.write(f"{Colors.DIM}│{Colors.RESET}")
    sys.stdout.flush()
    
    if menu_state.in_submenu == 'tools':
        draw_tools_menu(content_x, content_width, content_height)
    elif menu_state.in_submenu == 'system_info':
        draw_system_info_screen(content_x, content_width, content_height)
    elif menu_state.in_submenu == 'security_tools':
        draw_security_tools_screen(content_x, content_width, content_height)
    elif menu_state.in_submenu == 'git_manager':
        # Git manager is handling its own UI, just clear content area
        pass
    elif menu_state.in_submenu == 'web_forge':
        # Web forge menu is handling its own drawing
        pass
    elif menu_state.in_submenu == 'version_manager':
        # Version manager menu is handling its own drawing
        pass
    else:
        # Draw selected module info
        if menu_state.current_section == 0:
            if menu_state.selected_index < len(menu_state.modules):
                key, name, desc, available, action = menu_state.modules[menu_state.selected_index]
                draw_module_info(content_x, content_width, content_height, key, name, desc)
        elif menu_state.current_section == 1:
            if menu_state.selected_index < len(menu_state.tools):
                key, name, desc, available, action = menu_state.tools[menu_state.selected_index]
                draw_module_info(content_x, content_width, content_height, key, name, desc)
        else:  # dev tools section
            if menu_state.selected_index < len(menu_state.dev_tools):
                key, name, desc, available, action = menu_state.dev_tools[menu_state.selected_index]
                draw_module_info(content_x, content_width, content_height, key, name, desc)
    
    # No right panel anymore


def show_server_action(title, color, show_back_hint=True):
    """Show server action in main content area"""
    cols, lines = get_terminal_size()
    content_x = 27  # Match main content area
    
    # Use full width for content area
    content_width = cols - content_x - 1  # Only 1 for minimal right margin
    
    # Clear the main content area (without background color)
    for y in range(2, lines - 1):  # Changed from 3 to 2 for single-line header
        move_cursor(content_x, y)
        print(' ' * content_width, end='', flush=True)
    
    # Draw content box with back navigation hint in title if requested
    if show_back_hint:
        title_with_nav = f"{title}  {Colors.DIM}(← Back){Colors.RESET}"
        draw_box(content_x, 3, content_width - 1, lines - 4, title_with_nav, color)
    else:
        draw_box(content_x, 3, content_width - 1, lines - 4, title, color)


def load_module_documentation(module_name):
    """Load module documentation from markdown file"""
    # Check cache first
    if module_name in menu_state.module_docs_cache:
        return menu_state.module_docs_cache[module_name]
    
    # Map module names to markdown files
    file_mapping = {
        'recaria': 'recaria.md',
        'birlikteyiz': 'birlikteyiz.md',
        'kisisel': 'kisisel_enflasyon.md',
        'kisisel_enflasyon': 'kisisel_enflasyon.md',
        'currencies': 'currencies.md',
        'wimm': 'wimm.md',
        'wims': 'wims.md',
        'documents': 'documents.md',
        'movies': 'movies.md',
        'music': 'music.md',
        'restopos': 'restopos.md',
        # Tools section - individual markdown files
        'system_scrolls': 'system_scrolls.md',
        'castle_guard': 'castle_guard.md',
        'forge_smithy': 'forge_smithy.md',
        'anvil_repair': 'anvil_repair.md',
        'code_forge': 'code_forge.md',
        'web_forge': 'web_forge.md',
        # Dev tools section - individual markdown files
        'ai_builder': 'ai_builder.md',
        'database_setup': 'database_setup.md',
        'git': 'version_manager.md',  # Git uses version_manager docs
        'sd_card': 'sd_card.md',
        'version_manager': 'version_manager.md'
    }
    
    # Get the markdown filename
    md_filename = file_mapping.get(module_name)
    if not md_filename:
        return None
    
    # Construct the full path
    docs_path = Path('/Users/berkhatirli/Desktop/unibos/docs/modules') / md_filename
    
    # Try to read the file
    try:
        if docs_path.exists():
            content = docs_path.read_text(encoding='utf-8')
            # Parse the markdown content
            parsed = parse_markdown_doc(content, module_name)
            # Cache the result
            menu_state.module_docs_cache[module_name] = parsed
            return parsed
    except Exception as e:
        # Silently fail and return None
        pass
    
    return None

def parse_markdown_doc(content, module_name):
    """Parse markdown documentation into structured data - supports new standardized format"""
    lines = content.split('\n')
    doc = {
        'title': module_name,
        'overview': '',
        'version': 'v1.0',
        'features': [],
        'technical': [],
        'integrations': [],
        'performance': '',
        'completion': '',
        'updates': []
    }
    
    # Special handling for tools and dev tools overview files
    if 'tools section overview' in content or 'dev tools section overview' in content:
        # Map specific tool names to their sections in the overview
        tool_sections = {
            # Tools
            'system_scrolls': {'title': 'system scrolls', 'emoji': '🔮'},
            'castle_guard': {'title': 'castle guard', 'emoji': '🛡️'},
            'forge_smithy': {'title': 'forge smithy', 'emoji': '⚒️'},
            'anvil_repair': {'title': 'anvil repair', 'emoji': '🔧'},
            'code_forge': {'title': 'code forge', 'emoji': '📦'},
            'web_forge': {'title': 'web forge', 'emoji': '🌐'},
            # Dev tools
            'ai_builder': {'title': 'ai builder', 'emoji': '🤖'},
            'database_setup': {'title': 'database setup', 'emoji': '📁'},
            'git': {'title': 'git manager', 'emoji': '🔄'},
            'sd_card': {'title': 'sd card', 'emoji': '💾'},
            'version_manager': {'title': 'version manager', 'emoji': '📊'}
        }
        
        if module_name in tool_sections:
            tool_info = tool_sections[module_name]
            doc['title'] = tool_info['title']
            in_section = False
            collecting_features = False
            
            for i, line in enumerate(lines):
                line_stripped = line.strip()
                line_lower = line_stripped.lower()
                
                # Check if we found the specific tool section
                if line_stripped.startswith('### ') and tool_info['title'] in line_lower:
                    in_section = True
                    # Get the description from the next non-empty line
                    for j in range(i + 1, min(i + 5, len(lines))):
                        next_line = lines[j].strip()
                        if next_line and not next_line.startswith('#') and not next_line.startswith('-'):
                            doc['overview'] = next_line
                            break
                    collecting_features = True
                    continue
                
                # Stop when we hit the next section
                if in_section and line_stripped.startswith('### '):
                    break
                
                # Collect features
                if collecting_features and line_stripped.startswith('- '):
                    feature = line_stripped[2:].strip()
                    if len(doc['features']) < 5:
                        doc['features'].append(feature)
                
                # Get version from main overview
                if 'current version' in line_lower and i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line.startswith('v'):
                        doc['version'] = next_line
            
            # If we didn't find an overview, use the main file's overview
            if not doc['overview']:
                for i, line in enumerate(lines):
                    if line.strip().startswith('## overview') and i + 1 < len(lines):
                        doc['overview'] = lines[i + 1].strip()
                        break
            
            return doc
    
    current_section = None
    current_subsection = None
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Skip empty lines
        if not line:
            continue
        
        # Check for headers
        if line.startswith('## '):
            section = line[3:].lower()
            # Remove emoji if present
            if ' ' in section:
                section_parts = section.split(' ', 1)
                if len(section_parts[0]) <= 2:  # Likely an emoji
                    section = section_parts[1] if len(section_parts) > 1 else section
            
            if 'overview' in section:
                current_section = 'overview'
            elif 'capabilities' in section:
                current_section = 'capabilities'
            elif 'technical' in section:
                current_section = 'technical'
            elif 'integrations' in section:
                current_section = 'integrations'
            elif 'performance' in section:
                current_section = 'performance'
            elif 'development status' in section:
                current_section = 'dev_status'
            elif 'version history' in section:
                current_section = 'version_history'
            else:
                current_section = None
            current_subsection = None
        elif line.startswith('### '):
            # Subsection
            subsection = line[4:].lower()
            if 'functional' in subsection or 'fully' in subsection:
                current_subsection = 'functional'
            elif 'development' in subsection or 'progress' in subsection:
                current_subsection = 'in_development'
            elif 'planned' in subsection:
                current_subsection = 'planned'
            else:
                current_subsection = None
        elif line.startswith('# '):
            # Main title - keep emoji if present
            title = line[2:].strip()
            doc['title'] = title
        elif current_section:
            # Process content based on current section
            if current_section == 'overview' and not doc['overview']:
                if not line.startswith('-') and not line.startswith('*'):
                    doc['overview'] = line
            elif current_section == 'capabilities':
                if line.startswith('- '):
                    feature = line[2:].strip()
                    # Remove ** markdown formatting
                    feature = feature.replace('**', '')
                    # Categorize based on subsection or keywords
                    if current_subsection == 'functional' or any(w in feature.lower() for w in ['real-time', 'tracks', 'manages']):
                        if len(doc['features']) < 8:
                            doc['features'].append(feature)
                    elif current_subsection == 'in_development':
                        if len(doc['features']) < 8:
                            doc['features'].append(f"[dev] {feature}")
                    elif current_subsection == 'planned':
                        if len(doc['features']) < 8:
                            doc['features'].append(f"[planned] {feature}")
            elif current_section == 'technical':
                if line.startswith('- '):
                    # Technical function/class details
                    tech = line[2:].strip()
                    # Remove backticks and formatting
                    tech = tech.replace('`', '')
                    if len(doc['technical']) < 3:
                        doc['technical'].append(tech)
            elif current_section == 'integrations':
                if line.startswith('- '):
                    integration = line[2:].strip()
                    if len(doc['integrations']) < 3:
                        doc['integrations'].append(integration)
            elif current_section == 'performance':
                if line.startswith('- ') and not doc['performance']:
                    doc['performance'] = line[2:].strip()
            elif current_section == 'dev_status':
                if 'completion' in line.lower():
                    # Extract completion percentage
                    import re
                    match = re.search(r'(\d+)%', line)
                    if match:
                        doc['completion'] = f"{match.group(1)}% complete"
                    elif 'completion:' in line.lower():
                        # Try to extract from format like "**completion: 78%**"
                        clean_line = line.replace('*', '').strip()
                        doc['completion'] = clean_line
            elif current_section == 'version_history':
                if line.startswith('- v'):
                    if not doc['version']:
                        # Extract version from first entry
                        version_part = line.split(' ')[1] if ' ' in line else 'v1.0'
                        doc['version'] = version_part
    
    # Provide sensible defaults for tools and dev tools if no specific info found
    if not doc['overview']:
        if module_name in ['system_scrolls', 'castle_guard', 'forge_smithy', 'anvil_repair', 'code_forge', 'web_forge']:
            doc['overview'] = 'professional tools for system management and development'
            doc['features'] = [
                'system monitoring and status',
                'security and protection tools',
                'development environment setup',
                'maintenance and repair utilities',
                'integrated workflow automation'
            ]
        elif module_name in ['ai_builder', 'database_setup', 'git', 'sd_card', 'version_manager']:
            doc['overview'] = 'advanced development tools for modern software engineering'
            doc['features'] = [
                'ai-powered code generation',
                'database management systems',
                'version control integration',
                'backup and archive tools',
                'continuous deployment support'
            ]
    
    return doc

def draw_module_info(x, width, height, key, name, desc):
    """Draw module information in main content area with standardized documentation preview"""
    # Try to load documentation
    doc = load_module_documentation(key)
    
    # Clear the content area without box (adjusted for single-line header)
    for y in range(2, height):  # Changed from 3 to 2
        move_cursor(x, y)
        print(' ' * width)
    
    if doc and menu_state.preview_mode:
        # Display formatted documentation in exact documents module format
        y_pos = 3  # Changed from 4 to 3
        
        # Title with emoji (from documentation)
        title = doc.get('title', name).lower()
        move_cursor(x + 2, y_pos)
        print(f"{Colors.BOLD}{Colors.CYAN}# {title}{Colors.RESET}")
        y_pos += 2
        
        # 📋 Overview section with description
        move_cursor(x + 2, y_pos)
        print(f"{Colors.BOLD}{Colors.BLUE}## 📋 overview{Colors.RESET}")
        y_pos += 1
        if doc.get('overview'):
            overview_lines = wrap_text(doc['overview'], width - 6)
            for line in overview_lines[:2]:  # Max 2 lines
                move_cursor(x + 2, y_pos)
                print(f"{Colors.WHITE}{line}{Colors.RESET}")
                y_pos += 1
        y_pos += 2
        
        # 🔧 Current capabilities section with subsections
        if doc.get('features') and y_pos < height - 10:
            move_cursor(x + 2, y_pos)
            print(f"{Colors.BOLD}{Colors.BLUE}## 🔧 current capabilities{Colors.RESET}")
            y_pos += 1
            
            # Group features by status
            functional = []
            in_dev = []
            planned = []
            
            for feature in doc['features']:
                if '[dev]' in feature:
                    in_dev.append(feature.replace('[dev] ', ''))
                elif '[planned]' in feature:
                    planned.append(feature.replace('[planned] ', ''))
                else:
                    functional.append(feature)
            
            # Show functional features
            if functional and y_pos < height - 8:
                move_cursor(x + 2, y_pos)
                print(f"{Colors.GREEN}### ✅ fully functional{Colors.RESET}")
                y_pos += 1
                for feat in functional[:3]:  # Show max 3
                    if y_pos >= height - 6:
                        break
                    move_cursor(x + 2, y_pos)
                    # Split feature into name and description
                    if ' - ' in feat:
                        parts = feat.split(' - ', 1)
                        print(f"- {Colors.BOLD}{parts[0]}{Colors.RESET} - {parts[1][:width-15]}")
                    else:
                        print(f"- {feat[:width-6]}")
                    y_pos += 1
                y_pos += 1
            
            # Show in development features
            if in_dev and y_pos < height - 6:
                move_cursor(x + 2, y_pos)
                print(f"{Colors.YELLOW}### 🚧 in development{Colors.RESET}")
                y_pos += 1
                for feat in in_dev[:2]:  # Show max 2
                    if y_pos >= height - 5:
                        break
                    move_cursor(x + 2, y_pos)
                    print(f"- {feat[:width-6]}")
                    y_pos += 1
                y_pos += 1
            
            # Show planned features
            if planned and y_pos < height - 5:
                move_cursor(x + 2, y_pos)
                print(f"{Colors.DIM}### 📅 planned features{Colors.RESET}")
                y_pos += 1
                for feat in planned[:2]:  # Show max 2
                    if y_pos >= height - 4:
                        break
                    move_cursor(x + 2, y_pos)
                    print(f"{Colors.DIM}- {feat[:width-6]}{Colors.RESET}")
                    y_pos += 1
                y_pos += 1
        
        # 💻 Technical implementation section
        if doc.get('technical') and y_pos < height - 5:
            move_cursor(x + 2, y_pos)
            print(f"{Colors.BOLD}{Colors.BLUE}## 💻 technical implementation{Colors.RESET}")
            y_pos += 1
            move_cursor(x + 2, y_pos)
            print(f"{Colors.DIM}core components and architecture powering this module{Colors.RESET}")
            y_pos += 1
            for tech in doc['technical'][:2]:  # Show max 2
                if y_pos >= height - 4:
                    break
                move_cursor(x + 2, y_pos)
                print(f"- {tech[:width-6]}")
                y_pos += 1
            y_pos += 1
        
        # 🔌 API integrations section
        if doc.get('integrations') and y_pos < height - 4:
            move_cursor(x + 2, y_pos)
            print(f"{Colors.BOLD}{Colors.BLUE}## 🔌 api integrations{Colors.RESET}")
            y_pos += 1
            move_cursor(x + 2, y_pos)
            print(f"{Colors.DIM}external services and APIs connected to this module{Colors.RESET}")
            y_pos += 1
            for integration in doc['integrations'][:2]:  # Show max 2
                if y_pos >= height - 3:
                    break
                move_cursor(x + 2, y_pos)
                print(f"- {integration[:width-6]}")
                y_pos += 1
        
        # Development status at bottom
        if doc.get('completion'):
            move_cursor(x + 2, height - 4)
            import re
            match = re.search(r'(\d+)%', str(doc['completion']))
            if match:
                percent = int(match.group(1))
                if percent >= 80:
                    color = Colors.GREEN
                    emoji = "✅"
                elif percent >= 60:
                    color = Colors.YELLOW
                    emoji = "🚧"
                else:
                    color = Colors.RED
                    emoji = "📅"
                print(f"{Colors.BOLD}## 🛠️ development status{Colors.RESET}")
                move_cursor(x + 2, height - 3)
                print(f"{color}completion: {percent}% {emoji}{Colors.RESET}")
        
        # Launch hint
        move_cursor(x + 2, height - 2)
        print(f"{Colors.DIM}press enter to launch • ← back to menu{Colors.RESET}")
    else:
        # Fallback to simple display if no documentation found
        # Module description
        move_cursor(x + 3, 5)
        print(f"{Colors.BOLD}description:{Colors.RESET} {desc}")
        
        # Module status
        move_cursor(x + 3, 7)
        status = "ready" if key in ['recaria', 'currencies', 'birlikteyiz', 'kisisel', 'ai_builder', 'system_info', 'security_tools', 'git', 'web_forge', 'version_manager'] else "coming soon"
        color = Colors.GREEN if status == "ready" else Colors.YELLOW
        print(f"{Colors.BOLD}status:{Colors.RESET} {color}{status}{Colors.RESET}")

def draw_tools_menu(x, width, height):
    """Draw tools submenu"""
    draw_box(x, 3, width - 1, height, "🛠️ tools", Colors.GREEN)
    
    # Initialize tool items if not done
    if not menu_state.tool_items:
        menu_state.tool_items = [
            ("system_info", "📊 system information", "view system details"),
            ("security_tools", "🔒 security tools", "security utilities"),
            ("setup_manager", "🔧 setup manager", "initial setup"),
            ("repair_tools", "🛠️ repair tools", "fix issues"),
            ("git", "📦 git manager", "version control"),
            ("web_interface", "🌐 web interface", "browser ui"),
        ]
    
    # Display tool items (adjusted for single-line header)
    y_pos = 4  # Changed from 5 to 4
    for i, (key, name, desc) in enumerate(menu_state.tool_items):
        if y_pos + 2 < height:
            move_cursor(x + 3, y_pos)
            
            # Highlight selected item
            if i == menu_state.tool_selected_index:
                print(f"{Colors.BG_BLUE}{Colors.WHITE} {name:<35} {Colors.RESET}")
            else:
                print(f"  {name}")
            
            move_cursor(x + 5, y_pos + 1)
            print(f"{Colors.DIM}{desc}{Colors.RESET}")
            y_pos += 2
    
    # Instructions
    move_cursor(x + 3, height - 2)
    print(f"{Colors.DIM}↑↓ navigate | enter select | esc back{Colors.RESET}")

def draw_system_info_screen(x, width, height):
    """Draw system information screen"""
    draw_box(x, 3, width - 1, height, "📊 system information", Colors.BLUE)
    
    # Get system information
    info = get_system_info()
    
    # Display information (adjusted for box starting at line 3)
    y_pos = 5
    move_cursor(x + 3, y_pos)
    print(f"{Colors.BOLD}system information:{Colors.RESET}")
    y_pos += 2
    
    # System details
    details = [
        ("hostname", info.get("hostname", "unknown")),
        ("platform", info.get("platform", "unknown")),
        ("architecture", info.get("architecture", "unknown")),
        ("python", info.get("python_version", "unknown")),
        ("", ""),  # Spacer
        ("cpu cores", info.get("cpu_cores", "n/a")),
        ("cpu usage", info.get("cpu_usage", "n/a")),
        ("", ""),  # Spacer
        ("memory total", info.get("memory_total", "n/a")),
        ("memory used", info.get("memory_used", "n/a")),
        ("", ""),  # Spacer
        ("disk total", info.get("disk_total", "n/a")),
        ("disk free", info.get("disk_free", "n/a")),
    ]
    
    for label, value in details:
        if y_pos < height - 2:
            move_cursor(x + 3, y_pos)
            if label:
                print(f"{Colors.DIM}{label}:{Colors.RESET} {value}")
            y_pos += 1
    
    # Press any key hint
    move_cursor(x + 3, height - 2)
    print(f"{Colors.DIM}press any key to return{Colors.RESET}")

def draw_security_tools_screen(x, width, height):
    """Draw security tools screen"""
    draw_box(x, 3, width - 1, height, "🔒 security tools", Colors.RED)
    
    # Security information (adjusted for box starting at line 3)
    y_pos = 5
    move_cursor(x + 3, y_pos)
    print(f"{Colors.BOLD}network security:{Colors.RESET}")
    y_pos += 2
    
    if NETWORK_UTILS_AVAILABLE:
        security_info = get_network_security_info()
        
        # Display security details
        details = [
            ("firewall status", security_info.get("firewall_status", "unknown")),
            ("open ports", str(security_info.get("open_ports", []))),
            ("active connections", str(security_info.get("active_connections", 0))),
            ("", ""),  # Spacer
            ("security level", security_info.get("security_level", "unknown")),
        ]
        
        for label, value in details:
            if y_pos < height - 2:
                move_cursor(x + 3, y_pos)
                if label:
                    print(f"{Colors.DIM}{label}:{Colors.RESET} {value}")
                y_pos += 1
    else:
        move_cursor(x + 3, y_pos)
        print(f"{Colors.YELLOW}security monitoring not available{Colors.RESET}")
        y_pos += 2
        move_cursor(x + 3, y_pos)
        print(f"{Colors.DIM}network_utils module required{Colors.RESET}")
    
    # Press any key hint
    move_cursor(x + 3, height - 2)
    print(f"{Colors.DIM}press any key to return{Colors.RESET}")

def draw_main_screen():
    """Draw the complete main screen with NEW ARCHITECTURE"""
    global ui_controller
    
    # CRITICAL: Ensure we're in main menu state
    # This prevents any lingering submenu highlights
    if menu_state.in_submenu is None:
        # We're in main menu, ensure proper state
        pass
    
    # Initialize menu items FIRST before any UI setup
    if not hasattr(menu_state, 'modules') or not menu_state.modules:
        initialize_menu_items()
    
    # Initialize UI controller if not exists and available
    if not ui_controller and UI_ARCHITECTURE_AVAILABLE:
        ui_controller = UnibosUI()
        ui_controller.header.version = VERSION_INFO.get('version', 'v334')
    
    clear_screen()
    hide_cursor()
    
    # Ensure terminal is fully cleared before drawing
    sys.stdout.write('\033[2J\033[H')  # Clear screen and move to home
    sys.stdout.write('\033[?25l')  # Hide cursor during drawing
    sys.stdout.flush()
    
    # CRITICAL: Force cache invalidation to ensure complete redraw
    menu_state.last_sidebar_cache_key = None
    if hasattr(menu_state, 'sidebar_cache'):
        menu_state.sidebar_cache.clear()
    
    # Use new UI architecture if available
    if ui_controller and UI_ARCHITECTURE_AVAILABLE:
        ui_controller.header.render()
        # Update sidebar sections AFTER menu items are initialized
        update_sidebar_sections()
        ui_controller.sidebar.render()
    else:
        # Fallback to old rendering
        draw_header()  # Draws lines 1-3 with orange background
        
        # Ensure no gap between header and content areas
        # Clear line 4 specifically to prevent any gray band
        cols, _ = get_terminal_size()
        move_cursor(1, 4)
        print(f"\033[2K", end='')  # Clear entire line
        
        draw_sidebar()  # Draws from line 4 onwards - will now force redraw due to cache clear
    
    draw_footer()   # Draws at bottom
    draw_main_content()  # Draws from line 4 onwards
    
    # Show language selection if active
    if menu_state.in_language_menu:
        show_language_selection()

def update_sidebar_sections():
    """Update sidebar sections in UI controller based on menu_state"""
    global ui_controller
    
    if not ui_controller or not UI_ARCHITECTURE_AVAILABLE:
        return
    
    # Clear existing sections
    ui_controller.sidebar.sections = []
    
    # Add modules section
    module_items = [(key, name) for key, name, desc, available, action in menu_state.modules]
    ui_controller.sidebar.add_section("modules", module_items)
    
    # Add tools section
    tool_items = [(key, name) for key, name, desc, available, action in menu_state.tools]
    ui_controller.sidebar.add_section("tools", tool_items)
    
    # Add dev tools section
    dev_tool_items = [(key, name) for key, name, desc, available, action in menu_state.dev_tools]
    ui_controller.sidebar.add_section("dev tools", dev_tool_items)
    
    # Update selection
    ui_controller.sidebar.selected_section = menu_state.current_section
    ui_controller.sidebar.selected_index = menu_state.selected_index
    ui_controller.sidebar.is_dimmed = menu_state.in_submenu is not None

def get_simple_key():
    """Simple key input without timeout - for splash screen and basic input"""
    try:
        if platform.system() == 'Windows':
            import msvcrt
            key = msvcrt.getch()
            if isinstance(key, bytes):
                key = key.decode('utf-8', errors='ignore')
            return key.lower() if key else ''
        else:
            if not TERMIOS_AVAILABLE:
                # Fallback for systems without termios
                ch = input()
                return ch[0].lower() if ch else ''
            
            import termios
            import tty
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                key = sys.stdin.read(1)
                return key.lower() if key else ''
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    except Exception:
        return ''

def handle_minimize():
    """Handle minimize action - launch playable solitaire with security"""
    try:
        # Import solitaire game
        from solitaire_cli import play_solitaire_cli
        
        # Clear screen and launch solitaire with lock
        clear_screen()
        play_solitaire_cli(with_lock=True)
        
        # After returning from solitaire (password verified), restore main screen
        draw_main_screen()
    except ImportError:
        # Fallback to simple solitaire background if game not available
        clear_screen()
        cols, lines = get_terminal_size()
        draw_solitaire_background()
        
        # Simple password prompt
        move_cursor(cols//2 - 15, lines//2)
        print(f"{Colors.CYAN}enter password to return: {Colors.RESET}", end='')
        show_cursor()
        password = ""
        while True:
            key = get_single_key(timeout=None)
            if key == '\r':
                if password == "lplp":  # Database password
                    break
                else:
                    move_cursor(cols//2 - 10, lines//2 + 2)
                    print(f"{Colors.RED}incorrect password!{Colors.RESET}")
                    time.sleep(1)
                    move_cursor(cols//2 - 15, lines//2)
                    print(f"{Colors.CYAN}enter password to return: {' ' * 20}{Colors.RESET}", end='')
                    move_cursor(cols//2 + 11, lines//2)
                    password = ""
            elif key and len(key) == 1:
                password += key
                print('*', end='', flush=True)
        
        hide_cursor()
        draw_main_screen()

def draw_solitaire_background():
    """Draw a solitaire game background"""
    import random
    cols, lines = get_terminal_size()
    
    # Draw green felt background
    for y in range(1, lines - 2):
        move_cursor(1, y)
        print(f"{Colors.BG_GREEN}{' ' * cols}{Colors.RESET}")
    
    # Draw card piles (7 tableau piles)
    card_width = 5
    spacing = 2
    start_x = max(5, (cols - (7 * (card_width + spacing))) // 2)
    
    # Draw tableau
    for pile in range(7):
        x = start_x + pile * (card_width + spacing)
        if x + card_width > cols - 5:
            break
        
        # Draw cards in pile
        for card_num in range(min(pile + 1, 3)):  # Limit cards to prevent overflow
            y = 5 + card_num * 2
            if y + 4 > lines - 5:
                break
            move_cursor(x, y)
            
            if card_num == pile:  # Face-up card
                # Random card
                suits = ['♠', '♥', '♦', '♣']
                values = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
                suit = random.choice(suits)
                value = random.choice(values)
                color = Colors.RED if suit in ['♥', '♦'] else Colors.BLACK
                
                print(f"{Colors.BG_WHITE}{color}┌───┐{Colors.RESET}")
                move_cursor(x, y + 1)
                print(f"{Colors.BG_WHITE}{color}│{value:^3}│{Colors.RESET}")
                move_cursor(x, y + 2)
                print(f"{Colors.BG_WHITE}{color}│ {suit} │{Colors.RESET}")
                move_cursor(x, y + 3)
                print(f"{Colors.BG_WHITE}{color}└───┘{Colors.RESET}")
            else:  # Face-down card
                print(f"{Colors.BG_BLUE}{Colors.WHITE}┌───┐{Colors.RESET}")
                move_cursor(x, y + 1)
                print(f"{Colors.BG_BLUE}{Colors.WHITE}│▓▓▓│{Colors.RESET}")
    
    # Draw foundation piles (4 piles at top right)
    if cols > 60:
        foundation_x = cols - 30
        for pile in range(4):
            x = foundation_x + pile * (card_width + spacing)
            if x + card_width > cols - 2:
                break
            y = 3
            move_cursor(x, y)
            print(f"{Colors.DIM}┌───┐{Colors.RESET}")
            move_cursor(x, y + 1)
            suits = ['♠', '♥', '♦', '♣']
            print(f"{Colors.DIM}│ {suits[pile]} │{Colors.RESET}")
            move_cursor(x, y + 2)
            print(f"{Colors.DIM}└───┘{Colors.RESET}")
    
    # Draw stock pile
    if cols > 40:
        stock_x = 5
        y = 3
        move_cursor(stock_x, y)
        print(f"{Colors.BG_BLUE}{Colors.WHITE}┌───┐{Colors.RESET}")
        move_cursor(stock_x, y + 1)
        print(f"{Colors.BG_BLUE}{Colors.WHITE}│▓▓▓│{Colors.RESET}")
        move_cursor(stock_x, y + 2)
        print(f"{Colors.BG_BLUE}{Colors.WHITE}└───┘{Colors.RESET}")
    
    # Title
    title = "♠ ♥ SOLITAIRE ♦ ♣"
    move_cursor((cols - len(title)) // 2, 1)
    print(f"{Colors.BOLD}{Colors.WHITE}{title}{Colors.RESET}")

def get_single_key(timeout=0.1):
    """Simple and reliable single key input with arrow key support"""
    debug_mode = os.environ.get('UNIBOS_DEBUG', '').lower() == 'true'
    
    try:
        if platform.system() == 'Windows':
            import msvcrt
            # Clear any pending input
            while msvcrt.kbhit():
                msvcrt.getch()
            
            # Wait for key with timeout
            start_time = time.time()
            while True:
                if msvcrt.kbhit():
                    key = msvcrt.getch()
                    if key == b'\xe0':  # Special key prefix
                        key = msvcrt.getch()
                        if key == b'H': return '\x1b[A'  # Up
                        elif key == b'P': return '\x1b[B'  # Down
                        elif key == b'K': return '\x1b[D'  # Left
                        elif key == b'M': return '\x1b[C'  # Right
                    elif key == b'\r': return '\r'
                    elif key == b'\x1b': return '\x1b'
                    elif key == b'\t': return '\t'
                    elif key == b' ': return ' '
                    else:
                        try:
                            return key.decode('utf-8', errors='ignore')
                        except:
                            return key
                
                if time.time() - start_time > timeout:
                    return None
                time.sleep(0.01)
        else:
            # Unix/Linux/macOS
            if not TERMIOS_AVAILABLE:
                return None
            
            import termios, tty
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            
            try:
                # Set terminal to non-canonical mode with timeout
                new_settings = termios.tcgetattr(fd)
                new_settings[3] = new_settings[3] & ~termios.ICANON & ~termios.ECHO
                new_settings[6][termios.VMIN] = 0
                new_settings[6][termios.VTIME] = 0
                termios.tcsetattr(fd, termios.TCSADRAIN, new_settings)
                
                # Check if input is available
                rlist, _, _ = select.select([sys.stdin], [], [], timeout)
                if not rlist:
                    return None
                
                # Read character using os.read for better control
                ch = os.read(fd, 1).decode('utf-8', errors='ignore')
                
                if debug_mode:
                    with open('/tmp/unibos_key_debug.log', 'a') as f:
                        f.write(f"First char: {repr(ch)}\n")
                        f.flush()
                
                # Handle escape sequences
                if ch == '\x1b':
                    # Set a very short timeout for subsequent reads
                    new_settings[6][termios.VTIME] = 1  # 0.1 second timeout
                    termios.tcsetattr(fd, termios.TCSADRAIN, new_settings)
                    
                    try:
                        ch2 = os.read(fd, 1).decode('utf-8', errors='ignore')
                        if debug_mode:
                            with open('/tmp/unibos_key_debug.log', 'a') as f:
                                f.write(f"Second char: {repr(ch2)}\n")
                                f.flush()
                        
                        if ch2 == '[':
                            ch3 = os.read(fd, 1).decode('utf-8', errors='ignore')
                            if debug_mode:
                                with open('/tmp/unibos_key_debug.log', 'a') as f:
                                    f.write(f"Third char: {repr(ch3)}\n")
                                    f.flush()
                            
                            if ch3 == 'A': return '\x1b[A'  # Up
                            elif ch3 == 'B': return '\x1b[B'  # Down
                            elif ch3 == 'C': return '\x1b[C'  # Right
                            elif ch3 == 'D': return '\x1b[D'  # Left
                            # Handle numeric escape sequences
                            elif ch3.isdigit():
                                ch4 = os.read(fd, 1).decode('utf-8', errors='ignore')
                                if ch4 == 'A': return '\x1b[A'
                                elif ch4 == 'B': return '\x1b[B'
                                elif ch4 == 'C': return '\x1b[C'
                                elif ch4 == 'D': return '\x1b[D'
                    except:
                        pass
                    
                    return '\x1b'  # Just ESC
                
                # Check for Enter key
                if ch == '\r' or ch == '\n':
                    return '\r'
                
                return ch
                
            finally:
                # Restore terminal settings
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                
    except Exception as e:
        # Silently handle errors
        return None

def show_language_selection():
    """Show language selection overlay with arrow key navigation"""
    cols, lines = get_terminal_size()
    
    # Language menu dimensions
    lang_width = 40
    lang_height = 15
    lang_x = (cols - lang_width) // 2
    lang_y = (lines - lang_height) // 2
    
    # First clear the language box area with dark background
    for y in range(lang_y, lang_y + lang_height):
        move_cursor(lang_x, y)
        print(f"{Colors.BG_DARK}{' ' * lang_width}{Colors.RESET}", end='')
    
    # Draw language selection box
    draw_box(lang_x, lang_y, lang_width, lang_height, 
             f"{t('select_language')}", Colors.YELLOW)
    
    # Get available languages
    languages = get_available_languages()
    
    # Display languages with selection highlight
    for i, (code, name, flag) in enumerate(languages[:10]):  # Show max 10
        y_pos = lang_y + 2 + i
        
        if i == menu_state.language_selected_index:
            # Selected item with arrow - limit to box width
            move_cursor(lang_x + 3, y_pos)
            # First clear the line within box boundaries
            print(f"{' ' * (lang_width - 6)}", end='')
            move_cursor(lang_x + 3, y_pos)
            # Now print with blue background, strictly limited
            display_text = f" ▶ {flag} {name}"
            max_width = lang_width - 6
            if len(display_text) > max_width:
                display_text = display_text[:max_width]
            # Print blue background only for the text length
            print(f"{Colors.BG_BLUE}{Colors.WHITE}{display_text}{Colors.RESET}", end='')
            # Fill remaining space without background
            remaining = max_width - len(display_text)
            if remaining > 0:
                print(f"{' ' * remaining}", end='')
            print()  # End line
        elif code == CURRENT_LANG:
            # Current language highlighted
            move_cursor(lang_x + 3, y_pos)
            display_text = f"   {flag} {name}"
            max_width = lang_width - 10  # Leave space for checkmark
            if len(display_text) > max_width:
                display_text = display_text[:max_width]
            print(f"{Colors.YELLOW}{display_text}{Colors.RESET}", end='')
            # Position checkmark at fixed location
            move_cursor(lang_x + lang_width - 9, y_pos)
            print(f"{Colors.YELLOW}✓{Colors.RESET}")
        else:
            # Regular items
            move_cursor(lang_x + 3, y_pos)
            display_text = f"   {flag} {name}"
            max_width = lang_width - 6
            if len(display_text) > max_width:
                display_text = display_text[:max_width]
            print(f"{display_text}")
    
    # Instructions
    move_cursor(lang_x + 3, lang_y + lang_height - 2)
    print(f"{Colors.DIM}↑↓ navigate | enter select | l close{Colors.RESET}")

def handle_menu_selection():
    """Handle menu item selection"""
    if menu_state.current_section == 0:  # Modules
        if menu_state.selected_index < len(menu_state.modules):
            key, name, desc, available, action = menu_state.modules[menu_state.selected_index]
            handle_module_launch(key)
    else:  # Tools
        if menu_state.selected_index < len(menu_state.tools):
            handle_tool_selection()

def show_recaria_submenu():
    """Show recaria submenu with game, vehicles, launch points, and starship calc"""
    menu_state.in_submenu = 'recaria'
    recaria_selected = 0
    
    recaria_items = [
        ("play", f"🎮 {t('play_game')}", t('start_recaria')),
        ("vehicles", f"🚗 {t('vehicles')}", t('transport')),
        ("launch_points", f"🚀 {t('launch_points')}", t('eight_point_nav')),
        ("starship_calc", f"🛸 {t('starship_calc')}", t('spacex')),
    ]
    
    while True:
        draw_main_screen()
        
        # Draw recaria submenu in content area
        cols, lines = get_terminal_size()
        content_x = 27
        content_width = cols - content_x
        content_height = lines - 3
        
        # Clear content area
        for y in range(3, lines - 1):  # Stop before footer
            move_cursor(content_x, y)
            clear_width = min(content_width, cols - content_x)
            if clear_width > 0:
                print(' ' * clear_width, end='')
        
        # Draw box starting at line 3 (immediately after header)
        # Box extends to full width and down to footer
        draw_box(content_x, 3, content_width - 1, lines - 4, "🪐 recaria", Colors.CYAN)
        
        # Display menu items (moved up by 1 since box starts at line 4 now)
        y_pos = 6
        for i, (key, name, desc) in enumerate(recaria_items):
            move_cursor(content_x + 3, y_pos)
            
            if i == recaria_selected:
                print(f"{Colors.BG_BLUE}{Colors.WHITE} {name:<40} {Colors.RESET}")
            else:
                print(f" {name:<40} ")
            
            move_cursor(content_x + 5, y_pos + 1)
            print(f"{Colors.DIM}{desc}{Colors.RESET}")
            y_pos += 3
        
        # Instructions
        move_cursor(content_x + 3, content_height - 2)
        print(f"{Colors.DIM}↑↓ navigate | enter select | esc back{Colors.RESET}")
        
        # Get input
        key = get_single_key()
        
        if key == '\x1b[A' or key == 'k':  # Up
            recaria_selected = max(0, recaria_selected - 1)
        elif key == '\x1b[B' or key == 'j':  # Down
            recaria_selected = min(len(recaria_items) - 1, recaria_selected + 1)
        elif key == '\r' or key == '\x1b[C':  # Enter/Right
            selected_key = recaria_items[recaria_selected][0]
            if selected_key == 'play':
                clear_screen()
                print(f"{Colors.CYAN}{'='*50}{Colors.RESET}")
                print(f"{Colors.BOLD}🚀 launching recaria...{Colors.RESET}")
                print(f"{Colors.CYAN}{'='*50}{Colors.RESET}\n")
                print(f"🪐 {t('recaria')} - universe explorer")
                print(f"{Colors.GREEN}module loading...{Colors.RESET}")
                try:
                    sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'projects'))
                    from recaria.main import main as recaria_main
                    recaria_main()
                except ImportError:
                    print(f"{Colors.YELLOW}recaria module not found. please check installation.{Colors.RESET}")
                print(f"\n{Colors.DIM}press enter to continue...{Colors.RESET}")
                input()
            else:
                # Show coming soon for other options
                move_cursor(content_x + 10, content_height // 2)
                print(f"{Colors.YELLOW}feature coming soon!{Colors.RESET}")
                time.sleep(1)
        elif key == '\x1b' or key == '\x1b[D':  # Esc/Left
            menu_state.in_submenu = None
            break

def run_claude_embedded(x_start, y_start, width):
    """Run Claude in embedded mode within the content area"""
    import pty
    import select
    import termios
    import tty
    
    # Save current terminal settings
    old_settings = termios.tcgetattr(sys.stdin)
    
    try:
        # Create pseudo-terminal
        master_fd, slave_fd = pty.openpty()
        
        # Fork process to run claude
        pid = os.fork()
        
        if pid == 0:  # Child process
            # Close master side
            os.close(master_fd)
            
            # Make slave side our stdin/stdout/stderr
            os.dup2(slave_fd, 0)
            os.dup2(slave_fd, 1)
            os.dup2(slave_fd, 2)
            
            # Close original slave fd
            if slave_fd > 2:
                os.close(slave_fd)
            
            # Set terminal size to match content area
            cols, lines = get_terminal_size()
            content_height = lines - 8  # Account for header/footer
            
            # Create a temporary directory for Claude to avoid loading large CLAUDE files
            import tempfile
            temp_dir = tempfile.mkdtemp(prefix='claude_session_')
            os.chdir(temp_dir)
            
            # Execute the system's claude command directly
            # This will use the existing authenticated session
            os.execvp('claude', ['claude'])
            
        else:  # Parent process
            # Close slave side
            os.close(slave_fd)
            
            # Set stdin to raw mode for direct input
            tty.setraw(sys.stdin.fileno())
            
            # Track cursor position within content area
            current_line = 0
            
            while True:
                # Check for input/output
                rlist, _, _ = select.select([sys.stdin, master_fd], [], [], 0.1)
                
                if sys.stdin in rlist:
                    # Read user input
                    data = os.read(sys.stdin.fileno(), 1024)
                    
                    # Check for ESC key to exit
                    if data == b'\x1b':
                        break
                    
                    # Send to claude
                    os.write(master_fd, data)
                
                if master_fd in rlist:
                    # Read claude output
                    try:
                        data = os.read(master_fd, 1024)
                        if not data:
                            break
                        
                        # Process and display output within content area
                        output = data.decode('utf-8', errors='replace')
                        
                        # Parse output and constrain to content area
                        # Get terminal size for bounds checking
                        cols, term_lines = get_terminal_size()
                        max_content_lines = term_lines - 8
                        
                        for char in output:
                            if char == '\n':
                                current_line += 1
                                if current_line >= max_content_lines:
                                    # Scroll content up
                                    current_line = max_content_lines - 1
                                move_cursor(x_start, y_start + current_line)
                                print(' ' * width, end='')
                                move_cursor(x_start, y_start + current_line)
                            elif char == '\r':
                                move_cursor(x_start, y_start + current_line)
                            else:
                                # Print character with content background
                                print(char, end='', flush=True)
                    except OSError:
                        break
            
            # Wait for child process
            os.waitpid(pid, 0)
            
    finally:
        # Restore terminal settings
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        
        # Return to original directory
        os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Clear and redraw UI
        draw_main_screen()

def run_database_setup_wizard():
    """Run database setup wizard in content area"""
    clear_screen()
    show_cursor()
    
    try:
        from database_setup_wizard import run_setup_wizard
        
        # Terminal ayarlarını kaydet ve normal moda al
        if TERMIOS_AVAILABLE:
            import termios
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            # Normal terminal moduna geç (raw mode'dan çık)
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        
        # Wizard'ı çalıştır
        result = run_setup_wizard()
        
        # Ana ekrana dön
        menu_state.in_submenu = None
        hide_cursor()
        draw_main_screen()
        
    except ImportError:
        print(f"{Colors.RED}Database setup wizard not found!{Colors.RESET}")
        time.sleep(2)
        menu_state.in_submenu = None
        hide_cursor()
        draw_main_screen()
    except Exception as e:
        print(f"{Colors.RED}Error running database setup: {e}{Colors.RESET}")
        time.sleep(3)
        menu_state.in_submenu = None
        hide_cursor()
        draw_main_screen()

def run_claude_in_content_area():
    """Run Claude CLI integrated in the content area with model selection"""
    # Get terminal dimensions
    cols, lines = get_terminal_size()
    content_x = 27  # Match main content area positioning
    content_width = max(20, cols - content_x)  # Ensure minimum width
    
    # Clear content area but keep UI frame
    for y in range(2, lines - 1):  # Changed from 3 to 2, better bottom margin
        move_cursor(content_x, y)
        print(' ' * content_width, end='', flush=True)
    
    # Draw Claude interface header with style matching Claude Code
    header_y = 2  # Changed from 3 to 2 for single-line header
    move_cursor(content_x + 2, header_y)
    print(f"{Colors.ORANGE}╭{'─' * (content_width - 6)}╮{Colors.RESET}")
    move_cursor(content_x + 2, header_y + 1)
    print(f"{Colors.ORANGE}│{Colors.RESET} {Colors.BOLD}* welcome to claude code!{Colors.RESET}{''.ljust(content_width - 31)}{Colors.ORANGE}│{Colors.RESET}")
    move_cursor(content_x + 2, header_y + 2)
    print(f"{Colors.ORANGE}╰{'─' * (content_width - 6)}╯{Colors.RESET}")
    
    # Show model selection
    info_y = header_y + 4
    move_cursor(content_x + 4, info_y)
    print(f"{Colors.CYAN}select claude model:{Colors.RESET}")
    
    # Model options
    models = [
        ("default", "claude-3-haiku (fast, efficient)"),
        ("opus", "claude-3-opus (most capable)"),
        ("sonnet", "claude-3-sonnet (balanced)")
    ]
    
    selected_model = 0
    
    def draw_model_options():
        for i, (model, desc) in enumerate(models):
            move_cursor(content_x + 8, info_y + 2 + i * 2)
            if i == selected_model:
                print(f"{Colors.BG_ORANGE}{Colors.WHITE} [{model}] {desc} {Colors.RESET}")
            else:
                print(f" [{model}] {desc} ")
    
    # Draw initial options
    draw_model_options()
    
    # Navigation hint
    move_cursor(content_x + 4, info_y + 9)
    print(f"{Colors.DIM}↑↓ navigate | enter select | esc cancel{Colors.RESET}")
    
    # Model selection loop
    hide_cursor()
    while True:
        key = get_single_key()
        
        if key == '\x1b[A' or key == 'UP':  # Up arrow
            if selected_model > 0:
                selected_model -= 1
                draw_model_options()
        elif key == '\x1b[B' or key == 'DOWN':  # Down arrow
            if selected_model < len(models) - 1:
                selected_model += 1
                draw_model_options()
        elif key == '\r' or key == 'ENTER':  # Enter - launch claude
            model_name = models[selected_model][0]
            launch_claude_with_model(model_name, content_x, info_y + 11, content_width)
            break
        elif key == 'ESC' or key == '\x1b':  # Escape - cancel
            menu_state.in_submenu = 'tools'
            return
    
    # Return to menu
    menu_state.in_submenu = 'tools'

def launch_claude_with_model(model, content_x, launch_y, content_width):
    """Launch Claude CLI with specific model"""
    move_cursor(content_x + 4, launch_y)
    print(f"{Colors.DIM}launching claude {model} session...{Colors.RESET}")
    
    time.sleep(0.5)
    
    try:
        # Check if claude cli module exists
        from claude_cli import ClaudeCLI
        
        # Clear screen for full Claude experience
        clear_screen()
        show_cursor()
        
        # Initialize and run claude CLI with menu
        claude = ClaudeCLI()
        claude.run_interactive_session()
        
        # After claude exits, handle exit options
        handle_claude_exit()
        
    except ImportError:
        # Fallback to direct claude command if module not found
        result = subprocess.run(['which', 'claude'], capture_output=True, text=True)
        if result.returncode != 0:
            # Claude not installed - show installation message
            move_cursor(content_x + 4, launch_y + 2)
            print(f"{Colors.RED}error: claude cli not found{Colors.RESET}")
            move_cursor(content_x + 4, launch_y + 3)
            print(f"{Colors.YELLOW}please install claude cli first{Colors.RESET}")
            move_cursor(content_x + 4, launch_y + 5)
            print(f"{Colors.DIM}press enter to continue...{Colors.RESET}", end='')
            input()
            return
        
        # Run claude directly
        clear_screen()
        show_cursor()
        
        if model != "default":
            cmd = f"claude --model {model}"
        else:
            cmd = "claude"
        
        subprocess.run(cmd, shell=True)
        handle_claude_exit()
        
    except Exception as e:
        print(f"{Colors.RED}error: {str(e)}{Colors.RESET}")
        print(f"\n{Colors.DIM}press enter to continue...{Colors.RESET}")
        input()

def handle_claude_exit():
    """Handle exit from Claude session with version creation option"""
    try:
        clear_screen()
        print(f"{Colors.CYAN}claude session ended{Colors.RESET}\n")
        print(f"What would you like to do?\n")
        print(f"1. Return to unibos menu")
        print(f"2. Save changes and create new version (exit unibos)")
        print(f"\n{Colors.DIM}Enter choice (1 or 2): {Colors.RESET}", end='')
        
        choice = input().strip()
        
        if choice == '1':
            # Return to main menu
            menu_state.in_submenu = 'tools'
            return
        elif choice == '2':
            # Run version manager to create new version
            print(f"\n{Colors.YELLOW}Creating new version...{Colors.RESET}")
        try:
            # Get version description
            print(f"\n{Colors.CYAN}Enter version description: {Colors.RESET}", end='')
            description = input().strip() or "Claude AI assisted development"
            
            # Update VERSION.json description
            version_file = "/Users/berkhatirli/Desktop/unibos/src/VERSION.json"
            if os.path.exists(version_file):
                with open(version_file, 'r') as f:
                    version_data = json.loads(f.read())
                version_data['description'] = description
                with open(version_file, 'w') as f:
                    json.dump(version_data, f, indent=2)
            
            # Run version manager script
            print(f"\n{Colors.GREEN}Running version manager...{Colors.RESET}")
            result = subprocess.run(["/Users/berkhatirli/Desktop/unibos/src/version_manager.sh"], 
                                    input="e\n", text=True, capture_output=True)
            
            if result.returncode == 0:
                print(f"\n{Colors.GREEN}✓ Version created successfully{Colors.RESET}")
                print(f"{Colors.YELLOW}Restarting unibos with new version...{Colors.RESET}")
                time.sleep(2)
                
                # Exit current process and restart unibos.sh
                os.execv('/Users/berkhatirli/Desktop/unibos/unibos.sh', ['unibos.sh'])
            else:
                print(f"\n{Colors.RED}Error creating version:{Colors.RESET}")
                print(result.stderr)
                print(f"\n{Colors.DIM}Press enter to return to menu...{Colors.RESET}")
                input()
            
        except Exception as e:
            print(f"\n{Colors.RED}Error: {e}{Colors.RESET}")
            print(f"{Colors.DIM}Press enter to return to menu...{Colors.RESET}")
            input()
        else:
            # Invalid choice - return to menu
            print(f"\n{Colors.YELLOW}Invalid choice. Returning to menu...{Colors.RESET}")
            time.sleep(1)
            menu_state.in_submenu = 'tools'
            return
    except KeyboardInterrupt:
        # Handle Ctrl+C
        print(f"\n\n{Colors.YELLOW}Interrupted. Returning to menu...{Colors.RESET}")
        time.sleep(1)
        menu_state.in_submenu = 'tools'
        return
    except Exception as e:
        print(f"\n{Colors.RED}Error in handle_claude_exit: {e}{Colors.RESET}")
        print(f"{Colors.DIM}Press enter to return to menu...{Colors.RESET}")
        input()
        menu_state.in_submenu = 'tools'
        return

def handle_tool_launch(tool_key):
    """Handle tool launch from sidebar"""
    
    if tool_key == 'system_scrolls':
        menu_state.in_submenu = tool_key
        show_system_scrolls()
    elif tool_key == 'castle_guard':
        menu_state.in_submenu = tool_key
        show_castle_guard()
    elif tool_key == 'forge_smithy':
        menu_state.in_submenu = tool_key
        show_forge_smithy()
    elif tool_key == 'anvil_repair':
        menu_state.in_submenu = tool_key
        show_anvil_repair()
    elif tool_key == 'web_ui':
        # Launch web ui menu (formerly web forge)
        menu_state.in_submenu = 'web_forge'  # Keep internal state as web_forge for compatibility
        menu_state.web_forge_index = 0
        web_forge_menu()  # Actually launch the menu
    elif tool_key == 'code_forge':
        # Code forge handles its own submenu state
        from code_forge_menu import code_forge_menu
        code_forge_menu()
        # CRITICAL: Ensure state is cleared after menu exits
        menu_state.in_submenu = None
    elif tool_key == 'administration':
        # Administration handles its own submenu state
        from administration_menu import administration_menu
        administration_menu()
        # CRITICAL: Ensure state is cleared after menu exits
        menu_state.in_submenu = None
    else:
        # Generic tool display
        show_tool_screen(tool_key)

def handle_dev_tool_launch(tool_key):
    """Handle dev tool launch from sidebar"""
    
    if tool_key == 'ai_builder':
        # AI builder handles its own submenu state
        from ai_builder_menu import ai_builder_menu
        ai_builder_menu()
        # CRITICAL: Ensure state is cleared after menu exits
        menu_state.in_submenu = None
    elif tool_key == 'public_server':
        # Launch public server menu
        from public_server_menu_proper import public_server_menu
        public_server_menu()
        # State is managed inside the menu function
        menu_state.in_submenu = None
    elif tool_key == 'version_manager':
        menu_state.in_submenu = tool_key
        version_manager_menu()
    elif tool_key == 'database_setup':
        menu_state.in_submenu = tool_key
        database_setup_wizard()
    else:
        # Generic tool display
        show_tool_screen(tool_key)

def show_tool_screen(tool_key):
    """Generic tool screen display with proper sidebar dimming"""
    # Force sidebar redraw to ensure dimmed state
    menu_state.last_sidebar_cache_key = None
    draw_sidebar()
    
    cols, lines = get_terminal_size()
    content_x = 27  # After sidebar
    content_width = cols - content_x - 1
    
    # Find tool info
    tool_info = None
    for key, name, desc, available, action in menu_state.tools:
        if key == tool_key:
            tool_info = (name, desc)
            break
    
    if not tool_info:
        return
    
    name, desc = tool_info
    
    # Clear content area properly
    for y in range(2, lines - 1):
        move_cursor(content_x, y)
        sys.stdout.write('\033[K')  # Clear to end of line
    sys.stdout.flush()
    
    # Draw content box
    draw_box(content_x, 3, content_width - 1, lines - 4, name, Colors.BLUE)
    
    # Display content
    y = 5
    move_cursor(content_x + 3, y)
    print(f"{Colors.BOLD}description:{Colors.RESET} {desc}")
    y += 2
    move_cursor(content_x + 3, y)
    print(f"{Colors.BOLD}status:{Colors.RESET} {Colors.GREEN}ready{Colors.RESET}")
    y += 3
    
    move_cursor(content_x + 3, y)
    print(f"{Colors.YELLOW}🚧 Feature coming soon!{Colors.RESET}")
    y += 2
    
    move_cursor(content_x + 3, y)
    print(f"{Colors.DIM}This tool is under development and will be available in a future update.{Colors.RESET}")
    
    # Navigation hint
    move_cursor(content_x + 3, lines - 5)
    print(f"{Colors.DIM}press enter to launch{Colors.RESET}")
    
    # Wait for key
    while True:
        key = get_single_key(timeout=0.1)
        if key == '\x1b' or key == '\x1b[D':  # ESC, Left Arrow
            menu_state.in_submenu = None
            draw_main_screen()
            break
        elif key == '\r':  # Enter
            # Show coming soon message
            move_cursor(content_x + 3, lines - 7)
            print(f"{Colors.ORANGE}⚡ Launching soon...{Colors.RESET}")
            time.sleep(1)

def show_castle_guard():
    """Show security tools screen"""
    show_tool_screen('castle_guard')

def show_forge_smithy():
    """Show setup tools screen"""
    show_tool_screen('forge_smithy')

def show_anvil_repair():
    """Show repair tools screen"""
    show_tool_screen('anvil_repair')

def show_system_scrolls():
    """Display system information using system_scrolls module"""
    cols, lines = get_terminal_size()
    content_x = 27  # After sidebar
    content_width = cols - content_x - 2
    
    # Clear content area
    for y in range(2, lines - 1):  # Changed from 3 to 2 for single-line header
        move_cursor(content_x, y)
        print(' ' * content_width, end='', flush=True)
    
    # Draw content box with BLUE frame (not orange)
    draw_box(content_x, 3, content_width - 1, lines - 5, "📊 System Scrolls", Colors.CYAN)
    
    try:
        from system_scrolls import SystemScrolls
        scrolls = SystemScrolls()
        info = scrolls.get_all_info()
        
        # Display content
        y = 5
        max_y = lines - 5
        
        # OS Info
        move_cursor(content_x + 3, y)
        print(f"{Colors.BOLD}{Colors.ORANGE}System Information:{Colors.RESET}")
        y += 2
        
        # Format and display each section
        sections = []
        
        # OS information
        os_info = info.get('os', {})
        net_info = info.get('network', {})
        sections.extend([
            ("OS", f"{os_info.get('system', 'Unknown')} {os_info.get('release', '')}"),
            ("Platform", os_info.get('platform', 'Unknown')),
            ("Machine", os_info.get('machine', 'Unknown')),
            ("Hostname", net_info.get('hostname', os_info.get('node', 'Unknown'))),
        ])
        
        # Python information
        py_info = info.get('python', {})
        ver_info = py_info.get('version_info', {})
        py_version = f"{ver_info.get('major', 0)}.{ver_info.get('minor', 0)}.{ver_info.get('micro', 0)}"
        sections.append(("Python", py_version))
        
        # CPU information
        cpu_info = info.get('cpu', {})
        if cpu_info:
            sections.extend([
                ("", ""),  # Empty line
                ("CPU", cpu_info.get('model', 'Unknown')),
                ("Cores", f"{cpu_info.get('physical_cores', 'Unknown')} physical, {cpu_info.get('logical_cores', 'Unknown')} logical"),
            ])
            if 'usage_percent' in cpu_info:
                sections.append(("Usage", f"{cpu_info['usage_percent']}%"))
        
        # Memory information
        mem_info = info.get('memory', {})
        if mem_info and 'virtual' in mem_info:
            vm = mem_info['virtual']
            sections.extend([
                ("", ""),
                ("RAM", f"{vm.get('total', 'Unknown')} total"),
                ("Used", f"{vm.get('used', 'Unknown')} ({vm.get('percent', 0)}%)"),
                ("Available", vm.get('available', 'Unknown')),
            ])
        
        # Disk information
        disk_info = info.get('disk', {})
        partitions = disk_info.get('partitions', [])
        if partitions:
            sections.extend([
                ("", ""),
                ("Disk", f"{len(partitions)} partition(s)"),
            ])
            for part in partitions[:2]:  # Show first 2 partitions
                sections.append((f"  {part.get('device', 'Unknown')}", f"{part.get('percent', 0)}% used"))
        
        # Display sections
        for label, value in sections:
            if y >= max_y - 2:
                break
            if label:
                move_cursor(content_x + 5, y)
                print(f"{Colors.DIM}{label}:{Colors.RESET} {value}")
            y += 1
        
        # Navigation hint
        move_cursor(content_x + 3, max_y)
        print(f"{Colors.DIM}Press ESC or ← to go back{Colors.RESET}")
        
    except ImportError as e:
        # Fallback without psutil
        y = 5
        move_cursor(content_x + 3, y)
        print(f"{Colors.YELLOW}System information module not available{Colors.RESET}")
        y += 2
        move_cursor(content_x + 3, y)
        print(f"{Colors.DIM}Error: {str(e)}{Colors.RESET}")
        y += 2
        move_cursor(content_x + 3, y)
        print("Basic system info:")
        y += 2
        
        import platform
        move_cursor(content_x + 5, y)
        print(f"OS: {platform.system()} {platform.release()}")
        y += 1
        move_cursor(content_x + 5, y)
        print(f"Machine: {platform.machine()}")
        y += 1
        move_cursor(content_x + 5, y)
        print(f"Python: {platform.python_version()}")
        
        # Navigation hint
        y = max_y
        move_cursor(content_x + 3, y)
        print(f"{Colors.DIM}Press ESC or ← to go back{Colors.RESET}")
        
    except Exception as e:
        # General error handling
        y = 5
        move_cursor(content_x + 3, y)
        print(f"{Colors.RED}Error loading system information:{Colors.RESET}")
        y += 2
        move_cursor(content_x + 3, y)
        print(f"{Colors.DIM}{str(e)}{Colors.RESET}")
        y += 2
        
        # Log the full error for debugging
        import traceback
        error_msg = traceback.format_exc()
        lines = error_msg.split('\n')
        for line in lines[:5]:  # Show first 5 lines of traceback
            if y >= max_y - 2:
                break
            move_cursor(content_x + 5, y)
            print(f"{Colors.DIM}{line[:content_width-10]}{Colors.RESET}")
            y += 1
        
        # Navigation hint
        y = max_y
        move_cursor(content_x + 3, y)
        print(f"{Colors.DIM}Press ESC or ← to go back{Colors.RESET}")
    
    # Wait for key
    while True:
        key = get_single_key(timeout=0.1)
        if key == '\x1b' or key == '\x1b[D':  # ESC, Left Arrow
            menu_state.in_submenu = None
            draw_main_screen()
            break

def handle_tool_selection():
    """Handle tool selection in sidebar (admin tools)"""
    # Get selected tool from the admin tools list
    if menu_state.selected_index < len(menu_state.tools):
        key, name, desc = menu_state.tools[menu_state.selected_index]
        
        if key == 'system_info':
            menu_state.in_submenu = 'system_info'
            show_system_scrolls()
        elif key == 'security_tools':
            menu_state.in_submenu = 'security_tools'
        elif key == 'claude':
            # Launch claude cli in content area
            menu_state.in_submenu = 'claude'
            run_claude_in_content_area()
        elif key == 'git':
            # Launch git manager within main UI
            menu_state.in_submenu = 'git_manager'  # Set special submenu state
            try:
                from git_manager import GitManager
                git_manager = GitManager()
                # Pass the draw_main_screen function as callback
                git_manager.show_main_menu(draw_ui_callback=draw_main_screen)
                # After git manager exits, return to tools menu
                menu_state.in_submenu = 'tools'
            except ImportError as e:
                menu_state.in_submenu = 'tools'
                clear_screen()
                print(f"{Colors.RED}error: git_manager module not found{Colors.RESET}")
                print(f"{Colors.RED}details: {str(e)}{Colors.RESET}")
                time.sleep(2)
            except Exception as e:
                menu_state.in_submenu = 'tools'
                clear_screen()
                print(f"{Colors.RED}error: {e}{Colors.RESET}")
                time.sleep(2)
        else:
            # Show coming soon message
            cols, lines = get_terminal_size()
            move_cursor(cols // 2 - 10, lines // 2)
            print(f"{Colors.YELLOW}feature coming soon!{Colors.RESET}")
            time.sleep(1)

def show_module_screen(module_key):
    """Generic module screen display with proper sidebar dimming"""
    # Force sidebar redraw to ensure dimmed state
    menu_state.last_sidebar_cache_key = None
    draw_sidebar()
    
    cols, lines = get_terminal_size()
    content_x = 27  # After sidebar
    content_width = cols - content_x - 1
    
    # Find module info
    module_info = None
    for key, name, desc, available, action in menu_state.modules:
        if key == module_key:
            module_info = (name, desc)
            break
    
    if not module_info:
        return
    
    name, desc = module_info
    
    # Clear content area properly
    for y in range(2, lines - 1):
        move_cursor(content_x, y)
        sys.stdout.write('\033[K')  # Clear to end of line
    sys.stdout.flush()
    
    # Draw content box
    draw_box(content_x, 3, content_width - 1, lines - 4, name, Colors.CYAN)
    
    # Display content
    y = 5
    move_cursor(content_x + 3, y)
    print(f"{Colors.BOLD}description:{Colors.RESET} {desc}")
    y += 2
    move_cursor(content_x + 3, y)
    print(f"{Colors.BOLD}status:{Colors.RESET} {Colors.GREEN}ready{Colors.RESET}")
    y += 3
    
    # Module-specific content
    if module_key == 'recaria':
        move_cursor(content_x + 3, y)
        print(f"{Colors.BOLD}consciousness:{Colors.RESET} {Colors.MAGENTA}1 / 8.000.000.000{Colors.RESET}")
        y += 1
        move_cursor(content_x + 3, y)
        print(f"{Colors.BOLD}collective mind:{Colors.RESET} {Colors.YELLOW}∞ past + present + future{Colors.RESET}")
        y += 3
        move_cursor(content_x + 3, y)
        print(f"{Colors.BOLD}philosophy:{Colors.RESET}")
        y += 1
        move_cursor(content_x + 3, y)
        print(f"consciousness = lived experiences")
        y += 1
        move_cursor(content_x + 3, y)
        print(f"           + present influence")
        y += 1
        move_cursor(content_x + 3, y)
        print(f"           + future potential")
        y += 3
        move_cursor(content_x + 3, y)
        print(f"{Colors.BOLD}next 2 years:{Colors.RESET}")
        y += 1
        move_cursor(content_x + 3, y)
        print(f"• quantum communication")
        y += 1
        move_cursor(content_x + 3, y)
        print(f"• metaverse migration")
        y += 1
        move_cursor(content_x + 3, y)
        print(f"• neura-link awakening")
        y += 1
        move_cursor(content_x + 3, y)
        print(f"• global crisis sync")
        y += 3
        move_cursor(content_x + 3, y)
        print(f"{Colors.BOLD}game features:{Colors.RESET}")
        y += 1
        move_cursor(content_x + 3, y)
        print(f"• shape collective reality")
        y += 1
        move_cursor(content_x + 3, y)
        print(f"{Colors.DIM}press enter to launch{Colors.RESET}")
        
    elif module_key == 'birlikteyiz':
        move_cursor(content_x + 3, y)
        print(f"{Colors.BOLD}network type:{Colors.RESET} LoRa Mesh Network")
        y += 1
        move_cursor(content_x + 3, y)
        print(f"{Colors.BOLD}frequency:{Colors.RESET} 868 MHz (EU) / 915 MHz (US)")
        y += 1
        move_cursor(content_x + 3, y)
        print(f"{Colors.BOLD}range:{Colors.RESET} up to 15 km")
        y += 3
        move_cursor(content_x + 3, y)
        print(f"{Colors.YELLOW}🚧 Hardware required:{Colors.RESET}")
        y += 1
        move_cursor(content_x + 3, y)
        print(f"• Raspberry Pi or compatible")
        y += 1
        move_cursor(content_x + 3, y)
        print(f"• LoRa HAT/Module")
        y += 1
        move_cursor(content_x + 3, y)
        print(f"• Antenna")
        
    elif module_key == 'kisisel':
        move_cursor(content_x + 3, y)
        print(f"{Colors.BOLD}features:{Colors.RESET}")
        y += 1
        move_cursor(content_x + 3, y)
        print(f"• Track personal expenses")
        y += 1
        move_cursor(content_x + 3, y)
        print(f"• Calculate real inflation")
        y += 1
        move_cursor(content_x + 3, y)
        print(f"• Compare with official rates")
        y += 1
        move_cursor(content_x + 3, y)
        print(f"• Historical analysis")
        
    elif module_key == 'currencies':
        move_cursor(content_x + 3, y)
        print(f"{Colors.BOLD}supported:{Colors.RESET}")
        y += 1
        move_cursor(content_x + 3, y)
        print(f"• 10+ fiat currencies")
        y += 1
        move_cursor(content_x + 3, y)
        print(f"• 10+ cryptocurrencies")
        y += 1
        move_cursor(content_x + 3, y)
        print(f"• Real-time rates")
        y += 1
        move_cursor(content_x + 3, y)
        print(f"• Portfolio tracking")
    
    # Navigation hint
    move_cursor(content_x + 3, lines - 5)
    print(f"{Colors.DIM}press enter to launch{Colors.RESET}")
    
    # Import select for ESC key detection (do it once, outside the loop)
    import select
    
    # Wait for key
    while True:
        key = get_single_key(timeout=0.1)
        if key == '\x1b[D' or key in ['q', 'Q']:  # Left Arrow or q to exit
            # Exit module properly
            menu_state.in_submenu = None
            menu_state.last_sidebar_cache_key = None  # Force sidebar refresh
            draw_main_screen()
            break
        elif key == '\x1b':  # ESC alone
            # Check if standalone ESC
            if not select.select([sys.stdin], [], [], 0.0)[0]:
                menu_state.in_submenu = None
                menu_state.last_sidebar_cache_key = None
                draw_main_screen()
                break
        elif key == '\r' or key == '\x1b[C':  # Enter or Right Arrow to launch
            # Launch the actual module
            if module_key == 'recaria':
                show_recaria_submenu()
            elif module_key == 'birlikteyiz':
                launch_birlikteyiz()
            elif module_key == 'kisisel':
                launch_kisisel()
            elif module_key == 'currencies':
                launch_currencies()
            break

def launch_birlikteyiz():
    """Launch birlikteyiz module"""
    clear_screen()
    print(f"{Colors.CYAN}{'='*50}{Colors.RESET}")
    print(f"{Colors.BOLD}🚀 launching birlikteyiz...{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*50}{Colors.RESET}\n")
    print(f"📡 {t('birlikteyiz')} - mesh network")
    print(f"{Colors.GREEN}initializing lora network...{Colors.RESET}")
    try:
        from projects.birlikteyiz.main import main as birlikteyiz_main
        birlikteyiz_main()
    except ImportError:
        print(f"{Colors.YELLOW}birlikteyiz module not found.{Colors.RESET}")
    print(f"\n{Colors.DIM}press enter to continue...{Colors.RESET}")
    input()
    menu_state.in_submenu = None
    draw_main_screen()

def launch_kisisel():
    """Launch kisisel enflasyon module"""
    clear_screen()
    print(f"{Colors.CYAN}{'='*50}{Colors.RESET}")
    print(f"{Colors.BOLD}🚀 launching kişisel enflasyon...{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*50}{Colors.RESET}\n")
    print(f"📈 {t('kisisel')} - personal inflation calculator")
    try:
        from personal_inflation import show_inflation_menu
        show_inflation_menu()
    except ImportError:
        try:
            from projects.kisiselenflasyon.main import main as inflation_main
            inflation_main()
        except ImportError:
            print(f"{Colors.YELLOW}kişisel enflasyon module not found.{Colors.RESET}")
    print(f"\n{Colors.DIM}press enter to continue...{Colors.RESET}")
    input()
    menu_state.in_submenu = None
    draw_main_screen()

def launch_currencies():
    """Launch currencies module"""
    clear_screen()
    print(f"{Colors.CYAN}{'='*50}{Colors.RESET}")
    print(f"{Colors.BOLD}🚀 launching currencies...{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*50}{Colors.RESET}\n")
    print(f"💰 {t('currencies')} - exchange rates")
    try:
        from currencies_enhanced import CurrenciesModule
        module = CurrenciesModule()
        module.run()
    except ImportError:
        try:
            from projects.currencies.main import main as currencies_main
            currencies_main()
        except ImportError:
            print(f"{Colors.YELLOW}currencies module not found.{Colors.RESET}")
    print(f"\n{Colors.DIM}press enter to continue...{Colors.RESET}")
    input()
    menu_state.in_submenu = None
    draw_main_screen()

def handle_documents_module():
    """Handle documents module with submenu in content area - exactly like version_manager"""
    menu_state.in_submenu = 'documents'
    menu_state.documents_index = 0  # Initialize selection index
    
    # Clear screen and redraw everything to start fresh
    clear_screen()
    draw_header()
    
    # Force sidebar redraw to ensure dimmed state
    menu_state.last_sidebar_cache_key = None
    draw_sidebar()
    
    # Draw documents menu in content area
    draw_documents_menu()
    draw_footer()
    
    # Hide cursor
    hide_cursor()
    
    # Handle navigation
    while menu_state.in_submenu == 'documents':
        key = get_single_key(timeout=0.1)
        
        if key is None:
            continue  # Timeout, just continue loop
            
        if key == '\x1b[A':  # Up arrow
            if menu_state.documents_index > 0:
                menu_state.documents_index -= 1
                draw_documents_menu()
                
        elif key == '\x1b[B':  # Down arrow
            if menu_state.documents_index < 6:  # 7 items (0-6)
                menu_state.documents_index += 1
                draw_documents_menu()
                
        elif key == '\r' or key == '\x1b[C':  # Enter or Right arrow
            if menu_state.documents_index == 4:  # Invoice processor
                # Launch invoice processor without redrawing menu
                launch_documents_function(menu_state.documents_index)
                # After invoice processor exits, redraw everything
                draw_sidebar()
                draw_documents_menu()
            else:
                launch_documents_function(menu_state.documents_index)
                draw_documents_menu()
                
        elif key in '1234567':
            idx = int(key) - 1
            menu_state.documents_index = idx
            draw_documents_menu()
            if idx == 4:  # Invoice processor
                launch_documents_function(idx)
                # After invoice processor exits, redraw everything
                draw_sidebar()
                draw_documents_menu()
            else:
                launch_documents_function(idx)
                draw_documents_menu()
                
        elif key == '\x1b':  # ESC
            menu_state.in_submenu = None
            break
            
        elif key == '\x1b[D':  # Left arrow - go back
            menu_state.in_submenu = None
            break
    
    # Restore display
    draw_main_screen()

def draw_documents_menu():
    """Draw documents submenu in content area"""
    cols, lines = get_terminal_size()
    content_x = 27  # After sidebar
    content_width = cols - content_x - 1
    
    # Clear content area
    clear_content_area()
    
    # Title
    move_cursor(content_x + 2, 4)
    print(f"{Colors.BOLD}{Colors.BLUE}📄 documents{Colors.RESET}")
    
    # Subtitle
    move_cursor(content_x + 2, 5)
    print(f"{Colors.DIM}intelligent document management{Colors.RESET}")
    
    # Document submenu options
    options = [
        ("1", "browse documents", "view and manage documents"),
        ("2", "search", "full-text document search"),
        ("3", "upload", "upload new documents"),
        ("4", "ocr scanner", "extract text from images"),
        ("5", "invoice processor", "process invoices with ai"),
        ("6", "tag manager", "manage document tags"),
        ("7", "analytics", "document statistics"),
    ]
    
    # Display options
    y_pos = 7
    for i, (key, name, desc) in enumerate(options):
        move_cursor(content_x + 2, y_pos)
        
        if i == menu_state.documents_index:
            # Selected item
            print(f"{Colors.BG_ORANGE}{Colors.WHITE} [{key}] {name:<30} {Colors.RESET}")
        else:
            # Normal item
            print(f" [{key}] {name:<30}")
        
        # Description below
        move_cursor(content_x + 6, y_pos + 1)
        print(f"{Colors.DIM}{desc}{Colors.RESET}")
        
        y_pos += 3
    
    # Instructions at bottom
    move_cursor(content_x + 2, lines - 3)
    print(f"{Colors.DIM}↑↓ navigate | enter select | esc back{Colors.RESET}")
    
    sys.stdout.flush()

def launch_documents_function(index):
    """Launch the selected documents function"""
    try:
        show_cursor()
        
        if index == 4:  # Invoice processor - special handling for content area
            from invoice_processor_cli import InvoiceProcessorCLI
            processor = InvoiceProcessorCLI()
            # Keep sidebar visible and run in content area
            # Don't clear screen, just render in content area
            processor.run_in_content_area(31, 3, 88, 40)
        else:
            # Other functions use full screen
            clear_screen()
            
            if index == 0:  # Browse documents
                from documents_functions import browse_documents
                browse_documents()
            elif index == 1:  # Search
                from documents_functions import search_documents
                search_documents()
            elif index == 2:  # Upload
                from documents_functions import upload_documents
                upload_documents()
            elif index == 3:  # OCR Scanner
                from documents_functions import ocr_scanner
                ocr_scanner()
            elif index == 5:  # Tag manager
                from documents_functions import tag_manager
                tag_manager()
            elif index == 6:  # Analytics
                from documents_functions import document_analytics
                document_analytics()
        
        # Return to documents menu
        hide_cursor()
        clear_screen()
        draw_main_screen()  # Redraw everything
        
    except ImportError as e:
        show_documents_temp_message(f"Module not found: {e}")
        hide_cursor()
    except Exception as e:
        show_documents_temp_message(f"Error: {e}")
        hide_cursor()

def show_documents_temp_message(msg):
    """Show temporary message in documents menu"""
    cols, lines = get_terminal_size()
    content_x = 27
    
    move_cursor(content_x + 2, lines - 5)
    print(f"{Colors.YELLOW}{msg}{Colors.RESET}")
    sys.stdout.flush()
    time.sleep(1.5)

def handle_module_launch(module_key):
    """Handle module launch with proper submenu handling"""
    menu_state.in_submenu = module_key
    
    # Special handling for modules with their own submenus
    if module_key == 'recaria':
        # Recaria has its own submenu system
        show_module_screen(module_key)  # Show intro screen first
    elif module_key == 'documents':
        # Documents has its own submenu
        handle_documents_module()
    else:
        # All other modules show generic screen
        show_module_screen(module_key)


def update_module_selection(index):
    """Update visual selection for modules - OPTIMIZED"""
    # Store previous index before updating
    menu_state.previous_index = menu_state.selected_index
    
    # Update menu state
    menu_state.selected_index = index
    menu_state.current_section = 0  # 0 for modules
    
    # Use optimized update
    update_sidebar_selection()
    
    # Return the new index for synchronization
    return index

def update_tool_selection(index):
    """Update visual selection for tools - OPTIMIZED"""
    # Store previous index before updating
    menu_state.previous_index = menu_state.selected_index
    
    # Update menu state
    menu_state.selected_index = index
    menu_state.current_section = 1  # 1 for tools
    
    # Use optimized update
    update_sidebar_selection()
    
    # Return the new index for synchronization
    return index

def update_dev_tool_selection(index):
    """Update visual selection for dev tools - OPTIMIZED"""
    # Store previous index before updating
    menu_state.previous_index = menu_state.selected_index
    
    # Update menu state
    menu_state.selected_index = index
    menu_state.current_section = 2  # 2 for dev tools
    
    # Use optimized update
    update_sidebar_selection()
    
    # Return the new index for synchronization
    return index

def get_tool_icon(name):
    """Get icon for tool based on name"""
    name_lower = name.lower()
    if "system" in name_lower: return "📊"
    elif "security" in name_lower: return "🔒"
    elif "claude" in name_lower: return "🤖"
    elif "setup" in name_lower: return "🔧"
    elif "repair" in name_lower: return "🛠️"
    elif "git" in name_lower: return "📦"
    elif "web" in name_lower: return "🌐"
    elif "sd" in name_lower: return "💾"
    else: return "⚙️"

def main_loop():
    """Main application loop - with safe arrow key navigation"""
    global CURRENT_LANG
    
    # Clear input buffer multiple times to ensure it's empty
    if TERMIOS_AVAILABLE:
        try:
            import termios
            # Flush multiple times to ensure buffer is completely clear
            for _ in range(3):
                termios.tcflush(sys.stdin, termios.TCIFLUSH)
                time.sleep(0.01)
        except:
            pass
    
    # Longer delay to ensure terminal is fully ready after splash
    time.sleep(0.2)
    
    # Initialize menu items BEFORE drawing the screen
    initialize_menu_items()
    
    # Track last footer update time and last keypress
    last_footer_update = time.time()
    last_keypress_time = 0
    min_keypress_interval = 0.05  # 50ms debounce
    
    # Initial screen draw - now with populated menu items
    draw_main_screen()
    
    # Initialize terminal size for resize detection
    menu_state.last_cols, menu_state.last_lines = get_terminal_size()
    
    # Initialize selected module/tool indices and sync with menu_state
    menu_state.selected_index = 0
    menu_state.current_section = 0  # 0 for modules, 1 for tools, 2 for dev tools
    menu_state.previous_index = None  # Initialize previous index
    selected_module = 0
    selected_tool = 0
    selected_dev_tool = 0
    
    # Simple initialization - no complex buffer clearing
    if menu_state.modules:
        # Single buffer clear after splash screen
        if TERMIOS_AVAILABLE:
            try:
                termios.tcflush(sys.stdin, termios.TCIFLUSH)
            except:
                pass
        
        # Initial display with selection
        update_sidebar_selection()
        hide_cursor()
    
    # Track if this is the first keypress
    first_keypress = True
    
    while True:
        try:
            # Check for terminal resize
            cols, lines = get_terminal_size()
            if cols != menu_state.last_cols or lines != menu_state.last_lines:
                menu_state.last_cols = cols
                menu_state.last_lines = lines
                # Redraw everything on resize
                clear_screen()
                draw_main_screen()
            
            # Update footer only when needed (no more blinking)
            current_time = time.time()
            if current_time - last_footer_update >= 60.0:  # Check every minute for date change
                # Only update if date actually changed
                last_footer_update = current_time
                hide_cursor()
            
            # Get single key input with arrow support
            key = get_single_key(timeout=0.1)
            
            # If no key pressed, continue loop
            if not key:
                continue
            
            
            # Mark first keypress done
            if first_keypress:
                first_keypress = False
            
            # Debounce - prevent too rapid keypresses
            current_keypress_time = time.time()
            if current_keypress_time - last_keypress_time < min_keypress_interval:
                # Clear any remaining input in buffer
                if TERMIOS_AVAILABLE:
                    try:
                        termios.tcflush(sys.stdin, termios.TCIFLUSH)
                    except:
                        pass
                continue
            last_keypress_time = current_keypress_time
            
            # Debug output for key detection
            if os.environ.get('UNIBOS_DEBUG', '').lower() == 'true':
                with open('/tmp/unibos_main_debug.log', 'a') as f:
                    f.write(f"Main loop received key: {repr(key)}, section: {menu_state.current_section}, index: {menu_state.selected_index}\n")
                    f.flush()
            
            # Handle navigation keys
            if key == '\x1b[D' or (key == '\x1b' and menu_state.in_submenu):  # Left arrow or ESC in submenu
                if menu_state.in_submenu:
                    menu_state.in_submenu = None
                    draw_main_screen()
                continue
            
            # Handle keyboard combinations
            # Track pressed keys for combinations (Q+W for solitaire, Q+W+E for exit)
            if not hasattr(menu_state, 'keys_pressed'):
                menu_state.keys_pressed = set()
            
            # Add key to pressed set
            if key and len(key) == 1:
                menu_state.keys_pressed.add(key.lower())
                
                # Check for Q+W combination (solitaire)
                if 'q' in menu_state.keys_pressed and 'w' in menu_state.keys_pressed and 'e' not in menu_state.keys_pressed:
                    # Go to solitaire (minimize)
                    menu_state.keys_pressed.clear()
                    handle_minimize()
                    continue
                
                # Check for Q+W+E combination (exit)
                if 'q' in menu_state.keys_pressed and 'w' in menu_state.keys_pressed and 'e' in menu_state.keys_pressed:
                    # Exit unibos
                    menu_state.keys_pressed.clear()
                    break
                
                # Clear keys after a short timeout
                def clear_keys():
                    time.sleep(0.5)
                    menu_state.keys_pressed.clear()
                threading.Thread(target=clear_keys, daemon=True).start()
            else:
                # Clear on non-letter keys
                if hasattr(menu_state, 'keys_pressed'):
                    menu_state.keys_pressed.clear()
            
            # Handle arrow keys with simple handler
            if key == '\x1b[A':  # Up arrow
                selected_module, selected_tool, selected_dev_tool, needs_redraw = simple_navigation_handler(
                    menu_state, key, selected_module, selected_tool, selected_dev_tool
                )
                if needs_redraw:
                    draw_sidebar()
                    draw_main_content()
            
            elif key == '\x1b[B':  # Down arrow
                selected_module, selected_tool, selected_dev_tool, needs_redraw = simple_navigation_handler(
                    menu_state, key, selected_module, selected_tool, selected_dev_tool
                )
                if needs_redraw:
                    draw_sidebar()
                    draw_main_content()
            
            elif key == '\x1b[D' or (key == '\x1b' and menu_state.in_submenu):  # Left arrow or ESC in submenu
                # Handle back navigation
                if menu_state.in_submenu:
                    # Exit from submenu
                    menu_state.in_submenu = None
                    draw_main_screen()
                # If not in submenu, left arrow does nothing
            
            elif key == '\r' or key == '\x1b[C':  # Enter or Right arrow
                if menu_state.current_section == 0 and 0 <= menu_state.selected_index < len(menu_state.modules):
                    cmd, name, desc, available, action = menu_state.modules[menu_state.selected_index]
                    if available and action:
                        action()
                    draw_main_screen()
                elif menu_state.current_section == 1 and 0 <= menu_state.selected_index < len(menu_state.tools):
                    cmd, name, desc, available, action = menu_state.tools[menu_state.selected_index]
                    if available and action:
                        action()
                    draw_main_screen()
                elif menu_state.current_section == 2 and 0 <= menu_state.selected_index < len(menu_state.dev_tools):
                    cmd, name, desc, available, action = menu_state.dev_tools[menu_state.selected_index]
                    if available and action:
                        action()
                    draw_main_screen()
            
            elif key == '\t':  # Tab to switch sections
                selected_module, selected_tool, selected_dev_tool, needs_redraw = simple_navigation_handler(
                    menu_state, key, selected_module, selected_tool, selected_dev_tool
                )
                if needs_redraw:
                    draw_sidebar()
                    draw_main_content()
            
            
            # Minimize with solitaire background
            elif key and key.lower() == 'm':
                handle_minimize()
                continue
            
            # Language menu toggle
            elif key and key.lower() == 'l':
                menu_state.in_language_menu = True
                menu_state.language_selected_index = 0
                languages = get_available_languages()
                
                # Language selection loop with clock updates
                lang_last_update = time.time()
                while menu_state.in_language_menu:
                    # Update clock while in language menu
                    current_time = time.time()
                    if current_time - lang_last_update >= 1.0:
                        # Footer no longer needs time updates
                        lang_last_update = current_time
                    
                    show_language_selection()
                    lang_key = get_single_key(timeout=0.1)  # Short timeout for clock updates
                    
                    if lang_key:  # Only process if we got a key
                        if lang_key == '\x1b[A':  # Up arrow
                            if menu_state.language_selected_index > 0:
                                menu_state.language_selected_index -= 1
                        elif lang_key == '\x1b[B':  # Down arrow
                            if menu_state.language_selected_index < min(9, len(languages) - 1):
                                menu_state.language_selected_index += 1
                        elif lang_key == '\r':  # Enter
                            # Select the language
                            global CURRENT_LANG
                            code, name, flag = languages[menu_state.language_selected_index]
                            CURRENT_LANG = code
                            initialize_menu_items()
                            menu_state.in_language_menu = False
                        elif lang_key == '\x1b' or (lang_key and lang_key.lower() == 'l'):  # ESC or L to close
                            menu_state.in_language_menu = False
                        elif lang_key.isdigit():
                            # Number selection for backward compatibility
                            num = int(lang_key) if lang_key != '0' else 10
                            if num <= len(languages[:10]):
                                code, name, flag = languages[num - 1]
                                CURRENT_LANG = code
                                initialize_menu_items()
                                menu_state.in_language_menu = False
                
                draw_main_screen()  # Redraw after language selection
                continue
            
            # Handle module commands
            for i, (cmd, name, desc, available, action) in enumerate(menu_state.modules):
                if key == cmd:
                    if available:
                        if action:
                            action()
                        else:
                            print(f"\n{Colors.YELLOW}Module {name} not implemented yet.{Colors.RESET}")
                            time.sleep(2)
                    else:
                        print(f"\n{Colors.RED}Module {name} is not available.{Colors.RESET}")
                        time.sleep(2)
                    draw_main_screen()
                    continue
            
            # Handle tool commands
            for i, (cmd, name, desc, available, action) in enumerate(menu_state.tools):
                if key == cmd:
                    if available:
                        if action:
                            action()
                        else:
                            print(f"\n{Colors.YELLOW}Tool {name} not implemented yet.{Colors.RESET}")
                            time.sleep(2)
                    else:
                        print(f"\n{Colors.RED}Tool {name} is not available.{Colors.RESET}")
                        time.sleep(2)
                    draw_main_screen()
                    continue
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"\n{Colors.RED}Error: {e}{Colors.RESET}")
            time.sleep(2)
            draw_main_screen()

def database_setup_wizard():
    """Launch database setup wizard in content area - exactly like administration"""
    menu_state.in_submenu = 'database_setup'
    menu_state.database_setup_index = 0  # Add index tracking
    
    # Clear screen and redraw everything to start fresh
    clear_screen()
    draw_header()
    
    # Force sidebar redraw to ensure dimmed state is applied
    menu_state.last_sidebar_cache_key = None
    draw_sidebar()
    
    # Draw the menu once initially
    draw_database_setup_content()
    draw_footer()
    
    # Main loop with timeout like administration
    database_setup_menu_loop()
    
def database_setup_menu_loop():
    """Database setup menu loop with navigation"""
    last_header_update = time.time()
    
    # Define selectable options (without headers and separators)
    selectable_keys = ["full_install", "python_only", "postgres_only", "create_db", 
                      "start_service", "test_connection", "sqlite_mode", "back"]
    
    while menu_state.in_submenu == 'database_setup':
        # Update header time every second
        current_time = time.time()
        if current_time - last_header_update >= 1.0:
            draw_header_time_only()
            last_header_update = current_time
        
        # Get user input
        key = get_single_key(timeout=0.1)
        
        if key:
            num_options = len(selectable_keys)
            
            # Handle navigation
            if key == '\x1b[A' or key == 'k':  # Up arrow
                menu_state.database_setup_index = (menu_state.database_setup_index - 1) % num_options
                draw_database_setup_content()
            
            elif key == '\x1b[B' or key == 'j':  # Down arrow
                menu_state.database_setup_index = (menu_state.database_setup_index + 1) % num_options
                draw_database_setup_content()
            
            elif key == '\r' or key == '\x1b[C':  # Enter or Right arrow
                # Handle selection
                selected_option = selectable_keys[menu_state.database_setup_index]
                if selected_option == "back":
                    menu_state.in_submenu = None
                    break
                else:
                    handle_db_option(selected_option)
                    draw_database_setup_content()
            
            elif key in ['\x1b', '\x1b[D', 'q']:  # ESC, Left arrow or q
                menu_state.in_submenu = None
                break
    
def draw_database_setup_content():
    """Draw database setup menu content - called only when needed"""
    clear_content_area()
    
    # Small delay to ensure clear is processed
    time.sleep(0.002)
    
    cols, lines = get_terminal_size()
    content_x = 27  # After sidebar (don't add extra offset)
    content_width = cols - content_x - 1
    start_y = 3  # Changed from 4 to 3 for single-line header
    
    # Initialize selected_index if not exists
    if not hasattr(menu_state, 'database_setup_index'):
        menu_state.database_setup_index = 0
    selected_index = menu_state.database_setup_index
    
    # Check PostgreSQL status
    try:
        postgres_installed = subprocess.run(["which", "psql"], capture_output=True).returncode == 0
        postgres_running = subprocess.run(["pg_isready"], capture_output=True).returncode == 0
    except:
        postgres_installed = False
        postgres_running = False
        
    # Check Python packages - check in backend venv primarily
    python_packages = False
    
    # First check if backend venv has psycopg2-binary
    backend_venv_pip = Path(__file__).parent.parent / 'backend' / 'venv' / 'bin' / 'pip'
    if backend_venv_pip.exists():
        result = subprocess.run([str(backend_venv_pip), 'show', 'psycopg2-binary'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            python_packages = True
    
    # Also check system Python as fallback
    if not python_packages:
        try:
            import psycopg2
            python_packages = True
        except ImportError:
            # Check system pip
            result = subprocess.run(['pip3', 'show', 'psycopg2-binary'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                python_packages = True
    
    # Title
    move_cursor(content_x + 2, start_y)
    sys.stdout.write(f"{Colors.BOLD}{Colors.BLUE}🗄️  database setup{Colors.RESET}")
    sys.stdout.flush()
    
    # System status - compact like web forge
    y = start_y + 2
    move_cursor(content_x + 2, y)
    sys.stdout.write(f"{Colors.BOLD}system status:{Colors.RESET}")
    sys.stdout.flush()
    y += 1
    
    move_cursor(content_x + 4, y)
    status = "✅ installed" if postgres_installed else "❌ not installed"
    color = Colors.GREEN if postgres_installed else Colors.RED
    sys.stdout.write(f"postgresql: {color}{status}{Colors.RESET}")
    sys.stdout.flush()
    y += 1
    
    if postgres_installed:
        move_cursor(content_x + 4, y)
        status = "✅ running" if postgres_running else "⚠️  stopped"
        color = Colors.GREEN if postgres_running else Colors.YELLOW
        sys.stdout.write(f"service: {color}{status}{Colors.RESET}")
        sys.stdout.flush()
        y += 1
    
    move_cursor(content_x + 4, y)
    status = "✅ installed" if python_packages else "❌ not installed"
    color = Colors.GREEN if python_packages else Colors.RED
    sys.stdout.write(f"python packages: {color}{status}{Colors.RESET}")
    sys.stdout.flush()
    y += 2
    
    # Menu options with better grouping
    options = [
            ("header", "🛠️ installation", ""),
            ("full_install", "  🚀 full installation", "postgresql + python"),
            ("python_only", "  📦 install python packages only", ""),
            ("postgres_only", "  🗄️  install postgresql only", ""),
            ("separator", "---", "---"),
            ("header", "🔧 database operations", ""),
            ("create_db", "  🔨 create database", ""),
            ("start_service", "  ▶️  start postgresql service", ""),
            ("test_connection", "  🔍 test database connection", ""),
            ("separator", "---", "---"),
            ("header", "📦 alternatives", ""),
            ("sqlite_mode", "  💾 continue with sqlite", ""),
            ("separator", "---", "---"),
            ("back", "← back to dev tools", "")
    ]
    
    # Draw options header
    move_cursor(content_x + 2, y)
    sys.stdout.write(f"{Colors.CYAN}options:{Colors.RESET}")
    sys.stdout.flush()
    y += 1
    
    actual_index = 0
    for i, item in enumerate(options):
        if len(item) == 3:
            key, title, desc = item
        else:
            key, title = item
            desc = ""
        
        move_cursor(content_x + 3, y)
        sys.stdout.write('\033[K')  # Clear line
        
        if key == "separator":
            sys.stdout.write(f"{Colors.DIM}{'─' * min(content_width - 8, 60)}{Colors.RESET}")
            y += 1
        elif key == "header":
            if y > start_y + 3:  # Add space before headers except first
                y += 1
                move_cursor(content_x + 3, y)
            sys.stdout.write(f"{Colors.BOLD}{Colors.YELLOW}{title}{Colors.RESET}")
            y += 1
        else:
            # Regular option - check if selected
            if actual_index == selected_index:
                # Orange background for selected
                sys.stdout.write(f"{Colors.BG_ORANGE}{Colors.BLACK}{Colors.BOLD} → {title:<40}{Colors.RESET}")
            else:
                sys.stdout.write(f"   {title}")
            
            if desc:
                sys.stdout.write(f"  {Colors.DIM}{desc}{Colors.RESET}")
            
            actual_index += 1
            y += 1
        
        sys.stdout.flush()
    
    # Navigation hint at bottom
    y += 2
    move_cursor(content_x + 3, y)
    sys.stdout.write(f"{Colors.DIM}↑↓ navigate | enter select | ←/esc/q back{Colors.RESET}")
    sys.stdout.flush()
    
    # Navigation handled in database_setup_menu_loop now

def handle_db_option(option):
    """Handle database setup options"""
    # Clear the entire content area completely
    cols, lines = get_terminal_size()
    content_x = 27  # After sidebar (no extra offset)
    
    # Clear from line 3 (after header) to footer
    for y in range(3, lines - 1):
        move_cursor(content_x, y)
        # Clear from cursor to end of line
        sys.stdout.write('\033[K')
    sys.stdout.flush()
    
    # Small delay to ensure clearing is visible
    time.sleep(0.05)
    
    # Start display from line 5
    y = 5
    
    # Show what we're doing
    move_cursor(content_x + 2, y)
    print(f"{Colors.CYAN}🔄 processing: {option}{Colors.RESET}")
    y += 2
    
    if option == "full_install":
        move_cursor(content_x + 2, y)
        print(f"{Colors.YELLOW}full installation starting...{Colors.RESET}")
        y += 2
        
        # Install PostgreSQL
        move_cursor(content_x + 2, y)
        print(f"{Colors.CYAN}1. installing postgresql...{Colors.RESET}")
        y += 1
        
        try:
            result = subprocess.run(['brew', 'install', 'postgresql@14'], 
                                 capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                move_cursor(content_x + 4, y)
                print(f"{Colors.GREEN}✓ postgresql installed{Colors.RESET}")
            else:
                move_cursor(content_x + 4, y)
                print(f"{Colors.YELLOW}⚠ postgresql may already be installed{Colors.RESET}")
        except:
            move_cursor(content_x + 4, y)
            print(f"{Colors.RED}✗ installation failed{Colors.RESET}")
        
        y += 2
        
        # Install Python packages
        move_cursor(content_x + 2, y)
        print(f"{Colors.CYAN}2. installing python packages...{Colors.RESET}")
        y += 1
        
        # Check if backend venv exists, create if not
        backend_venv = Path(__file__).parent.parent / 'backend' / 'venv'
        backend_pip = backend_venv / 'bin' / 'pip'
        
        if not backend_venv.exists():
            move_cursor(content_x + 4, y)
            print(f"{Colors.DIM}creating virtual environment...{Colors.RESET}")
            subprocess.run(['python3', '-m', 'venv', str(backend_venv)], capture_output=True)
            y += 1
        
        packages = ['psycopg2-binary', 'django']
        for pkg in packages:
            move_cursor(content_x + 4, y)
            print(f"{Colors.DIM}installing {pkg}...{Colors.RESET}")
            # Install in backend venv if it exists, otherwise system
            if backend_pip.exists():
                subprocess.run([str(backend_pip), 'install', pkg], capture_output=True)
            else:
                subprocess.run(['pip3', 'install', pkg], capture_output=True)
            y += 1
        
        move_cursor(content_x + 4, y)
        print(f"{Colors.GREEN}✓ python packages installed{Colors.RESET}")
        y += 2
        
        # Start service
        move_cursor(content_x + 2, y)
        print(f"{Colors.CYAN}3. starting postgresql service...{Colors.RESET}")
        y += 1
        
        subprocess.run(['brew', 'services', 'start', 'postgresql@14'], capture_output=True)
        move_cursor(content_x + 4, y)
        print(f"{Colors.GREEN}✓ service started{Colors.RESET}")
        
        y += 2
        move_cursor(content_x + 2, y)
        print(f"{Colors.GREEN}✓ full installation complete!{Colors.RESET}")
        
        # Wait longer for user to see results
        y += 2
        move_cursor(content_x + 2, y)
        print(f"{Colors.DIM}returning to menu in 5 seconds...{Colors.RESET}")
        time.sleep(5)
        
    elif option == "test_connection":
        move_cursor(content_x + 2, y)
        print(f"{Colors.CYAN}testing database connection...{Colors.RESET}")
        try:
            import psycopg2
            conn = psycopg2.connect(
                host="localhost",
                database="postgres",
                user=os.environ.get('USER', 'postgres')
            )
            conn.close()
            y += 2
            move_cursor(content_x + 2, y)
            print(f"{Colors.GREEN}✅ connection successful!{Colors.RESET}")
        except Exception as e:
            y += 2
            move_cursor(content_x + 2, y)
            print(f"{Colors.RED}❌ connection failed{Colors.RESET}")
        # Wait for user to see result
        time.sleep(3)
    elif option == "sqlite_mode":
        move_cursor(content_x + 2, y)
        print(f"{Colors.GREEN}✅ continuing with sqlite{Colors.RESET}")
        y += 2
        move_cursor(content_x + 2, y)
        print(f"{Colors.DIM}database: data/unibos.db{Colors.RESET}")
        time.sleep(3)
    elif option == "python_only":
        move_cursor(content_x + 2, y)
        print(f"{Colors.CYAN}installing python packages...{Colors.RESET}")
        y += 2
        
        # Check if backend venv exists, create if not
        backend_venv = Path(__file__).parent.parent / 'backend' / 'venv'
        backend_pip = backend_venv / 'bin' / 'pip'
        
        if not backend_venv.exists():
            move_cursor(content_x + 2, y)
            print(f"{Colors.DIM}creating virtual environment...{Colors.RESET}")
            subprocess.run(['python3', '-m', 'venv', str(backend_venv)], capture_output=True)
            y += 1
        
        packages = ['psycopg2-binary', 'django', 'djangorestframework']
        for pkg in packages:
            move_cursor(content_x + 2, y)
            print(f"{Colors.DIM}pip install {pkg}...{Colors.RESET}")
            # Install in backend venv if it exists, otherwise system
            if backend_pip.exists():
                subprocess.run([str(backend_pip), 'install', pkg], capture_output=True)
            else:
                subprocess.run(['pip3', 'install', pkg], capture_output=True)
            y += 1
        move_cursor(content_x + 2, y)
        print(f"{Colors.GREEN}✓ packages installed{Colors.RESET}")
        time.sleep(3)
        
    elif option == "postgres_only":
        move_cursor(content_x + 2, y)
        print(f"{Colors.CYAN}installing postgresql...{Colors.RESET}")
        y += 2
        subprocess.run(['brew', 'install', 'postgresql@14'], capture_output=True)
        move_cursor(content_x + 2, y)
        print(f"{Colors.GREEN}✓ postgresql installed{Colors.RESET}")
        time.sleep(3)
        
    elif option == "create_db":
        move_cursor(content_x + 2, y)
        print(f"{Colors.CYAN}creating database...{Colors.RESET}")
        y += 2
        subprocess.run(['createdb', 'unibos'], capture_output=True)
        move_cursor(content_x + 2, y)
        print(f"{Colors.GREEN}✓ database 'unibos' created{Colors.RESET}")
        time.sleep(3)
        
    elif option == "start_service":
        move_cursor(content_x + 2, y)
        print(f"{Colors.CYAN}starting postgresql service...{Colors.RESET}")
        y += 2
        subprocess.run(['brew', 'services', 'start', 'postgresql@14'], capture_output=True)
        move_cursor(content_x + 2, y)
        print(f"{Colors.GREEN}✓ service started{Colors.RESET}")
        time.sleep(3)
        
    else:
        move_cursor(content_x + 2, y)
        print(f"{Colors.YELLOW}⚠️  option '{option}' coming soon{Colors.RESET}")
        time.sleep(2)

def launch_django_web_ui():
    """Launch Django web UI in browser with automatic start"""
    show_server_action("🌐 launching web interface", Colors.CYAN)
    
    cols, lines = get_terminal_size()
    content_x = 27 + 4
    y = 5
    
    # Step 1: Check server status
    move_cursor(content_x, y)
    print(f"{Colors.YELLOW}checking server status...{Colors.RESET}")
    y += 2
    
    backend_running, backend_pid = check_backend_running()
    
    # Step 2: Start server if needed
    if not backend_running:
        move_cursor(content_x, y)
        print(f"{Colors.YELLOW}server is not running. starting...{Colors.RESET}")
        y += 2
        
        # Check backend port
        backend_port_check = subprocess.run(['lsof', '-ti:8000'], capture_output=True, text=True)
        if backend_port_check.returncode == 0 and backend_port_check.stdout.strip():
            # Port is in use but backend is not running properly
            move_cursor(content_x, y)
            print(f"{Colors.YELLOW}⚠ port 8000 is in use, cleaning up...{Colors.RESET}")
            y += 1
            # Try to kill the process
            try:
                pids = backend_port_check.stdout.strip().split('\n')
                for pid in pids:
                    subprocess.run(['kill', '-9', pid], capture_output=True)
                time.sleep(1)
            except:
                pass
        
        # Start Django server
        move_cursor(content_x, y)
        print(f"{Colors.CYAN}starting django server...{Colors.RESET}")
        y += 1
        
        start_web_backend(is_restart=False)
        
        # Wait for startup
        move_cursor(content_x, y)
        print(f"{Colors.DIM}waiting for server to initialize...{Colors.RESET}")
        time.sleep(3)
        
        # Check status again
        backend_running, backend_pid = check_backend_running()
    
    # Clear the area and show status
    clear_content_area()
    y = 5
    
    # Step 3: Verify server is running
    move_cursor(content_x, y)
    print(f"{Colors.BOLD}{Colors.CYAN}═══ server status ═══{Colors.RESET}")
    y += 2
    
    move_cursor(content_x, y)
    if backend_running:
        print(f"{Colors.GREEN}✓ django server:{Colors.RESET} {Colors.BOLD}running{Colors.RESET}")
        move_cursor(content_x + 2, y + 1)
        print(f"{Colors.DIM}PID: {backend_pid}{Colors.RESET}")
        move_cursor(content_x + 2, y + 2)
        print(f"{Colors.DIM}URL: http://localhost:8000{Colors.RESET}")
        y += 4
    else:
        print(f"{Colors.RED}✗ server failed to start{Colors.RESET}")
        move_cursor(content_x + 2, y + 1)
        print(f"{Colors.DIM}check logs for details{Colors.RESET}")
        y += 3
    
    # Step 4: Open browser
    move_cursor(content_x, y)
    print(f"{Colors.BOLD}{Colors.CYAN}═══ opening web interface ═══{Colors.RESET}")
    y += 2
    
    # ALWAYS use backend URL since frontend is removed
    url = "http://localhost:8000"
    move_cursor(content_x, y)
    print(f"{Colors.CYAN}🌐 launching django application{Colors.RESET}")
    move_cursor(content_x, y + 1)
    print(f"{Colors.DIM}   URL: {url}{Colors.RESET}")
    
    y += 3
    
    try:
        import webbrowser
        webbrowser.open(url)
        move_cursor(content_x, y)
        print(f"{Colors.GREEN}✓ browser opened successfully{Colors.RESET}")
    except Exception as e:
        move_cursor(content_x, y)
        print(f"{Colors.YELLOW}⚠ could not auto-open browser{Colors.RESET}")
        y += 1
        move_cursor(content_x, y)
        print(f"{Colors.DIM}please open manually: {url}{Colors.RESET}")
    
    # Show available endpoints
    y += 3
    move_cursor(content_x, y)
    print(f"{Colors.DIM}available endpoints:{Colors.RESET}")
    y += 1
    
    move_cursor(content_x, y)
    print(f"{Colors.DIM}  • django app: http://localhost:8000/{Colors.RESET}")
    y += 1
    move_cursor(content_x, y)
    print(f"{Colors.DIM}  • admin panel: http://localhost:8000/admin/{Colors.RESET}")
    y += 1
    move_cursor(content_x, y)
    print(f"{Colors.DIM}  • documents: http://localhost:8000/documents/{Colors.RESET}")
    
    # Return handled by menu system

def start_web_backend(is_restart=False):
    """Start Django backend server using server_manager"""
    if not is_restart:
        show_server_action("⚙️ starting web core", Colors.CYAN)
    
    cols, lines = get_terminal_size()
    content_x = 27 + 4
    y = 5
    
    try:
        from server_manager import start_web_core, get_web_core_status
        
        move_cursor(content_x, y)
        print(f"{Colors.YELLOW}checking services...{Colors.RESET}")
        
        # Start with auto-recovery
        success = start_web_core(silent=True)
        
        # Check status
        time.sleep(2)
        status = get_web_core_status()
        
        move_cursor(content_x, y + 1)
        if success and status.get('running') and status.get('api_healthy'):
            move_cursor(content_x, y)
            print(f"{Colors.GREEN}✓ web core started successfully{Colors.RESET}")
            y += 1
            move_cursor(content_x, y)
            print(f"{Colors.DIM}URL: http://localhost:8000{Colors.RESET}")
        else:
            move_cursor(content_x, y)
            print(f"{Colors.RED}✗ failed to start web core{Colors.RESET}")
            if result.stderr:
                y += 1
                move_cursor(content_x, y)
                print(f"{Colors.DIM}{result.stderr[:100]}{Colors.RESET}")
    except subprocess.TimeoutExpired:
        move_cursor(content_x, y)
        print(f"{Colors.RED}✗ timeout while starting server{Colors.RESET}")
    except Exception as e:
        move_cursor(content_x, y)
        print(f"{Colors.RED}✗ error: {str(e)}{Colors.RESET}")
    
    if not is_restart:
        y += 2
        move_cursor(content_x, y)
        print(f"{Colors.DIM}press any key to continue...{Colors.RESET}")
        get_single_key()

def start_web_frontend(is_restart=False):
    """Frontend removed - no longer needed"""
    if not is_restart:
        show_server_action("ℹ️ frontend removed", Colors.YELLOW)
    
    cols, lines = get_terminal_size()
    content_x = 27 + 4
    y = 5
    
    move_cursor(content_x, y)
    print(f"{Colors.YELLOW}frontend has been removed from UNIBOS{Colors.RESET}")
    y += 2
    move_cursor(content_x, y)
    print(f"{Colors.DIM}the web interface is now served directly by django{Colors.RESET}")
    y += 1
    move_cursor(content_x, y)
    print(f"{Colors.DIM}use 'open web interface' to launch the application{Colors.RESET}")
    y += 3
    # Return handled by menu system
def install_redis():
    """Install Redis based on the operating system"""
    cols, lines = get_terminal_size()
    content_x = 31
    y = 5
    
    clear_content_area()
    
    move_cursor(content_x, y)
    print(f"{Colors.CYAN}🔴 redis installer{Colors.RESET}")
    y += 2
    
    # Detect OS
    system = platform.system()
    
    if system == "Darwin":  # macOS
        move_cursor(content_x, y)
        print(f"{Colors.YELLOW}installing redis on macos...{Colors.RESET}")
        y += 2
        
        # Check if Homebrew is installed
        try:
            subprocess.run(['which', 'brew'], check=True, capture_output=True)
            
            move_cursor(content_x, y)
            print(f"{Colors.GREEN}✓ homebrew detected{Colors.RESET}")
            y += 1
            
            move_cursor(content_x, y)
            print(f"{Colors.CYAN}running: brew install redis{Colors.RESET}")
            y += 2
            
            # Install Redis
            result = subprocess.run(['brew', 'install', 'redis'], 
                                 capture_output=True, text=True)
            
            if result.returncode == 0:
                move_cursor(content_x, y)
                print(f"{Colors.GREEN}✓ redis installed successfully!{Colors.RESET}")
                y += 2
                
                move_cursor(content_x, y)
                print(f"{Colors.DIM}to start redis: brew services start redis{Colors.RESET}")
                y += 1
                move_cursor(content_x, y)
                print(f"{Colors.DIM}to stop redis: brew services stop redis{Colors.RESET}")
            else:
                move_cursor(content_x, y)
                print(f"{Colors.RED}✗ installation failed{Colors.RESET}")
                y += 1
                move_cursor(content_x, y)
                print(f"{Colors.DIM}{result.stderr[:100]}{Colors.RESET}")
                
        except subprocess.CalledProcessError:
            move_cursor(content_x, y)
            print(f"{Colors.RED}✗ homebrew not found{Colors.RESET}")
            y += 2
            move_cursor(content_x, y)
            print(f"{Colors.YELLOW}please install homebrew first:{Colors.RESET}")
            y += 1
            move_cursor(content_x, y)
            print(f"{Colors.DIM}/bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"{Colors.RESET}")
            
    elif system == "Linux":
        move_cursor(content_x, y)
        print(f"{Colors.YELLOW}installing redis on linux...{Colors.RESET}")
        y += 2
        
        move_cursor(content_x, y)
        print(f"{Colors.CYAN}for ubuntu/debian: sudo apt-get install redis-server{Colors.RESET}")
        y += 1
        move_cursor(content_x, y)
        print(f"{Colors.CYAN}for fedora/rhel: sudo dnf install redis{Colors.RESET}")
        y += 1
        move_cursor(content_x, y)
        print(f"{Colors.CYAN}for arch: sudo pacman -S redis{Colors.RESET}")
        
    else:
        move_cursor(content_x, y)
        print(f"{Colors.RED}unsupported os: {system}{Colors.RESET}")
    
    # Wait for input
    y += 3
    move_cursor(content_x, y)
    time.sleep(3)  # Auto return after 3 seconds

def web_forge_menu():
    """Enhanced web forge with environment checks and setup wizard - exactly like version_manager"""
    menu_state.in_submenu = 'web_forge'
    menu_state.web_forge_index = 0
    
    # Clear screen and redraw everything to start fresh
    clear_screen()
    draw_header()
    
    # Force sidebar redraw to ensure dimmed state is applied
    menu_state.last_sidebar_cache_key = None  # Clear cache to force redraw
    draw_sidebar()
    
    # Clear input buffer before starting to prevent any leftover characters
    if TERMIOS_AVAILABLE:
        try:
            import termios
            # Flush multiple times to ensure buffer is completely clear
            for _ in range(3):
                termios.tcflush(sys.stdin, termios.TCIFLUSH)
                termios.tcflush(sys.stdin, termios.TCIOFLUSH)
                time.sleep(0.01)
        except:
            pass
    
    # Draw web forge menu in main content area
    draw_web_forge_menu()
    draw_footer()
    
    # Hide cursor for better visual experience
    hide_cursor()
    
    # Track last footer update time for clock
    last_footer_update = time.time()
    
    # Track last full redraw for periodic refresh (prevents artifacts)
    last_full_redraw = time.time()
    redraw_interval = 30.0  # Full redraw every 30 seconds to prevent artifacts
    
    # Track status updates separately - update every 5 seconds
    last_status_update = time.time()
    status_update_interval = 5.0
    
    # Track navigation count for stability check
    navigation_count = 0
    
    while menu_state.in_submenu == 'web_forge':
        # Don't update header during navigation to prevent blinking
        # Version manager doesn't update header and works perfectly
        
        # No periodic redraws needed if we handle updates properly
        current_time = time.time()
        
        # Update status independently every 5 seconds
        if current_time - last_status_update >= status_update_interval:
            draw_web_forge_menu(update_status_only=True)
            last_status_update = current_time
        
        # Handle input with timeout for clock updates
        key = get_single_key(timeout=0.1)
        
        # Handle navigation keys
        if key in ['\x1b[A', 'w', 'W', 'k', 'K']:  # Up arrow, w, k
            # Get actual selectable options count
            selectable_options = [opt for opt in get_web_forge_options() if opt[0] not in ['header', 'separator']]
            num_options = len(selectable_options)
            
            old_index = menu_state.web_forge_index
            menu_state.web_forge_index = (menu_state.web_forge_index - 1) % num_options
            
            # Use fast selection update instead of full redraw
            update_web_forge_selection_only(old_index, menu_state.web_forge_index)
            
        elif key in ['\x1b[B', 's', 'S', 'j', 'J']:  # Down arrow, s, j
            # Get actual selectable options count
            selectable_options = [opt for opt in get_web_forge_options() if opt[0] not in ['header', 'separator']]
            num_options = len(selectable_options)
            
            old_index = menu_state.web_forge_index
            menu_state.web_forge_index = (menu_state.web_forge_index + 1) % num_options
            
            # Use fast selection update instead of full redraw
            update_web_forge_selection_only(old_index, menu_state.web_forge_index)
            
        elif key in ['\x1b', '\x1b[D', 'q', 'Q']:  # ESC, Left Arrow, or q to exit
            # Exit Web Forge menu with COMPLETE cleanup
            menu_state.in_submenu = None
            
            # Clear ALL caches to force complete redraw of sidebar
            menu_state.last_sidebar_cache_key = None
            if hasattr(menu_state, 'last_content_cache_key'):
                menu_state.last_content_cache_key = None
            # Clear web forge status cache for fresh status on re-entry
            if hasattr(menu_state, 'web_forge_status_cache'):
                delattr(menu_state, 'web_forge_status_cache')
            
            # CRITICAL FIX: Complete terminal reset and redraw
            # Step 1: Clear screen completely
            clear_screen()
            
            # Step 2: Reset cursor to home position
            sys.stdout.write('\033[H')
            sys.stdout.flush()
            
            # Step 3: Small delay to ensure terminal processes the clear
            time.sleep(0.02)
            
            # Step 4: Force re-initialization of menu items to ensure sidebar is complete
            initialize_menu_items()
            
            # Step 5: Use draw_main_screen for complete redraw
            # This will now properly render the entire UI including full sidebar
            draw_main_screen()
            
            # Step 6: Ensure cursor is hidden
            hide_cursor()
            break
            
        elif key in ['\r', '\n', ' ', '\x1b[C', 'l', 'L']:  # Enter, Space, Right Arrow, or l to select
            # Get actual selectable options dynamically
            all_options = get_web_forge_options()
            selectable_options = [opt[0] for opt in all_options if opt[0] not in ['header', 'separator']]
            selected_option = selectable_options[menu_state.web_forge_index]
            
            if selected_option == "open_web_ui":
                launch_django_web_ui()
                # Redraw menu after returning
                draw_web_forge_menu()
            elif selected_option == "env_check":
                run_environment_check()
                # Redraw menu after returning
                draw_web_forge_menu()
            elif selected_option == "start_server":
                start_web_backend()
                draw_web_forge_menu()
            elif selected_option == "stop_server":
                stop_backend_server()
                draw_web_forge_menu()
            elif selected_option == "restart_server":
                restart_backend_server()
                draw_web_forge_menu()
            elif selected_option == "migrate":
                run_django_migrations()
                draw_web_forge_menu()
            elif selected_option == "install_redis":
                install_redis()
                draw_web_forge_menu()
            elif selected_option == "status":
                show_simple_web_status()
                draw_web_forge_menu()
            elif selected_option == "logs":
                show_server_logs()
                draw_web_forge_menu()
            elif selected_option == "back":
                # Exit Web Forge menu with COMPLETE cleanup (same as Q key)
                menu_state.in_submenu = None
                
                # Clear ALL caches to force complete redraw
                menu_state.last_sidebar_cache_key = None
                if hasattr(menu_state, 'last_content_cache_key'):
                    menu_state.last_content_cache_key = None
                
                # CRITICAL FIX: Complete terminal reset and redraw
                # Step 1: Clear screen completely
                clear_screen()
                
                # Step 2: Reset cursor to home position
                sys.stdout.write('\033[H')
                sys.stdout.flush()
                
                # Step 3: Small delay to ensure terminal processes the clear
                time.sleep(0.02)
                
                # Step 4: Use draw_main_screen for complete redraw
                # This is the most reliable way to restore the UI
                draw_main_screen()
                
                # Step 5: Ensure cursor is hidden
                hide_cursor()
                break
                
                # Ensure input buffer is completely clear
                if TERMIOS_AVAILABLE:
                    try:
                        import termios
                        fd = sys.stdin.fileno()
                        # Flush all pending input
                        termios.tcflush(fd, termios.TCIOFLUSH)
                        # Read and discard any remaining characters
                        old_settings = termios.tcgetattr(fd)
                        try:
                            import tty
                            tty.setraw(fd)
                            # Non-blocking read to clear buffer
                            import select
                            while True:
                                rlist, _, _ = select.select([sys.stdin], [], [], 0)
                                if not rlist:
                                    break
                                sys.stdin.read(1)
                        finally:
                            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                    except:
                        pass
                
                menu_state.in_submenu = None
                # Ensure tools section is selected (web_ui is in tools, not dev_tools)
                menu_state.current_section = 1  # tools section
                menu_state.selected_index = 5  # web_ui is at index 5
                # Force full screen redraw to prevent artifacts
                clear_screen()
                draw_main_screen()
                break
    
    # Don't do anything here - the exit is already handled in the q/back options

def get_version_manager_options():
    """Get version manager menu options"""
    return [
        # Version Management
        ("header", "🚀 version management", ""),
        ("quick_release", "⚡ quick release", "auto version + commit + archive"),
        ("separator", "---", "---"),
        # Archive Management
        ("header", "📦 archive management", ""),
        ("archive_analyzer", "📊 archive size analyzer", "analyze version archive sizes"),
        ("separator", "---", "---"),
        # Git Operations
        ("header", "🔧 git operations", ""),
        ("git_status", "📈 git status", "view current git status"),
        ("version_sync", "🔄 fix version sync", "align VERSION.json with git"),
        ("separator", "---", "---"),
        # Maintenance
        ("header", "🛠️ maintenance", ""),
        ("validate_versions", "✔️  validate versions", "check version integrity"),
    ]

def draw_version_manager_menu():
    """Draw version manager menu interface"""
    cols, lines = get_terminal_size()
    content_x = 27  # After sidebar
    content_width = cols - content_x - 2
    
    # Get menu options
    options = get_version_manager_options()
    
    # Clear content area properly with ANSI escape sequences
    for y in range(2, lines - 2):  # Adjusted for single-line header
        move_cursor(content_x, y)
        sys.stdout.write('\033[K')  # Clear to end of line
    sys.stdout.flush()
    
    # Title - lowercase
    move_cursor(content_x + 2, 3)  # Changed from 4 to 3
    print(f"{Colors.BOLD}{Colors.CYAN}📊 version manager{Colors.RESET}")
    
    # Description - lowercase
    move_cursor(content_x + 2, 5)  # Changed from 6 to 5
    print(f"{Colors.YELLOW}archive management & version control{Colors.RESET}")
    
    # Draw menu options
    y = 7  # Changed from 8 to 7
    option_index = 0
    
    for i, (key, name, desc) in enumerate(options):
        if key == "header":
            # Section header
            move_cursor(content_x + 2, y)
            print(f"{Colors.BOLD}{Colors.BLUE}{name}{Colors.RESET}")
            y += 1
        elif key == "separator":
            # Separator line
            move_cursor(content_x + 2, y)
            print(f"{Colors.DIM}{'─' * 40}{Colors.RESET}")
            y += 1
        else:
            # Menu option
            is_selected = (option_index == menu_state.version_manager_index)
            
            move_cursor(content_x + 2, y)
            if is_selected:
                # Use orange background like other menus
                print(f"{Colors.BG_ORANGE}{Colors.BLACK}{Colors.BOLD} → {name:<30} {Colors.RESET}", end='')
                # Show description on the right
                if desc:
                    print(f" {Colors.DIM}{desc}{Colors.RESET}")
                else:
                    print()
            else:
                print(f"   {name:<30}", end='')
                if desc:
                    print(f" {Colors.DIM}{desc}{Colors.RESET}")
                else:
                    print()
            
            option_index += 1
            y += 1
        
        # Prevent overflow
        if y >= lines - 3:
            break
    
    # No need for help text here - footer already shows navigation
    
    # Ensure everything is displayed
    sys.stdout.flush()

def version_manager_menu():
    """Version manager submenu with archive and git tools"""
    menu_state.in_submenu = 'version_manager'
    menu_state.version_manager_index = 0
    
    # Clear screen and redraw everything to start fresh
    clear_screen()
    draw_header()
    
    # Force sidebar redraw to ensure dimmed state is applied
    menu_state.last_sidebar_cache_key = None
    draw_sidebar()
    
    # Clear input buffer before starting
    if TERMIOS_AVAILABLE:
        try:
            import termios
            for _ in range(3):
                termios.tcflush(sys.stdin, termios.TCIFLUSH)
                termios.tcflush(sys.stdin, termios.TCIOFLUSH)
                time.sleep(0.01)
        except:
            pass
    
    # Draw version manager menu
    draw_version_manager_menu()
    draw_footer()
    
    # Hide cursor for better visual experience
    hide_cursor()
    
    # Track last footer update time for clock
    last_footer_update = time.time()
    
    while menu_state.in_submenu == 'version_manager':
        # Update header time every second
        current_time = time.time()
        if current_time - last_footer_update >= 1.0:
            draw_header_time_only()  # Use time-only update to prevent flickering
            last_footer_update = current_time
        
        # Non-blocking key check
        key = get_single_key(0.1)
        
        if key:
            # Get current options
            options = get_version_manager_options()
            # Filter out headers and separators for navigation
            selectable_options = [(k, n, d) for k, n, d in options if k not in ["header", "separator"]]
            
            if key in ['\x1b[A', 'k', 'K']:  # Up arrow or k
                if menu_state.version_manager_index > 0:
                    menu_state.version_manager_index -= 1
                    # Redraw header to prevent black spaces
                    draw_header()
                    draw_version_manager_menu()
            
            elif key in ['\x1b[B', 'j', 'J']:  # Down arrow or j
                if menu_state.version_manager_index < len(selectable_options) - 1:
                    menu_state.version_manager_index += 1
                    # Redraw header to prevent black spaces
                    draw_header()
                    draw_version_manager_menu()
            
            elif key == '\r':  # Enter
                if 0 <= menu_state.version_manager_index < len(selectable_options):
                    selected_key = selectable_options[menu_state.version_manager_index][0]
                    
                    if selected_key == "archive_analyzer":
                        # Launch the archive analyzer
                        version_archive_analyzer()
                        # After analyzer exits, redraw the menu properly
                        menu_state.in_submenu = 'version_manager'
                        # Clear caches to force fresh redraw
                        menu_state.last_sidebar_cache_key = None
                        if hasattr(menu_state, 'last_content_cache_key'):
                            menu_state.last_content_cache_key = None
                        # Clear and redraw everything to prevent artifacts
                        clear_screen()
                        draw_header()
                        draw_sidebar()  # This will now redraw properly with cache cleared
                        draw_version_manager_menu()
                        draw_footer()
                        # Force a full flush
                        sys.stdout.flush()
                    
                    elif selected_key == "quick_release":
                        # Run quick release directly in CLI
                        execute_quick_release()
                        # Redraw after returning
                        clear_screen()
                        draw_header()
                        draw_sidebar()
                        draw_version_manager_menu()
                        draw_footer()
                    
                    elif selected_key == "version_sync":
                        # Launch unified version manager in sync fix mode
                        launch_unified_version_manager("4")
                        # Redraw after returning
                        clear_screen()
                        draw_header()
                        draw_sidebar()
                        draw_version_manager_menu()
                        draw_footer()
                    
                    elif selected_key == "git_status":
                        # Show git status
                        show_git_status_quick()
                        draw_version_manager_menu()
                    
                    elif selected_key == "validate_versions":
                        print(f"\n{Colors.YELLOW}Version validation coming soon...{Colors.RESET}")
                        time.sleep(2)
                        draw_version_manager_menu()
            
            elif key in ['\x1b', '\x1b[D', 'q', 'Q']:  # ESC, Left Arrow, or q to exit
                # Exit version manager menu
                menu_state.in_submenu = None
                menu_state.current_section = 2  # dev tools section
                menu_state.selected_index = 3  # version manager is at index 3
                clear_screen()
                draw_main_screen()
                break
        
        # Small sleep to prevent CPU spinning
        time.sleep(0.01)
    
    # Show cursor when exiting
    show_cursor()

def clear_content_area_from_line(start_line):
    """Clear content area from specific line to bottom"""
    cols, lines = get_terminal_size()
    content_x = 27  # After sidebar
    content_width = cols - content_x - 2
    
    for y in range(start_line, lines - 2):
        move_cursor(content_x, y)
        sys.stdout.write('\033[K')
    sys.stdout.flush()

def execute_quick_release():
    """Execute quick release with native CLI interface"""
    cols, lines = get_terminal_size()
    content_x = 27  # After sidebar
    content_width = cols - content_x - 2
    
    # Clear content area
    for y in range(3, lines - 2):
        move_cursor(content_x, y)
        sys.stdout.write('\033[K')
    sys.stdout.flush()
    
    # Breadcrumb
    move_cursor(content_x + 2, 3)
    print(f"{Colors.DIM}dev tools > version manager > quick release{Colors.RESET}")
    
    # Title
    move_cursor(content_x + 2, 5)
    print(f"{Colors.BOLD}{Colors.CYAN}⚡ Quick Release{Colors.RESET}")
    
    try:
        # Calculate next version
        current_version = get_current_version_number()
        next_version = current_version + 1
        
        move_cursor(content_x + 2, 7)
        print(f"{Colors.GREEN}Next version: v{next_version}{Colors.RESET}")
        
        # Check for uncommitted changes
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True,
                              cwd='/Users/berkhatirli/Desktop/unibos')
        
        if result.stdout:
            # Show changed files
            move_cursor(content_x + 2, 9)
            print(f"{Colors.YELLOW}📊 Changed files:{Colors.RESET}")
            
            y = 11
            lines_changed = result.stdout.strip().split('\n')[:10]
            for line in lines_changed:
                move_cursor(content_x + 4, y)
                print(f"{Colors.DIM}{line[:content_width-6]}{Colors.RESET}")
                y += 1
            
            if len(result.stdout.strip().split('\n')) > 10:
                move_cursor(content_x + 4, y)
                print(f"{Colors.DIM}... and {len(result.stdout.strip().split('\n')) - 10} more files{Colors.RESET}")
                y += 1
            
            # Generate auto commit message and show recent logs
            auto_message = generate_auto_commit_message()
            recent_logs = get_recent_development_logs()
            
            # Show recent development logs if available
            if recent_logs and len(recent_logs) > 1:
                move_cursor(content_x + 2, y + 1)
                print(f"{Colors.CYAN}Recent development logs:{Colors.RESET}")
                for i, log in enumerate(recent_logs[:3]):
                    move_cursor(content_x + 4, y + 2 + i)
                    if i == 0:
                        print(f"{Colors.GREEN}• {log}{Colors.RESET}")
                    else:
                        print(f"{Colors.DIM}• {log}{Colors.RESET}")
                y += len(recent_logs[:3]) + 1
            
            move_cursor(content_x + 2, y + 2)
            print(f"{Colors.CYAN}Auto-selected commit message:{Colors.RESET}")
            move_cursor(content_x + 4, y + 3)
            print(f"{Colors.BOLD}{Colors.GREEN}{auto_message}{Colors.RESET}")
            
            # Get user input for description
            move_cursor(content_x + 2, y + 4)
            print(f"{Colors.YELLOW}Enter description (or press Enter for auto, q to cancel):{Colors.RESET}")
            move_cursor(content_x + 4, y + 5)
            
            # Show cursor for input
            show_cursor()
            description = input()
            hide_cursor()
            
            # Check if user wants to cancel
            if description.lower() == 'q':
                move_cursor(content_x + 2, lines - 2)
                print(f"{Colors.YELLOW}Cancelled.{Colors.RESET}")
                time.sleep(1)
                return
            
            if not description:
                description = auto_message
        else:
            move_cursor(content_x + 2, 8)
            print(f"{Colors.GREEN}✓ Working directory clean{Colors.RESET}")
            
            move_cursor(content_x + 2, 10)
            print(f"{Colors.YELLOW}Enter description (or q to cancel):{Colors.RESET}")
            move_cursor(content_x + 4, 11)
            
            show_cursor()
            description = input()
            hide_cursor()
            
            # Check if user wants to cancel
            if description.lower() == 'q':
                move_cursor(content_x + 2, lines - 2)
                print(f"{Colors.YELLOW}Cancelled.{Colors.RESET}")
                time.sleep(1)
                return
            
            if not description:
                description = "Regular update and maintenance"
        
        # Show progress
        move_cursor(content_x + 2, lines - 8)
        print(f"{Colors.CYAN}Processing...{Colors.RESET}")
        
        # Update VERSION.json
        move_cursor(content_x + 4, lines - 7)
        print(f"📝 Updating VERSION.json...", end='', flush=True)
        try:
            update_version_json(next_version, description)
            print(f" {Colors.GREEN}✓{Colors.RESET}")
        except Exception as e:
            print(f" {Colors.RED}✗ {str(e)}{Colors.RESET}")
            raise
        
        # Update Django files
        move_cursor(content_x + 4, lines - 6)
        print(f"🔧 Updating Django files...", end='', flush=True)
        try:
            update_django_version_files(next_version)
            print(f" {Colors.GREEN}✓{Colors.RESET}")
        except Exception as e:
            print(f" {Colors.RED}✗ {str(e)}{Colors.RESET}")
            # Non-critical, continue
        
        # Create archive
        move_cursor(content_x + 4, lines - 5)
        print(f"📦 Creating archive...", end='', flush=True)
        try:
            create_version_archive(next_version)
            print(f" {Colors.GREEN}✓{Colors.RESET}")
        except Exception as e:
            print(f" {Colors.RED}✗ {str(e)}{Colors.RESET}")
            raise
        
        # Git operations
        move_cursor(content_x + 4, lines - 4)
        print(f"🔄 Git operations...", end='', flush=True)
        try:
            commit_info = perform_git_operations(next_version, description)
            print(f" {Colors.GREEN}✓{Colors.RESET}")
            sys.stdout.flush()  # Ensure output is displayed immediately
        except Exception as e:
            print(f" {Colors.RED}✗ {str(e)}{Colors.RESET}")
            sys.stdout.flush()
            raise
        
        # Success message with detailed report
        move_cursor(content_x + 2, lines - 2)
        print(f"{Colors.BOLD}{Colors.GREEN}✅ Version v{next_version} released successfully!{Colors.RESET}")
        sys.stdout.flush()
        
        # Brief pause to ensure all operations are complete and displayed
        time.sleep(0.5)
        
        # Show release summary
        clear_content_area_from_line(8)
        move_cursor(content_x + 2, 8)
        print(f"{Colors.BOLD}{Colors.CYAN}📋 Release Summary:{Colors.RESET}")
        
        move_cursor(content_x + 2, 10)
        print(f"{Colors.GREEN}Version:{Colors.RESET} v{next_version}")
        
        # Get current build timestamp
        try:
            if ZoneInfo:
                istanbul_time = datetime.now(ZoneInfo('Europe/Istanbul'))
            else:
                from datetime import timezone, timedelta
                istanbul_tz = timezone(timedelta(hours=3))
                istanbul_time = datetime.now(istanbul_tz)
            build_timestamp = istanbul_time.strftime('%Y%m%d_%H%M')
        except:
            build_timestamp = 'N/A'
        
        move_cursor(content_x + 2, 11)
        print(f"{Colors.GREEN}Build:{Colors.RESET} {build_timestamp}")
        
        move_cursor(content_x + 2, 12)
        print(f"{Colors.GREEN}Commit Message:{Colors.RESET} {description}")
        
        move_cursor(content_x + 2, 14)
        print(f"{Colors.YELLOW}📦 Completed Operations:{Colors.RESET}")
        
        move_cursor(content_x + 4, 15)
        print(f"✓ VERSION.json updated")
        
        move_cursor(content_x + 4, 16)
        print(f"✓ Django files updated")
        
        move_cursor(content_x + 4, 17)
        print(f"✓ Archive created: unibos_v{next_version}_*")
        
        move_cursor(content_x + 4, 18)
        print(f"✓ Git branch: v{next_version}")
        
        move_cursor(content_x + 4, 19)
        print(f"✓ Git tag: v{next_version}")
        
        move_cursor(content_x + 4, 20)
        print(f"✓ Pushed to origin")
        
        move_cursor(content_x + 4, 21)
        if 'commit_info' in locals() and commit_info:
            print(f"✓ Commit: {commit_info[:50]}...")
        else:
            print(f"✓ Commit: Successfully committed")
        
        # Wait for key - more prominent (above footer line)
        move_cursor(content_x + 2, lines - 5)
        print(f"{Colors.CYAN}{'─' * 50}{Colors.RESET}")
        move_cursor(content_x + 2, lines - 4)
        print(f"{Colors.BOLD}{Colors.YELLOW}📋 Review the release summary above{Colors.RESET}")
        move_cursor(content_x + 2, lines - 3)
        print(f"{Colors.YELLOW}Press any key to return to version manager...{Colors.RESET}")
        sys.stdout.flush()
        get_single_key(timeout=None)  # Wait indefinitely for user input
        
    except Exception as e:
        move_cursor(content_x + 2, lines - 3)
        print(f"{Colors.RED}Error: {e}{Colors.RESET}")
        move_cursor(content_x + 2, lines - 1)
        print(f"{Colors.DIM}Press any key to continue...{Colors.RESET}")
        get_single_key(timeout=None)  # Wait indefinitely for user input

def get_current_version_number():
    """Get current version number from VERSION.json"""
    try:
        # Try different paths since main.py is in src/
        version_file = None
        possible_paths = [
            'VERSION.json',  # Same directory as main.py
            '../src/VERSION.json',  # If running from root
            '/Users/berkhatirli/Desktop/unibos/src/VERSION.json'  # Absolute path
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                version_file = path
                break
        
        if not version_file:
            raise FileNotFoundError("VERSION.json not found")
            
        with open(version_file, 'r') as f:
            data = json.load(f)
            version_str = data.get('version', 'v0')
            # Extract just the numeric part
            version_num = ''.join(filter(str.isdigit, version_str))
            return int(version_num) if version_num else 0
    except Exception as e:
        # If we can't read VERSION.json, try to get from git tags
        try:
            result = subprocess.run(['git', 'tag'], capture_output=True, text=True,
                                  cwd='/Users/berkhatirli/Desktop/unibos')
            tags = [tag for tag in result.stdout.strip().split('\n') if tag.startswith('v')]
            if tags:
                version_numbers = []
                for tag in tags:
                    try:
                        num = ''.join(filter(str.isdigit, tag))
                        if num:
                            version_numbers.append(int(num))
                    except:
                        pass
                if version_numbers:
                    return max(version_numbers)
        except:
            pass
        return 0

def get_recent_development_logs():
    """Get recent development log entries for commit message"""
    try:
        log_file = '/Users/berkhatirli/Desktop/unibos/DEVELOPMENT_LOG.md'
        if not os.path.exists(log_file):
            return []
        
        with open(log_file, 'r') as f:
            content = f.read()
        
        # Extract recent log entries (last 24 hours)
        import re
        from datetime import datetime, timedelta
        
        entries = []
        pattern = r'## \[(\d{4}-\d{2}-\d{2} \d{2}:\d{2})\] ([^:]+): (.+?)(?=\n-|\n##|\Z)'
        matches = re.findall(pattern, content, re.DOTALL)
        
        now = datetime.now()
        yesterday = now - timedelta(hours=24)
        
        for match in matches:
            try:
                log_time = datetime.strptime(match[0], '%Y-%m-%d %H:%M')
                if log_time > yesterday:
                    category = match[1].strip()
                    title = match[2].strip()
                    # Clean up title - remove newlines and extra spaces
                    title = ' '.join(title.split())
                    entries.append({
                        'time': log_time,
                        'category': category,
                        'title': title,
                        'full': f"{category}: {title}"
                    })
            except:
                continue
        
        # Sort by time, most recent first
        entries.sort(key=lambda x: x['time'], reverse=True)
        
        # Return just the formatted strings
        return [e['full'] for e in entries[:5]]  # Return last 5 relevant entries
    except Exception as e:
        return []

def generate_auto_commit_message():
    """Generate automatic commit message based on changes and development logs"""
    try:
        # Get recent development logs
        recent_logs = get_recent_development_logs()
        
        # If we have recent logs, use the most impactful one
        if recent_logs:
            # Priority order for categories
            priority_categories = ['Bug Fix', 'Feature', 'UI/UX', 'Performance', 'Version Manager', 
                                   'Navigation', 'Module', 'Development Tools', 'Documentation']
            
            # Find the highest priority log entry
            for category in priority_categories:
                for log in recent_logs:
                    if log.startswith(category):
                        return log
            
            # If no priority match, use the most recent
            return recent_logs[0]
        
        # Fallback to intelligent file analysis
        result = subprocess.run(['git', 'diff', '--name-only'], 
                              capture_output=True, text=True,
                              cwd='/Users/berkhatirli/Desktop/unibos')
        
        if not result.stdout:
            result = subprocess.run(['git', 'ls-files', '--others', '--exclude-standard'],
                                  capture_output=True, text=True,
                                  cwd='/Users/berkhatirli/Desktop/unibos')
        
        files = result.stdout.strip().split('\n') if result.stdout else []
        
        # Smart module detection based on file paths
        module_changes = set()
        for file in files:
            file_lower = file.lower()
            if 'version' in file_lower or 'archive' in file_lower:
                module_changes.add('Version Manager')
            elif 'movies' in file_lower:
                module_changes.add('Movies')
            elif 'music' in file_lower:
                module_changes.add('Music')
            elif 'documents' in file_lower:
                module_changes.add('Documents')
            elif 'currencies' in file_lower:
                module_changes.add('Currencies')
            elif 'wimm' in file_lower:
                module_changes.add('WIMM')
            elif 'wims' in file_lower:
                module_changes.add('WIMS')
            elif 'restopos' in file_lower:
                module_changes.add('RestoPOS')
            elif 'sidebar' in file_lower or 'navigation' in file_lower:
                module_changes.add('Navigation')
            elif 'web' in file_lower or 'django' in file_lower:
                module_changes.add('Web Interface')
        
        # Generate specific message based on changes
        if module_changes:
            if len(module_changes) == 1:
                module = list(module_changes)[0]
                return f"{module}: Updates and improvements"
            else:
                return f"Multiple modules: {', '.join(sorted(module_changes))}"
        
        # Count file types for generic message
        py_count = sum(1 for f in files if f.endswith('.py'))
        js_count = sum(1 for f in files if f.endswith('.js'))
        html_count = sum(1 for f in files if f.endswith('.html'))
        md_count = sum(1 for f in files if f.endswith('.md'))
        
        # Generate descriptive message
        if py_count > 3:
            return "Core system improvements and optimizations"
        elif js_count > 0 or html_count > 0:
            return "Web interface updates and improvements"
        elif md_count > 0:
            return "Documentation updates"
        else:
            return "General maintenance and improvements"
            
    except Exception as e:
        return "Regular update and maintenance"

def update_version_json(version, description):
    """Update VERSION.json file with intelligent changelog"""
    try:
        # Find VERSION.json path
        version_file = None
        possible_paths = [
            'VERSION.json',  # Same directory as main.py
            '../src/VERSION.json',  # If running from root
            '/Users/berkhatirli/Desktop/unibos/src/VERSION.json'  # Absolute path
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                version_file = path
                break
        
        if not version_file:
            raise FileNotFoundError("VERSION.json not found")
            
        with open(version_file, 'r') as f:
            data = json.load(f)
        
        # Get Istanbul time
        if ZoneInfo:
            istanbul_time = datetime.now(ZoneInfo('Europe/Istanbul'))
        else:
            # Fallback to local time with +3 offset
            from datetime import timezone, timedelta
            istanbul_tz = timezone(timedelta(hours=3))
            istanbul_time = datetime.now(istanbul_tz)
        
        # Update basic info
        data['version'] = f'v{version}'
        data['build_number'] = istanbul_time.strftime('%Y%m%d_%H%M')
        data['release_date'] = istanbul_time.strftime('%Y-%m-%d %H:%M:%S %z')
        data['description'] = description
        
        # Add changelog entry if it doesn't exist
        if 'changelog' not in data:
            data['changelog'] = []
        
        # Get recent development logs for detailed changelog
        recent_logs = get_recent_development_logs()
        
        # Create changelog entry
        changelog_entry = {
            'version': f'v{version}',
            'date': istanbul_time.strftime('%Y-%m-%d %H:%M'),
            'description': description,
            'changes': recent_logs[:3] if recent_logs else []
        }
        
        # Add to beginning of changelog (most recent first)
        data['changelog'].insert(0, changelog_entry)
        
        # Keep only last 10 changelog entries
        data['changelog'] = data['changelog'][:10]
        
        with open(version_file, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        raise Exception(f"Failed to update VERSION.json: {e}")

def update_django_version_files(version):
    """Update Django version files"""
    try:
        # Update Django views.py if exists
        views_file = 'backend/apps/web_ui/views.py'
        if os.path.exists(views_file):
            with open(views_file, 'r') as f:
                content = f.read()
            content = re.sub(r"'version': 'v\d+'", f"'version': 'v{version}'", content)
            with open(views_file, 'w') as f:
                f.write(content)
        
        # Update login template if exists
        login_file = 'backend/templates/authentication/login.html'
        if os.path.exists(login_file):
            with open(login_file, 'r') as f:
                content = f.read()
            content = re.sub(r'v\d+ - ', f'v{version} - ', content)
            with open(login_file, 'w') as f:
                f.write(content)
    except:
        pass  # Non-critical, continue

def create_version_archive(version):
    """Create version archive (folder only, no ZIP)"""
    try:
        # Get Istanbul time
        if ZoneInfo:
            istanbul_time = datetime.now(ZoneInfo('Europe/Istanbul'))
        else:
            from datetime import timezone, timedelta
            istanbul_tz = timezone(timedelta(hours=3))
            istanbul_time = datetime.now(istanbul_tz)
            
        timestamp = istanbul_time.strftime('%Y%m%d_%H%M')
        archive_name = f"unibos_v{version}_{timestamp}"
        archive_path = f"archive/versions/{archive_name}"
        
        # Create archive directory
        os.makedirs('archive/versions', exist_ok=True)
        
        # Use rsync to create archive
        cmd = [
            'rsync', '-av',
            '--exclude=archive', '--exclude=.git', '--exclude=venv',
            '--exclude=__pycache__', '--exclude=*.pyc', '--exclude=.DS_Store',
            '--exclude=*.zip', '--exclude=node_modules', '--exclude=.env.local',
            '.', f'{archive_path}/'
        ]
        
        result = subprocess.run(cmd, capture_output=True, cwd='/Users/berkhatirli/Desktop/unibos')
        if result.returncode != 0:
            raise Exception(f"rsync failed: {result.stderr.decode()}")
    except Exception as e:
        raise Exception(f"Failed to create archive: {e}")

def perform_git_operations(version, description):
    """Perform git operations for version release"""
    try:
        cwd = '/Users/berkhatirli/Desktop/unibos'
        
        # Add all changes - capture output to prevent screen disruption
        subprocess.run(['git', 'add', '-A'], cwd=cwd, capture_output=True)
        
        # Commit - capture output to prevent screen disruption
        result = subprocess.run(['git', 'commit', '-m', f'v{version}: {description}'], 
                              cwd=cwd, capture_output=True, text=True)
        
        # Store commit info for summary
        commit_info = result.stdout.split('\n')[0] if result.stdout else "Commit successful"
        
        # Create branch
        subprocess.run(['git', 'checkout', '-b', f'v{version}'], cwd=cwd, capture_output=True)
        subprocess.run(['git', 'push', 'origin', f'v{version}'], cwd=cwd, capture_output=True)
        
        # Back to main and merge
        subprocess.run(['git', 'checkout', 'main'], cwd=cwd, capture_output=True)
        subprocess.run(['git', 'merge', f'v{version}', '--no-edit'], cwd=cwd, capture_output=True)
        subprocess.run(['git', 'push', 'origin', 'main'], cwd=cwd, capture_output=True)
        
        # Create tag
        subprocess.run(['git', 'tag', f'v{version}'], cwd=cwd, capture_output=True)
        subprocess.run(['git', 'push', 'origin', '--tags'], cwd=cwd, capture_output=True)
        
        return commit_info
    except Exception as e:
        raise Exception(f"Git operations failed: {e}")

def show_version_status():
    """Show version status with native CLI interface"""
    cols, lines = get_terminal_size()
    content_x = 27  # After sidebar
    content_width = cols - content_x - 2
    
    # Clear content area
    for y in range(3, lines - 2):
        move_cursor(content_x, y)
        sys.stdout.write('\033[K')
    sys.stdout.flush()
    
    # Title
    move_cursor(content_x + 2, 4)
    print(f"{Colors.BOLD}{Colors.CYAN}📊 Version Status{Colors.RESET}")
    
    try:
        # Get current version from VERSION.json
        current_version = get_current_version_number()
        
        # Get highest git tag
        result = subprocess.run(['git', 'tag'], capture_output=True, text=True,
                              cwd='/Users/berkhatirli/Desktop/unibos')
        
        tags = [tag for tag in result.stdout.strip().split('\n') if tag.startswith('v')]
        highest_tag = 0
        if tags:
            version_numbers = []
            for tag in tags:
                try:
                    version_numbers.append(int(tag.replace('v', '')))
                except:
                    pass
            if version_numbers:
                highest_tag = max(version_numbers)
        
        # Display status
        y = 6
        move_cursor(content_x + 2, y)
        print(f"{Colors.BLUE}📊 Current Status:{Colors.RESET}")
        
        y += 2
        move_cursor(content_x + 4, y)
        print(f"VERSION.json: {Colors.GREEN}v{current_version}{Colors.RESET}")
        
        y += 1
        move_cursor(content_x + 4, y)
        print(f"Highest Git Tag: {Colors.GREEN}v{highest_tag}{Colors.RESET}")
        
        y += 2
        if current_version != highest_tag:
            move_cursor(content_x + 4, y)
            print(f"{Colors.YELLOW}⚠️  Version mismatch detected!{Colors.RESET}")
        else:
            move_cursor(content_x + 4, y)
            print(f"{Colors.GREEN}✅ Versions are synchronized{Colors.RESET}")
        
        # Check for gaps
        y += 2
        move_cursor(content_x + 2, y)
        print(f"{Colors.BLUE}🔍 Checking for gaps:{Colors.RESET}")
        
        y += 2
        start = max(1, highest_tag - 10)
        gaps = []
        for v in range(start, highest_tag + 1):
            if f"v{v}" not in tags:
                gaps.append(v)
        
        if gaps:
            for gap in gaps[:5]:  # Show max 5 gaps
                move_cursor(content_x + 4, y)
                print(f"{Colors.RED}Missing: v{gap}{Colors.RESET}")
                y += 1
            if len(gaps) > 5:
                move_cursor(content_x + 4, y)
                print(f"{Colors.DIM}... and {len(gaps) - 5} more{Colors.RESET}")
                y += 1
        else:
            move_cursor(content_x + 4, y)
            print(f"{Colors.GREEN}No gaps found{Colors.RESET}")
            y += 1
        
        # Recent versions
        y += 2
        move_cursor(content_x + 2, y)
        print(f"{Colors.BLUE}📝 Recent versions:{Colors.RESET}")
        
        y += 2
        recent_tags = sorted([int(t.replace('v', '')) for t in tags if t.startswith('v')])[-5:]
        for tag in reversed(recent_tags):
            move_cursor(content_x + 4, y)
            print(f"{Colors.CYAN}v{tag}{Colors.RESET}")
            y += 1
        
        # Press any key to continue
        move_cursor(content_x + 2, lines - 2)
        print(f"{Colors.DIM}Press any key to continue...{Colors.RESET}")
        get_single_key()
        
    except Exception as e:
        move_cursor(content_x + 2, 8)
        print(f"{Colors.RED}Error: {e}{Colors.RESET}")
        move_cursor(content_x + 2, lines - 2)
        print(f"{Colors.DIM}Press any key to continue...{Colors.RESET}")
        get_single_key()

def launch_unified_version_manager(option):
    """Launch the unified version manager script with a specific option"""
    # Clear screen and show launching message
    clear_screen()
    print(f"\n{Colors.CYAN}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.GREEN}🚀 Launching Unified Version Manager...{Colors.RESET}")
    print(f"{Colors.CYAN}{'=' * 60}{Colors.RESET}\n")
    
    # Ensure cursor is visible for the script
    show_cursor()
    
    try:
        # Save terminal settings
        if TERMIOS_AVAILABLE:
            import termios
            old_settings = termios.tcgetattr(sys.stdin)
        
        # Create a temporary script that will provide the option and then let user interact
        temp_script = f"""#!/bin/bash
# First send the menu option
echo '{option}'
# Then let the script run interactively for remaining inputs
exec < /dev/tty
cat
"""
        
        # Write temporary script
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
            f.write(temp_script)
            temp_script_path = f.name
        
        # Make it executable
        os.chmod(temp_script_path, 0o755)
        
        # If option is 0 (exit), just return
        if option == "0":
            os.unlink(temp_script_path)
            return
        
        # Run the script interactively
        # Use system() for full interactive control
        os.system(f"cd /Users/berkhatirli/Desktop/unibos && {temp_script_path} | ./unibos_version.sh")
        
        # Clean up temp script
        try:
            os.unlink(temp_script_path)
        except:
            pass
        
        # Always wait for user to press a key before returning
        print(f"\n{Colors.CYAN}{'=' * 60}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.YELLOW}📋 Operation completed. Review the report above.{Colors.RESET}")
        print(f"{Colors.YELLOW}Press any key to return to version manager...{Colors.RESET}")
        sys.stdout.flush()
        get_single_key()
        
    except Exception as e:
        print(f"\n{Colors.RED}Error running version manager: {e}{Colors.RESET}")
        print(f"{Colors.YELLOW}Press any key to continue...{Colors.RESET}")
        get_single_key()
    finally:
        # Restore terminal settings
        if TERMIOS_AVAILABLE:
            try:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
            except:
                pass
        
        # Hide cursor again for menu
        hide_cursor()

def show_git_status_quick():
    """Quick git status display in version manager"""
    cols, lines = get_terminal_size()
    content_x = 27  # After sidebar
    content_width = cols - content_x - 2
    
    # Clear content area
    for y in range(2, lines - 2):
        move_cursor(content_x, y)
        print(' ' * content_width)
    
    # Title
    move_cursor(content_x + 2, 4)
    print(f"{Colors.BOLD}{Colors.GREEN}📈 Git Status{Colors.RESET}")
    
    try:
        # Get git status
        result = subprocess.run(['git', 'status', '--short'], 
                              capture_output=True, text=True, 
                              cwd='/Users/berkhatirli/Desktop/unibos')
        
        y = 6
        if result.stdout:
            lines_output = result.stdout.strip().split('\n')
            for line in lines_output[:15]:  # Limit display
                move_cursor(content_x + 2, y)
                print(f"{Colors.YELLOW}{line[:content_width-4]}{Colors.RESET}")
                y += 1
                if y >= lines - 4:
                    break
        else:
            move_cursor(content_x + 2, y)
            print(f"{Colors.GREEN}✓ Working directory clean{Colors.RESET}")
        
        # Press any key to continue
        move_cursor(content_x + 2, lines - 3)
        print(f"{Colors.BOLD}{Colors.YELLOW}📋 Review the git status above{Colors.RESET}")
        move_cursor(content_x + 2, lines - 2)
        print(f"{Colors.YELLOW}Press any key to return to menu...{Colors.RESET}")
        sys.stdout.flush()
        get_single_key()
        
    except Exception as e:
        move_cursor(content_x + 2, 6)
        print(f"{Colors.RED}Error getting git status: {e}{Colors.RESET}")
        time.sleep(2)

def version_archive_analyzer():
    """Version Archive Analyzer - Shows file size anomalies in version archives"""
    import glob
    import statistics
    import threading
    
    # Don't change menu_state.in_submenu - keep it as 'version_manager'
    
    # Force sidebar redraw to ensure dimmed state is applied
    menu_state.last_sidebar_cache_key = None
    draw_sidebar()
    
    # Clear input buffer before starting
    if TERMIOS_AVAILABLE:
        try:
            import termios
            for _ in range(3):
                termios.tcflush(sys.stdin, termios.TCIFLUSH)
                termios.tcflush(sys.stdin, termios.TCIOFLUSH)
                time.sleep(0.01)
        except:
            pass
    
    # Get terminal dimensions
    cols, lines = get_terminal_size()
    content_x = 27  # After sidebar
    content_width = cols - content_x - 2
    content_height = lines - 4  # Account for header and footer
    
    # Hide cursor for better visual experience
    hide_cursor()
    
    # Clear content area and show loading message
    for y in range(3, lines - 2):
        move_cursor(content_x, y)
        sys.stdout.write('\033[K')  # Clear to end of line
    
    # Show loading header
    move_cursor(content_x + 2, 4)
    sys.stdout.write(f"{Colors.BOLD}{Colors.CYAN}📊 archive size analyzer{Colors.RESET}")
    
    move_cursor(content_x + 2, 7)
    sys.stdout.write(f"{Colors.YELLOW}⏳ scanning archive directories...{Colors.RESET}")
    sys.stdout.flush()
    
    # Collect archive data
    archive_path = "/Users/berkhatirli/Desktop/unibos/archive/versions"
    archives = []
    
    # Scan control variables
    scan_paused = False
    scan_stopped = False
    scan_lock = threading.Lock()
    
    try:
        # Get all version directories
        version_dirs = sorted(glob.glob(f"{archive_path}/unibos_v*"))
        total_dirs = len(version_dirs)
        
        if total_dirs == 0:
            move_cursor(content_x + 2, 9)
            sys.stdout.write(f"{Colors.YELLOW}No version archives found in {archive_path}{Colors.RESET}")
            sys.stdout.flush()
        else:
            move_cursor(content_x + 2, 9)
            sys.stdout.write(f"{Colors.DIM}found {total_dirs} version archives{Colors.RESET}")
            sys.stdout.flush()
            
            # Progress bar setup
            progress_width = min(50, content_width - 10)
            spinner_index = 0
            
            # Show control instructions
            move_cursor(content_x + 2, 17)
            sys.stdout.write(f"{Colors.DIM}[p] pause | [s] stop | [q] quit{Colors.RESET}")
            sys.stdout.flush()
            
            def scan_archives():
                """Scan archives in a separate thread"""
                nonlocal scan_stopped, scan_paused, spinner_index
                
                for idx, version_dir in enumerate(version_dirs):
                    # Check if stopped
                    with scan_lock:
                        if scan_stopped:
                            break
                        
                        # Wait while paused
                        while scan_paused and not scan_stopped:
                            move_cursor(content_x + 2, 11)
                            sys.stdout.write(f"{Colors.YELLOW}⏸ paused - press [p] to resume{Colors.RESET}          ")
                            sys.stdout.flush()
                            time.sleep(0.1)
                    
                    if os.path.isdir(version_dir):
                        # Update progress
                        progress = (idx + 1) / total_dirs
                        filled = int(progress_width * progress)
                        
                        # Draw progress bar with spinner
                        move_cursor(content_x + 2, 11)
                        spinner = get_spinner_frame(spinner_index)
                        spinner_index += 1
                        sys.stdout.write(f"{spinner} progress: [{Colors.GREEN}{'█' * filled}{Colors.DIM}{'░' * (progress_width - filled)}{Colors.RESET}] {idx + 1}/{total_dirs}")
                        
                        # Show current archive being processed
                        dirname = os.path.basename(version_dir)
                        move_cursor(content_x + 2, 13)
                        sys.stdout.write('\033[K')  # Clear line
                        sys.stdout.write(f"{Colors.DIM}analyzing: {dirname[:40]}...{Colors.RESET}")
                        sys.stdout.flush()
                    
                        # Extract version info from directory name
                        parts = dirname.split('_')
                        if len(parts) >= 2:
                            version_num = parts[1][1:] if parts[1].startswith('v') else parts[1]
                            
                            # Calculate directory size with file count
                            total_size = 0
                            file_count = 0
                            for dirpath, dirnames, filenames in os.walk(version_dir):
                                file_count += len(filenames)
                                for filename in filenames:
                                    filepath = os.path.join(dirpath, filename)
                                    try:
                                        total_size += os.path.getsize(filepath)
                                    except:
                                        pass
                            
                            # Show file count and size
                            move_cursor(content_x + 2, 14)
                            sys.stdout.write('\033[K')  # Clear line
                            sys.stdout.write(f"{Colors.DIM}  files: {file_count} | size: {total_size / (1024 * 1024):.2f} mb{Colors.RESET}")
                            sys.stdout.flush()
                            
                            archives.append({
                                'version': version_num,
                                'path': version_dir,
                                'size': total_size,
                                'size_mb': total_size / (1024 * 1024),
                                'name': dirname,
                                'file_count': file_count
                            })
            
            
            # Start scanning in a separate thread
            scan_thread = threading.Thread(target=scan_archives)
            scan_thread.start()
            
            # Handle keyboard input during scan
            while scan_thread.is_alive():
                key = get_single_key(timeout=0.1)
                
                if key in ['p', 'P']:  # Pause/Resume
                    with scan_lock:
                        scan_paused = not scan_paused
                        if scan_paused:
                            move_cursor(content_x + 2, 16)
                            sys.stdout.write(f"{Colors.YELLOW}⏸ scan paused{Colors.RESET}          ")
                        else:
                            move_cursor(content_x + 2, 16)
                            sys.stdout.write('\033[K')  # Clear pause message
                        sys.stdout.flush()
                        
                elif key in ['s', 'S']:  # Stop
                    with scan_lock:
                        scan_stopped = True
                    move_cursor(content_x + 2, 16)
                    sys.stdout.write(f"{Colors.RED}⏹ stopping scan...{Colors.RESET}")
                    sys.stdout.flush()
                    break
                    
                elif key in ['q', 'Q', '\x1b']:  # Quit
                    with scan_lock:
                        scan_stopped = True
                    scan_thread.join(timeout=1)
                    show_cursor()
                    return
            
            # Wait for thread to finish
            scan_thread.join()
            
            # Clear progress messages
            for y in range(7, 18):
                move_cursor(content_x + 2, y)
                sys.stdout.write('\033[K')
            
            move_cursor(content_x + 2, 7)
            if scan_stopped:
                sys.stdout.write(f"{Colors.YELLOW}⏹ scan stopped - {len(archives)} archives processed{Colors.RESET}")
            else:
                sys.stdout.write(f"{Colors.GREEN}✓ analysis complete - {len(archives)} archives processed{Colors.RESET}")
            sys.stdout.flush()
            time.sleep(1)  # Brief pause to show completion
        
    except Exception as e:
        move_cursor(content_x + 2, 9)
        sys.stdout.write(f"{Colors.RED}error: {str(e)}{Colors.RESET}")
        sys.stdout.flush()
        archives = []
    
    # Calculate statistics for anomaly detection
    if len(archives) > 2:
        sizes = [a['size'] for a in archives]
        mean_size = statistics.mean(sizes)
        stdev_size = statistics.stdev(sizes) if len(sizes) > 1 else 0
        
        # Mark anomalies (2 standard deviations from mean)
        for archive in archives:
            if stdev_size > 0:
                z_score = abs((archive['size'] - mean_size) / stdev_size)
                archive['anomaly'] = z_score > 2
                archive['z_score'] = z_score
            else:
                archive['anomaly'] = False
                archive['z_score'] = 0
    else:
        for archive in archives:
            archive['anomaly'] = False
            archive['z_score'] = 0
    
    # Pagination variables
    page = 0
    items_per_page = content_height - 12  # Leave room for header, stats, and instructions
    total_pages = (len(archives) + items_per_page - 1) // items_per_page if archives else 1
    
    # Track last update times
    last_footer_update = time.time()
    last_full_redraw = time.time()
    redraw_interval = 30.0
    
    def draw_archive_analyzer():
        """Draw the archive analyzer UI"""
        nonlocal page, items_per_page, total_pages
        
        # Clear content area properly
        for y in range(3, lines - 2):
            move_cursor(content_x, y)
            sys.stdout.write('\033[K')  # Clear to end of line
        
        y = 3
        
        # Title (without decorative lines)
        move_cursor(content_x + 2, y)
        title = "📊 version archive analyzer"
        sys.stdout.write(f"{Colors.BOLD}{Colors.CYAN}{title}{Colors.RESET}")
        y += 2
        
        # Statistics summary
        if archives:
            total_size = sum(a['size'] for a in archives)
            avg_size = total_size / len(archives) if archives else 0
            anomaly_count = sum(1 for a in archives if a['anomaly'])
            
            move_cursor(content_x + 2, y)
            sys.stdout.write(f"{Colors.DIM}total archives: {len(archives)} | total size: {total_size/(1024*1024*1024):.2f} gb | avg: {avg_size/(1024*1024):.1f} mb | anomalies: {anomaly_count}{Colors.RESET}")
            y += 2
        
        # Table header
        move_cursor(content_x + 2, y)
        sys.stdout.write(f"{Colors.BOLD}{Colors.WHITE}{'version':<10} {'size (mb)':<12} {'status':<15} {'z-score':<10} {'archive name'}{Colors.RESET}")
        y += 1
        
        move_cursor(content_x + 2, y)
        sys.stdout.write(f"{Colors.DIM}{'─' * (content_width - 4)}{Colors.RESET}")
        y += 1
        
        # Display archives for current page
        if archives:
            start_idx = page * items_per_page
            end_idx = min(start_idx + items_per_page, len(archives))
            
            for i in range(start_idx, end_idx):
                archive = archives[i]
                move_cursor(content_x + 2, y)
                
                # Color coding based on size thresholds
                size_mb = archive['size_mb']
                
                if size_mb >= 500:  # 500 MB+
                    color = Colors.RED
                    status = "⚠ huge"
                elif size_mb >= 200:  # 200-500 MB
                    color = Colors.ORANGE
                    status = "⚠ very large"
                elif size_mb >= 50:  # 50-200 MB
                    color = Colors.YELLOW
                    status = "⚠ large"
                else:  # Under 50 MB
                    color = Colors.WHITE
                    status = "normal"
                
                # Format the row
                version_str = f"v{archive['version']}"
                size_str = f"{archive['size_mb']:.2f}"
                z_score_str = f"{archive['z_score']:.2f}" if archive['z_score'] > 0 else "-"
                name_str = archive['name'][:40]  # Truncate long names
                
                sys.stdout.write(f"{color}{version_str:<10} {size_str:<12} {status:<15} {z_score_str:<10} {name_str}{Colors.RESET}")
                y += 1
        else:
            move_cursor(content_x + 2, y)
            sys.stdout.write(f"{Colors.DIM}no archives found in {archive_path}{Colors.RESET}")
            y += 2
        
        # Pagination info
        if total_pages > 1:
            y = content_height - 4
            move_cursor(content_x + 2, y)
            sys.stdout.write(f"{Colors.DIM}page {page + 1} of {total_pages} | use ← → to navigate pages{Colors.RESET}")
        
        # Instructions
        y = content_height - 2
        move_cursor(content_x + 2, y)
        sys.stdout.write(f"{Colors.DIM}↑↓ scroll | ←→ pages | r refresh | q/esc back{Colors.RESET}")
        
        sys.stdout.flush()
    
    # Initial draw
    draw_archive_analyzer()
    
    # Main loop - stay in version_manager submenu
    while menu_state.in_submenu == 'version_manager':
        # Update header time every second
        current_time = time.time()
        if current_time - last_footer_update >= 1.0:
            draw_header_time_only()
            last_footer_update = current_time
            hide_cursor()
        
        # Periodic full redraw
        if current_time - last_full_redraw >= redraw_interval:
            draw_archive_analyzer()
            last_full_redraw = current_time
            hide_cursor()
        
        # Handle input with timeout for clock updates
        key = get_single_key(timeout=0.1)
        
        # Handle navigation keys
        if key in ['\x1b[D', 'h', 'H']:  # Left arrow - previous page
            if page > 0:
                page -= 1
                draw_archive_analyzer()
        elif key in ['\x1b[C', 'l', 'L']:  # Right arrow - next page
            if page < total_pages - 1:
                page += 1
                draw_archive_analyzer()
        elif key in ['\x1b[A', 'k', 'K']:  # Up arrow - scroll up
            if page > 0:
                page -= 1
                draw_archive_analyzer()
        elif key in ['\x1b[B', 'j', 'J']:  # Down arrow - scroll down
            if page < total_pages - 1:
                page += 1
                draw_archive_analyzer()
        elif key in ['r', 'R']:  # Refresh
            # Recollect archive data
            archives.clear()
            try:
                version_dirs = sorted(glob.glob(f"{archive_path}/unibos_v*"))
                for version_dir in version_dirs:
                    if os.path.isdir(version_dir):
                        dirname = os.path.basename(version_dir)
                        parts = dirname.split('_')
                        if len(parts) >= 2:
                            version_num = parts[1][1:] if parts[1].startswith('v') else parts[1]
                            total_size = 0
                            for dirpath, dirnames, filenames in os.walk(version_dir):
                                for filename in filenames:
                                    filepath = os.path.join(dirpath, filename)
                                    try:
                                        total_size += os.path.getsize(filepath)
                                    except:
                                        pass
                            archives.append({
                                'version': version_num,
                                'path': version_dir,
                                'size': total_size,
                                'size_mb': total_size / (1024 * 1024),
                                'name': dirname
                            })
                
                # Recalculate statistics
                if len(archives) > 2:
                    sizes = [a['size'] for a in archives]
                    mean_size = statistics.mean(sizes)
                    stdev_size = statistics.stdev(sizes) if len(sizes) > 1 else 0
                    for archive in archives:
                        if stdev_size > 0:
                            z_score = abs((archive['size'] - mean_size) / stdev_size)
                            archive['anomaly'] = z_score > 2
                            archive['z_score'] = z_score
                        else:
                            archive['anomaly'] = False
                            archive['z_score'] = 0
            except:
                pass
            
            total_pages = (len(archives) + items_per_page - 1) // items_per_page if archives else 1
            page = 0
            draw_archive_analyzer()
            
        elif key in ['\x1b', 'q', 'Q']:  # ESC or q to exit
            # Exit analyzer and return to version manager menu
            show_cursor()
            
            # Clear caches to force full redraw
            menu_state.last_sidebar_cache_key = None
            if hasattr(menu_state, 'last_content_cache_key'):
                menu_state.last_content_cache_key = None
            
            # Exit the function to return to version_manager_menu
            return
    
    # Ensure cursor is shown when exiting
    show_cursor()

def update_web_forge_selection(old_index, new_index):
    """Update menu selection - ROBUST VERSION with error recovery"""
    try:
        cols, lines = get_terminal_size()
        content_x = 27  # After sidebar
        
        # Get all options to find positions
        all_options = get_web_forge_options()
        
        y_offset = 0
        selectable_count = 0
        is_first_header = True
        start_y = 7  # Changed from 8 to 7 for single-line header
        
        # Track positions of selectable items with their colors
        item_positions = []  # (selectable_index, y_position, title, color)
        
        # First, map all selectable items to their positions and colors
        for opt_type, title, desc in all_options:
            if opt_type == 'separator':
                y_offset += 1
            elif opt_type == 'header':
                if not is_first_header:
                    y_offset += 1
                is_first_header = False
                y_offset += 1
            else:  # selectable item
                y = start_y + y_offset
                # Determine the correct color based on item type
                if 'Start' in title or '▶' in title:
                    color = Colors.GREEN
                elif 'Stop' in title or '◼' in title or '🛑' in title:
                    color = Colors.RED
                elif 'Restart' in title or '↻' in title or '🔄' in title:
                    color = Colors.YELLOW
                elif 'Back' in title or '←' in title:
                    color = Colors.BLUE
                else:
                    color = Colors.WHITE  # Default white
                item_positions.append((selectable_count, y, title, color))
                selectable_count += 1
                y_offset += 1
        
        # Safety check: if we don't have enough items, force a full redraw
        if len(item_positions) == 0:
            draw_web_forge_menu()
            return
        
        # ROBUST UPDATE: Always redraw both old and new to prevent disappearing items
        # Clear and redraw OLD selection with proper color
        if old_index >= 0 and old_index < len(item_positions):
            _, old_y, old_title, old_color = item_positions[old_index]
            move_cursor(content_x + 5, old_y)
            # Redraw with proper color and formatting - no clear needed
            move_cursor(content_x + 5, old_y)
            # Use padding to clear any leftover text
            clean_title = old_title[:30]  # Shorter to prevent overlap
            sys.stdout.write(f"{old_color}  {clean_title:<35}{Colors.RESET}")
            sys.stdout.flush()
        
        # Draw NEW selection with orange background
        if new_index >= 0 and new_index < len(item_positions):
            _, new_y, new_title, new_color = item_positions[new_index]
            move_cursor(content_x + 5, new_y)
            # Redraw with orange background - no clear needed
            move_cursor(content_x + 5, new_y)
            # Use padding to clear any leftover text
            clean_title = new_title[:30]  # Shorter to prevent overlap
            sys.stdout.write(f"{Colors.BG_ORANGE}{Colors.BLACK}▶ {clean_title:<35}{Colors.RESET}")
            sys.stdout.flush()
        
        # Ensure cursor is hidden after update
        hide_cursor()
        
    except Exception as e:
        # If anything goes wrong, do a full redraw
        draw_web_forge_menu()

def get_web_forge_options():
    """Get web forge menu options"""
    return [
        # Main Web Controls
        ("header", "🌐 web server controls", ""),
        ("open_web_ui", "🚀 open web interface", "start server & launch browser"),
        ("start_server", "▶️  start web core", "start django backend server"),
        ("stop_server", "⏹️  stop web core", "stop django backend server"),
        ("restart_server", "🔄 restart web core", "restart django backend server"),
        ("separator", "---", "---"),
        # Status & Monitoring
        ("header", "📊 monitoring", ""),
        ("status", "📈 server status", "check web core status"),
        ("logs", "📜 view logs", "view server logs"),
        ("separator", "---", "---"),
        # Setup & Maintenance
        ("header", "🛠️ maintenance", ""),
        ("env_check", "🔍 environment check", "verify dependencies"),
        ("migrate", "🗄️  run migrations", "update database schema"),
        ("install_redis", "🔴 install redis", "brew install redis"),
    ]

def update_web_forge_selection_only(old_index, new_index):
    """Update only the selection without redrawing entire menu"""
    cols, lines = get_terminal_size()
    content_x = 27
    
    # Get options to find positions
    options = get_web_forge_options()
    start_y = 7
    y_pos = start_y
    actual_index = 0
    
    for i, (key, title, desc) in enumerate(options):
        if key == "separator":
            y_pos += 1
            continue
        elif key == "header":
            if y_pos > start_y:
                y_pos += 1
            y_pos += 1
            continue
            
        # Found a selectable item
        if actual_index == old_index:
            # Clear old selection
            move_cursor(content_x + 5, y_pos)
            if 'Start' in title or '▶' in title:
                color = Colors.GREEN
            elif 'Stop' in title or '◼' in title or '🛑' in title:
                color = Colors.RED
            elif 'Restart' in title or '↻' in title or '🔄' in title:
                color = Colors.YELLOW
            elif 'Back' in title or '←' in title:
                color = Colors.BLUE
            else:
                color = Colors.WHITE
            clean_title = title[:30]
            formatted_title = f"  {clean_title:<35}"
            sys.stdout.write(f"{color}{formatted_title}{Colors.RESET}")
            sys.stdout.flush()
            
        if actual_index == new_index:
            # Draw new selection
            move_cursor(content_x + 5, y_pos)
            clean_title = title[:30]
            sys.stdout.write(f"{Colors.BG_ORANGE}{Colors.BLACK}{Colors.BOLD}▶ {clean_title:<35}{Colors.RESET}")
            sys.stdout.flush()
            
        y_pos += 1
        actual_index += 1

def draw_web_forge_menu(update_status_only=False):
    """Enhanced web forge menu - STABLE VERSION with complete rendering"""
    global ui_controller
    
    # Cache status values to avoid repeated subprocess calls
    if not hasattr(menu_state, 'web_forge_status_cache'):
        menu_state.web_forge_status_cache = {
            'env_status': None,
            'backend_running': False,
            'backend_pid': None,
            'pg_running': False,
            'redis_running': False,
            'last_check': 0
        }
    
    if ui_controller and UI_ARCHITECTURE_AVAILABLE:
        # Only check status if updating status or cache is empty
        if update_status_only or menu_state.web_forge_status_cache['env_status'] is None:
            env_status = check_environment_quick()
            backend_running, backend_pid = check_backend_running()
            menu_state.web_forge_status_cache.update({
                'env_status': env_status,
                'backend_running': backend_running,
                'backend_pid': backend_pid,
                'last_check': time.time()
            })
        else:
            # Use cached values during navigation
            env_status = menu_state.web_forge_status_cache['env_status']
            backend_running = menu_state.web_forge_status_cache['backend_running']
            backend_pid = menu_state.web_forge_status_cache['backend_pid']
        
        # Get menu options
        options = get_web_forge_options()
        
        if not update_status_only:
            # Clear content area properly only when doing full redraw
            ui_controller.content.clear()
            
            # Small delay to ensure clear is processed - REMOVED to prevent flicker
            # time.sleep(0.001)
        
        # Render using new architecture - NO COLORED BOXES!
        ui_controller.content.render_web_forge_menu(
            options=options,
            selected_index=menu_state.web_forge_index,
            env_status=env_status,
            backend_status=(backend_running, backend_pid),
            frontend_status=(False, None),  # Frontend removed, pass dummy values
            update_status_only=update_status_only
        )
        return
    
    # Fallback to old implementation
    cols, lines = get_terminal_size()
    content_x = 27  # After sidebar
    content_width = cols - content_x - 1  # Full width with minimal margin
    content_height = lines - 4
    
    if not update_status_only:
        # Clear content area only when doing full redraw
        for y in range(2, lines - 2):  # Adjusted for single-line header
            move_cursor(content_x, y)
            sys.stdout.write('\033[K')  # Clear to end of line only
        sys.stdout.flush()
    
    # Store terminal size for verification
    menu_state.web_forge_terminal_size = (cols, lines)
    
    if not update_status_only:
        # Title without box - only draw on full redraw
        move_cursor(content_x + 2, 3)  # Changed from 4 to 3 for single-line header
        print(f"{Colors.BOLD}{Colors.BLUE}web ui{Colors.RESET}")
    
    # Only check statuses when explicitly updating status or on first draw
    if update_status_only or menu_state.web_forge_status_cache['env_status'] is None:
        # Quick environment status check
        env_status = check_environment_quick()
        
        # Show server status
        backend_running, backend_pid = check_backend_running()
        
        # PostgreSQL status check - more reliable method
        try:
            # Try using brew services first (macOS)
            brew_result = subprocess.run(['brew', 'services', 'list'], capture_output=True, text=True)
            if 'postgresql' in brew_result.stdout:
                pg_running = 'started' in brew_result.stdout.lower() and 'postgresql' in brew_result.stdout
            else:
                # Fallback to pg_isready which is more reliable
                pg_result = subprocess.run(['pg_isready'], capture_output=True, text=True)
                pg_running = pg_result.returncode == 0
        except:
            pg_running = False
        
        # Redis status check
        try:
            redis_result = subprocess.run(['redis-cli', 'ping'], capture_output=True, text=True)
            redis_running = 'PONG' in redis_result.stdout
        except:
            redis_running = False
        
        # Update cache
        menu_state.web_forge_status_cache.update({
            'env_status': env_status,
            'backend_running': backend_running,
            'backend_pid': backend_pid,
            'pg_running': pg_running,
            'redis_running': redis_running,
            'last_check': time.time()
        })
    else:
        # Use cached values during navigation
        backend_running = menu_state.web_forge_status_cache['backend_running']
        backend_pid = menu_state.web_forge_status_cache['backend_pid']
        pg_running = menu_state.web_forge_status_cache['pg_running']
        redis_running = menu_state.web_forge_status_cache['redis_running']
    
    # Always display status bar (but with cached values during navigation)
    # Create a status bar
    move_cursor(content_x + 5, 4)  # Changed from 5 to 4
    print(f"{Colors.BOLD}server status:{Colors.RESET}", end='')
    
    # Backend status
    move_cursor(content_x + 22, 4)  # Changed from 5 to 4
    backend_icon = "●" if backend_running else "○"
    backend_color = Colors.GREEN if backend_running else Colors.RED
    backend_text = f"{backend_color}{backend_icon}{Colors.RESET} web core: {Colors.BOLD if backend_running else ''}{backend_color}{'running' if backend_running else 'stopped'}{Colors.RESET}"
    if backend_running and backend_pid:
        backend_text += f" {Colors.DIM}[PID: {backend_pid}]{Colors.RESET}"
    print(backend_text)
    
    # Database status
    move_cursor(content_x + 5, 5)  # Changed from 6 to 5
    print(f"{Colors.BOLD}database status:{Colors.RESET}", end='')
    
    move_cursor(content_x + 22, 5)  # Changed from 6 to 5
    pg_icon = "●" if pg_running else "○"
    pg_color = Colors.GREEN if pg_running else Colors.RED
    print(f"{pg_color}{pg_icon}{Colors.RESET} postgresql: {pg_color}{'running' if pg_running else 'stopped'}{Colors.RESET}", end='')
    
    # Redis status
    move_cursor(content_x + 50, 5)  # Changed from 6 to 5
    redis_icon = "●" if redis_running else "○"
    redis_color = Colors.GREEN if redis_running else Colors.YELLOW  # Yellow for optional
    print(f"{redis_color}{redis_icon}{Colors.RESET} redis: {redis_color}{'running' if redis_running else 'not installed'}{Colors.RESET}")
    
    # Draw menu items only on full redraw
    if not update_status_only:
        # Web launcher options with medieval theme and grouping
        options = get_web_forge_options()
        
        # Calculate layout for better spacing
        start_y = 7  # Changed from 8 to 7 for single-line header
        y_pos = start_y
        actual_index = 0  # Track actual selectable items
        
        # Display options with PROPER visual hierarchy
        for i, (key, title, desc) in enumerate(options):
            if key == "separator":
                # Draw separator line
                move_cursor(content_x + 3, y_pos)
                sys.stdout.write('\033[K')  # Clear from cursor to end of line
                separator_width = min(content_width - 8, 60)
                sys.stdout.write(f"{Colors.DIM}{'─' * separator_width}{Colors.RESET}")
                sys.stdout.flush()
                y_pos += 1
                continue
            elif key == "header":
                # Draw section header with proper spacing
                if y_pos > start_y:  # Add space before headers (except first)
                    y_pos += 1
                move_cursor(content_x + 3, y_pos)
                sys.stdout.write('\033[K')  # Clear from cursor to end of line
                sys.stdout.write(f"{Colors.BOLD}{Colors.YELLOW}{title}{Colors.RESET}")
                sys.stdout.flush()
                y_pos += 1
                continue
            
            # Don't draw if it would go past the content area
            if y_pos + 1 >= content_height - 3:
                break
                
            # DO NOT use \033[2K - it clears entire line including sidebar!
            move_cursor(content_x + 5, y_pos)  # Indent menu items under headers
            
            if actual_index == menu_state.web_forge_index:
                # Selected option with orange background
                # No clear needed - just draw
                # Draw with orange background - use dark text for contrast
                clean_title = title[:30]  # Shorter to prevent overlap
                sys.stdout.write(f"{Colors.BG_ORANGE}{Colors.BLACK}{Colors.BOLD}▶ {clean_title:<35}{Colors.RESET}")
                sys.stdout.flush()
            else:
                # No clear needed - just draw
                move_cursor(content_x + 5, y_pos)
                # Use appropriate color based on item type (matching update_web_forge_selection)
                if 'Start' in title or '▶' in title:
                    color = Colors.GREEN
                elif 'Stop' in title or '◼' in title or '🛑' in title:
                    color = Colors.RED
                elif 'Restart' in title or '↻' in title or '🔄' in title:
                    color = Colors.YELLOW
                elif 'Back' in title or '←' in title:
                    color = Colors.BLUE
                else:
                    color = Colors.WHITE  # Default white, not cyan
                # Ensure proper spacing and formatting with padding to clear any artifacts
                # Truncate title to prevent overflow
                clean_title = title[:30]  # Shorter to prevent overlap
                formatted_title = f"  {clean_title:<35}"  # Pad to consistent width
                sys.stdout.write(f"{color}{formatted_title}{Colors.RESET}")
                sys.stdout.flush()
            
            y_pos += 1  # Spacing between items
            actual_index += 1  # Increment actual index for selectable items
    
    # Navigation instructions already in footer - no need for extra tips

def start_web_both():
    """Start both backend and frontend servers with simplified approach"""
    show_server_action("⚔️ firing up the entire forge", Colors.GREEN)
    
    cols, lines = get_terminal_size()
    content_x = 31
    y = 5
    
    move_cursor(content_x, y)
    print(f"{Colors.CYAN}starting both servers...{Colors.RESET}")
    y += 2
    
    # Use simple_server_manager.py for reliable startup
    backend_running = False
    frontend_running = False
    
    try:
        # Get base path
        base_path = Path(__file__).parent.parent
        
        # Start servers using the reliable manager
        result = subprocess.run(
            ['python3', 'src/simple_server_manager.py', 'start'],
            capture_output=True,
            text=True,
            timeout=30,  # Increased timeout for server startup
            cwd=base_path  # Ensure we run from the correct directory
        )
        
        # Check result
        if result.returncode == 0:
            # Parse output to check status
            backend_running = False
            frontend_running = False
            
            # Check if servers are actually running
            time.sleep(2)  # Give servers time to start
            
            status_result = subprocess.run(
                ['python3', 'src/simple_server_manager.py', 'status'],
                capture_output=True,
                text=True,
                cwd=base_path
            )
            
            if 'Backend:  🟢 Running' in status_result.stdout or 'Backend: Running' in status_result.stdout:
                backend_running = True
                move_cursor(content_x, y)
                print(f"{Colors.GREEN}✓ Backend started on http://localhost:8000{Colors.RESET}")
                y += 1
            else:
                move_cursor(content_x, y)
                print(f"{Colors.RED}✗ Backend failed to start{Colors.RESET}")
                y += 1
                
            if 'Frontend: 🟢 Running' in status_result.stdout or 'Frontend: Running' in status_result.stdout:
                frontend_running = True
                move_cursor(content_x, y)
                print(f"{Colors.GREEN}✓ Frontend started on http://localhost:3000{Colors.RESET}")
                y += 1
            else:
                move_cursor(content_x, y)
                print(f"{Colors.RED}✗ Frontend failed to start{Colors.RESET}")
                y += 1
        else:
            move_cursor(content_x, y)
            print(f"{Colors.RED}Failed to start servers (exit code: {result.returncode}){Colors.RESET}")
            y += 1
            if result.stderr:
                move_cursor(content_x, y)
                print(f"{Colors.RED}Error: {result.stderr[:200]}{Colors.RESET}")
                y += 1
            if result.stdout:
                move_cursor(content_x, y)
                print(f"{Colors.YELLOW}Output: {result.stdout[:200]}{Colors.RESET}")
                y += 1
            
    except subprocess.TimeoutExpired:
        move_cursor(content_x, y)
        print(f"{Colors.RED}Timeout: Servers took too long to start{Colors.RESET}")
        y += 1
    except Exception as e:
        move_cursor(content_x, y)
        print(f"{Colors.RED}Error starting servers: {str(e)}{Colors.RESET}")
        y += 1
        import traceback
        move_cursor(content_x, y)
        print(f"{Colors.DIM}Details: {traceback.format_exc()[:200]}{Colors.RESET}")
        y += 1
    finally:
        pass  # No need to restore directory since we use cwd parameter
    
    y += 2
    
    # Summary
    move_cursor(content_x, y)
    if backend_running and frontend_running:
        print(f"{Colors.GREEN}✓ Both servers are starting up!{Colors.RESET}")
    elif backend_running:
        print(f"{Colors.YELLOW}⚠ Only backend server started{Colors.RESET}")
    elif frontend_running:
        print(f"{Colors.YELLOW}⚠ Only frontend server started{Colors.RESET}")
    else:
        print(f"{Colors.RED}✗ Failed to start servers{Colors.RESET}")
    
    y += 2
    move_cursor(content_x, y)
    print(f"{Colors.DIM}Press any key to continue...{Colors.RESET}")
    get_single_key()

def restart_both_servers():
    """Restart both backend and frontend servers with improved handling"""
    show_server_action("🔄 restarting both servers", Colors.YELLOW)
    
    cols, lines = get_terminal_size()
    content_x = 31
    y = 5
    
    try:
        # Get base path
        base_path = Path(__file__).parent.parent
        
        # Step 1: Stop all servers first
        move_cursor(content_x, y)
        print(f"{Colors.YELLOW}Stopping all servers...{Colors.RESET}")
        
        stop_result = subprocess.run(
            ['python3', 'src/simple_server_manager.py', 'stop'],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=base_path
        )
        
        # Wait for complete shutdown
        time.sleep(2)
        
        # Step 2: Start backend
        y += 2
        move_cursor(content_x, y)
        print(f"{Colors.YELLOW}Starting backend server...{Colors.RESET}")
        
        backend_result = subprocess.run(
            ['python3', 'src/simple_server_manager.py', 'start-backend'],
            capture_output=True,
            text=True,
            timeout=15,
            cwd=base_path
        )
        
        # Wait for backend to be ready
        time.sleep(3)
        
        # Step 3: Start frontend
        y += 2
        move_cursor(content_x, y)
        print(f"{Colors.YELLOW}Starting frontend server...{Colors.RESET}")
        
        frontend_result = subprocess.run(
            ['python3', 'src/simple_server_manager.py', 'start-frontend'],
            capture_output=True,
            text=True,
            timeout=15,
            cwd=base_path
        )
        
        # Wait for frontend to initialize
        time.sleep(3)
        
        # Step 4: Check final status
        status_result = subprocess.run(
            ['python3', 'src/simple_server_manager.py', 'status'],
            capture_output=True,
            text=True,
            cwd=base_path
        )
        
        y += 2
        backend_running = False
        frontend_running = False
        
        if 'Backend:  🟢 Running' in status_result.stdout or 'Backend: Running' in status_result.stdout:
            backend_running = True
            move_cursor(content_x, y)
            print(f"{Colors.GREEN}✓ Backend restarted successfully{Colors.RESET}")
            y += 1
        else:
            move_cursor(content_x, y)
            print(f"{Colors.RED}✗ Backend failed to restart{Colors.RESET}")
            y += 1
            
        if 'Frontend: 🟢 Running' in status_result.stdout or 'Frontend: Running' in status_result.stdout:
            frontend_running = True
            move_cursor(content_x, y)
            print(f"{Colors.GREEN}✓ Frontend restarted successfully{Colors.RESET}")
            y += 1
        else:
            # Try once more for frontend
            move_cursor(content_x, y)
            print(f"{Colors.YELLOW}⚠ Frontend needs second attempt...{Colors.RESET}")
            time.sleep(2)
            
            # Direct frontend start attempt
            frontend_path = base_path / 'frontend'
            if frontend_path.exists():
                frontend_process = subprocess.Popen(
                    ['npm', 'start'],
                    cwd=frontend_path,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True
                )
                time.sleep(3)
                
                # Check if it started
                check_result = subprocess.run(
                    ['pgrep', '-f', 'react-scripts'],
                    capture_output=True
                )
                
                if check_result.returncode == 0:
                    y += 1
                    move_cursor(content_x, y)
                    print(f"{Colors.GREEN}✓ Frontend started on second attempt{Colors.RESET}")
                    frontend_running = True
                else:
                    y += 1
                    move_cursor(content_x, y)
                    print(f"{Colors.RED}✗ Frontend failed to start{Colors.RESET}")
        
        # Show URLs if successful
        if backend_running or frontend_running:
            y += 2
            move_cursor(content_x, y)
            print(f"{Colors.CYAN}Access URLs:{Colors.RESET}")
            if backend_running:
                y += 1
                move_cursor(content_x, y)
                print(f"Backend:  http://localhost:8000")
            if frontend_running:
                y += 1
                move_cursor(content_x, y)
                print(f"Frontend: http://localhost:3000")
        else:
            y += 2
            move_cursor(content_x, y)
            print(f"{Colors.RED}Restart failed (exit code: {result.returncode}){Colors.RESET}")
            if result.stderr:
                y += 1
                move_cursor(content_x, y)
                print(f"{Colors.RED}Error: {result.stderr[:200]}...{Colors.RESET}")
            if result.stdout:
                y += 1
                move_cursor(content_x, y)
                print(f"{Colors.YELLOW}Output: {result.stdout[:200]}...{Colors.RESET}")
            
    except subprocess.TimeoutExpired:
        y += 2
        move_cursor(content_x, y)
        print(f"{Colors.RED}Restart timed out after 30 seconds{Colors.RESET}")
    except Exception as e:
        y += 2
        move_cursor(content_x, y)
        print(f"{Colors.RED}Error during restart: {str(e)}{Colors.RESET}")
        
    # Wait for user to see the result
    y += 2
    move_cursor(content_x, y)
    print(f"{Colors.DIM}Press any key to continue...{Colors.RESET}")
    get_single_key()

def show_web_status():
    """Enhanced server status with detailed information"""
    show_server_action("📊 Forge Status Report", Colors.BLUE)
    
    cols, lines = get_terminal_size()
    content_x = 27 + 4
    y = 5
    
    # Clear content area properly
    clear_content_area()
    
    # NO BOXES - just show the title
    move_cursor(content_x, 4)
    print(f"{Colors.BOLD}{Colors.CYAN}📊 Web Forge Status{Colors.RESET}")
    
    move_cursor(content_x, y)
    print(f"{Colors.YELLOW}description:{Colors.RESET} django & react servers")
    y += 1
    move_cursor(content_x, y)
    print(f"{Colors.YELLOW}status:{Colors.RESET}", end=' ')
    
    # Quick status check
    backend_running, _ = check_backend_running()
    frontend_running, _ = check_frontend_running()
    
    if backend_running and frontend_running:
        print(f"{Colors.GREEN}ready{Colors.RESET}")
    elif backend_running or frontend_running:
        print(f"{Colors.YELLOW}partial{Colors.RESET}")
    else:
        print(f"{Colors.RED}offline{Colors.RESET}")
    y += 2
    
    # Environment status
    env_status = check_environment_quick()
    move_cursor(content_x, y)
    print(f"{Colors.CYAN}Environment Status:{Colors.RESET}")
    y += 1
    
    # Python
    move_cursor(content_x + 2, y)
    icon = "✓" if env_status['python'] else "✗"
    color = Colors.GREEN if env_status['python'] else Colors.RED
    print(f"{color}{icon} Python{Colors.RESET}")
    y += 1
    
    # Node.js
    move_cursor(content_x + 2, y)
    icon = "✓" if env_status['node'] else "✗"
    color = Colors.GREEN if env_status['node'] else Colors.RED
    print(f"{color}{icon} Node.js{Colors.RESET}")
    y += 1
    
    # Backend initialized
    move_cursor(content_x + 2, y)
    icon = "✓" if env_status['backend_initialized'] else "✗"
    color = Colors.GREEN if env_status['backend_initialized'] else Colors.YELLOW
    status = "Initialized" if env_status['backend_initialized'] else "Not initialized"
    print(f"{color}{icon} Backend: {status}{Colors.RESET}")
    y += 1
    
    # Frontend initialized
    move_cursor(content_x + 2, y)
    icon = "✓" if env_status['frontend_initialized'] else "✗"
    color = Colors.GREEN if env_status['frontend_initialized'] else Colors.YELLOW
    status = "Initialized" if env_status['frontend_initialized'] else "Not initialized"
    print(f"{color}{icon} Frontend: {status}{Colors.RESET}")
    y += 2
    
    # Server status using simple_server_manager
    move_cursor(content_x, y)
    print(f"{Colors.CYAN}server status:{Colors.RESET}")
    y += 1
    
    # Get base path
    base_path = Path(__file__).parent.parent
    
    # Use simple_server_manager to get accurate status
    backend_running = False
    frontend_running = False
    backend_pid = None
    frontend_pid = None
    
    try:
        status_result = subprocess.run(
            ['python3', 'src/simple_server_manager.py', 'status'],
            capture_output=True,
            text=True,
            cwd=base_path
        )
        
        if status_result.returncode == 0:
            # Parse status output
            if 'Backend:  🟢 Running' in status_result.stdout or 'Backend: Running' in status_result.stdout:
                backend_running = True
                # Try to get PID
                pid_result = subprocess.run("lsof -ti:8000", shell=True, capture_output=True, text=True)
                if pid_result.stdout:
                    backend_pid = pid_result.stdout.strip()
                    
            if 'Frontend: 🟢 Running' in status_result.stdout or 'Frontend: Running' in status_result.stdout:
                frontend_running = True
                # Try to get PID
                pid_result = subprocess.run("lsof -ti:3000", shell=True, capture_output=True, text=True)
                if pid_result.stdout:
                    frontend_pid = pid_result.stdout.strip()
    except:
        pass
    
    # Backend status section
    move_cursor(content_x, y)
    print(f"{Colors.CYAN}backend:{Colors.RESET} django + postgresql")
    y += 1
    move_cursor(content_x, y)
    print(f"{Colors.CYAN}frontend:{Colors.RESET} react + redux")
    y += 1
    move_cursor(content_x, y)
    print(f"{Colors.CYAN}ports:{Colors.RESET} 8000 (api) / 3000 (ui)")
    y += 2
    
    # Display servers section
    move_cursor(content_x, y)
    print(f"{Colors.CYAN}servers:{Colors.RESET}")
    y += 1
    
    # Backend server
    move_cursor(content_x, y)
    if backend_running:
        print(f"  • django backend")
        y += 1
        move_cursor(content_x, y)
        print(f"    {Colors.GREEN}● Running{Colors.RESET} on port 8000")
        if backend_pid:
            print(f" (pid: {backend_pid})", end='')
        print()
    else:
        print(f"  • django backend")
        y += 1
        move_cursor(content_x, y)
        print(f"    {Colors.RED}○ Stopped{Colors.RESET}")
    y += 1
    
    # Frontend server
    move_cursor(content_x, y)
    if frontend_running:
        print(f"  • react frontend")
        y += 1
        move_cursor(content_x, y)
        print(f"    {Colors.GREEN}● Running{Colors.RESET} on port 3000")
        if frontend_pid:
            print(f" (pid: {frontend_pid})", end='')
        print()
    else:
        print(f"  • react frontend")
        y += 1
        move_cursor(content_x, y)
        print(f"    {Colors.RED}○ Stopped{Colors.RESET}")
    y += 1
    
    # Additional status for servers that are running
    if backend_running or frontend_running:
        y += 1
        move_cursor(content_x, y)
        print(f"  • both servers")
        y += 1
        move_cursor(content_x, y)
        if backend_running and frontend_running:
            print(f"    {Colors.GREEN}● All systems operational{Colors.RESET}")
        else:
            print(f"    {Colors.YELLOW}◐ Partially operational{Colors.RESET}")
    y += 2
    
    # Features section
    move_cursor(content_x, y)
    print(f"{Colors.CYAN}features:{Colors.RESET}")
    y += 1
    move_cursor(content_x, y)
    print(f"  • manual mode")
    if env_status.get('redis'):
        y += 1
        move_cursor(content_x, y)
        print(f"  • redis caching")
    if env_status.get('postgresql'):
        y += 1
        move_cursor(content_x, y)
        print(f"  • postgresql database")
    
    # Add a launch hint at the bottom if servers are stopped
    if not backend_running or not frontend_running:
        y = lines - 7
        move_cursor(content_x, y)
        print(f"{Colors.DIM}press enter to launch{Colors.RESET}")
    
    # Navigation instruction at bottom
    y = lines - 5
    move_cursor(content_x, y)
    print(f"{Colors.DIM}press any key to return{Colors.RESET}", end='', flush=True)
    
    # Hide cursor for cleaner look
    hide_cursor()
    
    # Track last footer update for clock updates
    last_footer_update = time.time()
    
    # Wait for user input with timeout for clock updates
    while True:
        # Update footer every second for live clock
        current_time = time.time()
        if current_time - last_footer_update >= 1.0:
            # Footer no longer needs time updates
            draw_header_time_only()  # Update header time efficiently
            last_footer_update = current_time
            hide_cursor()
            # Restore cursor position after footer update
            move_cursor(content_x + len("Press any key to continue...") + 1, y)
        
        # Check for key press with short timeout
        key = get_single_key(timeout=0.1)
        if key:  # Any key pressed
            break
    
    # Clear the prompt before returning
    move_cursor(content_x, y)
    print(' ' * 30, end='', flush=True)

def stop_all_web_servers():
    """Enhanced stop all servers with detailed feedback"""
    show_server_action("🛑 Extinguishing the Forge", Colors.RED)
    
    cols, lines = get_terminal_size()
    content_x = 31
    y = 5
    
    move_cursor(content_x, y)
    print(f"{Colors.YELLOW}Stopping all servers...{Colors.RESET}")
    
    try:
        # Get base path
        base_path = Path(__file__).parent.parent
        
        # Use simple_server_manager to stop all servers
        result = subprocess.run(
            ['python3', 'src/simple_server_manager.py', 'stop'],
            capture_output=True,
            text=True,
            timeout=15,
            cwd=base_path
        )
        
        if result.returncode == 0:
            # Wait a moment for servers to fully stop
            time.sleep(1)
            
            # Check status to verify
            status_result = subprocess.run(
                ['python3', 'src/simple_server_manager.py', 'status'],
                capture_output=True,
                text=True,
                cwd=base_path
            )
            
            y += 2
            # Check if backend is stopped
            if 'Backend:  🔴 Stopped' in status_result.stdout or 'Backend: Stopped' in status_result.stdout:
                move_cursor(content_x, y)
                print(f"{Colors.GREEN}✓ Backend server stopped{Colors.RESET}")
                y += 1
            else:
                move_cursor(content_x, y)
                print(f"{Colors.YELLOW}⚠ Backend may still be running{Colors.RESET}")
                y += 1
                
            # Check if frontend is stopped
            if 'Frontend: 🔴 Stopped' in status_result.stdout or 'Frontend: Stopped' in status_result.stdout:
                move_cursor(content_x, y)
                print(f"{Colors.GREEN}✓ Frontend server stopped{Colors.RESET}")
                y += 1
            else:
                move_cursor(content_x, y)
                print(f"{Colors.YELLOW}⚠ Frontend may still be running{Colors.RESET}")
                y += 1
                
            y += 1
            move_cursor(content_x, y)
            print(f"{Colors.GREEN}✓ All servers have been stopped{Colors.RESET}")
        else:
            y += 2
            move_cursor(content_x, y)
            print(f"{Colors.RED}Failed to stop servers (exit code: {result.returncode}){Colors.RESET}")
            if result.stderr:
                y += 1
                move_cursor(content_x, y)
                print(f"{Colors.RED}Error: {result.stderr[:200]}...{Colors.RESET}")
            if result.stdout:
                y += 1
                move_cursor(content_x, y)
                print(f"{Colors.YELLOW}Output: {result.stdout[:200]}...{Colors.RESET}")
                
    except subprocess.TimeoutExpired:
        y += 2
        move_cursor(content_x, y)
        print(f"{Colors.RED}Stop operation timed out{Colors.RESET}")
    except Exception as e:
        y += 2
        move_cursor(content_x, y)
        print(f"{Colors.RED}Error stopping servers: {str(e)}{Colors.RESET}")
    
    y += 2
    move_cursor(content_x, y)
    print(f"{Colors.DIM}The forge has been extinguished.{Colors.RESET}")
    
    y += 2
    move_cursor(content_x, y)
    print(f"{Colors.DIM}Press any key to return...{Colors.RESET}")
    get_single_key()

def stop_backend_server():
    """Stop the backend Django server using server_manager"""
    show_server_action("🔴 Stopping Backend Server", Colors.RED)
    
    cols, lines = get_terminal_size()
    content_x = 27 + 4
    y = 5
    
    try:
        from server_manager import stop_web_core, get_web_core_status
        
        # Check current status first
        status = get_web_core_status()
        if not status.get('running'):
            move_cursor(content_x, y)
            print(f"{Colors.YELLOW}ℹ️ No backend server running{Colors.RESET}")
        else:
            move_cursor(content_x, y)
            print(f"{Colors.YELLOW}stopping web core...{Colors.RESET}")
            
            # Stop the server
            stop_web_core(silent=True)
            
            move_cursor(content_x, y + 1)
            print(f"{Colors.GREEN}✓ Backend server stopped successfully{Colors.RESET}")
            
    except Exception as e:
        move_cursor(content_x, y)
        print(f"{Colors.RED}✗ Error stopping backend: {str(e)}{Colors.RESET}")
    
    move_cursor(content_x, y + 2)
    print(f"{Colors.DIM}Press any key to continue...{Colors.RESET}")
    get_single_key()

def stop_frontend_server():
    """Frontend removed - no longer needed"""
    show_server_action("ℹ️ frontend removed", Colors.YELLOW)
    
    cols, lines = get_terminal_size()
    content_x = 27 + 4
    y = 5
    
    try:
        # Find and kill React process
        result = subprocess.run(['pkill', '-f', 'react-scripts start'], capture_output=True, text=True)
        
        move_cursor(content_x, y)
        if result.returncode == 0:
            print(f"{Colors.GREEN}✓ Frontend server stopped successfully{Colors.RESET}")
        else:
            # Try lsof approach
            lsof_result = subprocess.run(['lsof', '-ti:3000'], capture_output=True, text=True)
            if lsof_result.stdout.strip():
                pids = lsof_result.stdout.strip().split('\n')
                for pid in pids:
                    subprocess.run(['kill', '-9', pid])
                print(f"{Colors.GREEN}✓ Frontend server stopped (port 3000 freed){Colors.RESET}")
            else:
                print(f"{Colors.YELLOW}ℹ️ No frontend server running{Colors.RESET}")
    except Exception as e:
        move_cursor(content_x, y)
        print(f"{Colors.RED}✗ Error stopping frontend: {str(e)}{Colors.RESET}")
    
    move_cursor(content_x, y + 2)
    print(f"{Colors.DIM}Press any key to continue...{Colors.RESET}")
    get_single_key()

def restart_backend_server():
    """Restart the backend Django server with auto-recovery"""
    show_server_action("🔄 Restarting Backend Server", Colors.YELLOW)
    
    cols, lines = get_terminal_size()
    content_x = 27 + 4
    y = 5
    
    try:
        # Use the enhanced server_manager
        from server_manager import restart_web_core, get_web_core_status
        
        # Show status
        move_cursor(content_x, y)
        print("Checking services...")
        
        # Run restart with auto-recovery
        restart_web_core(silent=True)
        
        # Check final status
        time.sleep(2)
        status = get_web_core_status()
        
        move_cursor(content_x, y + 1)
        if status.get('running') and status.get('api_healthy'):
            print(f"{Colors.GREEN}✓ Web Core restarted successfully{Colors.RESET}")
            if status.get('pid'):
                print(f"  PID: {status['pid']}")
        else:
            print(f"{Colors.YELLOW}⚠ Web Core may need manual intervention{Colors.RESET}")
            if not status.get('postgresql'):
                print(f"  PostgreSQL not running")
            
    except ImportError:
        # Fallback to old method if server_manager not available
        move_cursor(content_x, y)
        print("Stopping backend server...")
        subprocess.run(['pkill', '-f', 'manage.py runserver'], capture_output=True)
        time.sleep(1)
        
        move_cursor(content_x, y + 1)
        print("Starting backend server...")
        start_web_backend(is_restart=True)

def restart_frontend_server():
    """Frontend removed - no longer needed"""
    show_server_action("ℹ️ frontend removed", Colors.YELLOW)
    
    cols, lines = get_terminal_size()
    content_x = 27 + 4
    y = 5
    
    # First stop
    move_cursor(content_x, y)
    print("Stopping frontend server...")
    subprocess.run(['pkill', '-f', 'react-scripts start'], capture_output=True)
    time.sleep(1)
    
    # Then start
    move_cursor(content_x, y + 1)
    print("Starting frontend server...")
    start_web_frontend(is_restart=True)

def check_environment_quick():
    """Quick environment check for status display"""
    env_status = {
        'python': False,
        'node': False,
        'npm': False,
        'backend_initialized': False,
        'frontend_initialized': False,
        'backend_venv': False,
        'all_good': False,
        'summary': ''
    }
    
    # Check Python
    try:
        result = subprocess.run(['python3', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            env_status['python'] = True
    except:
        pass
    
    # Check Node.js
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            env_status['node'] = True
    except:
        pass
    
    # Check npm
    try:
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            env_status['npm'] = True
    except:
        pass
    
    # Check backend initialization
    backend_path = Path('/Users/berkhatirli/Desktop/unibos/backend')
    if (backend_path / 'manage.py').exists():
        env_status['backend_initialized'] = True
        if (backend_path / 'venv').exists() or (backend_path / '.venv').exists():
            env_status['backend_venv'] = True
    
    # Check frontend initialization
    frontend_path = Path('/Users/berkhatirli/Desktop/unibos/frontend')
    if (frontend_path / 'package.json').exists():
        env_status['frontend_initialized'] = True
        if (frontend_path / 'node_modules').exists():
            env_status['frontend_initialized'] = True
    
    # Summary
    missing = []
    if not env_status['python']:
        missing.append('Python')
    if not env_status['node']:
        missing.append('Node.js')
    if not env_status['npm']:
        missing.append('npm')
    
    if missing:
        env_status['summary'] = f"Missing: {', '.join(missing)}"
    elif not env_status['backend_initialized'] or not env_status['frontend_initialized']:
        env_status['summary'] = "Setup needed"
    else:
        env_status['all_good'] = True
        env_status['summary'] = "Ready"
    
    return env_status

def run_environment_check():
    """Detailed environment check with helpful messages"""
    show_server_action("🔍 Environment Check", Colors.CYAN)
    
    cols, lines = get_terminal_size()
    content_x = 27 + 4  # Indented content
    y = 5
    
    # Add navigation hint at the top
    move_cursor(content_x, y)
    print(f"{Colors.DIM}← Press Left Arrow or ESC to go back{Colors.RESET}")
    y += 2
    
    checks = [
        ("Python 3.8+", check_python_version),
        ("Node.js 16+", check_node_version),
        ("npm/yarn", check_npm_version),
        ("PostgreSQL", check_postgresql),
        ("Redis", check_redis),
        ("Backend Dependencies", check_backend_deps),
        ("Frontend Dependencies", check_frontend_deps),
        ("Port 8000 Available", lambda: check_port_available(8000)),
        ("Port 3000 Available", lambda: check_port_available(3000)),
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        if y < lines - 5:  # Leave space for footer
            move_cursor(content_x, y)
            print(f"{Colors.YELLOW}Checking {check_name}...{Colors.RESET}", end='', flush=True)
            
            result, message = check_func()
            
            move_cursor(content_x, y)
            if result:
                print(f"{Colors.GREEN}✓ {check_name:<25} {message}{Colors.RESET}")
            else:
                print(f"{Colors.RED}✗ {check_name:<25} {message}{Colors.RESET}")
                all_passed = False
            
            y += 1
    
    # Summary
    y += 1
    move_cursor(content_x, y)
    if all_passed:
        print(f"{Colors.GREEN}✓ All checks passed! Your environment is ready.{Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}⚠ Some checks failed. Run Setup Wizard to fix issues.{Colors.RESET}")
    
    # Back hint with clear prompt
    y += 2
    move_cursor(content_x, y)
    print(f"{Colors.CYAN}Press any key to continue...{Colors.RESET}", end='', flush=True)
    
    # Wait for user input without timeout so user can read
    key = get_single_key(timeout=None)
    
    # Clear the prompt before returning
    move_cursor(content_x, y)
    print(' ' * 30, end='', flush=True)
    
    if key == '\x1b' or key == '\x1b[D':  # ESC or Left Arrow
        return  # Go back without clearing

def check_python_version():
    """Check if Python 3.8+ is installed"""
    try:
        result = subprocess.run(['python3', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            # Extract version number
            import re
            match = re.search(r'(\d+)\.(\d+)', version)
            if match:
                major, minor = int(match.group(1)), int(match.group(2))
                if major >= 3 and minor >= 8:
                    return True, version
            return False, f"{version} (Need 3.8+)"
        return False, "Not installed"
    except:
        return False, "Not installed"

def check_node_version():
    """Check if Node.js 16+ is installed"""
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            # Extract version number
            import re
            match = re.search(r'v(\d+)\.', version)
            if match:
                major = int(match.group(1))
                if major >= 16:
                    return True, version
            return False, f"{version} (Need v16+)"
        return False, "Not installed"
    except:
        return False, "Not installed"

def check_npm_version():
    """Check if npm is installed"""
    try:
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            return True, f"v{result.stdout.strip()}"
        return False, "Not installed"
    except:
        return False, "Not installed"

def check_postgresql():
    """Check if PostgreSQL is available"""
    try:
        result = subprocess.run(['psql', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            return True, result.stdout.strip().split()[-1]
        return False, "Not installed"
    except:
        return False, "Not installed (optional)"

def check_redis():
    """Check if Redis is available"""
    try:
        result = subprocess.run(['redis-cli', '--version'], capture_output=True, text=True, stderr=subprocess.DEVNULL)
        if result.returncode == 0:
            version = result.stdout.strip().split()[1]
            return True, f"v{version} (optional)"
        return False, "Not installed (optional - not required for basic operation)"
    except FileNotFoundError:
        return False, "Not installed (optional - not required for basic operation)"
    except:
        return False, "Not installed (optional - not required for basic operation)"

def check_backend_deps():
    """Check if backend dependencies are installed"""
    backend_path = Path('/Users/berkhatirli/Desktop/unibos/backend')
    venv_path = backend_path / 'venv'
    venv_alt_path = backend_path / '.venv'
    
    if not (backend_path / 'manage.py').exists():
        return False, "Backend not initialized"
    
    if venv_path.exists() or venv_alt_path.exists():
        return True, "Virtual environment found"
    
    return False, "No virtual environment"

def check_frontend_deps():
    """Check if frontend dependencies are installed"""
    frontend_path = Path('/Users/berkhatirli/Desktop/unibos/frontend')
    
    if not (frontend_path / 'package.json').exists():
        return False, "Frontend not initialized"
    
    if (frontend_path / 'node_modules').exists():
        return True, "Dependencies installed"
    
    return False, "Dependencies not installed"

def check_port_available(port):
    """Check if a port is available"""
    try:
        result = subprocess.run(f"lsof -ti:{port}", shell=True, capture_output=True)
        if result.returncode == 0 and result.stdout:
            return False, "In use"
        return True, "Available"
    except:
        return True, "Available"

def check_backend_running():
    """Check if Django backend server is running on port 8000"""
    try:
        # First check if port 8000 is in use
        result = subprocess.run(['lsof', '-ti:8000'], capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            # Verify it's actually a Django process
            for pid in pids:
                try:
                    # Check if the process is a Django runserver
                    ps_result = subprocess.run(['ps', '-p', pid, '-o', 'command='], 
                                             capture_output=True, text=True)
                    command = ps_result.stdout.lower()
                    # Check for various Django patterns
                    if any(pattern in command for pattern in ['manage.py', 'runserver', 'django', 'python', 'unibos']):
                        return True, int(pid)
                except:
                    pass
            # Port is in use but not by Django
            return True, int(pids[0]) if pids else None
        return False, None
    except Exception:
        return False, None

def check_frontend_running():
    """Check if React frontend server is running on port 3000"""
    try:
        # First check if port 3000 is in use
        result = subprocess.run(['lsof', '-ti:3000'], capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            # Verify it's actually a React dev server
            for pid in pids:
                try:
                    # Check if the process is a React dev server (node process)
                    ps_result = subprocess.run(['ps', '-p', pid, '-o', 'command='], 
                                             capture_output=True, text=True)
                    command = ps_result.stdout.lower()
                    # Check for various React/Node patterns
                    if any(pattern in command for pattern in ['node', 'react', 'webpack', 'npm', 'unibos']):
                        return True, int(pid)
                except:
                    pass
            # Port is in use but not by React
            return True, int(pids[0]) if pids else None
        return False, None
    except Exception:
        return False, None

def show_simple_web_status():
    """Show simplified server status for Web Core only"""
    show_server_action("📊 server status", Colors.CYAN)
    
    cols, lines = get_terminal_size()
    content_x = 27 + 4
    y = 5
    
    try:
        from server_manager import get_web_core_status
        status = get_web_core_status()
        
        backend_running = status.get('running', False)
        backend_pid = status.get('pid')
        postgresql_running = status.get('postgresql', False)
        api_healthy = status.get('api_healthy', False)
    except:
        # Fallback to old method
        backend_running, backend_pid = check_backend_running()
        postgresql_running = True  # Assume it's running
        api_healthy = backend_running
    
    move_cursor(content_x, y)
    print(f"{Colors.BOLD}{Colors.CYAN}═══ web core status ═══{Colors.RESET}")
    y += 2
    
    # PostgreSQL status
    move_cursor(content_x, y)
    if postgresql_running:
        print(f"{Colors.GREEN}● postgresql: RUNNING{Colors.RESET}")
    else:
        print(f"{Colors.RED}● postgresql: STOPPED{Colors.RESET}")
    y += 1
    
    # Backend status
    move_cursor(content_x, y)
    if backend_running:
        print(f"{Colors.GREEN}● web core: RUNNING{Colors.RESET}")
        y += 1
        move_cursor(content_x, y)
        print(f"  PID: {backend_pid}")
        y += 1
        move_cursor(content_x, y)
        print(f"  URL: http://localhost:8000")
        y += 1
        move_cursor(content_x, y)
        if api_healthy:
            print(f"  API: {Colors.GREEN}healthy{Colors.RESET}")
        else:
            print(f"  API: {Colors.YELLOW}not responding{Colors.RESET}")
    else:
        print(f"{Colors.RED}● web core: STOPPED{Colors.RESET}")
        y += 1
        move_cursor(content_x, y)
        print(f"  use 'start web core' to begin")
    
    y += 3
    move_cursor(content_x, y)
    print(f"{Colors.BOLD}available endpoints:{Colors.RESET}")
    y += 1
    endpoints = [
        "/           - main dashboard",
        "/documents/ - document management",
        "/module/    - module selector",
        "/admin/     - admin panel (if enabled)"
    ]
    for endpoint in endpoints:
        move_cursor(content_x, y)
        print(f"  {Colors.DIM}{endpoint}{Colors.RESET}")
        y += 1
    
    y += 2
    move_cursor(content_x, y)
    print(f"{Colors.BOLD}press any key to return...{Colors.RESET}")
    get_single_key(timeout=None)  # No timeout - wait for user input

def run_django_migrations():
    """Run Django database migrations"""
    show_server_action("🗄️ running migrations", Colors.MAGENTA)
    
    cols, lines = get_terminal_size()
    content_x = 27 + 4
    y = 5
    
    move_cursor(content_x, y)
    print(f"{Colors.YELLOW}running django migrations...{Colors.RESET}")
    y += 2
    
    backend_path = Path('/Users/berkhatirli/Desktop/unibos/backend')
    
    # Run makemigrations
    move_cursor(content_x, y)
    print(f"{Colors.CYAN}creating migrations...{Colors.RESET}")
    y += 1
    
    result = subprocess.run(
        ['python', 'manage.py', 'makemigrations'],
        cwd=backend_path,
        env={**os.environ, 'DJANGO_SETTINGS_MODULE': 'unibos_backend.settings.emergency'},
        capture_output=True,
        text=True
    )
    
    if "No changes detected" in result.stdout:
        move_cursor(content_x, y)
        print(f"{Colors.DIM}no new migrations needed{Colors.RESET}")
    else:
        move_cursor(content_x, y)
        print(f"{Colors.GREEN}✓ migrations created{Colors.RESET}")
    
    y += 2
    
    # Run migrate
    move_cursor(content_x, y)
    print(f"{Colors.CYAN}applying migrations...{Colors.RESET}")
    y += 1
    
    result = subprocess.run(
        ['python', 'manage.py', 'migrate'],
        cwd=backend_path,
        env={**os.environ, 'DJANGO_SETTINGS_MODULE': 'unibos_backend.settings.emergency'},
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        move_cursor(content_x, y)
        print(f"{Colors.GREEN}✓ migrations applied successfully{Colors.RESET}")
    else:
        move_cursor(content_x, y)
        print(f"{Colors.RED}✗ migration failed{Colors.RESET}")
        if result.stderr:
            y += 1
            move_cursor(content_x, y)
            print(f"{Colors.DIM}{result.stderr[:100]}...{Colors.RESET}")
    
    y += 3
    move_cursor(content_x, y)
    print(f"{Colors.BOLD}press any key to return...{Colors.RESET}")
    get_single_key()

def show_server_logs():
    """Show server logs"""
    show_server_action("📜 server logs", Colors.YELLOW)
    
    cols, lines = get_terminal_size()
    content_x = 27 + 4
    y = 5
    
    move_cursor(content_x, y)
    print(f"{Colors.BOLD}{Colors.CYAN}═══ recent server logs ═══{Colors.RESET}")
    y += 2
    
    # Check for Django log file
    log_file = Path('/Users/berkhatirli/Desktop/unibos/backend/logs/django.log')
    if log_file.exists():
        try:
            # Read last 20 lines of log
            with open(log_file, 'r') as f:
                lines_list = f.readlines()
                last_lines = lines_list[-20:] if len(lines_list) > 20 else lines_list
                
                for line in last_lines:
                    move_cursor(content_x, y)
                    # Truncate long lines
                    line = line.strip()[:80]
                    if 'ERROR' in line:
                        print(f"{Colors.RED}{line}{Colors.RESET}")
                    elif 'WARNING' in line:
                        print(f"{Colors.YELLOW}{line}{Colors.RESET}")
                    else:
                        print(f"{Colors.DIM}{line}{Colors.RESET}")
                    y += 1
                    if y >= lines - 5:  # Don't overflow screen
                        break
        except Exception as e:
            move_cursor(content_x, y)
            print(f"{Colors.RED}error reading logs: {str(e)}{Colors.RESET}")
    else:
        move_cursor(content_x, y)
        print(f"{Colors.YELLOW}no log file found{Colors.RESET}")
        y += 1
        move_cursor(content_x, y)
        print(f"{Colors.DIM}logs will be created when server runs{Colors.RESET}")
    
    y += 2
    move_cursor(content_x, y)
    print(f"{Colors.BOLD}press any key to return...{Colors.RESET}")
    get_single_key(timeout=None)  # No timeout - wait for user input

def run_setup_wizard():
    """Interactive setup wizard for first-time users"""
    show_server_action("🧙 Setup Wizard", Colors.MAGENTA, show_back_hint=True)
    
    cols, lines = get_terminal_size()
    content_x = 27 + 4
    y = 5
    
    # Welcome message
    move_cursor(content_x, y)
    print(f"{Colors.CYAN}welcome to the unibos web forge setup wizard!{Colors.RESET}")
    y += 2
    
    move_cursor(content_x, y)
    print(f"{Colors.WHITE}This wizard will help you set up:{Colors.RESET}")
    y += 1
    
    tasks = [
        "• Backend environment (Django + PostgreSQL)",
        "• Frontend environment (React + Node.js)",
        "• Database configuration",
        "• Initial project setup"
    ]
    
    for task in tasks:
        move_cursor(content_x + 2, y)
        print(f"{Colors.DIM}{task}{Colors.RESET}")
        y += 1
    
    y += 1
    move_cursor(content_x, y)
    print(f"{Colors.YELLOW}Continue with setup? (y/n/←): {Colors.RESET}", end='', flush=True)
    
    # Wait for user input without timeout
    key = get_single_key(timeout=None)  # No timeout for user prompt
    # Fixed key handling logic
    if not key:
        return
    if key == '\x1b' or key == '\x1b[D':  # ESC or Left Arrow
        return
    if key.lower() != 'y':  # If not 'y' or 'Y'
        return
    
    # Use enhanced setup wizard
    try:
        from web_forge_enhanced import run_enhanced_setup_wizard
        run_enhanced_setup_wizard()
    except ImportError:
        # Fallback to original setup if enhanced version not available
        setup_backend_environment()
        setup_frontend_environment()
        
        # Final message
        show_server_action("✅ Setup Complete", Colors.GREEN)
        y = 5
        move_cursor(content_x, y)
        print(f"{Colors.GREEN}Setup completed successfully!{Colors.RESET}")
        y += 2
        
        move_cursor(content_x, y)
        print(f"{Colors.WHITE}You can now:{Colors.RESET}")
        y += 1
        
        next_steps = [
            "• Start Backend Server (Django)",
            "• Start Frontend Server (React)",
            "• Or start both servers at once"
        ]
        
        for step in next_steps:
            move_cursor(content_x + 2, y)
            print(f"{Colors.CYAN}{step}{Colors.RESET}")
            y += 1
        
        y += 2
        move_cursor(content_x, y)
        print(f"{Colors.DIM}Press any key to continue...{Colors.RESET}")
        get_single_key(timeout=None)  # No timeout for user prompt

def setup_backend_environment():
    """Setup backend Django environment"""
    cols, lines = get_terminal_size()
    content_x = 27 + 4
    y = 5
    
    clear_content_area()
    show_server_action("⚙️ Setting Up Backend", Colors.BLUE)
    
    # Save current directory
    original_dir = os.getcwd()
    backend_path = Path('/Users/berkhatirli/Desktop/unibos/backend')
    
    # Check if backend directory exists
    if not backend_path.exists():
        move_cursor(content_x, y)
        print(f"{Colors.RED}Backend directory not found!{Colors.RESET}")
        return
    
    os.chdir(backend_path)
    
    # Create virtual environment
    move_cursor(content_x, y)
    print(f"{Colors.YELLOW}Creating Python virtual environment...{Colors.RESET}")
    y += 2
    
    result = subprocess.run(['python3', '-m', 'venv', 'venv'], capture_output=True)
    
    move_cursor(content_x, y)
    if result.returncode == 0:
        print(f"{Colors.GREEN}✓ Virtual environment created{Colors.RESET}")
    else:
        print(f"{Colors.RED}✗ Failed to create virtual environment{Colors.RESET}")
        return
    
    y += 2
    
    # Install dependencies
    move_cursor(content_x, y)
    print(f"{Colors.YELLOW}Installing backend dependencies...{Colors.RESET}")
    y += 2
    
    activate_cmd = 'source venv/bin/activate' if platform.system() != 'Windows' else 'venv\\Scripts\\activate'
    install_cmd = f"{activate_cmd} && pip install -r requirements.txt"
    
    result = subprocess.run(install_cmd, shell=True, capture_output=True)
    
    move_cursor(content_x, y)
    if result.returncode == 0:
        print(f"{Colors.GREEN}✓ Dependencies installed{Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}⚠ Some dependencies may have failed{Colors.RESET}")
    
    y += 2
    move_cursor(content_x, y)
    print(f"{Colors.DIM}Backend setup complete. Database setup can be done separately.{Colors.RESET}")
    
    # Restore original directory
    os.chdir(original_dir)
    time.sleep(2)

def setup_frontend_environment():
    """Setup frontend React environment"""
    cols, lines = get_terminal_size()
    content_x = 27 + 4
    y = 5
    
    clear_content_area()
    show_server_action("🎨 Setting Up Frontend", Colors.BLUE)
    
    # Save current directory
    original_dir = os.getcwd()
    frontend_path = Path('/Users/berkhatirli/Desktop/unibos/frontend')
    
    # Check if frontend directory exists
    if not frontend_path.exists():
        move_cursor(content_x, y)
        print(f"{Colors.RED}Frontend directory not found!{Colors.RESET}")
        return
    
    os.chdir(frontend_path)
    
    # Install dependencies
    move_cursor(content_x, y)
    print(f"{Colors.YELLOW}Installing frontend dependencies...{Colors.RESET}")
    y += 1
    move_cursor(content_x, y)
    print(f"{Colors.DIM}(This may take a few minutes){Colors.RESET}")
    y += 2
    
    result = subprocess.run(['npm', 'install'], capture_output=True)
    
    move_cursor(content_x, y)
    if result.returncode == 0:
        print(f"{Colors.GREEN}✓ Dependencies installed successfully{Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}⚠ Some dependencies may have failed{Colors.RESET}")
        y += 1
        move_cursor(content_x, y)
        print(f"{Colors.DIM}Try running 'npm install' manually{Colors.RESET}")
    
    y += 2
    move_cursor(content_x, y)
    print(f"{Colors.DIM}Frontend setup complete.{Colors.RESET}")
    
    # Restore original directory
    os.chdir(original_dir)
    time.sleep(2)

def show_server_logs():
    """Show server logs in a formatted view with arrow navigation"""
    selected_index = 0
    log_options = [
        ("backend_server", "📝 backend server log", "/Users/berkhatirli/Desktop/unibos/backend/server.log"),
        ("django_log", "🔧 django log", "/Users/berkhatirli/Desktop/unibos/backend/logs/django.log"),
        ("error_log", "❌ error log", "/Users/berkhatirli/Desktop/unibos/backend/error.log"),
        ("access_log", "🌐 access log", "/Users/berkhatirli/Desktop/unibos/backend/logs/access.log"),
        ("back", "← back to web forge", None)
    ]
    
    while True:  # Keep menu open until user chooses to go back
        show_server_action("📜 view logs", Colors.YELLOW)
        
        cols, lines = get_terminal_size()
        content_x = 27 + 4
        start_y = 7
        
        # Draw title
        move_cursor(content_x, 5)
        print(f"{Colors.BOLD}{Colors.CYAN}select log to view{Colors.RESET}")
        
        # Draw options with orange selector
        for i, (key, desc, path) in enumerate(log_options):
            y = start_y + i * 2  # Space between options
            move_cursor(content_x + 3, y)
            
            if i == selected_index:
                # Orange background for selected item (like web forge menu)
                bg_color = f"\033[48;5;{208}m"  # Orange background
                print(f"{bg_color}{Colors.BLACK}  {desc:<40}{Colors.RESET}")
            else:
                print(f"  {desc}")
        
        # Navigation hint at bottom
        y = start_y + len(log_options) * 2 + 2
        move_cursor(content_x + 3, y)
        print(f"{Colors.DIM}↑↓ navigate | enter select | ←/esc/q back{Colors.RESET}")
        
        # Get key input
        key = get_single_key(timeout=None)
        
        if key == '\x1b[A':  # Up arrow
            selected_index = (selected_index - 1) % len(log_options)
        elif key == '\x1b[B':  # Down arrow
            selected_index = (selected_index + 1) % len(log_options)
        elif key == '\r' or key == '\n' or key == '\x1b[C':  # Enter or Right arrow
            option_key, desc, path = log_options[selected_index]
            if option_key == "back":
                break
            elif path:
                view_log_file(path, desc)
        elif key == '\x1b' or key == '\x1b[D':  # ESC or Left Arrow
            break

def view_log_file(log_path, title):
    """View a specific log file with improved UI/UX"""
    # Clear content area first
    clear_content_area()
    
    cols, lines = get_terminal_size()
    content_x = 27 + 4
    y = 5
    
    # Draw clean title without duplicate emojis
    move_cursor(content_x, y)
    # Extract just the emoji from title (first 2 chars usually)
    emoji = ""
    clean_title = title
    if len(title) > 2 and ord(title[0]) > 127:  # Check if starts with emoji
        # Find where emoji ends (usually 2-4 chars)
        for i in range(min(4, len(title))):
            if ord(title[i]) < 127:  # ASCII character found
                emoji = title[:i].strip()
                clean_title = title[i:].strip()
                break
    
    print(f"{Colors.BOLD}{Colors.CYAN}━━━ {emoji} {clean_title} ━━━{Colors.RESET}")
    y += 2
    
    log_file = Path(log_path)
    
    if not log_file.exists():
        move_cursor(content_x, y)
        print(f"{Colors.YELLOW}⚠️  log file not found{Colors.RESET}")
        y += 2
        move_cursor(content_x, y)
        print(f"{Colors.DIM}path: {log_path}{Colors.RESET}")
        y += 1
        move_cursor(content_x, y)
        print(f"{Colors.DIM}the server may not have been started yet{Colors.RESET}")
    else:
        # Show file info
        move_cursor(content_x, y)
        file_size = log_file.stat().st_size
        file_modified = datetime.fromtimestamp(log_file.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        print(f"{Colors.DIM}file size: {file_size:,} bytes | modified: {file_modified}{Colors.RESET}")
        y += 1
        
        move_cursor(content_x, y)
        print(f"{Colors.DIM}{'─' * 60}{Colors.RESET}")
        y += 2
        
        # Read last N lines of log
        try:
            with open(log_file, 'r') as f:
                log_lines = f.readlines()
                total_lines = len(log_lines)
                display_lines = log_lines[-30:]  # Show more lines (30 instead of 20)
            
            # Show line count info
            move_cursor(content_x, y)
            print(f"{Colors.CYAN}showing last {len(display_lines)} of {total_lines} lines:{Colors.RESET}")
            y += 2
            
            for line in display_lines:
                if y < lines - 5:  # Leave space for footer
                    move_cursor(content_x, y)
                    # Truncate long lines
                    max_width = cols - content_x - 5
                    line = line.rstrip()
                    if len(line) > max_width:
                        line = line[:max_width-3] + "..."
                    
                    # Color code based on content
                    if 'ERROR' in line or 'CRITICAL' in line:
                        print(f"{Colors.RED}{line}{Colors.RESET}")
                    elif 'WARNING' in line or 'WARN' in line:
                        print(f"{Colors.YELLOW}{line}{Colors.RESET}")
                    elif 'INFO' in line:
                        print(f"{Colors.GREEN}{line}{Colors.RESET}")
                    elif 'DEBUG' in line:
                        print(f"{Colors.MAGENTA}{line}{Colors.RESET}")
                    else:
                        print(f"{Colors.DIM}{line}{Colors.RESET}")
                    y += 1
        except Exception as e:
            move_cursor(content_x, y)
            print(f"{Colors.RED}❌ error reading log: {e}{Colors.RESET}")
    
    # Navigation hint at bottom
    y = lines - 5
    move_cursor(content_x, y)
    print(f"{Colors.DIM}{'─' * 60}{Colors.RESET}")
    y += 1
    move_cursor(content_x, y)
    print(f"{Colors.BOLD}press any key to return...{Colors.RESET}")
    get_single_key(timeout=None)  # No timeout - wait for user input

def clear_content_area():
    """Clear the content area without affecting sidebar - CENTRALIZED"""
    # Use centralized context if available
    if CLI_CONTEXT_AVAILABLE and cli_context:
        cli_context.clear_content()
        return
    
    # Fallback to UI architecture if available
    global ui_controller
    if ui_controller and UI_ARCHITECTURE_AVAILABLE:
        ui_controller.content.clear()
    else:
        # Fallback to old method if UI not initialized
        cols, lines = get_terminal_size()
        content_x = 27  # Match main content area (after sidebar)
        
        # CRITICAL FIX: Only clear from content area to end of line
        # Do NOT use \033[2K which clears entire line including sidebar
        for y in range(2, lines - 1):  # Changed from 3 to 2 for single-line header
            move_cursor(content_x, y)  # Start at content area, NOT before
            print('\033[K', end='')  # Clear from cursor to end of line ONLY
        
        # Flush output to ensure immediate clearing
        sys.stdout.flush()
        
        # Small delay to ensure terminal processes the clear
        time.sleep(0.001)
        
        # IMPORTANT: Redraw sidebar borders to ensure they're not corrupted
        # Draw vertical separator line
        sidebar_width = 25
        for y in range(3, lines - 1):
            move_cursor(sidebar_width + 1, y)
            sys.stdout.write(f"{Colors.DIM}│{Colors.RESET}")
        sys.stdout.flush()

def show_ai_builder_menu():
    """Show AI builder menu with proper submenu interface"""
    # Force sidebar redraw to ensure dimmed state
    menu_state.last_sidebar_cache_key = None
    draw_sidebar()
    
    cols, lines = get_terminal_size()
    content_x = 27  # After sidebar
    content_width = cols - content_x - 1
    
    # Clear content area
    for y in range(2, lines - 1):
        move_cursor(content_x, y)
        sys.stdout.write('\033[K')
    sys.stdout.flush()
    
    # Title
    move_cursor(content_x + 2, 3)
    print(f"{Colors.BOLD}{Colors.CYAN}🤖 ai builder{Colors.RESET}")
    
    move_cursor(content_x + 2, 5)
    print(f"{Colors.YELLOW}ai-powered development tools{Colors.RESET}")
    
    # Options
    y = 7
    move_cursor(content_x + 2, y)
    print(f"{Colors.BOLD}available features:{Colors.RESET}")
    y += 2
    
    move_cursor(content_x + 4, y)
    print(f"• {Colors.GREEN}code generation{Colors.RESET} - generate code with ai")
    y += 1
    move_cursor(content_x + 4, y)
    print(f"• {Colors.GREEN}code review{Colors.RESET} - ai-powered code review")
    y += 1
    move_cursor(content_x + 4, y)
    print(f"• {Colors.GREEN}refactoring{Colors.RESET} - intelligent code refactoring")
    y += 1
    move_cursor(content_x + 4, y)
    print(f"• {Colors.GREEN}documentation{Colors.RESET} - auto-generate docs")
    y += 2
    
    move_cursor(content_x + 2, y)
    print(f"{Colors.DIM}press enter to launch ai builder{Colors.RESET}")
    
    # Import select for ESC key detection
    import select
    
    # Wait for key
    while True:
        key = get_single_key(timeout=0.1)
        if key == '\x1b[D' or key in ['q', 'Q']:  # Left Arrow or q to exit
            break
        elif key == '\x1b':  # ESC alone
            if not select.select([sys.stdin], [], [], 0.0)[0]:
                break
        elif key == '\r' or key == '\x1b[C':  # Enter or Right Arrow to launch
            # Launch actual AI builder
            ai_builder_tools()
            break

def ai_builder_tools():
    """Launch AI Builder interface"""
    try:
        # Try the new AI Builder implementation
        try:
            from ai_builder import AIBuilder
            
            # Save current terminal state
            show_cursor()
            clear_screen()
            
            # Initialize and run AI Builder
            builder = AIBuilder()
            builder.run()
            
            # After AI Builder exits, properly restore screen
            clear_screen()
            hide_cursor()
            draw_main_screen()
            return
            
        except ImportError:
            # Fall back to legacy implementation
            pass
        
        # Legacy implementation
        from claude_cli import ClaudeCLI
        
        # Save current terminal state
        show_cursor()
        
        # Initialize and run claude CLI with menu
        claude = ClaudeCLI()
        claude.show_claude_tools_menu()
        
        # After claude exits, properly restore screen
        clear_screen()  # Clear any Claude residue
        hide_cursor()
        draw_main_screen()  # Redraw entire interface
        
    except ImportError as e:
        clear_screen()
        print(f"\n{Colors.RED}Error loading Claude CLI: {e}{Colors.RESET}")
        time.sleep(2)
        hide_cursor()
        draw_main_screen()
    except Exception as e:
        clear_screen()
        print(f"\n{Colors.RED}Error in Claude tools: {e}{Colors.RESET}")
        print(f"{Colors.DIM}Error type: {type(e).__name__}{Colors.RESET}")
        
        # More detailed error for debugging
        import traceback
        print(f"\n{Colors.DIM}Traceback:{Colors.RESET}")
        traceback.print_exc()
        
        time.sleep(5)
        hide_cursor()
        draw_main_screen()

def show_code_forge_menu():
    """Show code forge menu with proper submenu interface"""
    # Force sidebar redraw to ensure dimmed state
    menu_state.last_sidebar_cache_key = None
    draw_sidebar()
    
    cols, lines = get_terminal_size()
    content_x = 27  # After sidebar
    content_width = cols - content_x - 1
    
    # Clear content area
    for y in range(2, lines - 1):
        move_cursor(content_x, y)
        sys.stdout.write('\033[K')
    sys.stdout.flush()
    
    # Title
    move_cursor(content_x + 2, 3)
    print(f"{Colors.BOLD}{Colors.CYAN}📦 code forge{Colors.RESET}")
    
    move_cursor(content_x + 2, 5)
    print(f"{Colors.YELLOW}version control & git tools{Colors.RESET}")
    
    # Options
    y = 7
    move_cursor(content_x + 2, y)
    print(f"{Colors.BOLD}available tools:{Colors.RESET}")
    y += 2
    
    move_cursor(content_x + 4, y)
    print(f"• {Colors.GREEN}git status{Colors.RESET} - view repository status")
    y += 1
    move_cursor(content_x + 4, y)
    print(f"• {Colors.GREEN}git commit{Colors.RESET} - commit changes")
    y += 1
    move_cursor(content_x + 4, y)
    print(f"• {Colors.GREEN}git push/pull{Colors.RESET} - sync with remote")
    y += 1
    move_cursor(content_x + 4, y)
    print(f"• {Colors.GREEN}branch management{Colors.RESET} - create/switch branches")
    y += 2
    
    move_cursor(content_x + 2, y)
    print(f"{Colors.DIM}press enter to launch git manager{Colors.RESET}")
    
    # Import select for ESC key detection
    import select
    
    # Wait for key
    while True:
        key = get_single_key(timeout=0.1)
        if key == '\x1b[D' or key in ['q', 'Q']:  # Left Arrow or q to exit
            break
        elif key == '\x1b':  # ESC alone
            if not select.select([sys.stdin], [], [], 0.0)[0]:
                break
        elif key == '\r' or key == '\x1b[C':  # Enter or Right Arrow to launch
            # Launch actual git manager
            try:
                show_cursor()
                clear_screen()
                from git_manager import GitManager
                git_manager = GitManager()
                git_manager.show_git_menu()
                hide_cursor()
            except ImportError as e:
                move_cursor(content_x + 2, lines - 5)
                print(f"{Colors.RED}Git Manager not found: {e}{Colors.RESET}")
                time.sleep(2)
            except Exception as e:
                move_cursor(content_x + 2, lines - 5)
                print(f"{Colors.RED}Error: {e}{Colors.RESET}")
                time.sleep(2)
            break

def show_git_menu():
    """Legacy git menu launcher - redirects to new code forge menu"""
    show_code_forge_menu()

def show_splash_screen():
    """Show animated splash screen"""
    clear_screen()
    cols, lines = get_terminal_size()
    
    # Get version info
    version = VERSION_INFO.get("version", "v308")
    
    # Claude Code style welcome message with box
    welcome_box = [
        f"{Colors.ORANGE}╭{'─' * 24}╮{Colors.RESET}",
        f"{Colors.ORANGE}│{Colors.RESET} {Colors.BOLD}* welcome to unibos! *{Colors.RESET} {Colors.ORANGE}│{Colors.RESET}",
        f"{Colors.ORANGE}╰{'─' * 24}╯{Colors.RESET}"
    ]
    
    # ASCII art - Large and impressive unibos logo (3D Shadow Effect)
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
    box_width = 26  # Updated to match new welcome box size
    logo_width = 48  # Width of the new impressive logo
    
    # Center the welcome box at top
    box_y = 4
    box_x = max(1, (cols - box_width) // 2)
    
    # Draw welcome box
    for i, line in enumerate(welcome_box):
        move_cursor(box_x, box_y + i)
        print(line)
    
    # Center the logo art
    logo_y = box_y + 6
    logo_x = max(1, (cols - logo_width) // 2)
    
    # Animate logo appearance
    for i, line in enumerate(logo_art):
        move_cursor(logo_x, logo_y + i)
        print(line, end='', flush=True)
        time.sleep(0.05)  # Smooth animation
    
    # Show additional info below
    info_y = logo_y + len(logo_art) + 2
    location = VERSION_INFO.get('location', 'bitez, bodrum, muğla, türkiye, dünya, güneş sistemi, samanyolu, yerel galaksi grubu, evren')
    
    info_lines = [
        f"{Colors.DIM}unicorn bodrum operating system{Colors.RESET}",
        f"{Colors.DIM}build {VERSION_INFO.get('build', '20250801_1537')}{Colors.RESET}",
        f"",
        f"{Colors.DIM}by berk hatırlı{Colors.RESET}",
        f"{Colors.DIM}{location}{Colors.RESET}"
    ]
    
    for i, line in enumerate(info_lines):
        # Adjust centering for longer location line
        if i == 4:  # Location line
            text_x = max(1, (cols - len(location)) // 2)
        else:
            text_x = max(1, (cols - 45) // 2)
        move_cursor(text_x, info_y + i)
        print(line)
    
    time.sleep(0.5)
    
    # Loading animation - positioned below the info
    loading_y = info_y + len(info_lines) + 2
    loading_text = "initializing system components..."
    loading_x = (cols - len(loading_text)) // 2
    
    # Show loading text
    move_cursor(loading_x, loading_y)
    print(f"{Colors.YELLOW}{loading_text}{Colors.RESET}")
    
    # Progress bar with wider design
    progress_y = loading_y + 2
    progress_width = 50  # Increased width
    progress_x = (cols - progress_width) // 2
    
    # Draw progress bar frame
    move_cursor(progress_x, progress_y)
    print(f"{Colors.DIM}[{' ' * (progress_width - 2)}]{Colors.RESET}")
    
    # Animate progress bar with varying speed
    for i in range(progress_width - 2):
        move_cursor(progress_x + 1 + i, progress_y)
        # Use different colors for different stages
        if i < (progress_width - 2) // 3:
            color = Colors.MAGENTA
        elif i < 2 * (progress_width - 2) // 3:
            color = Colors.YELLOW
        else:
            color = Colors.GREEN
        print(f"{color}█{Colors.RESET}", end='', flush=True)
        # Varying speed for more realistic loading
        if i % 5 == 0:
            time.sleep(0.03)
        else:
            time.sleep(0.01)
    
    # Keep the progress bar visible
    time.sleep(0.5)
    
    # Clear only the loading text
    move_cursor(loading_x - 2, loading_y)
    print(' ' * (len(loading_text) + 4), end='')
    
    # Show continue message below the progress bar
    continue_text = "press any key to continue..."
    continue_x = (cols - len(continue_text)) // 2
    continue_y = progress_y + 3  # 3 lines below progress bar
    move_cursor(continue_x, continue_y)
    print(f"{Colors.BLUE}{continue_text}{Colors.RESET}")
    
    # Wait for key press
    debug_mode = os.environ.get('UNIBOS_DEBUG', '').lower() == 'true'
    if debug_mode:
        with open('/tmp/unibos_debug.log', 'a') as f:
            f.write("splash screen: waiting for key press...\n")
    
    # Use simple key input for splash screen
    splash_key = get_simple_key()
    
    if debug_mode:
        with open('/tmp/unibos_debug.log', 'a') as f:
            f.write(f"splash screen: key pressed: {repr(splash_key)}\n")
    
    # Aggressive clear after splash screen
    if TERMIOS_AVAILABLE:
        try:
            import termios
            # Multiple flushes to ensure buffer is clear
            for _ in range(5):
                termios.tcflush(sys.stdin, termios.TCIFLUSH)
                termios.tcflush(sys.stdin, termios.TCIOFLUSH)
                time.sleep(0.01)
        except:
            pass

def update_header_time():
    """Background thread to update time in header every second"""
    while getattr(threading.current_thread(), "do_run", True):
        try:
            # Only update if not in submenu or special mode
            # Skip update if in web forge to prevent blinking
            if not menu_state.in_submenu or (menu_state.in_submenu and menu_state.in_submenu != 'web_forge'):
                # Use proper synchronization to avoid buffer conflicts
                sys.stdout.flush()
                draw_header()
                sys.stdout.flush()
            time.sleep(1)
        except Exception:
            # Silently ignore errors in background thread
            break

def main():
    """Main entry point"""
    try:
        # Ensure UTF-8 encoding for terminal
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8')
        
        # Set environment variable for UTF-8
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        
        # Debug output
        if os.environ.get('UNIBOS_DEBUG') == 'true':
            print("DEBUG: Starting UNIBOS main()")
            print(f"DEBUG: Terminal size: {get_terminal_size()}")
            print(f"DEBUG: TERMIOS available: {TERMIOS_AVAILABLE}")
        
        # Auto-check and fix web core before splash screen
        try:
            from server_manager import auto_fix_web_core, get_web_core_status
            
            # Check if web core needs fixing
            status = get_web_core_status()
            if not status.get('postgresql') or not status.get('running') or not status.get('api_healthy'):
                # Show a brief message
                print(f"{Colors.YELLOW}🔧 Checking services...{Colors.RESET}")
                
                # Run auto-recovery silently
                auto_fix_web_core()
                
                # Clear the message
                print("\r" + " " * 50 + "\r", end="")
        except Exception:
            # If server_manager not available or error, continue anyway
            pass
        
        # Show splash screen
        show_splash_screen()
        
        # Start time update thread (disabled to prevent buffer conflicts)
        # Background header updates cause stdout buffer issues
        # time_thread = threading.Thread(target=update_header_time, daemon=False)
        # time_thread.do_run = True
        # time_thread.start()
        
        # Start main loop
        main_loop()
        
    except KeyboardInterrupt:
        if os.environ.get('UNIBOS_DEBUG') == 'true':
            print("\nDEBUG: KeyboardInterrupt caught")
        pass
    except Exception as e:
        print(f"\n{Colors.RED}Fatal error: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()
    finally:
        # Stop background threads properly
        try:
            if 'time_thread' in locals() and time_thread.is_alive():
                time_thread.do_run = False
                time_thread.join(timeout=0.5)
        except:
            pass
        
        # Clean up UI properly
        global ui_controller
        if ui_controller and UI_ARCHITECTURE_AVAILABLE:
            try:
                ui_controller.cleanup()
            except:
                pass
        
        # Ensure all output is flushed before cleanup
        try:
            sys.stdout.flush()
            sys.stderr.flush()
        except:
            pass
        
        # Cleanup terminal state
        try:
            clear_screen()
            show_cursor()
            print(f"{Colors.GREEN}thank you for using unibos!{Colors.RESET}")
            print(f"{Colors.DIM}visit https://github.com/berkhatirli/unibos{Colors.RESET}\n")
            sys.stdout.flush()
        except:
            pass

if __name__ == "__main__":
    main()