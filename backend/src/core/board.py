import random
from enum import IntEnum
from typing import Tuple, List, Optional

class Move(IntEnum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3

class Board:
    def __init__(self, grid: Optional[Tuple[int, ...]] = None):
        self.grid = tuple(grid) if grid else tuple([0] * 16)

    def __getitem__(self, idx: int) -> int:
        return self.grid[idx]

    def get_empty_cells(self) -> List[int]:
        return [i for i, val in enumerate(self.grid) if val == 0]

    def __repr__(self) -> str:
        rows = [self.grid[i*4:(i+1)*4] for i in range(4)]
        return "\n".join(str(r) for r in rows)
