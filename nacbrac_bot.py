from dataclasses import dataclass
from datetime import timedelta
from typing import List
import pyautogui
import time
import logging
import sys
from math import sqrt

from nacbrac import NacbracSolver, DfsSolver, Gameboard, pretty_format_solution, Move, Suit, Card

WILDCARD_SLOT_IMG_LOCATION = (1365, 210, 125, 190)
CARD_DEALING_WAIT = timedelta(seconds=8)
FOLDER = 'resources/'
IMAGE_EXT = 'png'
DETECTION_REGION = (364, 458, 1120, 124)
WIN_BANNER_REGION = (700, 540, 530, 75)

log = logging.getLogger(__name__)


@dataclass
class Point:
    x: int
    y: int


class NacbracBot:
    def __init__(self, solver: NacbracSolver):
        self._solver = solver

    def run(self):
        log.info("Start running...")

        while True:
            # Detects in game or not
            log.info("Detecting in game or not...")
            if self._is_in_game() and not self._is_win():
                log.info("Found an active game.")
                gameboard = self._identify_board()
                log.info(f"Gameboard is {gameboard}")
                solution = self._solver.solve(gameboard)
                if solution:
                    log.info(f"Found solution in {len(solution)} moves: {pretty_format_solution(solution)}")
                    log.info("Executing solution...")
                    self._execute_solution(solution)
                    self._assert_win()
                else:
                    log.info(f"No solution, starting new game...")
                self._goto_next_game()
            elif self._is_win():
                self._goto_next_game()
            else:
                log.info("Not in game. Sleeping...")
            time.sleep(CARD_DEALING_WAIT.total_seconds())

    def _is_in_game(self) -> bool:
        try:
            result = pyautogui.locateOnScreen(self._get_filepath('wildcard_slot_empty'), region=(1335, 180, 185, 250), grayscale=True)
            if not result:
                raise pyautogui.ImageNotFoundException
            return True
        except pyautogui.ImageNotFoundException:
            return False

    def _identify_board(self) -> Gameboard:
        # Identify card locations
        screenshot = pyautogui.screenshot(region=DETECTION_REGION)
        card_location_dict = {}
        for i in range(6, 11):
            fn = str(i) + 'R'
            card_location_dict[str(i) + 'D'] = self._find_locations(screenshot, self._get_filepath(fn), 2)
            fn = str(i) + 'B'
            card_location_dict[str(i) + 'S'] = self._find_locations(screenshot, self._get_filepath(fn), 2)
        for suit in Suit:
            card_location_dict['0' + suit.value] = self._find_locations(screenshot, self._get_filepath(suit.value), 4)

        # Reverse to get location and its card
        location_card_list = []
        for card, locations in card_location_dict.items():
            for location in locations:
                location_card_list.append((location, card))
        assert len(location_card_list) == 36, f"We detected {len(location_card_list)} card locations."

        # Sort locations from left to right
        location_card_list.sort(key=lambda t: t[0].left)

        field_slot_boxes = [location_card_list[i:i+4] for i in range(0, 36, 4)]
        field_slots = []
        for field_slot_box in field_slot_boxes:
            # Sort locations from top to bottom
            field_slot_box.sort(key=lambda t: t[0].top)
            field_slot = []
            for dummy, card_str in field_slot_box:
                field_slot.append(Card.from_str(card_str))
            field_slots.append(field_slot)

        return Gameboard(field_slots=field_slots)

    def _execute_solution(self, solution: List[Move]) -> None:
        def get_card_location(slot_idx: int, card_idx: int) -> Point:
            if slot_idx < 0:
                return Point(1430, 300)
            return Point(int(425 + slot_idx * 133.75), int(473 + card_idx * 29.33))

        def move_cards(before: Point, after: Point) -> None:
            pyautogui.moveTo(before.x, before.y)
            d = Point(after.x - before.x, after.y - before.y)
            speed = sqrt(d.x ** 2 + d.y ** 2) / 800.0
            pyautogui.dragTo(after.x, after.y, speed, button='left')

        for move in solution:
            before_point = get_card_location(move.before, move.before_idx)
            after_point = get_card_location(move.after, move.after_idx)
            move_cards(before_point, after_point)

    def _assert_win(self) -> None:
        time.sleep(3)
        assert self._is_win()

    def _is_win(self) -> bool:
        banner = pyautogui.screenshot(region=WIN_BANNER_REGION)
        return len(list(pyautogui.locateAll(self._get_filepath("win"), banner, grayscale=True))) > 0

    def _goto_next_game(self) -> None:
        pyautogui.moveTo(1377,898)       
        pyautogui.mouseDown()
        time.sleep(0.5) 
        pyautogui.mouseUp()

    def _get_filepath(self, filename: str) -> str:
        return f"{FOLDER}{filename}.{IMAGE_EXT}"

    def _find_locations(self, img, fp: str, expected: int):
        locations = list(pyautogui.locateAll(fp, img, grayscale=False))
        assert len(locations) == expected, f"Didn't find {expected} cards for {fp}"
        return locations

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def main():
    setup_logging()
    logging.info("This is Nacbrac bot.")

    solver: NacbracSolver = DfsSolver()
    bot: NacbracBot = NacbracBot(solver)

    bot.run()

if __name__ == "__main__":
    main()