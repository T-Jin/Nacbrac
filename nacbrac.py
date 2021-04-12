import pdb
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, unique
from typing import List, Union, Set
import datetime

@unique
class Suit(Enum):
    Heart = "H"
    Diamond = "D"
    Spade = "S"
    Club = "C"

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

    def __str__(self) -> str:
        return str(self.value) + self.suit.value

    @staticmethod
    def from_str(source: str):
        value_str = source[:-1]
        suit_str = source[-1]
        return Card(value=int(value_str), suit=Suit(suit_str))

class WildcardSlot:
    def __init__(self, card: Card=None):
        self.card = card

    def peek(self) -> Card:
        return self.card

    def pop(self) -> Card:
        card = self.card
        self.card = None
        return card

    def push(self, card: Card) -> bool:
        if self.card is not None:
            return False
        else:
            self.card = card
        return True

    def has_card(self) -> bool:
        return self.card is not None

    def __str__(self):
        return str(self.card) if self.has_card() else "_"

    @staticmethod
    def from_str(source: str):
        if source == "_":
            return WildcardSlot()
        else:
            return WildcardSlot(Card.from_str(source))

@dataclass
class Move:
    before: int # negative means wildcard slot
    after: int # negative means wildcard slot
    num_cards: int

    def is_before_wildcard_slot(self) -> bool:
        return self.before < 0

    def is_after_wildcard_slot(self) -> bool:
        return self.after < 0

def empty_field_slots():
    return [[], [], [], [], [], [], [], [], []]

@dataclass(unsafe_hash=True)
class Gameboard:
    wildcard_slot: WildcardSlot = WildcardSlot()
    field_slots: List[List[Card]] = field(default_factory=empty_field_slots)

    def validate(self) -> bool:
        if len(self.field_slots) != 9:
            return False

        cards: List[Card] = []
        # count all cards
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
        # print("exec: {}".format(repr(move)))
        try:
            if move.is_after_wildcard_slot():
                card = self.field_slots[move.before].pop()
                self.wildcard_slot.push(card)
            elif move.is_before_wildcard_slot():
                card = self.wildcard_slot.pop()
                self.field_slots[move.after].append(card)
            else:
                cards = self.field_slots[move.before][-move.num_cards:]
                self.field_slots[move.after].extend(cards)
                before_list = self.field_slots[move.before]
                self.field_slots[move.before] = before_list[:(len(before_list)-move.num_cards)]
        except:
            pdb.set_trace()

    def undo(self, move: Move) -> None:
        # print("undo: {}".format(repr(move)))
        if move.is_after_wildcard_slot():
            card = self.wildcard_slot.pop()
            self.field_slots[move.before].append(card)
        elif move.is_before_wildcard_slot():
            card = self.field_slots[move.after].pop()
            self.wildcard_slot.push(card)
        else:
            cards = self.field_slots[move.after][-move.num_cards:]
            self.field_slots[move.before].extend(cards)
            after_list = self.field_slots[move.after]
            self.field_slots[move.after] = after_list[:(len(after_list)-move.num_cards)]

    def solved(self) -> bool:
        if self.wildcard_slot.has_card():
            return False
        return all([self._is_field_slot_done(field_slot) for field_slot in self.field_slots])

    def get_field_slot_moves(self) -> List[Move]:
        """
        generate field slot moves first, then consider wildcard slot
        """
        valid_moves: List[Move] = []
        for from_idx in range(0, 9):
            # skip if the field slot is already sorted (including empty slot)
            if self._is_field_slot_done(self.field_slots[from_idx]):
                continue

            for to_idx in range(0, 9):
                if from_idx == to_idx:
                    continue

                from_slot = self.field_slots[from_idx]
                to_slot = self.field_slots[to_idx]
                for num_cards in range(len(from_slot), 0, -1):
                    cards_to_move = from_slot[-num_cards:]
                    if self._can_move_cards(cards_to_move, to_slot):
                        # don't move the whole stack to empty slot and leave an empty slot
                        # don't move values from sub-stack to another sub-stack (noop)
                        if (not (not to_slot and num_cards == len(from_slot))) \
                            and (not (not from_slot[-num_cards].is_face() and len(to_slot) > 0 and num_cards < len(from_slot) and from_slot[-(num_cards+1)].value == to_slot[-1].value)):
                            valid_moves.append(Move(from_idx, to_idx, num_cards))
                        # move the whole stack, ignore partial moves
                        break
        return valid_moves

    def get_wildcard_slot_moves(self) -> List[Move]:
        valid_moves: List[Move] = []
        if not self.wildcard_slot.has_card():
            for from_idx in range(0, 9):
                field_slot = self.field_slots[from_idx]
                if len(field_slot) > 1:
                    last_card = field_slot[-1]
                    prev_card = field_slot[-2]
                    if not self._can_move_cards([last_card], [prev_card]):
                        valid_moves.append(Move(from_idx, -1, 1))
        return valid_moves

    def _can_move_cards(self, cards: List[Card], to_slot: List[Card]) -> bool:
        def is_decending_values(cards: List[Card]) -> bool:
            values = [card.value for card in cards]
            for i in range(0, len(values) - 1):
                if values[i]-1 != values[i+1]:
                    return False
            return True

        def is_alternating_color(cards: List[Card]) -> bool:
            if len(cards) == 1:
                return True
            reds = [card.is_red() for card in cards]
            odd_reds = reds[::2] # should be of same color but opposite of even ones
            even_reds = reds[1::2] # should be of same color
            odd_reds_inv = [not red for red in odd_reds]
            all_reds = odd_reds_inv + even_reds # should all be the same color
            return all(red == all_reds[0] for red in all_reds)

        # cards must be (all faces && same suit) or (cards must be all values and decending value and alternating color)
        if not \
            ((all([card.is_face() for card in cards]) and all([card.suit == cards[0].suit for card in cards])) \
            or ((all([not card.is_face() for card in cards]) and is_decending_values(cards) and is_alternating_color(cards)))):
            return False

        # empty slot can accept any card (stack)
        if not to_slot: 
            return True
        
        to_card = to_slot[-1]
        current_card = cards[0]
        
        if current_card.is_face() and to_card.is_face():
            return to_card.suit == current_card.suit
        elif not (current_card.is_face() or to_card.is_face()):
            return (to_card.value == current_card.value + 1) and (current_card.is_red() != to_card.is_red())
        else:
            return False

    @staticmethod
    def _is_field_slot_done(cards: List[Card]) -> bool:
        # empty slot
        if not cards:
            return True
        # all face, same suit
        if len(cards) == 4 and all([card.is_face() for card in cards]):
            return all([card.suit == cards[0].suit for card in cards]) 
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

    def __str__(self):
        return "|".join([str(self.wildcard_slot)] + [",".join([str(card) for card in field_slot]) for field_slot in self.field_slots])

    @staticmethod
    def from_str(source: str):
        groups = source.split('|')
        wildcard_str = groups[0]
        field_slots_str = groups[1:]
        field_slots: List[List[Card]] = []
        for field_slot_str in field_slots_str:
            field_slot: List[Card] = []
            card_strs = field_slot_str.split(",")
            for card_str in card_strs:
                if card_str:
                    field_slot.append(Card.from_str(card_str))
            field_slots.append(field_slot)
        return Gameboard(wildcard_slot=WildcardSlot.from_str(wildcard_str), field_slots=field_slots)

