"""
UNIBOS CLI Color Definitions
ANSI color codes for terminal UI

Extracted from v527 main.py (lines 153-183)
Reference: docs/development/cli_v527_reference.md
"""


class Colors:
    """ANSI color codes for terminal output"""

    # Reset and styles
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
    BG_ORANGE = "\033[48;5;208m"    # Orange background for UNIBOS branding
    BG_ORANGE_DIM = "\033[48;5;95m" # Muted purple/mauve for inactive selection
    BG_DARK = "\033[48;5;234m"      # Darker background for header/footer
    BG_CONTENT = "\033[48;5;236m"   # Dark but visible content background
    BG_DARK_GRAY = "\033[48;5;235m" # Status bar background

    @classmethod
    def strip(cls, text: str) -> str:
        """Remove all ANSI color codes from text"""
        import re
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)
