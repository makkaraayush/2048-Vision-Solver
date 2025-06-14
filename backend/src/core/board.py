import random
from enum import IntEnum
from typing import Tuple, List, Optional

class Move(IntEnum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3

def slide_and_merge_row(row: List[int]) -> Tuple[List[int], int]:
    non_zero = [x for x in row if x != 0]
    merged = []
    score = 0
    skip = False
    for i in range(len(non_zero)):
        if skip:
            skip = False
            continue
        if i + 1 < len(non_zero) and non_zero[i] == non_zero[i + 1]:
            val = non_zero[i] * 2
            merged.append(val)
            score += val
            skip = True
        else:
            merged.append(non_zero[i])
    while len(merged) < 4:
        merged.append(0)
    return merged, score

class Board:
    def __init__(self, grid: Optional[Tuple[int, ...]] = None):
        self.grid = tuple(grid) if grid else tuple([0] * 16)

    def get_empty_cells(self) -> List[int]:
        return [i for i, val in enumerate(self.grid) if val == 0]

    def spawn_tile(self) -> 'Board':
        empty = self.get_empty_cells()
        if not empty:
            return self
        idx = random.choice(empty)
        val = 2 if random.random() < 0.9 else 4
        new_grid = list(self.grid)
        new_grid[idx] = val
        return Board(tuple(new_grid))
