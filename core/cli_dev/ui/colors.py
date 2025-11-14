"""
UNIBOS CLI Color Definitions
ANSI color codes for terminal output
"""


class Colors:
    """ANSI color codes for terminal styling"""

    # Basic colors
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'

    # Foreground colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'

    # Bright foreground colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'

    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'

    # Special colors (for UNIBOS theme)
    ORANGE = '\033[38;5;208m'  # 256-color orange
    PURPLE = '\033[38;5;141m'  # 256-color purple

    @classmethod
    def rgb(cls, r: int, g: int, b: int) -> str:
        """
        Create RGB color code (24-bit true color)

        Args:
            r: Red (0-255)
            g: Green (0-255)
            b: Blue (0-255)

        Returns:
            ANSI color code string
        """
        return f'\033[38;2;{r};{g};{b}m'

    @classmethod
    def bg_rgb(cls, r: int, g: int, b: int) -> str:
        """
        Create RGB background color code

        Args:
            r: Red (0-255)
            g: Green (0-255)
            b: Blue (0-255)

        Returns:
            ANSI background color code string
        """
        return f'\033[48;2;{r};{g};{b}m'

    @classmethod
    def strip(cls, text: str) -> str:
        """
        Remove all ANSI color codes from text

        Args:
            text: Text with ANSI codes

        Returns:
            Plain text without color codes
        """
        import re
        ansi_escape = re.compile(r'\033\[[0-9;]+m')
        return ansi_escape.sub('', text)
