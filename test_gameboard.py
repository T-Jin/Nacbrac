from unittest import TestCase
from nacbrac import Gameboard, WildcardSlot, Card, Suit, Move

SOME_INITIAL_GAMEBOARD = "_|8H,0C,0S,0S|0H,8D,0S,0D|10H,6H,10D,7H|0H,0S,9D,9H|7D,0H,0C,0H|9S,7C,8C,8S|0D,0D,0C,6D|6S,10S,0D,9C|7S,10C,6C,0C"

class TestGameboard(TestCase):
    def setUp(self):
        self.gameboard = Gameboard.from_str(SOME_INITIAL_GAMEBOARD)

    def test__validate__valid_board(self):
        self.assertTrue(self.gameboard.validate())

    def test__is_field_slot_done__valide(self):
        self.assertTrue(Gameboard._is_field_slot_done([]))
        self.assertTrue(Gameboard._is_field_slot_done([
            Card(0, Suit.Heart),
            Card(0, Suit.Heart),
            Card(0, Suit.Heart),
            Card(0, Suit.Heart),
        ]))
        self.assertTrue(Gameboard._is_field_slot_done([
            Card(10, Suit.Heart),
            Card(9, Suit.Spade),
            Card(8, Suit.Diamond),
            Card(7, Suit.Spade),
            Card(6, Suit.Heart),
        ]))
        self.assertTrue(Gameboard._is_field_slot_done([
            Card(10, Suit.Club),
            Card(9, Suit.Diamond),
            Card(8, Suit.Spade),
            Card(7, Suit.Heart),
            Card(6, Suit.Spade),
        ]))

    def test__is_field_slot_done__invalide(self):
        self.assertFalse(Gameboard._is_field_slot_done([
            Card(0, Suit.Club),
            Card(0, Suit.Heart),
            Card(0, Suit.Heart),
            Card(0, Suit.Heart),
        ]))
        self.assertFalse(Gameboard._is_field_slot_done([
            Card(10, Suit.Spade),
            Card(9, Suit.Spade),
            Card(8, Suit.Diamond),
            Card(7, Suit.Spade),
            Card(6, Suit.Heart),
        ]))
        self.assertFalse(Gameboard._is_field_slot_done([
            Card(10, Suit.Club),
            Card(9, Suit.Diamond),
            Card(8, Suit.Spade),
            Card(7, Suit.Heart),
            Card(7, Suit.Spade),
        ]))
        self.assertFalse(Gameboard._is_field_slot_done([
            Card(6, Suit.Club),
            Card(9, Suit.Diamond),
            Card(8, Suit.Spade),
            Card(7, Suit.Heart),
            Card(10, Suit.Spade),
        ]))

    def test__solved__initial_board(self):
        self.assertFalse(self.gameboard.solved())

    def test__execute_undo__noop(self):
        initial_hash = hash(str(self.gameboard))
        move = Move(before=5, after=3, num_cards=1)
        self.gameboard.execute(move)
        self.assertNotEqual(initial_hash, hash(str(self.gameboard)))
        self.gameboard.undo(move)
        self.assertEqual(initial_hash, hash(str(self.gameboard)))

    def test__get_field_slot_moves__happy_case(self):
        expected = [Move(before=2, after=5, num_cards=1), Move(before=5, after=3, num_cards=1)]
        self.assertEqual(expected, self.gameboard.get_field_slot_moves())

        self.gameboard = Gameboard.from_str("_|10D,9C,8D,7C,6D|0H,0H,0H|10H,9S,8H,7S,6H|0H|10S,9D,8C,7D,6C|0S,0S,0S,0S|0D,0D,0D,0D|10C,9H,8S,7H,6S|0C,0C,0C,0C")
        expected = [Move(before=1, after=3, num_cards=3), Move(before=3, after=1, num_cards=1)]
        self.assertEqual(expected, self.gameboard.get_field_slot_moves())

    def test__wildcard_slot_moves__valid_moves(self):
        self.gameboard = Gameboard.from_str("_|10D,9C,8D,7C|0H,0H,0H,6D|10H,9S,8H,7S,6H|0H|10S,9D,8C,7D,6C|0S,0S,0S,0S|0D,0D,0D,0D|10C,9H,8S,7H,6S|0C,0C,0C,0C")
        expected = [Move(before=1, after=-1, num_cards=1)]
        self.assertEqual(expected, self.gameboard.get_wildcard_slot_moves())
        