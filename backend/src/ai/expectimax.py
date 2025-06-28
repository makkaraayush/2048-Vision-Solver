from typing import Optional
from src.core.board import Board, Move
from src.ai.heuristics import evaluate_board

class ExpectimaxAI:
    def __init__(self, max_depth: int = 3):
        self.max_depth = max_depth

    def get_best_move(self, board: Board) -> Optional[Move]:
        best_score = -float('inf')
        best_move = None
        for move in Move:
            nb, _, changed = board.move(move)
            if changed:
                score = evaluate_board(nb.grid)
                if score > best_score:
                    best_score = score
                    best_move = move
        return best_move