class NacbracSolver(ABC):
    @abstractmethod
    def solve(self, gameboard: Gameboard) -> List[Move]:
        pass

class DfsSolver(NacbracSolver):
    def solve(self, gameboard: Gameboard) -> List[Move]:
        if not gameboard.validate():
            raise ValueError("Invalid gameboard!")

        self.hashes: Set = set()
        self.gameboard = gameboard
        self.last_update = datetime.datetime.now()
        depth = 0
        return self._solve(depth)

    def _solve(self, depth: int) -> List[Move]:
        # dfs
        if depth > 55:
            return []

        now = datetime.datetime.now()
        if now > self.last_update + datetime.timedelta(seconds=60):
            self.last_update = now
            print(len(self.hashes))

        def try_moves(moves: List[Move]) -> List[Move]:
            for move in field_slot_moves:
                self.gameboard.execute(move)
                new_gameboard_hash = (str(self.gameboard))
                if new_gameboard_hash not in self.hashes: # consider this new position
                    self.hashes.add(new_gameboard_hash)
                    if self.gameboard.solved():
                        return [move]
                    else:
                        solution_moves = self._solve(depth + 1)
                        if solution_moves:
                            return [move] + solution_moves
                # not a good move, revert
                self.gameboard.undo(move)
            return []
        
        field_slot_moves = self.gameboard.get_field_slot_moves()
        solution = try_moves(field_slot_moves)

        if solution:
            return solution
        
        wildcard_slot_moves = self.gameboard.get_wildcard_slot_moves()
        return try_moves(wildcard_slot_moves)

SOME_INITIAL_GAMEBOARD = "_|8H,0C,0S,0S|0H,8D,0S,0D|10H,6H,10D,7H|0H,0S,9D,9H|7D,0H,0C,0H|9S,7C,8C,8S|0D,0D,0C,6D|6S,10S,0D,9C|7S,10C,6C,0C"

def interactive_solution(solution: List[Move]):
    for move in solution:
        print("({} -> {})".format(move.before, move.after))
        input()

def pretty_format_solution(solution: List[Move]):
    return ", ".join(["({} -> {})".format(move.before, move.after) for move in solution])

def main():
    print("This is Nacbrac solver.")

    solver: NacbracSolver = DfsSolver()
    starttime = datetime.datetime.now()
    print("starttime {}".format(starttime))

    gameboard_str = SOME_INITIAL_GAMEBOARD
    solution: List[Move] = solver.solve(Gameboard.from_str(gameboard_str))
    
    endtime = datetime.datetime.now()
    print("endtime {}".format(endtime))
    print("It took {}".format(endtime - starttime))
    print("{} moves, solution [{}]".format(len(solution), pretty_format_solution(solution)))
    #interactive_solution(solution)

if __name__ == "__main__":
    main()