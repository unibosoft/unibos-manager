"""
Solitaire Game Logic
Complete implementation of Klondike Solitaire
"""

import random
import hashlib
from typing import List, Dict, Tuple, Optional

class Card:
    """Represents a playing card"""
    
    SUITS = {'spades': '♠', 'hearts': '♥', 'diamonds': '♦', 'clubs': '♣'}
    RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    VALUES = {'A': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, 
              '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13}
    
    def __init__(self, suit: str, rank: str, face_up: bool = False):
        self.suit = suit
        self.rank = rank
        self.face_up = face_up
    
    @property
    def color(self):
        """Return card color (red or black)"""
        return 'red' if self.suit in ['hearts', 'diamonds'] else 'black'
    
    @property
    def value(self):
        """Return numeric value of card"""
        return self.VALUES[self.rank]
    
    @property
    def symbol(self):
        """Return suit symbol"""
        return self.SUITS[self.suit]
    
    def flip(self):
        """Flip the card"""
        self.face_up = not self.face_up
    
    def can_stack_on_tableau(self, other):
        """Check if this card can be placed on another in tableau"""
        if not other:
            return self.rank == 'K'  # Only Kings on empty tableau
        return (self.color != other.color and 
                self.value == other.value - 1)
    
    def can_stack_on_foundation(self, foundation_cards):
        """Check if this card can be placed on foundation"""
        if not foundation_cards:
            return self.rank == 'A'  # Only Aces on empty foundation
        top_card = foundation_cards[-1]
        return (self.suit == top_card.suit and 
                self.value == top_card.value + 1)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'suit': self.suit,
            'rank': self.rank,
            'face_up': self.face_up
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create card from dictionary"""
        return cls(data['suit'], data['rank'], data['face_up'])
    
    def __str__(self):
        if self.face_up:
            return f"{self.rank}{self.symbol}"
        return "🂠"  # Card back
    
    def __repr__(self):
        return f"Card({self.suit}, {self.rank}, {'up' if self.face_up else 'down'})"


class SolitaireGame:
    """Complete Klondike Solitaire game implementation"""
    
    def __init__(self):
        self.stock = []
        self.waste = []
        self.foundations = {'spades': [], 'hearts': [], 'diamonds': [], 'clubs': []}
        self.tableau = [[] for _ in range(7)]
        self.moves = 0
        self.score = 0
        self.time = 0
        self.selected_cards = []
        self.selected_from = None
        self.undo_stack = []
        self.move_history = []
        
    def new_game(self):
        """Start a new game with proper Klondike Solitaire rules"""
        # Reset all game state
        self.stock = []
        self.waste = []
        self.foundations = {'spades': [], 'hearts': [], 'diamonds': [], 'clubs': []}
        self.tableau = [[] for _ in range(7)]
        self.moves = 0
        self.score = 0
        self.time = 0
        self.selected_cards = []
        self.selected_from = None
        self.move_history = []
        self.undo_stack = []
        
        # Create a fresh deck (52 cards, all face down)
        deck = []
        for suit in Card.SUITS.keys():
            for rank in Card.RANKS:
                deck.append(Card(suit, rank, False))  # All cards start face down
        
        # Shuffle the deck
        random.shuffle(deck)
        
        # Deal to tableau (Klondike rules)
        # Column 0: 1 card (0 face down, 1 face up)
        # Column 1: 2 cards (1 face down, 1 face up)
        # Column 2: 3 cards (2 face down, 1 face up)
        # ... and so on
        for col in range(7):
            for row in range(col + 1):
                card = deck.pop()
                # Only the last card in each column is face up
                if row == col:
                    card.face_up = True
                else:
                    card.face_up = False
                self.tableau[col].append(card)
        
        # Remaining cards go to stock (all face down)
        self.stock = deck  # Should be 24 cards
        for card in self.stock:
            card.face_up = False
        
        # Log the game state
        import logging
        logger = logging.getLogger(__name__)
        logger.debug(f"New game created: {len(self.stock)} cards in stock")
        for i, pile in enumerate(self.tableau):
            face_up_count = sum(1 for card in pile if card.face_up)
            logger.debug(f"Tableau {i}: {len(pile)} cards, {face_up_count} face up")
    
    def draw_from_stock(self):
        """Draw cards from stock to waste"""
        if not self.stock and self.waste:
            # Recycle waste to stock
            self.stock = list(reversed(self.waste))
            self.waste = []
            for card in self.stock:
                card.face_up = False
            self.score = max(0, self.score - 100)  # Penalty for recycling
        
        # Draw 3 cards (or remaining) from stock to waste
        if self.stock:
            for _ in range(min(3, len(self.stock))):
                card = self.stock.pop()
                card.face_up = True
                self.waste.append(card)
        
        self.moves += 1
        return True
    
    def select_card(self, pile_type: str, pile_index: int = 0, card_index: int = -1):
        """Select a card or cards for moving"""
        if pile_type == 'waste' and self.waste:
            self.selected_cards = [self.waste[-1]]
            self.selected_from = ('waste', 0)
        elif pile_type == 'tableau' and pile_index < 7:
            pile = self.tableau[pile_index]
            if pile and card_index < len(pile):
                # Select from card_index to end (must all be face up)
                cards_to_select = pile[card_index:]
                if all(c.face_up for c in cards_to_select):
                    self.selected_cards = cards_to_select
                    self.selected_from = ('tableau', pile_index)
        elif pile_type == 'foundation':
            suit = list(self.foundations.keys())[pile_index]
            if self.foundations[suit]:
                self.selected_cards = [self.foundations[suit][-1]]
                self.selected_from = ('foundation', suit)
    
    def move_selected_to(self, pile_type: str, pile_index: int = 0):
        """Move selected cards to target pile"""
        if not self.selected_cards:
            return False
        
        # Save state for undo
        self.save_state()
        
        moved = False
        
        if pile_type == 'tableau' and pile_index < 7:
            target_pile = self.tableau[pile_index]
            if not target_pile or self.selected_cards[0].can_stack_on_tableau(target_pile[-1] if target_pile else None):
                # Remove from source
                self.remove_selected_from_source()
                # Add to target
                target_pile.extend(self.selected_cards)
                moved = True
                self.score += 5
        
        elif pile_type == 'foundation':
            if len(self.selected_cards) == 1:
                card = self.selected_cards[0]
                suit = card.suit
                if card.can_stack_on_foundation(self.foundations[suit]):
                    # Remove from source
                    self.remove_selected_from_source()
                    # Add to foundation
                    self.foundations[suit].append(card)
                    moved = True
                    self.score += 10
        
        if moved:
            self.moves += 1
            self.reveal_tableau_cards()
            self.selected_cards = []
            self.selected_from = None
            return True
        
        # Restore state if move failed
        self.undo_stack.pop()
        return False
    
    def remove_selected_from_source(self):
        """Remove selected cards from their source pile"""
        source_type, source_index = self.selected_from
        
        if source_type == 'waste':
            self.waste.pop()
        elif source_type == 'tableau':
            pile = self.tableau[source_index]
            for _ in range(len(self.selected_cards)):
                pile.pop()
        elif source_type == 'foundation':
            self.foundations[source_index].pop()
    
    def reveal_tableau_cards(self):
        """Reveal top cards in tableau if needed"""
        for pile in self.tableau:
            if pile and not pile[-1].face_up:
                pile[-1].face_up = True
                self.score += 5
    
    def auto_move_to_foundation(self):
        """Automatically move eligible cards to foundation"""
        moved = False
        
        # Check waste
        if self.waste:
            card = self.waste[-1]
            if card.can_stack_on_foundation(self.foundations[card.suit]):
                self.waste.pop()
                self.foundations[card.suit].append(card)
                self.score += 10
                moved = True
        
        # Check tableau
        for pile in self.tableau:
            if pile and pile[-1].face_up:
                card = pile[-1]
                if card.can_stack_on_foundation(self.foundations[card.suit]):
                    pile.pop()
                    self.foundations[card.suit].append(card)
                    self.score += 10
                    moved = True
                    self.reveal_tableau_cards()
        
        if moved:
            self.moves += 1
        return moved
    
    def is_won(self):
        """Check if game is won"""
        for suit in self.foundations:
            if len(self.foundations[suit]) != 13:
                return False
        return True
    
    def save_state(self):
        """Save current state for undo"""
        state = {
            'stock': [c.to_dict() for c in self.stock],
            'waste': [c.to_dict() for c in self.waste],
            'foundations': {s: [c.to_dict() for c in cards] 
                          for s, cards in self.foundations.items()},
            'tableau': [[c.to_dict() for c in pile] for pile in self.tableau],
            'score': self.score,
            'moves': self.moves
        }
        # Only keep the last state for single undo
        self.undo_stack = [state]
    
    def undo(self):
        """Undo last move - can only be used once"""
        if self.undo_stack:
            state = self.undo_stack.pop()
            self.stock = [Card.from_dict(c) for c in state['stock']]
            self.waste = [Card.from_dict(c) for c in state['waste']]
            self.foundations = {s: [Card.from_dict(c) for c in cards]
                              for s, cards in state['foundations'].items()}
            self.tableau = [[Card.from_dict(c) for c in pile] 
                           for pile in state['tableau']]
            self.score = state['score']
            self.moves = state['moves']
            # Clear undo stack after using undo once
            self.undo_stack = []
            return True
        return False
    
    def get_hint(self):
        """Get a hint for next move"""
        hints = []
        
        # Check waste to tableau/foundation
        if self.waste:
            card = self.waste[-1]
            # Check foundations
            if card.can_stack_on_foundation(self.foundations[card.suit]):
                hints.append(('waste', 'foundation', card.suit))
            # Check tableau
            for i, pile in enumerate(self.tableau):
                if not pile or card.can_stack_on_tableau(pile[-1] if pile else None):
                    hints.append(('waste', 'tableau', i))
        
        # Check tableau to tableau/foundation
        for i, pile in enumerate(self.tableau):
            if pile:
                # Find all face-up sequences
                face_up_start = len(pile)
                for j in range(len(pile) - 1, -1, -1):
                    if pile[j].face_up:
                        face_up_start = j
                    else:
                        break
                
                # Check each face-up card
                for j in range(face_up_start, len(pile)):
                    card = pile[j]
                    # Check foundation
                    if j == len(pile) - 1 and card.can_stack_on_foundation(self.foundations[card.suit]):
                        hints.append((('tableau', i), 'foundation', card.suit))
                    # Check other tableau piles
                    for k, other_pile in enumerate(self.tableau):
                        if k != i:
                            if not other_pile or pile[j].can_stack_on_tableau(other_pile[-1] if other_pile else None):
                                hints.append((('tableau', i, j), 'tableau', k))
        
        return hints
    
    def to_dict(self):
        """Convert game state to dictionary"""
        return {
            'stock': [c.to_dict() for c in self.stock],
            'waste': [c.to_dict() for c in self.waste],
            'foundations': {s: [c.to_dict() for c in cards] 
                          for s, cards in self.foundations.items()},
            'tableau': [[c.to_dict() for c in pile] for pile in self.tableau],
            'moves': self.moves,
            'score': self.score,
            'time': self.time,
            'is_won': self.is_won(),
            'move_history': self.move_history,
            'undo_stack': self.undo_stack
        }
    
    def from_dict(self, data):
        """Load game state from dictionary"""
        self.stock = [Card.from_dict(c) for c in data.get('stock', [])]
        self.waste = [Card.from_dict(c) for c in data.get('waste', [])]
        self.foundations = {s: [Card.from_dict(c) for c in cards]
                          for s, cards in data.get('foundations', {}).items()}
        self.tableau = [[Card.from_dict(c) for c in pile] 
                       for pile in data.get('tableau', [])]
        self.moves = data.get('moves', 0)
        self.score = data.get('score', 0)
        self.time = data.get('time', 0)
        self.move_history = data.get('move_history', [])
        self.undo_stack = data.get('undo_stack', [])


def hash_password(password: str) -> str:
    """Hash a password for storage"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against hash"""
    return hash_password(password) == hashed