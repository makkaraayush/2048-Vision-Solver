from typing import Optional, Tuple
from src.core.board import Board, Move
from src.ai.heuristics import evaluate_board

class ExpectimaxAI:
    def __init__(self, max_depth: int = 3):
        self.max_depth = max_depth

    def get_best_move(self, board: Board) -> Optional[Move]:
        best_score = -float('inf')
        best_move = None
        for move in Move:
            new_board, _, changed = board.move(move)
            if not changed:
                continue
            score = self._expectimax(new_board, self.max_depth - 1, False)
            if score > best_score:
                best_score = score
                best_move = move
        return best_move

    def _expectimax(self, board: Board, depth: int, is_player: bool) -> float:
        if depth == 0 or board.is_game_over():
            return evaluate_board(board.grid)
        if is_player:
            best = -float('inf')
            for move in Move:
                new_board, _, changed = board.move(move)
                if changed:
                    best = max(best, self._expectimax(new_board, depth - 1, False))
            return best if best != -float('inf') else evaluate_board(board.grid)
        else:
            empty = board.get_empty_cells()
            if not empty:
                return evaluate_board(board.grid)
            total = 0.0
            prob_2 = 0.9 / len(empty)
            prob_4 = 0.1 / len(empty)
            for idx in empty:
                g2 = list(board.grid)
                g2[idx] = 2
                total += prob_2 * self._expectimax(Board(tuple(g2)), depth - 1, True)
                g4 = list(board.grid)
                g4[idx] = 4
                total += prob_4 * self._expectimax(Board(tuple(g4)), depth - 1, True)
            return total
