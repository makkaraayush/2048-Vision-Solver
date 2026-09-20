import random
from typing import Tuple, List, Optional
from src.core.board import Board, Move

class Headless2048:
    def __init__(self):
        self.board = Board().spawn_tile().spawn_tile()
        self.score = 0
        self.moves = 0

    def step(self, move: Move) -> bool:
        new_board, points, changed = self.board.move(move)
        if changed:
            self.board = new_board.spawn_tile()
            self.score += points
            self.moves += 1
            return True
        return False

    def is_game_over(self) -> bool:
        return self.board.is_game_over()
