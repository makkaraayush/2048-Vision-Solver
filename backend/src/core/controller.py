import time
from src.core.board import Move
from pynput.keyboard import Controller, Key
import logging

logger = logging.getLogger(__name__)

class GameController:
    def __init__(self, delay: float = 0.05):
        """
        Initializes the controller.
        delay: Time to hold down the key to ensure the browser registers it.
        """
        self.delay = delay
        self.keyboard = Controller()

    def execute_move(self, move: Move):
        """Simulates a key press for the given move using pynput."""
        if move == Move.UP:
            key = Key.up
        elif move == Move.DOWN:
            key = Key.down
        elif move == Move.LEFT:
            key = Key.left
        elif move == Move.RIGHT:
            key = Key.right
        else:
            logger.error(f"Unknown move: {move}")
            return

        logger.debug(f"Executing move: {key}")
        # Press and hold for a split second to ensure Javascript catches the keydown event
        self.keyboard.press(key)
        time.sleep(self.delay)
        self.keyboard.release(key)
