import functools
from typing import Tuple, Dict, Any, Optional
from src.core.board import Board, Move
from src.ai.heuristics import evaluate_board
import time
import logging

logger = logging.getLogger(__name__)

class ExpectimaxSolver:
    def __init__(self, max_depth: int = 4):
        self.max_depth = max_depth
        self.nodes_evaluated = 0

    @functools.lru_cache(maxsize=1000000)
    def _expectimax(self, grid: Tuple[int, ...], depth: int, is_player: bool) -> float:
        self.nodes_evaluated += 1
        board = Board(grid)

        if depth == 0 or board.is_game_over():
            return evaluate_board(board)

        if is_player:
            max_score = float('-inf')
            for move in Move:
                new_board, score = board.move(move)
                if new_board is not None:
                    # Recursive call for chance node
                    eval_score = self._expectimax(new_board.grid, depth - 1, False)
                    # We can add score gained to evaluation if desired, but heuristics usually handle this
                    max_score = max(max_score, eval_score)
            
            return max_score if max_score != float('-inf') else evaluate_board(board)
        else:
            # Chance node
            empty_cells = board.get_empty_cells()
            if not empty_cells:
                return evaluate_board(board)
                
            expected_score = 0.0
            prob_2 = 0.9 * (1.0 / len(empty_cells))
            prob_4 = 0.1 * (1.0 / len(empty_cells))

            for idx in empty_cells:
                # Spawn 2
                grid_list = list(grid)
                grid_list[idx] = 2
                expected_score += prob_2 * self._expectimax(tuple(grid_list), depth - 1, True)
                
                # Spawn 4
                grid_list[idx] = 4
                expected_score += prob_4 * self._expectimax(tuple(grid_list), depth - 1, True)

            return expected_score

    def get_best_move(self, board: Board, time_limit: float = 0.5) -> Tuple[Optional[Move], Dict[str, Any]]:
        self.nodes_evaluated = 0
        start_time = time.time()
        
        # Adaptive depth based on empty cells
        empty_count = len(board.get_empty_cells())
        if empty_count >= 8:
            depth = 3
        elif empty_count >= 4:
            depth = 4
        else:
            depth = 5

        # Optional override
        depth = max(depth, self.max_depth)

        best_move = None
        max_score = float('-inf')
        move_scores = {}

        self._expectimax.cache_clear() # Prevent stale large caches from slowing down memory

        for move in Move:
            new_board, score = board.move(move)
            if new_board is not None:
                eval_score = self._expectimax(new_board.grid, depth - 1, False)
                move_scores[move.name] = eval_score
                if eval_score > max_score:
                    max_score = eval_score
                    best_move = move
                    
        elapsed = time.time() - start_time
        logger.info(f"Evaluated {self.nodes_evaluated} nodes in {elapsed:.3f}s. Best move: {best_move}")

        import math
        structure_quality = min(10.0, math.log10(max_score) if max_score > 0 else 0.0)

        stats = {
            "best_move": best_move.name if best_move is not None else None,
            "score": max_score,
            "structure_quality": round(structure_quality, 2),
            "depth": depth,
            "nodes_evaluated": self.nodes_evaluated,
            "time_ms": int(elapsed * 1000),
            "move_scores": move_scores
        }
        
        return best_move, stats
