from typing import Tuple

def evaluate_board(grid: Tuple[int, ...]) -> float:
    empty_cells = sum(1 for x in grid if x == 0)
    max_tile = max(grid)
    return empty_cells * 10.0 + max_tile
