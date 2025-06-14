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
