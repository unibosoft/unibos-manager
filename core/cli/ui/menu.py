"""
UNIBOS CLI Menu State Management
State management and navigation for interactive menus

Extracted from v527 main.py (lines 186-217)
Reference: docs/development/cli_v527_reference.md
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class MenuItem:
    """
    A single menu item

    Attributes:
        id: Unique identifier
        label: Display text
        icon: Optional emoji/icon
        action: Callback function or submenu
        enabled: Whether item is selectable
        description: Optional description text
    """
    id: str
    label: str
    icon: str = ""
    action: Any = None
    enabled: bool = True
    description: str = ""


class MenuState:
    """
    State management for interactive menu navigation

    This class tracks the current state of menu navigation including:
    - Current section and selected item
    - Submenu context
    - Terminal size for resize detection
    - Caching for performance optimization
    """

    def __init__(self):
        # Navigation state
        self.current_section = 0  # Current top-level section index
        self.selected_index = 0   # Currently selected item within section
        self.previous_index = None  # For efficient UI updates

        # Submenu state
        self.in_submenu = None  # Current submenu context (if any)
        self.submenu_index = 0  # Selected index within submenu

        # Terminal state
        self.last_cols = 0   # For resize detection
        self.last_lines = 0

        # Content sections
        self.sections: List[Dict[str, Any]] = []  # Top-level sections
        self.items: List[MenuItem] = []  # All menu items

        # Caching for performance
        self.sidebar_cache: Dict[str, str] = {}  # Cached rendered lines
        self.docs_cache: Dict[str, str] = {}  # Cached documentation

        # Optimization settings
        self.last_update_time = 0  # For debouncing
        self.update_buffer: List[Any] = []  # For batching updates

    def get_selected_item(self) -> Optional[MenuItem]:
        """Get the currently selected menu item (v527 exact)"""
        if self.in_submenu:
            # In submenu - return submenu item
            if self.in_submenu.get('items'):
                items = self.in_submenu['items']
                if 0 <= self.submenu_index < len(items):
                    return items[self.submenu_index]
        else:
            # In main menu - return item from current section (v527 style)
            current_section = self.get_current_section()
            if current_section:
                items = current_section.get('items', [])
                if 0 <= self.selected_index < len(items):
                    return items[self.selected_index]
        return None

    def get_current_section(self) -> Optional[Dict[str, Any]]:
        """Get the current section"""
        if 0 <= self.current_section < len(self.sections):
            return self.sections[self.current_section]
        return None

    def navigate_up(self) -> bool:
        """
        Navigate up in the menu (v527 style - wraps to previous section)

        Returns:
            True if navigation occurred, False if at top
        """
        if self.in_submenu:
            if self.submenu_index > 0:
                self.submenu_index -= 1
                return True
        else:
            if self.selected_index > 0:
                # Move up within current section
                self.previous_index = self.selected_index
                self.selected_index -= 1
                return True
            elif self.current_section > 0:
                # At top of section, jump to previous section (last item)
                self.current_section -= 1
                prev_section = self.sections[self.current_section] if self.sections else None
                if prev_section:
                    self.previous_index = self.selected_index
                    self.selected_index = len(prev_section.get('items', [])) - 1
                    return True
        return False

    def navigate_down(self, max_items: int) -> bool:
        """
        Navigate down in the menu (v527 style - wraps to next section)

        Args:
            max_items: Maximum number of items in current context

        Returns:
            True if navigation occurred, False if at bottom
        """
        if self.in_submenu:
            submenu_items = len(self.in_submenu.get('items', []))
            if self.submenu_index < submenu_items - 1:
                self.submenu_index += 1
                return True
        else:
            if self.selected_index < max_items - 1:
                # Move down within current section
                self.previous_index = self.selected_index
                self.selected_index += 1
                return True
            elif self.current_section < len(self.sections) - 1:
                # At bottom of section, jump to next section (first item)
                self.current_section += 1
                self.previous_index = self.selected_index
                self.selected_index = 0
                return True
        return False

    def navigate_left(self) -> bool:
        """
        Navigate left (previous section or exit submenu)

        Returns:
            True if navigation occurred
        """
        if self.in_submenu:
            # Exit submenu
            self.in_submenu = None
            self.submenu_index = 0
            return True
        else:
            # Previous section
            if self.current_section > 0:
                self.current_section -= 1
                self.selected_index = 0
                self.previous_index = None
                return True
        return False

    def navigate_right(self, max_sections: int) -> bool:
        """
        Navigate right (next section)

        Args:
            max_sections: Total number of sections

        Returns:
            True if navigation occurred
        """
        if not self.in_submenu:
            if self.current_section < max_sections - 1:
                self.current_section += 1
                self.selected_index = 0
                self.previous_index = None
                return True
        return False

    def enter_submenu(self, submenu: Dict[str, Any]):
        """
        Enter a submenu

        Args:
            submenu: Submenu configuration dict
        """
        self.in_submenu = submenu
        self.submenu_index = 0

    def exit_submenu(self):
        """Exit current submenu"""
        self.in_submenu = None
        self.submenu_index = 0

    def quick_select(self, number: int) -> Optional[MenuItem]:
        """
        Quick select item by number (0-9) - v527 exact

        Args:
            number: Number key pressed (0-9)

        Returns:
            Selected menu item if valid, None otherwise
        """
        if self.in_submenu:
            items = self.in_submenu.get('items', [])
            if 0 <= number < len(items):
                self.submenu_index = number
                return items[number]
        else:
            # Use current section items (v527 style)
            current_section = self.get_current_section()
            if current_section:
                items = current_section.get('items', [])
                if 0 <= number < len(items):
                    self.selected_index = number
                    self.previous_index = None
                    return items[number]
        return None

    def terminal_resized(self, cols: int, lines: int) -> bool:
        """
        Check if terminal was resized

        Args:
            cols: Current terminal columns
            lines: Current terminal lines

        Returns:
            True if terminal size changed
        """
        if cols != self.last_cols or lines != self.last_lines:
            self.last_cols = cols
            self.last_lines = lines
            # Clear caches on resize
            self.sidebar_cache.clear()
            return True
        return False

    def clear_caches(self):
        """Clear all caches (for refresh)"""
        self.sidebar_cache.clear()
        self.docs_cache.clear()
