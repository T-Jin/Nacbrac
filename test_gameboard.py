from unittest import TestCase
from nacbrac import Gameboard, WildcardSlot, Card, Suit

class TestGameboard(TestCase):
    def test__validate__valid_board(self):
        field_slots = [
            [
                Card(8, Suit.Heart),
                Card(0, Suit.Club),
                Card(0, Suit.Spade),
                Card(0, Suit.Spade),
            ],
            [
                Card(0, Suit.Heart),
                Card(8, Suit.Diamond),
                Card(0, Suit.Spade),
                Card(0, Suit.Diamond),
            ],
            [
                Card(10, Suit.Heart),
                Card(6, Suit.Heart),
                Card(10, Suit.Diamond),
                Card(7, Suit.Heart),
            ],
            [
                Card(0, Suit.Heart),
                Card(0, Suit.Spade),
                Card(9, Suit.Diamond),
                Card(9, Suit.Heart),
            ],
            [
                Card(7, Suit.Diamond),
                Card(0, Suit.Heart),
                Card(0, Suit.Club),
                Card(0, Suit.Heart),
            ],
            [
                Card(9, Suit.Spade),
                Card(7, Suit.Club),
                Card(8, Suit.Club),
                Card(8, Suit.Spade),
            ],
            [
                Card(0, Suit.Diamond),
                Card(0, Suit.Diamond),
                Card(0, Suit.Club),
                Card(6, Suit.Diamond),
            ],
            [
                Card(6, Suit.Spade),
                Card(10, Suit.Spade),
                Card(0, Suit.Diamond),
                Card(9, Suit.Club),
            ],
                        [
                Card(7, Suit.Spade),
                Card(10, Suit.Club),
                Card(6, Suit.Club),
                Card(0, Suit.Club),
            ],
        ]
        gameboard = Gameboard(WildcardSlot(), field_slots)
        self.assertTrue(gameboard.validate())

    def test__is_field_slot_done__valide(self):
        gameboard = Gameboard(WildcardSlot(), [])

        self.assertTrue(gameboard._is_field_slot_done([]))
        self.assertTrue(gameboard._is_field_slot_done([
            Card(0, Suit.Heart),
            Card(0, Suit.Heart),
            Card(0, Suit.Heart),
            Card(0, Suit.Heart),
        ]))
        self.assertTrue(gameboard._is_field_slot_done([
            Card(10, Suit.Heart),
            Card(9, Suit.Spade),
            Card(8, Suit.Diamond),
            Card(7, Suit.Spade),
            Card(6, Suit.Heart),
        ]))
        self.assertTrue(gameboard._is_field_slot_done([
            Card(10, Suit.Club),
            Card(9, Suit.Diamond),
            Card(8, Suit.Spade),
            Card(7, Suit.Heart),
            Card(6, Suit.Spade),
        ]))

    def test__is_field_slot_done__invalide(self):
        gameboard = Gameboard(WildcardSlot(), [])

        self.assertFalse(gameboard._is_field_slot_done([
            Card(0, Suit.Club),
            Card(0, Suit.Heart),
            Card(0, Suit.Heart),
            Card(0, Suit.Heart),
        ]))
        self.assertFalse(gameboard._is_field_slot_done([
            Card(10, Suit.Spade),
            Card(9, Suit.Spade),
            Card(8, Suit.Diamond),
            Card(7, Suit.Spade),
            Card(6, Suit.Heart),
        ]))
        self.assertFalse(gameboard._is_field_slot_done([
            Card(10, Suit.Club),
            Card(9, Suit.Diamond),
            Card(8, Suit.Spade),
            Card(7, Suit.Heart),
            Card(7, Suit.Spade),
        ]))
        self.assertFalse(gameboard._is_field_slot_done([
            Card(6, Suit.Club),
            Card(9, Suit.Diamond),
            Card(8, Suit.Spade),
            Card(7, Suit.Heart),
            Card(10, Suit.Spade),
        ]))
