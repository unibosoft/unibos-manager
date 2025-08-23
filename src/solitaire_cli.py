"""
CLI Solitaire Game
Full-featured playable solitaire for terminal
"""

import sys
import os
import time
import json
from typing import Optional, Tuple
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import from main for colors and utilities
from src.main import (
    Colors, clear_screen, get_terminal_size, move_cursor, 
    hide_cursor, show_cursor, get_single_key
)

# Import game logic
try:
    from backend.apps.solitaire.game import SolitaireGame, Card, hash_password, verify_password
except ImportError:
    # Fallback if backend not available
    class Card:
        pass
    class SolitaireGame:
        pass

class CLISolitaire:
    """Terminal-based solitaire game"""
    
    def __init__(self):
        self.game = SolitaireGame()
        self.cursor_pile = 'tableau'
        self.cursor_index = 0
        self.cursor_card = 0
        self.message = ""
        self.show_help = False
        self.game_time_start = time.time()
        self.password_hash = None
        self.last_message = ""
        self.last_cursor_pos = None
        self.screen_initialized = False
        self.keys_pressed = set()  # Track pressed keys for QW combination
        
    def draw_game(self, force_redraw=False):
        """Draw the complete game screen"""
        cols, lines = get_terminal_size()
        
        # Only clear screen on first draw or when forced
        if not self.screen_initialized or force_redraw:
            clear_screen()
            # Green felt background
            for y in range(1, lines - 3):
                move_cursor(1, y)
                print(f"{Colors.BG_GREEN}{' ' * cols}{Colors.RESET}", end='')
            self.screen_initialized = True
        
        # Title and stats (update every time for timer)
        self.draw_header(cols)
        
        # Draw game areas
        self.draw_stock_and_waste(5, 3)
        self.draw_foundations(cols - 35, 3)
        self.draw_tableau(5, 8)
        
        # Clear previous cursor if position changed
        if self.last_cursor_pos and self.last_cursor_pos != (self.cursor_pile, self.cursor_index):
            self.clear_cursor_at_position(self.last_cursor_pos)
        
        # Draw cursor
        self.draw_cursor()
        self.last_cursor_pos = (self.cursor_pile, self.cursor_index)
        
        # Clear previous message if it changed
        if self.last_message != self.message:
            if self.last_message:
                move_cursor(cols//2 - len(self.last_message)//2, lines - 4)
                print(f"{Colors.BG_GREEN}{' ' * len(self.last_message)}{Colors.RESET}")
            self.last_message = self.message
        
        # Draw message
        if self.message:
            move_cursor(cols//2 - len(self.message)//2, lines - 4)
            print(f"{Colors.YELLOW}{self.message}{Colors.RESET}")
        
        # Draw controls (static, only on first draw or force redraw)
        if not self.screen_initialized or force_redraw:
            self.draw_controls(lines - 2)
        
        # Show help overlay if enabled
        if self.show_help:
            self.draw_help_overlay(cols, lines)
    
    def draw_header(self, cols):
        """Draw game header with stats"""
        title = "♠ ♥ klondike solitaire ♦ ♣"
        move_cursor((cols - len(title))//2, 1)
        print(f"{Colors.BOLD}{Colors.WHITE}{title}{Colors.RESET}")
        
        # Stats
        elapsed = int(time.time() - self.game_time_start + self.game.time)
        time_str = f"{elapsed//60:02d}:{elapsed%60:02d}"
        stats = f"moves: {self.game.moves} | score: {self.game.score} | time: {time_str}"
        move_cursor(cols - len(stats) - 2, 2)
        print(f"{Colors.WHITE}{stats}{Colors.RESET}")
    
    def draw_stock_and_waste(self, x, y):
        """Draw stock and waste piles"""
        # Stock pile
        move_cursor(x, y)
        if self.game.stock:
            print(f"{Colors.BG_BLUE}{Colors.WHITE}┌───┐{Colors.RESET}")
            move_cursor(x, y + 1)
            print(f"{Colors.BG_BLUE}{Colors.WHITE}│▓▓▓│{Colors.RESET}")
            move_cursor(x, y + 2)
            print(f"{Colors.BG_BLUE}{Colors.WHITE}│{len(self.game.stock):^3}│{Colors.RESET}")
            move_cursor(x, y + 3)
            print(f"{Colors.BG_BLUE}{Colors.WHITE}└───┘{Colors.RESET}")
        else:
            # Empty stock - show recycle symbol
            print(f"{Colors.DIM}┌───┐{Colors.RESET}")
            move_cursor(x, y + 1)
            print(f"{Colors.DIM}│ ♻ │{Colors.RESET}")
            move_cursor(x, y + 2)
            print(f"{Colors.DIM}│   │{Colors.RESET}")
            move_cursor(x, y + 3)
            print(f"{Colors.DIM}└───┘{Colors.RESET}")
        
        # Waste pile (show up to 3 cards spread)
        waste_x = x + 8
        if self.game.waste:
            for i, card in enumerate(self.game.waste[-3:]):
                offset = i * 2
                self.draw_card(card, waste_x + offset, y)
    
    def draw_foundations(self, x, y):
        """Draw foundation piles"""
        suits_order = ['spades', 'hearts', 'diamonds', 'clubs']
        for i, suit in enumerate(suits_order):
            pile_x = x + i * 7
            cards = self.game.foundations[suit]
            
            if cards:
                # Show top card
                self.draw_card(cards[-1], pile_x, y)
            else:
                # Empty foundation
                move_cursor(pile_x, y)
                print(f"{Colors.DIM}┌───┐{Colors.RESET}")
                move_cursor(pile_x, y + 1)
                symbol = Card.SUITS[suit]
                print(f"{Colors.DIM}│ {symbol} │{Colors.RESET}")
                move_cursor(pile_x, y + 2)
                print(f"{Colors.DIM}│   │{Colors.RESET}")
                move_cursor(pile_x, y + 3)
                print(f"{Colors.DIM}└───┘{Colors.RESET}")
    
    def draw_tableau(self, start_x, start_y):
        """Draw tableau piles"""
        for pile_index in range(7):
            x = start_x + pile_index * 12
            pile = self.game.tableau[pile_index]
            
            if not pile:
                # Empty pile
                move_cursor(x, start_y)
                print(f"{Colors.DIM}┌───┐{Colors.RESET}")
                move_cursor(x, start_y + 1)
                print(f"{Colors.DIM}│   │{Colors.RESET}")
                move_cursor(x, start_y + 2)
                print(f"{Colors.DIM}│ K │{Colors.RESET}")
                move_cursor(x, start_y + 3)
                print(f"{Colors.DIM}└───┘{Colors.RESET}")
            else:
                # Draw cards cascading down
                for card_index, card in enumerate(pile):
                    y = start_y + card_index * 2
                    if card_index == len(pile) - 1:
                        # Full card for last one
                        self.draw_card(card, x, y)
                    else:
                        # Partial card for others
                        self.draw_card_top(card, x, y)
    
    def draw_card(self, card: Card, x: int, y: int):
        """Draw a complete card"""
        if not card.face_up:
            # Face down
            move_cursor(x, y)
            print(f"{Colors.BG_BLUE}{Colors.WHITE}┌───┐{Colors.RESET}")
            move_cursor(x, y + 1)
            print(f"{Colors.BG_BLUE}{Colors.WHITE}│▓▓▓│{Colors.RESET}")
            move_cursor(x, y + 2)
            print(f"{Colors.BG_BLUE}{Colors.WHITE}│▓▓▓│{Colors.RESET}")
            move_cursor(x, y + 3)
            print(f"{Colors.BG_BLUE}{Colors.WHITE}└───┘{Colors.RESET}")
        else:
            # Face up
            color = Colors.RED if card.color == 'red' else Colors.BLACK
            bg = Colors.BG_WHITE
            
            # Highlight selected cards
            if self.game.selected_cards and card in self.game.selected_cards:
                bg = Colors.BG_YELLOW
            
            move_cursor(x, y)
            print(f"{bg}{color}┌───┐{Colors.RESET}")
            move_cursor(x, y + 1)
            print(f"{bg}{color}│{card.rank:^3}│{Colors.RESET}")
            move_cursor(x, y + 2)
            print(f"{bg}{color}│ {card.symbol} │{Colors.RESET}")
            move_cursor(x, y + 3)
            print(f"{bg}{color}└───┘{Colors.RESET}")
    
    def draw_card_top(self, card: Card, x: int, y: int):
        """Draw just the top of a card (for cascading)"""
        if not card.face_up:
            move_cursor(x, y)
            print(f"{Colors.BG_BLUE}{Colors.WHITE}┌───┐{Colors.RESET}")
            move_cursor(x, y + 1)
            print(f"{Colors.BG_BLUE}{Colors.WHITE}│▓▓▓│{Colors.RESET}")
        else:
            color = Colors.RED if card.color == 'red' else Colors.BLACK
            bg = Colors.BG_WHITE
            
            if self.game.selected_cards and card in self.game.selected_cards:
                bg = Colors.BG_YELLOW
            
            move_cursor(x, y)
            print(f"{bg}{color}┌───┐{Colors.RESET}")
            move_cursor(x, y + 1)
            print(f"{bg}{color}│{card.rank:^3}│{Colors.RESET}")
    
    def draw_cursor(self):
        """Draw cursor highlight"""
        cols, lines = get_terminal_size()
        
        # Calculate cursor position
        if self.cursor_pile == 'stock':
            x, y = 5, 3
            self.draw_cursor_box(x, y)
        elif self.cursor_pile == 'waste':
            x, y = 13 + len(self.game.waste[-3:]) * 2 if self.game.waste else 13, 3
            self.draw_cursor_box(x, y)
        elif self.cursor_pile == 'foundation':
            x = cols - 35 + self.cursor_index * 7
            y = 3
            self.draw_cursor_box(x, y)
        elif self.cursor_pile == 'tableau':
            x = 5 + self.cursor_index * 12
            pile = self.game.tableau[self.cursor_index]
            y = 8 + (len(pile) - 1) * 2 if pile else 8
            self.draw_cursor_box(x, y)
    
    def draw_cursor_box(self, x, y):
        """Draw cursor highlight box"""
        move_cursor(x - 1, y)
        print(f"{Colors.CYAN}[{Colors.RESET}", end='')
        move_cursor(x + 5, y)
        print(f"{Colors.CYAN}]{Colors.RESET}", end='')
    
    def clear_cursor_at_position(self, pos):
        """Clear cursor at previous position"""
        pile, index = pos
        cols, lines = get_terminal_size()
        
        if pile == 'stock':
            x, y = 5, 3
        elif pile == 'waste':
            x, y = 13 + len(self.game.waste[-3:]) * 2 if self.game.waste else 13, 3
        elif pile == 'foundation':
            x = cols - 35 + index * 7
            y = 3
        elif pile == 'tableau':
            x = 5 + index * 12
            tableau_pile = self.game.tableau[index]
            y = 8 + (len(tableau_pile) - 1) * 2 if tableau_pile else 8
        else:
            return
        
        # Clear cursor brackets
        move_cursor(x - 1, y)
        print(f"{Colors.BG_GREEN} {Colors.RESET}", end='')
        move_cursor(x + 5, y)
        print(f"{Colors.BG_GREEN} {Colors.RESET}", end='')
    
    def draw_controls(self, y):
        """Draw control hints"""
        controls = "←↑↓→ move | space select | enter place | d draw | a auto | u undo | h help | q quit"
        cols, _ = get_terminal_size()
        move_cursor((cols - len(controls))//2, y)
        print(f"{Colors.DIM}{controls}{Colors.RESET}")
    
    def draw_help_overlay(self, cols, lines):
        """Draw help overlay"""
        # Semi-transparent overlay
        help_width = 60
        help_height = 20
        x = (cols - help_width) // 2
        y = (lines - help_height) // 2
        
        # Draw box
        for i in range(help_height):
            move_cursor(x, y + i)
            if i == 0:
                print(f"{Colors.BG_BLACK}{Colors.CYAN}╔{'═' * (help_width - 2)}╗{Colors.RESET}")
            elif i == help_height - 1:
                print(f"{Colors.BG_BLACK}{Colors.CYAN}╚{'═' * (help_width - 2)}╝{Colors.RESET}")
            else:
                print(f"{Colors.BG_BLACK}{Colors.CYAN}║{' ' * (help_width - 2)}║{Colors.RESET}")
        
        # Help content
        help_text = [
            "klondike solitaire help",
            "",
            "objective:",
            "move all cards to the four foundation piles",
            "in ascending order (ace to king) by suit.",
            "",
            "controls:",
            "arrow keys - navigate cursor",
            "space - select/deselect cards",
            "enter - move selected cards",
            "d - draw from stock",
            "a - auto-move to foundations",
            "u - undo last move",
            "h - toggle this help",
            "q - quit game",
            "",
            "press h to close help"
        ]
        
        for i, line in enumerate(help_text):
            move_cursor(x + 2, y + i + 2)
            if i == 0:
                print(f"{Colors.BG_BLACK}{Colors.YELLOW}{line:^{help_width-4}}{Colors.RESET}")
            else:
                print(f"{Colors.BG_BLACK}{Colors.WHITE}{line}{Colors.RESET}")
    
    def handle_input(self, key: str) -> bool:
        """Handle keyboard input"""
        self.message = ""
        
        # Handle QW combination for exit
        if key and len(key) == 1:
            self.keys_pressed.add(key.lower())
            
            # Check for Q+W combination (exit)
            if 'q' in self.keys_pressed and 'w' in self.keys_pressed:
                return False
            
            # Clear keys after a short timeout
            import threading
            def clear_keys():
                time.sleep(0.5)
                self.keys_pressed.clear()
            threading.Thread(target=clear_keys, daemon=True).start()
        
        if key == 'q':
            return False
        elif key == 'h':
            self.show_help = not self.show_help
        elif key == 'd':
            # Draw from stock
            if self.game.draw_from_stock():
                self.message = "Drew from stock"
        elif key == 'a':
            # Auto move
            if self.game.auto_move_to_foundation():
                self.message = "Auto-moved to foundation"
        elif key == 'u':
            # Undo
            if self.game.undo():
                self.message = "Move undone"
        elif key == ' ':
            # Select/deselect
            self.handle_select()
        elif key == '\r':
            # Place selected cards
            self.handle_place()
        elif key == '\x1b[A':  # Up arrow
            self.move_cursor_up()
        elif key == '\x1b[B':  # Down arrow
            self.move_cursor_down()
        elif key == '\x1b[C':  # Right arrow
            self.move_cursor_right()
        elif key == '\x1b[D':  # Left arrow
            self.move_cursor_left()
        
        # Check for win
        if self.game.is_won():
            self.message = "🎉 congratulations! you won! 🎉"
        
        return True
    
    def handle_select(self):
        """Handle card selection"""
        if self.cursor_pile == 'waste':
            self.game.select_card('waste')
            self.message = "Selected waste card"
        elif self.cursor_pile == 'tableau':
            pile = self.game.tableau[self.cursor_index]
            if pile:
                # Find the first face-up card from cursor position
                for i in range(len(pile)):
                    if pile[i].face_up:
                        self.game.select_card('tableau', self.cursor_index, i)
                        self.message = f"Selected {len(pile) - i} card(s)"
                        break
        elif self.cursor_pile == 'foundation':
            suits = ['spades', 'hearts', 'diamonds', 'clubs']
            suit = suits[self.cursor_index]
            if self.game.foundations[suit]:
                self.game.select_card('foundation', self.cursor_index)
                self.message = "Selected foundation card"
    
    def handle_place(self):
        """Handle placing selected cards"""
        if not self.game.selected_cards:
            self.message = "No cards selected"
            return
        
        if self.cursor_pile == 'tableau':
            if self.game.move_selected_to('tableau', self.cursor_index):
                self.message = "Cards moved"
            else:
                self.message = "Invalid move"
        elif self.cursor_pile == 'foundation':
            if self.game.move_selected_to('foundation', self.cursor_index):
                self.message = "Card moved to foundation"
            else:
                self.message = "Invalid move"
    
    def move_cursor_up(self):
        """Move cursor up"""
        if self.cursor_pile == 'tableau':
            self.cursor_pile = 'stock'
            self.cursor_index = 0
    
    def move_cursor_down(self):
        """Move cursor down"""
        if self.cursor_pile in ['stock', 'waste', 'foundation']:
            self.cursor_pile = 'tableau'
            self.cursor_index = min(self.cursor_index, 6)
    
    def move_cursor_right(self):
        """Move cursor right"""
        if self.cursor_pile == 'stock':
            self.cursor_pile = 'waste'
        elif self.cursor_pile == 'waste':
            self.cursor_pile = 'foundation'
            self.cursor_index = 0
        elif self.cursor_pile == 'foundation':
            if self.cursor_index < 3:
                self.cursor_index += 1
        elif self.cursor_pile == 'tableau':
            if self.cursor_index < 6:
                self.cursor_index += 1
    
    def move_cursor_left(self):
        """Move cursor left"""
        if self.cursor_pile == 'waste':
            self.cursor_pile = 'stock'
        elif self.cursor_pile == 'foundation':
            if self.cursor_index > 0:
                self.cursor_index -= 1
            else:
                self.cursor_pile = 'waste'
        elif self.cursor_pile == 'tableau':
            if self.cursor_index > 0:
                self.cursor_index -= 1
    
    def play(self):
        """Main game loop"""
        self.game.new_game()
        hide_cursor()
        
        # Initial draw with full screen clear
        self.draw_game(force_redraw=True)
        
        while True:
            # Update only what's needed (no full screen clear)
            self.draw_game()
            key = get_single_key(timeout=1.0)  # Update every second for timer
            
            if key:
                if not self.handle_input(key):
                    break
        
        show_cursor()
        clear_screen()
    
    def request_password(self) -> str:
        """Request password for lock screen"""
        clear_screen()
        cols, lines = get_terminal_size()
        
        # Draw lock screen
        for y in range(lines):
            move_cursor(1, y)
            print(f"{Colors.BG_BLACK}{' ' * cols}{Colors.RESET}", end='')
        
        # Draw lock box
        box_width = 50
        box_height = 10
        x = (cols - box_width) // 2
        y = (lines - box_height) // 2
        
        # Draw box
        for i in range(box_height):
            move_cursor(x, y + i)
            if i == 0:
                print(f"{Colors.CYAN}╔{'═' * (box_width - 2)}╗{Colors.RESET}")
            elif i == box_height - 1:
                print(f"{Colors.CYAN}╚{'═' * (box_width - 2)}╝{Colors.RESET}")
            else:
                print(f"{Colors.CYAN}║{' ' * (box_width - 2)}║{Colors.RESET}")
        
        # Lock icon and text
        move_cursor(x + box_width//2 - 2, y + 2)
        print(f"{Colors.YELLOW}🔒{Colors.RESET}")
        
        move_cursor(x + 2, y + 4)
        print(f"{Colors.WHITE}screen locked - enter password:{Colors.RESET}")
        
        move_cursor(x + 2, y + 6)
        print(f"{Colors.CYAN}> {Colors.RESET}", end='')
        
        # Get password input
        show_cursor()
        password = ""
        while True:
            key = get_single_key(timeout=None)
            if key == '\r':
                break
            elif key == '\x7f' or key == '\x08':  # Backspace
                if password:
                    password = password[:-1]
                    print('\b \b', end='', flush=True)
            elif key and len(key) == 1 and ord(key) >= 32:
                password += key
                print('*', end='', flush=True)
        
        hide_cursor()
        return password


def play_solitaire_cli(with_lock=False):
    """Launch CLI solitaire game"""
    game = CLISolitaire()
    
    if with_lock:
        # Set a lock password
        game.password_hash = hash_password("lplp")  # Database password
    
    game.play()
    
    if with_lock:
        # Request password to return
        while True:
            password = game.request_password()
            if verify_password(password, game.password_hash):
                break
            else:
                # Show error
                cols, lines = get_terminal_size()
                move_cursor(cols//2 - 10, lines//2 + 4)
                print(f"{Colors.RED}incorrect password!{Colors.RESET}")
                time.sleep(2)


if __name__ == "__main__":
    play_solitaire_cli()