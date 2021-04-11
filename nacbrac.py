import pdb
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Union

class Suit(Enum):
    Heart = auto()
    Diamond = auto()
    Spade = auto()
    Club = auto()

@dataclass
class Card:
    value: int
    suit: Suit

    def is_face(self):
        return self.value < 6 or self.value > 10

    def is_red(self):
        return self.suit == Suit.Heart or self.suit == Suit.Diamond

    def is_black(self):
        return self.suit == Suit.Spade or self.suit == Suit.Club

class WildcardSlot:
    def __init__(self, card: Card=None):
        self.card = card

    def peek(self) -> Card:
        return self.card

    def get(self) -> Card:
        card = self.card
        self.card = None
        return card

    def put(self, card: Card) -> bool:
        if self.card is not None:
            return False
        else:
            self.card = card
        return True

    def has_card(self) -> bool:
        return self.card is not None

@dataclass
class Move:
    before: Union[WildcardSlot, int]
    after: Union[WildcardSlot, int]
    cards: List[Card]

@dataclass
class Gameboard:
    wildcard_slot: WildcardSlot = WildcardSlot()
    field_slots: List[List[Card]] = [[], [], [], [], [], [], [], [], []]

    def validate(self) -> bool:
        cards: List[Card] = []
        if self.wildcard_slot.has_card():
            cards.append(self.wildcard_slot.peek())
        for card_stack in self.field_slots:
            for card in card_stack:
                cards.append(card)

        if not (len(cards) == 36):
            return False
        hearts = [card for card in cards if card.suit == Suit.Heart]
        diamonds = [card for card in cards if card.suit == Suit.Diamond]
        spades = [card for card in cards if card.suit == Suit.Spade]
        clubs = [card for card in cards if card.suit == Suit.Club]
        if not (len(hearts) == 9 and len(diamonds) == 9 and len(spades) == 9 and len(clubs) == 9):
            return False
        card_groups: List[List[Card]] = [hearts, diamonds, spades, clubs]
        for card_group in card_groups:
            non_face_cards = [card for card in card_group if not card.is_face()]
            if not (len(non_face_cards) == 5):
                return False
            values = [card.value for card in non_face_cards]
            values.sort()
            if values != [6, 7, 8, 9, 10]:
                return False
        return True

    def execute(self, move: Move) -> None:
        pass

    def undo(self, move: Move) -> None:
        pass

    def solved(self) -> bool:
        if self.wildcard_slot.has_card():
            return False
        
        pass

    def get_valid_moves(self) -> List[Move]:
        pass

    @staticmethod
    def _is_field_slot_done(cards: List[Card]) -> bool:
        # empty slot
        if not cards:
            return True
        # all face, same suit
        if all([card.is_face() for card in cards]):
            suit = cards[0].suit
            return all([card.suit == suit for card in cards])
        # ordered values, interleaving color
        elif all([not card.is_face() for card in cards]):
            values = [card.value for card in cards]
            if values != [10, 9, 8, 7, 6]:
                return False
            else:
                red_color = [card.is_red() for card in cards]
                return (red_color == [True, False, True, False, True]) or (red_color == [False, True, False, True, False])
        # mix of face and value
        else:
            return False

class NacbracSolver(ABC):
    @abstractmethod
    def solve(self, gameboard: Gameboard) -> List[Move]:
        pass

class DfsSolver(NacbracSolver):
    def solve(self, gameboard: Gameboard) -> List[Move]:
        # dfs
        #if solved(gameboard):
            
        # self.get_valid_moves(gameboard)
        return []



def main():
    print("This is Nacbrac solver.")

    gameboard: Gameboard = Gameboard(WildcardSlot(), [])
    solver: NacbracSolver = DfsSolver()
    solution: List[Move] = solver.solve(gameboard)

    print("{}".format(solution))

if __name__ == "__main__":
    main()