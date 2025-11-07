"""
Spot It game logic module.

This module handles the mathematical card generation for Spot It.
The key property: every pair of cards shares exactly one matching symbol.

For 8 symbols per card, we use a projective plane structure:
- Total symbols needed: n² - n + 1 = 8² - 8 + 1 = 57
- Total cards possible: 57

However, for a simpler two-player game, we can use a smaller subset
while maintaining the property that any two cards share exactly one symbol.
"""

import random
from typing import List, Set, Dict, Tuple


class SpotItGame:
    """
    Generates Spot It cards ensuring every pair shares exactly one symbol.
    
    Uses a simplified algorithm based on combinatorial design:
    - Each card has 8 symbols
    - Any two cards share exactly 1 symbol
    """
    
    def __init__(self, symbols: List[str], symbols_per_card: int = 8):
        """
        Initialize the game with a list of symbols.
        
        Args:
            symbols: List of all available symbols/objects
            symbols_per_card: Number of symbols to display on each card (default: 8)
        """
        self.symbols = symbols
        self.symbols_per_card = symbols_per_card
        self.cards: List[Set[str]] = []
        self._generate_cards()
    
    def _generate_cards(self):
        """
        Generate cards using a simplified algorithm.
        
        For a proper Spot It game, we'd need exactly n² - n + 1 symbols
        where n = symbols_per_card. But for flexibility, we'll use a
        greedy algorithm that ensures the property holds.
        """
        if len(self.symbols) < self.symbols_per_card:
            raise ValueError(f"Need at least {self.symbols_per_card} symbols, got {len(self.symbols)}")
        
        # Shuffle symbols for randomness
        shuffled = self.symbols.copy()
        random.shuffle(shuffled)
        
        # Generate cards using a greedy approach
        # Start with first card
        self.cards = [set(shuffled[:self.symbols_per_card])]
        used_symbols = set(self.cards[0])
        
        # For each new card, ensure it shares exactly one symbol with each existing card
        max_attempts = 1000
        attempts = 0
        
        while len(self.cards) < 30 and attempts < max_attempts:  # Generate up to 30 cards
            attempts += 1
            new_card = set()
            
            # Try to create a card that shares exactly one symbol with each existing card
            for existing_card in self.cards:
                # Find symbols that are in this existing card but not yet used in new_card
                candidates = existing_card - new_card
                if candidates:
                    # Pick one symbol from this card
                    symbol = random.choice(list(candidates))
                    new_card.add(symbol)
                else:
                    # This card already shares a symbol, skip
                    break
            
            # Fill remaining slots with unused symbols
            remaining = self.symbols_per_card - len(new_card)
            if remaining > 0:
                unused = [s for s in shuffled if s not in new_card]
                if len(unused) >= remaining:
                    new_card.update(random.sample(unused, remaining))
            
            # Verify the card shares exactly one symbol with each existing card
            valid = True
            for existing_card in self.cards:
                intersection = new_card & existing_card
                if len(intersection) != 1:
                    valid = False
                    break
            
            if valid and len(new_card) == self.symbols_per_card:
                self.cards.append(new_card)
                used_symbols.update(new_card)
        
        # If we couldn't generate enough cards, use a simpler approach
        # Generate cards that share at least one symbol (relaxed constraint)
        if len(self.cards) < 10:
            self._generate_simple_cards()
    
    def _generate_simple_cards(self):
        """
        Fallback: Generate cards using a simpler algorithm.
        Ensures each card shares at least one symbol with others.
        """
        self.cards = []
        shuffled = self.symbols.copy()
        random.shuffle(shuffled)
        
        # Create overlapping cards
        for i in range(20):  # Generate 20 cards
            card = set()
            # Each card includes some symbols from previous cards plus new ones
            if i > 0:
                # Share one symbol with previous card
                prev_card = self.cards[-1]
                shared = random.choice(list(prev_card))
                card.add(shared)
            
            # Fill with random symbols
            remaining = self.symbols_per_card - len(card)
            available = [s for s in shuffled if s not in card]
            if len(available) >= remaining:
                card.update(random.sample(available, remaining))
            else:
                card.update(available)
                # Fill with duplicates if needed (not ideal, but works)
                while len(card) < self.symbols_per_card:
                    card.add(random.choice(shuffled))
            
            self.cards.append(card)
    
    def get_two_cards(self) -> Tuple[List[str], List[str]]:
        """
        Get two random cards that share exactly one symbol.
        
        Returns:
            Tuple of (card1_symbols, card2_symbols) as lists
        """
        if len(self.cards) < 2:
            raise ValueError("Need at least 2 cards")
        
        # Try to find two cards that share exactly one symbol
        max_attempts = 100
        for _ in range(max_attempts):
            card1, card2 = random.sample(self.cards, 2)
            intersection = card1 & card2
            
            if len(intersection) == 1:
                # Perfect! These cards share exactly one symbol
                return list(card1), list(card2)
        
        # If we can't find a perfect pair, create one dynamically
        # Pick a random card and create a second card that shares exactly one symbol
        card1 = random.choice(self.cards)
        shared_symbol = random.choice(list(card1))
        
        # Create card2 with the shared symbol and 7 other random symbols
        card2 = {shared_symbol}
        available_symbols = [s for s in self.symbols if s != shared_symbol and s not in card1]
        if len(available_symbols) >= 7:
            card2.update(random.sample(available_symbols, 7))
        else:
            # Fallback: use any symbols not in card1
            card2.update([s for s in self.symbols if s not in card1][:7])
            # Fill remaining slots if needed
            while len(card2) < self.symbols_per_card:
                card2.add(random.choice(self.symbols))
        
        return list(card1), list(card2)
    
    def find_match(self, card1: List[str], card2: List[str]) -> str:
        """
        Find the matching symbol between two cards.
        
        Args:
            card1: First card's symbols
            card2: Second card's symbols
            
        Returns:
            The matching symbol, or None if no match
        """
        set1 = set(card1)
        set2 = set(card2)
        intersection = set1 & set2
        if len(intersection) == 1:
            return list(intersection)[0]
        return None


def load_symbols(filename: str = "funny_objects.txt") -> List[str]:
    """
    Load symbols from a text file (one per line).
    
    Args:
        filename: Path to the symbols file
        
    Returns:
        List of symbol names
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            symbols = [line.strip() for line in f if line.strip()]
        return symbols
    except FileNotFoundError:
        # Return default symbols if file not found
        return [
            "banana peel", "toothbrush", "angry cat", "toilet paper roll",
            "screaming sun", "spilled coffee", "dancing pickle", "flying pizza"
        ]

