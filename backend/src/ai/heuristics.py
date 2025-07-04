import math
from typing import Tuple

SNAKE_WEIGHTS = (
    1.0,        4.0,        16.0,       64.0,
    16384.0,    4096.0,     1024.0,     256.0,
    65536.0,    262144.0,   1048576.0,  4194304.0,
    1073741824.0, 268435456.0, 67108864.0, 16777216.0
)

def evaluate_board(grid: Tuple[int, ...]) -> float:
    empty_cells = sum(1 for x in grid if x == 0)
    snake = 0.0
    for i in range(16):
        if grid[i] > 0:
            snake += grid[i] * SNAKE_WEIGHTS[i]
    return snake + (empty_cells * 100000.0)
