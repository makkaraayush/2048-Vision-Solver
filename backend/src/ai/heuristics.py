import math
from typing import Tuple

SNAKE_WEIGHTS = (
    1,     2,     4,     8,
    128,   64,    32,    16,
    256,   512,   1024,  2048,
    65536, 32768, 16384, 8192
)

def get_smoothness(grid: Tuple[int, ...]) -> float:
    smoothness = 0.0
    for r in range(4):
        for c in range(4):
            idx = r * 4 + c
            val = grid[idx]
            if val == 0:
                continue
            log_val = math.log2(val)
            if c + 1 < 4:
                right = grid[idx + 1]
                if right > 0:
                    smoothness -= abs(log_val - math.log2(right))
            if r + 1 < 4:
                down = grid[idx + 4]
                if down > 0:
                    smoothness -= abs(log_val - math.log2(down))
    return smoothness

def evaluate_board(grid: Tuple[int, ...]) -> float:
    empty_cells = sum(1 for x in grid if x == 0)
    snake = sum(grid[i] * SNAKE_WEIGHTS[i] for i in range(16))
    smooth = get_smoothness(grid)
    return snake + (empty_cells * 250.0) + (smooth * 12.0)
