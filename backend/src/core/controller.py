import time
from pynput.keyboard import Controller as KeyboardController, Key
from src.core.board import Move

class GameController:
    def __init__(self, key_delay: float = 0.04, settle_delay: float = 0.09):
        self.keyboard = KeyboardController()
        self.key_delay = key_delay
        self.settle_delay = settle_delay
