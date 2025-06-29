from typing import Optional, Tuple, Dict
from src.core.board import Board, Move
from src.ai.heuristics import evaluate_board

class ExpectimaxAI:
    def __init__(self, max_depth: int = 3):
        self.max_depth = max_depth
        self.transposition_table: Dict[Tuple[Tuple[int, ...], int, bool], float] = {}
