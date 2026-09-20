import random
import time
import json
import os
from typing import Tuple, List, Optional
from src.core.board import Board, Move
from src.ai.heuristics import evaluate_board
from src.ai.expectimax import ExpectimaxAI

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

def run_simulation(weights: dict, games: int = 5) -> float:
    total_score = 0
    for _ in range(games):
        game = Headless2048()
        ai = ExpectimaxAI(max_depth=3)
        while not game.is_game_over() and game.moves < 1500:
            m = ai.get_best_move(game.board)
            if not m or not game.step(m):
                break
        total_score += game.score
    return total_score / games
