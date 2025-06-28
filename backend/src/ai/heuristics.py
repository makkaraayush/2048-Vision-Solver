from typing import Tuple

SNAKE_WEIGHTS = (
    1,     2,     4,     8,
    128,   64,    32,    16,
    256,   512,   1024,  2048,
    32768, 16384, 8192,  4096
)

def evaluate_board(grid: Tuple[int, ...]) -> float:
    empty_cells = sum(1 for x in grid if x == 0)
    score = empty_cells * 50.0
    for i in range(16):
        score += grid[i] * SNAKE_WEIGHTS[i]
    return float(score)
