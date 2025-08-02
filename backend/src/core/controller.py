import time
from pynput.keyboard import Controller as KeyboardController, Key
from src.core.board import Move

class GameController:
    def __init__(self, key_delay: float = 0.05, settle_delay: float = 0.12):
        self.keyboard = KeyboardController()
        self.key_delay = key_delay
        self.settle_delay = settle_delay

    def send_move(self, move: Move):
        key_map = {
            Move.UP: Key.up,
            Move.DOWN: Key.down,
            Move.LEFT: Key.left,
            Move.RIGHT: Key.right
        }
        key = key_map.get(move)
        if key:
            try:
                self.keyboard.press(key)
                time.sleep(self.key_delay)
            finally:
                self.keyboard.release(key)
            time.sleep(self.settle_delay)
