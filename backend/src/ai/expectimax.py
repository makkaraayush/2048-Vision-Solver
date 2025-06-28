from typing import Optional
from src.core.board import Board, Move
from src.ai.heuristics import evaluate_board

class ExpectimaxAI:
    def __init__(self, max_depth: int = 4):
        self.max_depth = max_depth
